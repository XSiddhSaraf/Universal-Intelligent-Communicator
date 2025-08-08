#!/usr/bin/env python3
"""
Comprehensive test suite for Universal Intelligent Communicator (UnIC)
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
import json
import sqlite3

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import CATEGORIES, DATA_SOURCES, DATABASE_CONFIG
from core.database import db_manager, KnowledgeEntry, Conversation
from core.nlp_engine import nlp_engine
from core.nlg_engine import nlg_engine
from ingestion.data_ingestion import ingestion_manager

class TestUnICSystem(unittest.TestCase):
    """Test suite for UnIC system components"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        
        # Override database path for testing
        original_path = DATABASE_CONFIG['sqlite']['path']
        DATABASE_CONFIG['sqlite']['path'] = self.temp_db.name
        
        # Reinitialize database manager with test database
        self.db_manager = db_manager.__class__()
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_config_loading(self):
        """Test configuration loading"""
        self.assertIsInstance(CATEGORIES, dict)
        self.assertIsInstance(DATA_SOURCES, dict)
        self.assertIsInstance(DATABASE_CONFIG, dict)
        
        # Check required categories
        required_categories = ['arts', 'creativity', 'defence', 'love', 'philosophy', 'scientific', 'spirituality']
        for category in required_categories:
            self.assertIn(category, CATEGORIES)
    
    def test_database_operations(self):
        """Test database operations"""
        # Test adding knowledge entry
        test_entry = {
            'title': 'Test Entry',
            'content': 'This is a test entry for testing purposes.',
            'category': 'philosophy',
            'source': 'test',
            'source_type': 'test',
            'author': 'Test Author',
            'tags': json.dumps(['test', 'philosophy']),
            'confidence_score': 0.9
        }
        
        entry_id = self.db_manager.add_knowledge_entry(test_entry)
        self.assertIsInstance(entry_id, int)
        self.assertGreater(entry_id, 0)
        
        # Test retrieving knowledge entries
        entries = self.db_manager.get_knowledge_entries(category='philosophy')
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, 'Test Entry')
        
        # Test search functionality
        search_results = self.db_manager.search_knowledge('test')
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].title, 'Test Entry')
    
    def test_nlp_engine(self):
        """Test NLP engine functionality"""
        # Test text preprocessing
        test_text = "Hello, World! This is a TEST sentence."
        processed = nlp_engine.preprocess_text(test_text)
        self.assertIsInstance(processed, str)
        self.assertIn('hello', processed.lower())
        
        # Test embedding generation
        embedding = nlp_engine.get_embedding(test_text)
        self.assertIsInstance(embedding, list)
        self.assertGreater(len(embedding), 0)
        
        # Test similarity calculation
        embedding1 = nlp_engine.get_embedding("Hello world")
        embedding2 = nlp_engine.get_embedding("Hello world")
        similarity = nlp_engine.calculate_similarity(embedding1, embedding2)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        
        # Test keyword extraction
        keywords = nlp_engine.extract_keywords(test_text)
        self.assertIsInstance(keywords, list)
        
        # Test text categorization
        category = nlp_engine.categorize_text(test_text)
        self.assertIn(category, CATEGORIES.keys())
        
        # Test sentiment analysis
        sentiment = nlp_engine.analyze_sentiment(test_text)
        self.assertIsInstance(sentiment, dict)
        self.assertIn('polarity', sentiment)
        self.assertIn('subjectivity', sentiment)
    
    def test_nlg_engine(self):
        """Test NLG engine functionality"""
        # Test response generation
        query_context = {
            'query': 'Hello',
            'search_results': [],
            'confidence_score': 0.8,
            'category': 'philosophy'
        }
        
        response = nlg_engine.generate_response(query_context)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
        # Test conversation response generation
        response_data = nlg_engine.generate_conversation_response("Hello", "test_session")
        self.assertIsInstance(response_data, dict)
        self.assertIn('response', response_data)
        self.assertIn('confidence_score', response_data)
        self.assertIn('category', response_data)
    
    def test_data_ingestion(self):
        """Test data ingestion functionality"""
        # Test quote categorization
        test_quote = "Love is the most beautiful thing in the world."
        category = ingestion_manager._categorize_quote(test_quote)
        self.assertEqual(category, 'love')
        
        # Test file processing (mock)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test file content.")
            f.flush()
            
            try:
                file_data = ingestion_manager.process_file_upload(
                    Path(f.name), 'philosophy', 'test'
                )
                self.assertIsInstance(file_data, dict)
                self.assertEqual(file_data['category'], 'philosophy')
                self.assertIn('This is a test file content.', file_data['content'])
            finally:
                os.unlink(f.name)
    
    def test_system_integration(self):
        """Test system integration"""
        # Add test data to database
        test_entries = [
            {
                'title': 'Philosophy Test',
                'content': 'This is a philosophical text about wisdom and knowledge.',
                'category': 'philosophy',
                'source': 'test',
                'source_type': 'test',
                'author': 'Test Philosopher',
                'tags': json.dumps(['philosophy', 'wisdom']),
                'confidence_score': 0.9
            },
            {
                'title': 'Science Test',
                'content': 'This is a scientific text about research and discovery.',
                'category': 'scientific',
                'source': 'test',
                'source_type': 'test',
                'author': 'Test Scientist',
                'tags': json.dumps(['science', 'research']),
                'confidence_score': 0.9
            }
        ]
        
        for entry in test_entries:
            self.db_manager.add_knowledge_entry(entry)
        
        # Test semantic search
        search_results = nlp_engine.semantic_search('wisdom')
        self.assertIsInstance(search_results, list)
        
        # Test conversation flow
        response_data = nlg_engine.generate_conversation_response(
            "Tell me about wisdom", "test_session"
        )
        self.assertIsInstance(response_data, dict)
        self.assertIn('response', response_data)
    
    def test_error_handling(self):
        """Test error handling"""
        # Test invalid database operations
        with self.assertRaises(Exception):
            self.db_manager.add_knowledge_entry({})
        
        # Test invalid NLP operations
        embedding = nlp_engine.get_embedding("")
        self.assertEqual(embedding, [])
        
        # Test invalid NLG operations
        response = nlg_engine.generate_response({})
        self.assertIsInstance(response, str)

def run_performance_test():
    """Run performance tests"""
    print("Running performance tests...")
    
    # Test embedding generation speed
    import time
    test_texts = [
        "This is a test sentence for performance testing.",
        "Another test sentence to measure processing speed.",
        "A third sentence to ensure consistent performance."
    ]
    
    start_time = time.time()
    for text in test_texts:
        nlp_engine.get_embedding(text)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / len(test_texts)
    print(f"Average embedding generation time: {avg_time:.4f} seconds")
    
    # Test database operations speed
    start_time = time.time()
    for i in range(10):
        test_entry = {
            'title': f'Performance Test {i}',
            'content': f'This is performance test entry number {i}.',
            'category': 'philosophy',
            'source': 'performance_test',
            'source_type': 'test',
            'author': 'Performance Tester',
            'tags': json.dumps(['performance', 'test']),
            'confidence_score': 0.8
        }
        db_manager.add_knowledge_entry(test_entry)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 10
    print(f"Average database insertion time: {avg_time:.4f} seconds")

if __name__ == '__main__':
    print("🧪 Running UnIC System Tests")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run performance tests
    print("\n" + "=" * 50)
    run_performance_test()
    
    print("\n✅ All tests completed!") 