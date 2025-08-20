#!/usr/bin/env python3
"""
Script to run both WebSocket servers for load balancing
"""

import asyncio
import subprocess
import sys
import os
import time
import threading
import config

def check_requirements():
    """Check if required packages are installed"""
    try:
        import websockets
        import sentence_transformers
        import faiss
        import numpy
        import google.genai
        import fitz  # PyMuPDF
        print("All required packages are installed")
        return True
    except ImportError as e:
        print(f"Missing package: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "data/uploads",
        "data/faiss_index"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def start_server(port):
    """Start WebSocket server on specified port"""
    if port == config.PRIMARY_PORT:
        script_name = "websocket_server_8080.py"
    else:
        script_name = "websocket_server_8081.py"
    
    try:
        subprocess.run([sys.executable, script_name], check=True)
    except KeyboardInterrupt:
        print(f"Server on port {port} stopped")
    except Exception as e:
        print(f"Error running server on port {port}: {e}")

def main():
    """Main function to start both servers"""
    print("Live Document Q&A System - Server Startup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check config
    if not os.path.exists("config.py"):
        print("config.py not found!")
        sys.exit(1)
    
    print("\nStarting WebSocket servers...")
    print(f"Primary server: ws://localhost:{config.PRIMARY_PORT}")
    print(f"Secondary server: ws://localhost:{config.SECONDARY_PORT}")
    print("Client interface: Open client.html in your browser")
    print("Press Ctrl+C to stop both servers")
    print("=" * 50)
    
    try:
        # Start primary server in background thread
        primary_thread = threading.Thread(
            target=start_server, 
            args=(config.PRIMARY_PORT,), 
            daemon=True
        )
        primary_thread.start()
        
        # Wait a moment for primary server to start
        time.sleep(2)
        
        # Start secondary server in main thread
        start_server(config.SECONDARY_PORT)
        
    except KeyboardInterrupt:
        print("\nShutting down servers...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()