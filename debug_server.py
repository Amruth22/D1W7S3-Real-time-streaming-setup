#!/usr/bin/env python3
"""
Debug server to identify initialization issues
"""

import asyncio
import websockets
import json
import traceback
import config

class DebugServer:
    def __init__(self, port):
        self.port = port
        self.clients = set()
        self.initialization_error = None
        
        # Try to initialize components and catch errors
        try:
            print(f"Initializing components for port {self.port}...")
            self.init_components()
            print("All components initialized successfully")
        except Exception as e:
            self.initialization_error = str(e)
            print(f"Initialization error: {e}")
            traceback.print_exc()
    
    def init_components(self):
        """Initialize all components with error tracking"""
        print("1. Testing basic imports...")
        import os
        import json
        import base64
        print("   Basic imports OK")
        
        print("2. Testing config...")
        print(f"   GEMINI_API_KEY: {'SET' if config.GEMINI_API_KEY else 'NOT SET'}")
        print(f"   EMBEDDING_MODEL: {config.EMBEDDING_MODEL}")
        print("   Config OK")
        
        print("3. Testing document processor...")
        from document_processor import DocumentProcessor
        self.document_processor = DocumentProcessor()
        print("   Document processor OK")
        
        print("4. Testing sentence transformers...")
        from sentence_transformers import SentenceTransformer
        print(f"   Loading model: {config.EMBEDDING_MODEL}")
        model = SentenceTransformer(config.EMBEDDING_MODEL)
        print("   Sentence transformers OK")
        
        print("5. Testing vector search...")
        from vector_search import VectorSearch
        self.vector_search = VectorSearch()
        print("   Vector search OK")
        
        print("6. Testing Gemini client...")
        from gemini_client import GeminiClient
        self.gemini_client = GeminiClient()
        print("   Gemini client OK")
        
        print("7. Creating directories...")
        import os
        os.makedirs("data/uploads", exist_ok=True)
        print("   Directories OK")
    
    async def register_client(self, websocket):
        """Register client"""
        self.clients.add(websocket)
        
        if self.initialization_error:
            await websocket.send(json.dumps({
                "type": "initialization_error",
                "error": self.initialization_error,
                "server_port": self.port
            }))
        else:
            await websocket.send(json.dumps({
                "type": "connection_status",
                "status": "connected",
                "server_port": self.port,
                "message": f"Debug server on port {self.port} - All systems OK"
            }))
        
        print(f"Client connected to debug server {self.port}")
    
    async def unregister_client(self, websocket):
        """Unregister client"""
        self.clients.discard(websocket)
        print(f"Client disconnected from debug server {self.port}")
    
    async def handle_message(self, websocket, message):
        """Handle messages with detailed error reporting"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            print(f"Received message type: {message_type}")
            
            if message_type == "test_connection":
                await websocket.send(json.dumps({
                    "type": "test_response",
                    "message": "Connection test successful",
                    "server_port": self.port,
                    "initialization_ok": self.initialization_error is None
                }))
            
            elif message_type == "get_debug_info":
                debug_info = {
                    "type": "debug_info",
                    "server_port": self.port,
                    "initialization_error": self.initialization_error,
                    "components_loaded": self.initialization_error is None,
                    "active_clients": len(self.clients)
                }
                await websocket.send(json.dumps(debug_info))
            
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Debug server - unknown message type: {message_type}"
                }))
                
        except json.JSONDecodeError as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"JSON decode error: {str(e)}"
            }))
        except Exception as e:
            error_msg = f"Message handling error: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            await websocket.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
    
    async def handle_client(self, websocket):
        """Handle client connection"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            print("Client connection closed normally")
        except Exception as e:
            print(f"Client error: {e}")
            traceback.print_exc()
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start debug server"""
        print(f"Starting debug server on port {self.port}")
        
        async def handler(websocket, path):
            await self.handle_client(websocket)
        
        try:
            server = await websockets.serve(
                handler,
                config.HOST,
                self.port
            )
            
            print(f"Debug server running on ws://{config.HOST}:{self.port}")
            print(f"Initialization status: {'OK' if not self.initialization_error else 'ERROR'}")
            
            await server.wait_closed()
            
        except Exception as e:
            print(f"Server start error: {e}")
            traceback.print_exc()

async def main():
    """Start debug server"""
    server = DebugServer(8080)
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())