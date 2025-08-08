#!/usr/bin/env python3
"""
Script to generate embeddings for all knowledge entries
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import db_manager
from core.nlp_engine import nlp_engine
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_embeddings():
    """Generate embeddings for all unprocessed knowledge entries"""
    try:
        # Get all entries without embeddings
        entries = db_manager.get_knowledge_entries(limit=10000)  # Get all entries
        unprocessed_entries = [e for e in entries if not e.is_processed or not e.embedding]
        
        logger.info(f"Found {len(unprocessed_entries)} entries without embeddings")
        
        if not unprocessed_entries:
            logger.info("All entries already have embeddings!")
            return
        
        # Generate embeddings in batches
        batch_size = 10
        for i in range(0, len(unprocessed_entries), batch_size):
            batch = unprocessed_entries[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(unprocessed_entries) + batch_size - 1)//batch_size}")
            
            for entry in batch:
                try:
                    # Create text for embedding (title + content)
                    text = f"{entry.title} {entry.content}"
                    
                    # Generate embedding
                    embedding = nlp_engine.get_embedding(text)
                    
                    # Update entry
                    db_manager.update_embedding(entry.id, embedding)
                    
                    logger.info(f"Generated embedding for entry {entry.id}: {entry.title[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Failed to generate embedding for entry {entry.id}: {e}")
                    continue
        
        logger.info("Embedding generation completed!")
        
        # Show statistics
        stats = db_manager.get_statistics()
        logger.info(f"Database now has {stats['total_knowledge_entries']} entries")
        
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise

if __name__ == "__main__":
    print("🔧 Generating embeddings for knowledge entries...")
    generate_embeddings()
    print("✅ Embedding generation completed!") 