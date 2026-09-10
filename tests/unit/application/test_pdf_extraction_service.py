"""Unit tests for the PDF extraction application service."""

import pytest

from app.application.services.pdf_extraction_service import PdfExtractionService
from app.domain.entities.extracted_document import ExtractedDocument, ExtractedPage
from app.domain.exceptions import (
    EncryptedPdfError,
    FileTooLargeError,
    InvalidBase64Error,
    NoExtractableTextError,
)
from app.domain.ports.payload_decoder import PayloadDecoder
from app.domain.ports.pdf_extractor import PdfExtractor


def _document(*texts: str) -> ExtractedDocument:
    pages = tuple(
        ExtractedPage(index, text) for index, text in enumerate(texts, start=1)
    )
    return ExtractedDocument(pages)


class FakeDecoder(PayloadDecoder):
    def __init__(self, output: bytes, error: Exception | None = None) -> None:
        self._output = output
        self._error = error
        self.received: list[str] = []

    def decode(self, payload: str) -> bytes:
        self.received.append(payload)
        if self._error:
            raise self._error
        return self._output


class FakeExtractor(PdfExtractor):
    def __init__(
        self, output: ExtractedDocument, error: Exception | None = None
    ) -> None:
        self._output = output
        self._error = error
        self.received: list[bytes] = []

    def extract(self, data: bytes) -> ExtractedDocument:
        self.received.append(data)
        if self._error:
            raise self._error
        return self._output


class TestPdfExtractionService:
    def test_extracts_document_when_payload_is_within_limit(self):
        service = PdfExtractionService(
            FakeDecoder(b"pdf-data"), FakeExtractor(_document("text"))
        )

        result = service.extract("b64-payload", max_size_bytes=100)

        assert result.total_pages == 1
        assert result.pages[0].text == "text"

    def test_feeds_extractor_with_the_decoded_bytes(self):
        decoder = FakeDecoder(b"decoded-bytes")
        extractor = FakeExtractor(_document("text"))
        service = PdfExtractionService(decoder, extractor)

        service.extract("b64-payload", max_size_bytes=100)

        assert extractor.received == [b"decoded-bytes"]

    def test_allows_decoded_size_equal_to_the_cap(self):
        service = PdfExtractionService(
            FakeDecoder(b"x" * 10), FakeExtractor(_document("text"))
        )

        assert service.extract("b64", max_size_bytes=10).total_pages == 1

    def test_raises_file_too_large_when_decoded_size_exceeds_the_cap(self):
        service = PdfExtractionService(
            FakeDecoder(b"x" * 11), FakeExtractor(_document("text"))
        )

        with pytest.raises(FileTooLargeError):
            service.extract("b64", max_size_bytes=10)

    def test_raises_file_too_large_before_calling_the_extractor(self):
        extractor = FakeExtractor(_document("text"))
        service = PdfExtractionService(FakeDecoder(b"x" * 101), extractor)

        with pytest.raises(FileTooLargeError):
            service.extract("b64", max_size_bytes=100)

        assert extractor.received == []

    def test_raises_no_extractable_text_when_every_page_is_empty(self):
        service = PdfExtractionService(
            FakeDecoder(b"data"), FakeExtractor(_document("", ""))
        )

        with pytest.raises(NoExtractableTextError):
            service.extract("b64", max_size_bytes=100)

    def test_accepts_document_with_some_non_empty_pages(self):
        service = PdfExtractionService(
            FakeDecoder(b"data"), FakeExtractor(_document("", "hi"))
        )

        result = service.extract("b64", max_size_bytes=100)

        assert result.total_pages == 2

    def test_propagates_decoder_errors_unchanged(self):
        service = PdfExtractionService(
            FakeDecoder(b"", error=InvalidBase64Error("bad")),
            FakeExtractor(_document("text")),
        )

        with pytest.raises(InvalidBase64Error):
            service.extract("b64", max_size_bytes=100)

    def test_propagates_extractor_errors_unchanged(self):
        service = PdfExtractionService(
            FakeDecoder(b"data"),
            FakeExtractor(_document("text"), error=EncryptedPdfError("encrypted")),
        )

        with pytest.raises(EncryptedPdfError):
            service.extract("b64", max_size_bytes=100)
