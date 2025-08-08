#!/usr/bin/env python3
"""
Demo script for Universal Intelligent Communicator (UnIC)
Showcases all features and capabilities of the system
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_banner():
    """Print demo banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    UnIC - Universal Intelligent Communicator                ║
    ║                                                              ║
    ║    Interactive Demo                                          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def demo_nlp_features():
    """Demo NLP features"""
    print("\n🧠 NLP Engine Demo")
    print("=" * 50)
    
    try:
        from core.nlp_engine import nlp_engine
        
        test_texts = [
            "Machine learning is transforming the world of artificial intelligence.",
            "Love is the most beautiful emotion that connects all humanity.",
            "Philosophy helps us understand the deeper meaning of existence.",
            "Innovation drives progress and creates new possibilities."
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n{i}. Analyzing: '{text}'")
            
            # Text preprocessing
            processed = nlp_engine.preprocess_text(text)
            print(f"   Preprocessed: {processed}")
            
            # Categorization
            category = nlp_engine.categorize_text(text)
            print(f"   Category: {category}")
            
            # Sentiment analysis
            sentiment = nlp_engine.analyze_sentiment(text)
            print(f"   Sentiment: Polarity={sentiment['polarity']:.2f}, Subjectivity={sentiment['subjectivity']:.2f}")
            
            # Keyword extraction
            keywords = nlp_engine.extract_keywords(text, max_keywords=5)
            print(f"   Keywords: {', '.join(keywords)}")
            
            # Entity extraction
            entities = nlp_engine.extract_entities(text)
            if entities:
                print(f"   Entities: {[e['text'] for e in entities]}")
            
            # Summary generation
            summary = nlp_engine.generate_summary(text, max_sentences=1)
            print(f"   Summary: {summary}")
        
        print("\n✅ NLP features demo completed!")
        
    except Exception as e:
        print(f"❌ NLP demo failed: {e}")

def demo_nlg_features():
    """Demo NLG features"""
    print("\n🗣️  NLG Engine Demo")
    print("=" * 50)
    
    try:
        from core.nlg_engine import nlg_engine
        
        # Test response generation
        test_queries = [
            "Hello, how are you?",
            "What is artificial intelligence?",
            "Tell me about love and relationships",
            "What is the meaning of life?",
            "How can I be more creative?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: '{query}'")
            
            # Generate response
            response_data = nlg_engine.generate_conversation_response(query, f"demo_session_{i}")
            
            print(f"   Response: {response_data['response']}")
            print(f"   Confidence: {response_data['confidence_score']:.3f}")
            print(f"   Category: {response_data['category']}")
        
        # Test text-to-speech (optional)
        print(f"\n🔊 Text-to-Speech Demo")
        test_speech = "Hello! I am UnIC, your Universal Intelligent Communicator."
        print(f"   Speaking: '{test_speech}'")
        
        # Uncomment the next line to enable actual speech
        # success = nlg_engine.speak_text(test_speech)
        # print(f"   Speech result: {'Success' if success else 'Failed'}")
        
        print("\n✅ NLG features demo completed!")
        
    except Exception as e:
        print(f"❌ NLG demo failed: {e}")

def demo_database_features():
    """Demo database features"""
    print("\n🗄️  Database Demo")
    print("=" * 50)
    
    try:
        from core.database import db_manager
        import json
        from datetime import datetime
        
        # Get current statistics
        stats = db_manager.get_statistics()
        print(f"Current database statistics:")
        print(f"   Total knowledge entries: {stats['total_knowledge_entries']}")
        print(f"   Total conversations: {stats['total_conversations']}")
        print(f"   Category distribution:")
        for category, count in stats['category_distribution'].items():
            print(f"     {category}: {count}")
        
        # Add a demo entry
        demo_entry = {
            'title': 'Demo Entry - The Power of Knowledge',
            'content': 'Knowledge is the foundation of wisdom. Through continuous learning and understanding, we can navigate the complexities of life with greater clarity and purpose. This demo entry showcases the database capabilities of UnIC.',
            'category': 'philosophy',
            'source': 'demo',
            'source_type': 'demo',
            'author': 'UnIC Demo',
            'tags': json.dumps(['demo', 'knowledge', 'wisdom', 'philosophy']),
            'confidence_score': 0.95
        }
        
        entry_id = db_manager.add_knowledge_entry(demo_entry)
        print(f"\nAdded demo entry with ID: {entry_id}")
        
        # Search for the entry
        search_results = db_manager.search_knowledge('knowledge')
        print(f"\nSearch results for 'knowledge': {len(search_results)} entries")
        
        if search_results:
            for result in search_results[:3]:  # Show first 3 results
                print(f"   - {result.title} (Category: {result.category})")
        
        # Get entries by category
        philosophy_entries = db_manager.get_knowledge_entries(category='philosophy', limit=5)
        print(f"\nPhilosophy entries: {len(philosophy_entries)} found")
        
        print("\n✅ Database features demo completed!")
        
    except Exception as e:
        print(f"❌ Database demo failed: {e}")

def demo_semantic_search():
    """Demo semantic search"""
    print("\n🔍 Semantic Search Demo")
    print("=" * 50)
    
    try:
        from core.nlp_engine import nlp_engine
        
        test_queries = [
            "machine learning",
            "love and relationships",
            "philosophical wisdom",
            "creative thinking",
            "scientific research"
        ]
        
        for query in test_queries:
            print(f"\nSearching for: '{query}'")
            
            results = nlp_engine.semantic_search(query)
            
            if results:
                print(f"   Found {len(results)} results:")
                for i, result in enumerate(results[:3], 1):  # Show top 3
                    print(f"   {i}. {result['title']}")
                    print(f"      Category: {result['category']}")
                    print(f"      Similarity: {result['similarity_score']:.3f}")
                    print(f"      Content: {result['content'][:100]}...")
            else:
                print("   No results found")
        
        print("\n✅ Semantic search demo completed!")
        
    except Exception as e:
        print(f"❌ Semantic search demo failed: {e}")

def demo_conversation_flow():
    """Demo conversation flow"""
    print("\n💬 Conversation Flow Demo")
    print("=" * 50)
    
    try:
        from core.nlg_engine import nlg_engine
        
        # Simulate a conversation
        conversation = [
            "Hello! I'm interested in learning about artificial intelligence.",
            "That sounds fascinating! Can you tell me more about machine learning?",
            "What are the ethical implications of AI?",
            "How can I start learning about AI?",
            "Thank you for your help!"
        ]
        
        session_id = "demo_conversation_session"
        
        for i, message in enumerate(conversation, 1):
            print(f"\n{i}. User: {message}")
            
            # Generate response
            response_data = nlg_engine.generate_conversation_response(message, session_id)
            
            print(f"   UnIC: {response_data['response']}")
            print(f"   Confidence: {response_data['confidence_score']:.3f}")
            print(f"   Category: {response_data['category']}")
            
            # Small delay for readability
            time.sleep(1)
        
        print("\n✅ Conversation flow demo completed!")
        
    except Exception as e:
        print(f"❌ Conversation flow demo failed: {e}")

def demo_data_ingestion():
    """Demo data ingestion features"""
    print("\n📥 Data Ingestion Demo")
    print("=" * 50)
    
    try:
        from ingestion.data_ingestion import ingestion_manager
        
        # Test quote categorization
        test_quotes = [
            "Love is the most beautiful thing in the world.",
            "Innovation is the key to progress.",
            "Wisdom comes from experience and reflection.",
            "Art is the expression of the human soul.",
            "Science is the pursuit of truth and understanding."
        ]
        
        print("Testing quote categorization:")
        for quote in test_quotes:
            category = ingestion_manager._categorize_quote(quote)
            print(f"   '{quote}' -> Category: {category}")
        
        # Test file processing (create a temporary file)
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a demo file content for testing the file processing capabilities of UnIC.")
            f.flush()
            
            try:
                file_data = ingestion_manager.process_file_upload(
                    Path(f.name), 'philosophy', 'demo'
                )
                print(f"\nFile processing demo:")
                print(f"   Title: {file_data['title']}")
                print(f"   Category: {file_data['category']}")
                print(f"   Content: {file_data['content'][:50]}...")
            finally:
                import os
                os.unlink(f.name)
        
        print("\n✅ Data ingestion demo completed!")
        
    except Exception as e:
        print(f"❌ Data ingestion demo failed: {e}")

def demo_api_endpoints():
    """Demo API endpoints"""
    print("\n🌐 API Endpoints Demo")
    print("=" * 50)
    
    try:
        from api.app import app
        from core.nlg_engine import nlg_engine
        from core.nlp_engine import nlp_engine
        
        # Test chat endpoint
        print("Testing chat endpoint:")
        with app.test_client() as client:
            response = client.post('/api/chat', json={
                'message': 'Hello, UnIC!',
                'session_id': 'demo_api_session'
            })
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Chat response: {data['response'][:100]}...")
                print(f"   Confidence: {data['confidence_score']:.3f}")
            else:
                print(f"   Chat endpoint failed: {response.status_code}")
        
        # Test search endpoint
        print("\nTesting search endpoint:")
        with app.test_client() as client:
            response = client.post('/api/search', json={
                'query': 'knowledge'
            })
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Search results: {data['total_results']} found")
            else:
                print(f"   Search endpoint failed: {response.status_code}")
        
        # Test statistics endpoint
        print("\nTesting statistics endpoint:")
        with app.test_client() as client:
            response = client.get('/api/statistics')
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Total entries: {data['total_knowledge_entries']}")
                print(f"   Total conversations: {data['total_conversations']}")
            else:
                print(f"   Statistics endpoint failed: {response.status_code}")
        
        print("\n✅ API endpoints demo completed!")
        
    except Exception as e:
        print(f"❌ API endpoints demo failed: {e}")

def interactive_demo():
    """Interactive demo mode"""
    print("\n🎮 Interactive Demo Mode")
    print("=" * 50)
    print("You can now interact with UnIC directly!")
    print("Type your questions and see how UnIC responds.")
    print("Type 'quit' to exit the demo.")
    print()
    
    try:
        from core.nlg_engine import nlg_engine
        
        session_id = f"interactive_demo_{int(time.time())}"
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("UnIC: Thank you for trying the demo! Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Generate response
            response_data = nlg_engine.generate_conversation_response(user_input, session_id)
            
            print(f"UnIC: {response_data['response']}")
            print(f"      (Confidence: {response_data['confidence_score']:.3f}, Category: {response_data['category']})")
            print()
    
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Interactive demo failed: {e}")

def main():
    """Main demo function"""
    print_banner()
    
    print("Welcome to the UnIC Demo!")
    print("This demo will showcase all the features of the Universal Intelligent Communicator.")
    print()
    
    # Run all demos
    demos = [
        ("NLP Features", demo_nlp_features),
        ("NLG Features", demo_nlg_features),
        ("Database Features", demo_database_features),
        ("Semantic Search", demo_semantic_search),
        ("Conversation Flow", demo_conversation_flow),
        ("Data Ingestion", demo_data_ingestion),
        ("API Endpoints", demo_api_endpoints)
    ]
    
    for demo_name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"❌ {demo_name} demo failed: {e}")
            continue
    
    print("\n" + "="*60)
    print("🎉 Demo completed!")
    print("="*60)
    
    # Ask if user wants interactive demo
    try:
        response = input("\nWould you like to try the interactive demo? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_demo()
    except KeyboardInterrupt:
        print("\n\nDemo ended. Thank you for trying UnIC!")
    
    print("\n🚀 To start using UnIC:")
    print("   python main.py --mode interactive")
    print("   python main.py --mode api")
    print("   python run.py")

if __name__ == "__main__":
    main() 