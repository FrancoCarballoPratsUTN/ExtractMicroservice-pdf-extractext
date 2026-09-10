# Tasks: Big Pickle — PDF Text Extraction Microservice

## Task 1: Project scaffolding

**Description:** Set up `pyproject.toml` with uv, pytest, pytest-cov and ruff;
create the test/package layout and shared fixture helpers for generating
in-memory PDFs.

**Acceptance criteria:**
- [x] `uv sync` succeeds and locks dependencies (fastapi, pypdf, pydantic,
      uvicorn, pytest, pytest-cov, httpx, ruff)
- [x] `pyproject.toml` configures pytest (`testpaths`, `--cov=app`,
      `--cov-fail-under=85`) and ruff (`target-version = py310`)
- [x] `conftest.py` exposes a helper that builds minimal in-memory PDF bytes

**Verification:**
- [x] Tests pass: `uv run pytest`
- [x] Lint clean: `uv run ruff check .`
- [ ] Manual check: `uv run uvicorn app.main:app` not required yet (no app)

**Dependencies:** None

**Files likely touched:**
- `pyproject.toml`
- `tests/conftest.py`
- `app/main.py` (empty placeholder) (if needed)

**Estimated scope:** Small

## Task 2: Domain layer

**Description:** Define the domain: `ExtractedDocument` entity (pages +
metadata), domain exceptions carrying `status`/`code`/`type_uri` for RFC 9457,
and the `PdfExtractor` + `PayloadDecoder` abstract ports.

**Acceptance criteria:**
- [ ] `ExtractedDocument` validates non-empty pages and consistent metadata
- [ ] Each domain exception has typed `status` (int), `code` (str), `type_uri`
      (str) attributes
- [ ] Ports are abstract classes (or Protocols) with clear signatures —
      `extract(data: bytes) -> ExtractedDocument`,
      `decode(payload: str) -> bytes`

**Verification:**
- [ ] Tests pass: `uv run pytest tests/unit/domain -q`
- [ ] Lint clean: `uv run ruff check .`

**Dependencies:** Task 1

**Files likely touched:**
- `app/domain/entities/extracted_document.py`
- `app/domain/exceptions.py`
- `app/domain/ports/pdf_extractor.py`
- `app/domain/ports/payload_decoder.py`
- `tests/unit/domain/test_extracted_document.py`
- `tests/unit/domain/test_exceptions.py`

**Estimated scope:** Medium

## Task 3: pypdf adapter

**Description:** Implement `PypdfExtractor` (infrastructure) behind the
`PdfExtractor` port: read from bytes, detect encryption, extract per page,
return `ExtractedDocument`.

**Acceptance criteria:**
- [ ] Valid multi-page PDF bytes → `ExtractedDocument` with per-page text and
      correct `total_pages`/`total_characters`
- [ ] Encrypted PDF → `EncryptedPdfError`
- [ ] Corrupt/unparseable PDF → `PdfCorruptedError`
- [ ] No pypdf API used outside this adapter

**Verification:**
- [ ] Tests pass: `uv run pytest tests/integration/infrastructure -q`
- [ ] Lint clean: `uv run ruff check .`

**Dependencies:** Task 2

**Files likely touched:**
- `app/infrastructure/pdf/pypdf_extractor.py`
- `tests/integration/infrastructure/test_pypdf_extractor.py`

**Estimated scope:** Small

## Task 4: Base64 adapter

**Description:** Implement `Base64PayloadDecoder` behind the `PayloadDecoder`
port: strict, in-memory Base64 decoding; corrupt payload → `InvalidBase64Error`.

**Acceptance criteria:**
- [ ] Valid standard Base64 → decoded `bytes`
- [ ] Rejects urlsafe/whitespace/non-Base64 payloads → `InvalidBase64Error`
- [ ] Decoding is in-memory (no temp files)

**Verification:**
- [ ] Tests pass: `uv run pytest tests/integration/infrastructure -q`
- [ ] Lint clean: `uv run ruff check .`

**Dependencies:** Task 2

**Files likely touched:**
- `app/infrastructure/encoding/base64_payload_decoder.py`
- `tests/integration/infrastructure/test_base64_payload_decoder.py`

**Estimated scope:** Small

## Task 5: Extraction service

**Description:** Implement `PdfExtractionService` (application): inject decoder
+ extractor, decode, enforce size cap (`FILE_TOO_LARGE`), extract, detect empty
result (`NO_EXTRACTABLE_TEXT`), map to `ExtractedDocument`.

**Acceptance criteria:**
- [ ] Valid payload → `ExtractedDocument` with per-page text + metadata
- [ ] Decoded size > cap → `FileTooLargeError`
- [ ] All pages empty → `NoExtractableTextError`
- [ ] Depends only on domain ports (no pypdf/base64 imports)

**Verification:**
- [ ] Tests pass: `uv run pytest tests/unit/application -q`
- [ ] Lint clean: `uv run ruff check .`

**Dependencies:** Tasks 3, 4

**Files likely touched:**
- `app/application/services/pdf_extraction_service.py`
- `tests/unit/application/test_pdf_extraction_service.py`

**Estimated scope:** Small

## Task 6: DTOs

**Description:** Define Pydantic v2 request/response DTOs (frozen) and the RFC
9457 problem-details body builder used by the exception handler.

**Acceptance criteria:**
- [ ] `ExtractRequest` validates `file_base64` (str, non-empty) and
      `max_size_bytes` (positive int, optional)
- [ ] `ExtractResult` serializes pages + `total_pages` + `total_characters`
- [ ] Problem-details builder produces `type`/`title`/`status`/`detail`/
      `instance`/`code` from a domain exception
- [ ] All DTOs are `frozen=True`

**Verification:**
- [ ] Tests pass: `uv run pytest tests/unit/api -q`
- [ ] Lint clean: `uv run ruff check .`

**Dependencies:** Task 5

**Files likely touched:**
- `app/api/dto/requests.py`
- `app/api/dto/responses.py`
- `app/api/dto/errors.py`
- `tests/unit/api/test_dtos.py`

**Estimated scope:** Small

## Task 7: Routes + wiring

**Description:** Add `GET /health` and `POST /extract`, FastAPI DI, global
exception handlers (domain → RFC 9457, validation → 422, fallback → 500), and
the app factory in `app/main.py`; run `extract` off the event loop via
`run_in_threadpool`. Integration-test the full endpoint.

**Acceptance criteria:**
- [ ] `GET /health` → `200 {"status": "ok"}`
- [ ] `POST /extract` with valid in-memory PDF → `200` with per-page text +
      metadata
- [ ] Each error catalogue row returns its HTTP status + problem-details body
      with `Content-Type: application/problem+json`
- [ ] Extraction executed via `run_in_threadpool`
- [ ] `/docs` serves OpenAPI
- [ ] `instance` populated with the request URL

**Verification:**
- [ ] Tests pass: `uv run pytest --cov=app --cov-fail-under=85`
- [ ] Lint clean: `uv run ruff check . && uv run ruff format .`
- [ ] Manual check: `uv run uvicorn app.main:app --reload` + `/docs` loads

**Dependencies:** Task 6

**Files likely touched:**
- `app/api/routes/health.py`
- `app/api/routes/extract.py`
- `app/api/dependencies.py`
- `app/main.py`
- `tests/integration/api/test_extract_endpoint.py`
- `tests/integration/api/test_health_endpoint.py`

**Estimated scope:** Medium