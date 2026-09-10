"""Shared pytest fixtures for the test suite."""

import pytest

from tests.fixtures.pdf_factory import build_pdf_bytes, pdf_to_base64


@pytest.fixture
def pdf_bytes() -> bytes:
    """Return the bytes of a minimal single-page PDF."""
    return build_pdf_bytes(["Hello Big Pickle"])


@pytest.fixture
def base64_pdf(pdf_bytes: bytes) -> str:
    """Return a Base64-encoded single-page PDF."""
    return pdf_to_base64(pdf_bytes)
