import logging
from datetime import datetime
import json
import csv
from io import StringIO

logger = logging.getLogger(__name__)

class NewsletterGenerator:
    def __init__(self):
        pass

    def generate_newsletter(self, articles, title, format_type='html'):
        """Generate newsletter in specified format"""
        if format_type == 'html':
            return self.generate_html_newsletter(articles, title)
        elif format_type == 'csv':
            return self.generate_csv_newsletter(articles)
        elif format_type == 'json':
            return self.generate_json_newsletter(articles)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def generate_html_newsletter(self, articles, title):
        """Generate HTML newsletter"""
        # Group articles by category
        categories = {}
        for article in articles:
            category = article.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(article)
        
        # Start building HTML
        html_parts = []
        
        # HTML header
        html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f9f9f9;
        }}
        .newsletter-container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.2em;
            font-weight: 300;
        }}
        .content {{
            padding: 30px;
        }}
        .summary {{
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 0 5px 5px 0;
        }}
        .category-section {{
            margin-bottom: 40px;
        }}
        .category-header {{
            background: #343a40;
            color: white;
            padding: 15px 20px;
            margin: 0 0 20px 0;
            border-radius: 5px;
            font-size: 1.3em;
            font-weight: 500;
        }}
        .article {{
            margin-bottom: 25px;
            padding: 20px;
            background: #fff;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .article-title {{
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        .article-title a {{
            text-decoration: none;
            color: #2c3e50;
        }}
        .article-meta {{
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 15px;
        }}
        .source {{
            font-weight: 600;
            text-transform: uppercase;
        }}
        .sentiment {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
            margin-left: 10px;
        }}
        .sentiment-positive {{
            background: #d4edda;
            color: #155724;
        }}
        .sentiment-negative {{
            background: #f8d7da;
            color: #721c24;
        }}
        .sentiment-neutral {{
            background: #e2e3e5;
            color: #383d41;
        }}
        .importance {{
            float: right;
            background: #ffc107;
            color: #212529;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .importance.high {{
            background: #dc3545;
            color: white;
        }}
        .importance.medium {{
            background: #fd7e14;
            color: white;
        }}
        .article-summary {{
            font-size: 0.95em;
            line-height: 1.5;
            color: #495057;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #6c757d;
            text-transform: uppercase;
        }}
    </style>
</head>
<body>
    <div class="newsletter-container">
        <div class="header">
            <h1>{title}</h1>
            <div class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y')}</div>
        </div>
        <div class="content">""")
        
        # Add summary and statistics
        html_parts.append(self.generate_summary_section(articles))
        html_parts.append(self.generate_statistics_section(articles))
        
        # Add content sections for each category
        for category, category_articles in categories.items():
            html_parts.append(f'<div class="category-section">')
            html_parts.append(f'<h2 class="category-header">{category} ({len(category_articles)} articles)</h2>')
            
            for article in category_articles:
                html_parts.append(self.generate_article_html(article))
            
            html_parts.append('</div>')
        
        # Close HTML
        html_parts.append(f"""
        </div>
        <div class="footer">
            <p><strong>Newsletter Statistics:</strong> {len(articles)} articles analyzed from {len(set(article.get('source', 'Unknown') for article in articles))} sources</p>
            <p>Generated by Free Financial News Extraction System</p>
            <p><em>This newsletter contains AI-generated summaries. Please verify important information independently.</em></p>
        </div>
    </div>
</body>
</html>""")
        
        return ''.join(html_parts)

    def generate_summary_section(self, articles):
        """Generate executive summary section"""
        if not articles:
            return ""
        
        # Calculate key metrics
        avg_sentiment = sum(article.get('sentiment_score', 0) for article in articles) / len(articles)
        high_importance_count = sum(1 for article in articles if article.get('importance_score', 0) > 0.7)
        
        # Get top 3 most important articles
        top_articles = sorted(articles, key=lambda x: x.get('importance_score', 0), reverse=True)[:3]
        
        sentiment_text = "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral"
        
        summary_parts = [
            '<div class="summary">',
            '<h2>Executive Summary</h2>',
            f'<p>This newsletter covers <strong>{len(articles)} articles</strong> from multiple financial news sources.',
            f'The overall market sentiment appears <strong>{sentiment_text}</strong> with an average sentiment score of <strong>{avg_sentiment:.2f}</strong>.</p>',
            f'<p><strong>{high_importance_count} high-priority articles</strong> require immediate attention.</p>',
            '<h3>Top Stories This Period:</h3>',
            '<ul>'
        ]
        
        for article in top_articles:
            summary_parts.append(f'<li><strong>{article.get("title", "")}</strong> (Importance: {article.get("importance_score", 0):.1f}/1.0)</li>')
        
        summary_parts.extend(['</ul>', '</div>'])
        
        return ''.join(summary_parts)

    def generate_statistics_section(self, articles):
        """Generate statistics section"""
        if not articles:
            return ""
        
        # Calculate statistics
        total_articles = len(articles)
        positive_sentiment = sum(1 for a in articles if a.get('sentiment_score', 0) > 0.1)
        negative_sentiment = sum(1 for a in articles if a.get('sentiment_score', 0) < -0.1)
        high_importance = sum(1 for a in articles if a.get('importance_score', 0) > 0.7)
        
        return f"""
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{total_articles}</div>
                <div class="stat-label">Total Articles</div>
            </div>
            <div class="stat">
                <div class="stat-number">{positive_sentiment}</div>
                <div class="stat-label">Positive</div>
            </div>
            <div class="stat">
                <div class="stat-number">{negative_sentiment}</div>
                <div class="stat-label">Negative</div>
            </div>
            <div class="stat">
                <div class="stat-number">{high_importance}</div>
                <div class="stat-label">High Priority</div>
            </div>
        </div>
        """

    def generate_article_html(self, article):
        """Generate HTML for a single article"""
        title = article.get('title', 'No Title')
        url = article.get('url', '#')
        source = article.get('source', 'Unknown').upper()
        published_date = article.get('published_date', '')
        sentiment_score = article.get('sentiment_score', 0)
        importance_score = article.get('importance_score', 0)
        summary = article.get('summary', article.get('content', ''))
        
        # Format date
        date_str = ""
        if published_date:
            try:
                if isinstance(published_date, str):
                    date_obj = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%B %d, %Y')
            except:
                date_str = str(published_date)[:10]
        
        # Determine sentiment class
        if sentiment_score > 0.1:
            sentiment_class = "sentiment-positive"
            sentiment_text = "Positive"
        elif sentiment_score < -0.1:
            sentiment_class = "sentiment-negative"
            sentiment_text = "Negative"
        else:
            sentiment_class = "sentiment-neutral"
            sentiment_text = "Neutral"
        
        # Determine importance class
        if importance_score > 0.7:
            importance_class = "importance high"
            importance_text = "High"
        elif importance_score > 0.5:
            importance_class = "importance medium"
            importance_text = "Medium"
        else:
            importance_class = "importance"
            importance_text = "Standard"
        
        return f"""
        <div class="article">
            <div class="article-title">
                <a href="{url}" target="_blank">{title}</a>
            </div>
            <div class="article-meta">
                <span class="source">{source}</span>
                {f"• {date_str}" if date_str else ""}
                <span class="sentiment {sentiment_class}">{sentiment_text}</span>
                <span class="{importance_class}">{importance_text} Priority</span>
            </div>
            <div class="article-summary">{summary[:300]}{"..." if len(summary) > 300 else ""}</div>
        </div>
        """

    def generate_csv_newsletter(self, articles):
        """Generate CSV format newsletter"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Title', 'Source', 'Published Date', 'URL', 'Category',
            'Sentiment Score', 'Importance Score', 'Summary'
        ])
        
        # Write articles
        for article in sorted(articles, key=lambda x: x.get('importance_score', 0), reverse=True):
            writer.writerow([
                article.get('title', ''),
                article.get('source', ''),
                article.get('published_date', ''),
                article.get('url', ''),
                article.get('category', ''),
                article.get('sentiment_score', 0),
                article.get('importance_score', 0),
                article.get('summary', '')
            ])
        
        return output.getvalue()

    def generate_json_newsletter(self, articles):
        """Generate JSON format newsletter"""
        newsletter_data = {
            'metadata': {
                'title': f'Financial Newsletter - {datetime.now().strftime("%B %Y")}',
                'generated_date': datetime.now().isoformat(),
                'total_articles': len(articles),
                'sources': list(set(article.get('source', 'Unknown') for article in articles))
            },
            'statistics': {
                'average_sentiment': sum(article.get('sentiment_score', 0) for article in articles) / len(articles) if articles else 0,
                'high_importance_count': sum(1 for article in articles if article.get('importance_score', 0) > 0.7),
                'positive_sentiment_count': sum(1 for article in articles if article.get('sentiment_score', 0) > 0.1),
                'negative_sentiment_count': sum(1 for article in articles if article.get('sentiment_score', 0) < -0.1)
            },
            'articles': sorted(articles, key=lambda x: x.get('importance_score', 0), reverse=True)
        }
        
        return json.dumps(newsletter_data, indent=2, default=str)