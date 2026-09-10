"""RFC 9457 problem-details DTO and its builders."""

from pydantic import BaseModel, ConfigDict

from app.domain.exceptions import DomainError


class ProblemDetails(BaseModel):
    """Problem-details body as defined by RFC 9457, plus a ``code`` extension."""

    model_config = ConfigDict(frozen=True)

    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str


def from_domain_error(error: DomainError, instance: str) -> ProblemDetails:
    """Map a domain exception onto an RFC 9457 problem-details body."""
    return ProblemDetails(
        type=error.type_uri,
        title=error.title,
        status=error.status,
        detail=error.detail,
        instance=instance,
        code=error.code,
    )
