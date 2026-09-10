"""pypdf adapter implementing the PdfExtractor port."""

from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.domain.entities.extracted_document import ExtractedDocument, ExtractedPage
from app.domain.exceptions import EncryptedPdfError, PdfCorruptedError
from app.domain.ports.pdf_extractor import PdfExtractor


class PypdfExtractor(PdfExtractor):
    """Extract structured text from PDF bytes using pypdf."""

    def extract(self, data: bytes) -> ExtractedDocument:
        try:
            reader = PdfReader(BytesIO(data))
        except PdfReadError as exc:
            raise PdfCorruptedError(
                "The PDF file is corrupt or cannot be parsed."
            ) from exc

        if reader.is_encrypted:
            raise EncryptedPdfError(
                "The PDF is encrypted and requires a password to read."
            )

        pages = tuple(
            ExtractedPage(index, self._extract_page_text(reader, index))
            for index in range(1, len(reader.pages) + 1)
        )
        return ExtractedDocument(pages)

    @staticmethod
    def _extract_page_text(reader: PdfReader, page_number: int) -> str:
        return reader.pages[page_number - 1].extract_text()
