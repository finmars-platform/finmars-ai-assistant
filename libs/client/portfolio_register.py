from typing import Optional, List

from ..schema import (
    PortfolioRegister,
    PortfolioRegisterRecord,
    PortfolioRegisterListResponse,
    PortfolioRegisterRecordListResponse,
    GenericAttributeType,
    GenericAttributeTypeListResponse,
    RecalculateAttributes,
)
from .base import BaseHTTPClient


class PortfolioRegisterClient(BaseHTTPClient):
    """Client for portfolio register related operations."""

    async def list_portfolio_registers(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PortfolioRegisterListResponse:
        """
        List all portfolio registers.

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            PortfolioRegisterListResponse with paginated results
        """
        params = {}
        if ordering:
            params["ordering"] = ordering
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size

        return await self.get(
            endpoint="portfolios/portfolio-register/",
            params=params,
            response_model=PortfolioRegisterListResponse,
        )

    async def get_portfolio_register(self, register_id: int) -> PortfolioRegister:
        """
        Get a specific portfolio register by ID.

        Args:
            register_id: The ID of the portfolio register

        Returns:
            PortfolioRegister object
        """
        return await self.get(
            endpoint=f"portfolios/portfolio-register/{register_id}/",
            response_model=PortfolioRegister,
        )

    async def list_portfolio_register_records(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PortfolioRegisterRecordListResponse:
        """
        List all portfolio register records.

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            PortfolioRegisterRecordListResponse with paginated results
        """
        params = {}
        if ordering:
            params["ordering"] = ordering
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size

        return await self.get(
            endpoint="portfolios/portfolio-register-record/",
            params=params,
            response_model=PortfolioRegisterRecordListResponse,
        )

    async def get_portfolio_register_record(
        self, record_id: int
    ) -> PortfolioRegisterRecord:
        """
        Get a specific portfolio register record by ID.

        Args:
            record_id: The ID of the portfolio register record

        Returns:
            PortfolioRegisterRecord object
        """
        return await self.get(
            endpoint=f"portfolios/portfolio-register-record/{record_id}/",
            response_model=PortfolioRegisterRecord,
        )

    async def list_portfolio_register_attribute_types(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> GenericAttributeTypeListResponse:
        """
        List all portfolio register attribute types.

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            GenericAttributeTypeListResponse with paginated results
        """
        params = {}
        if ordering:
            params["ordering"] = ordering
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size

        return await self.get(
            endpoint="portfolios/portfolio-register-attribute-type/",
            params=params,
            response_model=GenericAttributeTypeListResponse,
        )

    async def get_portfolio_register_attribute_type(
        self, attribute_type_id: int
    ) -> GenericAttributeType:
        """
        Get a specific portfolio register attribute type by ID.

        Args:
            attribute_type_id: The ID of the attribute type

        Returns:
            GenericAttributeType object
        """
        return await self.get(
            endpoint=f"portfolios/portfolio-register-attribute-type/{attribute_type_id}/",
            response_model=GenericAttributeType,
        )

    async def get_portfolio_register_attribute_type_objects_to_recalculate(
        self, attribute_type_id: int
    ) -> RecalculateAttributes:
        """
        Get objects to recalculate for a portfolio register attribute type.

        Args:
            attribute_type_id: The ID of the attribute type

        Returns:
            RecalculateAttributes object
        """
        return await self.get(
            endpoint=f"portfolios/portfolio-register-attribute-type/{attribute_type_id}/objects-to-recalculate/",
            response_model=RecalculateAttributes,
        )
