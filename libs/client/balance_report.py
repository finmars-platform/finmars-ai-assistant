import json
from typing import Optional

from ..schema.via_data_model_codegen.report_schema import BackendBalanceReportItems
from .base import BaseHTTPClient


class BalanceReportClient(BaseHTTPClient):
    """Client for balance report operations."""

    async def get_balance_report_items(
        self,
        request_data: BackendBalanceReportItems
    ) -> BackendBalanceReportItems:
        """
        Get balance report items.
        
        Args:
            request_data: BackendBalanceReportItems model with all report parameters
            
        Returns:
            BackendBalanceReportItems response model
        """
        res: dict = await self.post(
            endpoint="reports/backend-balance-report/items/",
            json_data=json.loads(request_data.model_dump_json(exclude_none=True)),
        )
        res["accounts"] = [str(a) for a in res.get("accounts", [])]
        res["portfolios"] = [str(a) for a in res.get("portfolios", [])]
        res["accounts_position"] = [str(a) for a in res.get("accounts_position", [])]
        res["accounts_cash"] = [str(a) for a in res.get("accounts_cash", [])]
        res["strategies1"] = [str(a) for a in res.get("strategies1", [])]
        res["strategies2"] = [str(a) for a in res.get("strategies2", [])]
        res["strategies2"] = [str(a) for a in res.get("strategies2", [])]
        res["strategies3"] = [str(a) for a in res.get("strategies3", [])]
        return BackendBalanceReportItems(**res)