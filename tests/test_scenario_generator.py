import pytest
from unittest.mock import MagicMock, patch


def _make_mock_client(json_text: str):
    """Helper: returns a mock Anthropic client that returns json_text."""
    mock_content = MagicMock()
    mock_content.text = json_text
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


def test_generate_scenario_returns_scenario_and_prompt():
    json_response = '{"scenario": "The couple is skydiving over the Grand Canyon.", "image_prompt": "A couple skydiving at sunset, wide angle shot."}'
    mock_client = _make_mock_client(json_response)

    with patch("scenario_generator.Anthropic", return_value=mock_client):
        from scenario_generator import generate_scenario
        result = generate_scenario(api_key="fake-key")

    assert "scenario" in result
    assert "image_prompt" in result
    assert isinstance(result["scenario"], str)
    assert isinstance(result["image_prompt"], str)


def test_generate_scenario_raises_on_invalid_json():
    mock_client = _make_mock_client("not valid json")

    with patch("scenario_generator.Anthropic", return_value=mock_client):
        from scenario_generator import generate_scenario
        with pytest.raises(ValueError, match="Failed to parse"):
            generate_scenario(api_key="fake-key")


def test_generate_scenario_raises_on_missing_fields():
    mock_client = _make_mock_client('{"scenario": "something"}')

    with patch("scenario_generator.Anthropic", return_value=mock_client):
        from scenario_generator import generate_scenario
        with pytest.raises(ValueError, match="image_prompt"):
            generate_scenario(api_key="fake-key")
