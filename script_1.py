# Create the main Flask application file with proper indentation
app_py_content = """from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import os
from datetime import datetime, timedelta
import threading
import time
from scraper import NewsScaper
from ai_analyzer import AIAnalyzer
from newsletter_generator import NewsletterGenerator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize components
scraper = NewsScaper()
analyzer = AIAnalyzer()
newsletter_gen = NewsletterGenerator()

# Global variable to track scraping status
scraping_status = {"status": "idle", "progress": 0, "message": ""}

def init_db():
    \"\"\"Initialize SQLite database\"\"\"
    conn = sqlite3.connect('data/news.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            url TEXT UNIQUE,
            source TEXT,
            published_date DATETIME,
            scraped_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            sentiment_score REAL DEFAULT 0,
            importance_score REAL DEFAULT 0,
            category TEXT,
            summary TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    \"\"\"Main dashboard\"\"\"
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    \"\"\"Start the news scraping process\"\"\"
    global scraping_status
    
    if scraping_status["status"] == "running":
        return jsonify({"error": "Scraping already in progress"}), 400
    
    data = request.json
    sources = data.get('sources', ['yahoo', 'reuters', 'marketwatch'])
    days_back = data.get('days_back', 7)
    
    # Start scraping in background thread
    thread = threading.Thread(target=scrape_news_background, args=(sources, days_back))
    thread.start()
    
    return jsonify({"message": "Scraping started", "status": "running"})

def scrape_news_background(sources, days_back):
    \"\"\"Background function to scrape news\"\"\"
    global scraping_status
    
    try:
        scraping_status = {"status": "running", "progress": 0, "message": "Starting scraper..."}
        
        # Scrape from each source
        total_sources = len(sources)
        all_articles = []
        
        for i, source in enumerate(sources):
            scraping_status["message"] = f"Scraping {source}..."
            scraping_status["progress"] = int((i / total_sources) * 50)  # First 50% for scraping
            
            articles = scraper.scrape_source(source, days_back)
            all_articles.extend(articles)
            time.sleep(1)  # Be nice to servers
        
        # Analyze articles with AI
        scraping_status["message"] = "Analyzing articles with AI..."
        scraping_status["progress"] = 60
        
        analyzed_articles = analyzer.analyze_articles(all_articles)
        
        # Save to database
        scraping_status["message"] = "Saving to database..."
        scraping_status["progress"] = 80
        
        save_articles_to_db(analyzed_articles)
        
        scraping_status = {
            "status": "completed", 
            "progress": 100, 
            "message": f"Successfully processed {len(analyzed_articles)} articles"
        }
        
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        scraping_status = {
            "status": "error", 
            "progress": 0, 
            "message": f"Error: {str(e)}"
        }

def save_articles_to_db(articles):
    \"\"\"Save articles to SQLite database\"\"\"
    conn = sqlite3.connect('data/news.db')
    c = conn.cursor()
    
    for article in articles:
        try:
            c.execute('''
                INSERT OR REPLACE INTO articles 
                (title, content, url, source, published_date, sentiment_score, 
                 importance_score, category, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article['title'],
                article.get('content', ''),
                article['url'],
                article['source'],
                article.get('published_date'),
                article.get('sentiment_score', 0),
                article.get('importance_score', 0),
                article.get('category', 'General'),
                article.get('summary', '')
            ))
        except sqlite3.IntegrityError:
            # Article already exists, skip
            pass
    
    conn.commit()
    conn.close()

@app.route('/api/status')
def get_status():
    \"\"\"Get current scraping status\"\"\"
    return jsonify(scraping_status)

@app.route('/api/articles')
def get_articles():
    \"\"\"Get articles from database\"\"\"
    conn = sqlite3.connect('data/news.db')
    c = conn.cursor()
    
    # Get query parameters
    limit = request.args.get('limit', 50, type=int)
    source = request.args.get('source', '')
    min_importance = request.args.get('min_importance', 0, type=float)
    
    query = '''
        SELECT * FROM articles 
        WHERE importance_score >= ?
    '''
    params = [min_importance]
    
    if source:
        query += ' AND source = ?'
        params.append(source)
    
    query += ' ORDER BY importance_score DESC, published_date DESC LIMIT ?'
    params.append(limit)
    
    c.execute(query, params)
    
    columns = [description[0] for description in c.description]
    articles = [dict(zip(columns, row)) for row in c.fetchall()]
    
    conn.close()
    
    return jsonify(articles)

@app.route('/api/newsletter/generate', methods=['POST'])
def generate_newsletter():
    \"\"\"Generate newsletter from selected articles\"\"\"
    data = request.json
    
    # Get parameters
    title = data.get('title', f'Financial Newsletter - {datetime.now().strftime("%B %Y")}')
    min_importance = data.get('min_importance', 0.5)
    max_articles = data.get('max_articles', 20)
    format_type = data.get('format', 'html')
    
    # Get articles from database
    conn = sqlite3.connect('data/news.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM articles 
        WHERE importance_score >= ?
        ORDER BY importance_score DESC, published_date DESC 
        LIMIT ?
    ''', (min_importance, max_articles))
    
    columns = [description[0] for description in c.description]
    articles = [dict(zip(columns, row)) for row in c.fetchall()]
    
    conn.close()
    
    if not articles:
        return jsonify({"error": "No articles found matching criteria"}), 400
    
    # Generate newsletter
    newsletter_content = newsletter_gen.generate_newsletter(
        articles, title, format_type
    )
    
    # Save newsletter file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"newsletter_{timestamp}.{format_type}"
    filepath = os.path.join('data', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(newsletter_content)
    
    return jsonify({
        "message": "Newsletter generated successfully",
        "filename": filename,
        "article_count": len(articles)
    })

@app.route('/api/newsletter/download/<filename>')
def download_newsletter(filename):
    \"\"\"Download generated newsletter\"\"\"
    filepath = os.path.join('data', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

@app.route('/api/stats')
def get_stats():
    \"\"\"Get database statistics\"\"\"
    conn = sqlite3.connect('data/news.db')
    c = conn.cursor()
    
    # Get basic stats
    c.execute('SELECT COUNT(*) FROM articles')
    total_articles = c.fetchone()[0]
    
    c.execute('SELECT COUNT(DISTINCT source) FROM articles')
    total_sources = c.fetchone()[0]
    
    c.execute('SELECT source, COUNT(*) FROM articles GROUP BY source')
    source_counts = dict(c.fetchall())
    
    c.execute('''
        SELECT AVG(sentiment_score), AVG(importance_score) 
        FROM articles WHERE sentiment_score > 0
    ''')
    avg_scores = c.fetchone()
    
    conn.close()
    
    return jsonify({
        "total_articles": total_articles,
        "total_sources": total_sources,
        "source_breakdown": source_counts,
        "average_sentiment": avg_scores[0] if avg_scores[0] else 0,
        "average_importance": avg_scores[1] if avg_scores[1] else 0
    })

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Get port from environment (for deployment)
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host='0.0.0.0', port=port, debug=False)
"""

# Save the file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py_content)

print("✅ Created app.py - Main Flask application")
print("File size:", len(app_py_content), "characters")