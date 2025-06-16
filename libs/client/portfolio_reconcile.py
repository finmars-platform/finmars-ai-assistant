from typing import Optional, Dict, Any
from datetime import date

from ..schema import (
    PortfolioReconcileGroup,
    PortfolioReconcileHistory,
    PortfolioReconcileGroupListResponse,
    PortfolioReconcileHistoryListResponse,
    PortfolioReconcileStatus,
)
from .base import BaseHTTPClient


class PortfolioReconcileClient(BaseHTTPClient):
    """Client for portfolio reconciliation related operations."""

    async def list_portfolio_reconcile_groups(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PortfolioReconcileGroupListResponse:
        """
        List all portfolio reconcile groups.

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            PortfolioReconcileGroupListResponse with paginated results
        """
        params = {}
        if ordering:
            params["ordering"] = ordering
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size

        return await self.get(
            endpoint="portfolios/portfolio-reconcile-group/",
            params=params,
            response_model=PortfolioReconcileGroupListResponse,
        )

    async def get_portfolio_reconcile_group(
        self, group_id: int
    ) -> PortfolioReconcileGroup:
        """
        Get a specific portfolio reconcile group by ID.

        Args:
            group_id: The ID of the portfolio reconcile group

        Returns:
            PortfolioReconcileGroup object
        """
        return await self.get(
            endpoint=f"portfolios/portfolio-reconcile-group/{group_id}/",
            response_model=PortfolioReconcileGroup,
        )

    async def list_portfolio_reconcile_history(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PortfolioReconcileHistoryListResponse:
        """
        List all portfolio reconcile history records.

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            PortfolioReconcileHistoryListResponse with paginated results
        """
        params = {}
        if ordering:
            params["ordering"] = ordering
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size

        return await self.get(
            endpoint="portfolios/portfolio-reconcile-history/",
            params=params,
            response_model=PortfolioReconcileHistoryListResponse,
        )

    async def get_portfolio_reconcile_history(
        self, history_id: int
    ) -> PortfolioReconcileHistory:
        """
        Get a specific portfolio reconcile history record by ID.

        Args:
            history_id: The ID of the portfolio reconcile history record

        Returns:
            PortfolioReconcileHistory object
        """
        return await self.get(
            endpoint=f"portfolios/portfolio-reconcile-history/{history_id}/",
            response_model=PortfolioReconcileHistory,
        )

    async def get_portfolio_reconcile_status(self) -> Dict[str, Any]:
        """
        Get portfolio reconcile status.

        Returns:
            Dictionary with reconcile status information
        """
        return await self.get(endpoint="portfolios/portfolio-reconcile-history/status/")
