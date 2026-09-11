"""PDF text-extraction endpoint."""

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from app.api.dependencies import ExtractionServiceDep
from app.api.dto.requests import ExtractRequest
from app.api.dto.responses import ExtractResult

router = APIRouter(tags=["extract"])


@router.post("/extract", response_model=ExtractResult, status_code=200)
async def extract(
    request: ExtractRequest, service: ExtractionServiceDep
) -> ExtractResult:
    """Decode a Base64 PDF and return its per-page text."""
    document = await run_in_threadpool(
        service.extract, request.file_base64, request.max_size_bytes
    )
    return ExtractResult.from_document(document)
