# Live Document Q&A System

A real-time document processing and question-answering system with WebSocket load balancing, local vector search, and AI-powered responses.

## Architecture

**Dual WebSocket Server Setup with Load Balancing:**
- **Primary Server** (Port 8080): Main WebSocket server
- **Secondary Server** (Port 8081): Backup WebSocket server  
- **Client-side Load Balancing**: Automatic server selection and failover
- **Local Vector Search**: sentence-transformers + FAISS
- **AI Integration**: Gemini 2.0 Flash for intelligent responses

```
Client (Load Balancer) 
    ↓ 
WebSocket Server 8080 ←→ FAISS + sentence-transformers ←→ Gemini API
WebSocket Server 8081 ←→ FAISS + sentence-transformers ←→ Gemini API
    ↑
PyMuPDF (PDF processing)
```

## Features

### Real-time Streaming
- **File Upload Progress**: Live progress updates during file upload
- **Document Processing**: Real-time status during PDF text extraction
- **Embedding Creation**: Progress updates during vector embedding generation
- **Search Results**: Instant search results as user types
- **AI Responses**: Streaming AI responses from Gemini 2.0 Flash

### Local Vector Search
- **sentence-transformers**: Local embedding generation (all-MiniLM-L6-v2)
- **FAISS Integration**: Fast similarity search and indexing
- **Document Chunking**: Intelligent text splitting for better search
- **Real-time Search**: Search as you type functionality

### WebSocket Load Balancing
- **Dual Server Setup**: Primary (8080) and Secondary (8081) servers
- **Client-side Balancing**: Automatic server selection
- **Failover Mechanism**: Seamless switching if server is down
- **Connection Management**: Automatic reconnection with backoff

### Document Processing
- **PyMuPDF**: Fast PDF text extraction
- **Text Files**: Support for .txt files
- **Progress Streaming**: Real-time processing updates
- **Chunking**: Intelligent text segmentation

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure API key:**
   - Edit `config.py`
   - Add your Gemini API key
   - Get key from: https://makersuite.google.com/app/apikey

3. **Start both servers:**
```bash
python run_servers.py
```

4. **Open client interface:**
   - Open `client.html` in your web browser
   - The client will automatically connect to available servers

## Manual Server Setup

**Start Primary Server (Terminal 1):**
```bash
python websocket_server_8080.py
```

**Start Secondary Server (Terminal 2):**
```bash
python websocket_server_8081.py
```

## Usage Flow

1. **Upload Documents:**
   - Drag and drop PDF or text files
   - Watch real-time processing progress
   - Documents are automatically indexed

2. **Search Documents:**
   - Type in search box for instant results
   - See relevance scores and source files
   - Results update as you type

3. **Ask Questions:**
   - Enter questions about your documents
   - AI searches relevant content first
   - Get streaming responses with context

## WebSocket Message Types

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

**Get Stats:**
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

## Configuration

Edit `config.py` to customize:

```python
# Gemini API
GEMINI_API_KEY = "your-api-key-here"
GEMINI_MODEL = "gemini-2.0-flash"

# WebSocket Servers
PRIMARY_PORT = 8080
SECONDARY_PORT = 8081

# Vector Search
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
MAX_SEARCH_RESULTS = 5
SIMILARITY_THRESHOLD = 0.6

# Document Processing
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

## Testing

Run comprehensive unit tests:
```bash
python unit_test.py
```

**Tests cover:**
- **Text Chunking**: Document segmentation functionality
- **File Saving**: Upload and storage mechanisms
- **Vector Store**: FAISS initialization and operations
- **Gemini Client**: AI integration setup
- **WebSocket Messages**: Message format validation

## Project Structure

```
├── websocket_server_8080.py    # Primary WebSocket server
├── websocket_server_8081.py    # Secondary WebSocket server
├── document_processor.py       # PyMuPDF document processing
├── vector_search.py           # sentence-transformers + FAISS
├── gemini_client.py           # Gemini 2.0 Flash integration
├── client.html                # Web client interface
├── client.js                  # Client-side load balancing
├── config.py                  # Configuration settings
├── unit_test.py              # Unit tests (5 core tests)
├── run_servers.py            # Server startup script
├── requirements.txt          # Dependencies
└── data/
    ├── uploads/              # Uploaded files
    ├── faiss_index/         # Vector index storage
    └── sample_document.txt  # Sample document
```

## Load Balancing Logic

The client implements intelligent load balancing:

1. **Server Priority**: Attempts primary server (8080) first
2. **Automatic Failover**: Switches to secondary (8081) if primary fails
3. **Health Monitoring**: Continuously monitors connection status
4. **Reconnection**: Automatic reconnection with exponential backoff
5. **Round Robin**: Alternates between servers for load distribution

## Troubleshooting

### Common Issues

**Servers won't start:**
- Check if ports 8080/8081 are available
- Verify all dependencies are installed
- Ensure config.py has valid Gemini API key

**Client connection fails:**
- Make sure at least one server is running
- Check browser console for WebSocket errors
- Try refreshing the page

**File upload fails:**
- Check file size (max 50MB)
- Verify file type (.pdf or .txt only)
- Ensure sufficient disk space

**Search returns no results:**
- Upload documents first
- Wait for processing to complete
- Try different search terms

**AI responses fail:**
- Verify Gemini API key is valid
- Check internet connection
- Monitor API quotas and limits

### Performance Tips

- Upload documents in smaller batches
- Use descriptive filenames
- Keep document chunks reasonably sized
- Monitor system resources during processing

## Dependencies

- **websockets**: WebSocket server implementation
- **sentence-transformers**: Local embedding generation
- **faiss-cpu**: Fast similarity search
- **google-genai**: Gemini API integration
- **PyMuPDF**: PDF text extraction
- **numpy**: Numerical computations

## System Requirements

- Python 3.8+
- 4GB+ RAM (for sentence-transformers)
- Modern web browser with WebSocket support
- Internet connection (for Gemini API)

## Real-time Features Summary

- File upload progress streaming
- Document processing status updates
- Real-time vector embedding creation
- Instant search as you type
- Live AI response streaming
- Automatic server failover
- Connection status monitoring
- System statistics updates