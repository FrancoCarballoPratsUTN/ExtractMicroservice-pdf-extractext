"""FastAPI application factory and module-level instance."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.exception_handlers import (
    domain_error_handler,
    internal_error_handler,
    validation_error_handler,
)
from app.api.routes import extract, health
from app.config import get_settings
from app.domain.exceptions import DomainError


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.version)

    app.include_router(health.router)
    app.include_router(extract.router)

    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, internal_error_handler)

    return app


app = create_app()
