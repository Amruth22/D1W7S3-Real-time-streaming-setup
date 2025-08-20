#!/usr/bin/env python3
"""
Test client for minimal WebSocket server
"""

import asyncio
import websockets
import json

async def test_minimal_server():
    """Test minimal server"""
    try:
        print("Connecting to minimal server...")
        
        async with websockets.connect("ws://localhost:8080") as websocket:
            print("Connected!")
            
            # Receive welcome message
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Welcome: {data}")
            
            # Send test message
            test_msg = {"type": "test", "content": "Hello server!"}
            await websocket.send(json.dumps(test_msg))
            print(f"Sent: {test_msg}")
            
            # Receive echo
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Echo: {data}")
            
            print("Minimal server test PASSED!")
            
    except Exception as e:
        print(f"Minimal server test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_minimal_server())