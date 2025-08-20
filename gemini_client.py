import json
import asyncio
from google import genai
from google.genai import types
import config

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    async def stream_response(self, question: str, context: str, websocket) -> None:
        """Stream AI response from Gemini with context"""
        try:
            # Send AI start
            await websocket.send(json.dumps({
                "type": "ai_status",
                "status": "Getting AI response",
                "question": question
            }))
            
            # Prepare prompt with context
            if context:
                prompt = f"""You are a helpful document assistant. Answer the user's question based on the provided context from their documents.

Context from documents:
{context}

User Question: {question}

Please provide a clear and helpful answer based on the context provided:"""
            else:
                prompt = f"""You are a helpful document assistant. The user asked: {question}

Please provide a helpful response:"""
            
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ]
            
            # Stream response
            response_parts = []
            for chunk in self.client.models.generate_content_stream(
                model=config.GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig()
            ):
                if chunk.text:
                    response_parts.append(chunk.text)
                    
                    # Send chunk to client
                    await websocket.send(json.dumps({
                        "type": "ai_chunk",
                        "content": chunk.text
                    }))
                    
                    # Small delay for streaming effect
                    await asyncio.sleep(0.05)
            
            # Send completion
            complete_response = "".join(response_parts)
            await websocket.send(json.dumps({
                "type": "ai_complete",
                "response": complete_response,
                "question": question,
                "context_used": bool(context)
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"AI response error: {str(e)}"
            }))
    
    async def simple_response(self, question: str, context: str = "") -> str:
        """Get simple non-streaming response"""
        try:
            if context:
                prompt = f"""Based on this context: {context}

Question: {question}

Answer:"""
            else:
                prompt = question
            
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ]
            
            response = self.client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=contents
            )
            
            return response.text
            
        except Exception as e:
            return f"Error: {str(e)}"