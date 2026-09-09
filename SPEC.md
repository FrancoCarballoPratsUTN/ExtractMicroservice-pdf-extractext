# Spec: Big Pickle — PDF Text Extraction Microservice

## Objective

Build a FastAPI microservice that extracts text from PDF documents sent as
Base64-encoded JSON, returning the extracted content as structured JSON.

The consumer sends a PDF file encoded in Base64 inside a JSON request body. The
service decodes it safely in memory, extracts text with `pypdf`, cleans it, and
returns a page-structured JSON response with metadata.

**User story:**
> As an API consumer, I send a Base64-encoded PDF to `POST /extract` and receive
> the extracted text per page plus metadata, or a clear machine-readable error if
> the file cannot be processed.

**Success:** a caller can submit a valid PDF and always receive either a `200 OK`
with the extracted text or a well-formed, correctly-coded error — never a crash
or an unhandled exception leaking to the client.

## Tech Stack

- Python `3.10+`
- FastAPI (latest stable, Pydantic v2)
- `pypdf` for PDF text extraction
- `uv` as package manager (`pyproject.toml` + `uv.lock`)
- `uvicorn` as ASGI server
- Testing: `pytest`, `httpx`, `pytest-cov`
- Linting/formatting: `ruff`

## Commands

```bash
# Sync dependencies (creates .venv + uv.lock)
uv sync

# Run the API locally (dev, with reload)
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Run tests with coverage threshold
uv run pytest --cov=app --cov-fail-under=85

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

## Project Structure

Strict N-layer architecture. Dependency direction: the outer layers depend on
the inner ones; the API layer never talks to the infrastructure layer directly.

```
app/
├── main.py                  → FastAPI app factory, routing + middleware setup
├── api/
│   ├── routes/
│   │   ├── health.py        → GET /health
│   │   └── extract.py       → POST /extract
│   ├── dto/
│   │   ├── requests.py      → Request DTOs (Pydantic models)
│   │   ├── responses.py     → Response DTOs (Pydantic models)
│   │   └── errors.py        → RFC 9457 problem-details DTO (exception → HTTP)
│   └── dependencies.py      → FastAPI dependency injection wiring
├── application/
│   └── services/
│       └── pdf_extraction_service.py  → Use case orchestrator
├── domain/
│   ├── entities/
│   │   └── extracted_document.py      → Domain entity (pages + metadata)
│   ├── ports/
│   │   └── pdf_extractor.py           → Abstract port (interface)
│   └── exceptions.py                  → Domain exceptions with error codes
└── infrastructure/
    └── pdf/
        └── pypdf_extractor.py         → pypdf adapter implementing the port
```

Tests mirror the package layout:

```
tests/
├── unit/
│   ├── application/          → service tests with mocked port
│   └── domain/               → entity/exceptions tests
├── integration/
│   ├── api/                  → TestClient endpoint tests
│   └── infrastructure/       → pypdf adapter tests with real PDF fixtures
├── fixtures/                 → minimal generated/static PDF samples
└── conftest.py               → shared fixtures (valid PDF bytes, base64 payloads)
```

## Code Style

- PEP 8 via `ruff` defaults; type hints on every function signature.
- Docstrings in **English** (Google style) on public functions and classes.
- Internal helper names: `_private` underscore prefix.
- Domain exceptions carry a stable snake_case `code` used on the wire.

```python
# example of the prevailing style
async def extract(self, request: ExtractRequest) -> ExtractResult:
    """Extract text from a Base64-encoded PDF.

    Args:
        request: Validated request DTO containing the Base64 payload.

    Returns:
        ExtractResult with per-page text and document metadata.

    Raises:
        EncryptedPdfError: If the PDF requires a password.
    """
    ...
```

DTOs are `frozen=True`; validation lives in Pydantic field validators, business
rules live in services.

## Testing Strategy

- **Framework:** `pytest`.
- **Levels:**
  - *Unit* — service use case with a `FakePdfExtractor` port; DTO validation.
  - *Integration* — pypdf adapter against real in-memory generated PDFs; full
    endpoint via `httpx`/`TestClient`.
- **Coverage:** `--cov=app --cov-fail-under=85`.
- **Fixtures:** minimal valid PDFs generated at test time; corrupt/encrypted/
  no-text PDFs built in `conftest.py`.
- **Concurrency concern:** extraction is an expensive async-friendly operation;
  the endpoint offloads CPU work via `fastapi.concurrency.run_in_threadpool`.

## Boundaries

- **Always:**
  - Run `uv run pytest` and `uv run ruff check .` before committing.
  - Type hints and Google-style docstrings on all public symbols.
  - Validate every request at the boundary with Pydantic.
  - Map domain exceptions to HTTP codes in the controller; never leak a raw
    exception.
  - Offload CPU-bound extraction off the event loop.
- **Ask first:**
  - Adding new dependencies.
  - Changing the request/response contract.
  - Adding or removing endpoints.
  - Changing the coverage threshold or CI config.
- **Never:**
  - Write the PDF to disk in the request path (in-memory only).
  - Log PDF content, secrets, or Base64 payloads.
  - Bypass the port/adapter boundary (API touching pypdf directly).
  - Ignore/suppress a failing test.

## API Contract

### `POST /extract`

Request:
```json
{
  "file_base64": "JVBERi0...",
  "max_size_bytes": 10485760
}
```

- `file_base64`: required, standardized (non-urlsafe) Base64 string.
- `max_size_bytes`: optional, caller-declared cap; default 10 MiB. The service
  enforces the actual decoded size regardless.

Response `200 OK`:
```json
{
  "pages": [
    { "page": 1, "text": "extracted text..." }
  ],
  "total_pages": 2,
  "total_characters": 1234
}
```

Errors are compliant with **RFC 9457** (HTTP Problem Details). Responses use
`Content-Type: application/problem+json` and expose the canonical members
(`type`, `title`, `status`, `detail`, `instance`) plus a `code` extension that
carries the machine-readable error identifier:

```json
{
  "type": "/problems/invalid_base64",
  "title": "Invalid Base64 payload",
  "status": 400,
  "detail": "The provided payload is not valid Base64.",
  "instance": "/extract",
  "code": "INVALID_BASE64"
}
```

- `type` → relative problem-type URI (`/problems/<snake_case>`).
- `title` → short, human-readable summary of the problem class.
- `status` → the HTTP status code.
- `detail` → human-readable explanation of this specific occurrence.
- `instance` → the request path that triggered the error.
- `code` → extension member; stable, machine-readable error identifier
  (see the error catalogue below).

**Error catalogue:**

| Scenario | HTTP | `code` (extension) | `type` URI |
|---|---|---|---|
| Body fails Pydantic validation | 422 | `VALIDATION_ERROR` | `/problems/validation_error` |
| Invalid/corrupt Base64 | 400 | `INVALID_BASE64` | `/problems/invalid_base64` |
| Decoded size exceeds cap | 413 | `FILE_TOO_LARGE` | `/problems/file_too_large` |
| PDF is encrypted / requires password | 400 | `ENCRYPTED_PDF` | `/problems/encrypted_pdf` |
| PDF is corrupt or unparseable | 400 | `PDF_CORRUPTED` | `/problems/pdf_corrupted` |
| No extractable text | 400 | `NO_EXTRACTABLE_TEXT` | `/problems/no_extractable_text` |
| Unexpected internal error | 500 | `INTERNAL_ERROR` | `/problems/internal_error` |

### `GET /health`

Response `200 OK`:
```json
{ "status": "ok" }
```

### OpenAPI

Provided automatically by FastAPI at `/docs` and `/openapi.json`.

## Success Criteria

- `POST /extract` returns `200` with correct per-page text + metadata for a
  valid multi-page PDF.
- Every row in the error catalogue returns its expected HTTP status and `code`.
- CPU-bound extraction runs off the event loop (verified by test/inspection).
- `uv run pytest --cov=app --cov-fail-under=85` passes.
- `uv run ruff check .` passes with zero violations.
- No file is ever written to disk during request handling.

## Open Questions

- Response shape: interpreted as **structured-by-page JSON** (per your "Json"
  answer). Confirm or request a plain-concatenated-text variant.
- Whether the response should include extraction metadata beyond
  `total_pages`/`total_characters` (e.g. producer, PDF version).