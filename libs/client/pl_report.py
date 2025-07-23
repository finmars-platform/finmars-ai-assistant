import json
from typing import Optional, List

from ..schema.via_data_model_codegen.report_schema import PLReport, PLReportItems
from .base import BaseHTTPClient


class PLReportClient(BaseHTTPClient):
    """Client for PL report operations."""

    async def create_pl_report(self, request_data: PLReportItems) -> PLReportItems:
        """
        Create a PL report.

        Args:
            request_data: PLReportItems model with all report parameters

        Returns:
            PLReportItems response model
        """
        res: dict = await self.post(
            endpoint="reports/pl-report/",
            json_data=json.loads(request_data.model_dump_json(exclude_none=True)),
        )
        res["portfolios"] = [str(a) for a in res.get("portfolios", [])]
        return PLReportItems(**res)

    # async def list_pl_report_attributes(self) -> List[PLReportItems]:
    #     """
    #     List PL report attributes.
    #
    #     Returns:
    #         List of PLReportItems objects
    #     """
    #     res: List[dict] = await self.get(
    #         endpoint="reports/pl-report/attributes/"
    #     )
    #     return [PLReportItems(**item) for item in res]
