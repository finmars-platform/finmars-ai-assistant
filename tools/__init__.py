"""
Finmars AI Assistant Tools Package

This package contains LangChain-compatible toolkits for interacting with the Finmars Portfolio API.
Each toolkit provides structured tools with input schemas optimized for LLM interactions.

Available Toolkits:
- PortfolioToolkit: Portfolio management operations
- PortfolioTypeToolkit: Portfolio type and attribute management
- PortfolioRegisterToolkit: Portfolio register operations
- PortfolioHistoryToolkit: Historical portfolio data access
- PortfolioReconcileToolkit: Portfolio reconciliation operations
- BalanceReportToolkit: Balance report with holdings and allocations
- PLReportToolkit: Profit & Loss report with investment performance analysis
- TransactionReportToolkit: Transaction report with detailed buy/sell transactions

Each toolkit follows the same pattern:
1. LLM-optimized input schemas (separate from API payload models)
2. Async toolkit methods that call the Finmars API client
3. LangChain StructuredTool builders for agent integration
4. Comprehensive error handling and user-friendly output formatting
"""

from .portfolio_toolkit import PortfolioToolkit, build_portfolio_tools
from .portfolio_type_toolkit import PortfolioTypeToolkit, build_portfolio_type_tools
from .portfolio_register_toolkit import (
    PortfolioRegisterToolkit,
    build_portfolio_register_tools,
)
from .portfolio_history_toolkit import (
    PortfolioHistoryToolkit,
    build_portfolio_history_tools,
)
from .portfolio_reconcile_toolkit import (
    PortfolioReconcileToolkit,
    build_portfolio_reconcile_tools,
)
from .balance_report_toolkit import (
    BalanceReportToolkit,
    build_balance_report_tools,
)
from .pl_report_toolkit import (
    PLReportToolkit,
    build_pl_report_tools,
)
from .transaction_report_toolkit import (
    TransactionReportToolkit,
    build_transaction_report_tools,
)

__all__ = [
    # Toolkit classes
    "PortfolioToolkit",
    "PortfolioTypeToolkit",
    "PortfolioRegisterToolkit",
    "PortfolioHistoryToolkit",
    "PortfolioReconcileToolkit",
    "BalanceReportToolkit",
    "PLReportToolkit",
    "TransactionReportToolkit",
    # Tool builder functions
    "build_portfolio_tools",
    "build_portfolio_type_tools",
    "build_portfolio_register_tools",
    "build_portfolio_history_tools",
    "build_portfolio_reconcile_tools",
    "build_balance_report_tools",
    "build_pl_report_tools",
    "build_transaction_report_tools",
]


def build_all_tools():
    """
    Build and return all available Finmars portfolio tools.

    Returns:
        List[BaseTool]: Complete list of all portfolio-related tools
    """
    tools = []
    tools.extend(build_portfolio_tools())
    tools.extend(build_portfolio_type_tools())
    tools.extend(build_portfolio_register_tools())
    tools.extend(build_portfolio_history_tools())
    tools.extend(build_portfolio_reconcile_tools())
    tools.extend(build_balance_report_tools())
    tools.extend(build_pl_report_tools())
    tools.extend(build_transaction_report_tools())
    return tools
