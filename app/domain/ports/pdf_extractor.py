"""Abstract port for PDF text extraction."""

from abc import ABC, abstractmethod

from app.domain.entities.extracted_document import ExtractedDocument


class PdfExtractor(ABC):
    """Boundary that infrastructure adapters implement with a concrete PDF library."""

    @abstractmethod
    def extract(self, data: bytes) -> ExtractedDocument:
        """Extract structured text from PDF bytes.

        Raises:
            EncryptedPdfError: If the PDF requires a password.
            PdfCorruptedError: If the PDF cannot be parsed.
        """
