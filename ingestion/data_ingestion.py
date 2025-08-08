"""
Data Ingestion Module for Universal Intelligent Communicator (UnIC)
Handles data collection from various sources
"""

import requests
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse
import os

from config import DATA_SOURCES, SCRAPING_CONFIG, CATEGORIES
from core.database import db_manager

# Configure logging
logger = logging.getLogger(__name__)

class DataIngestionManager:
    """Manages data ingestion from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': SCRAPING_CONFIG['user_agent']
        })
        self.session.timeout = SCRAPING_CONFIG['timeout']
    
    def scrape_arxiv_papers(self, categories: List[str] = None, max_papers: int = 100) -> List[Dict]:
        """Scrape research papers from ArXiv"""
        if categories is None:
            categories = DATA_SOURCES['arxiv']['categories']
        
        papers = []
        base_url = DATA_SOURCES['arxiv']['base_url']
        
        for category in categories:
            try:
                logger.info(f"Scraping ArXiv category: {category}")
                url = f"{base_url}/list/{category}/recent"
                
                response = self.session.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                content_div = soup.find('div', id='content')
                
                if not content_div:
                    continue
                
                dl_element = content_div.find('dl')
                if not dl_element:
                    continue
                
                # Extract paper information
                dt_elements = dl_element.find_all('dt')
                dd_elements = dl_element.find_all('dd')
                
                for i, (dt, dd) in enumerate(zip(dt_elements, dd_elements)):
                    if len(papers) >= max_papers:
                        break
                    
                    try:
                        # Extract title
                        title_element = dd.find('div', class_='list-title')
                        title = title_element.get_text().strip() if title_element else "Untitled"
                        
                        # Extract authors
                        authors_element = dd.find('div', class_='list-authors')
                        authors = authors_element.get_text().strip() if authors_element else "Unknown"
                        
                        # Extract abstract
                        abstract_element = dd.find('p', class_='mathjax')
                        abstract = abstract_element.get_text().strip() if abstract_element else ""
                        
                        # Extract PDF link
                        pdf_link = dt.find('a', title="Download PDF")
                        pdf_url = urljoin(base_url, pdf_link['href']) if pdf_link else None
                        
                        paper_data = {
                            'title': title,
                            'content': abstract,
                            'category': 'scientific',
                            'source': pdf_url or url,
                            'source_type': 'arxiv',
                            'author': authors,
                            'tags': json.dumps([category, 'research', 'academic']),
                            'date_published': datetime.utcnow()
                        }
                        
                        papers.append(paper_data)
                        logger.info(f"Extracted paper: {title[:50]}...")
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract paper {i}: {e}")
                        continue
                
                # Respect rate limiting
                time.sleep(SCRAPING_CONFIG['request_delay'])
                
            except Exception as e:
                logger.error(f"Failed to scrape ArXiv category {category}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(papers)} papers from ArXiv")
        return papers
    
    def scrape_quotes(self, max_quotes: int = 200) -> List[Dict]:
        """Scrape quotes from various sources"""
        quotes = []
        sources = DATA_SOURCES['quotes']['sources']
        
        for source_url in sources:
            try:
                logger.info(f"Scraping quotes from: {source_url}")
                
                response = self.session.get(source_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Different quote extraction strategies based on source
                if 'brainyquote.com' in source_url:
                    quote_elements = soup.find_all('a', class_='b-qt')
                    author_elements = soup.find_all('a', class_='bq-aut')
                    
                    for i, (quote_elem, author_elem) in enumerate(zip(quote_elements, author_elements)):
                        if len(quotes) >= max_quotes:
                            break
                        
                        quote_text = quote_elem.get_text().strip()
                        author = author_elem.get_text().strip()
                        
                        if quote_text and len(quote_text) > 10:
                            quote_data = {
                                'title': f"Quote by {author}",
                                'content': quote_text,
                                'category': self._categorize_quote(quote_text),
                                'source': source_url,
                                'source_type': 'quotes',
                                'author': author,
                                'tags': json.dumps(['quote', 'inspiration', 'wisdom']),
                                'date_published': datetime.utcnow()
                            }
                            quotes.append(quote_data)
                
                elif 'keepinspiring.me' in source_url:
                    quote_elements = soup.find_all('blockquote')
                    
                    for quote_elem in quote_elements:
                        if len(quotes) >= max_quotes:
                            break
                        
                        quote_text = quote_elem.get_text().strip()
                        if quote_text and len(quote_text) > 10:
                            quote_data = {
                                'title': "Inspirational Quote",
                                'content': quote_text,
                                'category': self._categorize_quote(quote_text),
                                'source': source_url,
                                'source_type': 'quotes',
                                'author': "Unknown",
                                'tags': json.dumps(['quote', 'inspiration', 'motivation']),
                                'date_published': datetime.utcnow()
                            }
                            quotes.append(quote_data)
                
                time.sleep(SCRAPING_CONFIG['request_delay'])
                
            except Exception as e:
                logger.error(f"Failed to scrape quotes from {source_url}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(quotes)} quotes")
        return quotes
    
    def scrape_scientific_news(self, max_articles: int = 100) -> List[Dict]:
        """Scrape scientific news articles"""
        articles = []
        sources = DATA_SOURCES['scientific_news']['sources']
        
        for source_url in sources:
            try:
                logger.info(f"Scraping scientific news from: {source_url}")
                
                response = self.session.get(source_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract article links
                article_links = []
                if 'scientificamerican.com' in source_url:
                    article_links = soup.find_all('a', href=re.compile(r'/article/'))
                elif 'newscientist.com' in source_url:
                    article_links = soup.find_all('a', href=re.compile(r'/article/'))
                elif 'sciencenews.org' in source_url:
                    article_links = soup.find_all('a', href=re.compile(r'/article/'))
                
                for link in article_links[:max_articles//len(sources)]:
                    try:
                        article_url = urljoin(source_url, link['href'])
                        
                        # Get article content
                        article_response = self.session.get(article_url)
                        article_response.raise_for_status()
                        
                        article_soup = BeautifulSoup(article_response.content, 'html.parser')
                        
                        # Extract title and content (simplified)
                        title = link.get_text().strip()
                        content = article_soup.get_text()[:1000]  # First 1000 characters
                        
                        if title and content:
                            article_data = {
                                'title': title,
                                'content': content,
                                'category': 'scientific',
                                'source': article_url,
                                'source_type': 'scientific_news',
                                'author': "Science News",
                                'tags': json.dumps(['science', 'news', 'research']),
                                'date_published': datetime.utcnow()
                            }
                            articles.append(article_data)
                        
                        time.sleep(SCRAPING_CONFIG['request_delay'])
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract article: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Failed to scrape scientific news from {source_url}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(articles)} scientific articles")
        return articles
    
    def _categorize_quote(self, quote_text: str) -> str:
        """Categorize a quote based on its content"""
        quote_lower = quote_text.lower()
        
        if any(word in quote_lower for word in ['love', 'heart', 'relationship', 'romance']):
            return 'love'
        elif any(word in quote_lower for word in ['art', 'creative', 'beauty', 'music', 'painting']):
            return 'arts'
        elif any(word in quote_lower for word in ['philosophy', 'wisdom', 'truth', 'meaning']):
            return 'philosophy'
        elif any(word in quote_lower for word in ['spiritual', 'soul', 'divine', 'god', 'faith']):
            return 'spirituality'
        elif any(word in quote_lower for word in ['innovation', 'create', 'invent', 'new']):
            return 'creativity'
        else:
            return 'philosophy'  # Default category
    
    def process_file_upload(self, file_path: Path, category: str, source_type: str = "manual") -> Dict:
        """Process uploaded files (PDF, TXT, DOCX, etc.)"""
        try:
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.pdf':
                content = self._extract_pdf_text(file_path)
            elif file_extension == '.txt':
                content = self._extract_txt_text(file_path)
            elif file_extension == '.docx':
                content = self._extract_docx_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            file_data = {
                'title': file_path.stem,
                'content': content,
                'category': category,
                'source': str(file_path),
                'source_type': source_type,
                'author': "Uploaded by user",
                'tags': json.dumps([category, 'uploaded', file_extension[1:]]),
                'date_published': datetime.utcnow()
            }
            
            logger.info(f"Processed uploaded file: {file_path.name}")
            return file_data
            
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            raise
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            from pdfminer.high_level import extract_text
            return extract_text(str(file_path))
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {e}")
            return ""
    
    def _extract_txt_text(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to extract TXT text: {e}")
            return ""
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            from docx import Document
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Failed to extract DOCX text: {e}")
            return ""
    
    def run_full_ingestion(self) -> Dict[str, int]:
        """Run complete data ingestion from all sources"""
        results = {
            'arxiv_papers': 0,
            'quotes': 0,
            'scientific_news': 0,
            'total_added': 0
        }
        
        try:
            logger.info("Starting full data ingestion process...")
            
            # Scrape ArXiv papers
            papers = self.scrape_arxiv_papers()
            for paper in papers:
                db_manager.add_knowledge_entry(paper)
                results['arxiv_papers'] += 1
                results['total_added'] += 1
            
            # Scrape quotes
            quotes = self.scrape_quotes()
            for quote in quotes:
                db_manager.add_knowledge_entry(quote)
                results['quotes'] += 1
                results['total_added'] += 1
            
            # Scrape scientific news
            articles = self.scrape_scientific_news()
            for article in articles:
                db_manager.add_knowledge_entry(article)
                results['scientific_news'] += 1
                results['total_added'] += 1
            
            logger.info(f"Data ingestion completed. Results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")
            raise

# Global ingestion manager instance
ingestion_manager = DataIngestionManager() 