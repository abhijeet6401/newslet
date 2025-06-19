from flask import Flask, render_template, jsonify, request
import logging
import json
import os
from datetime import datetime
import threading
from fixed_financial_scraper import FinancialNewsScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-change-in-production')

# Global variables for scraping status
scraping_status = {
    'is_running': False,
    'last_run': None,
    'article_count': 0,
    'error_message': None,
    'progress': 0
}

class ScrapingTask:
    def __init__(self):
        self.scraper = None

    def run_scraping(self):
        """Run scraping in background thread"""
        global scraping_status

        try:
            logger.info("Starting background scraping task...")
            scraping_status['is_running'] = True
            scraping_status['error_message'] = None
            scraping_status['progress'] = 10

            # Initialize scraper
            self.scraper = FinancialNewsScraper()
            scraping_status['progress'] = 30

            # Start scraping
            articles = self.scraper.start_scraping()
            scraping_status['progress'] = 90

            # Update status
            scraping_status['article_count'] = len(articles)
            scraping_status['last_run'] = datetime.now().isoformat()
            scraping_status['progress'] = 100

            logger.info(f"Scraping completed successfully. Found {len(articles)} articles.")

        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            logger.error(error_msg)
            scraping_status['error_message'] = error_msg
            scraping_status['progress'] = 0

        finally:
            scraping_status['is_running'] = False

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'scraper_available': True
    })

@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """Start scraping process"""
    global scraping_status

    try:
        if scraping_status['is_running']:
            return jsonify({
                'success': False,
                'message': 'Scraping is already in progress'
            }), 400

        # Reset status
        scraping_status = {
            'is_running': True,
            'last_run': None,
            'article_count': 0,
            'error_message': None,
            'progress': 0
        }

        # Start scraping in background thread
        task = ScrapingTask()
        thread = threading.Thread(target=task.run_scraping)
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'message': 'Scraping started successfully'
        })

    except Exception as e:
        logger.error(f"Error starting scraping: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to start scraping: {str(e)}'
        }), 500

@app.route('/api/status')
def get_status():
    """Get scraping status"""
    return jsonify(scraping_status)

@app.route('/api/articles')
def get_articles():
    """Get latest scraped articles"""
    try:
        # Look for the most recent JSON file
        json_files = [f for f in os.listdir('.') if f.startswith('financial_news_') and f.endswith('.json')]

        if not json_files:
            return jsonify({
                'success': False,
                'message': 'No articles found. Please run scraping first.'
            })

        # Get the most recent file
        latest_file = sorted(json_files)[-1]

        with open(latest_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)

        return jsonify({
            'success': True,
            'articles': articles,
            'count': len(articles),
            'file': latest_file
        })

    except Exception as e:
        logger.error(f"Error getting articles: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error retrieving articles: {str(e)}'
        }), 500

@app.route('/api/test')
def test_scraper():
    """Test scraper functionality"""
    try:
        scraper = FinancialNewsScraper()

        # Test one RSS feed
        test_articles = scraper.scrape_rss_feed(
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'yahoo_finance_test'
        )

        return jsonify({
            'success': True,
            'message': 'Scraper test completed successfully',
            'test_articles_count': len(test_articles),
            'sample_article': test_articles[0] if test_articles else None
        })

    except Exception as e:
        logger.error(f"Scraper test failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Scraper test failed: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

# Create templates directory and basic HTML template
def create_templates():
    """Create templates directory and basic HTML template"""
    os.makedirs('templates', exist_ok=True)

    # Create simple HTML template (avoiding CSS syntax issues)
    html_content = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>Financial News Scraper</title>',
        '    <style>',
        '        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }',
        '        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }',
        '        .button { background-color: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; }',
        '        .button:hover { background-color: #0056b3; }',
        '        .status { margin: 20px 0; padding: 15px; border-radius: 5px; }',
        '        .status.success { background-color: #d4edda; color: #155724; }',
        '        .status.error { background-color: #f8d7da; color: #721c24; }',
        '        .status.info { background-color: #d1ecf1; color: #0c5460; }',
        '        .progress { width: 100%; background-color: #e9ecef; border-radius: 5px; }',
        '        .progress-bar { height: 25px; background-color: #007bff; text-align: center; line-height: 25px; color: white; }',
        '    </style>',
        '</head>',
        '<body>',
        '    <div class="container">',
        '        <h1>🚀 Financial News Scraper</h1>',
        '        <p>Free, automated financial news extraction from top sources</p>',
        '        ',
        '        <button class="button" onclick="startScraping()" id="scrapeBtn">Start Scraping</button>',
        '        <button class="button" onclick="getStatus()">Check Status</button>',
        '        <button class="button" onclick="getArticles()">View Articles</button>',
        '        <button class="button" onclick="testScraper()">Test Scraper</button>',
        '        ',
        '        <div id="status"></div>',
        '        <div id="progress" style="display: none;">',
        '            <div class="progress">',
        '                <div class="progress-bar" id="progressBar" style="width: 0%;">0%</div>',
        '            </div>',
        '        </div>',
        '        <div id="results"></div>',
        '    </div>',
        '',
        '    <script>',
        '        async function startScraping() {',
        '            document.getElementById("scrapeBtn").disabled = true;',
        '            try {',
        '                const response = await fetch("/api/scrape", { method: "POST" });',
        '                const data = await response.json();',
        '                if (data.success) {',
        '                    showStatus("Scraping started!", "success");',
        '                } else {',
        '                    showStatus(data.message, "error");',
        '                }',
        '            } catch (error) {',
        '                showStatus("Error: " + error.message, "error");',
        '            }',
        '            document.getElementById("scrapeBtn").disabled = false;',
        '        }',
        '        ',
        '        async function getStatus() {',
        '            const response = await fetch("/api/status");',
        '            const status = await response.json();',
        '            const message = `Status: ${status.is_running ? "Running" : "Idle"}<br>Articles: ${status.article_count}`;',
        '            showStatus(message, "info");',
        '        }',
        '        ',
        '        async function getArticles() {',
        '            const response = await fetch("/api/articles");',
        '            const data = await response.json();',
        '            if (data.success) {',
        '                showStatus(`Found ${data.count} articles`, "success");',
        '                displayArticles(data.articles);',
        '            } else {',
        '                showStatus(data.message, "error");',
        '            }',
        '        }',
        '        ',
        '        async function testScraper() {',
        '            const response = await fetch("/api/test");',
        '            const data = await response.json();',
        '            showStatus(data.message, data.success ? "success" : "error");',
        '        }',
        '        ',
        '        function showStatus(message, type) {',
        '            document.getElementById("status").innerHTML = `<div class="status ${type}">${message}</div>`;',
        '        }',
        '        ',
        '        function displayArticles(articles) {',
        '            let html = "<h3>Latest Articles</h3>";',
        '            articles.slice(0, 5).forEach(article => {',
        '                html += `<div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">`,
        '                html += `<h4>${article.title}</h4>`;',
        '                html += `<p>Source: ${article.source}</p>`;',
        '                html += `<p>${article.description}</p>`;',
        '                html += `</div>`;',
        '            });',
        '            document.getElementById("results").innerHTML = html;',
        '        }',
        '    </script>',
        '</body>',
        '</html>'
    ]

    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))

if __name__ == '__main__':
    try:
        # Create templates
        create_templates()

        # Get port from environment or use default
        port = int(os.environ.get('PORT', 5000))

        print("🚀 Financial News Scraper Flask App")
        print("=" * 40)
        print(f"Starting server on port {port}")
        print(f"Access: http://localhost:{port}")
        print("=" * 40)

        app.run(
            host='0.0.0.0',
            port=port,
            debug=False
        )

    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
        print(f"\n❌ Error starting Flask app: {str(e)}")
