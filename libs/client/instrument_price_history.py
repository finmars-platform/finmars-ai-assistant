from typing import Optional, List, Union
from datetime import date, datetime
import re

from .base import BaseHTTPClient
from ..schema.base import PaginatedResponse
from ..schema.via_data_model_codegen.instrument_schema import PriceHistoryActual


def _date_to_str(d: Optional[Union[str, date, datetime]]) -> Optional[str]:
    if d is None:
        return None
    if isinstance(d, str):
        # Enforce strict YYYY-MM-DD format for strings
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            return d
        raise ValueError(
            "date_after/date_before must be in 'YYYY-MM-DD' format, e.g. '2022-11-30'."
        )
    if isinstance(d, datetime):
        return d.date().isoformat()
    return d.isoformat()


class PriceHistoryListResponse(PaginatedResponse):
    results: List[PriceHistoryActual]


class InstrumentPriceHistoryClient(BaseHTTPClient):
    """Client for instrument price history operations (GET only)."""

    async def list_price_history(
        self,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        # Filters
        id: Optional[int] = None,
        instrument: Optional[int] = None,
        pricing_policy: Optional[str] = None,
        date_after: Optional[Union[str, date, datetime]] = None,
        date_before: Optional[Union[str, date, datetime]] = None,
        principal_price_min: Optional[float] = None,
        principal_price_max: Optional[float] = None,
        accrued_price_min: Optional[float] = None,
        accrued_price_max: Optional[float] = None,
    ) -> PriceHistoryListResponse:
        """
        List instrument price history records.

        Args:
            ordering: Which field to use when ordering the results.
            page: A page number within the paginated result set.
            page_size: Number of results to return per page.
            id: Filter by record ID.
            instrument: Filter by instrument ID.
            pricing_policy: Filter by pricing policy user_code (string).
            date_after: Include records with `date` >= this value. Accepts `date`, `datetime`, or a string strictly formatted as "YYYY-MM-DD" (e.g., "2022-11-30").
            date_before: Include records with `date` <= this value. Accepts `date`, `datetime`, or a string strictly formatted as "YYYY-MM-DD" (e.g., "2022-11-30").
            principal_price_min: Minimum principal price filter.
            principal_price_max: Maximum principal price filter.
            accrued_price_min: Minimum accrued price filter.
            accrued_price_max: Maximum accrued price filter.

        Returns:
            PriceHistoryListResponse with paginated results.
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

        # Apply filters if provided
        if id is not None:
            params["id"] = id

        if instrument is not None:
            params["instrument"] = instrument

        if pricing_policy:
            params["pricing_policy"] = pricing_policy

        d_after = _date_to_str(date_after)
        if d_after:
            params["date_after"] = d_after

        d_before = _date_to_str(date_before)
        if d_before:
            params["date_before"] = d_before

        if principal_price_min is not None:
            params["principal_price_min"] = principal_price_min

        if principal_price_max is not None:
            params["principal_price_max"] = principal_price_max

        if accrued_price_min is not None:
            params["accrued_price_min"] = accrued_price_min

        if accrued_price_max is not None:
            params["accrued_price_max"] = accrued_price_max

        return await self.get(
            endpoint="instruments/price-history/",
            params=params,
            response_model=PriceHistoryListResponse,
        )
