#!/usr/bin/env python3
"""
Main entry point for Universal Intelligent Communicator (UnIC)
Command-line interface and system orchestration
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import LOGGING_CONFIG, CATEGORIES
from core.database import db_manager
from core.nlp_engine import nlp_engine
from core.nlg_engine import nlg_engine
from ingestion.data_ingestion import ingestion_manager
from api.app import app

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UnICSystem:
    """Main system class for UnIC"""
    
    def __init__(self):
        self.session_id = None
        logger.info("UnIC System initialized")
    
    def start_interactive_mode(self):
        """Start interactive command-line mode"""
        print("\n" + "="*60)
        print("Welcome to UnIC - Universal Intelligent Communicator")
        print("="*60)
        print("Type 'help' for available commands")
        print("Type 'quit' or 'exit' to leave")
        print("="*60 + "\n")
        
        self.session_id = f"cli_session_{int(time.time())}"
        
        while True:
            try:
                user_input = input("UnIC> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Thank you for using UnIC. Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower().startswith('ingest'):
                    self._handle_ingest_command(user_input)
                    continue
                
                if user_input.lower().startswith('search'):
                    self._handle_search_command(user_input)
                    continue
                
                if user_input.lower().startswith('stats'):
                    self._show_statistics()
                    continue
                
                if user_input.lower().startswith('speak'):
                    self._handle_speak_command(user_input)
                    continue
                
                # Default: treat as a chat message
                self._handle_chat_message(user_input)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"An error occurred: {e}")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
------------------
help                    - Show this help message
quit/exit/bye          - Exit the system
ingest [source]        - Ingest data from sources (arxiv, quotes, all)
search <query>         - Search knowledge base
stats                  - Show system statistics
speak <text>           - Convert text to speech
<message>              - Chat with UnIC

Examples:
---------
ingest arxiv           - Ingest research papers from ArXiv
ingest quotes          - Ingest quotes from various sources
ingest all             - Ingest from all sources
search "machine learning" - Search for machine learning topics
speak "Hello world"    - Speak the text
"""
        print(help_text)
    
    def _handle_ingest_command(self, command: str):
        """Handle ingest commands"""
        parts = command.split()
        if len(parts) < 2:
            print("Usage: ingest [arxiv|quotes|all]")
            return
        
        source_type = parts[1].lower()
        
        print(f"Starting data ingestion from {source_type}...")
        
        try:
            if source_type == 'all':
                results = ingestion_manager.run_full_ingestion()
            elif source_type == 'arxiv':
                papers = ingestion_manager.scrape_arxiv_papers()
                results = {'arxiv_papers': len(papers), 'total_added': len(papers)}
                for paper in papers:
                    db_manager.add_knowledge_entry(paper)
            elif source_type == 'quotes':
                quotes = ingestion_manager.scrape_quotes()
                results = {'quotes': len(quotes), 'total_added': len(quotes)}
                for quote in quotes:
                    db_manager.add_knowledge_entry(quote)
            else:
                print(f"Unknown source type: {source_type}")
                return
            
            print(f"Ingestion completed! Results: {results}")
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            print(f"Ingestion failed: {e}")
    
    def _handle_search_command(self, command: str):
        """Handle search commands"""
        parts = command.split(' ', 1)
        if len(parts) < 2:
            print("Usage: search <query>")
            return
        
        query = parts[1]
        print(f"Searching for: {query}")
        
        try:
            results = nlp_engine.semantic_search(query)
            
            if not results:
                print("No results found.")
                return
            
            print(f"\nFound {len(results)} results:\n")
            for i, result in enumerate(results[:5], 1):
                print(f"{i}. {result['title']}")
                print(f"   Category: {result['category']}")
                print(f"   Author: {result['author']}")
                print(f"   Similarity: {result['similarity_score']:.3f}")
                print(f"   Content: {result['content'][:200]}...")
                print()
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            print(f"Search failed: {e}")
    
    def _handle_chat_message(self, message: str):
        """Handle chat messages"""
        try:
            response_data = nlg_engine.generate_conversation_response(message, self.session_id)
            
            print(f"\nUnIC: {response_data['response']}")
            print(f"Confidence: {response_data['confidence_score']:.3f}")
            print(f"Category: {response_data['category']}")
            print()
            
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            print(f"Sorry, I encountered an error: {e}")
    
    def _handle_speak_command(self, command: str):
        """Handle speak commands"""
        parts = command.split(' ', 1)
        if len(parts) < 2:
            print("Usage: speak <text>")
            return
        
        text = parts[1]
        print(f"Speaking: {text}")
        
        try:
            success = nlg_engine.speak_text(text)
            if success:
                print("Text spoken successfully!")
            else:
                print("Failed to speak text.")
        except Exception as e:
            logger.error(f"Speech failed: {e}")
            print(f"Speech failed: {e}")
    
    def _show_statistics(self):
        """Show system statistics"""
        try:
            stats = db_manager.get_statistics()
            
            print("\nUnIC System Statistics:")
            print("="*40)
            print(f"Total Knowledge Entries: {stats['total_knowledge_entries']}")
            print(f"Total Conversations: {stats['total_conversations']}")
            print("\nCategory Distribution:")
            for category, count in stats['category_distribution'].items():
                print(f"  {category.capitalize()}: {count}")
            print(f"\nLast Updated: {stats['last_updated']}")
            print()
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            print(f"Failed to get statistics: {e}")
    
    def run_data_ingestion(self, source_type: str = 'all'):
        """Run data ingestion"""
        logger.info(f"Starting data ingestion for source: {source_type}")
        
        try:
            if source_type == 'all':
                results = ingestion_manager.run_full_ingestion()
            elif source_type == 'arxiv':
                papers = ingestion_manager.scrape_arxiv_papers()
                results = {'arxiv_papers': len(papers), 'total_added': len(papers)}
                for paper in papers:
                    db_manager.add_knowledge_entry(paper)
            elif source_type == 'quotes':
                quotes = ingestion_manager.scrape_quotes()
                results = {'quotes': len(quotes), 'total_added': len(quotes)}
                for quote in quotes:
                    db_manager.add_knowledge_entry(quote)
            else:
                raise ValueError(f"Unknown source type: {source_type}")
            
            logger.info(f"Data ingestion completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")
            raise
    
    def start_api_server(self, host: str = None, port: int = None, debug: bool = False):
        """Start the API server"""
        from config import API_CONFIG
        
        # Use config values if not provided
        host = host or API_CONFIG['host']
        port = port or API_CONFIG['port']
        
        logger.info(f"Starting API server on {host}:{port}")
        app.run(host=host, port=port, debug=debug)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Universal Intelligent Communicator (UnIC)')
    parser.add_argument('--mode', choices=['interactive', 'api', 'ingest'], 
                       default='interactive', help='Operation mode')
    parser.add_argument('--source', choices=['arxiv', 'quotes', 'all'], 
                       default='all', help='Data source for ingestion')
    parser.add_argument('--host', default='0.0.0.0', help='API server host')
    parser.add_argument('--port', type=int, help='API server port (default from config)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Initialize UnIC system
    unic = UnICSystem()
    
    try:
        if args.mode == 'interactive':
            unic.start_interactive_mode()
        elif args.mode == 'api':
            unic.start_api_server(host=args.host, port=args.port, debug=args.debug)
        elif args.mode == 'ingest':
            results = unic.run_data_ingestion(args.source)
            print(f"Ingestion completed: {results}")
    
    except KeyboardInterrupt:
        print("\nShutting down UnIC...")
    except Exception as e:
        logger.error(f"UnIC system error: {e}")
        print(f"System error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 