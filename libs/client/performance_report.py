import json

from ..schema.via_data_model_codegen.report_schema import PerformanceReport
from .base import BaseHTTPClient

# Convert numeric fields to strings as expected by the model
STRING_FIELDS = [
    "bundle",
    "report_currency",
    "begin_nav",
    "end_nav",
    "grand_return",
    "grand_cash_flow_weighted",
    "grand_cash_flow",
    "grand_cash_inflow",
    "grand_cash_outflow",
    "grand_nav",
    "grand_absolute_pl",
]


class PerformanceReportClient(BaseHTTPClient):
    """Client for performance report operations."""

    async def create_performance_report(
        self, request_data: PerformanceReport
    ) -> PerformanceReport:
        """
        Create a performance report.

        Args:
            request_data: PerformanceReport model with all report parameters

        Returns:
            PerformanceReport response model
        """
        res: dict = await self.post(
            endpoint="reports/performance-report/",
            json_data=json.loads(request_data.model_dump_json(exclude_none=True)),
        )

        # Convert list fields back to strings if they exist
        if "registers" in res and res["registers"]:
            res["registers"] = [str(r) for r in res.get("registers", [])]

        for field in STRING_FIELDS:
            if field in res and res[field] is not None:
                res[field] = str(res[field])

        return PerformanceReport(**res)
