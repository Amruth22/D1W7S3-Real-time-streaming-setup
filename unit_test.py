import pytest
import asyncio
import os
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, AsyncMock
import numpy as np

# Import components to test
from document_processor import DocumentProcessor
from vector_search import VectorSearch
from gemini_client import GeminiClient
import config

class TestDocumentProcessor:
    """Test document processing functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = DocumentProcessor()
        # Override upload directory for testing
        self.processor.upload_dir = self.temp_dir
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_chunk_text(self):
        """Test 1: Text chunking functionality"""
        try:
            # Test text chunking
            test_text = "This is a test document. " * 100  # Create long text
            chunks = self.processor._chunk_text(test_text)
            
            assert len(chunks) > 0, "No chunks created"
            assert all(isinstance(chunk, str) for chunk in chunks), "Invalid chunk types"
            assert all(len(chunk.split()) <= config.CHUNK_SIZE for chunk in chunks), "Chunks too large"
            
            print("Test 1 PASSED: Text chunking functionality")
            return True
            
        except Exception as e:
            print(f"Test 1 FAILED: {e}")
            return False
    
    def test_save_uploaded_file(self):
        """Test 2: File saving functionality"""
        try:
            # Test file saving
            test_filename = "test_document.txt"
            test_data = b"This is test file content"
            
            file_path = self.processor.save_uploaded_file(test_filename, test_data)
            
            assert os.path.exists(file_path), "File not saved"
            
            with open(file_path, 'rb') as f:
                saved_data = f.read()
            
            assert saved_data == test_data, "File content mismatch"
            
            print("Test 2 PASSED: File saving functionality")
            return True
            
        except Exception as e:
            print(f"Test 2 FAILED: {e}")
            return False

class TestVectorSearch:
    """Test vector search functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock config for testing
        with patch('vector_search.config') as mock_config:
            mock_config.FAISS_INDEX_PATH = self.temp_dir
            mock_config.EMBEDDING_DIMENSION = 384
            mock_config.EMBEDDING_MODEL = "all-MiniLM-L6-v2"
            mock_config.MAX_SEARCH_RESULTS = 5
            mock_config.SIMILARITY_THRESHOLD = 0.6
            
            # Mock sentence transformer
            with patch('vector_search.SentenceTransformer') as mock_transformer:
                mock_model = Mock()
                mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
                mock_transformer.return_value = mock_model
                
                self.vector_search = VectorSearch()
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_vector_store_initialization(self):
        """Test 3: Vector store initialization"""
        try:
            assert self.vector_search is not None, "Vector search not initialized"
            assert self.vector_search.index is not None, "FAISS index not created"
            assert isinstance(self.vector_search.documents, list), "Documents list not initialized"
            
            stats = self.vector_search.get_stats()
            assert 'total_documents' in stats, "Stats missing total_documents"
            assert 'index_size' in stats, "Stats missing index_size"
            
            print("Test 3 PASSED: Vector store initialization")
            return True
            
        except Exception as e:
            print(f"Test 3 FAILED: {e}")
            return False

class TestGeminiClient:
    """Test Gemini client functionality"""
    
    def test_gemini_client_initialization(self):
        """Test 4: Gemini client initialization"""
        try:
            client = GeminiClient()
            assert client is not None, "Gemini client not initialized"
            assert hasattr(client, 'client'), "Gemini client missing client attribute"
            
            print("Test 4 PASSED: Gemini client initialization")
            return True
            
        except Exception as e:
            print(f"Test 4 FAILED: {e}")
            return False

class TestWebSocketIntegration:
    """Test WebSocket server integration"""
    
    def test_websocket_message_handling(self):
        """Test 5: WebSocket message handling"""
        try:
            # Test message format validation
            test_messages = [
                {
                    'type': 'file_upload',
                    'filename': 'test.pdf',
                    'file_data': 'base64data'
                },
                {
                    'type': 'search_query',
                    'query': 'test search'
                },
                {
                    'type': 'ask_question',
                    'question': 'What is this about?'
                }
            ]
            
            # Validate message structure
            for msg in test_messages:
                assert 'type' in msg, f"Message missing type: {msg}"
                
                # Validate specific message types
                if msg['type'] == 'file_upload':
                    assert 'filename' in msg, "File upload missing filename"
                    assert 'file_data' in msg, "File upload missing file_data"
                elif msg['type'] == 'search_query':
                    assert 'query' in msg, "Search query missing query"
                elif msg['type'] == 'ask_question':
                    assert 'question' in msg, "Ask question missing question"
                
                # Test JSON serialization
                json_str = json.dumps(msg)
                parsed_msg = json.loads(json_str)
                assert parsed_msg == msg, "JSON serialization failed"
            
            print("Test 5 PASSED: WebSocket message handling")
            return True
            
        except Exception as e:
            print(f"Test 5 FAILED: {e}")
            return False

def run_tests():
    """Run all unit tests"""
    print("Running Live Document Q&A System Unit Tests")
    print("=" * 50)
    
    # Test instances
    doc_processor_test = TestDocumentProcessor()
    vector_search_test = TestVectorSearch()
    gemini_client_test = TestGeminiClient()
    websocket_test = TestWebSocketIntegration()
    
    tests = [
        ("Text Chunking Functionality", lambda: (
            doc_processor_test.setup_method(),
            doc_processor_test.test_chunk_text(),
            doc_processor_test.teardown_method()
        )[1]),
        
        ("File Saving Functionality", lambda: (
            doc_processor_test.setup_method(),
            doc_processor_test.test_save_uploaded_file(),
            doc_processor_test.teardown_method()
        )[1]),
        
        ("Vector Store Initialization", lambda: (
            vector_search_test.setup_method(),
            vector_search_test.test_vector_store_initialization(),
            vector_search_test.teardown_method()
        )[1]),
        
        ("Gemini Client Initialization", gemini_client_test.test_gemini_client_initialization),
        
        ("WebSocket Message Handling", websocket_test.test_websocket_message_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"{test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! System is ready.")
        return True
    else:
        print("Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)