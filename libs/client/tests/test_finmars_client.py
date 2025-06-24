import os
import pytest

from ..finmars_client import FinmarsPortfolioClient
from ..portfolio import PortfolioClient
from ..portfolio_type import PortfolioTypeClient
from ..portfolio_register import PortfolioRegisterClient
from ..portfolio_history import PortfolioHistoryClient
from ..portfolio_reconcile import PortfolioReconcileClient


class TestFinmarsPortfolioClient:
    """Test cases for FinmarsPortfolioClient."""

    @pytest.fixture
    def client(self):
        return FinmarsPortfolioClient(
            base_url=os.getenv("FINMARS_BASE_URL"),
            realm="test_realm",
            space="test_space",
            api_key="test-api-key",
            timeout=30.0,
        )

    def test_init(self, client):
        """Test client initialization."""
        assert client.base_url == os.getenv("FINMARS_BASE_URL")
        assert client.realm == "test_realm"
        assert client.space == "test_space"
        assert client.api_key == "test-api-key"
        assert client.timeout == 30.0

    def test_sub_clients_initialization(self, client):
        """Test that all sub-clients are properly initialized."""
        assert isinstance(client.portfolios, PortfolioClient)
        assert isinstance(client.portfolio_types, PortfolioTypeClient)
        assert isinstance(client.portfolio_registers, PortfolioRegisterClient)
        assert isinstance(client.portfolio_history, PortfolioHistoryClient)
        assert isinstance(client.portfolio_reconcile, PortfolioReconcileClient)

    def test_sub_clients_configuration(self, client):
        """Test that sub-clients have correct configuration."""
        # Check portfolios client
        assert client.portfolios.base_url == os.getenv("FINMARS_BASE_URL")
        assert client.portfolios.realm == "test_realm"
        assert client.portfolios.space == "test_space"
        assert client.portfolios.api_key == "test-api-key"

        # Check portfolio_types client
        assert client.portfolio_types.base_url == os.getenv(
            "FINMARS_BASE_URL",
        )
        assert client.portfolio_types.realm == "test_realm"
        assert client.portfolio_types.space == "test_space"
        assert client.portfolio_types.api_key == "test-api-key"

    def test_repr(self, client):
        """Test string representation."""
        expected = f"FinmarsPortfolioClient(base_url='{os.getenv('FINMARS_BASE_URL', 'https://api.finmars.com')}', realm='test_realm', space='test_space')"
        assert repr(client) == expected

    def test_custom_configuration(self):
        """Test client with custom configuration."""
        client = FinmarsPortfolioClient(
            base_url="https://custom.finmars.com",
            realm="custom_realm",
            space="custom_space",
            api_key="custom-key",
            timeout=60.0,
        )

        assert client.base_url == "https://custom.finmars.com"
        assert client.realm == "custom_realm"
        assert client.space == "custom_space"
        assert client.api_key == "custom-key"
        assert client.timeout == 60.0

        # Verify sub-clients have same configuration
        assert client.portfolios.realm == "custom_realm"
        assert client.portfolios.space == "custom_space"
