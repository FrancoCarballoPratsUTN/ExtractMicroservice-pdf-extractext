"""Tests for the application settings read from the environment."""

from app.config import Settings, get_settings


def test_default_max_size_is_ten_megabytes():
    get_settings.cache_clear()

    try:
        assert get_settings().max_size_bytes == 10 * 1024 * 1024
    finally:
        get_settings.cache_clear()


def test_reads_max_size_from_environment_variable(monkeypatch):
    monkeypatch.setenv("MAX_SIZE_BYTES", "2048")
    get_settings.cache_clear()

    try:
        assert get_settings().max_size_bytes == 2048
    finally:
        get_settings.cache_clear()


def test_exposes_typed_settings_object():
    get_settings.cache_clear()

    try:
        assert isinstance(get_settings(), Settings)
    finally:
        get_settings.cache_clear()
