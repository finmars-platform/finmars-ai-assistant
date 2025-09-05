from typing import Optional

from .base import BaseHTTPClient
from .portfolio import PortfolioClient
from .portfolio_type import PortfolioTypeClient
from .portfolio_register import PortfolioRegisterClient
from .portfolio_history import PortfolioHistoryClient
from .portfolio_reconcile import PortfolioReconcileClient
from .balance_report import BalanceReportClient
from .pl_report import PLReportClient
from .performance_report import PerformanceReportClient
from .transaction_report import TransactionReportClient
from .price_history_check import PriceHistoryCheckClient
from .instrument_price_history import InstrumentPriceHistoryClient


class FinmarsPortfolioClient:
    """
    Main Finmars Portfolio API client that aggregates all sub-clients.

    This client provides access to all portfolio-related endpoints through
    organized sub-clients based on business logic.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        realm: Optional[str] = None,
        space: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the Finmars Portfolio Client.

        Args:
            base_url: The base URL of the Finmars API
            realm: The realm code
            space: The space code
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds (default: 30.0)
        """
        # Base configuration
        self.base_url = base_url
        self.realm = realm
        self.space = space
        self.api_key = api_key
        self.timeout = timeout

        # Initialize sub-clients
        self.portfolios = PortfolioClient(
            base_url=base_url,
            realm=realm,
            space=space,
            api_key=api_key,
            timeout=timeout,
        )

        self.portfolio_types = PortfolioTypeClient(
            base_url=base_url,
            realm=realm,
            space=space,
            api_key=api_key,
            timeout=timeout,
        )

        self.portfolio_registers = PortfolioRegisterClient(
            base_url=base_url,
            realm=realm,
            space=space,
            api_key=api_key,
            timeout=timeout,
        )

        self.portfolio_history = PortfolioHistoryClient(
            base_url=base_url,
            realm=realm,
            space=space,
            api_key=api_key,
            timeout=timeout,
        )

        self.portfolio_reconcile = PortfolioReconcileClient(
            base_url=base_url,
            realm=realm,
            space=space,
            api_key=api_key,
            timeout=timeout,
        )

        self.balance_report = BalanceReportClient(
            base_url=base_url,
            realm=realm,
            space=space,
            api_key=api_key,
            timeout=timeout,
        )

        self.pl_report = PLReportClient(
            base_url=base_url,
            realm=realm,
            space=space,
            api_key=api_key,
            timeout=timeout,
        )

        self.performance_report = PerformanceReportClient(
            base_url=base_url,
            realm=realm,
            space=space,
            api_key=api_key,
            timeout=timeout,
        )

        self.transaction_report = TransactionReportClient(
            base_url=base_url,
            realm=realm,
            space=space,
            api_key=api_key,
            timeout=timeout,
        )

        self.price_history_check = PriceHistoryCheckClient(
            base_url=base_url,
            realm=realm,
            space=space,
            api_key=api_key,
            timeout=timeout,
        )

        self.instrument_price_history = InstrumentPriceHistoryClient(
            base_url=base_url,
            realm=realm,
            space=space,
            api_key=api_key,
            timeout=timeout,
        )

    def __repr__(self) -> str:
        return f"FinmarsPortfolioClient(base_url='{self.base_url}', realm='{self.realm}', space='{self.space}')"
