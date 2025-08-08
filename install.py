#!/usr/bin/env python3
"""
Installation script for Universal Intelligent Communicator (UnIC)
Sets up the system with all dependencies and initial configuration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import json

def print_banner():
    """Print installation banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    UnIC - Universal Intelligent Communicator                ║
    ║                                                              ║
    ║    Installation Script                                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def check_system_requirements():
    """Check system requirements"""
    print("\n🔍 Checking system requirements...")
    
    system = platform.system()
    print(f"   Operating System: {system}")
    
    # Check for required system packages
    if system == "Linux":
        # Check for audio dependencies
        try:
            subprocess.run(["which", "espeak"], check=True, capture_output=True)
            print("   ✅ espeak found")
        except subprocess.CalledProcessError:
            print("   ⚠️  espeak not found (text-to-speech may not work)")
            print("   Install with: sudo apt-get install espeak")
    
    elif system == "Darwin":  # macOS
        print("   ✅ macOS detected (text-to-speech should work)")
    
    elif system == "Windows":
        print("   ✅ Windows detected (text-to-speech should work)")
    
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ Error: requirements.txt not found!")
        return False
    
    try:
        # Upgrade pip first
        print("   Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install requirements
        print("   Installing requirements...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                               check=True, capture_output=True, text=True)
        
        print("✅ Python dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print(f"   Error output: {e.stderr}")
        return False

def download_nltk_data():
    """Download required NLTK data"""
    print("\n📚 Downloading NLTK data...")
    
    try:
        import nltk
        
        # Download required NLTK data
        nltk_data = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
        
        for data in nltk_data:
            print(f"   Downloading {data}...")
            nltk.download(data, quiet=True)
        
        print("✅ NLTK data downloaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "data_lake",
        "logs", 
        "models",
        "temp"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        print(f"   ✅ Created {directory}/")
    
    return True

def initialize_database():
    """Initialize the database"""
    print("\n🗄️  Initializing database...")
    
    try:
        from core.database import db_manager
        
        # Test database connection
        stats = db_manager.get_statistics()
        print("✅ Database initialized successfully")
        print(f"   Current entries: {stats['total_knowledge_entries']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def test_system_components():
    """Test system components"""
    print("\n🧪 Testing system components...")
    
    try:
        # Test imports
        from config import CATEGORIES, DATA_SOURCES
        from core.database import db_manager
        from core.nlp_engine import nlp_engine
        from core.nlg_engine import nlg_engine
        from ingestion.data_ingestion import ingestion_manager
        
        print("   ✅ All modules imported successfully")
        
        # Test NLP engine
        test_text = "Hello, world!"
        embedding = nlp_engine.get_embedding(test_text)
        if embedding:
            print("   ✅ NLP engine working")
        
        # Test NLG engine
        response = nlg_engine.generate_response({
            'query': 'Hello',
            'search_results': [],
            'confidence_score': 0.8,
            'category': 'philosophy'
        })
        if response:
            print("   ✅ NLG engine working")
        
        # Test database
        stats = db_manager.get_statistics()
        print("   ✅ Database working")
        
        print("✅ All system components tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error testing components: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    print("\n📝 Creating sample data...")
    
    try:
        from core.database import db_manager
        import json
        from datetime import datetime
        
        sample_entries = [
            {
                'title': 'Welcome to UnIC',
                'content': 'Welcome to the Universal Intelligent Communicator. I am here to help you explore knowledge, wisdom, and meaningful conversations.',
                'category': 'philosophy',
                'source': 'system',
                'source_type': 'manual',
                'author': 'UnIC System',
                'tags': json.dumps(['welcome', 'introduction', 'philosophy']),
                'confidence_score': 1.0
            },
            {
                'title': 'The Power of Knowledge',
                'content': 'Knowledge is the foundation of wisdom. Through learning and understanding, we can navigate the complexities of life with greater clarity and purpose.',
                'category': 'philosophy',
                'source': 'system',
                'source_type': 'manual',
                'author': 'UnIC System',
                'tags': json.dumps(['knowledge', 'wisdom', 'philosophy']),
                'confidence_score': 1.0
            },
            {
                'title': 'Innovation and Creativity',
                'content': 'Innovation is the process of creating something new and valuable. It requires creativity, persistence, and the courage to think differently.',
                'category': 'creativity',
                'source': 'system',
                'source_type': 'manual',
                'author': 'UnIC System',
                'tags': json.dumps(['innovation', 'creativity', 'thinking']),
                'confidence_score': 1.0
            }
        ]
        
        for entry in sample_entries:
            db_manager.add_knowledge_entry(entry)
        
        print(f"✅ Created {len(sample_entries)} sample entries")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def create_config_file():
    """Create configuration file if it doesn't exist"""
    print("\n⚙️  Checking configuration...")
    
    config_file = Path(".env")
    if not config_file.exists():
        print("   Creating .env file...")
        
        env_content = """# UnIC Configuration File
# Database Configuration (optional - uses SQLite by default)
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=unic_db
# DB_USER=unic_user
# DB_PASSWORD=your_password

# AWS Configuration (optional)
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
# S3_BUCKET=your_bucket_name

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=False

# Logging Configuration
LOG_LEVEL=INFO
"""
        
        with open(config_file, 'w') as f:
            f.write(env_content)
        
        print("   ✅ Created .env file")
    else:
        print("   ✅ Configuration file exists")
    
    return True

def show_usage_instructions():
    """Show usage instructions"""
    print("\n" + "="*60)
    print("🎉 UnIC Installation Complete!")
    print("="*60)
    
    print("\n🚀 Getting Started:")
    print("   1. Interactive Mode:")
    print("      python main.py --mode interactive")
    print("      python run.py")
    print()
    print("   2. API Server Mode:")
    print("      python main.py --mode api")
    print("      Then open web_interface/index.html in your browser")
    print()
    print("   3. Data Ingestion:")
    print("      python main.py --mode ingest --source all")
    print()
    print("   4. Run Tests:")
    print("      python test_unic.py")
    print()
    
    print("📚 Available Commands (Interactive Mode):")
    print("   help                    - Show available commands")
    print("   ingest [source]         - Ingest data from sources")
    print("   search <query>          - Search knowledge base")
    print("   stats                   - Show system statistics")
    print("   speak <text>            - Convert text to speech")
    print("   quit/exit/bye          - Exit the system")
    print()
    
    print("🌐 Web Interface:")
    print("   Start the API server and open web_interface/index.html")
    print("   Features: Chat interface, voice commands, file upload")
    print()
    
    print("📖 Documentation:")
    print("   README.md               - Complete documentation")
    print("   config.py               - Configuration settings")
    print()
    
    print("🔧 Troubleshooting:")
    print("   - Check logs/unic.log for error messages")
    print("   - Ensure all dependencies are installed")
    print("   - Verify database permissions")
    print("   - Check audio system for voice features")
    print()
    
    print("="*60)

def main():
    """Main installation function"""
    print_banner()
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_system_requirements():
        print("⚠️  Some system requirements may not be met, but installation will continue...")
    
    # Install dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Download NLTK data
    if not download_nltk_data():
        print("⚠️  Failed to download NLTK data, but installation will continue...")
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        sys.exit(1)
    
    # Test components
    if not test_system_components():
        print("❌ Failed to test system components")
        sys.exit(1)
    
    # Create sample data
    if not create_sample_data():
        print("⚠️  Failed to create sample data, but installation will continue...")
    
    # Create config file
    if not create_config_file():
        print("⚠️  Failed to create configuration file, but installation will continue...")
    
    # Show usage instructions
    show_usage_instructions()
    
    print("✅ Installation completed successfully!")

if __name__ == "__main__":
    main() 