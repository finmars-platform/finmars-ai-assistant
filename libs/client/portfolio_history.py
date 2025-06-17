from typing import Optional

from .base import BaseHTTPClient
from ..schema.responses import PortfolioHistoryListResponse
from ..schema.via_data_model_codegen.finmars_schema import PortfolioHistory


class PortfolioHistoryClient(BaseHTTPClient):
    """Client for portfolio history related operations."""

    async def list_portfolio_history(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PortfolioHistoryListResponse:
        """
        List all portfolio history records.

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            PortfolioHistoryListResponse with paginated results
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
            endpoint="portfolios/portfolio-history/",
            params=params,
            response_model=PortfolioHistoryListResponse,
        )

    async def get_portfolio_history(self, history_id: int) -> PortfolioHistory:
        """
        Get a specific portfolio history record by ID.

        Args:
            history_id: The ID of the portfolio history record

        Returns:
            PortfolioHistory object
        """
        params = {
            "realm_code": self.realm,
            "space_code": self.space,
        }
        return await self.get(
            endpoint=f"portfolios/portfolio-history/{history_id}/",
            params=params,
            response_model=PortfolioHistory,
        )
