"""Tests for the in-memory PDF fixture builders."""

import base64
from io import BytesIO

from pypdf import PdfReader

from tests.fixtures.pdf_factory import build_pdf_bytes, pdf_to_base64


class TestBuildPdfBytes:
    def test_builds_pdf_with_expected_page_count(self):
        data = build_pdf_bytes(["First page", "Second page"])
        reader = PdfReader(BytesIO(data))

        assert len(reader.pages) == 2

    def test_first_page_contains_expected_text(self):
        data = build_pdf_bytes(["Hello Big Pickle", "Second page"])
        reader = PdfReader(BytesIO(data))

        assert reader.pages[0].extract_text().strip() == "Hello Big Pickle"

    def test_last_page_contains_expected_text(self):
        data = build_pdf_bytes(["First page", "Bye Big Pickle"])
        reader = PdfReader(BytesIO(data))

        assert reader.pages[1].extract_text().strip() == "Bye Big Pickle"

    def test_returns_raw_in_memory_bytes(self):
        data = build_pdf_bytes(["Solo pag"])

        assert isinstance(data, bytes)
        assert data.startswith(b"%PDF")


class TestPdfToBase64:
    def test_roundtrips_back_to_original_bytes(self):
        data = build_pdf_bytes(["Round trip"])

        assert base64.b64decode(pdf_to_base64(data)) == data
