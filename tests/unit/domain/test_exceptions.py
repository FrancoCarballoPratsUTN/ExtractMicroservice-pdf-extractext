"""Tests for domain exceptions and their RFC 9457 metadata."""

import pytest

from app.domain.exceptions import (
    DomainError,
    EncryptedPdfError,
    FileTooLargeError,
    InvalidBase64Error,
    NoExtractableTextError,
    PdfCorruptedError,
)

ERROR_CATALOGUE = (
    (
        InvalidBase64Error,
        400,
        "INVALID_BASE64",
        "/problems/invalid_base64",
        "Invalid Base64 payload",
    ),
    (
        FileTooLargeError,
        413,
        "FILE_TOO_LARGE",
        "/problems/file_too_large",
        "File is too large",
    ),
    (
        EncryptedPdfError,
        400,
        "ENCRYPTED_PDF",
        "/problems/encrypted_pdf",
        "Encrypted PDF",
    ),
    (
        PdfCorruptedError,
        400,
        "PDF_CORRUPTED",
        "/problems/pdf_corrupted",
        "Corrupt PDF",
    ),
    (
        NoExtractableTextError,
        400,
        "NO_EXTRACTABLE_TEXT",
        "/problems/no_extractable_text",
        "No extractable text",
    ),
)


@pytest.mark.parametrize(
    (
        "exception_cls",
        "expected_status",
        "expected_code",
        "expected_type",
        "expected_title",
    ),
    ERROR_CATALOGUE,
)
class TestDomainErrorMetadata:
    def test_exposes_rfc9457_metadata(
        self,
        exception_cls,
        expected_status,
        expected_code,
        expected_type,
        expected_title,
    ):
        error = exception_cls("some detail")

        assert error.status == expected_status
        assert error.code == expected_code
        assert error.type_uri == expected_type
        assert error.title == expected_title


class TestDomainErrorBehavior:
    @pytest.mark.parametrize("exception_cls", [row[0] for row in ERROR_CATALOGUE])
    def test_carries_human_readable_detail(self, exception_cls):
        error = exception_cls("boom")

        assert error.detail == "boom"

    @pytest.mark.parametrize("exception_cls", [row[0] for row in ERROR_CATALOGUE])
    def test_is_a_domain_error(self, exception_cls):
        assert isinstance(exception_cls("x"), DomainError)
