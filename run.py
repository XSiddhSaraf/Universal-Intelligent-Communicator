#!/usr/bin/env python3
"""
Simple run script for UnIC - Universal Intelligent Communicator
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main run function"""
    print("🚀 Starting UnIC - Universal Intelligent Communicator")
    print("=" * 60)
    
    # Check if main.py exists
    main_file = project_root / "main.py"
    if not main_file.exists():
        print("❌ Error: main.py not found!")
        print("Please make sure you're running this from the project root directory.")
        sys.exit(1)
    
    # Import and run main
    try:
        from main import main as unic_main
        unic_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting UnIC: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 