from typing import Optional, List

from .base import BaseHTTPClient
from ..schema.base import PaginatedResponse
from ..schema.via_data_model_codegen.instrument_schema import PriceHistoryActual


class PriceHistoryListResponse(PaginatedResponse):
    results: List[PriceHistoryActual]


class InstrumentPriceHistoryClient(BaseHTTPClient):
    """Client for instrument price history operations (GET only)."""

    async def list_price_history(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PriceHistoryListResponse:
        """
        List instrument price history records.

        Args:
            ordering: Which field to use when ordering the results.
            page: A page number within the paginated result set.
            page_size: Number of results to return per page.

        Returns:
            PriceHistoryListResponse with paginated results.
        """
        params = {
            "realm_code": self.realm,
            "space_code": self.space,
        }
        if ordering:
            params["ordering"] = ordering
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size

        return await self.get(
            endpoint="instruments/price-history/",
            params=params,
            response_model=PriceHistoryListResponse,
        )
