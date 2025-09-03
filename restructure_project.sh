#!/bin/bash

# Project Restructuring Script for Electrical Estimation App
# This script reorganizes the project into a proper structure

echo "🔧 Starting project restructuring..."

# Create base directory structure
PROJECT_ROOT="electrical-estimation-app"
mkdir -p "$PROJECT_ROOT"

# Backend structure
echo "📁 Creating backend structure..."
mkdir -p "$PROJECT_ROOT/backend/src/{models,routes,services,utils}"
mkdir -p "$PROJECT_ROOT/backend/tests"
mkdir -p "$PROJECT_ROOT/backend/migrations"

# Frontend structure
echo "📁 Creating frontend structure..."
mkdir -p "$PROJECT_ROOT/frontend/src/{components,hooks,services,utils,styles}"
mkdir -p "$PROJECT_ROOT/frontend/public"
mkdir -p "$PROJECT_ROOT/frontend/tests"

# Additional directories
echo "📁 Creating additional directories..."
mkdir -p "$PROJECT_ROOT/docker"
mkdir -p "$PROJECT_ROOT/docs"
mkdir -p "$PROJECT_ROOT/scripts"
mkdir -p "$PROJECT_ROOT/.github/workflows"

# Move Python files to backend
echo "🔄 Moving backend files..."
if [ -f "main.py" ]; then
    mv main.py "$PROJECT_ROOT/backend/src/app.py"
fi

if [ -f "estimates.py" ]; then
    mv estimates.py "$PROJECT_ROOT/backend/src/routes/estimates.py"
fi

if [ -f "estimate.py" ]; then
    mv estimate.py "$PROJECT_ROOT/backend/src/models/estimate.py"
fi

for service in ai_service.py ai_service_factory.py mock_ai_service.py pricing_service.py pdf_service.py; do
    if [ -f "$service" ]; then
        mv "$service" "$PROJECT_ROOT/backend/src/services/"
    fi
done

# Move React components to frontend
echo "🔄 Moving frontend files..."
for component in App.jsx EstimateForm.jsx EstimateList.jsx EstimateView.jsx FileUpload.jsx Header.jsx MaterialsList.jsx PricingDisplay.jsx; do
    if [ -f "$component" ]; then
        mv "$component" "$PROJECT_ROOT/frontend/src/components/"
    fi
done

if [ -f "use-toast.js" ]; then
    mv use-toast.js "$PROJECT_ROOT/frontend/src/hooks/"
fi

if [ -f "index.html" ]; then
    mv index.html "$PROJECT_ROOT/frontend/"
fi

if [ -f "vite.config.js" ]; then
    mv vite.config.js "$PROJECT_ROOT/frontend/"
fi

# Move documentation files
echo "📚 Organizing documentation..."
for doc in *.md; do
    if [ -f "$doc" ]; then
        mv "$doc" "$PROJECT_ROOT/docs/"
    fi
done

# Create .env.example file
echo "🔐 Creating environment configuration template..."
cat > "$PROJECT_ROOT/.env.example" << 'EOF'
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-generate-with-secrets-token-hex-32
PORT=5000

# Database Configuration
DATABASE_URL=sqlite:///app.db
# For production, use PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# File Upload Configuration
UPLOAD_FOLDER=/app/uploads
MAX_FILE_SIZE=10485760

# AI Service Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-generate-with-secrets-token-hex-32
JWT_EXPIRATION_HOURS=24

# Redis Configuration (for caching and background jobs)
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Frontend Configuration
VITE_API_URL=http://localhost:5000/api
VITE_APP_TITLE=Electrical Estimation App
EOF

# Create requirements.txt for backend
echo "📦 Creating backend requirements.txt..."
cat > "$PROJECT_ROOT/backend/requirements.txt" << 'EOF'
# Core Flask dependencies
Flask==3.0.0
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-Limiter==3.5.0

# Database
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9

# Authentication & Security
PyJWT==2.8.0
python-dotenv==1.0.0
cryptography==41.0.7

# AI Services
anthropic==0.8.1
google-generativeai==0.3.2

# PDF Generation
reportlab==4.0.7
Pillow==10.1.0

# Caching & Background Jobs
redis==5.0.1
celery==5.3.4
Flask-Caching==2.1.0

# Utilities
python-dateutil==2.8.2
requests==2.31.0

# Development & Testing
pytest==7.4.3
pytest-flask==1.3.0
pytest-cov==4.1.0
black==23.12.1
flake8==7.0.0
mypy==1.7.1

# Production
gunicorn==21.2.0
gevent==23.9.1
EOF

# Create package.json for frontend
echo "📦 Creating frontend package.json..."
cat > "$PROJECT_ROOT/frontend/package.json" << 'EOF'
{
  "name": "electrical-estimation-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "lint": "eslint src --ext js,jsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \"src/**/*.{js,jsx,css,md}\""
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.1",
    "axios": "^1.6.2",
    "react-hook-form": "^7.48.2",
    "react-query": "^3.39.3",
    "zustand": "^4.4.7",
    "react-dropzone": "^14.2.3",
    "react-hot-toast": "^2.4.1",
    "date-fns": "^2.30.0",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.55.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "postcss": "^8.4.32",
    "prettier": "^3.1.1",
    "tailwindcss": "^3.3.6",
    "vite": "^5.0.8",
    "vitest": "^1.0.4",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/user-event": "^14.5.1"
  }
}
EOF

# Create .gitignore
echo "🚫 Creating .gitignore..."
cat > "$PROJECT_ROOT/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
*.egg-info/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite3

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# Build outputs
dist/
build/
*.egg
.eggs/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.env.local
.env.*.local

# Uploads
uploads/
temp/

# Logs
logs/
*.log

# Testing
coverage/
.nyc_output/

# Production
*.pem
*.key
*.crt
EOF

# Create main backend application file with proper imports
echo "🔧 Creating main application file..."
cat > "$PROJECT_ROOT/backend/src/app.py" << 'EOF'
"""
Main Flask application with proper configuration
"""
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure CORS
    CORS(app, origins=os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(','))
    
    # Register blueprints
    from routes.estimates import estimates_bp
    app.register_blueprint(estimates_bp, url_prefix='/api/estimates')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Run application
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
EOF

# Create README for the restructured project
echo "📝 Creating project README..."
cat > "$PROJECT_ROOT/README.md" << 'EOF'
# Electrical Estimation Application

A modern web application for electrical project estimation with AI-powered photo analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (for caching and background jobs)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env
# Edit .env with your configuration
flask db init
flask db migrate
flask db upgrade
python src/app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure
```
electrical-estimation-app/
├── backend/              # Flask backend
│   ├── src/             # Source code
│   │   ├── models/      # Database models
│   │   ├── routes/      # API endpoints
│   │   └── services/    # Business logic
│   └── tests/           # Backend tests
├── frontend/            # React frontend
│   ├── src/             # Source code
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom hooks
│   │   └── services/    # API services
│   └── tests/           # Frontend tests
├── docker/              # Docker configuration
├── docs/                # Documentation
└── scripts/             # Utility scripts
```

## 🔒 Security
- Environment-based configuration
- JWT authentication
- Rate limiting
- Input validation
- Secure file uploads

## 🧪 Testing
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

## 📦 Deployment
See `docs/DEPLOYMENT_GUIDE.md` for detailed deployment instructions.

## 📝 License
[Your License Here]
EOF

echo "✅ Project restructuring complete!"
echo ""
echo "Next steps:"
echo "1. Review the new structure in $PROJECT_ROOT/"
echo "2. Copy and configure .env from .env.example"
echo "3. Install dependencies:"
echo "   - Backend: cd backend && pip install -r requirements.txt"
echo "   - Frontend: cd frontend && npm install"
echo "4. Extract and properly place any files from the .tar.gz archives"
echo "5. Run the application:"
echo "   - Backend: cd backend && python src/app.py"
echo "   - Frontend: cd frontend && npm run dev"
echo ""
echo "⚠️  Note: This script creates the structure but doesn't extract compressed archives."
echo "    Please manually extract and place files from .tar.gz archives in the appropriate locations."