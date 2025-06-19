import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
import time
import logging
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

class NewsScaper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # RSS Feed URLs for different sources
        self.rss_feeds = {
            'yahoo': 'https://finance.yahoo.com/news/rssindex',
            'reuters': 'https://feeds.reuters.com/reuters/businessNews',
            'marketwatch': 'https://feeds.marketwatch.com/marketwatch/realtimeheadlines',
            'cnbc': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'benzinga': 'https://www.benzinga.com/feed'
        }

        # Website scraping URLs
        self.website_urls = {
            'yahoo_web': 'https://finance.yahoo.com/news/',
            'reuters_web': 'https://www.reuters.com/business/',
            'marketwatch_web': 'https://www.marketwatch.com/newsviewer'
        }

    def scrape_source(self, source, days_back=7):
        """Scrape news from a specific source"""
        try:
            logger.info(f"Scraping {source}...")

            # Try RSS feed first, then fallback to web scraping
            if source in self.rss_feeds:
                articles = self.scrape_rss(source, days_back)
                if articles:
                    return articles

            # Fallback to web scraping
            web_source = f"{source}_web"
            if web_source in self.website_urls:
                return self.scrape_website(web_source, days_back)

            logger.warning(f"No scraping method available for {source}")
            return []

        except Exception as e:
            logger.error(f"Error scraping {source}: {e}")
            return []

    def scrape_rss(self, source, days_back):
        """Scrape news from RSS feeds"""
        try:
            feed_url = self.rss_feeds[source]
            logger.info(f"Fetching RSS feed: {feed_url}")

            feed = feedparser.parse(feed_url)

            if not feed.entries:
                logger.warning(f"No entries found in RSS feed for {source}")
                return []

            articles = []
            cutoff_date = datetime.now() - timedelta(days=days_back)

            for entry in feed.entries:
                try:
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])

                    # Skip old articles
                    if pub_date and pub_date < cutoff_date:
                        continue

                    # Extract article data
                    article = {
                        'title': entry.title,
                        'url': entry.link,
                        'source': source,
                        'published_date': pub_date.isoformat() if pub_date else None,
                        'content': self.extract_content_from_entry(entry),
                        'summary': entry.summary if hasattr(entry, 'summary') else ''
                    }

                    articles.append(article)

                except Exception as e:
                    logger.error(f"Error processing RSS entry: {e}")
                    continue

            logger.info(f"Scraped {len(articles)} articles from {source} RSS")
            return articles

        except Exception as e:
            logger.error(f"Error scraping RSS for {source}: {e}")
            return []

    def extract_content_from_entry(self, entry):
        """Extract content from RSS entry"""
        content = ""

        # Try different content fields
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if isinstance(entry.content, list) else entry.content
        elif hasattr(entry, 'description'):
            content = entry.description
        elif hasattr(entry, 'summary'):
            content = entry.summary

        # Clean HTML tags
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text().strip()

        return content

    def scrape_website(self, source, days_back):
        """Scrape news directly from websites"""
        try:
            url = self.website_urls[source]
            logger.info(f"Scraping website: {url}")

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            if 'yahoo' in source:
                articles = self.scrape_yahoo_web(soup, days_back)
            elif 'reuters' in source:
                articles = self.scrape_reuters_web(soup, days_back)
            elif 'marketwatch' in source:
                articles = self.scrape_marketwatch_web(soup, days_back)

            logger.info(f"Scraped {len(articles)} articles from {source} website")
            return articles

        except Exception as e:
            logger.error(f"Error scraping website {source}: {e}")
            return []

    def scrape_yahoo_web(self, soup, days_back):
        """Scrape Yahoo Finance website"""
        articles = []

        # Look for news articles
        news_items = soup.find_all(['h3', 'h4'], class_=re.compile(r'.*title.*|.*headline.*'))

        for item in news_items[:20]:  # Limit to 20 articles
            try:
                link_elem = item.find('a') or item.find_parent('a')
                if not link_elem:
                    continue

                title = item.get_text().strip()
                url = link_elem.get('href', '')

                if url.startswith('/'):
                    url = urljoin('https://finance.yahoo.com', url)

                if title and url:
                    article = {
                        'title': title,
                        'url': url,
                        'source': 'yahoo',
                        'published_date': datetime.now().isoformat(),
                        'content': '',
                        'summary': ''
                    }
                    articles.append(article)

            except Exception as e:
                logger.error(f"Error processing Yahoo article: {e}")
                continue

        return articles

    def scrape_reuters_web(self, soup, days_back):
        """Scrape Reuters website"""
        articles = []

        # Look for news articles
        story_items = soup.find_all('div', class_=re.compile(r'.*story.*|.*article.*'))

        for item in story_items[:20]:  # Limit to 20 articles
            try:
                title_elem = item.find(['h3', 'h4', 'h2'])
                link_elem = item.find('a')

                if not title_elem or not link_elem:
                    continue

                title = title_elem.get_text().strip()
                url = link_elem.get('href', '')

                if url.startswith('/'):
                    url = urljoin('https://www.reuters.com', url)

                if title and url:
                    article = {
                        'title': title,
                        'url': url,
                        'source': 'reuters',
                        'published_date': datetime.now().isoformat(),
                        'content': '',
                        'summary': ''
                    }
                    articles.append(article)

            except Exception as e:
                logger.error(f"Error processing Reuters article: {e}")
                continue

        return articles

    def scrape_marketwatch_web(self, soup, days_back):
        """Scrape MarketWatch website"""
        articles = []

        # Look for news articles
        headline_items = soup.find_all(['h3', 'h4'], class_=re.compile(r'.*headline.*|.*title.*'))

        for item in headline_items[:20]:  # Limit to 20 articles
            try:
                link_elem = item.find('a') or item.find_parent('a')
                if not link_elem:
                    continue

                title = item.get_text().strip()
                url = link_elem.get('href', '')

                if url.startswith('/'):
                    url = urljoin('https://www.marketwatch.com', url)

                if title and url:
                    article = {
                        'title': title,
                        'url': url,
                        'source': 'marketwatch',
                        'published_date': datetime.now().isoformat(),
                        'content': '',
                        'summary': ''
                    }
                    articles.append(article)

            except Exception as e:
                logger.error(f"Error processing MarketWatch article: {e}")
                continue

        return articles

    def get_article_content(self, url):
        """Fetch full article content from URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Try to find main content
            content_selectors = [
                'article',
                '.article-body',
                '.story-body', 
                '.content',
                '[data-module="ArticleBody"]',
                '.caas-body'
            ]

            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text().strip()
                    break

            if not content:
                # Fallback: get all paragraph text
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs])

            return content

        except Exception as e:
            logger.error(f"Error fetching article content from {url}: {e}")
            return ""

    def is_financial_news(self, title, content):
        """Check if article is financial news"""
        financial_keywords = [
            'stock', 'market', 'trading', 'investment', 'finance', 'economy',
            'earnings', 'revenue', 'profit', 'loss', 'dividend', 'IPO',
            'merger', 'acquisition', 'SEC', 'FDA', 'bank', 'interest rate',
            'inflation', 'GDP', 'unemployment', 'fed', 'federal reserve',
            'cryptocurrency', 'bitcoin', 'nasdaq', 'dow jones', 's&p 500'
        ]

        text = f"{title} {content}".lower()
        return any(keyword in text for keyword in financial_keywords)
