import os
import httpx
from typing import Optional, Dict, Any, TypeVar, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseHTTPClient:
    """Base HTTP client with async support for making API requests."""

    def __init__(
        self,
        base_url: str,
        realm: str = "realm0v4ry",
        space: str = "space0ihxm",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.realm = realm
        self.space = space
        # Load API key from environment variable if not provided
        self.api_key = api_key or os.environ.get("FINMARS_EXPERT_TOKEN")
        self.timeout = timeout
        self.headers = self._get_default_headers()

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_url(self, endpoint: str) -> str:
        """Build full URL with realm and space."""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{self.realm}/{self.space}/api/v1/{endpoint}"

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> T:
        """Make an HTTP request and return validated response."""
        url = self._build_url(endpoint)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=json_data,
            )
            response.raise_for_status()

            if response_model:
                return response_model.model_validate(response.json())
            return response.json()

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> T:
        """Make a GET request."""
        return await self._make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
            response_model=response_model,
        )
