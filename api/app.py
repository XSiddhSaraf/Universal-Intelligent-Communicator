"""
Flask API Server for Universal Intelligent Communicator (UnIC)
Provides REST endpoints for the UnIC system
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from flask import Flask, request, jsonify, send_file
from pathlib import Path
from flask_cors import CORS
import json

from config import API_CONFIG, LOGGING_CONFIG
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
CORS(app, origins=['*'], methods=['GET', 'POST', 'PUT', 'DELETE'], allow_headers=['Content-Type'])

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

@app.route('/api/chat', methods=['POST'])
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
def get_conversation_history(session_id):
    """Get conversation history for a session"""
    try:
        limit = request.args.get('limit', 50, type=int)
        conversations = db_manager.get_conversation_history(session_id, limit=limit)
        
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