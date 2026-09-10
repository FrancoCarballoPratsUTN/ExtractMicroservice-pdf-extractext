"""Domain exceptions that map to RFC 9457 problem details."""

from typing import ClassVar


class DomainError(Exception):
    """Base class for domain errors carrying problem-details metadata.

    Subclasses declare the HTTP status, machine-readable code, and problem
    type URI so the API layer can translate them declaratively.
    """

    status: ClassVar[int]
    code: ClassVar[str]
    type_uri: ClassVar[str]

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class InvalidBase64Error(DomainError):
    """The payload is not valid standard Base64."""

    status = 400
    code = "INVALID_BASE64"
    type_uri = "/problems/invalid_base64"


class FileTooLargeError(DomainError):
    """The decoded payload exceeds the configured size limit."""

    status = 413
    code = "FILE_TOO_LARGE"
    type_uri = "/problems/file_too_large"


class EncryptedPdfError(DomainError):
    """The PDF is encrypted and requires a password to read."""

    status = 400
    code = "ENCRYPTED_PDF"
    type_uri = "/problems/encrypted_pdf"


class PdfCorruptedError(DomainError):
    """The PDF is corrupt or cannot be parsed by the extractor."""

    status = 400
    code = "PDF_CORRUPTED"
    type_uri = "/problems/pdf_corrupted"


class NoExtractableTextError(DomainError):
    """The PDF contains no text extractable from any page."""

    status = 400
    code = "NO_EXTRACTABLE_TEXT"
    type_uri = "/problems/no_extractable_text"
