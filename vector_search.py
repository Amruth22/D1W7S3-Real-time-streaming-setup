import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict
import config

class VectorSearch:
    def __init__(self):
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.index = None
        self.documents = []
        self.index_path = config.FAISS_INDEX_PATH
        self.documents_path = os.path.join(self.index_path, "documents.json")
        
        # Create directories
        os.makedirs(self.index_path, exist_ok=True)
        
        # Load or create index
        self.load_index()
    
    def load_index(self):
        """Load existing FAISS index and documents"""
        index_file = os.path.join(self.index_path, "faiss.index")
        
        if os.path.exists(index_file) and os.path.exists(self.documents_path):
            try:
                self.index = faiss.read_index(index_file)
                with open(self.documents_path, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                print(f"Loaded index with {len(self.documents)} documents")
            except Exception as e:
                print(f"Error loading index: {e}")
                self.create_index()
        else:
            self.create_index()
    
    def create_index(self):
        """Create new FAISS index"""
        self.index = faiss.IndexFlatIP(config.EMBEDDING_DIMENSION)
        self.documents = []
        print("Created new FAISS index")
    
    def save_index(self):
        """Save FAISS index and documents"""
        try:
            index_file = os.path.join(self.index_path, "faiss.index")
            faiss.write_index(self.index, index_file)
            
            with open(self.documents_path, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            
            print(f"Saved index with {len(self.documents)} documents")
        except Exception as e:
            print(f"Error saving index: {e}")
    
    async def add_document(self, filename: str, chunks: List[str], websocket) -> None:
        """Add document chunks to vector index with progress updates"""
        try:
            # Send embedding start
            await websocket.send(json.dumps({
                "type": "embedding_status",
                "status": "Creating embeddings",
                "progress": 0
            }))
            
            # Create embeddings for chunks
            embeddings = []
            for i, chunk in enumerate(chunks):
                embedding = self.model.encode([chunk])[0]
                embeddings.append(embedding)
                
                # Update progress
                progress = (i + 1) / len(chunks) * 80
                await websocket.send(json.dumps({
                    "type": "embedding_status",
                    "status": f"Processing chunk {i + 1}/{len(chunks)}",
                    "progress": int(progress)
                }))
            
            # Normalize embeddings for cosine similarity
            embeddings_array = np.array(embeddings, dtype=np.float32)
            faiss.normalize_L2(embeddings_array)
            
            # Add to FAISS index
            self.index.add(embeddings_array)
            
            # Store document metadata
            for i, chunk in enumerate(chunks):
                self.documents.append({
                    'filename': filename,
                    'chunk_id': i,
                    'text': chunk
                })
            
            # Save index
            self.save_index()
            
            await websocket.send(json.dumps({
                "type": "embedding_complete",
                "status": "Document indexed successfully",
                "progress": 100,
                "chunks_added": len(chunks)
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Error creating embeddings: {str(e)}"
            }))
    
    async def search(self, query: str, websocket, k: int = None) -> List[Tuple[str, float, Dict]]:
        """Search for similar documents with real-time updates"""
        if k is None:
            k = config.MAX_SEARCH_RESULTS
            
        if self.index is None or len(self.documents) == 0:
            await websocket.send(json.dumps({
                "type": "search_results",
                "results": [],
                "message": "No documents indexed yet"
            }))
            return []
        
        try:
            # Send search start
            await websocket.send(json.dumps({
                "type": "search_status",
                "status": "Searching documents",
                "query": query
            }))
            
            # Create query embedding
            query_embedding = self.model.encode([query])[0]
            query_array = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_array)
            
            # Search
            scores, indices = self.index.search(query_array, min(k, len(self.documents)))
            
            # Prepare results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.documents) and score >= config.SIMILARITY_THRESHOLD:
                    doc = self.documents[idx]
                    results.append((doc['text'], float(score), {
                        'filename': doc['filename'],
                        'chunk_id': doc['chunk_id']
                    }))
            
            # Send results
            await websocket.send(json.dumps({
                "type": "search_results",
                "results": [
                    {
                        "text": text,
                        "score": score,
                        "metadata": metadata
                    }
                    for text, score, metadata in results
                ],
                "query": query,
                "total_found": len(results)
            }))
            
            return results
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Search error: {str(e)}"
            }))
            return []
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        return {
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal if self.index else 0,
            'embedding_model': config.EMBEDDING_MODEL
        }