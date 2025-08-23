# Configuration for Live Document Q&A System

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API Configuration - loaded from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Validate API key
if not GEMINI_API_KEY:
    print("⚠️  WARNING: GEMINI_API_KEY not found in .env file!")
    print("Please add your Gemini API key to the .env file:")
    print("1. Copy .env.example to .env: cp .env.example .env")
    print("2. Get your API key from: https://makersuite.google.com/app/apikey")
    print("3. Add 'GEMINI_API_KEY=your-api-key-here' to .env file")
else:
    print(f"✅ Gemini API key loaded successfully (length: {len(GEMINI_API_KEY)})")

# WebSocket Server Configuration - can be overridden via environment variables
PRIMARY_PORT = int(os.getenv("PRIMARY_PORT", 8080))
SECONDARY_PORT = int(os.getenv("SECONDARY_PORT", 8081))
HOST = os.getenv("HOST", "localhost")

# Vector Search Configuration - can be overridden via environment variables
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "data/faiss_index")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 384))
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", 5))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.6))

# Document Processing Configuration - can be overridden via environment variables
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data/uploads")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

# File Processing
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB default
ALLOWED_EXTENSIONS = ['.pdf', '.txt']  # Static for security
