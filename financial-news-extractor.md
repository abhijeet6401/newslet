# Free Financial News Extraction System

A completely free, deployable system that scrapes top financial websites and extracts important news for monthly newsletters using open-source AI models.

## 🎯 Features

- **100% Free**: No API keys required, uses local AI models
- **Multi-Source Scraping**: Yahoo Finance, Reuters, MarketWatch, CNBC, Benzinga
- **AI-Powered Analysis**: Local sentiment analysis and news ranking
- **Web Interface**: Easy-to-use dashboard for newsletter generation
- **Multiple Export Formats**: HTML, CSV, JSON output
- **Free Deployment**: Deploy on Render, Railway, or Fly.io for free

## 🚀 Quick Start

### Local Setup

```bash
# Clone and setup
git clone <your-repo-url>
cd financial-news-extractor
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run locally
python app.py
```

### Free Deployment Options

1. **Render** (Recommended): Free tier with 750 hours/month
2. **Railway**: Free $5 credit monthly
3. **Fly.io**: Free tier with 256MB RAM
4. **Vercel**: For frontend deployment

## 🔧 Configuration

All configuration is handled through environment variables or the web interface - no API keys needed!

## 📋 Usage

1. Open the web interface
2. Select news sources to scrape
3. Choose date range and filters
4. Generate newsletter content
5. Export in your preferred format

## 🏗️ Architecture

- **Backend**: Flask web application
- **AI Models**: Hugging Face transformers (local)
- **Scraping**: BeautifulSoup + Requests
- **Database**: SQLite (file-based, no external DB needed)
- **Frontend**: HTML/CSS/JavaScript

## 📁 Project Structure

```
financial-news-extractor/
├── app.py                 # Main Flask application
├── scraper.py            # News scraping module
├── ai_analyzer.py        # Local AI analysis
├── newsletter_generator.py # Newsletter creation
├── requirements.txt      # Python dependencies
├── render.yaml          # Render deployment config
├── Dockerfile           # Docker configuration
├── static/              # CSS, JS, images
├── templates/           # HTML templates
└── data/                # SQLite database and exports
```

## 🔄 How It Works

1. **Scrape**: Fetches news from free RSS feeds and web sources
2. **Analyze**: Uses local Hugging Face models for sentiment and importance
3. **Rank**: Scores articles based on relevance and impact
4. **Generate**: Creates formatted newsletter content
5. **Export**: Outputs in HTML, CSV, or JSON formats

## 🆓 Why This is Completely Free

- **No API Costs**: Uses open-source Hugging Face models locally
- **Free News Sources**: Scrapes public RSS feeds and websites
- **Free Hosting**: Deploy on platforms with generous free tiers
- **No External Dependencies**: SQLite database, no external services

## 🛠️ Tech Stack

- **Python 3.8+**
- **Flask** - Web framework
- **Transformers** - Hugging Face AI models
- **BeautifulSoup** - Web scraping
- **SQLite** - Local database
- **Bootstrap** - UI framework

## 📊 Performance

- Processes ~50 articles in 2-3 minutes
- Memory usage: ~500MB (including AI models)
- Disk space: ~1GB (with downloaded models)

## 🔒 Privacy & Security

- All data processed locally
- No external API calls for AI processing
- No user data stored on external servers
- Respects robots.txt and rate limiting

## 🤝 Contributing

Contributions welcome! This is an open-source project designed to help investment funds create better newsletters without costly subscriptions.

## 📄 License

MIT License - Use freely for commercial and personal projects.