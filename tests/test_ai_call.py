from unittest.mock import patch, Mock
import pytest
from app.utils import generate_ai_summary

@pytest.fixture
def mock_grok_response():
    return {
        "choices": [{"message": {"content": "Test summary text here."}}],
        "usage": {"prompt_tokens": 500, "completion_tokens": 100}
    }

@patch('app.utils.requests.post')
def test_generate_ai_summary_success(mock_post, mock_grok_response):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_grok_response
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    # Pass non-empty logs to trigger API call
    sample_logs = [{'raw_message': 'test log'}]  # minimal non-empty
    result = generate_ai_summary(sample_logs, use_normalizer=False)

    assert result['summary'] == "Test summary text here."
    assert result['input_tokens'] == 500
    assert result['output_tokens'] == 100
    assert result['cost_est'] == (500 / 1_000_000 * 0.20) + (100 / 1_000_000 * 0.50)

@patch('app.utils.requests.post')
def test_generate_ai_summary_empty_input(mock_post):
    result = generate_ai_summary([], use_normalizer=True)
    assert result['summary'] == 'No recent threats.'
    assert result['input_tokens'] == 0
    assert result['output_tokens'] == 0
    assert result['cost_est'] == 0.0
    mock_post.assert_not_called()  # no API call on empty