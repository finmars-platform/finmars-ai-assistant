import json
from typing import Optional

from ..schema.via_data_model_codegen.report_schema import PriceHistoryCheckItems
from .base import BaseHTTPClient


class PriceHistoryCheckClient(BaseHTTPClient):
    """Client for price history check operations."""

    async def check_price_history(
        self, request_data: PriceHistoryCheckItems
    ) -> PriceHistoryCheckItems:
        """
        Check price history for instruments.

        Args:
            request_data: PriceHistoryCheckItems model with report parameters

        Returns:
            PriceHistoryCheckItems response model with missing pricing history items
        """
        res: dict = await self.post(
            endpoint="reports/price-history-check/",
            json_data=json.loads(request_data.model_dump_json(exclude_none=True)),
        )
        return PriceHistoryCheckItems(**res)