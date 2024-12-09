import pytest
from unittest.mock import patch, Mock
from config.gpt_client import GPTClient

@pytest.fixture(autouse=True)
def mock_openai():
    # Crear un mock para la respuesta de OpenAI
    mock_response = Mock()
    mock_choice = Mock()
    mock_choice.message.content = "Mocked response"
    mock_response.choices = [mock_choice]
    
    # Parchear todas las llamadas a OpenAI
    with patch('openai.api_key', 'fake_key'), \
         patch('openai.chat.completions.create', return_value=mock_response), \
         patch('config.config.Config.validate_config'), \
         patch('config.config.Config.get_api_key', return_value='fake_key'):
        yield mock_response

@pytest.fixture
def gpt_client(mock_openai):
    return GPTClient()

def test_cached_response(gpt_client):
    messages = [
        {"role": "system", "content": "You are a financial advisor."},
        {"role": "user", "content": "What is ROI?"}
    ]
    
    # Primera llamada
    first_response = gpt_client._make_request(messages)
    assert isinstance(first_response, str)
    
    # Segunda llamada (debería venir del caché)
    second_response = gpt_client._make_request(messages)
    assert second_response == first_response

def test_different_prompts(gpt_client):
    # Dos prompts diferentes
    response1 = gpt_client._make_request([
        {"role": "user", "content": "What is ROI?"}
    ])
    
    response2 = gpt_client._make_request([
        {"role": "user", "content": "What is ROE?"}
    ])
    
    assert isinstance(response1, str)
    assert isinstance(response2, str)