import pytest
from unittest.mock import mock_open, patch, MagicMock
from bs4 import BeautifulSoup
import eml_parser
import os
import sys
import re

# Add the directory containing the module to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Mock dependencies before importing
with patch('langchain.embeddings.HuggingFaceEmbeddings') as mock_embeddings, \
     patch('langchain.llms.Ollama') as mock_ollama, \
     patch('re.search') as mock_re_search, \
     patch('json.loads') as mock_json_loads, \
     patch('sentence_transformers.SentenceTransformer') as mock_transformer:
    
    # Configure mock embeddings
    mock_embeddings_instance = MagicMock()
    mock_embeddings.return_value = mock_embeddings_instance
    
    # Configure mock LLM responses with correct keys
    mock_llm_response = MagicMock()
    mock_llm_response.content = '{"request_type": "test", "sub_request_type": "test"}'
    mock_ollama.return_value.generate.return_value = mock_llm_response
    
    # Configure mock JSON parsing with correct keys
    mock_re_search.return_value.group.return_value = '{"request_type": "test", "sub_request_type": "test"}'
    mock_json_loads.return_value = {
        "request_type": "test", 
        "sub_request_type": "test"
    }
    
    # Mock transformer
    mock_transformer_instance = MagicMock()
    mock_transformer.return_value = mock_transformer_instance
    mock_transformer_instance.encode.return_value = [[1.0] * 768]  # Mock embedding vector
    
    from emailclassification_surendra import extract_text_from_pdf, extract_text_from_eml

@pytest.fixture(autouse=True)
def mock_dependencies():
    """Mock all external dependencies for tests"""
    with patch('langchain.embeddings.HuggingFaceEmbeddings') as mock_embeddings, \
         patch('langchain.llms.Ollama') as mock_ollama, \
         patch('re.search') as mock_re_search, \
         patch('json.loads') as mock_json_loads, \
         patch('sentence_transformers.SentenceTransformer') as mock_transformer:
        
        # Configure mocks with correct keys
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_llm_response = MagicMock()
        mock_llm_response.content = '{"request_type": "test", "sub_request_type": "test"}'
        mock_ollama.return_value.generate.return_value = mock_llm_response
        
        mock_re_search.return_value.group.return_value = '{"request_type": "test", "sub_request_type": "test"}'
        mock_json_loads.return_value = {
            "request_type": "test", 
            "sub_request_type": "test"
        }
        
        # Mock transformer
        mock_transformer_instance = MagicMock()
        mock_transformer.return_value = mock_transformer_instance
        mock_transformer_instance.encode.return_value = [[1.0] * 768]  # Mock embedding vector
        
        yield

# Test cases for PDF extraction
def test_extract_text_from_pdf():
    # Mock PyPDFLoader and its behavior
    mock_document = MagicMock()
    mock_document.page_content = "Test PDF content page 1\n"
    
    with patch('emailClassification_surendra.PyPDFLoader') as mock_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = [mock_document]
        mock_loader.return_value = mock_loader_instance
        
        # Test with single PDF
        result = extract_text_from_pdf(['test.pdf'])
        assert result == "Test PDF content page 1\n"
        mock_loader.assert_called_once_with('test.pdf')

def test_extract_text_from_pdf_multiple_files():
    # Mock PyPDFLoader for multiple files
    mock_document1 = MagicMock()
    mock_document1.page_content = "PDF 1 content\n"
    mock_document2 = MagicMock()
    mock_document2.page_content = "PDF 2 content\n"
    
    with patch('emailClassification_surendra.PyPDFLoader') as mock_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.side_effect = [[mock_document1], [mock_document2]]
        mock_loader.return_value = mock_loader_instance
        
        result = extract_text_from_pdf(['test1.pdf', 'test2.pdf'])
        assert result == "PDF 1 content\nPDF 2 content\n"
        assert mock_loader.call_count == 2

# Test cases for EML extraction
def test_extract_text_from_eml_plain():
    mock_eml_content = b"Test email content"
    mock_parsed_eml = {'body': ['Plain text email content']}
    
    with patch('builtins.open', mock_open(read_data=mock_eml_content)):
        with patch('eml_parser.eml_parser.decode_email_b', return_value=mock_parsed_eml):
            result = extract_text_from_eml('test.eml')
            assert result == 'Plain text email content'

def test_extract_text_from_eml_html():
    mock_eml_content = b"Test email content"
    mock_parsed_eml = {
        'body': [''],
        'html': ['<html><body><p>HTML email content</p></body></html>']
    }
    
    with patch('builtins.open', mock_open(read_data=mock_eml_content)):
        with patch('eml_parser.eml_parser.decode_email_b', return_value=mock_parsed_eml):
            result = extract_text_from_eml('test.eml')
            assert result.strip() == 'HTML email content'

def test_extract_text_from_eml_empty():
    mock_eml_content = b""
    mock_parsed_eml = {'body': ['']}
    
    with patch('builtins.open', mock_open(read_data=mock_eml_content)):
        with patch('eml_parser.eml_parser.decode_email_b', return_value=mock_parsed_eml):
            result = extract_text_from_eml('test.eml')
            assert result == ''