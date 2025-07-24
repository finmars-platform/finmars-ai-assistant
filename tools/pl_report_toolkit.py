import asyncio
import json
import traceback
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool

from libs.client.finmars_client import FinmarsPortfolioClient
from libs.logger.logger import logger
from libs.schema.via_data_model_codegen.report_schema import PLReportItems
from .shared_models import ReportCurrency, PLReportSortBy as SortBy, drop_empty_fields


class GetPLReportSchema(BaseModel):
    """Input schema for getting P/L report"""

    portfolio_code: str = Field(
        description="The portfolio user code (user_code from portfolio)"
    )
    report_currency: ReportCurrency = Field(
        default=ReportCurrency.USD,
        description="The currency for the report (USD or EUR)",
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
                page=1,
                page_size=500,
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
            output += f"Currency: {report_currency}\n\n"

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
                    }

                    positions.append(position_data)
                    
                    # Group positions by instrument (without aggregation)
                    if instrument_code not in instrument_positions:
                        instrument_positions[instrument_code] = {
                            "name": instrument_name,
                            "country": instrument_country,
                            "positions": []
                        }
                    
                    instrument_positions[instrument_code]["positions"].append(position_data)

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
            for inst_code, inst_data in instrument_positions.items():
                instrument_name = inst_data["name"]
                instrument_country = inst_data["country"]
                
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
                
                output += f"INSTRUMENT: {inst_code} - {clean_name}\n"
                if instrument_country:
                    output += f"Country: {instrument_country}\n"
                if bond_features:
                    output += f"Features: {', '.join(bond_features)}\n"
                output += "\n"
                
                # Group positions by status
                opened_positions = [p for p in inst_data["positions"] if p["item_group_code"] == "OPENED"]
                closed_positions = [p for p in inst_data["positions"] if p["item_group_code"] == "CLOSED"]
                fx_positions = [p for p in inst_data["positions"] if p["item_group_code"] == "FX_VARIATIONS"]
                
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
                        output += f"            Total P&L: ${pos['total']:,.2f}\n"
                        output += f"            Principal: ${pos['principal']:,.2f}\n"
                        output += f"            Carry P&L: ${pos['carry']:,.2f}\n"
                        output += f"            Overheads: ${pos['overheads']:,.2f}\n"
                        output += f"            Market Value: ${pos['market_value']:,.2f}\n"
                        if pos["position_size"] != 0:
                            output += f"            Position Size: {pos['position_size']:,.2f} units\n"
                            output += f"            Current Price: ${pos['current_price']:,.2f}\n"
                            if pos["net_cost_price"] != 0:
                                output += f"            Average Cost: ${pos['net_cost_price']:,.2f}\n"
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
                        output += f"            Total P&L: ${pos['total']:,.2f}\n"
                        output += f"            Principal: ${pos['principal']:,.2f}\n"
                        output += f"            Carry P&L: ${pos['carry']:,.2f}\n"
                        output += f"            Overheads: ${pos['overheads']:,.2f}\n"
                        output += f"            Market Value: ${pos['market_value']:,.2f}\n"
                        output += "\n"
                
                # Display FX_VARIATIONS if any
                if fx_positions:
                    output += "  └── FX_VARIATIONS\n"
                    for pos in fx_positions:
                        output += f"        Portfolio: {pos['portfolio_code']}\n"
                        output += f"        PL Type: FX_VARIATIONS\n"
                        output += f"        Total P&L: ${pos['total']:,.2f}\n"
                        output += f"        Principal: ${pos['principal']:,.2f}\n"
                        output += f"        Carry P&L: ${pos['carry']:,.2f}\n"
                        output += f"        Overheads: ${pos['overheads']:,.2f}\n"
                        output += f"        Market Value: ${pos['market_value']:,.2f}\n"
                        output += "\n"
                
                output += "-" * 60 + "\n\n"

            # Portfolio summary
            output += "-" * 100 + "\n"
            output += "PORTFOLIO SUMMARY:\n"
            output += f"Total Amount Invested: ${total_invested:,.2f}\n"
            output += f"Total Current Market Value: ${total_market_value:,.2f}\n"
            output += f"Total P/L: ${total_principle:,.2f}"
            if total_principle > 0:
                output += " (PROFIT)\n"
            elif total_principle < 0:
                output += " (LOSS)\n"
            else:
                output += " (BREAK EVEN)\n"

            # Calculate overall portfolio return percentage
            if total_invested != 0:
                overall_return = (total_principle / abs(total_invested)) * 100
                output += f"Overall Portfolio Return: {overall_return:.2f}%\n"
                output += "Note: Return % is calculated at portfolio level only, not for individual instruments\n"

            output += f"Number of Positions: {len(positions)}\n"

            # Performance summary
            profitable_positions = [p for p in positions if p["total"] > 0]
            losing_positions = [p for p in positions if p["total"] < 0]

            output += f"\nPerformance Summary:\n"
            output += f"- Profitable Positions: {len(profitable_positions)}\n"
            output += f"- Losing Positions: {len(losing_positions)}\n"
            output += f"- Break Even Positions: {len(positions) - len(profitable_positions) - len(losing_positions)}\n"

            if profitable_positions:
                best_performer = max(
                    profitable_positions, key=lambda x: x["total"]
                )
                output += f"- Best Performer by P/L: {best_performer['name']} (${best_performer['total']:,.2f})\n"

            if losing_positions:
                worst_performer = min(
                    losing_positions, key=lambda x: x["total"]
                )
                output += f"- Worst Performer by P/L: {worst_performer['name']} (${worst_performer['total']:,.2f})\n"

            return output, artifact

        except Exception as e:
            exc = traceback.format_exc()
            logger.error(exc)
            return (
                f"Error getting P/L report for portfolio {kwargs.get('portfolio_code')}: {str(e)}",
                None,
            )


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
                "- Calculate overall portfolio return percentage\n"
                "\n"
                "The report includes:\n"
                "- Position details (shares held, cost basis, current value)\n"
                "- Individual P/L calculations for each holding\n"
                "- Return percentages for each position\n"
                "- Portfolio-wide performance summary\n"
                "- Performance categorization (profitable/losing positions)\n"
                "\n"
                "Required parameters:\n"
                "- portfolio_code: The portfolio identifier\n"
                "- pl_first_date: Start date for P/L calculation (YYYY-MM-DD)\n"
                "\n"
                "Optional parameters:\n"
                "- report_date: End date (defaults to today)\n"
                "- report_currency: USD or EUR (default: USD)\n"
                "- sort_by: Sort results by various metrics (instrument_name, position_size, amount_invested, market_value, principle, total_pl)\n"
                "\n"
                "Example questions this tool can answer:\n"
                "- What is my profit/loss for portfolio X since January 1st?\n"
                "- Show me all positions with returns above 20%\n"
                "- Which investments lost money this year?\n"
                "- What's my overall portfolio return for 2024?\n"
                "- List my worst performing stocks\n"
                "- Calculate my realized vs unrealized gains\n"
                "\n"
                "Key P/L calculations explained:\n"
                "- amount_invested: Total USD invested (negative for long positions)\n"
                "- market_value: Current position value (position_size × current_price)\n"
                "- total: Total P/L for the position (sum of principal + carry + overheads)\n"
                "- Note: Return percentage is calculated only at portfolio level, not for individual instruments"
            ),
            args_schema=GetPLReportSchema,
            response_format="content_and_artifact",
        ),
    ]

    return tools
