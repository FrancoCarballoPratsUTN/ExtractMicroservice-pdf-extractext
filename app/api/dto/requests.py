"""Request DTOs for the extraction API."""

from pydantic import BaseModel, ConfigDict, Field

from app.config import get_settings


class ExtractRequest(BaseModel):
    """Validated input for the PDF extraction endpoint."""

    model_config = ConfigDict(frozen=True)

    file_base64: str = Field(min_length=1)
    max_size_bytes: int = Field(
        default_factory=lambda: get_settings().max_size_bytes, gt=0
    )
