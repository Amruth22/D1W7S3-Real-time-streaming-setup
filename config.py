# Configuration for Live Document Q&A System

# Gemini API Configuration
GEMINI_API_KEY = ""
GEMINI_MODEL = "gemini-2.0-flash"

# WebSocket Server Configuration
PRIMARY_PORT = 8080
SECONDARY_PORT = 8081
HOST = "localhost"

# Vector Search Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
FAISS_INDEX_PATH = "data/faiss_index"
EMBEDDING_DIMENSION = 384
MAX_SEARCH_RESULTS = 5
SIMILARITY_THRESHOLD = 0.6

# Document Processing Configuration
UPLOAD_DIR = "data/uploads"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# File Processing
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = ['.pdf', '.txt']
