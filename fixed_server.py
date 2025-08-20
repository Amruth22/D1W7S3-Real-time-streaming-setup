#!/usr/bin/env python3
"""
Fixed WebSocket server compatible with modern websockets library
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

class FixedWebSocketServer:
    def __init__(self, port):
        self.port = port
        self.clients = set()
        
        # Initialize components with error handling
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
    
    async def handle_client(self, websocket, path):
        """Handle client connection - compatible with websockets library"""
        print(f"New client connection from {websocket.remote_address}")
        
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            print("Client connection closed normally")
        except Exception as e:
            print(f"Client handling error: {e}")
            traceback.print_exc()
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start WebSocket server"""
        print(f"Starting WebSocket server on port {self.port}")
        
        try:
            # Use the handle_client method directly - it already has the right signature
            server = await websockets.serve(
                self.handle_client,
                config.HOST,
                self.port
            )
            
            print(f"WebSocket server running on ws://{config.HOST}:{self.port}")
            await server.wait_closed()
            
        except Exception as e:
            print(f"Server start error: {e}")
            traceback.print_exc()

async def main():
    """Start server"""
    try:
        server = FixedWebSocketServer(8080)
        await server.start_server()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())