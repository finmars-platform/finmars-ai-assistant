import os
import pytest
from unittest.mock import AsyncMock, patch

from ..portfolio_type import PortfolioTypeClient
from ...schema.responses import (
    PortfolioTypeListResponse,
    PortfolioTypeLightListResponse,
    GenericAttributeTypeListResponse,
)
from ...schema.via_data_model_codegen.portfolio_schema import (
    PortfolioTypeLight,
    GenericAttribute,
    GenericAttributeType,
    RecalculateAttributes,
)


class TestPortfolioTypeClient:
    """Test cases for PortfolioTypeClient."""

    @pytest.fixture
    def client(self):
        return PortfolioTypeClient(
            base_url=os.getenv("FINMARS_BASE_URL"),
            realm="test_realm",
            space="test_space",
            api_key="test-api-key",
        )

    @pytest.mark.asyncio
    async def test_list_portfolio_types(self, client):
        """Test listing portfolio types."""
        mock_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "user_code": "TYPE001",
                    "configuration_code": "CONFIG001",
                    "name": "Test Portfolio Type",
                    "short_name": "TPT",
                    "portfolio_class": 1,
                }
            ],
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = PortfolioTypeListResponse.model_validate(
                mock_response
            )

            result = await client.list_portfolio_types()

            mock_get.assert_called_once_with(
                endpoint="portfolios/portfolio-type/",
                params={},
                response_model=PortfolioTypeListResponse,
            )

            assert result.count == 1
            assert result.results[0].name == "Test Portfolio Type"

    @pytest.mark.asyncio
    async def test_get_portfolio_type(self, client):
        """Test getting a specific portfolio type."""
        mock_response = {
            "id": 1,
            "user_code": "TYPE001",
            "configuration_code": "CONFIG001",
            "name": "Test Portfolio Type",
            "portfolio_class": 1,
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = PortfolioType.model_validate(mock_response)

            result = await client.get_portfolio_type(1)

            mock_get.assert_called_once_with(
                endpoint="portfolios/portfolio-type/1/", response_model=PortfolioType
            )

            assert result.id == 1
            assert result.name == "Test Portfolio Type"

    @pytest.mark.asyncio
    async def test_list_portfolio_attribute_types(self, client):
        """Test listing portfolio attribute types."""
        mock_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "configuration_code": "ATTR_CONFIG",
                    "name": "Test Attribute Type",
                    "content_type": "portfolio.portfolio",
                }
            ],
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = GenericAttributeTypeListResponse.model_validate(
                mock_response
            )

            result = await client.list_portfolio_attribute_types(page=1, page_size=20)

            mock_get.assert_called_once_with(
                endpoint="portfolios/portfolio-attribute-type/",
                params={"page": 1, "page_size": 20},
                response_model=GenericAttributeTypeListResponse,
            )

            assert result.count == 1
            assert result.results[0].name == "Test Attribute Type"

    @pytest.mark.asyncio
    async def test_get_portfolio_attribute_type(self, client):
        """Test getting a specific portfolio attribute type."""
        mock_response = {
            "id": 1,
            "configuration_code": "ATTR_CONFIG",
            "name": "Test Attribute Type",
            "content_type": "portfolio.portfolio",
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = GenericAttributeType.model_validate(mock_response)

            result = await client.get_portfolio_attribute_type(1)

            mock_get.assert_called_once_with(
                endpoint="portfolios/portfolio-attribute-type/1/",
                response_model=GenericAttributeType,
            )

            assert result.id == 1
            assert result.name == "Test Attribute Type"

    @pytest.mark.asyncio
    async def test_get_portfolio_attribute_type_objects_to_recalculate(self, client):
        """Test getting objects to recalculate for portfolio attribute type."""
        mock_response = {
            "task_id": "task-123",
            "task_status": "pending",
            "processed_rows": "0",
            "total_rows": "100",
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = RecalculateAttributes.model_validate(mock_response)

            result = await client.get_portfolio_attribute_type_objects_to_recalculate(1)

            mock_get.assert_called_once_with(
                endpoint="portfolios/portfolio-attribute-type/1/objects-to-recalculate/",
                response_model=RecalculateAttributes,
            )

            assert result.task_id == "task-123"
            assert result.task_status == "pending"
