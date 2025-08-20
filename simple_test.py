#!/usr/bin/env python3
"""
Simple WebSocket test client to debug connection issues
"""

import asyncio
import websockets
import json

async def test_debug_server():
    """Test the debug server"""
    try:
        print("Connecting to debug server...")
        uri = "ws://localhost:8080"
        
        async with websockets.connect(uri) as websocket:
            print("Connected successfully!")
            
            # Wait for initial message
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            print(f"Initial message: {data}")
            
            # Send test message
            await websocket.send(json.dumps({"type": "test_connection"}))
            
            # Get response
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            print(f"Test response: {data}")
            
            # Get debug info
            await websocket.send(json.dumps({"type": "get_debug_info"}))
            
            # Get debug response
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            print(f"Debug info: {data}")
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_debug_server())