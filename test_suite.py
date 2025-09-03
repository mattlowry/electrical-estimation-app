"""
Comprehensive Testing Suite for Electrical Estimation App
Includes unit tests, integration tests, and performance tests
"""

import os
import json
import pytest
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import asyncio

# Flask testing
from flask import Flask
from flask_testing import TestCase

# Testing utilities
from faker import Faker
import factory
from hypothesis import given, strategies as st

# Performance testing
import locust
from locust import HttpUser, task, between

# ============================================================
# TEST CONFIGURATION
# ============================================================

@pytest.fixture
def app():
    """Create test Flask application"""
    from src.app import create_app
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
    })
    
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def db(app):
    """Create test database"""
    from src.app import db
    
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture
def auth_headers():
    """Generate authentication headers for testing"""
    import jwt
    
    token = jwt.encode(
        {'user_id': 'test_user', 'exp': datetime.utcnow() + timedelta(hours=1)},
        'test-secret-key',
        algorithm='HS256'
    )
    
    return {'Authorization': f'Bearer {token}'}

# ============================================================
# UNIT TESTS
# ============================================================

class TestSecurityModule:
    """Test security implementations"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        from src.security_fixes import generate_password_hash, check_password_hash
        
        password = "SecurePassword123!"
        hashed = generate_password_hash(password)
        
        assert hashed != password
        assert check_password_hash(hashed, password)
        assert not check_password_hash(hashed, "WrongPassword")
    
    def test_jwt_token_generation(self):
        """Test JWT token generation and validation"""
        from src.security_fixes import SecurityConfig
        import jwt
        
        user_id = "test_user_123"
        token = jwt.encode(
            {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(hours=1)},
            SecurityConfig.JWT_SECRET_KEY,
            algorithm='HS256'
        )
        
        decoded = jwt.decode(token, SecurityConfig.JWT_SECRET_KEY, algorithms=['HS256'])
        assert decoded['user_id'] == user_id
    
    def test_file_upload_validation(self):
        """Test file upload security validation"""
        from src.security_fixes import validate_file_upload
        
        # Create mock file
        mock_file = Mock()
        mock_file.filename = "test_image.jpg"
        mock_file.tell.return_value = 1024 * 1024  # 1MB
        mock_file.seek = Mock()
        
        is_valid, result = validate_file_upload(mock_file)
        assert is_valid
        assert result == "test_image.jpg"
        
        # Test invalid file type
        mock_file.filename = "malicious.exe"
        is_valid, result = validate_file_upload(mock_file)
        assert not is_valid
        assert "not allowed" in result
    
    def test_input_validation(self):
        """Test input validation for estimates"""
        from src.security_fixes import validate_estimate_input
        
        # Valid input
        valid_data = {
            'project_name': 'Test Project',
            'description': 'Test Description',
            'labor_hours': 10.5
        }
        errors = validate_estimate_input(valid_data)
        assert len(errors) == 0
        
        # Invalid input
        invalid_data = {
            'project_name': 'A' * 201,  # Too long
            'labor_hours': -5  # Negative
        }
        errors = validate_estimate_input(invalid_data)
        assert len(errors) > 0

class TestPerformanceOptimizations:
    """Test performance optimization implementations"""
    
    @pytest.mark.asyncio
    async def test_cache_manager(self):
        """Test caching functionality"""
        from src.performance_optimization import CacheManager
        
        app = Flask(__name__)
        cache_manager = CacheManager(app)
        
        @cache_manager.cache_result(timeout=60, key_prefix="test")
        def expensive_function(x):
            return x * 2
        
        # First call should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        
        # Second call should use cache
        with patch.object(cache_manager.redis_client, 'get', return_value='10'):
            result2 = expensive_function(5)
            assert result2 == 10
    
    def test_database_optimizer(self):
        """Test database optimization"""
        from src.performance_optimization import DatabaseOptimizer
        
        optimizer = DatabaseOptimizer('sqlite:///:memory:')
        
        # Test index creation
        optimizer.create_indexes()
        
        # Test optimized session
        with optimizer.optimized_session() as session:
            assert session is not None
    
    @pytest.mark.asyncio
    async def test_ai_service_batch_processing(self):
        """Test AI service batch processing"""
        from src.performance_optimization import AIServiceOptimizer, CacheManager
        
        app = Flask(__name__)
        cache_manager = CacheManager(app)
        ai_optimizer = AIServiceOptimizer(cache_manager)
        
        # Mock AI service calls
        with patch.object(ai_optimizer, '_call_ai_service') as mock_call:
            mock_call.return_value = {'result': 'analyzed'}
            
            image_paths = ['/path/image1.jpg', '/path/image2.jpg']
            results = await ai_optimizer.analyze_images_batch(image_paths)
            
            assert len(results) == 2

# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestAPIEndpoints(TestCase):
    """Test API endpoint integration"""
    
    def create_app(self):
        """Create test app"""
        from src.app import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'healthy')
    
    def test_estimate_creation(self):
        """Test estimate creation endpoint"""
        with patch('src.routes.estimates.require_auth'):
            data = {
                'project_name': 'Test Project',
                'description': 'Test Description',
                'materials': []
            }
            
            response = self.client.post(
                '/api/estimates',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 201)
    
    def test_file_upload_endpoint(self):
        """Test secure file upload endpoint"""
        with patch('src.routes.estimates.require_auth'):
            with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp:
                tmp.write(b'fake image data')
                tmp.seek(0)
                
                response = self.client.post(
                    '/api/upload',
                    data={'file': (tmp, 'test.jpg')},
                    content_type='multipart/form-data'
                )
                
                self.assertIn(response.status_code, [200, 201])

# ============================================================
# PERFORMANCE TESTS
# ============================================================

class PerformanceTestUser(HttpUser):
    """Locust user for performance testing"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get auth token"""
        response = self.client.post("/api/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        if response.status_code == 200:
            self.token = response.json().get('token')
            self.headers = {'Authorization': f'Bearer {self.token}'}
        else:
            self.headers = {}
    
    @task(3)
    def view_estimates(self):
        """Test viewing estimates list"""
        self.client.get("/api/estimates", headers=self.headers)
    
    @task(2)
    def view_estimate_detail(self):
        """Test viewing single estimate"""
        estimate_id = "test_estimate_id"
        self.client.get(f"/api/estimates/{estimate_id}", headers=self.headers)
    
    @task(1)
    def create_estimate(self):
        """Test creating new estimate"""
        self.client.post("/api/estimates", 
            json={
                "project_name": "Performance Test Project",
                "description": "Testing performance"
            },
            headers=self.headers
        )

# ============================================================
# FACTORY AND FIXTURES
# ============================================================

fake = Faker()

class EstimateFactory(factory.Factory):
    """Factory for creating test estimates"""
    class Meta:
        model = dict
    
    id = factory.LazyFunction(lambda: fake.uuid4())
    project_name = factory.LazyFunction(lambda: fake.company())
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    created_at = factory.LazyFunction(lambda: fake.date_time())
    labor_hours = factory.LazyFunction(lambda: fake.random_int(1, 100))
    total_cost = factory.LazyFunction(lambda: fake.random_int(1000, 100000))

class MaterialFactory(factory.Factory):
    """Factory for creating test materials"""
    class Meta:
        model = dict
    
    id = factory.LazyFunction(lambda: fake.uuid4())
    name = factory.LazyFunction(lambda: fake.word())
    category = factory.LazyFunction(lambda: fake.random_element(['Electrical', 'Plumbing', 'HVAC']))
    unit_price = factory.LazyFunction(lambda: fake.random_int(10, 1000))
    quantity = factory.LazyFunction(lambda: fake.random_int(1, 50))

# ============================================================
# PROPERTY-BASED TESTING
# ============================================================

class TestPropertyBased:
    """Property-based testing with Hypothesis"""
    
    @given(
        project_name=st.text(min_size=1, max_size=200),
        labor_hours=st.floats(min_value=0, max_value=10000),
        materials_count=st.integers(min_value=0, max_value=100)
    )
    def test_estimate_calculation(self, project_name, labor_hours, materials_count):
        """Test estimate calculation with random inputs"""
        from src.services.pricing_service import calculate_estimate_total
        
        materials = [MaterialFactory() for _ in range(materials_count)]
        
        total = calculate_estimate_total(labor_hours, materials)
        
        # Verify calculations
        assert total >= 0
        assert isinstance(total, (int, float))

# ============================================================
# TEST RUNNERS AND CONFIGURATION
# ============================================================

def run_unit_tests():
    """Run unit tests with coverage"""
    pytest.main([
        'test_suite.py::TestSecurityModule',
        'test_suite.py::TestPerformanceOptimizations',
        '--cov=src',
        '--cov-report=html',
        '--cov-report=term',
        '-v'
    ])

def run_integration_tests():
    """Run integration tests"""
    pytest.main([
        'test_suite.py::TestAPIEndpoints',
        '-v'
    ])

def run_performance_tests():
    """Run performance tests with Locust"""
    os.system('locust -f test_suite.py --host=http://localhost:5000 --users=100 --spawn-rate=10 --time=60s')

def run_all_tests():
    """Run complete test suite"""
    print("🧪 Running Unit Tests...")
    run_unit_tests()
    
    print("\n🔗 Running Integration Tests...")
    run_integration_tests()
    
    print("\n⚡ Running Performance Tests...")
    run_performance_tests()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    # Configure test environment
    os.environ['TESTING'] = 'true'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    # Run all tests
    run_all_tests()