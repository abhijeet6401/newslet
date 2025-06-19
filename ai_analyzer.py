import logging
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
from datetime import datetime
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = None
        self.summarizer = None
        self.classifier = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Initialize models
        self.load_models()

        # Financial keywords for importance scoring
        self.high_importance_keywords = [
            'fed', 'federal reserve', 'interest rate', 'inflation', 'recession',
            'earnings', 'ipo', 'merger', 'acquisition', 'bankruptcy', 'sec',
            'market crash', 'bull market', 'bear market', 'dividend',
            'stock split', 'buyback', 'guidance', 'outlook'
        ]

        self.medium_importance_keywords = [
            'revenue', 'profit', 'loss', 'sales', 'growth', 'decline',
            'investment', 'funding', 'valuation', 'analyst', 'upgrade',
            'downgrade', 'target price', 'recommendation'
        ]

    def load_models(self):
        """Load free Hugging Face models"""
        try:
            logger.info("Loading AI models... This may take a few minutes on first run.")

            # Load sentiment analysis model (financial domain)
            logger.info("Loading sentiment analyzer...")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                tokenizer="ProsusAI/finbert",
                device=0 if self.device == "cuda" else -1
            )

            # Load summarization model
            logger.info("Loading summarizer...")
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if self.device == "cuda" else -1
            )

            # Load text classification for news categorization
            logger.info("Loading classifier...")
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if self.device == "cuda" else -1
            )

            logger.info("✅ All AI models loaded successfully!")

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            logger.info("Falling back to basic analysis without AI models")
            self.sentiment_analyzer = None
            self.summarizer = None
            self.classifier = None

    def analyze_articles(self, articles):
        """Analyze a list of articles"""
        analyzed_articles = []

        for i, article in enumerate(articles):
            try:
                logger.info(f"Analyzing article {i+1}/{len(articles)}: {article['title'][:50]}...")

                analyzed_article = self.analyze_single_article(article)
                analyzed_articles.append(analyzed_article)

            except Exception as e:
                logger.error(f"Error analyzing article: {e}")
                # Add article with default scores if analysis fails
                article['sentiment_score'] = 0.0
                article['importance_score'] = 0.5
                article['category'] = 'General'
                article['summary'] = article.get('content', '')[:200] + '...'
                analyzed_articles.append(article)

        return analyzed_articles

    def analyze_single_article(self, article):
        """Analyze a single article"""
        title = article.get('title', '')
        content = article.get('content', '')

        # Get full text for analysis
        full_text = f"{title}. {content}".strip()

        # Sentiment analysis
        sentiment_score = self.analyze_sentiment(full_text)

        # Importance scoring
        importance_score = self.calculate_importance_score(title, content)

        # Categorization
        category = self.categorize_article(title, content)

        # Summarization
        summary = self.generate_summary(full_text)

        # Update article with analysis results
        article['sentiment_score'] = sentiment_score
        article['importance_score'] = importance_score
        article['category'] = category
        article['summary'] = summary

        return article

    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        try:
            if self.sentiment_analyzer and text:
                # Truncate text to fit model limits
                text = text[:512]

                result = self.sentiment_analyzer(text)

                # Convert to numeric score (-1 to 1)
                label = result[0]['label'].lower()
                confidence = result[0]['score']

                if 'positive' in label:
                    return confidence
                elif 'negative' in label:
                    return -confidence
                else:  # neutral
                    return 0.0
            else:
                # Fallback sentiment analysis using keywords
                return self.keyword_sentiment_analysis(text)

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return 0.0

    def keyword_sentiment_analysis(self, text):
        """Fallback sentiment analysis using keywords"""
        positive_words = [
            'gain', 'gains', 'up', 'rise', 'surge', 'jump', 'soar', 'climb',
            'rally', 'boost', 'strong', 'bullish', 'optimistic', 'positive',
            'growth', 'profit', 'beat', 'exceed', 'outperform'
        ]

        negative_words = [
            'fall', 'falls', 'drop', 'decline', 'plunge', 'crash', 'sink',
            'tumble', 'slide', 'weak', 'bearish', 'pessimistic', 'negative',
            'loss', 'miss', 'underperform', 'concern', 'worry', 'fear'
        ]

        text_lower = text.lower()

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count + negative_count == 0:
            return 0.0

        return (positive_count - negative_count) / (positive_count + negative_count)

    def calculate_importance_score(self, title, content):
        """Calculate importance score (0-1)"""
        score = 0.5  # Base score

        text = f"{title} {content}".lower()

        # Check for high importance keywords
        high_matches = sum(1 for keyword in self.high_importance_keywords if keyword in text)
        score += min(high_matches * 0.2, 0.4)  # Max 0.4 boost

        # Check for medium importance keywords
        medium_matches = sum(1 for keyword in self.medium_importance_keywords if keyword in text)
        score += min(medium_matches * 0.1, 0.2)  # Max 0.2 boost

        # Boost score for breaking news indicators
        breaking_indicators = ['breaking', 'urgent', 'alert', 'just in', 'developing']
        if any(indicator in text for indicator in breaking_indicators):
            score += 0.15

        # Check for market impact indicators
        market_indicators = ['dow', 'nasdaq', 's&p', 'market', 'trading', 'volume']
        market_matches = sum(1 for indicator in market_indicators if indicator in text)
        score += min(market_matches * 0.05, 0.15)

        # Check for company mentions (simplified)
        if re.search(r'\b[A-Z]{2,5}\b', title):  # Likely stock symbols
            score += 0.1

        return min(score, 1.0)  # Cap at 1.0

    def categorize_article(self, title, content):
        """Categorize article into financial categories"""
        try:
            if self.classifier:
                text = f"{title}. {content}"[:512]

                categories = [
                    "Market News",
                    "Company Earnings", 
                    "Economic Indicators",
                    "Central Bank Policy",
                    "Cryptocurrency",
                    "Commodities",
                    "Mergers & Acquisitions",
                    "IPO News",
                    "Regulatory News"
                ]

                result = self.classifier(text, categories)
                return result['labels'][0]  # Return top category
            else:
                # Fallback categorization using keywords
                return self.keyword_categorization(title, content)

        except Exception as e:
            logger.error(f"Error in categorization: {e}")
            return "General"

    def keyword_categorization(self, title, content):
        """Fallback categorization using keywords"""
        text = f"{title} {content}".lower()

        category_keywords = {
            "Market News": ["market", "trading", "dow", "nasdaq", "s&p", "index"],
            "Company Earnings": ["earnings", "revenue", "profit", "quarterly", "results"],
            "Economic Indicators": ["gdp", "inflation", "unemployment", "cpi", "ppi"],
            "Central Bank Policy": ["fed", "federal reserve", "interest rate", "monetary policy"],
            "Cryptocurrency": ["bitcoin", "crypto", "blockchain", "ethereum", "digital currency"],
            "Commodities": ["oil", "gold", "silver", "commodity", "crude", "natural gas"],
            "Mergers & Acquisitions": ["merger", "acquisition", "takeover", "buyout"],
            "IPO News": ["ipo", "initial public offering", "going public", "debut"],
            "Regulatory News": ["sec", "regulation", "compliance", "investigation"]
        }

        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category

        return "General"

    def generate_summary(self, text):
        """Generate article summary"""
        try:
            if self.summarizer and text and len(text.split()) > 50:
                # Ensure text is not too long for the model
                max_length = 1000
                if len(text) > max_length:
                    text = text[:max_length]

                # Generate summary
                summary_result = self.summarizer(
                    text,
                    max_length=150,
                    min_length=50,
                    do_sample=False
                )

                return summary_result[0]['summary_text']
            else:
                # Fallback: return first 150 words
                words = text.split()
                if len(words) > 150:
                    return ' '.join(words[:150]) + '...'
                return text

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fallback summary
            words = text.split()
            if len(words) > 100:
                return ' '.join(words[:100]) + '...'
            return text

    def get_model_info(self):
        """Get information about loaded models"""
        return {
            "sentiment_analyzer": "ProsusAI/finbert" if self.sentiment_analyzer else "Keyword-based fallback",
            "summarizer": "facebook/bart-large-cnn" if self.summarizer else "Text truncation fallback",
            "classifier": "facebook/bart-large-mnli" if self.classifier else "Keyword-based fallback",
            "device": self.device
        }
