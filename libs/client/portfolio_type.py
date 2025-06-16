from typing import Optional, List, Dict, Any

from ..schema.responses import (
    PortfolioTypeListResponse,
    PortfolioTypeLightListResponse,
    GenericAttributeTypeListResponse,
)
from ..schema.via_data_model_codegen.finmars_schema import (
    PortfolioType,
    PortfolioTypeLight,
    GenericAttribute,
    GenericAttributeType,
    RecalculateAttributes,
)

from .base import BaseHTTPClient


class PortfolioTypeClient(BaseHTTPClient):
    """Client for portfolio type related operations."""

    async def list_portfolio_types(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PortfolioTypeListResponse:
        """
        List all portfolio types.

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            PortfolioTypeListResponse with paginated results
        """
        params = {}
        if ordering:
            params["ordering"] = ordering
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size

        return await self.get(
            endpoint="portfolios/portfolio-type/",
            params=params,
            response_model=PortfolioTypeListResponse,
        )

    async def get_portfolio_type(self, portfolio_type_id: int) -> PortfolioType:
        """
        Get a specific portfolio type by ID.

        Args:
            portfolio_type_id: The ID of the portfolio type

        Returns:
            PortfolioType object
        """
        return await self.get(
            endpoint=f"portfolios/portfolio-type/{portfolio_type_id}/",
            response_model=PortfolioType,
        )

    async def list_portfolio_types_light(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> PortfolioTypeLightListResponse:
        """
        List all portfolio types in light format (minimal data).

        Args:
            ordering: Which field to use when ordering the results
            page: Page number within the paginated result set
            page_size: Number of results to return per page

        Returns:
            PortfolioTypeLightListResponse with paginated results
        """
        params = {}
        if ordering:
            params["ordering"] = ordering
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size

        return await self.get(
            endpoint="portfolios/portfolio-type/light/",
            params=params,
            response_model=PortfolioTypeLightListResponse,
        )

    async def get_portfolio_type_attributes(self) -> List[GenericAttribute]:
        """
        Get portfolio type attributes.

        Returns:
            List of GenericAttribute objects
        """
        response = await self.get(
            endpoint="portfolios/portfolio-type/attributes/",
        )
        return [GenericAttribute.model_validate(item) for item in response]

    async def list_portfolio_attribute_types(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> GenericAttributeTypeListResponse:
        """
        List all portfolio attribute types.

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
            endpoint="portfolios/portfolio-attribute-type/",
            params=params,
            response_model=GenericAttributeTypeListResponse,
        )

    async def get_portfolio_attribute_type(
        self, attribute_type_id: int
    ) -> GenericAttributeType:
        """
        Get a specific portfolio attribute type by ID.

        Args:
            attribute_type_id: The ID of the attribute type

        Returns:
            GenericAttributeType object
        """
        return await self.get(
            endpoint=f"portfolios/portfolio-attribute-type/{attribute_type_id}/",
            response_model=GenericAttributeType,
        )

    async def get_portfolio_attribute_type_objects_to_recalculate(
        self, attribute_type_id: int
    ) -> RecalculateAttributes:
        """
        Get objects to recalculate for a portfolio attribute type.

        Args:
            attribute_type_id: The ID of the attribute type

        Returns:
            RecalculateAttributes object
        """
        return await self.get(
            endpoint=f"portfolios/portfolio-attribute-type/{attribute_type_id}/objects-to-recalculate/",
            response_model=RecalculateAttributes,
        )

    async def list_portfolio_type_attribute_types(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> GenericAttributeTypeListResponse:
        """
        List all portfolio type attribute types.

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
            endpoint="portfolios/portfolio-type-attribute-type/",
            params=params,
            response_model=GenericAttributeTypeListResponse,
        )

    async def get_portfolio_type_attribute_type(
        self, attribute_type_id: int
    ) -> GenericAttributeType:
        """
        Get a specific portfolio type attribute type by ID.

        Args:
            attribute_type_id: The ID of the attribute type

        Returns:
            GenericAttributeType object
        """
        return await self.get(
            endpoint=f"portfolios/portfolio-type-attribute-type/{attribute_type_id}/",
            response_model=GenericAttributeType,
        )

    async def get_portfolio_type_attribute_type_objects_to_recalculate(
        self, attribute_type_id: int
    ) -> RecalculateAttributes:
        """
        Get objects to recalculate for a portfolio type attribute type.

        Args:
            attribute_type_id: The ID of the attribute type

        Returns:
            RecalculateAttributes object
        """
        return await self.get(
            endpoint=f"portfolios/portfolio-type-attribute-type/{attribute_type_id}/objects-to-recalculate/",
            response_model=RecalculateAttributes,
        )
