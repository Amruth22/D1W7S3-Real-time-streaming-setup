#!/usr/bin/env python3
"""
WebSocket server compatible with websockets 15.x API
"""

import asyncio
import websockets
import json
import base64
import os
import traceback
import config
from document_processor import DocumentProcessor
from vector_search import VectorSearch
from gemini_client import GeminiClient

class WorkingWebSocketServer:
    def __init__(self, port):
        self.port = port
        self.clients = set()
        
        # Initialize components
        try:
            print(f"Initializing server components for port {self.port}...")
            self.document_processor = DocumentProcessor()
            self.vector_search = VectorSearch()
            self.gemini_client = GeminiClient()
            os.makedirs("data/uploads", exist_ok=True)
            print("All components initialized successfully")
        except Exception as e:
            print(f"Component initialization error: {e}")
            traceback.print_exc()
            raise
    
    async def register_client(self, websocket):
        """Register new client"""
        self.clients.add(websocket)
        try:
            await websocket.send(json.dumps({
                "type": "connection_status",
                "status": "connected",
                "server_port": self.port,
                "message": f"Connected to server on port {self.port}"
            }))
            print(f"Client connected to server {self.port}. Total: {len(self.clients)}")
        except Exception as e:
            print(f"Error sending welcome message: {e}")
    
    async def unregister_client(self, websocket):
        """Unregister client"""
        self.clients.discard(websocket)
        print(f"Client disconnected from server {self.port}. Total: {len(self.clients)}")
    
    async def handle_message(self, websocket, message):
        """Handle incoming messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            print(f"Handling message type: {message_type}")
            
            if message_type == "get_stats":
                await self.handle_stats(websocket)
            elif message_type == "test_connection":
                await websocket.send(json.dumps({
                    "type": "test_response",
                    "message": "Connection test successful",
                    "server_port": self.port
                }))
            elif message_type == "file_upload":
                await self.handle_file_upload(websocket, data)
            elif message_type == "search_query":
                await self.handle_search_query(websocket, data)
            elif message_type == "ask_question":
                await self.handle_ask_question(websocket, data)
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }))
                
        except json.JSONDecodeError as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Invalid JSON: {str(e)}"
            }))
        except Exception as e:
            print(f"Message handling error: {e}")
            traceback.print_exc()
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Server error: {str(e)}"
            }))
    
    async def handle_stats(self, websocket):
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
    
    async def handle_file_upload(self, websocket, data):
        """Handle file upload"""
        try:
            filename = data.get("filename")
            file_data_b64 = data.get("file_data")
            
            if not filename or not file_data_b64:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Missing filename or file data"
                }))
                return
            
            # Decode and save file
            file_data = base64.b64decode(file_data_b64)
            file_path = self.document_processor.save_uploaded_file(filename, file_data)
            
            await websocket.send(json.dumps({
                "type": "upload_complete",
                "filename": filename,
                "size": len(file_data)
            }))
            
            # Process document
            async for update in self.document_processor.process_file(file_path, websocket):
                await websocket.send(json.dumps(update))
                
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
        """Handle search query"""
        try:
            query = data.get("query", "").strip()
            if not query:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Empty search query"
                }))
                return
            
            await self.vector_search.search(query, websocket)
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Search error: {str(e)}"
            }))
    
    async def handle_ask_question(self, websocket, data):
        """Handle AI question"""
        try:
            question = data.get("question", "").strip()
            if not question:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Empty question"
                }))
                return
            
            # Search for context
            search_results = await self.vector_search.search(question, websocket)
            
            # Prepare context
            context = ""
            if search_results:
                context_parts = [result[0] for result in search_results[:3]]
                context = "\n\n".join(context_parts)
            
            # Get AI response
            await self.gemini_client.stream_response(question, context, websocket)
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Question handling error: {str(e)}"
            }))

# Modern websockets handler function (standalone)
async def websocket_handler(websocket):
    """WebSocket handler compatible with websockets 15.x"""
    server = websocket_handler.server_instance
    
    await server.register_client(websocket)
    
    try:
        async for message in websocket:
            await server.handle_message(websocket, message)
            
    except websockets.exceptions.ConnectionClosed:
        print("Client connection closed normally")
    except Exception as e:
        print(f"Client handling error: {e}")
        traceback.print_exc()
    finally:
        await server.unregister_client(websocket)

async def start_server(port):
    """Start WebSocket server with modern API"""
    print(f"Starting WebSocket server on port {port}")
    
    try:
        # Create server instance
        server_instance = WorkingWebSocketServer(port)
        
        # Attach server instance to handler function
        websocket_handler.server_instance = server_instance
        
        # Start server with modern API
        async with websockets.serve(websocket_handler, config.HOST, port):
            print(f"WebSocket server running on ws://{config.HOST}:{port}")
            await asyncio.Future()  # Run forever
            
    except Exception as e:
        print(f"Server start error: {e}")
        traceback.print_exc()

async def main():
    """Start server"""
    try:
        await start_server(8080)
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())