#!/usr/bin/env python3
"""
Test client for working WebSocket server
"""

import asyncio
import websockets
import json
import base64

async def test_working_server():
    """Test the working server"""
    try:
        print("Connecting to working server...")
        
        async with websockets.connect("ws://localhost:8080") as websocket:
            print("Connected!")
            
            # Test 1: Receive welcome message
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            print(f"Welcome: {data}")
            assert data['type'] == 'connection_status'
            
            # Test 2: Test connection
            await websocket.send(json.dumps({"type": "test_connection"}))
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            print(f"Test response: {data}")
            assert data['type'] == 'test_response'
            
            # Test 3: Get stats
            await websocket.send(json.dumps({"type": "get_stats"}))
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            print(f"Stats: {data}")
            assert data['type'] == 'stats'
            
            # Test 4: Upload a small text file
            test_content = "This is a test document for the working server."
            file_data = base64.b64encode(test_content.encode()).decode()
            
            await websocket.send(json.dumps({
                "type": "file_upload",
                "filename": "test_working.txt",
                "file_data": file_data
            }))
            
            # Collect upload responses
            upload_responses = []
            for _ in range(10):  # Max 10 responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    data = json.loads(response)
                    upload_responses.append(data)
                    print(f"Upload response: {data['type']}")
                    
                    if data['type'] == 'embedding_complete':
                        break
                except asyncio.TimeoutError:
                    break
            
            print(f"Upload completed with {len(upload_responses)} responses")
            
            # Test 5: Search
            await websocket.send(json.dumps({
                "type": "search_query",
                "query": "test document"
            }))
            
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            print(f"Search results: {data}")
            
            # Test 6: Ask question (optional - might fail if Gemini API issues)
            await websocket.send(json.dumps({
                "type": "ask_question",
                "question": "What is this document about?"
            }))
            
            # Collect AI responses
            ai_responses = []
            for _ in range(10):  # Max 10 responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=15)
                    data = json.loads(response)
                    ai_responses.append(data)
                    print(f"AI response: {data['type']}")
                    
                    if data['type'] in ['ai_complete', 'error']:
                        break
                except asyncio.TimeoutError:
                    print("AI response timeout (this is OK)")
                    break
            
            print(f"AI completed with {len(ai_responses)} responses")
            
            print("Working server test PASSED!")
            return True
            
    except Exception as e:
        print(f"Working server test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_working_server())
    exit(0 if success else 1)