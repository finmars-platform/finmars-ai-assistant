"""
Shared Pydantic models and enums for Finmars toolkit operations.

This module contains common models that are used across multiple toolkit files
to avoid duplication and ensure consistency.
"""

from enum import Enum
from typing import Optional, Any, Dict, List, Union
from pydantic import BaseModel, Field


class ReportCurrency(str, Enum):
    """Supported report currencies for balance and P/L reports"""

    USD = "USD"
    EUR = "EUR"


class OrderingField(BaseModel):
    """Common ordering field used across listing operations"""

    ordering: Optional[str] = Field(
        default=None,
        description=(
            "Sort order for results. Use field name for ascending order, "
            "'-field_name' for descending order (e.g., 'name' or '-created_at')"
        ),
    )


class PaginationFields(BaseModel):
    """Common pagination fields for list operations"""

    page: Optional[int] = Field(
        default=1, ge=1, description="Page number for pagination (default: 1)"
    )
    page_size: Optional[int] = Field(
        default=50,
        ge=1,
        le=1000,
        description="Number of items per page (default: 50, max: 1000)",
    )


class ListingSchema(OrderingField, PaginationFields):
    """Base schema for listing operations with ordering and pagination"""

    pass


# Sorting enums specific to each report type (kept separate as they differ)
class BalanceReportSortBy(str, Enum):
    """Sorting options for the balance report"""

    POSITION_SIZE = "position_size"
    MARKET_VALUE = "market_value"
    EXPOSURE = "exposure"
    NAME = "name"


class PLReportSortBy(str, Enum):
    """Sorting options for the P/L report"""

    INSTRUMENT_NAME = "instrument_name"
    POSITION_SIZE = "position_size"
    AMOUNT_INVESTED = "amount_invested"
    MARKET_VALUE = "market_value"
    PRINCIPLE = "principle"
    TOTAL_PL = "total_pl"  # Total P/L amount


class TransactionReportSortBy(str, Enum):
    """Sorting options for the transaction report"""

    TRANSACTION_DATE = "transaction_date"
    INSTRUMENT_NAME = "instrument_name"
    POSITION_SIZE = "position_size"
    PRINCIPAL = "principal"
    TRADE_PRICE = "trade_price"


# Common date field patterns
class DateRangeFields(BaseModel):
    """Common date range fields for reports"""

    start_date: str = Field(
        description="Start date in YYYY-MM-DD format (e.g., '2024-01-01')"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date in YYYY-MM-DD format (e.g., '2024-12-31'). If not provided, today's date will be used.",
    )


def drop_empty_fields(
    data: Union[Dict[str, Any], List, Any],
) -> Union[Dict[str, Any], List, Any]:
    """
    Recursively drop empty fields from a dictionary or list.

    Empty fields are:
    - None values
    - Empty lists []
    - Empty strings ""
    - Empty dicts {}

    Note: The value 0 (zero) is NOT considered empty and will be kept.

    Args:
        data: The data structure to clean

    Returns:
        The cleaned data structure with empty fields removed
    """
    if isinstance(data, dict):
        return {
            k: drop_empty_fields(v)
            for k, v in data.items()
            if v is not None and v != [] and v != "" and v != {}
        }
    elif isinstance(data, list):
        return [drop_empty_fields(item) for item in data]
    else:
        return data
