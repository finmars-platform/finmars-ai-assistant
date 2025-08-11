import asyncio
import json
import traceback
from datetime import datetime
from typing import List, Optional

from langchain_core.tools import StructuredTool, BaseTool
from pydantic import BaseModel, Field

from libs.client.finmars_client import FinmarsPortfolioClient
from libs.logger.logger import logger
from libs.schema.via_data_model_codegen.report_schema import (
    PLReportItems,
    PriceHistoryCheckItems,
)
from .shared_models import ReportCurrency, PLReportSortBy as SortBy, drop_empty_fields


class GetPLReportSchema(BaseModel):
    """Input schema for getting P/L report"""

    portfolio_code: str = Field(
        description="The portfolio user code (user_code from portfolio)"
    )
    report_currency: ReportCurrency = Field(
        default=ReportCurrency.USD,
        description="The currency for the report",
    )
    pl_first_date: str = Field(
        description="The start date for P/L calculation in YYYY-MM-DD format (e.g., '2024-01-01')"
    )
    report_date: Optional[str] = Field(
        default=None,
        description="The end date for P/L calculation in YYYY-MM-DD format (e.g., '2024-12-31'). If not provided, today's date will be used.",
    )
    sort_by: Optional[SortBy] = Field(
        default=None,
        description="Sort results by instrument_name, position_size, amount_invested, market_value, principle, or total_pl",
    )
    descending: bool = Field(
        default=True,
        description="Sort in descending order (highest to lowest). Set to false for ascending order.",
    )
    page: int = Field(
        default=1,
        description="Page number for pagination (starts from 1)",
    )
    page_size: int = Field(
        default=500,
        description="Number of items per page (default: 500, max: 1000)",
    )
    # Return percentage filters removed - not applicable for individual instruments
    # Only portfolio-level return percentage is calculated


class PLReportToolkit:
    """Toolkit for P/L report operations using the Finmars API"""

    def __init__(self):
        self.client = FinmarsPortfolioClient()

    async def _get_pl_report(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get P/L report with profit and loss information"""
        try:
            schema = GetPLReportSchema(**kwargs)

            # Pre-process: Build the request according to requirements
            # Parse dates
            try:
                pl_first_date = datetime.strptime(
                    schema.pl_first_date, "%Y-%m-%d"
                ).date()
            except ValueError:
                return (
                    f"Error: Invalid pl_first_date format. Please use YYYY-MM-DD format (e.g., '2024-01-01')",
                    None,
                )

            if schema.report_date:
                try:
                    report_date = datetime.strptime(
                        schema.report_date, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    return (
                        f"Error: Invalid report_date format. Please use YYYY-MM-DD format (e.g., '2024-12-31')",
                        None,
                    )
            else:
                report_date = datetime.now().date()

            request_data = PLReportItems(
                account_mode=1,
                accounts=[],
                accounts_cash=[],
                accounts_position=[],
                allocation_mode=0,
                calculation_group="portfolio.id",
                cost_method=1,
                custom_fields_to_calculate="",
                date_field="transaction_date",
                expression_iterations_count=1,
                pl_first_date=pl_first_date,
                portfolio_mode=1,
                portfolios=[schema.portfolio_code],
                pricing_policy="com.finmars.standard-pricing:standard",
                report_currency=schema.report_currency.value,
                report_date=report_date,
                report_type=1,
                strategies1=[],
                strategies2=[],
                strategies3=[],
                strategy1_mode=0,
                strategy2_mode=0,
                strategy3_mode=0,
                page=schema.page,
                page_size=min(schema.page_size, 1000),  # Ensure max 1000
                report_instance_id=None,
                custom_fields=[1, 2],
            )
            input_str = request_data.model_dump_json()

            # Make the API call
            result: PLReportItems = await self.client.pl_report.create_pl_report(
                request_data
            )

            # Create artifacts
            request_dict = json.loads(request_data.model_dump_json())
            cleaned_request = drop_empty_fields(request_dict)
            response_dict = json.loads(result.model_dump_json())

            # Create the artifact in the required format
            artifact = {"request_data": cleaned_request, "response_data": response_dict}

            report_currency = result.report_currency

            # Post-process: Extract the required information
            items = result.items if hasattr(result, "items") else []

            # If items is a string (JSON), parse it
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except:
                    return f"Error: Could not parse items from response", None

            # Extract portfolio information
            output = f"The FULL request to get P/L Report was: {input_str}\n\n\n"
            output += f"RESPONSE:\nProfit & Loss Report for Portfolio: {schema.portfolio_code}\n"
            output += f"Period: {pl_first_date} to {report_date}\n"
            output += f"Currency: {report_currency}\n"
            output += f"Pricing Policy: {request_data.pricing_policy}\n"
            output += f"Page: {schema.page} (Page size: {schema.page_size})\n\n"

            if not items:
                output += (
                    "No positions found in this portfolio for the specified period.\n"
                )
                return output, artifact

            output += "Profit & Loss Analysis:\n"
            output += "=" * 100 + "\n\n"

            total_invested = 0.0
            total_market_value = 0.0
            total_principle = 0.0
            positions = []

            # Group items by instrument code for hierarchical display
            instrument_positions = {}

            # Process each item to extract P/L information
            for item in items:
                if isinstance(item, dict):
                    # Get item group
                    item_group_code = item.get("item_group_code", "UNKNOWN")

                    # Extract instrument information
                    instrument_code = item.get("instrument.user_code")

                    # For FX_VARIATIONS, use the name/user_code from the item itself
                    if item_group_code == "FX_VARIATIONS":
                        instrument_code = item.get(
                            "user_code", item.get("name", "FX_VARIATIONS")
                        )
                        instrument_name = item.get("name", "FX Variations")
                    else:
                        if instrument_code is None:
                            continue
                        instrument_name = item.get("instrument.name", "Unknown")
                    instrument_country = item.get("instrument.country.name", "")
                    portfolio_code = item.get(
                        "portfolio.user_code", schema.portfolio_code
                    )

                    # Extract P/L fields for the table format
                    principal = item.get("principal") or 0  # Principal P&L
                    carry = item.get("carry") or 0  # Carry P&L
                    overheads = item.get("overheads") or 0  # Overheads
                    total = item.get("total") or 0  # Total P&L
                    market_value = item.get("market_value") or 0  # Market value

                    # Extract local currency P/L values
                    principal_loc = item.get("principal_loc")
                    carry_loc = item.get("carry_loc")
                    overheads_loc = item.get("overheads_loc")
                    total_loc = item.get("total_loc")
                    market_value_loc = item.get("market_value_loc")

                    # Extract local currencies
                    instrument_pricing_currency = item.get(
                        "instrument.pricing_currency.user_code"
                    )
                    exposure_currency_code = item.get("exposure_currency.user_code")

                    # Additional position details
                    position_size = item.get("position_size") or 0
                    net_cost_price = item.get("net_cost_price") or 0
                    amount_invested = item.get("amount_invested_fixed") or 0
                    current_price = item.get("instrument_principal_price") or 0

                    position_data = {
                        "portfolio_code": portfolio_code,
                        "code": instrument_code,
                        "name": instrument_name,
                        "country": instrument_country,
                        "item_group_code": item_group_code,
                        "position_size": position_size,
                        "net_cost_price": net_cost_price,
                        "current_price": current_price,
                        "amount_invested": amount_invested,
                        "market_value": market_value,
                        "principal": principal,
                        "carry": carry,
                        "overheads": overheads,
                        "total": total,
                        "principal_loc": principal_loc,
                        "carry_loc": carry_loc,
                        "overheads_loc": overheads_loc,
                        "total_loc": total_loc,
                        "market_value_loc": market_value_loc,
                        "instrument_pricing_currency": instrument_pricing_currency,
                        "exposure_currency_code": exposure_currency_code,
                    }

                    positions.append(position_data)

                    # Group positions by instrument (without aggregation)
                    # For FX_VARIATIONS, use a special key since they don't have instrument codes
                    group_key = (
                        instrument_code
                        if item_group_code != "FX_VARIATIONS"
                        else f"FX_VARIATIONS_{instrument_name}"
                    )

                    if group_key not in instrument_positions:
                        instrument_positions[group_key] = {
                            "name": instrument_name,
                            "country": instrument_country,
                            "positions": [],
                            "instrument_code": instrument_code,
                        }

                    instrument_positions[group_key]["positions"].append(position_data)

                    # Accumulate totals
                    if isinstance(amount_invested, (int, float)):
                        total_invested += amount_invested
                    if isinstance(market_value, (int, float)):
                        total_market_value += market_value
                    if isinstance(total, (int, float)):
                        total_principle += total

            # Sort positions if requested
            if schema.sort_by:

                def sort_key(pos):
                    if schema.sort_by == SortBy.INSTRUMENT_NAME:
                        return pos["name"].lower()
                    elif schema.sort_by == SortBy.POSITION_SIZE:
                        return (
                            pos["position_size"]
                            if isinstance(pos["position_size"], (int, float))
                            else -float("inf")
                        )
                    elif schema.sort_by == SortBy.AMOUNT_INVESTED:
                        return (
                            abs(pos["amount_invested"])
                            if isinstance(pos["amount_invested"], (int, float))
                            else -float("inf")
                        )
                    elif schema.sort_by == SortBy.MARKET_VALUE:
                        return (
                            pos["market_value"]
                            if isinstance(pos["market_value"], (int, float))
                            else -float("inf")
                        )
                    elif schema.sort_by == SortBy.PRINCIPLE:
                        return (
                            pos["principle"]
                            if isinstance(pos["principle"], (int, float))
                            else -float("inf")
                        )
                    elif schema.sort_by == SortBy.TOTAL_PL:
                        return (
                            pos["total"]
                            if isinstance(pos["total"], (int, float))
                            else -float("inf")
                        )
                    return 0

                positions.sort(
                    key=sort_key,
                    reverse=(
                        schema.descending
                        if schema.sort_by != SortBy.INSTRUMENT_NAME
                        else not schema.descending
                    ),
                )

                # Add sorting info to output
                output += f"Sorted by: {schema.sort_by.value} ({'descending' if schema.descending else 'ascending'})\n"
                output += "=" * 100 + "\n\n"

            # Create consolidated P&L report matching the table format
            output += "\nCONSOLIDATED P&L REPORT\n"
            output += "=" * 100 + "\n"
            output += "Hierarchical view by Portfolio > Instrument > Status (OPENED/CLOSED)\n\n"

            # Display portfolio header
            output += f"PORTFOLIO: {schema.portfolio_code}\n"
            output += "-" * 80 + "\n\n"

            # Display each instrument with its positions
            for group_key, inst_data in instrument_positions.items():
                instrument_name = inst_data["name"]
                instrument_country = inst_data["country"]
                instrument_code = inst_data["instrument_code"]

                # Extract clean name without bond features
                bond_features = []
                if "<" in instrument_name and ">" in instrument_name:
                    features_start = instrument_name.find("<")
                    features_end = instrument_name.find(">")
                    features_str = instrument_name[features_start + 1 : features_end]
                    bond_features = [f.strip() for f in features_str.split(",")]
                    clean_name = instrument_name[:features_start].strip()
                else:
                    clean_name = instrument_name

                # Use instrument_code for display, not group_key
                output += f"INSTRUMENT: {instrument_code} - {clean_name}\n"
                if instrument_country:
                    output += f"Country: {instrument_country}\n"
                if bond_features:
                    output += f"Features: {', '.join(bond_features)}\n"
                output += "\n"

                # Group positions by status
                opened_positions = [
                    p
                    for p in inst_data["positions"]
                    if p["item_group_code"] == "OPENED"
                ]
                closed_positions = [
                    p
                    for p in inst_data["positions"]
                    if p["item_group_code"] == "CLOSED"
                ]
                fx_positions = [
                    p
                    for p in inst_data["positions"]
                    if p["item_group_code"] == "FX_VARIATIONS"
                ]

                # Display OPENED positions
                if opened_positions:
                    output += "  └── OPENED\n"
                    for pos in opened_positions:
                        # Determine asset type
                        asset_type = (
                            "Debt"
                            if "bond" in pos["name"].lower()
                            or "bill" in pos["name"].lower()
                            or "note" in pos["name"].lower()
                            else "Equity"
                        )

                        output += f"        └── {asset_type}\n"
                        output += f"            Portfolio: {pos['portfolio_code']}\n"
                        output += f"            PL Type: OPENED\n"
                        output += f"            Total P&L: {report_currency} {pos['total']:,.2f}\n"
                        if (
                            isinstance(pos["total_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"              Total P&L (Instrument Currency): {pos['instrument_pricing_currency']} {pos['total_loc']:,.2f}\n"
                        else:
                            output += (
                                f"              Total P&L (Instrument Currency): N/A\n"
                            )
                        output += f"            Principal: {report_currency} {pos['principal']:,.2f}\n"
                        if (
                            isinstance(pos["principal_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"              Principal (Instrument Currency): {pos['instrument_pricing_currency']} {pos['principal_loc']:,.2f}\n"
                        else:
                            output += (
                                f"              Principal (Instrument Currency): N/A\n"
                            )

                        output += f"            Carry P&L: {report_currency} {pos['carry']:,.2f}\n"
                        if (
                            isinstance(pos["carry_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"              Carry P&L (Instrument Currency): {pos['instrument_pricing_currency']} {pos['carry_loc']:,.2f}\n"
                        else:
                            output += (
                                f"              Carry P&L (Instrument Currency): N/A\n"
                            )

                        output += f"            Overheads: {report_currency} {pos['overheads']:,.2f}\n"
                        if (
                            isinstance(pos["overheads_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"              Overheads (Instrument Currency): {pos['instrument_pricing_currency']} {pos['overheads_loc']:,.2f}\n"
                        else:
                            output += (
                                f"              Overheads (Instrument Currency): N/A\n"
                            )

                        output += f"            Market Value: {report_currency} {pos['market_value']:,.2f}\n"
                        if (
                            isinstance(pos["market_value_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"              Market Value (Instrument Currency): {pos['instrument_pricing_currency']} {pos['market_value_loc']:,.2f}\n"
                        else:
                            output += f"              Market Value (Instrument Currency): N/A\n"
                        if pos["position_size"] != 0:
                            # Format position size with decimals only if needed
                            if pos["position_size"] == int(pos["position_size"]):
                                output += f"            Position Size: {int(pos['position_size']):,} units\n"
                            else:
                                output += (
                                    f"            Position Size: {pos['position_size']:,.6f} units".rstrip(
                                        "0"
                                    ).rstrip(
                                        "."
                                    )
                                    + "\n"
                                )
                            output += f"            Current Price: {report_currency} {pos['current_price']:,.2f}\n"
                            if pos["net_cost_price"] != 0:
                                output += f"            Average Cost: {report_currency} {pos['net_cost_price']:,.2f}\n"
                        output += "\n"

                # Display CLOSED positions
                if closed_positions:
                    output += "  └── CLOSED\n"
                    for pos in closed_positions:
                        # Determine asset type
                        asset_type = (
                            "Debt"
                            if "bond" in pos["name"].lower()
                            or "bill" in pos["name"].lower()
                            or "note" in pos["name"].lower()
                            else "Equity"
                        )

                        output += f"        └── {asset_type}\n"
                        output += f"            Portfolio: {pos['portfolio_code']}\n"
                        output += f"            PL Type: CLOSED\n"
                        output += f"            Total P&L: {report_currency} {pos['total']:,.2f}\n"
                        if (
                            isinstance(pos["total_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"              Total P&L (Instrument Currency): {pos['instrument_pricing_currency']} {pos['total_loc']:,.2f}\n"
                        else:
                            output += (
                                f"              Total P&L (Instrument Currency): N/A\n"
                            )
                        output += f"            Principal: {report_currency} {pos['principal']:,.2f}\n"
                        if (
                            isinstance(pos["principal_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"              Principal (Instrument Currency): {pos['instrument_pricing_currency']} {pos['principal_loc']:,.2f}\n"
                        else:
                            output += (
                                f"              Principal (Instrument Currency): N/A\n"
                            )

                        output += f"            Carry P&L: {report_currency} {pos['carry']:,.2f}\n"
                        if (
                            isinstance(pos["carry_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"              Carry P&L (Instrument Currency): {pos['instrument_pricing_currency']} {pos['carry_loc']:,.2f}\n"
                        else:
                            output += (
                                f"              Carry P&L (Instrument Currency): N/A\n"
                            )

                        output += f"            Overheads: {report_currency} {pos['overheads']:,.2f}\n"
                        if (
                            isinstance(pos["overheads_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"              Overheads (Instrument Currency): {pos['instrument_pricing_currency']} {pos['overheads_loc']:,.2f}\n"
                        else:
                            output += (
                                f"              Overheads (Instrument Currency): N/A\n"
                            )

                        output += f"            Market Value: {report_currency} {pos['market_value']:,.2f}\n"
                        if (
                            isinstance(pos["market_value_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"              Market Value (Instrument Currency): {pos['instrument_pricing_currency']} {pos['market_value_loc']:,.2f}\n"
                        else:
                            output += f"              Market Value (Instrument Currency): N/A\n"
                        output += "\n"

                # Display FX_VARIATIONS if any
                if fx_positions:
                    output += "  └── FX_VARIATIONS\n"
                    for pos in fx_positions:
                        output += f"        Portfolio: {pos['portfolio_code']}\n"
                        output += f"        PL Type: FX_VARIATIONS\n"
                        output += f"        Total P&L: {report_currency} {pos['total']:,.2f}\n"
                        if (
                            isinstance(pos["total_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"          Total P&L (Instrument Currency): {pos['instrument_pricing_currency']} {pos['total_loc']:,.2f}\n"
                        else:
                            output += (
                                f"          Total P&L (Instrument Currency): N/A\n"
                            )

                        output += f"        Principal: {report_currency} {pos['principal']:,.2f}\n"
                        if (
                            isinstance(pos["principal_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"          Principal (Instrument Currency): {pos['instrument_pricing_currency']} {pos['principal_loc']:,.2f}\n"
                        else:
                            output += (
                                f"          Principal (Instrument Currency): N/A\n"
                            )

                        output += f"        Carry P&L: {report_currency} {pos['carry']:,.2f}\n"
                        if (
                            isinstance(pos["carry_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"          Carry P&L (Instrument Currency): {pos['instrument_pricing_currency']} {pos['carry_loc']:,.2f}\n"
                        else:
                            output += (
                                f"          Carry P&L (Instrument Currency): N/A\n"
                            )

                        output += f"        Overheads: {report_currency} {pos['overheads']:,.2f}\n"
                        if (
                            isinstance(pos["overheads_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"          Overheads (Instrument Currency): {pos['instrument_pricing_currency']} {pos['overheads_loc']:,.2f}\n"
                        else:
                            output += (
                                f"          Overheads (Instrument Currency): N/A\n"
                            )

                        output += f"        Market Value: {report_currency} {pos['market_value']:,.2f}\n"
                        if (
                            isinstance(pos["market_value_loc"], (int, float))
                            and pos["instrument_pricing_currency"]
                        ):
                            output += f"          Market Value (Instrument Currency): {pos['instrument_pricing_currency']} {pos['market_value_loc']:,.2f}\n"
                        else:
                            output += (
                                f"          Market Value (Instrument Currency): N/A\n"
                            )
                        output += "\n"

                output += "-" * 60 + "\n\n"

            # Portfolio summary
            output += "-" * 100 + "\n"
            output += "PORTFOLIO SUMMARY:\n"
            output += (
                f"Total Amount Invested: {report_currency} {total_invested:,.2f}\n"
            )
            output += f"Total Current Market Value: {report_currency} {total_market_value:,.2f}\n"
            output += f"Total P/L: {report_currency} {total_principle:,.2f}"
            if total_principle > 0:
                output += " (PROFIT)\n"
            elif total_principle < 0:
                output += " (LOSS)\n"
            else:
                output += " (BREAK EVEN)\n"

            output += f"Number of Positions: {len(positions)}\n"

            # Performance summary
            profitable_positions = [p for p in positions if p["total"] > 0]
            losing_positions = [p for p in positions if p["total"] < 0]

            output += f"\nPerformance Summary:\n"
            output += f"- Profitable Positions: {len(profitable_positions)}\n"
            output += f"- Losing Positions: {len(losing_positions)}\n"
            output += f"- Break Even Positions: {len(positions) - len(profitable_positions) - len(losing_positions)}\n"

            if profitable_positions:
                best_performer = max(profitable_positions, key=lambda x: x["total"])
                output += f"- Best Performer by P/L: {best_performer['name']} ({report_currency} {best_performer['total']:,.2f})\n"

            if losing_positions:
                worst_performer = min(losing_positions, key=lambda x: x["total"])
                output += f"- Worst Performer by P/L: {worst_performer['name']} ({report_currency} {worst_performer['total']:,.2f})\n"

            # Check if we have any items with None or zero market values
            missing_market_values = []
            for item in items:
                if isinstance(item, dict):
                    instrument_code = item.get("instrument.user_code")
                    market_value = item.get("market_value")
                    if instrument_code and (market_value is None or market_value == 0):
                        missing_market_values.append(
                            {
                                "code": instrument_code,
                                "name": item.get("instrument.name", "Unknown"),
                                "position_size": item.get("position_size", 0),
                                "item_group": item.get("item_group_code", "UNKNOWN"),
                            }
                        )

            # If we have missing market values, call price history check
            if missing_market_values:
                output += "\n\n" + "=" * 100 + "\n"
                output += "IMPORTANT: Missing pricing data detected!\n"
                output += "=" * 100 + "\n\n"

                output += (
                    "The following instruments have missing or zero market values:\n"
                )
                for inst in missing_market_values:
                    output += f"- {inst['name']} ({inst['code']}) - Position: {inst['position_size']} - Group: {inst['item_group']}\n"

                output += "\nChecking price history availability...\n\n"

                try:
                    # Create price history check request with actual P/L dates
                    price_check_request = PriceHistoryCheckItems(
                        pl_first_date=pl_first_date,
                        report_date=report_date,
                        report_currency=schema.report_currency.value,
                        pricing_policy=request_data.pricing_policy,
                    )

                    # Call price history check
                    price_check_result = (
                        await self.client.price_history_check.check_price_history(
                            price_check_request
                        )
                    )

                    if price_check_result.items:
                        output += "Price History Check Results:\n"
                        output += "-" * 40 + "\n"

                        # Display all items without filtering by type
                        for item in price_check_result.items:
                            item_type = item.get("type", "unknown")
                            output += f"\nType: {item_type}\n"

                            # Display common fields
                            if item.get("name"):
                                output += f"  Name: {item.get('name')}\n"
                            if item.get("user_code"):
                                output += f"  Code: {item.get('user_code')}\n"
                            if item.get("id"):
                                output += f"  ID: {item.get('id')}\n"
                            if item.get("position_size") is not None:
                                output += (
                                    f"  Position Size: {item.get('position_size')}\n"
                                )

                            # Display type-specific fields
                            if item.get("accounting_date"):
                                output += f"  Accounting Date: {item.get('accounting_date')}\n"
                            if item.get("transaction_currency_name"):
                                output += f"  Currency: {item.get('transaction_currency_name')} ({item.get('transaction_currency_user_code')})\n"
                            if item.get("transaction_currency_id"):
                                output += f"  Currency ID: {item.get('transaction_currency_id')}\n"

                        output += "\nRECOMMENDATION:\n"
                        output += "The missing market values are due to unavailable pricing data.\n"
                        output += "To resolve this, you need to:\n"
                        output += "1. Try using a different report date where pricing data might be available\n"
                        output += "2. For P/L reports, ensure pricing data exists for both start and end dates\n"
                    else:
                        output += "Price history check completed - no specific issues found.\n"
                        output += "The missing values may be due to other configuration issues.\n"

                except Exception as e:
                    output += f"Could not perform price history check: {str(e)}\n"

                output += "\n" + "=" * 100 + "\n"
                output += f"\nNote: {len(missing_market_values)} instruments have missing or zero market values.\n"
                output += "The P/L calculations above may be incomplete for these instruments.\n"

            return output, artifact

        except Exception as e:
            exc = traceback.format_exc()
            logger.error(exc)
            error_msg = f"Error getting P/L report for portfolio {kwargs.get('portfolio_code')}: {str(e)}"
            if "input_str" in locals():
                error_msg += f"\n\nFull request sent:\n{input_str}"
            return error_msg, None


def build_pl_report_tools() -> List[BaseTool]:
    """Build and return P/L report tools"""
    toolkit = PLReportToolkit()

    tools = [
        StructuredTool.from_function(
            name="get_pl_report",
            func=lambda **kwargs: asyncio.run(toolkit._get_pl_report(**kwargs)),
            coroutine=toolkit._get_pl_report,
            description=(
                "Get a comprehensive Profit & Loss (P/L) report for a portfolio that shows investment performance over time. "
                "Use this tool to:\n"
                "- Calculate profit/loss for each position in a portfolio\n"
                "- Analyze investment returns over a specific period\n"
                "- Compare cost basis vs current market value\n"
                "- Track realized and unrealized gains/losses\n"
                "- Identify best and worst performing investments\n"
                "- Track FX variations impact on positions\n"
                "\n"
                "The report includes:\n"
                "- Position details (position size, cost basis, current value)\n"
                "- Individual P/L calculations for each holding\n"
                "- Return percentages for each position\n"
                "- Portfolio-wide performance summary\n"
                "- Performance categorization (profitable/losing positions)\n"
                "- Hierarchical grouping by position status: OPENED, CLOSED, and FX_VARIATIONS\n"
                "\n"
                "Position Status Types:\n"
                "- OPENED: Currently held positions\n"
                "- CLOSED: Previously held positions that have been sold\n"
                "- FX_VARIATIONS: Foreign exchange impact on positions\n"
                "\n"
                "Required parameters:\n"
                "- portfolio_code: The portfolio identifier\n"
                "- pl_first_date: Start date for P/L calculation (YYYY-MM-DD)\n"
                "\n"
                "Optional parameters:\n"
                "- report_date: End date (defaults to today)\n"
                "- report_currency: USD, EUR, BTC, CHF, GBP, or HKD (default: USD)\n"
                "- sort_by: Sort results by various metrics (instrument_name, position_size, amount_invested, market_value, principle, total_pl)\n"
                "\n"
                "Example questions this tool can answer:\n"
                "- What is my profit/loss for portfolio X since January 1st?\n"
                "- Show me all positions with positive returns\n"
                "- Which investments lost money this year?\n"
                "- List my worst performing stocks\n"
                "- Calculate my realized vs unrealized gains\n"
                "- What's the FX impact on my international positions?\n"
                "\n"
                "Key P/L calculations explained:\n"
                "- amount_invested: Total USD invested (negative for long positions)\n"
                "- market_value: Current position value (position_size × current_price)\n"
                "- total: Total P/L for the position (sum of principal + carry + overheads)\n"
                "- principal: Price-related P/L component\n"
                "- carry: Interest/dividend income component\n"
                "- overheads: Fees and expenses component\n"
            ),
            args_schema=GetPLReportSchema,
            response_format="content_and_artifact",
        ),
    ]

    return tools
