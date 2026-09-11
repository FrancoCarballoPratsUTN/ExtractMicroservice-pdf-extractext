"""FastAPI dependency-injection wiring for the application layer."""

from typing import Annotated

from fastapi import Depends

from app.application.services.pdf_extraction_service import PdfExtractionService
from app.infrastructure.encoding.base64_payload_decoder import Base64PayloadDecoder
from app.infrastructure.pdf.pypdf_extractor import PypdfExtractor


def build_extraction_service() -> PdfExtractionService:
    """Compose the extraction use case with its concrete adapters."""
    return PdfExtractionService(
        decoder=Base64PayloadDecoder(), extractor=PypdfExtractor()
    )


ExtractionServiceDep = Annotated[
    PdfExtractionService, Depends(build_extraction_service)
]
