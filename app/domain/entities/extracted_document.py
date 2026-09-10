"""Domain entity representing text extracted from a PDF."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedPage:
    """A single page of extracted text."""

    page: int
    text: str


@dataclass(frozen=True)
class ExtractedDocument:
    """An immutable set of extracted pages plus derived metadata."""

    pages: tuple[ExtractedPage, ...]

    def __post_init__(self) -> None:
        if not self.pages:
            raise ValueError("A document must contain at least one page")
        expected = tuple(range(1, len(self.pages) + 1))
        actual = tuple(page.page for page in self.pages)
        if actual != expected:
            raise ValueError("Pages must be numbered sequentially from 1")

    @property
    def total_pages(self) -> int:
        return len(self.pages)

    @property
    def total_characters(self) -> int:
        return sum(len(page.text) for page in self.pages)
