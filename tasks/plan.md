# Implementation Plan: Big Pickle — PDF Text Extraction Microservice

## Overview

Build a FastAPI microservice (greenfield) that extracts per-page text from PDFs
submitted as Base64 in JSON. Strict N-layer architecture; RFC 9457 problem
details for errors; in-memory processing; pytest + ruff quality gates.

## Architecture Decisions

- **N-layer, dependency direction inward:** `api` → `application` → `domain`
  ← `infrastructure`. The API never instantiates pypdf; it relies on FastAPI DI
  to inject adapters behind domain ports.
- **Ports & adapters:** `PdfExtractor` port (domain) implemented by
  `PypdfExtractor` (infrastructure); `PayloadDecoder` port implemented by
  `Base64PayloadDecoder`. Keeps pypdf/base64 mechanics out of the application.
- **Exceptions carry wire metadata:** each domain exception defines its own
  `status`, `code`, and `type_uri` so the RFC 9457 handler maps exceptions
  declaratively — no if/else ladder in the controller.
- **RFC 9457 everywhere:** includes converting FastAPI's default
  `RequestValidationError` (422) into the same problem-details shape via a
  global exception handler.
- **Off-event-loop extraction:** the endpoint calls the blocking
  `PdfExtractor.extract` via `fastapi.concurrency.run_in_threadpool`.
- **In-memory only:** decode to `bytes`, wrap in `io.BytesIO`, never touch disk.
- **uv:** single source of truth `pyproject.toml`; `uv sync` vendor + infra locks.

## Task List

### Phase 1: Foundation

- [ ] **Task 1: Project scaffolding** — pyproject.toml (uv, pytest-cov, ruff
      config), test layout, shared fixtures helpers.
- [ ] **Task 2: Domain layer** — `extracted_document` entity, domain exceptions
      (with `status`/`code`/`type_uri`), `PdfExtractor` + `PayloadDecoder`
      ports.

### Checkpoint: Foundation
- [ ] `uv sync` clean, `uv run ruff check .` passes, `uv run pytest` collects.
- [ ] Domain exceptions expose correct `status`/`code`/`type_uri`.
- [ ] Review with human before proceeding.

### Phase 2: Application + Infrastructure

- [ ] **Task 3: pypdf adapter** — `PypdfExtractor` implementing `PdfExtractor`
      (encrypted/corrupt detection).
- [ ] **Task 4: Base64 adapter** — `Base64PayloadDecoder` implementing
      `PayloadDecoder` (strict validation).
- [ ] **Task 5: Extraction service** — orchestrates decode → size check →
      extract → clean → result; raises remainder of the error catalogue
      (`FILE_TOO_LARGE`, `NO_EXTRACTABLE_TEXT`).

### Checkpoint: Core Pipeline
- [ ] Service turns valid payload into `ExtractedDocument` (per-page text +
      metadata) using fake ports.
- [ ] Every domain exception in the catalogue is reachable in tests.
- [ ] Review with human before proceeding.

### Phase 3: API Layer

- [ ] **Task 6: DTOs** — request/response DTOs (Pydantic v2, frozen) + RFC 9457
      problem-details body builder.
- [ ] **Task 7: Routes + wiring** — `GET /health`, `POST /extract`, DI module,
      global exception handlers, app factory in `app/main.py`, `TestClient`
      integration tests.

### Checkpoint: Complete
- [ ] `uv run pytest --cov=app --cov-fail-under=85` passes.
- [ ] `uv run ruff check .` and `uv run ruff format .` clean.
- [ ] Full endpoint flow verified via TestClient against real generated PDFs.
- [ ] Success criteria from SPEC.md all met.
- [ ] Ready for human review.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| pypdf behavior varies across PDF generators (encryption, empty pages) | Med | Test against multiple generated fixtures (plain, multi-page, encrypted, image-only) built in `conftest.py` |
| FastAPI's default 422 is not RFC 9457 | Med | Dedicated `RequestValidationError` handler applied globally; covered by integration test |
| Coverage ≥ 85% hard on adapter edge cases | Low | Unit-test ports with fakes; integration-test adapters against fixtures |
| Event loop blocking under concurrency | Med | `run_in_threadpool` for extraction; verified by inspection/structure |

## Open Questions

- None blocking. `instance` will be the request URL (canonical RFC 9457 usage).