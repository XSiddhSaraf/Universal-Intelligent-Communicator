"""
NLP Engine for Universal Intelligent Communicator (UnIC)
Handles natural language understanding, text processing, and semantic search
"""

import logging
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
from textblob import TextBlob

from config import NLP_CONFIG
from core.database import db_manager

# Configure logging
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class NLPEngine:
    """Natural Language Processing engine for UnIC"""
    
    def __init__(self):
        self.model = SentenceTransformer(NLP_CONFIG['model_name'])
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.max_length = NLP_CONFIG['max_length']
        self.similarity_threshold = NLP_CONFIG['similarity_threshold']
        self.max_results = NLP_CONFIG['max_results']
        
        logger.info("NLP Engine initialized successfully")
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better NLP processing"""
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove special characters and extra whitespace
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Tokenize and remove stop words
            tokens = word_tokenize(text)
            tokens = [token for token in tokens if token not in self.stop_words]
            
            # Lemmatize tokens
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
            return ' '.join(tokens)
            
        except Exception as e:
            logger.error(f"Text preprocessing failed: {e}")
            return text
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text"""
        try:
            # Truncate text if too long
            if len(text) > self.max_length:
                text = text[:self.max_length]
            
            embedding = self.model.encode(text)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            if not embedding1 or not embedding2:
                return 0.0
            
            # Convert to numpy arrays
            emb1 = np.array(embedding1).reshape(1, -1)
            emb2 = np.array(embedding2).reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(emb1, emb2)[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def semantic_search(self, query: str, category: Optional[str] = None, limit: int = None) -> List[Dict]:
        """Perform semantic search on knowledge base"""
        try:
            # Use the database's semantic search method
            search_limit = limit if limit is not None else self.max_results
            entries = db_manager.search_knowledge(query, category=category, limit=search_limit)
            
            results = []
            for entry in entries:
                results.append({
                    'id': entry.id,
                    'title': entry.title,
                    'content': entry.content,
                    'category': entry.category,
                    'author': entry.author,
                    'source': entry.source,
                    'similarity_score': 0.8,  # Default similarity score
                    'confidence_score': entry.confidence_score
                })
            
            logger.info(f"Semantic search returned {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Tokenize
            tokens = word_tokenize(processed_text)
            
            # Remove short tokens and common words
            keywords = [token for token in tokens if len(token) > 3 and token not in self.stop_words]
            
            # Count frequency
            from collections import Counter
            keyword_freq = Counter(keywords)
            
            # Return top keywords
            return [keyword for keyword, freq in keyword_freq.most_common(max_keywords)]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def categorize_text(self, text: str) -> str:
        """Categorize text based on content"""
        try:
            processed_text = self.preprocess_text(text)
            keywords = self.extract_keywords(processed_text, max_keywords=20)
            
            # Define category keywords
            category_keywords = {
                'arts': ['art', 'creative', 'beauty', 'music', 'painting', 'sculpture', 'design'],
                'creativity': ['innovation', 'create', 'invent', 'new', 'original', 'creative'],
                'defence': ['military', 'defense', 'security', 'war', 'strategy', 'tactics'],
                'love': ['love', 'heart', 'relationship', 'romance', 'affection', 'passion'],
                'philosophy': ['philosophy', 'wisdom', 'truth', 'meaning', 'existence', 'knowledge'],
                'scientific': ['science', 'research', 'experiment', 'theory', 'data', 'analysis'],
                'spirituality': ['spiritual', 'soul', 'divine', 'god', 'faith', 'religion', 'meditation']
            }
            
            # Calculate category scores
            category_scores = {}
            for category, cat_keywords in category_keywords.items():
                score = sum(1 for keyword in keywords if keyword in cat_keywords)
                category_scores[category] = score
            
            # Return category with highest score
            if category_scores:
                return max(category_scores, key=category_scores.get)
            else:
                return 'philosophy'  # Default category
                
        except Exception as e:
            logger.error(f"Text categorization failed: {e}")
            return 'philosophy'
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment
            
            return {
                'polarity': sentiment.polarity,  # -1 to 1 (negative to positive)
                'subjectivity': sentiment.subjectivity  # 0 to 1 (objective to subjective)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.5}
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text"""
        try:
            # Simple entity extraction using regex patterns
            entities = []
            
            # Extract person names (capitalized words)
            person_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
            persons = re.findall(person_pattern, text)
            for person in persons:
                entities.append({
                    'text': person,
                    'type': 'PERSON',
                    'start': text.find(person),
                    'end': text.find(person) + len(person)
                })
            
            # Extract organizations (words ending with common org suffixes)
            org_pattern = r'\b[A-Z][a-zA-Z\s]+(?:Inc|Corp|LLC|Ltd|Company|University|Institute)\b'
            organizations = re.findall(org_pattern, text)
            for org in organizations:
                entities.append({
                    'text': org,
                    'type': 'ORGANIZATION',
                    'start': text.find(org),
                    'end': text.find(org) + len(org)
                })
            
            # Extract dates
            date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}\b'
            dates = re.findall(date_pattern, text)
            for date in dates:
                entities.append({
                    'text': date,
                    'type': 'DATE',
                    'start': text.find(date),
                    'end': text.find(date) + len(date)
                })
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    def generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate a summary of the text"""
        try:
            # Split into sentences
            sentences = sent_tokenize(text)
            
            if len(sentences) <= max_sentences:
                return text
            
            # Calculate sentence importance based on keyword frequency
            keywords = self.extract_keywords(text, max_keywords=10)
            
            sentence_scores = []
            for sentence in sentences:
                processed_sentence = self.preprocess_text(sentence)
                sentence_tokens = word_tokenize(processed_sentence)
                score = sum(1 for token in sentence_tokens if token in keywords)
                sentence_scores.append((sentence, score))
            
            # Sort by score and take top sentences
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            top_sentences = [sentence for sentence, score in sentence_scores[:max_sentences]]
            
            # Sort by original order
            summary_sentences = []
            for sentence in sentences:
                if sentence in top_sentences:
                    summary_sentences.append(sentence)
                    if len(summary_sentences) >= max_sentences:
                        break
            
            return ' '.join(summary_sentences)
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query comprehensively"""
        try:
            # Preprocess query
            processed_query = self.preprocess_text(query)
            
            # Analyze query
            sentiment = self.analyze_sentiment(query)
            category = self.categorize_text(query)
            keywords = self.extract_keywords(query)
            entities = self.extract_entities(query)
            
            # Perform semantic search
            search_results = self.semantic_search(query, category=category)
            
            # Generate response context
            context = {
                'query': query,
                'processed_query': processed_query,
                'category': category,
                'sentiment': sentiment,
                'keywords': keywords,
                'entities': entities,
                'search_results': search_results,
                'confidence_score': max([result['similarity_score'] for result in search_results], default=0.0)
            }
            
            logger.info(f"Query processed successfully: {query}")
            return context
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                'query': query,
                'error': str(e),
                'search_results': [],
                'confidence_score': 0.0
            }

# Global NLP engine instance
nlp_engine = NLPEngine() 