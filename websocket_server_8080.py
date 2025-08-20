import asyncio
import websockets
import json
import base64
import os
from typing import Set
import config
from document_processor import DocumentProcessor
from vector_search import VectorSearch
from gemini_client import GeminiClient

class WebSocketServer:
    def __init__(self, port: int):
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.document_processor = DocumentProcessor()
        self.vector_search = VectorSearch()
        self.gemini_client = GeminiClient()
        
        # Create data directories
        os.makedirs("data/uploads", exist_ok=True)
    
    async def register_client(self, websocket):
        """Register new client connection"""
        self.clients.add(websocket)
        await websocket.send(json.dumps({
            "type": "connection_status",
            "status": "connected",
            "server_port": self.port,
            "message": f"Connected to server on port {self.port}"
        }))
        print(f"Client connected to server {self.port}. Total clients: {len(self.clients)}")
    
    async def unregister_client(self, websocket):
        """Unregister client connection"""
        self.clients.discard(websocket)
        print(f"Client disconnected from server {self.port}. Total clients: {len(self.clients)}")
    
    async def handle_message(self, websocket, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "file_upload":
                await self.handle_file_upload(websocket, data)
            elif message_type == "search_query":
                await self.handle_search_query(websocket, data)
            elif message_type == "ask_question":
                await self.handle_ask_question(websocket, data)
            elif message_type == "get_stats":
                await self.handle_get_stats(websocket)
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Invalid JSON message"
            }))
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Server error: {str(e)}"
            }))
    
    async def handle_file_upload(self, websocket, data):
        """Handle file upload with progress streaming"""
        try:
            filename = data.get("filename")
            file_data_b64 = data.get("file_data")
            
            if not filename or not file_data_b64:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Missing filename or file data"
                }))
                return
            
            # Check file extension
            if not any(filename.lower().endswith(ext) for ext in config.ALLOWED_EXTENSIONS):
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Unsupported file type. Allowed: {config.ALLOWED_EXTENSIONS}"
                }))
                return
            
            # Decode file data
            file_data = base64.b64decode(file_data_b64)
            
            # Check file size
            if len(file_data) > config.MAX_FILE_SIZE:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "File too large"
                }))
                return
            
            # Save file
            file_path = self.document_processor.save_uploaded_file(filename, file_data)
            
            # Send upload complete
            await websocket.send(json.dumps({
                "type": "upload_complete",
                "filename": filename,
                "size": len(file_data)
            }))
            
            # Process document
            async for update in self.document_processor.process_file(file_path, websocket):
                await websocket.send(json.dumps(update))
                
                # If processing complete, add to vector index
                if update.get("type") == "processing_complete":
                    chunks = update.get("chunks", [])
                    if chunks:
                        await self.vector_search.add_document(filename, chunks, websocket)
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"File upload error: {str(e)}"
            }))
    
    async def handle_search_query(self, websocket, data):
        """Handle search query with real-time results"""
        try:
            query = data.get("query", "").strip()
            if not query:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Empty search query"
                }))
                return
            
            # Perform search
            await self.vector_search.search(query, websocket)
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Search error: {str(e)}"
            }))
    
    async def handle_ask_question(self, websocket, data):
        """Handle question with AI response"""
        try:
            question = data.get("question", "").strip()
            if not question:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Empty question"
                }))
                return
            
            # First search for relevant context
            search_results = await self.vector_search.search(question, websocket)
            
            # Prepare context from search results
            context = ""
            if search_results:
                context_parts = [result[0] for result in search_results[:3]]
                context = "\n\n".join(context_parts)
            
            # Get AI response with context
            await self.gemini_client.stream_response(question, context, websocket)
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Question handling error: {str(e)}"
            }))
    
    async def handle_get_stats(self, websocket):
        """Handle stats request"""
        try:
            stats = self.vector_search.get_stats()
            stats["server_port"] = self.port
            stats["active_clients"] = len(self.clients)
            
            await websocket.send(json.dumps({
                "type": "stats",
                "data": stats
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Stats error: {str(e)}"
            }))
    
    async def handle_client(self, websocket):
        """Handle individual client connection"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start WebSocket server"""
        print(f"Starting WebSocket server on port {self.port}")
        
        async def handler(websocket, path):
            await self.handle_client(websocket)
        
        server = await websockets.serve(
            handler,
            config.HOST,
            self.port
        )
        
        print(f"WebSocket server running on ws://{config.HOST}:{self.port}")
        await server.wait_closed()

async def main():
    """Main function to start primary server"""
    server = WebSocketServer(config.PRIMARY_PORT)
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())