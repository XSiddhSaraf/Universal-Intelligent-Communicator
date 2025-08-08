"""
NLG Engine for Universal Intelligent Communicator (UnIC)
Handles Natural Language Generation and Text-to-Speech
"""

import logging
import pyttsx3
import speech_recognition as sr
from typing import Dict, List, Optional, Any
import json
import random
from datetime import datetime

from config import NLG_CONFIG
from core.nlp_engine import nlp_engine
from core.database import db_manager

# Configure logging
logger = logging.getLogger(__name__)

class NLGEngine:
    """Natural Language Generation engine for UnIC"""
    
    def __init__(self):
        self.voice_rate = NLG_CONFIG['voice_rate']
        self.voice_volume = NLG_CONFIG['voice_volume']
        self.voice_id = NLG_CONFIG['voice_id']
        
        # Initialize text-to-speech engine
        self.tts_engine = None
        self._setup_tts()
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
        except AttributeError:
            # PyAudio not available, speech recognition will be disabled
            self.microphone = None
            logger.warning("PyAudio not available. Speech recognition will be disabled.")
        
        # Response templates
        self.response_templates = self._load_response_templates()
        
        logger.info("NLG Engine initialized successfully")
    
    def _setup_tts(self):
        """Setup text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)
            
            # Set voice if specified
            if self.voice_id != "default":
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if self.voice_id in voice.id:
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            logger.info("Text-to-speech engine setup completed")
            
        except Exception as e:
            logger.error(f"Text-to-speech setup failed: {e}")
            self.tts_engine = None
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different scenarios"""
        return {
            'greeting': [
                "Hello! I'm UnIC, your Universal Intelligent Communicator. How can I help you today?",
                "Greetings! I'm here to assist you with knowledge and wisdom. What would you like to explore?",
                "Welcome! I'm UnIC, ready to share insights and answer your questions. What's on your mind?"
            ],
            'farewell': [
                "Thank you for our conversation. I hope I've been helpful!",
                "It's been a pleasure talking with you. Feel free to return anytime!",
                "Goodbye! Remember, knowledge is always here when you need it."
            ],
            'no_results': [
                "I don't have specific information about that, but I'd be happy to explore related topics with you.",
                "That's an interesting question. While I don't have exact information, I can share some general wisdom on related subjects.",
                "I'm not sure about that specific topic, but I can help you find information on similar subjects."
            ],
            'high_confidence': [
                "Based on my knowledge, here's what I can tell you:",
                "I found some relevant information that might help:",
                "Here's what I know about that topic:"
            ],
            'low_confidence': [
                "I'm not entirely certain, but here's what I think might be relevant:",
                "This is a bit outside my expertise, but I can share some related thoughts:",
                "I'm not completely sure about this, but here's some information that might be helpful:"
            ],
            'thinking': [
                "Let me think about that for a moment...",
                "That's an interesting question. Let me search my knowledge base...",
                "I'm processing your question and looking for the best information..."
            ],
            'clarification': [
                "Could you please clarify what you mean?",
                "I want to make sure I understand correctly. Can you rephrase that?",
                "That's a bit unclear to me. Could you provide more details?"
            ]
        }
    
    def generate_response(self, query_context: Dict[str, Any]) -> str:
        """Generate a natural language response based on query context"""
        try:
            query = query_context.get('query', '')
            search_results = query_context.get('search_results', [])
            confidence_score = query_context.get('confidence_score', 0.0)
            category = query_context.get('category', 'philosophy')
            
            # Check if query is a greeting
            if self._is_greeting(query):
                return random.choice(self.response_templates['greeting'])
            
            # Check if query is a farewell
            if self._is_farewell(query):
                return random.choice(self.response_templates['farewell'])
            
            # Generate response based on search results
            if not search_results:
                return self._generate_no_results_response(query, category)
            
            # Generate response with search results
            response = self._generate_informed_response(query_context)
            
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    def _is_greeting(self, query: str) -> bool:
        """Check if query is a greeting"""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
        query_lower = query.lower()
        return any(greeting in query_lower for greeting in greetings)
    
    def _is_farewell(self, query: str) -> bool:
        """Check if query is a farewell"""
        farewells = ['goodbye', 'bye', 'see you', 'farewell', 'thank you', 'thanks']
        query_lower = query.lower()
        return any(farewell in query_lower for farewell in farewells)
    
    def _generate_no_results_response(self, query: str, category: str) -> str:
        """Generate response when no search results are found"""
        base_response = random.choice(self.response_templates['no_results'])
        
        # Add category-specific suggestions
        category_suggestions = {
            'arts': "Perhaps you'd like to explore topics about creativity, beauty, or artistic expression?",
            'creativity': "I can help you with topics about innovation, invention, or creative thinking.",
            'defence': "I have information about military strategy, security, and defense topics.",
            'love': "I can share wisdom about relationships, love, and matters of the heart.",
            'philosophy': "I have access to philosophical wisdom and existential questions.",
            'scientific': "I can help with scientific research, theories, and discoveries.",
            'spirituality': "I have knowledge about spiritual matters, faith, and inner peace."
        }
        
        suggestion = category_suggestions.get(category, "I can help you explore various topics in my knowledge base.")
        
        return f"{base_response} {suggestion}"
    
    def _generate_informed_response(self, query_context: Dict[str, Any]) -> str:
        """Generate response using search results"""
        search_results = query_context.get('search_results', [])
        confidence_score = query_context.get('confidence_score', 0.0)
        
        if not search_results:
            return random.choice(self.response_templates['no_results'])
        
        # Choose confidence level template
        if confidence_score > 0.8:
            intro = random.choice(self.response_templates['high_confidence'])
        else:
            intro = random.choice(self.response_templates['low_confidence'])
        
        # Get top result
        top_result = search_results[0]
        content = top_result.get('content', '')
        title = top_result.get('title', '')
        author = top_result.get('author', '')
        
        # Generate summary if content is too long
        if len(content) > 300:
            summary = nlp_engine.generate_summary(content, max_sentences=2)
        else:
            summary = content
        
        # Format response
        response_parts = [intro]
        
        if title and title != "Untitled":
            response_parts.append(f"From '{title}'")
        
        if author and author != "Unknown":
            response_parts.append(f"by {author}")
        
        response_parts.append(f": {summary}")
        
        # Add additional context if available
        if len(search_results) > 1:
            response_parts.append("\n\nI also found some related information that might interest you.")
        
        return " ".join(response_parts)
    
    def speak_text(self, text: str) -> bool:
        """Convert text to speech"""
        try:
            if self.tts_engine is None:
                logger.warning("Text-to-speech engine not available")
                return False
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            logger.info("Text-to-speech completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            return False
    
    def listen_for_speech(self, timeout: int = 5) -> Optional[str]:
        """Listen for speech input and convert to text"""
        if self.microphone is None:
            logger.warning("Speech recognition not available (PyAudio not installed)")
            return None
            
        try:
            with self.microphone as source:
                logger.info("Listening for speech...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=timeout)
            
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Speech recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.info("No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            logger.info("Speech was unintelligible")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Speech recognition failed: {e}")
            return None
    
    def generate_conversation_response(self, user_message: str, session_id: str) -> Dict[str, Any]:
        """Generate a complete conversation response"""
        try:
            # Process the user query
            query_context = nlp_engine.process_query(user_message)
            
            # Generate response
            response_text = self.generate_response(query_context)
            
            # Prepare response data
            response_data = {
                'response': response_text,
                'confidence_score': query_context.get('confidence_score', 0.0),
                'category': query_context.get('category', 'philosophy'),
                'sources_used': [result.get('id') for result in query_context.get('search_results', [])],
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': session_id
            }
            
            # Save conversation to database
            conversation_data = {
                'session_id': session_id,
                'user_message': user_message,
                'bot_response': response_text,
                'category': response_data['category'],
                'confidence_score': response_data['confidence_score'],
                'sources_used': json.dumps(response_data['sources_used'])
            }
            
            db_manager.add_conversation(conversation_data)
            
            logger.info(f"Generated conversation response for session {session_id}")
            return response_data
            
        except Exception as e:
            logger.error(f"Conversation response generation failed: {e}")
            return {
                'response': "I apologize, but I'm having trouble processing your request right now.",
                'confidence_score': 0.0,
                'category': 'philosophy',
                'sources_used': [],
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': session_id
            }
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get information about available voices"""
        try:
            if self.tts_engine is None:
                return {'error': 'Text-to-speech engine not available'}
            
            voices = self.tts_engine.getProperty('voices')
            voice_info = []
            
            for voice in voices:
                voice_info.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': voice.gender,
                    'age': voice.age
                })
            
            return {
                'available_voices': voice_info,
                'current_voice': self.tts_engine.getProperty('voice'),
                'rate': self.tts_engine.getProperty('rate'),
                'volume': self.tts_engine.getProperty('volume')
            }
            
        except Exception as e:
            logger.error(f"Failed to get voice info: {e}")
            return {'error': str(e)}
    
    def set_voice_properties(self, rate: Optional[int] = None, volume: Optional[float] = None, voice_id: Optional[str] = None) -> bool:
        """Set voice properties"""
        try:
            if self.tts_engine is None:
                return False
            
            if rate is not None:
                self.tts_engine.setProperty('rate', rate)
                self.voice_rate = rate
            
            if volume is not None:
                self.tts_engine.setProperty('volume', volume)
                self.voice_volume = volume
            
            if voice_id is not None:
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if voice_id in voice.id:
                        self.tts_engine.setProperty('voice', voice.id)
                        self.voice_id = voice_id
                        break
            
            logger.info("Voice properties updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set voice properties: {e}")
            return False

# Global NLG engine instance
nlg_engine = NLGEngine() 