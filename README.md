# ⚡ Electrical Estimation App

> AI-powered electrical project estimation with photo analysis capabilities

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

## 🎯 Overview

A modern web application that combines AI-powered photo analysis with electrical project estimation. Built with Flask backend, React frontend, and enterprise-grade security and performance optimizations.

### ✨ Key Features

- 🔍 **AI Photo Analysis** - Claude 3.5 Sonnet & Gemini 2.0 Flash integration
- 📊 **Smart Estimation** - Automated material detection and cost calculation
- 🔐 **Enterprise Security** - JWT authentication, input validation, secure file uploads
- ⚡ **High Performance** - Redis caching, async processing, optimized queries
- 🐳 **Production Ready** - Docker containerization, monitoring, CI/CD ready
- 🧪 **Comprehensive Testing** - Unit, integration, and performance tests

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

### 🐳 Docker Deployment (Recommended)

```bash
# 1. Clone and setup
git clone https://github.com/mattlowry/electrical-estimation-app.git
cd electrical-estimation-app

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys and configuration

# 3. Start all services
docker-compose up -d

# 4. Verify deployment
curl http://localhost:5000/health
```

### 🛠️ Local Development

```bash
# 1. Restructure project (first time only)
chmod +x restructure_project.sh
./restructure_project.sh

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/app.py

# 3. Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
electrical-estimation-app/
├── 📂 backend/              # Flask API server
│   ├── src/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   └── app.py           # Main application
│   ├── tests/               # Backend tests
│   └── requirements.txt     # Python dependencies
├── 📂 frontend/             # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   └── services/        # API services
│   ├── tests/               # Frontend tests
│   └── package.json         # Node dependencies
├── 📂 docker/               # Docker configuration
├── 📂 docs/                 # Documentation
├── docker-compose.yml       # Multi-container setup
└── README.md               # This file
```

## 🔒 Security Features

- **Environment-based Configuration** - No hardcoded secrets
- **JWT Authentication** - Secure token-based auth
- **Input Validation** - Comprehensive data validation
- **File Upload Security** - Type validation, size limits, safe storage
- **CORS Protection** - Configurable origin restrictions
- **Rate Limiting** - API abuse prevention
- **Security Headers** - XSS, CSRF, clickjacking protection

## ⚡ Performance Optimizations

- **Redis Caching** - Intelligent result caching
- **Async Processing** - Celery background jobs
- **Database Optimization** - Proper indexing, query optimization
- **Connection Pooling** - Efficient database connections
- **CDN Ready** - Static asset optimization
- **Monitoring** - Prometheus & Grafana integration

## 🧪 Testing

```bash
# Run all tests
python test_suite.py

# Unit tests only
pytest tests/unit/ -v --cov

# Integration tests
pytest tests/integration/ -v

# Performance tests
locust -f test_suite.py --host=http://localhost:5000
```

## 📊 Monitoring & Observability

Access monitoring dashboards (when running with monitoring profile):

- **Application**: http://localhost:3000
- **API Health**: http://localhost:5000/health
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## 🚀 Deployment

### Production Deployment

```bash
# 1. Production environment
export FLASK_ENV=production
export DATABASE_URL=postgresql://...

# 2. Start with production profile
docker-compose --profile production up -d

# 3. Run database migrations
docker-compose exec backend flask db upgrade
```

### Monitoring Deployment

```bash
# Start with monitoring stack
docker-compose --profile monitoring up -d
```

## 📝 API Documentation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/estimates` | GET | List estimates |
| `/api/estimates` | POST | Create estimate |
| `/api/estimates/{id}` | GET | Get estimate details |
| `/api/upload` | POST | Upload image for analysis |

## 🔧 Configuration

Key environment variables:

```bash
# Core Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0

# AI Services
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key

# Security
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
JWT_SECRET_KEY=your-jwt-secret

# Performance
CELERY_BROKER_URL=redis://localhost:6379/0
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📈 Performance Metrics

- **API Response Time**: <500ms (95th percentile)
- **Image Processing**: <5s per image
- **Database Queries**: <100ms average
- **Page Load Time**: <3s initial load
- **Test Coverage**: >80%

## 🎯 Roadmap

- [ ] Mobile app development
- [ ] Advanced ML models
- [ ] Real-time collaboration
- [ ] 3D visualization
- [ ] IoT device integration

## 📞 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/mattlowry/electrical-estimation-app/issues)
- 📖 **Documentation**: [Wiki](https://github.com/mattlowry/electrical-estimation-app/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/mattlowry/electrical-estimation-app/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [React](https://reactjs.org/) - Frontend library
- [Anthropic Claude](https://www.anthropic.com/) - AI analysis
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI analysis
- [Redis](https://redis.io/) - Caching and queues
- [PostgreSQL](https://www.postgresql.org/) - Database

---

<div align="center">
  <strong>Built with ❤️ for the electrical industry</strong>
</div>