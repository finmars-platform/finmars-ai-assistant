import asyncio
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

    async def list_grouped_by_instrument(
        self,
        begin_date: str,
        end_date: str,
        instrument_id: int,
        pricing_policy_user_code: Optional[str] = None,
        page_size: int = 200,
        only_first_page: bool = True,
    ) -> dict:
        """
        Fetch price history via GET with pagination and return grouped by instrument.

        Input:
        - begin_date: YYYY-MM-DD inclusive
        - end_date: YYYY-MM-DD inclusive
        - instrument_id: target instrument id
        - pricing_policy_user_code: optional user_code filter (exact/contains depending on API)
        - page_size: page size to use when traversing pagination (default 200)
        - only_first_page: if True, return only the first page (default True)

        Output structure:
        {
          "grouped_by_instrument": {
            <instrument_id>: {
              "instrument_public_name": <str|None>,
              "pricing_policy_user_code": <str|None>,
              "count": <int>,
              "items": [
                {
                  "date": "YYYY-MM-DD",
                  "principal_price": <float|None>,
                  "accrued_price": <float|None>
                }, ...
              ]
            }
          }
        }
        """
        page = 1
        total = 0
        all_items: list[PriceHistoryActual] = []

        while True:
            resp = await self.list_price_history(
                ordering="date",
                page=page,
                page_size=page_size,
                instrument=instrument_id,
                pricing_policy=pricing_policy_user_code,
                date_after=begin_date,
                date_before=end_date,
            )

            items = resp.results or []
            all_items.extend(items)
            total = resp.count or total
            if only_first_page or not resp.next:
                break
            page += 1

        grouped: dict[int, dict] = {}

        for it in all_items:
            inst_id = it.instrument
            inst_public_name = None
            if getattr(it, "instrument_object", None):
                inst_public_name = getattr(it.instrument_object, "public_name", None)

            pp_user_code = None
            if getattr(it, "pricing_policy_object", None):
                pp_user_code = getattr(it.pricing_policy_object, "user_code", None)

            if inst_id not in grouped:
                grouped[inst_id] = {
                    "instrument_public_name": inst_public_name,
                    "pricing_policy_user_code": (
                        pp_user_code
                        if pp_user_code is not None
                        else pricing_policy_user_code
                    ),
                    "count": 0,
                    "items": [],
                }
            else:
                # If group exists but pricing policy is still None, hydrate from record
                if (
                    grouped[inst_id].get("pricing_policy_user_code") is None
                    and pp_user_code is not None
                ):
                    grouped[inst_id]["pricing_policy_user_code"] = pp_user_code

            grouped[inst_id]["items"].append(
                {
                    "date": str(getattr(it, "date", "")),
                    "principal_price": getattr(it, "principal_price", None),
                    "accrued_price": getattr(it, "accrued_price", None),
                }
            )

        for g in grouped.values():
            g["items"].sort(key=lambda x: x.get("date") or "")
            # total number of matching records for this instrument (across API pages)
            g["count"] = total

        return {"grouped_by_instrument": grouped}

    async def list_grouped_by_instruments(
        self,
        begin_date: str,
        end_date: str,
        instrument_ids: list[int],
        pricing_policy_user_code: Optional[str] = None,
        page_size: int = 200,
        only_first_page: bool = True,
    ) -> dict:
        """
        Fetch price history for multiple instruments concurrently and group results by instrument.

        Args:
            begin_date: Start date (YYYY-MM-DD, inclusive).
            end_date: End date (YYYY-MM-DD, inclusive).
            instrument_ids: List of instrument IDs to fetch.
            pricing_policy_user_code: Optional pricing policy filter.
            page_size: Page size for each paginated fetch.
            only_first_page: if True, return only the first page per instrument (default True).

        Returns:
            Dict with grouped_by_instrument mapping where each instrument has its own count.
        """
        # Deduplicate instrument IDs while preserving order
        seen = set()
        unique_ids: list[int] = []
        for iid in instrument_ids:
            if iid not in seen:
                unique_ids.append(iid)
                seen.add(iid)

        tasks = [
            self.list_grouped_by_instrument(
                begin_date=begin_date,
                end_date=end_date,
                instrument_id=iid,
                pricing_policy_user_code=pricing_policy_user_code,
                page_size=page_size,
                only_first_page=only_first_page,
            )
            for iid in unique_ids
        ]

        results = await asyncio.gather(*tasks)

        grouped: dict[int, dict] = {}

        for res in results:
            sub = res.get("grouped_by_instrument", {}) or {}
            for inst_key, group in sub.items():
                # inst_key may be int or str depending on serialization path
                try:
                    inst_id = int(inst_key)
                except Exception:
                    inst_id = inst_key

                if inst_id not in grouped:
                    grouped[inst_id] = group
                else:
                    # Merge items if the same instrument appears more than once
                    existing = grouped[inst_id]
                    if (
                        existing.get("pricing_policy_user_code") is None
                        and group.get("pricing_policy_user_code") is not None
                    ):
                        existing["pricing_policy_user_code"] = group.get(
                            "pricing_policy_user_code"
                        )

                    # Merge count (prefer larger total if differs)
                    try:
                        existing_count = int(existing.get("count", 0) or 0)
                        group_count = int(group.get("count", 0) or 0)
                        existing["count"] = max(existing_count, group_count)
                    except Exception:
                        existing["count"] = group.get("count", existing.get("count"))

                    # Extend items and resort by date
                    existing_items = existing.get("items", [])
                    new_items = group.get("items", [])
                    existing_items.extend(new_items)
                    existing_items.sort(key=lambda x: x.get("date") or "")
                    existing["items"] = existing_items

        return {"grouped_by_instrument": grouped}
