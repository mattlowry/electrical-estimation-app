# 🚀 Vercel Deployment Guide

## Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/mattlowry/electrical-estimation-app)

## Step-by-Step Deployment

### 1. Prerequisites
- Vercel account ([sign up free](https://vercel.com/signup))
- GitHub repository (already created ✅)

### 2. Deploy to Vercel

**Option A: One-Click Deploy**
1. Click the "Deploy with Vercel" button above
2. Connect your GitHub account
3. Select the repository
4. Configure environment variables
5. Click "Deploy"

**Option B: Manual Deploy**
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the configuration
5. Configure environment variables (see below)
6. Click "Deploy"

### 3. Environment Variables

Add these environment variables in Vercel dashboard:

```bash
# Required
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# Optional (with defaults)
FLASK_ENV=production
```

### 4. Domain Configuration

- Vercel provides a free domain: `your-app.vercel.app`
- Add custom domain in Project Settings → Domains

### 5. API Endpoints

Your deployed API will be available at:
- Health Check: `https://your-app.vercel.app/api/health`
- Estimates: `https://your-app.vercel.app/api/estimates`
- Upload: `https://your-app.vercel.app/api/upload`
- AI Analysis: `https://your-app.vercel.app/api/analyze`

## ⚠️ Vercel Limitations

**Current Setup:**
- ✅ Frontend fully functional
- ✅ API endpoints working (demo mode)
- ❌ Database persistence (Vercel functions are stateless)
- ❌ File uploads (no persistent storage)
- ❌ Background jobs (Celery not supported)

**For Full Features:**
Consider deploying backend separately on:
- Railway
- Render
- DigitalOcean App Platform
- AWS/GCP/Azure

## 🔧 Configuration Files

The following files enable Vercel deployment:

- `vercel.json` - Vercel configuration
- `api/index.py` - Serverless function entry point
- `requirements.txt` - Python dependencies
- `package.json` - Build configuration

## 🚀 Production Recommendations

For a full production deployment:

1. **Database**: Use PlanetScale, Supabase, or MongoDB Atlas
2. **File Storage**: Use Cloudinary, AWS S3, or similar
3. **Background Jobs**: Use Vercel Edge Functions or external service
4. **Monitoring**: Use Vercel Analytics + Sentry

## 🛠️ Local Development

```bash
# Install Vercel CLI
npm i -g vercel

# Run locally
vercel dev

# Deploy
vercel --prod
```

## 📝 Next Steps After Deploy

1. Test all API endpoints
2. Configure custom domain
3. Set up monitoring
4. Add database for persistence
5. Configure file storage for uploads

Your app is now live on Vercel! 🎉