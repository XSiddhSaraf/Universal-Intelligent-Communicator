#!/usr/bin/env python3
"""
Script to start UnIC web interface
"""

import webbrowser
import time
import subprocess
import sys
from pathlib import Path

def start_web_interface():
    """Start the API server and open web interface"""
    print("🚀 Starting UnIC Web Interface...")
    
    # Start API server in background
    print("📡 Starting API server on port 8000...")
    api_process = subprocess.Popen([
        sys.executable, "main.py", "--mode", "api"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Open web interface
    web_path = Path(__file__).parent / "web_interface" / "index.html"
    if web_path.exists():
        print("🌐 Opening web interface...")
        webbrowser.open(f"file://{web_path.absolute()}")
        print("✅ Web interface opened!")
        print("\n📋 Available API endpoints:")
        print("   • Health: http://localhost:8000/health")
        print("   • Chat: http://localhost:8000/api/chat")
        print("   • Search: http://localhost:8000/api/search")
        print("   • Statistics: http://localhost:8000/api/statistics")
        print("\n🔄 Press Ctrl+C to stop the server")
        
        try:
            # Keep the script running
            api_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            api_process.terminate()
            print("✅ Server stopped!")
    else:
        print("❌ Web interface file not found!")
        api_process.terminate()

if __name__ == "__main__":
    start_web_interface() 