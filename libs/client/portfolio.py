from typing import Optional, List, Dict, Any
from datetime import date

from ..schema.responses import (
    PortfolioListResponse,
    PortfolioLightListResponse,
    FirstTransactionDateListResponse,
)
from ..schema.via_data_model_codegen.portfolio_schema import (
    Portfolio,
    PortfolioLight,
    FirstTransactionDateRequest,
    GenericAttribute,
)
from .base import BaseHTTPClient


class PortfolioClient(BaseHTTPClient):
    """Client for portfolio-related operations."""

    async def list_portfolios(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PortfolioListResponse:
        """
        List all portfolios.

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            PortfolioListResponse with paginated results
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
            endpoint="portfolios/portfolio/",
            params=params,
            response_model=PortfolioListResponse,
        )

    async def get_portfolio(self, portfolio_id: int) -> Portfolio:
        """
        Get a specific portfolio by ID.

        Args:
            portfolio_id: The ID of the portfolio

        Returns:
            Portfolio object
        """
        params = {
            "realm_code": self.realm,
            "space_code": self.space,
        }
        return await self.get(
            endpoint=f"portfolios/portfolio/{portfolio_id}/",
            params=params,
            response_model=Portfolio,
        )

    async def list_portfolios_light(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PortfolioLightListResponse:
        """
        List all portfolios in light format (minimal data).

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            PortfolioLightListResponse with paginated results
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
            endpoint="portfolios/portfolio/light/",
            params=params,
            response_model=PortfolioLightListResponse,
        )

    async def list_portfolio_attributes(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PortfolioListResponse:
        """
        List portfolio attributes.

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            PortfolioListResponse with paginated results
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
            endpoint="portfolios/portfolio/attributes/",
            params=params,
            response_model=PortfolioListResponse,
        )

    async def get_inception_date(self) -> Dict[str, Any]:
        """
        Get portfolio inception date information.

        Returns:
            Dictionary with inception date information
        """
        params = {
            "realm_code": self.realm,
            "space_code": self.space,
        }
        return await self.get(
            endpoint="portfolios/portfolio/get-inception-date/", params=params
        )

    async def list_first_transaction_dates(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> FirstTransactionDateListResponse:
        """
        List first transaction dates for portfolios.

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            FirstTransactionDateListResponse with paginated results
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
            endpoint="portfolios/first-transaction-date/",
            params=params,
            response_model=FirstTransactionDateListResponse,
        )

    async def get_first_transaction_date(
        self, portfolio_id: int
    ) -> FirstTransactionDateRequest:
        """
        Get first transaction date for a specific portfolio.

        Args:
            portfolio_id: The ID of the portfolio

        Returns:
            FirstTransactionDateRequest object
        """
        params = {
            "realm_code": self.realm,
            "space_code": self.space,
        }
        return await self.get(
            endpoint=f"portfolios/first-transaction-date/{portfolio_id}/",
            params=params,
            response_model=FirstTransactionDateRequest,
        )
