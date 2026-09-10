"""Application service orchestrating the PDF extraction use case."""

from app.domain.entities.extracted_document import ExtractedDocument
from app.domain.exceptions import FileTooLargeError, NoExtractableTextError
from app.domain.ports.payload_decoder import PayloadDecoder
from app.domain.ports.pdf_extractor import PdfExtractor


class PdfExtractionService:
    """Turns a Base64-encoded PDF payload into an extracted document.

    The service depends only on domain ports, keeping the use case decoupled
    from any concrete encoding or PDF library.
    """

    def __init__(self, decoder: PayloadDecoder, extractor: PdfExtractor) -> None:
        self._decoder = decoder
        self._extractor = extractor

    def extract(self, payload: str, max_size_bytes: int) -> ExtractedDocument:
        data = self._decoder.decode(payload)
        if len(data) > max_size_bytes:
            raise FileTooLargeError(
                "The decoded file exceeds the configured size limit."
            )
        document = self._extractor.extract(data)
        if document.total_characters == 0:
            raise NoExtractableTextError("The PDF does not contain extractable text.")
        return document
