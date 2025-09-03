"""
Security Configuration Module for Electrical Estimation App
Implements all critical security fixes identified in the audit
"""

import os
import secrets
from datetime import timedelta
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SecurityConfig:
    """Centralized security configuration"""
    
    # Environment-based configuration
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
    JWT_EXPIRATION_DELTA = timedelta(hours=24)
    
    # CORS configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
    
    # File upload configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/uploads')
    
    # API rate limiting
    RATE_LIMIT = "100 per hour"
    
    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    # AI Service configuration
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    @staticmethod
    def validate_api_keys():
        """Validate that required API keys are present"""
        missing_keys = []
        if not SecurityConfig.ANTHROPIC_API_KEY:
            missing_keys.append('ANTHROPIC_API_KEY')
        if not SecurityConfig.GOOGLE_API_KEY:
            missing_keys.append('GOOGLE_API_KEY')
        
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")

def create_secure_app():
    """Factory function to create a secure Flask application"""
    app = Flask(__name__)
    
    # Apply security configuration
    app.config['SECRET_KEY'] = SecurityConfig.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = SecurityConfig.MAX_FILE_SIZE
    
    # Configure CORS with specific origins
    CORS(app, origins=SecurityConfig.ALLOWED_ORIGINS, 
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'])
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[SecurityConfig.RATE_LIMIT]
    )
    
    # Security headers middleware
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    
    return app, limiter

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in SecurityConfig.ALLOWED_EXTENSIONS

def validate_file_upload(file):
    """Comprehensive file upload validation"""
    if not file:
        return False, "No file provided"
    
    filename = secure_filename(file.filename)
    if not filename:
        return False, "Invalid filename"
    
    if not allowed_file(filename):
        return False, f"File type not allowed. Allowed types: {', '.join(SecurityConfig.ALLOWED_EXTENSIONS)}"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > SecurityConfig.MAX_FILE_SIZE:
        return False, f"File size exceeds maximum allowed size of {SecurityConfig.MAX_FILE_SIZE / 1024 / 1024}MB"
    
    return True, filename

# JWT Authentication decorator
def require_auth(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(
                token, 
                SecurityConfig.JWT_SECRET_KEY, 
                algorithms=['HS256']
            )
            request.user_id = payload['user_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

# Input validation helpers
def validate_estimate_input(data):
    """Validate estimate creation/update input"""
    errors = []
    
    # Required fields
    required_fields = ['project_name', 'description']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Field '{field}' is required")
    
    # Field length validation
    if 'project_name' in data and len(data['project_name']) > 200:
        errors.append("Project name must be less than 200 characters")
    
    if 'description' in data and len(data['description']) > 1000:
        errors.append("Description must be less than 1000 characters")
    
    # Validate numeric fields if present
    if 'labor_hours' in data:
        try:
            hours = float(data['labor_hours'])
            if hours < 0 or hours > 10000:
                errors.append("Labor hours must be between 0 and 10000")
        except (ValueError, TypeError):
            errors.append("Labor hours must be a valid number")
    
    return errors

class SecureFileHandler:
    """Secure file handling with path traversal prevention"""
    
    @staticmethod
    def get_safe_path(filename):
        """Get a safe file path preventing directory traversal"""
        # Remove any directory components
        filename = os.path.basename(filename)
        # Secure the filename
        filename = secure_filename(filename)
        # Generate unique filename to prevent overwrites
        unique_filename = f"{secrets.token_hex(8)}_{filename}"
        # Create full path
        filepath = os.path.join(SecurityConfig.UPLOAD_FOLDER, unique_filename)
        # Verify the path is within upload folder
        if not os.path.abspath(filepath).startswith(os.path.abspath(SecurityConfig.UPLOAD_FOLDER)):
            raise ValueError("Invalid file path")
        return filepath
    
    @staticmethod
    def save_uploaded_file(file):
        """Safely save an uploaded file"""
        is_valid, result = validate_file_upload(file)
        if not is_valid:
            raise ValueError(result)
        
        safe_path = SecureFileHandler.get_safe_path(result)
        
        # Ensure upload directory exists
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        
        # Save file
        file.save(safe_path)
        
        return safe_path

# Example usage in main.py
if __name__ == "__main__":
    # Validate API keys on startup
    try:
        SecurityConfig.validate_api_keys()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        exit(1)
    
    # Create secure app
    app, limiter = create_secure_app()
    
    # Example secure endpoint
    @app.route('/api/secure-upload', methods=['POST'])
    @require_auth
    @limiter.limit("10 per hour")
    def secure_upload():
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        try:
            filepath = SecureFileHandler.save_uploaded_file(file)
            return jsonify({'success': True, 'filepath': filepath}), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    # Run app securely (never in debug mode for production)
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )