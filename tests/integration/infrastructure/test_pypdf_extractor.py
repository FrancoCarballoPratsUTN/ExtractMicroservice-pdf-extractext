"""Integration tests for the pypdf extractor adapter."""

import pytest

from app.domain.exceptions import EncryptedPdfError, PdfCorruptedError
from app.domain.ports.pdf_extractor import PdfExtractor
from app.infrastructure.pdf.pypdf_extractor import PypdfExtractor
from tests.fixtures.pdf_factory import build_encrypted_pdf_bytes, build_pdf_bytes


class TestPypdfExtractor:
    def test_implements_the_pdf_extractor_port(self):
        assert isinstance(PypdfExtractor(), PdfExtractor)

    def test_extracts_text_from_every_page(self):
        extractor = PypdfExtractor()

        document = extractor.extract(build_pdf_bytes(["Alpha page", "Beta page"]))

        assert document.total_pages == 2
        assert document.pages[0].text.strip() == "Alpha page"
        assert document.pages[1].text.strip() == "Beta page"

    def test_reports_total_characters_across_pages(self):
        extractor = PypdfExtractor()

        document = extractor.extract(build_pdf_bytes(["ab", "cde"]))

        assert document.total_characters == 5

    def test_raises_encrypted_pdf_error_for_encrypted_pdf(self):
        extractor = PypdfExtractor()

        with pytest.raises(EncryptedPdfError):
            extractor.extract(build_encrypted_pdf_bytes(["Secret"]))

    def test_raises_pdf_corrupted_error_for_garbage_bytes(self):
        extractor = PypdfExtractor()

        with pytest.raises(PdfCorruptedError):
            extractor.extract(b"this is definitely not a pdf")

    def test_raises_pdf_corrupted_error_for_empty_bytes(self):
        extractor = PypdfExtractor()

        with pytest.raises(PdfCorruptedError):
            extractor.extract(b"")
