# 🚀 Free Deployment Guide

This guide will help you deploy your Financial News Extraction System on completely free hosting platforms.

## 📋 Prerequisites

- GitHub account (free)
- Basic familiarity with Git

## 🌟 Recommended Option: Render (Free Tier)

**Why Render?**
- ✅ 750 hours/month free (enough for 24/7 operation)
- ✅ Automatic deployments from GitHub
- ✅ Built-in SSL certificates
- ✅ Easy setup, no credit card required

### Steps:

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/financial-news-extractor.git
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Choose these settings:
     - **Name**: financial-news-extractor
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app`
   - Click "Create Web Service"

3. **Wait for deployment** (5-10 minutes)
4. **Access your app** at the provided URL

## 🚅 Alternative Option 1: Railway (Free $5 Credit)

**Why Railway?**
- ✅ $5 free credit monthly
- ✅ Simple deployment process
- ✅ Automatic HTTPS

### Steps:

1. **Push to GitHub** (same as above)
2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Python and deploy
   - Configuration is handled by `railway.toml`

## ✈️ Alternative Option 2: Fly.io (Free Tier)

**Why Fly.io?**
- ✅ 256MB RAM free
- ✅ 3GB storage
- ✅ Global edge locations

### Steps:

1. **Install Fly CLI:**
   ```bash
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Setup Fly:**
   ```bash
   fly auth signup  # or fly auth login
   fly launch       # Follow prompts, choose free tier
   fly deploy
   ```

## 🖥️ Alternative Option 3: PythonAnywhere (Free Tier)

**Why PythonAnywhere?**
- ✅ Always-on free tier
- ✅ Web-based console
- ✅ No credit card required

### Steps:

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com)
2. **Upload your files** via the file manager
3. **Setup web app:**
   - Go to "Web" tab
   - Create new web app
   - Choose Python 3.9
   - Set source code directory
   - Configure WSGI file

## 📱 Local Development

For testing locally before deployment:

### Linux/macOS:
```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
python app.py
```

### Windows:
```cmd
setup.bat
venv\Scripts\activate.bat
python app.py
```

Open browser to `http://localhost:5000`

## 🎛️ Environment Configuration

### Required Environment Variables (for production):
- `PORT`: Automatically set by hosting platforms
- `FLASK_ENV`: Set to `production`

### Optional Optimizations:
- `WORKERS`: Number of gunicorn workers (default: 1 for free tiers)
- `TIMEOUT`: Request timeout in seconds (default: 120)

## 🔧 Platform-Specific Notes

### Render:
- Uses `render.yaml` for configuration
- Automatic deploys on git push
- Logs available in dashboard

### Railway:
- Uses `railway.toml` for configuration
- Automatic scaling based on usage
- Built-in database options available

### Fly.io:
- Uses `Dockerfile` for deployment
- Excellent for global deployment
- More technical setup required

## 🚨 Important Notes for Free Tiers

### Resource Limitations:
- **Memory**: 512MB - 1GB (sufficient for this app)
- **CPU**: Shared/limited (AI models load slower)
- **Storage**: 1-3GB (enough for SQLite + models)
- **Bandwidth**: 100GB/month (more than enough)

### Performance Tips:
1. **AI Models**: First load takes 2-3 minutes (models download)
2. **Cold Starts**: Free tiers may sleep after inactivity
3. **Scaling**: Keep to 1 worker to stay within memory limits
4. **Database**: SQLite is perfect for free tier constraints

## 🔄 CI/CD (Automatic Deployments)

All recommended platforms support automatic deployments:
- Push to GitHub → Automatic deployment
- No manual intervention required
- Rollback capabilities available

## 💾 Data Persistence

- **SQLite database**: Persists automatically on most platforms
- **Generated newsletters**: Stored in `/data` directory
- **AI models**: Cached after first download

## 🆘 Troubleshooting

### Common Issues:

**Memory Errors:**
- Use only 1 worker: `--workers 1`
- Increase timeout: `--timeout 120`

**AI Model Loading:**
- Models download on first use (be patient)
- Subsequent loads are much faster

**Cold Start Issues:**
- First request may timeout
- Keep app warm with periodic pings

### Support:
- Check platform logs for specific errors
- Refer to platform documentation
- GitHub issues for app-specific problems

## 🎉 Success!

Once deployed, your Financial News Extraction System will:
- ✅ Scrape financial news automatically
- ✅ Analyze content with AI models
- ✅ Generate professional newsletters
- ✅ Run completely free 24/7

**Remember**: This is a production-ready system that costs $0 to run!