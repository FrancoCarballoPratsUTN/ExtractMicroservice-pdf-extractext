"""Unit tests for the API DTOs."""

import pytest
from pydantic import ValidationError

from app.api.dto.errors import from_domain_error
from app.api.dto.requests import ExtractRequest
from app.api.dto.responses import ExtractResult
from app.config import get_settings
from app.domain.entities.extracted_document import ExtractedDocument, ExtractedPage
from app.domain.exceptions import EncryptedPdfError


class TestExtractRequest:
    def test_accepts_a_valid_payload(self):
        request = ExtractRequest(file_base64="JVBERi0=", max_size_bytes=2048)

        assert request.file_base64 == "JVBERi0="
        assert request.max_size_bytes == 2048

    def test_defaults_max_size_to_ten_megabytes(self):
        request = ExtractRequest(file_base64="abc=")

        assert request.max_size_bytes == 10 * 1024 * 1024

    def test_defaults_max_size_to_the_configured_limit(self, monkeypatch):
        monkeypatch.setenv("MAX_SIZE_BYTES", "4096")
        get_settings.cache_clear()

        try:
            assert ExtractRequest(file_base64="abc=").max_size_bytes == 4096
        finally:
            get_settings.cache_clear()

    def test_rejects_empty_file_base64(self):
        with pytest.raises(ValidationError):
            ExtractRequest(file_base64="")

    def test_rejects_missing_file_base64(self):
        with pytest.raises(ValidationError):
            ExtractRequest()

    def test_rejects_non_positive_max_size(self):
        with pytest.raises(ValidationError):
            ExtractRequest(file_base64="abc=", max_size_bytes=0)


class TestExtractResult:
    def test_serializes_pages_and_metadata_from_document(self):
        document = ExtractedDocument((ExtractedPage(1, "hi"), ExtractedPage(2, "bye")))

        payload = ExtractResult.from_document(document).model_dump()

        assert payload == {
            "pages": [
                {"page": 1, "text": "hi"},
                {"page": 2, "text": "bye"},
            ],
            "total_pages": 2,
            "total_characters": 5,
        }


class TestProblemDetails:
    def test_serializes_rfc9457_shape_from_domain_error(self):
        error = EncryptedPdfError("The PDF is encrypted and requires a password.")

        payload = from_domain_error(error, instance="/extract").model_dump()

        assert payload == {
            "type": "/problems/encrypted_pdf",
            "title": "Encrypted PDF",
            "status": 400,
            "detail": "The PDF is encrypted and requires a password.",
            "instance": "/extract",
            "code": "ENCRYPTED_PDF",
        }
