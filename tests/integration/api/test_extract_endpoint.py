"""Integration tests for the PDF extraction endpoint."""

from tests.fixtures.pdf_factory import build_pdf_bytes, pdf_to_base64


class TestExtractEndpoint:
    def test_returns_extracted_pages(self, client):
        encoded = pdf_to_base64(build_pdf_bytes(["Alpha page", "Beta page"]))

        response = client.post("/extract", json={"file_base64": encoded})

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        pages = response.json()["pages"]
        assert pages[0]["text"].strip() == "Alpha page"
        assert pages[1]["text"].strip() == "Beta page"

    def test_returns_page_metadata(self, client):
        encoded = pdf_to_base64(build_pdf_bytes(["One", "Two", "Three"]))

        response = client.post("/extract", json={"file_base64": encoded})

        body = response.json()
        assert body["total_pages"] == 3
        assert body["total_characters"] == len("OneTwoThree")
