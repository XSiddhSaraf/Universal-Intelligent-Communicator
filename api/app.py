"""
Flask API Server for Universal Intelligent Communicator (UnIC)
Provides REST endpoints for the UnIC system
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from flask import Flask, request, jsonify, send_file, session
from pathlib import Path
from flask_cors import CORS
import json
from functools import wraps

from config import API_CONFIG, LOGGING_CONFIG, AUTH_CONFIG
from core.database import db_manager
from core.nlp_engine import nlp_engine
from core.nlg_engine import nlg_engine
from ingestion.data_ingestion import ingestion_manager

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

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production!
CORS(app, origins=['*'], methods=['GET', 'POST', 'PUT', 'DELETE'], allow_headers=['Content-Type', 'Authorization'])

# Authentication decorator
def require_auth(f):
    """Decorator to require authentication for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session token in Authorization header or session
        auth_header = request.headers.get('Authorization')
        session_token = None
        
        if auth_header and auth_header.startswith('Bearer '):
            session_token = auth_header.split(' ')[1]
        elif 'session_token' in session:
            session_token = session['session_token']
        
        if not session_token:
            return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
        
        # Validate session
        user = db_manager.validate_session(session_token)
        if not user:
            return jsonify({'error': 'Invalid or expired session', 'code': 'INVALID_SESSION'}), 401
        
        # Add user to request context
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if not request.current_user.is_admin:
            return jsonify({'error': 'Admin privileges required', 'code': 'ADMIN_REQUIRED'}), 403
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'UnIC API'
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for debugging"""
    return jsonify({
        'message': 'API is working!',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/', methods=['GET'])
def serve_web_interface():
    """Serve the web interface"""
    try:
        web_path = Path(__file__).parent.parent / "web_interface" / "index.html"
        if web_path.exists():
            return send_file(web_path)
        else:
            return jsonify({'error': 'Web interface not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Authentication endpoints

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        if not AUTH_CONFIG['allow_registration']:
            return jsonify({'error': 'Registration is disabled'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email is required'}), 400
        
        if not password or len(password) < AUTH_CONFIG['password_min_length']:
            return jsonify({'error': f'Password must be at least {AUTH_CONFIG["password_min_length"]} characters long'}), 400
        
        try:
            user_id = db_manager.create_user(username, email, password)
            logger.info(f"New user registered: {username}")
            
            return jsonify({
                'message': 'User registered successfully',
                'user_id': user_id,
                'username': username,
                'requires_approval': AUTH_CONFIG['require_admin_approval']
            }), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 409
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Authenticate user
        user = db_manager.authenticate_user(username, password)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create session
        session_token = db_manager.create_session(
            user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            expires_hours=AUTH_CONFIG['session_timeout_hours']
        )
        
        # Store in session
        session['session_token'] = session_token
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Login successful',
            'session_token': session_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """User logout endpoint"""
    try:
        # Get session token
        auth_header = request.headers.get('Authorization')
        session_token = None
        
        if auth_header and auth_header.startswith('Bearer '):
            session_token = auth_header.split(' ')[1]
        elif 'session_token' in session:
            session_token = session['session_token']
        
        if session_token:
            db_manager.invalidate_session(session_token)
        
        # Clear session
        session.clear()
        
        return jsonify({'message': 'Logout successful'})
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information"""
    try:
        user = request.current_user
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        })
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({'error': 'Failed to get user info'}), 500

@app.route('/api/chat', methods=['POST'])
@require_auth
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message']
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Generate response
        response_data = nlg_engine.generate_conversation_response(message, session_id)
        
        # Store conversation with user_id
        conversation_data = {
            'session_id': session_id,
            'user_id': request.current_user.id,
            'user_message': message,
            'bot_response': response_data['response'],
            'category': response_data['category'],
            'confidence_score': response_data['confidence_score'],
            'sources_used': json.dumps(response_data.get('sources_used', []))
        }
        db_manager.add_conversation(conversation_data)
        
        return jsonify({
            'response': response_data['response'],
            'session_id': session_id,
            'confidence_score': response_data['confidence_score'],
            'category': response_data['category'],
            'timestamp': response_data['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/search', methods=['POST'])
@require_auth
def search():
    """Search knowledge base"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        category = data.get('category')
        
        # Perform search
        results = nlp_engine.semantic_search(query, category=category)
        
        return jsonify({
            'query': query,
            'results': results,
            'total_results': len(results)
        })
        
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/ingest', methods=['POST'])
@require_admin
def ingest_data():
    """Trigger data ingestion"""
    try:
        data = request.get_json() or {}
        source_type = data.get('source_type', 'all')
        
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
            return jsonify({'error': 'Invalid source type'}), 400
        
        return jsonify({
            'message': 'Data ingestion completed',
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Ingest endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/upload', methods=['POST'])
@require_auth
def upload_file():
    """Upload and process files"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        category = request.form.get('category', 'philosophy')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file temporarily
        import tempfile
        import os
        from pathlib import Path
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            file.save(tmp_file.name)
            tmp_path = Path(tmp_file.name)
        
        try:
            # Process file
            file_data = ingestion_manager.process_file_upload(tmp_path, category)
            
            # Add to database
            entry_id = db_manager.add_knowledge_entry(file_data)
            
            return jsonify({
                'message': 'File uploaded and processed successfully',
                'entry_id': entry_id,
                'title': file_data['title'],
                'category': file_data['category']
            })
            
        finally:
            # Clean up temporary file
            if tmp_path.exists():
                os.unlink(tmp_path)
        
    except Exception as e:
        logger.error(f"Upload endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        stats = db_manager.get_statistics()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Statistics endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/conversations/<session_id>', methods=['GET'])
@require_auth
def get_conversation_history(session_id):
    """Get conversation history for a session"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        # Get conversations for the current user only
        from core.database import Conversation
        with db_manager.get_session() as db_session:
            conversations = db_session.query(Conversation).filter(
                Conversation.session_id == session_id,
                Conversation.user_id == request.current_user.id
            ).order_by(Conversation.timestamp.desc()).limit(limit).all()
        
        history = []
        for conv in conversations:
            history.append({
                'id': conv.id,
                'user_message': conv.user_message,
                'bot_response': conv.bot_response,
                'timestamp': conv.timestamp.isoformat(),
                'category': conv.category,
                'confidence_score': conv.confidence_score
            })
        
        return jsonify({
            'session_id': session_id,
            'conversations': history,
            'total': len(history)
        })
        
    except Exception as e:
        logger.error(f"Conversation history endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/voice/speak', methods=['POST'])
@require_auth
def speak_text():
    """Text-to-speech endpoint"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        success = nlg_engine.speak_text(text)
        
        return jsonify({
            'success': success,
            'message': 'Text spoken successfully' if success else 'Text-to-speech failed'
        })
        
    except Exception as e:
        logger.error(f"Speak endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/voice/listen', methods=['POST'])
@require_auth
def listen_speech():
    """Speech-to-text endpoint"""
    try:
        data = request.get_json() or {}
        timeout = data.get('timeout', 5)
        
        text = nlg_engine.listen_for_speech(timeout=timeout)
        
        return jsonify({
            'success': text is not None,
            'text': text,
            'message': 'Speech recognized' if text else 'No speech detected'
        })
        
    except Exception as e:
        logger.error(f"Listen endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/voice/info', methods=['GET'])
def get_voice_info():
    """Get voice information"""
    try:
        voice_info = nlg_engine.get_voice_info()
        return jsonify(voice_info)
        
    except Exception as e:
        logger.error(f"Voice info endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/voice/settings', methods=['POST'])
@require_auth
def set_voice_settings():
    """Set voice properties"""
    try:
        data = request.get_json()
        rate = data.get('rate')
        volume = data.get('volume')
        voice_id = data.get('voice_id')
        
        success = nlg_engine.set_voice_properties(rate=rate, volume=volume, voice_id=voice_id)
        
        return jsonify({
            'success': success,
            'message': 'Voice settings updated' if success else 'Failed to update voice settings'
        })
        
    except Exception as e:
        logger.error(f"Voice settings endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/analyze', methods=['POST'])
@require_auth
def analyze_text():
    """Analyze text comprehensively"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        
        # Perform comprehensive analysis
        analysis = {
            'sentiment': nlp_engine.analyze_sentiment(text),
            'category': nlp_engine.categorize_text(text),
            'keywords': nlp_engine.extract_keywords(text),
            'entities': nlp_engine.extract_entities(text),
            'summary': nlp_engine.generate_summary(text)
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Analyze endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/knowledge', methods=['GET'])
@require_auth
def get_knowledge_entries():
    """Get knowledge entries with filtering"""
    try:
        category = request.args.get('category')
        source_type = request.args.get('source_type')
        limit = request.args.get('limit', 100, type=int)
        
        entries = db_manager.get_knowledge_entries(
            category=category,
            source_type=source_type,
            limit=limit
        )
        
        knowledge_list = []
        for entry in entries:
            knowledge_list.append({
                'id': entry.id,
                'title': entry.title,
                'content': entry.content[:500] + '...' if len(entry.content) > 500 else entry.content,
                'category': entry.category,
                'author': entry.author,
                'source': entry.source,
                'date_added': entry.date_added.isoformat(),
                'confidence_score': entry.confidence_score
            })
        
        return jsonify({
            'entries': knowledge_list,
            'total': len(knowledge_list),
            'filters': {
                'category': category,
                'source_type': source_type,
                'limit': limit
            }
        })
        
    except Exception as e:
        logger.error(f"Knowledge entries endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting UnIC API server...")
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    ) 