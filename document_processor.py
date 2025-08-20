import os
import fitz  # PyMuPDF
import asyncio
from typing import List, Dict, AsyncGenerator
import config

class DocumentProcessor:
    def __init__(self):
        self.upload_dir = config.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def process_file(self, file_path: str, websocket) -> AsyncGenerator[Dict, None]:
        """Process uploaded file and yield progress updates"""
        try:
            # Send processing start
            yield {
                "type": "processing_status",
                "status": "Starting document processing",
                "progress": 0
            }
            
            # Extract text based on file type
            if file_path.endswith('.pdf'):
                async for update in self._process_pdf(file_path, websocket):
                    yield update
            elif file_path.endswith('.txt'):
                async for update in self._process_text(file_path, websocket):
                    yield update
            else:
                yield {
                    "type": "error",
                    "message": "Unsupported file type"
                }
                return
            
        except Exception as e:
            yield {
                "type": "error",
                "message": f"Error processing file: {str(e)}"
            }
    
    async def _process_pdf(self, file_path: str, websocket) -> AsyncGenerator[Dict, None]:
        """Process PDF file using PyMuPDF"""
        try:
            # Open PDF
            yield {
                "type": "processing_status",
                "status": "Opening PDF file",
                "progress": 10
            }
            
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            yield {
                "type": "processing_status",
                "status": f"Found {total_pages} pages",
                "progress": 20
            }
            
            # Extract text from all pages
            full_text = ""
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                text = page.get_text()
                full_text += text + "\n"
                
                # Update progress
                progress = 20 + (page_num + 1) / total_pages * 50
                yield {
                    "type": "processing_status",
                    "status": f"Extracting text from page {page_num + 1}/{total_pages}",
                    "progress": int(progress)
                }
                
                # Small delay to show progress
                await asyncio.sleep(0.1)
            
            doc.close()
            
            yield {
                "type": "processing_status",
                "status": "Text extraction completed",
                "progress": 70
            }
            
            # Chunk the text
            chunks = self._chunk_text(full_text)
            
            yield {
                "type": "processing_status",
                "status": f"Created {len(chunks)} text chunks",
                "progress": 80
            }
            
            yield {
                "type": "processing_complete",
                "text": full_text,
                "chunks": chunks,
                "progress": 100
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "message": f"Error processing PDF: {str(e)}"
            }
    
    async def _process_text(self, file_path: str, websocket) -> AsyncGenerator[Dict, None]:
        """Process text file"""
        try:
            yield {
                "type": "processing_status",
                "status": "Reading text file",
                "progress": 30
            }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
            
            yield {
                "type": "processing_status",
                "status": "Text file loaded",
                "progress": 60
            }
            
            # Chunk the text
            chunks = self._chunk_text(full_text)
            
            yield {
                "type": "processing_status",
                "status": f"Created {len(chunks)} text chunks",
                "progress": 80
            }
            
            yield {
                "type": "processing_complete",
                "text": full_text,
                "chunks": chunks,
                "progress": 100
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "message": f"Error processing text file: {str(e)}"
            }
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks for better search"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), config.CHUNK_SIZE - config.CHUNK_OVERLAP):
            chunk_words = words[i:i + config.CHUNK_SIZE]
            chunk = " ".join(chunk_words)
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks
    
    def save_uploaded_file(self, filename: str, file_data: bytes) -> str:
        """Save uploaded file and return path"""
        file_path = os.path.join(self.upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        return file_path