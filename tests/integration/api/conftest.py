"""Shared fixtures for API integration tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client_no_raise() -> TestClient:
    """TestClient that surfaces 500 responses instead of re-raising the cause.

    Starlette's ServerErrorMiddleware always re-raises the original exception
    after sending the 500 response; with the default client that exception is
    propagated to the test. This fixture is only for tests that assert on that
    response body.
    """
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
