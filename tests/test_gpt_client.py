# test_gpt_client.py
import pytest
from unittest.mock import Mock, patch
from config.gpt_client import GPTClient
from config.config import Config

@pytest.fixture
def mock_openai():
    with patch('openai.chat.completions.create') as mock_create:
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Mocked response"))]
        mock_create.return_value = mock_response
        yield mock_create

@pytest.fixture
def gpt_client():
    # Configurar una API key de prueba
    Config.OPENAI_API_KEY = 'test_key'
    with patch('openai.chat.completions.create'):  # Mock todas las llamadas a OpenAI
        return GPTClient()

def test_process_pdf(gpt_client, mock_openai):
    test_pdf_path = "test.pdf"
    with open(test_pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\ntest content")
    
    try:
        result = gpt_client.process_pdf(test_pdf_path)
        assert isinstance(result, str)
        assert len(result) > 0
    finally:
        import os
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)

def test_generate_scenarios(gpt_client, mock_openai):
    result = gpt_client.generate_scenarios(
        "Test data",
        {"sector": "Test", "region": "Test"}
    )
    assert isinstance(result, str)
    assert len(result) > 0

def test_generate_financial_opinion(gpt_client, mock_openai):
    result = gpt_client.generate_financial_opinion(
        "Test data",
        {"sector": "Test", "region": "Test"}
    )
    assert isinstance(result, str)
    assert len(result) > 0