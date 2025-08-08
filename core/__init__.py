"""
Core module for UnIC - Universal Intelligent Communicator
"""

from .database import db_manager
from .nlp_engine import nlp_engine
from .nlg_engine import nlg_engine

__all__ = ['db_manager', 'nlp_engine', 'nlg_engine'] 