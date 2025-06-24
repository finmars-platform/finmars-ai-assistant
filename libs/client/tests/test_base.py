import os
import pytest
import httpx
from unittest.mock import AsyncMock, patch
from pydantic import BaseModel

from ..base import BaseHTTPClient


class TestModel(BaseModel):
    id: int
    name: str


class TestBaseHTTPClient:
    """Test cases for BaseHTTPClient."""

    @pytest.fixture
    def client(self):
        return BaseHTTPClient(
            base_url=os.getenv("FINMARS_BASE_URL"),
            realm="test_realm",
            space="test_space",
            api_key="test-api-key",
        )

    def test_init(self, client):
        """Test client initialization."""
        assert client.base_url == os.getenv("FINMARS_BASE_URL")
        assert client.realm == "test_realm"
        assert client.space == "test_space"
        assert client.api_key == "test-api-key"
        assert client.timeout == 30.0

    def test_get_default_headers(self, client):
        """Test default headers generation."""
        headers = client._get_default_headers()
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test-api-key"

    def test_build_url(self, client):
        """Test URL building."""
        url = client._build_url("portfolios/portfolio/")
        expected = f"{os.getenv('FINMARS_BASE_URL', 'https://api.finmars.com')}/test_realm/test_space/api/v1/portfolios/portfolio/"
        assert url == expected

    @pytest.mark.asyncio
    async def test_get_success(self, client):
        """Test successful GET request."""
        mock_response = AsyncMock()
        mock_response.json.return_value = {"id": 1, "name": "Test"}
        mock_response.raise_for_status = AsyncMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.request.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_class.return_value = mock_client_instance

            result = await client.get(
                endpoint="portfolios/portfolio/1/", response_model=TestModel
            )

            assert isinstance(result, TestModel)
            assert result.id == 1
            assert result.name == "Test"

    @pytest.mark.asyncio
    async def test_get_with_params(self, client):
        """Test GET request with query parameters."""
        mock_response = AsyncMock()
        mock_response.json.return_value = {"count": 1, "results": []}
        mock_response.raise_for_status = AsyncMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.request.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_class.return_value = mock_client_instance

            result = await client.get(
                endpoint="portfolios/portfolio/", params={"page": 1, "page_size": 10}
            )

            # Verify the request was made with correct parameters
            mock_client_instance.request.assert_called_once()
            call_args = mock_client_instance.request.call_args
            assert call_args.kwargs["params"] == {"page": 1, "page_size": 10}

    @pytest.mark.asyncio
    async def test_get_http_error(self, client):
        """Test GET request with HTTP error."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_response = AsyncMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=AsyncMock(), response=AsyncMock()
            )
            mock_client_instance.request.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_class.return_value = mock_client_instance

            with pytest.raises(httpx.HTTPStatusError):
                await client.get(endpoint="portfolios/portfolio/999/")
