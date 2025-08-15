"""
Configuration file for Universal Intelligent Communicator (UnIC)
"""

import os
from pathlib import Path
from typing import Dict, List

# Base project paths
PROJECT_ROOT = Path(__file__).parent
DATA_LAKE_PATH = PROJECT_ROOT / "data_lake"
INGESTION_PATH = PROJECT_ROOT / "ingestion"
LOGS_PATH = PROJECT_ROOT / "logs"
MODELS_PATH = PROJECT_ROOT / "models"

# Create directories if they don't exist
for path in [DATA_LAKE_PATH, LOGS_PATH, MODELS_PATH]:
    path.mkdir(exist_ok=True)

# Data categories
CATEGORIES = {
    "arts": "Arts and creative works",
    "creativity": "Creativity and innovation",
    "defence": "Defense and military",
    "love": "Love and relationships", 
    "philosophy": "Philosophy and wisdom",
    "scientific": "Scientific research and papers",
    "spirituality": "Spirituality and religion"
}

# Data sources configuration
DATA_SOURCES = {
    "arxiv": {
        "base_url": "https://arxiv.org",
        "categories": ["cs.LG", "cs.AI", "physics.app-ph", "math.OC"],
        "years_back": 4
    },
    "quotes": {
        "sources": [
            "https://www.brainyquote.com/topics/life-quotes",
            "https://www.brainyquote.com/topics/success-quotes",
            "https://www.brainyquote.com/topics/love-quotes",
            "https://www.keepinspiring.me/quotes-about-relationships/"
        ]
    },
    "scientific_news": {
        "sources": [
            "https://www.scientificamerican.com/",
            "https://www.newscientist.com/section/news/",
            "https://www.sciencenews.org/"
        ]
    },
    "spirituality": {
        "sources": [
            "https://vedpuran.net/download-all-ved-and-puran-pdf-hindi-free/",
            "http://www.vedpuran.com/"
        ]
    }
}

# Database configuration
DATABASE_CONFIG = {
    "sqlite": {
        "path": DATA_LAKE_PATH / "unic_database.db"
    },
    "postgresql": {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", 5432),
        "database": os.getenv("DB_NAME", "unic_db"),
        "username": os.getenv("DB_USER", "unic_user"),
        "password": os.getenv("DB_PASSWORD", "")
    }
}

# NLP Model configuration
NLP_CONFIG = {
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "max_length": 512,
    "similarity_threshold": 0.7,
    "max_results": 10
}

# NLG (Text-to-Speech) configuration
NLG_CONFIG = {
    "voice_rate": 150,
    "voice_volume": 0.9,
    "voice_id": "default"
}

# Web scraping configuration
SCRAPING_CONFIG = {
    "request_delay": 1.0,  # seconds between requests
    "timeout": 30,
    "max_retries": 3,
    "user_agent": "UnIC-Bot/1.0 (Educational Research Project)"
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_PATH / "unic.log"
}

# AWS configuration (optional)
AWS_CONFIG = {
    "region": os.getenv("AWS_REGION", "us-east-1"),
    "access_key": os.getenv("AWS_ACCESS_KEY_ID", ""),
    "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
    "s3_bucket": os.getenv("S3_BUCKET", "")
}

# API configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": False,
    "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"]
}

# File processing configuration
FILE_CONFIG = {
    "supported_formats": [".pdf", ".txt", ".docx", ".doc", ".xlsx", ".csv"],
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "encoding": "utf-8"
}

# Authentication configuration
AUTH_CONFIG = {
    "session_timeout_hours": 24,
    "require_email_verification": False,
    "password_min_length": 6,
    "max_login_attempts": 5,
    "login_attempt_timeout_minutes": 15,
    "allow_registration": True,
    "require_admin_approval": False
} 