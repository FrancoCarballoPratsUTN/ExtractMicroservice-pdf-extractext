"""Response DTOs for the extraction API."""

from pydantic import BaseModel, ConfigDict

from app.domain.entities.extracted_document import ExtractedDocument


class ExtractedPageData(BaseModel):
    """Serialized text of a single PDF page."""

    model_config = ConfigDict(frozen=True)

    page: int
    text: str


class ExtractResult(BaseModel):
    """Serialized output of a PDF extraction."""

    model_config = ConfigDict(frozen=True)

    pages: list[ExtractedPageData]
    total_pages: int
    total_characters: int

    @classmethod
    def from_document(cls, document: ExtractedDocument) -> "ExtractResult":
        """Map a domain document onto its serializable representation."""
        return cls(
            pages=[
                ExtractedPageData(page=page.page, text=page.text)
                for page in document.pages
            ],
            total_pages=document.total_pages,
            total_characters=document.total_characters,
        )
