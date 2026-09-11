"""Integration tests for the PDF extraction endpoint."""

import base64

from tests.fixtures.pdf_factory import (
    build_encrypted_pdf_bytes,
    build_no_text_pdf_bytes,
    build_pdf_bytes,
    pdf_to_base64,
)


def _problem(client, **payload) -> dict:
    response = client.post("/extract", json=payload)
    assert response.headers["content-type"].startswith("application/problem+json")
    return response.status_code, response.json()


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

    def test_returns_problem_details_for_invalid_base64(self, client):
        status, body = _problem(client, file_base64="%%%")

        assert status == 400
        assert body["code"] == "INVALID_BASE64"
        assert body["title"] == "Invalid Base64 payload"
        assert body["status"] == 400

    def test_returns_problem_details_for_encrypted_pdf(self, client):
        encoded = pdf_to_base64(build_encrypted_pdf_bytes(["Secret"]))

        status, body = _problem(client, file_base64=encoded)

        assert status == 400
        assert body["code"] == "ENCRYPTED_PDF"

    def test_returns_problem_details_for_corrupt_pdf(self, client):
        encoded = base64.b64encode(b"this is not a pdf").decode("ascii")

        status, body = _problem(client, file_base64=encoded)

        assert status == 400
        assert body["code"] == "PDF_CORRUPTED"

    def test_returns_problem_details_when_file_exceeds_declared_size(self, client):
        encoded = pdf_to_base64(build_pdf_bytes(["Some text"]))

        status, body = _problem(client, file_base64=encoded, max_size_bytes=64)

        assert status == 413
        assert body["code"] == "FILE_TOO_LARGE"
        assert body["title"] == "File is too large"

    def test_returns_problem_details_when_no_text_is_extractable(self, client):
        encoded = pdf_to_base64(build_no_text_pdf_bytes())

        status, body = _problem(client, file_base64=encoded)

        assert status == 400
        assert body["code"] == "NO_EXTRACTABLE_TEXT"

    def test_returns_problem_details_for_validation_errors(self, client):
        status, body = _problem(client)

        assert status == 422
        assert body["code"] == "VALIDATION_ERROR"
        assert body["detail"] != ""

    def test_populates_instance_with_the_request_url(self, client):
        response = client.post("/extract", json={"file_base64": "%%%"})

        assert response.json()["instance"].endswith("/extract")


class TestInternalServerErrors:
    def test_returns_problem_details_for_unexpected_errors(self, client_no_raise):
        from app.api import dependencies
        from app.main import app

        class ExplodingExtractor:
            def extract(self, *args, **kwargs):  # pragma: no cover - never returns
                raise RuntimeError("boom")

        app.dependency_overrides[dependencies.build_extraction_service] = lambda: (
            ExplodingExtractor()
        )
        try:
            status, body = _problem(client_no_raise, file_base64="placeholder")
        finally:
            app.dependency_overrides.pop(dependencies.build_extraction_service)

        assert status == 500
        assert body["code"] == "INTERNAL_ERROR"
        assert body["title"] == "Internal server error"
        assert body["status"] == 500


class TestOpenApiDocs:
    def test_serves_interactive_docs(self, client):
        response = client.get("/docs")

        assert response.status_code == 200
