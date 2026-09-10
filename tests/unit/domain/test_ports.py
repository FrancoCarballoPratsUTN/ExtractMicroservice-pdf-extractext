"""Tests for the abstract ports of the domain layer."""

import pytest

from app.domain.ports.payload_decoder import PayloadDecoder
from app.domain.ports.pdf_extractor import PdfExtractor


class TestPdfExtractorPort:
    def test_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            PdfExtractor()


class TestPayloadDecoderPort:
    def test_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            PayloadDecoder()
