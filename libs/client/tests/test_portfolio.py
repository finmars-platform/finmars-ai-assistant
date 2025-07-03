import os
import pytest
from unittest.mock import AsyncMock, patch
from datetime import date

from ..portfolio import PortfolioClient
from ...schema.responses import (
    PortfolioListResponse,
    PortfolioLightListResponse,
    FirstTransactionDateListResponse,
)
from ...schema.via_data_model_codegen.portfolio_schema import (
    Portfolio,
    PortfolioLight,
    FirstTransactionDateRequest,
    GenericAttribute,
)


class TestPortfolioClient:
    """Test cases for PortfolioClient."""

    @pytest.fixture
    def client(self):
        return PortfolioClient(
            base_url=os.getenv("FINMARS_BASE_URL"),
            realm="test_realm",
            space="test_space",
            api_key="test-api-key",
        )

    @pytest.mark.asyncio
    async def test_list_portfolios(self, client):
        """Test listing portfolios."""
        mock_response = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "user_code": "PORT001",
                    "name": "Test Portfolio 1",
                    "short_name": "TP1",
                    "public_name": "Test Portfolio 1",
                },
                {
                    "id": 2,
                    "user_code": "PORT002",
                    "name": "Test Portfolio 2",
                    "short_name": "TP2",
                    "public_name": "Test Portfolio 2",
                },
            ],
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = PortfolioListResponse.model_validate(mock_response)

            result = await client.list_portfolios(page=1, page_size=10)

            mock_get.assert_called_once_with(
                endpoint="portfolios/portfolio/",
                params={"page": 1, "page_size": 10},
                response_model=PortfolioListResponse,
            )

            assert result.count == 2
            assert len(result.results) == 2
            assert result.results[0].name == "Test Portfolio 1"

    @pytest.mark.asyncio
    async def test_get_portfolio(self, client):
        """Test getting a specific portfolio."""
        mock_response = {
            "id": 1,
            "user_code": "PORT001",
            "name": "Test Portfolio",
            "short_name": "TP",
            "public_name": "Test Portfolio",
            "portfolio_type": 1,
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = Portfolio.model_validate(mock_response)

            result = await client.get_portfolio(1)

            mock_get.assert_called_once_with(
                endpoint="portfolios/portfolio/1/", response_model=Portfolio
            )

            assert result.id == 1
            assert result.name == "Test Portfolio"

    @pytest.mark.asyncio
    async def test_list_portfolios_light(self, client):
        """Test listing portfolios in light format."""
        mock_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "user_code": "PORT001",
                    "name": "Test Portfolio Light",
                    "short_name": "TPL",
                    "public_name": "Test Portfolio Light",
                }
            ],
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = PortfolioLightListResponse.model_validate(
                mock_response
            )

            result = await client.list_portfolios_light(ordering="name")

            mock_get.assert_called_once_with(
                endpoint="portfolios/portfolio/light/",
                params={"ordering": "name"},
                response_model=PortfolioLightListResponse,
            )

            assert result.count == 1
            assert result.results[0].name == "Test Portfolio Light"

    @pytest.mark.asyncio
    async def test_get_portfolio_attributes(self, client):
        """Test getting portfolio attributes."""
        mock_response = [
            {
                "id": 1,
                "attribute_type": "ATTR001",
                "value_string": "Test Value",
                "value_float": None,
                "value_date": None,
                "classifier": None,
            }
        ]

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_portfolio_attributes()

            mock_get.assert_called_once_with(
                endpoint="portfolios/portfolio/attributes/"
            )

            assert len(result) == 1
            assert isinstance(result[0], GenericAttribute)
            assert result[0].value_string == "Test Value"

    @pytest.mark.asyncio
    async def test_get_inception_date(self, client):
        """Test getting inception date."""
        mock_response = {"inception_date": "2023-01-01", "portfolio_id": 1}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_inception_date()

            mock_get.assert_called_once_with(
                endpoint="portfolios/portfolio/get-inception-date/"
            )

            assert result["inception_date"] == "2023-01-01"

    @pytest.mark.asyncio
    async def test_list_first_transaction_dates(self, client):
        """Test listing first transaction dates."""
        mock_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"portfolio": "PORT001", "date_field": "transaction_date"}],
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = FirstTransactionDateListResponse.model_validate(
                mock_response
            )

            result = await client.list_first_transaction_dates()

            mock_get.assert_called_once_with(
                endpoint="portfolios/first-transaction-date/",
                params={},
                response_model=FirstTransactionDateListResponse,
            )

            assert result.count == 1

    @pytest.mark.asyncio
    async def test_get_first_transaction_date(self, client):
        """Test getting first transaction date for a specific portfolio."""
        mock_response = {"portfolio": "PORT001", "date_field": "transaction_date"}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = FirstTransactionDateRequest.model_validate(
                mock_response
            )

            result = await client.get_first_transaction_date(1)

            mock_get.assert_called_once_with(
                endpoint="portfolios/first-transaction-date/1/",
                response_model=FirstTransactionDateRequest,
            )

            assert result.portfolio == "PORT001"
