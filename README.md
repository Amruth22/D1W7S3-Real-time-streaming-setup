# Live Document Q&A System - Backend

A high-performance document processing and question-answering backend system with WebSocket APIs, local vector search, and AI-powered responses.

## Architecture

**Dual WebSocket Server Backend:**
- **Primary Server** (Port 8080): Main WebSocket server
- **Secondary Server** (Port 8081): Backup WebSocket server with load balancing
- **Local Vector Search**: sentence-transformers + FAISS for fast semantic search
- **AI Integration**: Google Gemini 2.0 Flash for intelligent responses

```
WebSocket Client
    ↓ 
WebSocket Server 8080 ←→ FAISS + sentence-transformers ←→ Gemini API
WebSocket Server 8081 ←→ FAISS + sentence-transformers ←→ Gemini API
    ↑
PyMuPDF (PDF processing)
```

## Features

### Real-time Streaming Backend
- **File Upload Progress**: Live progress updates during file upload
- **Document Processing**: Real-time status during PDF text extraction
- **Embedding Creation**: Progress updates during vector embedding generation  
- **Search Results**: Fast semantic search with relevance scoring
- **AI Responses**: Streaming AI responses from Gemini 2.0 Flash

### Local Vector Search Engine
- **sentence-transformers**: Local embedding generation (all-MiniLM-L6-v2)
- **FAISS Integration**: Fast similarity search and indexing
- **Document Chunking**: Intelligent text splitting for optimal search
- **Persistent Storage**: Automatic index saving and loading

### WebSocket Load Balancing
- **Dual Server Setup**: Primary (8080) and Secondary (8081) servers
- **Automatic Failover**: Server redundancy for high availability
- **Connection Management**: Proper WebSocket connection handling

### Document Processing Engine
- **PyMuPDF**: Fast PDF text extraction with progress tracking
- **Text Files**: Support for .txt files
- **Progress Streaming**: Real-time processing status updates
- **Chunking**: Intelligent text segmentation with configurable overlap

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Copy the environment template
cp .env.example .env

# Edit .env file and add your Gemini API key
# Get key from: https://makersuite.google.com/app/apikey
```

**In .env file:**
```bash
GEMINI_API_KEY=your-actual-api-key-here
```

### 3. Start Backend Servers
```bash
# Start both servers (recommended)
python run_servers.py

# OR start individually
python websocket_server_8080.py  # Terminal 1
python websocket_server_8081.py  # Terminal 2
```

### 4. Test the Backend
```bash
python unit_test.py
```

## WebSocket API Endpoints

### Server Endpoints
- **Primary**: `ws://localhost:8080`
- **Secondary**: `ws://localhost:8081`

### Client to Server Messages

**File Upload:**
```json
{
  "type": "file_upload",
  "filename": "document.pdf",
  "file_data": "base64_encoded_data"
}
```

**Search Query:**
```json
{
  "type": "search_query",
  "query": "machine learning concepts"
}
```

**Ask Question:**
```json
{
  "type": "ask_question",
  "question": "What is supervised learning?"
}
```

**Get Statistics:**
```json
{
  "type": "get_stats"
}
```

### Server to Client Messages

**Connection Status:**
```json
{
  "type": "connection_status",
  "status": "connected",
  "server_port": 8080,
  "message": "Connected to server on port 8080"
}
```

**Processing Progress:**
```json
{
  "type": "processing_status",
  "status": "Extracting text from page 1/10",
  "progress": 25
}
```

**Search Results:**
```json
{
  "type": "search_results",
  "results": [
    {
      "text": "Machine learning is...",
      "score": 0.85,
      "metadata": {
        "filename": "ml_guide.pdf",
        "chunk_id": 0
      }
    }
  ],
  "query": "machine learning",
  "total_found": 5
}
```

**AI Response Streaming:**
```json
{
  "type": "ai_chunk",
  "content": "Machine learning "
}
```

**AI Response Complete:**
```json
{
  "type": "ai_complete",
  "response": "Complete response text",
  "question": "What is supervised learning?",
  "context_used": true
}
```

## Configuration

### Environment Variables (.env file)
Copy `.env.example` to `.env` and customize:
```bash
# Required: Gemini API key
GEMINI_API_KEY=your-actual-api-key-here

# Optional: Override defaults
GEMINI_MODEL=gemini-2.0-flash
PRIMARY_PORT=8080
SECONDARY_PORT=8081
HOST=localhost
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
MAX_SEARCH_RESULTS=5
SIMILARITY_THRESHOLD=0.6
UPLOAD_DIR=data/uploads
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_FILE_SIZE=52428800
```

### Setup Steps
1. **Copy template**: `cp .env.example .env`
2. **Get API key**: Visit https://makersuite.google.com/app/apikey
3. **Edit .env**: Add your actual Gemini API key
4. **Start servers**: `python run_servers.py`

## Testing

Run comprehensive integration tests:
```bash
python unit_test.py
```

**Test Coverage (10 Tests):**
- ✅ Server connections (both ports)
- ✅ Statistics requests  
- ✅ File upload and processing
- ✅ Document indexing and embedding
- ✅ Vector search functionality
- ✅ AI question answering
- ✅ Real-time streaming responses
- ✅ Error handling
- ✅ Load balancing
- ✅ WebSocket message validation

## Project Structure

```
D1W7S3-Real-time-streaming-setup/
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── run_servers.py              # Server startup script
├── unit_test.py                # Comprehensive tests (10 tests)
├── websocket_server_8080.py    # Primary WebSocket server
├── websocket_server_8081.py    # Secondary WebSocket server
├── document_processor.py       # PyMuPDF document processing
├── vector_search.py           # sentence-transformers + FAISS
├── gemini_client.py           # Gemini 2.0 Flash integration
├── data/
│   ├── uploads/                # Uploaded files storage
│   ├── faiss_index/           # Vector index storage
│   │   ├── faiss.index        # FAISS vector index
│   │   └── documents.json     # Document metadata
│   └── sample_document.txt    # Sample document
└── README.md                   # This file
```

## Performance & Scalability

### Current Performance
- **Local Vector Search**: Sub-second response times
- **Document Processing**: Real-time progress streaming
- **Concurrent Connections**: Multiple WebSocket clients supported
- **Memory Usage**: Optimized FAISS indexing
- **File Processing**: 50MB max file size, PDF + TXT support

### Load Balancing Features
- **Dual Server Setup**: Primary/secondary server redundancy
- **Automatic Failover**: Client-side connection management
- **Health Monitoring**: Server status tracking
- **Persistent Storage**: Shared FAISS index between servers

## Dependencies

**Core Backend:**
- `websockets>=11.0.0` - WebSocket server implementation
- `sentence-transformers>=2.0.0` - Local embedding generation
- `faiss-cpu>=1.7.0` - Fast similarity search
- `google-genai>=0.3.0` - Gemini API integration
- `PyMuPDF>=1.20.0` - PDF text extraction
- `numpy>=1.21.0` - Numerical computations

**Testing:**
- `pytest>=7.0.0` - Testing framework

## System Requirements

- **Python**: 3.8+
- **Memory**: 4GB+ RAM (for sentence-transformers model)
- **Storage**: 2GB+ for models and indices
- **Network**: Internet connection (for Gemini API)
- **OS**: Windows, macOS, Linux

## Troubleshooting

### Common Issues

**Servers won't start:**
- Check if ports 8080/8081 are available
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure `.env` file exists with valid Gemini API key
- Check `.env` file format: `GEMINI_API_KEY=your-key-here`

**Connection failures:**
- Make sure at least one server is running
- Check firewall settings for ports 8080/8081
- Verify WebSocket client implementation

**File upload fails:**
- Check file size (max 50MB)
- Verify file type (.pdf or .txt only)
- Ensure sufficient disk space in data/uploads/

**Search returns no results:**
- Upload and process documents first
- Wait for embedding completion
- Check similarity threshold in config.py

**AI responses fail:**
- Check `.env` file contains valid Gemini API key
- Verify API key is active: https://makersuite.google.com/app/apikey
- Check internet connection
- Monitor API rate limits
- Ensure `python-dotenv` is installed: `pip install python-dotenv`

### Performance Optimization

- **Memory**: Monitor RAM usage during large file processing
- **Storage**: Regularly clean up data/uploads/ directory
- **Network**: Ensure stable internet for Gemini API calls
- **Concurrent Users**: Scale by running multiple server instances

## API Integration Examples

### Python WebSocket Client
```python
import asyncio
import websockets
import json
import base64

async def connect_to_backend():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        # Upload file
        with open("document.pdf", "rb") as f:
            file_data = base64.b64encode(f.read()).decode()
        
        await websocket.send(json.dumps({
            "type": "file_upload",
            "filename": "document.pdf",
            "file_data": file_data
        }))
        
        # Handle responses
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data['type']}")

asyncio.run(connect_to_backend())
```

### Search and Q&A Example
```python
# Search documents
await websocket.send(json.dumps({
    "type": "search_query",
    "query": "machine learning algorithms"
}))

# Ask AI question
await websocket.send(json.dumps({
    "type": "ask_question", 
    "question": "Explain supervised learning"
}))
```

## Production Deployment

For production use:
1. **Environment Variables**: ✅ Already implemented with .env file
2. **HTTPS/WSS**: Use secure WebSocket connections
3. **Load Balancer**: Deploy behind a proper load balancer
4. **Monitoring**: Add logging and health check endpoints
5. **Authentication**: Implement user authentication
6. **Rate Limiting**: Add rate limiting for API calls
7. **Database**: Consider external database for document metadata
8. **Secret Management**: Use proper secret management (AWS Secrets, etc.)
9. **Container Deployment**: Docker/Kubernetes deployment

## License

This project is a backend system for document processing and Q&A functionality.