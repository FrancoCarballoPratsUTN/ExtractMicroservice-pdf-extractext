"""Tests for the application settings read from the environment."""

import pytest

from app.config import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_default_max_size_is_ten_megabytes():
    assert get_settings().max_size_bytes == 10 * 1024 * 1024


def test_reads_max_size_from_environment_variable(monkeypatch):
    monkeypatch.setenv("MAX_SIZE_BYTES", "2048")

    assert get_settings().max_size_bytes == 2048


def test_exposes_typed_settings_object():
    assert isinstance(get_settings(), Settings)


def test_default_app_metadata():
    settings = get_settings()
    assert settings.app_name == "Big Pickle"
    assert settings.version == "0.1.0"


def test_reads_app_metadata_from_environment(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Other Service")
    monkeypatch.setenv("VERSION", "9.9.9")

    settings = get_settings()
    assert settings.app_name == "Other Service"
    assert settings.version == "9.9.9"
