import json
from typing import Optional, List
from collections.abc import Iterable

from ..schema.via_data_model_codegen.report_schema import TransactionReportItems
from .base import BaseHTTPClient


class TransactionReportClient(BaseHTTPClient):
    """Client for transaction report operations."""

    async def create_transaction_report(
        self, request_data: TransactionReportItems
    ) -> TransactionReportItems:
        """
        Create a transaction report.

        Args:
            request_data: TransactionReportItems model with all report parameters

        Returns:
            TransactionReportItems response model
        """
        res: dict = await self.post(
            endpoint="reports/transaction-report/",
            json_data=json.loads(request_data.model_dump_json(exclude_none=True)),
        )
        # Convert list fields back to strings if they exist
        res["portfolios"] = [str(a) for a in res.get("portfolios", [])]
        res["accounts"] = [str(a) for a in res.get("accounts", [])]
        res["accounts_position"] = [str(a) for a in res.get("accounts_position", [])]
        res["accounts_cash"] = [str(a) for a in res.get("accounts_cash", [])]
        res["strategies1"] = [str(a) for a in res.get("strategies1", [])]
        res["strategies2"] = [str(a) for a in res.get("strategies2", [])]
        res["strategies3"] = [str(a) for a in res.get("strategies3", [])]

        # Fix type conversions for accounts_object
        if (
            "accounts_object" in res
            and isinstance(res["accounts_object"], Iterable)
            and not isinstance(res["accounts_object"], (str, bytes))
        ):
            for account in res["accounts_object"]:
                if (
                    isinstance(account, dict)
                    and "type" in account
                    and isinstance(account["type"], int)
                ):
                    account["type"] = str(account["type"])

        # Fix type conversions for accounts_position_object
        if (
            "accounts_position_object" in res
            and isinstance(res["accounts_position_object"], Iterable)
            and not isinstance(res["accounts_position_object"], (str, bytes))
        ):
            for account in res["accounts_position_object"]:
                if (
                    isinstance(account, dict)
                    and "type" in account
                    and isinstance(account["type"], int)
                ):
                    account["type"] = str(account["type"])

        # Fix type conversions for accounts_cash_object
        if (
            "accounts_cash_object" in res
            and isinstance(res["accounts_cash_object"], Iterable)
            and not isinstance(res["accounts_cash_object"], (str, bytes))
        ):
            for account in res["accounts_cash_object"]:
                if (
                    isinstance(account, dict)
                    and "type" in account
                    and isinstance(account["type"], int)
                ):
                    account["type"] = str(account["type"])

        # Fix empty strings for item_instruments reference_for_pricing
        if (
            "item_instruments" in res
            and isinstance(res["item_instruments"], Iterable)
            and not isinstance(res["item_instruments"], (str, bytes))
        ):
            for instrument in res["item_instruments"]:
                if (
                    isinstance(instrument, dict)
                    and "reference_for_pricing" in instrument
                    and instrument["reference_for_pricing"] == ""
                ):
                    instrument["reference_for_pricing"] = None

        # Fix type conversions for item_responsibles
        if (
            "item_responsibles" in res
            and isinstance(res["item_responsibles"], Iterable)
            and not isinstance(res["item_responsibles"], (str, bytes))
        ):
            for responsible in res["item_responsibles"]:
                if (
                    isinstance(responsible, dict)
                    and "group" in responsible
                    and isinstance(responsible["group"], int)
                ):
                    responsible["group"] = str(responsible["group"])

        # Fix type conversions for item_counterparties
        if (
            "item_counterparties" in res
            and isinstance(res["item_counterparties"], Iterable)
            and not isinstance(res["item_counterparties"], (str, bytes))
        ):
            for counterparty in res["item_counterparties"]:
                if (
                    isinstance(counterparty, dict)
                    and "group" in counterparty
                    and isinstance(counterparty["group"], int)
                ):
                    counterparty["group"] = str(counterparty["group"])

        return TransactionReportItems(**res)
