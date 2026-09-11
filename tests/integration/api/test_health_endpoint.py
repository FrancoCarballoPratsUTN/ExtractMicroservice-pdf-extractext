"""Integration tests for the health check endpoint."""


class TestHealthEndpoint:
    def test_returns_ok_status(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
