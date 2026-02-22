# tests/test_config.py
import os
import pytest
from unittest.mock import patch


def test_load_config_returns_both_keys():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-ant", "FAL_KEY": "test-fal"}):
        from config import load_config
        cfg = load_config()
        assert cfg["anthropic_api_key"] == "test-ant"
        assert "fal_key" not in cfg


def test_load_config_raises_if_anthropic_key_missing():
    env = {"FAL_KEY": "test-fal"}
    with patch.dict(os.environ, env, clear=True):
        from config import load_config
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            load_config()


def test_load_config_raises_if_fal_key_missing():
    env = {"ANTHROPIC_API_KEY": "test-ant"}
    with patch.dict(os.environ, env, clear=True):
        from config import load_config
        with pytest.raises(ValueError, match="FAL_KEY"):
            load_config()
