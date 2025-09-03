"""
Performance Optimization Module for Electrical Estimation App
Implements caching, async processing, and database optimizations
"""

import os
import hashlib
import asyncio
import functools
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import redis
from flask import Flask, g
from flask_caching import Cache
from celery import Celery
from sqlalchemy import create_engine, event, Index
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.pool import QueuePool
import aiohttp

# Performance monitoring
import time
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# ============================================================
# CACHING CONFIGURATION
# ============================================================

class CacheManager:
    """Advanced caching with Redis backend"""
    
    def __init__(self, app: Flask = None):
        self.cache = None
        self.redis_client = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize caching with Flask app"""
        # Redis connection
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Flask-Caching configuration
        app.config['CACHE_TYPE'] = 'RedisCache'
        app.config['CACHE_REDIS_URL'] = redis_url
        app.config['CACHE_DEFAULT_TIMEOUT'] = 300
        app.config['CACHE_KEY_PREFIX'] = 'estimation_app:'
        
        self.cache = Cache(app)
        
    def get_cache_key(self, *args, **kwargs):
        """Generate consistent cache key from arguments"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def cache_result(self, timeout=300, key_prefix="result"):
        """Decorator for caching function results"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}:{self.get_cache_key(*args, **kwargs)}"
                
                # Try to get from cache
                cached = self.redis_client.get(cache_key)
                if cached:
                    logger.info(f"Cache hit for {cache_key}")
                    return eval(cached)  # Use json.loads for production
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.redis_client.setex(
                    cache_key, 
                    timeout, 
                    str(result)  # Use json.dumps for production
                )
                logger.info(f"Cached result for {cache_key}")
                
                return result
            return wrapper
        return decorator
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all cache keys matching pattern"""
        for key in self.redis_client.scan_iter(match=f"estimation_app:{pattern}"):
            self.redis_client.delete(key)

# ============================================================
# ASYNC PROCESSING WITH CELERY
# ============================================================

class AsyncProcessor:
    """Background job processing with Celery"""
    
    def __init__(self):
        self.celery = Celery(
            'estimation_app',
            broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
            backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
        )
        
        # Configure Celery
        self.celery.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            task_track_started=True,
            task_time_limit=300,  # 5 minutes
            task_soft_time_limit=240,  # 4 minutes
            worker_prefetch_multiplier=1,
            worker_max_tasks_per_child=100,
        )
        
        self._register_tasks()
    
    def _register_tasks(self):
        """Register Celery tasks"""
        
        @self.celery.task(bind=True, name='process_image')
        def process_image_task(self, image_path: str, estimate_id: str):
            """Process image in background"""
            try:
                # Update task state
                self.update_state(state='PROCESSING', meta={'status': 'Analyzing image...'})
                
                # Simulate image processing
                result = analyze_image_with_ai(image_path)
                
                # Update database
                update_estimate_with_results(estimate_id, result)
                
                return {'status': 'completed', 'result': result}
                
            except Exception as e:
                logger.error(f"Image processing failed: {e}")
                raise
        
        @self.celery.task(bind=True, name='generate_pdf')
        def generate_pdf_task(self, estimate_id: str):
            """Generate PDF report in background"""
            try:
                self.update_state(state='GENERATING', meta={'status': 'Creating PDF...'})
                
                # Generate PDF
                pdf_path = generate_estimate_pdf(estimate_id)
                
                return {'status': 'completed', 'pdf_path': pdf_path}
                
            except Exception as e:
                logger.error(f"PDF generation failed: {e}")
                raise
        
        @self.celery.task(bind=True, name='batch_process')
        def batch_process_task(self, items: List[Dict]):
            """Process multiple items in batch"""
            results = []
            total = len(items)
            
            for i, item in enumerate(items):
                self.update_state(
                    state='PROCESSING',
                    meta={'current': i + 1, 'total': total}
                )
                
                # Process item
                result = process_single_item(item)
                results.append(result)
            
            return {'status': 'completed', 'results': results}

# ============================================================
# DATABASE OPTIMIZATION
# ============================================================

class DatabaseOptimizer:
    """Database performance optimizations"""
    
    def __init__(self, database_url: str):
        # Create optimized engine with connection pooling
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo_pool=False
        )
        
        # Register event listeners
        self._register_listeners()
    
    def _register_listeners(self):
        """Register SQLAlchemy event listeners for optimization"""
        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            """Optimize SQLite performance"""
            if 'sqlite' in self.engine.url.drivername:
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
    
    def create_indexes(self):
        """Create optimized indexes for common queries"""
        with self.engine.connect() as conn:
            # Composite indexes for efficient queries
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_estimates_project_status ON estimates(project_id, status)",
                "CREATE INDEX IF NOT EXISTS idx_estimates_created_date ON estimates(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_materials_category_active ON materials(category, is_active)",
                "CREATE INDEX IF NOT EXISTS idx_photos_estimate_created ON photos(estimate_id, created_at)",
                "CREATE INDEX IF NOT EXISTS idx_estimate_items_estimate ON estimate_items(estimate_id)",
            ]
            
            for index_sql in indexes:
                conn.execute(index_sql)
                logger.info(f"Created index: {index_sql}")
    
    @contextmanager
    def optimized_session(self):
        """Context manager for optimized database sessions"""
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

class QueryOptimizer:
    """Optimized database queries"""
    
    @staticmethod
    def get_estimate_with_relations(session: Session, estimate_id: str):
        """Efficiently load estimate with all relations"""
        from models.estimate import Estimate
        
        return session.query(Estimate)\
            .options(
                joinedload(Estimate.photos),
                joinedload(Estimate.materials),
                selectinload(Estimate.items),
                joinedload(Estimate.project)
            )\
            .filter(Estimate.id == estimate_id)\
            .first()
    
    @staticmethod
    def get_estimates_paginated(session: Session, page: int = 1, per_page: int = 20,
                               project_id: Optional[str] = None):
        """Get paginated estimates with efficient loading"""
        from models.estimate import Estimate
        
        query = session.query(Estimate)\
            .options(
                joinedload(Estimate.project),
                selectinload(Estimate.photos)
            )
        
        if project_id:
            query = query.filter(Estimate.project_id == project_id)
        
        # Calculate pagination
        total = query.count()
        estimates = query\
            .order_by(Estimate.created_at.desc())\
            .limit(per_page)\
            .offset((page - 1) * per_page)\
            .all()
        
        return {
            'items': estimates,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }

# ============================================================
# AI SERVICE OPTIMIZATION
# ============================================================

class AIServiceOptimizer:
    """Optimized AI service calls with caching and batching"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.executor = ThreadPoolExecutor(max_workers=5)
        
    async def analyze_images_batch(self, image_paths: List[str]) -> List[Dict]:
        """Analyze multiple images concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for image_path in image_paths:
                # Check cache first
                cache_key = self._get_image_cache_key(image_path)
                cached_result = self.cache_manager.redis_client.get(cache_key)
                
                if cached_result:
                    tasks.append(asyncio.create_task(
                        self._return_cached(cached_result)
                    ))
                else:
                    tasks.append(asyncio.create_task(
                        self._analyze_single_image(session, image_path)
                    ))
            
            results = await asyncio.gather(*tasks)
            return results
    
    async def _analyze_single_image(self, session: aiohttp.ClientSession, 
                                   image_path: str) -> Dict:
        """Analyze single image with AI service"""
        # Implementation for AI service call
        result = await self._call_ai_service(session, image_path)
        
        # Cache result
        cache_key = self._get_image_cache_key(image_path)
        self.cache_manager.redis_client.setex(
            cache_key,
            86400,  # Cache for 24 hours
            str(result)
        )
        
        return result
    
    async def _return_cached(self, cached_data: str) -> Dict:
        """Return cached result"""
        return eval(cached_data)  # Use json.loads in production
    
    def _get_image_cache_key(self, image_path: str) -> str:
        """Generate cache key for image analysis"""
        with open(image_path, 'rb') as f:
            image_hash = hashlib.md5(f.read()).hexdigest()
        return f"ai_analysis:{image_hash}"
    
    async def _call_ai_service(self, session: aiohttp.ClientSession, 
                              image_path: str) -> Dict:
        """Actual AI service call - implement based on your service"""
        # Placeholder for actual implementation
        pass

# ============================================================
# PERFORMANCE MONITORING
# ============================================================

class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        
    @contextmanager
    def track_time(self, operation_name: str):
        """Track execution time of operations"""
        start_time = time.time()
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            
            # Log performance
            logger.info(f"{operation_name} took {duration:.2f}s")
            
            # Store metrics
            if operation_name not in self.metrics:
                self.metrics[operation_name] = []
            self.metrics[operation_name].append(duration)
            
            # Alert if slow
            if duration > 5:
                logger.warning(f"{operation_name} is slow: {duration:.2f}s")
    
    def get_statistics(self, operation_name: str) -> Dict:
        """Get performance statistics for an operation"""
        if operation_name not in self.metrics:
            return {}
        
        times = self.metrics[operation_name]
        return {
            'count': len(times),
            'total': sum(times),
            'average': sum(times) / len(times),
            'min': min(times),
            'max': max(times)
        }

# ============================================================
# INTEGRATION WITH FLASK APP
# ============================================================

def init_performance_optimizations(app: Flask):
    """Initialize all performance optimizations"""
    
    # Initialize cache manager
    cache_manager = CacheManager(app)
    
    # Initialize database optimizer
    db_optimizer = DatabaseOptimizer(
        app.config['SQLALCHEMY_DATABASE_URI']
    )
    db_optimizer.create_indexes()
    
    # Initialize async processor
    async_processor = AsyncProcessor()
    
    # Initialize AI optimizer
    ai_optimizer = AIServiceOptimizer(cache_manager)
    
    # Initialize performance monitor
    perf_monitor = PerformanceMonitor()
    
    # Store in app context
    app.cache_manager = cache_manager
    app.db_optimizer = db_optimizer
    app.async_processor = async_processor
    app.ai_optimizer = ai_optimizer
    app.perf_monitor = perf_monitor
    
    # Add before request handler for performance tracking
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        return response
    
    logger.info("Performance optimizations initialized")

# ============================================================
# USAGE EXAMPLES
# ============================================================

if __name__ == "__main__":
    # Example usage
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    
    # Initialize optimizations
    init_performance_optimizations(app)
    
    # Example cached endpoint
    @app.route('/api/estimates/<estimate_id>')
    @app.cache_manager.cache_result(timeout=300, key_prefix="estimate")
    def get_estimate(estimate_id):
        with app.perf_monitor.track_time("get_estimate"):
            # Your implementation
            pass
    
    # Example async processing
    @app.route('/api/process-image', methods=['POST'])
    def process_image():
        # Queue async task
        task = app.async_processor.celery.send_task(
            'process_image',
            args=[image_path, estimate_id]
        )
        return {'task_id': task.id}
    
    app.run(debug=False)