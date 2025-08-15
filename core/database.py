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
import hashlib
import secrets

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

class User(Base):
    """Database model for user accounts"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class UserSession(Base):
    """Database model for user sessions"""
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # References User.id
    session_token = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"

class Conversation(Base):
    """Database model for conversation history"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100))
    user_id = Column(Integer, nullable=True)  # References User.id, nullable for anonymous chats
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
        """Search knowledge entries by content using semantic similarity"""
        try:
            from core.nlp_engine import nlp_engine
            import json
            import numpy as np
            
            # Get query embedding
            query_embedding = nlp_engine.get_embedding(query)
            
            with self.get_session() as session:
                # Get all entries with embeddings
                entries_query = session.query(KnowledgeEntry).filter(
                    KnowledgeEntry.embedding.isnot(None),
                    KnowledgeEntry.is_processed == True
                )
                
                if category:
                    entries_query = entries_query.filter(KnowledgeEntry.category == category)
                
                entries = entries_query.all()
                
                if not entries:
                    logger.info("No entries with embeddings found")
                    return []
                
                # Calculate similarities
                similarities = []
                for entry in entries:
                    try:
                        entry_embedding = json.loads(entry.embedding)
                        similarity = nlp_engine.calculate_similarity(query_embedding, entry_embedding)
                        similarities.append((entry, similarity))
                    except Exception as e:
                        logger.warning(f"Failed to calculate similarity for entry {entry.id}: {e}")
                        continue
                
                # Sort by similarity and return top results
                similarities.sort(key=lambda x: x[1], reverse=True)
                results = [entry for entry, similarity in similarities[:limit]]
                
                logger.info(f"Semantic search returned {len(results)} results for query: {query}")
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
    
    # Authentication methods
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _generate_salt(self) -> str:
        """Generate a random salt"""
        return secrets.token_hex(16)
    
    def _generate_session_token(self) -> str:
        """Generate a random session token"""
        return secrets.token_urlsafe(32)
    
    def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> int:
        """Create a new user account"""
        try:
            with self.get_session() as session:
                # Check if username or email already exists
                existing_user = session.query(User).filter(
                    (User.username == username) | (User.email == email)
                ).first()
                
                if existing_user:
                    if existing_user.username == username:
                        raise ValueError("Username already exists")
                    else:
                        raise ValueError("Email already exists")
                
                # Generate salt and hash password
                salt = self._generate_salt()
                password_hash = self._hash_password(password, salt)
                
                # Create user
                user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    salt=salt,
                    is_admin=is_admin
                )
                
                session.add(user)
                session.commit()
                session.refresh(user)
                
                logger.info(f"Created user account: {username}")
                return user.id
                
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(
                    User.username == username,
                    User.is_active == True
                ).first()
                
                if not user:
                    return None
                
                # Verify password
                password_hash = self._hash_password(password, user.salt)
                if password_hash == user.password_hash:
                    # Update last login
                    user.last_login = datetime.utcnow()
                    session.commit()
                    logger.info(f"User authenticated: {username}")
                    # Ensure all attributes are loaded before session closes
                    _ = (user.id, user.username, user.email, user.is_admin, 
                         user.created_at, user.last_login, user.is_active)
                    session.expunge(user)
                    return user
                else:
                    logger.warning(f"Authentication failed for user: {username}")
                    return None
                    
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def create_session(self, user_id: int, ip_address: str = None, user_agent: str = None, expires_hours: int = 24) -> str:
        """Create a new user session"""
        try:
            with self.get_session() as session:
                # Generate session token
                session_token = self._generate_session_token()
                expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
                
                # Create session record
                user_session = UserSession(
                    user_id=user_id,
                    session_token=session_token,
                    expires_at=expires_at,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                session.add(user_session)
                session.commit()
                
                logger.info(f"Created session for user_id: {user_id}")
                return session_token
                
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def validate_session(self, session_token: str) -> Optional[User]:
        """Validate session token and return user if valid"""
        try:
            with self.get_session() as session:
                user_session = session.query(UserSession).filter(
                    UserSession.session_token == session_token,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                ).first()
                
                if not user_session:
                    return None
                
                # Get user details
                user = session.query(User).filter(
                    User.id == user_session.user_id,
                    User.is_active == True
                ).first()
                
                if user:
                    logger.info(f"Session validated for user: {user.username}")
                    # Ensure all attributes are loaded before session closes
                    _ = (user.id, user.username, user.email, user.is_admin, 
                         user.created_at, user.last_login, user.is_active)
                    session.expunge(user)
                    return user
                else:
                    # Deactivate session if user not found or inactive
                    user_session.is_active = False
                    session.commit()
                    return None
                    
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a user session (logout)"""
        try:
            with self.get_session() as session:
                user_session = session.query(UserSession).filter(
                    UserSession.session_token == session_token
                ).first()
                
                if user_session:
                    user_session.is_active = False
                    session.commit()
                    logger.info(f"Session invalidated: {session_token[:8]}...")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to invalidate session: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            with self.get_session() as session:
                deleted_count = session.query(UserSession).filter(
                    UserSession.expires_at < datetime.utcnow()
                ).delete()
                session.commit()
                logger.info(f"Cleaned up {deleted_count} expired sessions")
                return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                return user
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None

# Global database manager instance
db_manager = DatabaseManager() 