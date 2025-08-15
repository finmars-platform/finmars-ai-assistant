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
    BackendBalanceReportItems,
    DateField,
    PriceHistoryCheckItems,
)
from .shared_models import (
    ReportCurrency,
    BalanceReportSortBy as SortBy,
    drop_empty_fields,
)


class GetBalanceReportSchema(BaseModel):
    """Input schema for getting balance report"""

    portfolio_code: str = Field(
        description="The portfolio user code (user_code from portfolio)"
    )
    report_currency: ReportCurrency = Field(
        default=ReportCurrency.USD,
        description="The currency for the report (USD, EUR, BTC, CHF, GBP, HKD)",
    )
    report_date: Optional[str] = Field(
        default=None,
        description="The date for the balance report in YYYY-MM-DD format (e.g., '2024-03-15'). If not provided, today's date will be used.",
    )
    sort_by: Optional[SortBy] = Field(
        default=None,
        description="Sort positions by position_size, market_value, exposure, or name. If not provided, positions will be shown in original order.",
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
        default=200,
        description="Number of items per page (default: 200, max: 500)",
    )


class BalanceReportToolkit:
    """Toolkit for balance report operations using the Finmars API"""

    def __init__(self):
        self.client = FinmarsPortfolioClient()

    async def _get_balance_report(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get balance report with portfolio positions information"""
        try:
            schema = GetBalanceReportSchema(**kwargs)

            # Pre-process: Build the request according to requirements
            # Parse report_date if provided, otherwise use today's date
            if schema.report_date:
                try:
                    report_date = datetime.strptime(
                        schema.report_date, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    return (
                        f"Error: Invalid date format. Please use YYYY-MM-DD format (e.g., '2024-03-15')",
                        None,
                    )
            else:
                report_date = datetime.now().date()

            request_data = BackendBalanceReportItems(
                account_mode=0,  # To accumulate market value on all accounts Account_mode = ignore should be used
                accounts=[],
                accounts_cash=[],
                accounts_position=[],
                # allocation_detailing=True,
                allocation_mode=0,
                # approach_multiplier=0.5,
                calculate_pl=True,
                # complex_transaction_statuses_filter="booked",
                cost_method=1,
                custom_fields_to_calculate="Asset Type",
                # date_field="transaction_date",
                date_field=DateField.transaction_date,
                # depth_level="base_transaction",
                expression_iterations_count=1,
                pl_first_date=None,
                # pl_include_zero=False,
                portfolio_mode=1,
                portfolios=[schema.portfolio_code],
                pricing_policy="com.finmars.standard-pricing:standard",
                report_currency=schema.report_currency.value,
                report_date=report_date,
                report_type=1,
                # show_balance_exposure_details=True,
                # show_transaction_details=True,
                frontend_request_options={"groups_types": [], "groups_values": []},
                strategies1=[],
                strategies2=[],
                strategies3=[],
                strategy1_mode=0,
                strategy2_mode=0,
                strategy3_mode=0,
                # table_font_size="small",
                # transaction_classes=[],
                page=schema.page,
                page_size=min(schema.page_size, 500),  # Ensure max 500
                report_instance_id=None,
                # portfolios_table_data_items=[]
            )
            input_str = request_data.model_dump_json()

            # Make the API call
            result: BackendBalanceReportItems = (
                await self.client.balance_report.get_balance_report_items(request_data)
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
            output = f"The FULL request to get Balance Report was: {input_str}\n\n\n"
            output += (
                f"RESPONSE:\nBalance Report for Portfolio: {schema.portfolio_code}\n"
            )
            output += f"Report Date: {report_date}\n"
            output += f"Report Currency: {report_currency}\n"
            output += f"Pricing Policy: {request_data.pricing_policy}\n"
            output += f"Page: {schema.page} (Page size: {schema.page_size})\n\n"

            if not items:
                output += "No positions found in this portfolio.\n"
                return output, artifact

            output += "Portfolio Positions:\n"
            output += "=" * 80 + "\n\n"

            total_value = 0.0
            total_exposure = 0.0
            positions = []
            cash_positions = []

            # Process each item to extract instrument info
            for item in items:
                if isinstance(item, dict):
                    # Check if this is a cash position (currency) or instrument position
                    instrument_code = item.get("instrument.user_code")
                    currency_code = item.get("currency.user_code")

                    # Extract account information (common for all items)
                    account_code = item.get("account.user_code", "")
                    account_name = item.get("account.name", "")
                    account_short_name = item.get("account.short_name", "")
                    account_public_name = item.get("account.public_name", "")
                    account_notes = item.get("account.notes", "")

                    # Extract portfolio information (if available)
                    portfolio_user_code = item.get(
                        "portfolio.user_code", schema.portfolio_code
                    )
                    portfolio_name = item.get("portfolio.name", "")
                    portfolio_short_name = item.get("portfolio.short_name", "")
                    portfolio_public_name = item.get("portfolio.public_name", "")
                    portfolio_notes = item.get("portfolio.notes", "")
                    portfolio_first_transaction_date = item.get(
                        "portfolio.first_transaction_date", ""
                    )
                    portfolio_first_cash_flow_date = item.get(
                        "portfolio.first_cash_flow_date", ""
                    )

                    if instrument_code:
                        # This is an instrument position
                        instrument_name = item.get("instrument.name", "Unknown")
                        instrument_country = item.get("instrument.country.name", "")
                    elif currency_code:
                        # This is a cash position
                        instrument_code = currency_code
                        instrument_name = item.get("currency.name") or item.get(
                            "name", "Unknown Currency"
                        )
                        instrument_country = item.get("currency.country.name", "")
                    else:
                        # Skip items that are neither instruments nor currencies
                        continue

                    # Extract position size and value information from actual API response
                    position_size = item.get("position_size")

                    market_value = item.get("market_value")
                    exposure = item.get("exposure")

                    # Extract local currency values
                    market_value_loc = item.get("market_value_loc")
                    exposure_loc = item.get("exposure_loc")

                    # Extract local currencies
                    instrument_pricing_currency = item.get(
                        "instrument.pricing_currency.user_code"
                    )
                    exposure_currency_code = item.get("exposure_currency.user_code")

                    # Extract percentage fields directly from the response
                    market_value_percent = item.get("market_value_percent")
                    exposure_percent = item.get("exposure_percent")
                    if market_value_percent is not None:
                        market_value_percent = market_value_percent * 100.0

                    if exposure_percent is not None:
                        exposure_percent = exposure_percent * 100.0

                    # Если вдруг чего-то нет, агент должен предложить другую дату и тп
                    # Данные предыдущие, шаг назад, где данные есть
                    # Какие именно шаги нужны, чтобы это получить
                    # `item` <- позиции долларов портфеля

                    # Extract cost price fields
                    net_cost_price = item.get("net_cost_price")
                    net_cost_price_loc = item.get("net_cost_price_loc")
                    gross_cost_price = item.get("gross_cost_price")
                    gross_cost_price_loc = item.get("gross_cost_price_loc")

                    # Extract YTM and Duration for bonds
                    ytm = item.get("ytm", 0)
                    if ytm is not None and ytm != 0:
                        ytm = ytm * 100.0 # Convert to percentage

                    ytm_at_cost = item.get("ytm_at_cost", 0)
                    if ytm_at_cost is not None and ytm_at_cost != 0:
                        ytm_at_cost = ytm_at_cost * 100.0  # Convert to percentage

                    modified_duration = item.get(
                        "modified_duration", 0
                    )  # Duration in years

                    position_data = {
                        "code": instrument_code,
                        "name": instrument_name,
                        "country": instrument_country,
                        "position_size": position_size,
                        "value": market_value,
                        "exposure": exposure,
                        "market_value_loc": market_value_loc,
                        "exposure_loc": exposure_loc,
                        "instrument_pricing_currency": instrument_pricing_currency,
                        "exposure_currency_code": exposure_currency_code,
                        "market_value_percent": market_value_percent,
                        "exposure_percent": exposure_percent,
                        "net_cost_price": net_cost_price,
                        "net_cost_price_loc": net_cost_price_loc,
                        "gross_cost_price": gross_cost_price,
                        "gross_cost_price_loc": gross_cost_price_loc,
                        "ytm": ytm,
                        "ytm_at_cost": ytm_at_cost,
                        "modified_duration": modified_duration,
                        "is_cash": currency_code is not None,
                        "account_code": account_code,
                        "account_name": account_name,
                        "account_short_name": account_short_name,
                        "account_public_name": account_public_name,
                        "account_notes": account_notes,
                        "portfolio_user_code": portfolio_user_code,
                        "portfolio_name": portfolio_name,
                        "portfolio_short_name": portfolio_short_name,
                        "portfolio_public_name": portfolio_public_name,
                        "portfolio_notes": portfolio_notes,
                        "portfolio_first_transaction_date": portfolio_first_transaction_date,
                        "portfolio_first_cash_flow_date": portfolio_first_cash_flow_date,
                    }

                    if currency_code:
                        cash_positions.append(position_data)
                    else:
                        positions.append(position_data)

                    # Accumulate totals for both cash and instrument positions
                    if isinstance(market_value, (int, float)):
                        total_value += market_value

                    if isinstance(exposure, (int, float)):
                        total_exposure += exposure

                    # output += "-" * 80 + "\n"
                    # output += f"Source:\n"
                    # output += json.dumps(item, ensure_ascii=False)
                    # output += "\n" + "-" * 80 + "\n"

            # Sort positions if requested
            if schema.sort_by:

                def sort_key(position):
                    if schema.sort_by == SortBy.POSITION_SIZE:
                        val = position["position_size"]
                        return (
                            val
                            if isinstance(val, (int, float))
                            else (-float("inf") if schema.descending else float("inf"))
                        )
                    elif schema.sort_by == SortBy.MARKET_VALUE:
                        val = position["value"]
                        return (
                            val
                            if isinstance(val, (int, float))
                            else (-float("inf") if schema.descending else float("inf"))
                        )
                    elif schema.sort_by == SortBy.EXPOSURE:
                        val = position["exposure"]
                        return (
                            val
                            if isinstance(val, (int, float))
                            else (-float("inf") if schema.descending else float("inf"))
                        )
                    elif schema.sort_by == SortBy.NAME:
                        return position["name"].lower()
                    return 0

                positions.sort(
                    key=sort_key,
                    reverse=(
                        schema.descending
                        if schema.sort_by != SortBy.NAME
                        else not schema.descending
                    ),
                )

                # Add sorting info to output
                output += f"Sorted by: {schema.sort_by.value} ({'descending' if schema.descending else 'ascending'})\n"
                output += "=" * 80 + "\n\n"

            # Calculate allocations and format output
            market_value_pct_total = []
            exposure_pct_total = []

            # Display instrument positions first
            if positions:
                output += "INSTRUMENT POSITIONS:\n"
                output += "-" * 60 + "\n\n"

            for position in positions:
                output += f"Instrument: {position['name']} ({position['code']})\n"
                if position["country"]:
                    output += f"  - Country: {position['country']}\n"
                else:
                    output += f"  - Country: N/A\n"

                # Account information (using public name only)
                if position["account_public_name"]:
                    output += f"  - Account (Public Name): {position['account_public_name']}\n"

                # Position Size
                if isinstance(position["position_size"], (int, float)):
                    # Format with decimals only if needed
                    if position["position_size"] == int(position["position_size"]):
                        output += (
                            f"  - Position Size: {int(position['position_size']):,}"
                        )
                    else:
                        output += f"  - Position Size: {position['position_size']:,.6f}".rstrip(
                            "0"
                        ).rstrip(
                            "."
                        )
                    if position["position_size"] < 0:
                        output += " (Short Position)\n"
                    else:
                        output += "\n"
                else:
                    output += "  - Position Size: N/A\n"

                # Market Value with percentage (use field from response)
                if isinstance(position["value"], (int, float)):
                    output += (
                        f"  - Market Value: {report_currency} {position['value']:,.2f}"
                    )
                    if position["value"] < 0:
                        output += " (Short Position)"
                    elif position["market_value_percent"] >= 0:
                        market_value_pct_total.append(position["market_value_percent"])
                        output += f" ({position['market_value_percent']:.2f}%)"
                    output += "\n"
                else:
                    output += "  - Market Value: N/A\n"

                # Add local currency value
                if (
                    isinstance(position["market_value_loc"], (int, float))
                    and position["instrument_pricing_currency"]
                ):
                    output += f"    Market Value (Instrument Currency): {position['instrument_pricing_currency']} {position['market_value_loc']:,.2f}\n"
                else:
                    output += "    Market Value (Instrument Currency): N/A\n"

                # Exposure with percentage (use field from response)
                if isinstance(position["exposure"], (int, float)):
                    output += (
                        f"  - Exposure: {report_currency} {position['exposure']:,.2f}"
                    )
                    if position["exposure"] < 0:
                        output += " (Short Position)"
                    elif position["exposure_percent"] >= 0:
                        exposure_pct_total.append(position["exposure_percent"])
                        output += f" ({position['exposure_percent']:.2f}%)"
                    output += "\n"
                else:
                    output += "  - Exposure: N/A\n"

                # Add local currency exposure
                if (
                    isinstance(position["exposure_loc"], (int, float))
                    and position["exposure_currency_code"]
                ):
                    output += f"    Exposure (Exposure Currency): {position['exposure_currency_code']} {position['exposure_loc']:,.2f}\n"
                else:
                    output += "    Exposure (Exposure Currency): N/A\n"

                # Cost Price fields
                # Net Cost Price
                if isinstance(position["net_cost_price"], (int, float)):
                    output += f"  - Net Cost Price: {report_currency} {position['net_cost_price']:,.2f}\n"
                else:
                    output += "  - Net Cost Price: N/A\n"

                if (
                    isinstance(position["net_cost_price_loc"], (int, float))
                    and position["instrument_pricing_currency"]
                ):
                    output += f"    Net Cost Price (Instrument Currency): {position['instrument_pricing_currency']} {position['net_cost_price_loc']:,.2f}\n"
                else:
                    output += "    Net Cost Price (Instrument Currency): N/A\n"

                # Gross Cost Price
                if isinstance(position["gross_cost_price"], (int, float)):
                    output += f"  - Gross Cost Price: {report_currency} {position['gross_cost_price']:,.2f}\n"
                else:
                    output += "  - Gross Cost Price: N/A\n"

                if (
                    isinstance(position["gross_cost_price_loc"], (int, float))
                    and position["instrument_pricing_currency"]
                ):
                    output += f"    Gross Cost Price (Instrument Currency): {position['instrument_pricing_currency']} {position['gross_cost_price_loc']:,.2f}\n"
                else:
                    output += "    Gross Cost Price (Instrument Currency): N/A\n"

                # YTM and Duration fields (only show for bonds - when values are non-zero)
                # Check if this is a bond by looking at YTM or Duration values
                is_bond = (
                    (isinstance(position["ytm"], (int, float)) and position["ytm"] != 0)
                    or (
                        isinstance(position["ytm_at_cost"], (int, float))
                        and position["ytm_at_cost"] != 0
                    )
                    or (
                        isinstance(position["modified_duration"], (int, float))
                        and position["modified_duration"] != 0
                    )
                )

                if is_bond:
                    # Yield to Maturity at current price
                    if (
                        isinstance(position["ytm"], (int, float))
                        and position["ytm"] != 0
                    ):
                        output += (
                            f"  - Yield to Maturity (YTM): {position['ytm']:.2f}%\n"
                        )
                    else:
                        output += "  - Yield to Maturity (YTM): N/A (price may be 0)\n"

                    # YTM at acquisition cost
                    if (
                        isinstance(position["ytm_at_cost"], (int, float))
                        and position["ytm_at_cost"] != 0
                    ):
                        output += (
                            f"  - YTM at Acquisition: {position['ytm_at_cost']:.2f}%\n"
                        )
                    else:
                        output += "  - YTM at Acquisition: N/A\n"

                    # Modified Duration
                    if (
                        isinstance(position["modified_duration"], (int, float))
                        and position["modified_duration"] != 0
                    ):
                        output += (
                            f"  - Duration: {position['modified_duration']:.2f} years\n"
                        )
                        # Add note about floating coupon bonds
                        if position["modified_duration"] < 1:
                            output += "    (Note: Low duration may indicate floating rate bond)\n"
                    else:
                        output += "  - Duration: N/A\n"

                output += "\n"

            # Display cash positions
            if cash_positions:
                output += "\nCASH POSITIONS:\n"
                output += "-" * 60 + "\n\n"

                for position in cash_positions:
                    output += f"Currency: {position['name']} ({position['code']})\n"

                    # Account information (using public name only)
                    if position["account_public_name"]:
                        output += f"  - Account (Public Name): {position['account_public_name']}\n"

                    # Position Size (Amount)
                    if isinstance(position["position_size"], (int, float)):
                        output += f"  - Amount: {position['code']} {position['position_size']:,.2f}\n"
                    else:
                        output += "  - Amount: N/A\n"

                    # Market Value with percentage
                    if isinstance(position["value"], (int, float)):
                        output += f"  - Market Value: {report_currency} {position['value']:,.2f}"
                        if (
                            position["market_value_percent"]
                            and position["market_value_percent"] >= 0
                        ):
                            market_value_pct_total.append(
                                position["market_value_percent"]
                            )
                            output += f" ({position['market_value_percent']:.2f}%)"
                        output += "\n"
                    else:
                        output += "  - Market Value: N/A\n"

                    # Exposure with percentage
                    if isinstance(position["exposure"], (int, float)):
                        output += f"  - Exposure: {report_currency} {position['exposure']:,.2f}"
                        if (
                            position["exposure_percent"]
                            and position["exposure_percent"] >= 0
                        ):
                            exposure_pct_total.append(position["exposure_percent"])
                            output += f" ({position['exposure_percent']:.2f}%)"
                        output += "\n"
                    else:
                        output += "  - Exposure: N/A\n"

                    output += "\n"

            output += "-" * 80 + "\n"
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
                            }
                        )

            # If we have missing market values, call price history check
            if missing_market_values:
                output += "\n" + "=" * 80 + "\n"
                output += "IMPORTANT: Missing pricing data detected!\n"
                output += "=" * 80 + "\n\n"

                output += (
                    "The following instruments have missing or zero market values:\n"
                )
                for inst in missing_market_values:
                    output += f"- {inst['name']} ({inst['code']}) - Position: {inst['position_size']}\n"

                output += "\nChecking price history availability...\n\n"

                try:
                    # Create price history check request
                    price_check_request = PriceHistoryCheckItems(
                        pl_first_date=report_date,  # For balance report, both dates are the same
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
                    else:
                        output += "Price history check completed - no specific issues found.\n"
                        output += "The missing values may be due to other configuration issues.\n"

                except Exception as e:
                    output += f"Could not perform price history check: {str(e)}\n"

                output += "\n" + "=" * 80 + "\n\n"

            # Add portfolio metadata if available - collect unique values from all positions
            all_positions = positions + cash_positions
            if all_positions:
                # Use sets to collect unique portfolio metadata
                portfolio_names = {
                    p.get("portfolio_name")
                    for p in all_positions
                    if p.get("portfolio_name")
                }
                portfolio_notes = {
                    p.get("portfolio_notes")
                    for p in all_positions
                    if p.get("portfolio_notes")
                }
                portfolio_first_transaction_dates = {
                    p.get("portfolio_first_transaction_date")
                    for p in all_positions
                    if p.get("portfolio_first_transaction_date")
                }
                portfolio_first_cash_flow_dates = {
                    p.get("portfolio_first_cash_flow_date")
                    for p in all_positions
                    if p.get("portfolio_first_cash_flow_date")
                }

                # Display portfolio information if we have any metadata
                if (
                    portfolio_names
                    or portfolio_notes
                    or portfolio_first_transaction_dates
                    or portfolio_first_cash_flow_dates
                ):
                    output += "\nPORTFOLIO INFORMATION:\n"
                    output += "-" * 60 + "\n"

                    # Display each unique value (should typically be just one per field)
                    if portfolio_names:
                        for name in portfolio_names:
                            output += f"Portfolio Name: {name}\n"

                    if portfolio_notes:
                        for note in portfolio_notes:
                            output += f"Portfolio Type: {note}\n"

                    if portfolio_first_transaction_dates:
                        for date in portfolio_first_transaction_dates:
                            output += f"First Transaction Date: {date}\n"

                    if portfolio_first_cash_flow_dates:
                        for date in portfolio_first_cash_flow_dates:
                            output += f"First Cash Flow Date: {date}\n"

                    output += "\n"

            output += f"Total Portfolio Value (Market Value): {report_currency} {total_value:,.2f}\n"
            output += (
                f"Total Portfolio Exposure: {report_currency} {total_exposure:,.2f}\n"
            )
            output += f"Number of Instrument Positions: {len(positions)}\n"
            output += f"Number of Cash Positions: {len(cash_positions)}\n"
            output += f"Total Positions: {len(positions) + len(cash_positions)}\n"

            if missing_market_values:
                output += f"\nNote: {len(missing_market_values)} instruments have missing or zero market values.\n"
                output += "The total values above exclude these instruments.\n"

            return output, artifact

        except Exception as e:
            exc = traceback.format_exc()
            logger.error(exc)
            error_msg = f"Error getting balance report for portfolio {kwargs.get('portfolio_code')}: {str(e)}"
            if "input_str" in locals():
                error_msg += f"\n\nFull request sent:\n{input_str}"
            return error_msg, None


def build_balance_report_tools() -> List[BaseTool]:
    """Build and return balance report tools"""
    toolkit = BalanceReportToolkit()

    tools = [
        StructuredTool.from_function(
            name="get_balance_report",
            func=lambda **kwargs: asyncio.run(toolkit._get_balance_report(**kwargs)),
            coroutine=toolkit._get_balance_report,
            description=(
                "Get a comprehensive balance report for a portfolio that answers questions about portfolio content and composition. "
                "Use this tool to:\n"
                "- Find out what companies/stocks/instruments are in a portfolio\n"
                "- Get the percentage/allocation of specific companies in the portfolio\n"
                "- See the shares count for each position\n"
                "- View cash positions (USD, EUR, etc.) with account details\n"
                "- Analyze portfolio concentration and diversification\n"
                "- Check for short positions (negative shares/values)\n"
                "- View total portfolio value and exposure\n"
                "- Get historical reports by specifying a date\n"
                "- Sort positions by position size, market value, exposure, or name\n"
                "- View bond-specific metrics (YTM, Duration) for fixed income positions\n"
                "\n"
                "The report includes:\n"
                "- Complete list of instrument positions with names and codes\n"
                "- Cash positions with currency amounts and account details\n"
                "- Position sizes (number of shares/bonds/units)\n"
                "- Market values with allocation percentages\n"
                "- Exposure amounts and percentages\n"
                "- Account information for each position\n"
                "- Portfolio metadata (name, type, first transaction date)\n"
                "- For bonds: Yield to Maturity (YTM), YTM at cost, and Duration\n"
                "- Total portfolio metrics\n"
                "\n"
                "Bond-specific fields:\n"
                "- YTM: Yield to Maturity at current bond price\n"
                "- YTM at Cost: Yield to Maturity at acquisition price\n"
                "- Duration: Modified duration (time to maturity in years considering coupons)\n"
                "  Note: For floating rate bonds, duration shows time to next coupon\n"
                "  Note: If price is 0, YTM will be undefined/zero\n"
                "\n"
                "Example questions this tool can answer:\n"
                "- What companies are in portfolio X?\n"
                "- What is the percentage/allocation of Apple in this portfolio?\n"
                "- Show me the allocations in portfolio Y\n"
                "- What is the portfolio allocation breakdown?\n"
                "- Show me the top positions in portfolio Z\n"
                "- Is the portfolio diversified or concentrated?\n"
                "- Are there any short positions?\n"
                "- What are the YTM and Duration of bonds in the portfolio?"
            ),
            args_schema=GetBalanceReportSchema,
            response_format="content_and_artifact",
        ),
    ]

    return tools
