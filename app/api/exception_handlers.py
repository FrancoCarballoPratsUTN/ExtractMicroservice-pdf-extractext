"""RFC 9457 exception handlers that serialize failures as problem details."""

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.dto.errors import ProblemDetails, from_domain_error
from app.domain.exceptions import DomainError

logger = logging.getLogger(__name__)


def _problem_response(problem: ProblemDetails) -> JSONResponse:
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(),
        media_type="application/problem+json",
    )


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Serialize any domain exception as an RFC 9457 problem-details body."""
    return _problem_response(from_domain_error(exc, instance=str(request.url)))


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Rewrite FastAPI 422 validation failures as problem details."""
    problem = ProblemDetails(
        type="/problems/validation_error",
        title="Request validation error",
        status=422,
        detail=_summarize_validation_errors(exc),
        instance=str(request.url),
        code="VALIDATION_ERROR",
    )
    return _problem_response(problem)


async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all that returns a problem body without leaking internals."""
    logger.error("Unhandled error", exc_info=exc)
    problem = ProblemDetails(
        type="/problems/internal_error",
        title="Internal server error",
        status=500,
        detail="An unexpected error occurred.",
        instance=str(request.url),
        code="INTERNAL_ERROR",
    )
    return _problem_response(problem)


def _summarize_validation_errors(exc: RequestValidationError) -> str:
    summaries = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"])
        summaries.append(f"{location}: {error['msg']}")
    return "; ".join(summaries)
