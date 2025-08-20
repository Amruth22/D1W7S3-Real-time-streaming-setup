#!/usr/bin/env python3
"""
Minimal WebSocket server to test basic functionality
"""

import asyncio
import websockets
import json

async def handle_client(websocket, path):
    """Handle WebSocket client"""
    print(f"Client connected from {websocket.remote_address}")
    
    try:
        # Send welcome message
        await websocket.send(json.dumps({
            "type": "connection_status",
            "status": "connected",
            "message": "Minimal server working"
        }))
        
        # Handle messages
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"Received: {data}")
                
                # Echo back
                await websocket.send(json.dumps({
                    "type": "echo",
                    "original": data,
                    "message": "Message received successfully"
                }))
                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON"
                }))
                
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected normally")
    except Exception as e:
        print(f"Client error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Client connection ended")

async def main():
    """Start minimal server"""
    print("Starting minimal WebSocket server on port 8080...")
    
    try:
        server = await websockets.serve(
            handle_client,
            "localhost",
            8080
        )
        
        print("Minimal server running on ws://localhost:8080")
        print("Press Ctrl+C to stop")
        
        await server.wait_closed()
        
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())