"""Tests for the ExtractedDocument domain entity."""

import pytest

from app.domain.entities.extracted_document import ExtractedDocument, ExtractedPage


class TestExtractedDocument:
    def test_builds_pages_numbered_from_one(self):
        doc = ExtractedDocument((ExtractedPage(1, "first"), ExtractedPage(2, "second")))

        assert doc.total_pages == 2
        assert doc.pages[0].page == 1
        assert doc.pages[1].page == 2

    def test_counts_total_characters_across_pages(self):
        doc = ExtractedDocument((ExtractedPage(1, "ab"), ExtractedPage(2, "cde")))

        assert doc.total_characters == 5

    def test_allows_individual_empty_pages(self):
        doc = ExtractedDocument((ExtractedPage(1, ""), ExtractedPage(2, "text")))

        assert doc.total_pages == 2

    def test_rejects_document_without_pages(self):
        with pytest.raises(ValueError, match="at least one page"):
            ExtractedDocument(())

    def test_rejects_non_sequential_page_numbers(self):
        with pytest.raises(ValueError, match="sequentially"):
            ExtractedDocument((ExtractedPage(1, "a"), ExtractedPage(3, "b")))

    def test_rejects_page_numbers_starting_at_zero(self):
        with pytest.raises(ValueError, match="sequentially"):
            ExtractedDocument((ExtractedPage(0, "a"),))
