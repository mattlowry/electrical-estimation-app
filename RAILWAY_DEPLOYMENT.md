# 🚂 Railway Deployment Guide

**One-Platform Solution - No Multiple Services Needed!**

Railway handles everything in one place:
- ✅ Full-stack app deployment
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ File storage
- ✅ Auto-scaling
- ✅ Domain management

## 🚀 One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/electrical-estimation-app)

## Manual Deployment

### 1. Setup Railway Account
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login
```

### 2. Deploy Your App
```bash
# In your project directory
railway link
railway up
```

### 3. Add Services
Railway automatically provisions:
- **PostgreSQL** database
- **Redis** cache
- **App** container

### 4. Environment Variables
Railway auto-configures database URLs. Add these in the dashboard:

```env
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
ALLOWED_ORIGINS=https://your-app.railway.app
```

### 5. Custom Domain (Optional)
- Railway provides: `your-app.railway.app`
- Add custom domain in settings

## 🔧 What Railway Provides

### Automatic Configuration
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis for sessions and caching
- **Storage**: Persistent volumes for file uploads
- **SSL**: Automatic HTTPS certificates
- **Scaling**: Auto-scale based on traffic
- **Monitoring**: Built-in metrics and logs

### File Structure for Railway
```
electrical-estimation-app/
├── Dockerfile.railway      # Single container build
├── railway.json            # Railway configuration
├── backend/                # Flask app
├── frontend/               # React app (builds into backend)
└── docker-compose.yml      # Local development
```

## 💰 Pricing
- **Free Tier**: $0/month (500 hours)
- **Pro Tier**: $5/month (unlimited)
- **Database**: $5/month for PostgreSQL
- **Redis**: $3/month for managed Redis

**Total: ~$13/month for full production stack**

## 🚀 Alternative Single-Platform Options

### Option 1: Render
```bash
# Connect GitHub repo to Render
# Auto-deploys Docker containers
# Built-in PostgreSQL and Redis
```

### Option 2: DigitalOcean App Platform
```bash
# Upload docker-compose.yml
# Managed databases included
# One-click deployment
```

### Option 3: Fly.io
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

## 🎯 Why Railway?

### Pros:
- ✅ **Single platform** for everything
- ✅ **Docker native** - uses your existing setup
- ✅ **Auto-scaling** and monitoring
- ✅ **Great free tier** (500 hours/month)
- ✅ **Simple pricing** - no surprises
- ✅ **GitHub integration** - auto-deploy on push

### Perfect For:
- Full-stack applications
- Teams wanting simplicity
- Production deployments
- Auto-scaling apps

## 📝 Deployment Steps Summary

1. **Connect**: Link your GitHub repo
2. **Configure**: Add environment variables
3. **Deploy**: Railway handles everything else
4. **Scale**: Automatically scales with traffic

Your app will be live at `https://your-app.railway.app` with:
- Full backend functionality
- Database persistence  
- File uploads working
- AI analysis operational
- Monitoring dashboard

**No need for multiple platforms - Railway does it all!** 🚂