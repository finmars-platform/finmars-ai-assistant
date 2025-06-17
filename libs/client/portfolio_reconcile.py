from typing import Optional, Dict, Any
from datetime import date

from ..schema.responses import (
    PortfolioReconcileGroupListResponse,
    PortfolioReconcileHistoryListResponse,
)
from ..schema.via_data_model_codegen.finmars_schema import (
    PortfolioReconcileGroup,
    PortfolioReconcileHistory,
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
        params = {
            "realm_code": self.realm,
            "space_code": self.space,
        }
        return await self.get(
            endpoint=f"portfolios/portfolio-reconcile-group/{group_id}/",
            params=params,
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
        params = {
            "realm_code": self.realm,
            "space_code": self.space,
        }
        return await self.get(
            endpoint=f"portfolios/portfolio-reconcile-history/{history_id}/",
            params=params,
            response_model=PortfolioReconcileHistory,
        )

    async def list_portfolio_reconcile_status(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PortfolioReconcileStatus:
        """
        List portfolio reconcile status.

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            PortfolioReconcileStatus with paginated results
        """
        params = {}
        if ordering:
            params["ordering"] = ordering
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size

        return await self.get(
            endpoint="portfolios/portfolio-reconcile-history/status/",
            params=params,
            response_model=PortfolioReconcileStatus,
        )
