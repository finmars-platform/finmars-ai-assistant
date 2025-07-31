import asyncio
import json
import traceback
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool

from libs.client.finmars_client import FinmarsPortfolioClient
from libs.logger.logger import logger
from libs.schema.via_data_model_codegen.report_schema import TransactionReportItems
from .shared_models import (
    TransactionReportSortBy as SortBy,
    drop_empty_fields,
)


class GetTransactionReportSchema(BaseModel):
    """Input schema for getting transaction report"""

    portfolio_code: str = Field(
        description="The portfolio user code (user_code from portfolio)"
    )
    begin_date: str = Field(
        description="Mandatory field. The start date for transactions in YYYY-MM-DD format (e.g., '2024-01-01'). If not provided, all transactions from the beginning will be included.",
    )
    end_date: str = Field(
        description="Mandatory field. The end date for transactions in YYYY-MM-DD format (e.g., '2024-12-31')"
    )
    sort_by: Optional[SortBy] = Field(
        default=None,
        description="Sort transactions by transaction_date, instrument_name, position_size, principal, or trade_price",
    )
    descending: bool = Field(
        default=True,
        description="Sort in descending order (newest/highest first). Set to false for ascending order.",
    )
    page: int = Field(
        default=1,
        description="Page number for pagination (starts from 1)",
    )
    page_size: int = Field(
        default=100,
        description="Number of transactions per page (max 500)",
    )


class TransactionReportToolkit:
    """Toolkit for transaction report operations using the Finmars API"""

    def __init__(self):
        self.client = FinmarsPortfolioClient()

    async def _get_transaction_report(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get transaction report with detailed transaction information"""
        try:
            schema = GetTransactionReportSchema(**kwargs)

            # Pre-process: Build the request according to requirements
            # Parse dates
            if schema.begin_date:
                try:
                    begin_date = datetime.strptime(
                        schema.begin_date, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    return (
                        f"Error: Invalid begin_date format. Please use YYYY-MM-DD format (e.g., '2024-01-01')",
                        None,
                    )
            else:
                begin_date = None

            try:
                end_date = datetime.strptime(schema.end_date, "%Y-%m-%d").date()
            except ValueError:
                return (
                    f"Error: Invalid end_date format. Please use YYYY-MM-DD format (e.g., '2024-12-31')",
                    None,
                )

            # Build request
            request_data = TransactionReportItems(
                begin_date=begin_date,
                end_date=end_date,
                portfolios=[schema.portfolio_code],
                page=schema.page,
                page_size=min(schema.page_size, 500),  # Ensure max 500
                date_field="transaction_date",
                depth_level="entry",
                expression_iterations_count=1,
            )
            input_str = request_data.model_dump_json()

            # Make the API call
            result: TransactionReportItems = (
                await self.client.transaction_report.create_transaction_report(
                    request_data
                )
            )

            # Create artifacts
            request_dict = json.loads(request_data.model_dump_json())
            cleaned_request = drop_empty_fields(request_dict)
            response_dict = json.loads(result.model_dump_json())

            # Create the artifact in the required format
            artifact = {"request_data": cleaned_request, "response_data": response_dict}

            # Post-process: Extract the required information
            items = result.items if hasattr(result, "items") else []

            # If items is a string (JSON), parse it
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except:
                    return f"Error: Could not parse items from response", None

            # Extract transaction information
            output = f"The FULL request to get Transaction Report was: {input_str}\n\n\n"
            output += f"RESPONSE:\nTransaction Report for Portfolio: {schema.portfolio_code}\n"
            output += f"Period: {begin_date or 'Beginning'} to {end_date}\n"
            output += f"Page: {schema.page} (Page size: {schema.page_size})\n\n"

            if not items:
                output += "No transactions found for the specified criteria.\n"
                return output, artifact

            output += "Transaction Details:\n"
            output += "=" * 120 + "\n\n"

            transactions = []

            # Process each transaction
            for item in items:
                if isinstance(item, dict):
                    # Extract key transaction fields
                    transaction_id = item.get("id", "")
                    transaction_code = item.get("transaction_code", "")
                    transaction_class = item.get("transaction_class.name", "")
                    transaction_date = item.get("transaction_date", "")
                    accounting_date = item.get("accounting_date", "")
                    cash_date = item.get("cash_date", "")

                    # Extract instrument information
                    instrument_code = item.get("instrument.user_code") or item.get(
                        "transaction_item_user_code"
                    )
                    instrument_name = item.get("instrument.name") or item.get(
                        "transaction_item_name"
                    )
                    instrument_country = item.get("instrument.country.name", "")
                    instrument_currency = None
                    if "instrument.pricing_currency.user_code" in item:
                        instrument_currency = item.get(
                            "instrument.pricing_currency.user_code"
                        )

                    # Extract transaction amounts
                    position_size = item.get("position_size_with_sign", 0)
                    principal = item.get("principal_with_sign", 0)
                    trade_price = item.get("trade_price", 0)
                    cash_consideration = item.get("cash_consideration", 0)

                    # Extract additional details
                    portfolio_code = item.get(
                        "portfolio.user_code", schema.portfolio_code
                    )
                    account_cash = item.get("account_cash.user_code", "")
                    account_position = item.get("account_position.user_code", "")
                    complex_transaction_text = item.get("complex_transaction.text", "")
                    complex_transaction_code = item.get(
                        "complex_transaction.transaction_unique_code", ""
                    )

                    transaction_data = {
                        "id": transaction_id,
                        "code": transaction_code,
                        "class": transaction_class,
                        "date": transaction_date,
                        "instrument_code": instrument_code,
                        "instrument_name": instrument_name,
                        "instrument_country": instrument_country,
                        "instrument_currency": instrument_currency,
                        "position_size": position_size,
                        "principal": principal,
                        "trade_price": trade_price,
                        "cash_consideration": cash_consideration,
                        "portfolio_code": portfolio_code,
                        "account_cash": account_cash,
                        "account_position": account_position,
                        "complex_transaction_text": complex_transaction_text,
                        "complex_transaction_code": complex_transaction_code,
                        "accounting_date": accounting_date,
                        "cash_date": cash_date,
                    }

                    transactions.append(transaction_data)

            # Sort transactions if requested
            if schema.sort_by:

                def sort_key(trans):
                    if schema.sort_by == SortBy.TRANSACTION_DATE:
                        return trans["date"]
                    elif schema.sort_by == SortBy.INSTRUMENT_NAME:
                        return (trans["instrument_name"] or "").lower()
                    elif schema.sort_by == SortBy.POSITION_SIZE:
                        return (
                            abs(trans["position_size"])
                            if isinstance(trans["position_size"], (int, float))
                            else 0
                        )
                    elif schema.sort_by == SortBy.PRINCIPAL:
                        return (
                            abs(trans["principal"])
                            if isinstance(trans["principal"], (int, float))
                            else 0
                        )
                    elif schema.sort_by == SortBy.TRADE_PRICE:
                        return (
                            trans["trade_price"]
                            if isinstance(trans["trade_price"], (int, float))
                            else 0
                        )
                    return 0

                transactions.sort(
                    key=sort_key,
                    reverse=(
                        schema.descending
                        if schema.sort_by != SortBy.INSTRUMENT_NAME
                        else not schema.descending
                    ),
                )

                # Add sorting info to output
                output += f"Sorted by: {schema.sort_by.value} ({'descending' if schema.descending else 'ascending'})\n"
                output += "=" * 120 + "\n\n"

            # Display each transaction
            for trans in transactions:
                output += f"Transaction ID: {trans['id']}\n"
                output += f"Date: {trans['date']}\n"
                output += f"Type: {trans['class']} (Code: {trans['code']})\n"

                if trans["instrument_name"]:
                    output += f"Instrument: {trans['instrument_name']}\n"
                    if trans["instrument_code"]:
                        output += f"Instrument Code: {trans['instrument_code']}\n"
                    if trans["instrument_country"]:
                        output += f"Instrument Country: {trans['instrument_country']}\n"
                    if trans["instrument_currency"]:
                        output += f"Instrument Currency: {trans['instrument_currency']}\n"

                # Transaction details
                if trans["position_size"] != 0:
                    # Format position size with decimals only if needed
                    if trans["position_size"] == int(trans["position_size"]):
                        output += f"Position Size: {int(trans['position_size']):,} units"
                    else:
                        output += f"Position Size: {trans['position_size']:,.6f} units".rstrip('0').rstrip('.')
                    if trans["position_size"] > 0:
                        output += " (Buy/Long)\n"
                    else:
                        output += " (Sell/Short)\n"

                if trans["trade_price"] != 0:
                    output += f"Trade Price: {trans['trade_price']:,.2f}\n"

                if trans["principal"] != 0:
                    output += f"Principal Value: {trans['principal']:,.2f}"
                    if trans["principal"] < 0:
                        output += " (Outflow)\n"
                    else:
                        output += " (Inflow)\n"

                if trans["cash_consideration"] != 0:
                    output += f"Cash Consideration: {trans['cash_consideration']:,.2f}\n"

                # Account information
                if trans["account_cash"]:
                    output += f"Cash Account: {trans['account_cash']}\n"
                if trans["account_position"]:
                    output += f"Position Account: {trans['account_position']}\n"

                # Complex transaction details
                if trans["complex_transaction_text"]:
                    output += f"Description: {trans['complex_transaction_text']}\n"
                if trans["complex_transaction_code"]:
                    output += f"Transaction Code: {trans['complex_transaction_code']}\n"

                output += "-" * 80 + "\n\n"

            # Summary statistics
            output += "=" * 120 + "\n"
            output += "TRANSACTION SUMMARY:\n"
            output += f"Total Transactions: {len(transactions)}\n"

            # Additional pagination info
            if result.count and result.count > len(items):
                total_pages = (result.count + schema.page_size - 1) // schema.page_size
                output += f"\nPagination Info:\n"
                output += f"- Total Records: {result.count}\n"
                output += f"- Current Page: {schema.page} of {total_pages}\n"
                output += f"- Records on this page: {len(items)}\n"

            return output, artifact

        except Exception as e:
            exc = traceback.format_exc()
            logger.error(exc)
            error_msg = f"Error getting transaction report for portfolio {kwargs.get('portfolio_code')}: {str(e)}"
            if 'input_str' in locals():
                error_msg += f"\n\nFull request sent:\n{input_str}"
            return (error_msg, None)


def build_transaction_report_tools() -> List[BaseTool]:
    """Build and return transaction report tools"""
    toolkit = TransactionReportToolkit()

    tools = [
        StructuredTool.from_function(
            name="get_transaction_report",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_transaction_report(**kwargs)
            ),
            coroutine=toolkit._get_transaction_report,
            description=(
                "Get a detailed transaction report for a portfolio showing all transactions. "
                "Use this tool to:\n"
                "- View all transactions in a portfolio for a specific period\n"
                "- Track transaction activity with prices and quantities\n"
                "- Analyze transaction patterns and timing\n"
                "- Export transaction history for tax or audit purposes\n"
                "\n"
                "The report includes:\n"
                "- Transaction dates and types\n"
                "- Instrument details (name, code, currency)\n"
                "- Position sizes (number of shares/bonds/units)\n"
                "- Trade prices and principal values\n"
                "- Account information\n"
                "- Complex transaction descriptions\n"
                "\n"
                "Key fields explained:\n"
                "- position_size_with_sign: Number of shares/bonds/units (positive or negative based on transaction direction)\n"
                "- principal_with_sign: Transaction value\n"
                "- trade_price: Price per unit at transaction time\n"
                "- transaction_date: Date when the transaction occurred\n"
                "\n"
                "Example questions this tool can answer:\n"
                "- What are all transactions for portfolio X in 2024?\n"
                "- What transactions occurred in January 2024?\n"
                "- Show me the most recent transactions\n"
                "- What are the transactions of a certain instrument in a certain portfolio in a period\n"
                "- All transactions in a portfolio for a certain period\n"
                "\n"
                "Pagination:\n"
                "- Use page and page_size parameters to navigate large transaction lists\n"
                "- Default page_size is 100, maximum is 500\n"
                "- Results can be sorted by date, instrument name, position size, principal, or trade price"
            ),
            args_schema=GetTransactionReportSchema,
            response_format="content_and_artifact",
        ),
    ]

    return tools