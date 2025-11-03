import pytest
from app.config import get_settings


def test_settings_load():
    """Test that settings can be loaded."""
    settings = get_settings()
    assert settings is not None
    assert hasattr(settings, 'github_app_id')
    assert hasattr(settings, 'anthropic_api_key')


def test_review_command_default():
    """Test default review command."""
    settings = get_settings()
    assert settings.review_command == "/review"


def test_auto_review_default():
    """Test auto review is enabled by default."""
    settings = get_settings()
    assert settings.auto_review_enabled is True
