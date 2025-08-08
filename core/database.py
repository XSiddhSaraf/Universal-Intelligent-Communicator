"""
Database module for Universal Intelligent Communicator (UnIC)
Handles data storage, retrieval, and management
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config import DATABASE_CONFIG, DATA_LAKE_PATH

# Configure logging
logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()

class KnowledgeEntry(Base):
    """Database model for knowledge entries"""
    __tablename__ = 'knowledge_entries'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    content = Column(Text)
    category = Column(String(100))
    source = Column(String(500))
    source_type = Column(String(100))  # 'arxiv', 'quotes', 'manual', etc.
    author = Column(String(200))
    date_added = Column(DateTime, default=datetime.utcnow)
    date_published = Column(DateTime, nullable=True)
    tags = Column(Text)  # JSON string of tags
    embedding = Column(Text)  # JSON string of vector embedding
    confidence_score = Column(Float, default=1.0)
    is_processed = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<KnowledgeEntry(id={self.id}, title='{self.title}', category='{self.category}')>"

class Conversation(Base):
    """Database model for conversation history"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100))
    user_message = Column(Text)
    bot_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    category = Column(String(100))
    confidence_score = Column(Float)
    sources_used = Column(Text)  # JSON string of source IDs
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id='{self.session_id}')>"

class DatabaseManager:
    """Manages database operations for UnIC"""
    
    def __init__(self, db_type: str = "sqlite"):
        self.db_type = db_type
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connection and create tables"""
        try:
            if self.db_type == "sqlite":
                db_path = DATABASE_CONFIG["sqlite"]["path"]
                self.engine = create_engine(f"sqlite:///{db_path}")
            elif self.db_type == "postgresql":
                pg_config = DATABASE_CONFIG["postgresql"]
                connection_string = (
                    f"postgresql://{pg_config['username']}:{pg_config['password']}"
                    f"@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
                )
                self.engine = create_engine(connection_string)
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            # Create tables
            Base.metadata.create_all(self.engine)
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            logger.info(f"Database setup completed for {self.db_type}")
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def add_knowledge_entry(self, entry_data: Dict[str, Any]) -> int:
        """Add a new knowledge entry to the database"""
        try:
            with self.get_session() as session:
                entry = KnowledgeEntry(**entry_data)
                session.add(entry)
                session.commit()
                session.refresh(entry)
                logger.info(f"Added knowledge entry: {entry.id}")
                return entry.id
        except Exception as e:
            logger.error(f"Failed to add knowledge entry: {e}")
            raise
    
    def get_knowledge_entries(self, 
                            category: Optional[str] = None,
                            source_type: Optional[str] = None,
                            limit: int = 100) -> List[KnowledgeEntry]:
        """Retrieve knowledge entries with optional filtering"""
        try:
            with self.get_session() as session:
                query = session.query(KnowledgeEntry)
                
                if category:
                    query = query.filter(KnowledgeEntry.category == category)
                
                if source_type:
                    query = query.filter(KnowledgeEntry.source_type == source_type)
                
                entries = query.limit(limit).all()
                logger.info(f"Retrieved {len(entries)} knowledge entries")
                return entries
                
        except Exception as e:
            logger.error(f"Failed to retrieve knowledge entries: {e}")
            raise
    
    def search_knowledge(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[KnowledgeEntry]:
        """Search knowledge entries by content"""
        try:
            with self.get_session() as session:
                search_query = session.query(KnowledgeEntry).filter(
                    KnowledgeEntry.content.contains(query)
                )
                
                if category:
                    search_query = search_query.filter(KnowledgeEntry.category == category)
                
                results = search_query.limit(limit).all()
                logger.info(f"Search returned {len(results)} results for query: {query}")
                return results
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def add_conversation(self, conversation_data: Dict[str, Any]) -> int:
        """Add a conversation entry"""
        try:
            with self.get_session() as session:
                conversation = Conversation(**conversation_data)
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
                logger.info(f"Added conversation: {conversation.id}")
                return conversation.id
        except Exception as e:
            logger.error(f"Failed to add conversation: {e}")
            raise
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Conversation]:
        """Get conversation history for a session"""
        try:
            with self.get_session() as session:
                conversations = session.query(Conversation).filter(
                    Conversation.session_id == session_id
                ).order_by(Conversation.timestamp.desc()).limit(limit).all()
                
                logger.info(f"Retrieved {len(conversations)} conversations for session: {session_id}")
                return conversations
                
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            raise
    
    def update_embedding(self, entry_id: int, embedding: List[float]) -> bool:
        """Update embedding for a knowledge entry"""
        try:
            with self.get_session() as session:
                entry = session.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
                if entry:
                    entry.embedding = json.dumps(embedding)
                    entry.is_processed = True
                    session.commit()
                    logger.info(f"Updated embedding for entry: {entry_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to update embedding: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_session() as session:
                total_entries = session.query(KnowledgeEntry).count()
                total_conversations = session.query(Conversation).count()
                
                category_counts = {}
                for category in ['arts', 'creativity', 'defence', 'love', 'philosophy', 'scientific', 'spirituality']:
                    count = session.query(KnowledgeEntry).filter(
                        KnowledgeEntry.category == category
                    ).count()
                    category_counts[category] = count
                
                stats = {
                    'total_knowledge_entries': total_entries,
                    'total_conversations': total_conversations,
                    'category_distribution': category_counts,
                    'last_updated': datetime.utcnow().isoformat()
                }
                
                logger.info("Retrieved database statistics")
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise
    
    def cleanup_old_data(self, days_old: int = 365) -> int:
        """Clean up old conversation data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            with self.get_session() as session:
                deleted_count = session.query(Conversation).filter(
                    Conversation.timestamp < cutoff_date
                ).delete()
                session.commit()
                logger.info(f"Cleaned up {deleted_count} old conversations")
                return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise

# Global database manager instance
db_manager = DatabaseManager() 