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
    PerformanceReport,
    BackendBalanceReportItems,
    DateField,
)
from .shared_models import ReportCurrency, drop_empty_fields
from libs.utils.hashing_utils import ACTIVATE_PUBLIC_NAME


class GetPerformanceReportSchema(BaseModel):
    """Input schema for getting performance report"""

    portfolio_code: str = Field(
        description="The portfolio user code (user_code from portfolio)"
    )
    report_currency: ReportCurrency = Field(
        default=ReportCurrency.USD,
        description="The currency for the report (USD, EUR, BTC, CHF, GBP, HKD)",
    )
    end_date: str = Field(
        description="The end date for performance calculation in YYYY-MM-DD format (e.g., '2024-12-31')"
    )
    begin_date: Optional[str] = Field(
        default=None,
        description="The start date for performance calculation in YYYY-MM-DD format (e.g., '2024-01-01'). If not provided, performance will be calculated from the portfolio's inception.",
    )


class PerformanceReportToolkit:
    """Toolkit for performance report operations using the Finmars API"""

    def __init__(self, finmars_token: str = None, space: str = None, realm: str = None):
        self.client = FinmarsPortfolioClient(
            api_key=finmars_token, space=space, realm=realm
        )

    async def _get_performance_report(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get performance report with portfolio-level performance metrics"""
        try:
            schema = GetPerformanceReportSchema(**kwargs)

            # Parse dates
            try:
                end_date = datetime.strptime(schema.end_date, "%Y-%m-%d").date()
            except ValueError:
                return (
                    f"Error: Invalid end_date format. Please use YYYY-MM-DD format (e.g., '2024-12-31')",
                    None,
                )

            begin_date = None
            if schema.begin_date:
                try:
                    begin_date = datetime.strptime(schema.begin_date, "%Y-%m-%d").date()
                except ValueError:
                    return (
                        f"Error: Invalid begin_date format. Please use YYYY-MM-DD format (e.g., '2024-01-01')",
                        None,
                    )

            # Build request - note that 'bundle' is the portfolio code
            request_data = PerformanceReport(
                save_report=False,
                begin_date=begin_date,
                end_date=end_date,
                calculation_type="modified_dietz",  # Hardcoded as requested
                period_type="ytd",  # Hardcoded as requested
                segmentation_type="months",  # Hardcoded as requested
                adjustment_type="original",  # Hardcoded as requested
                bundle=schema.portfolio_code,  # bundle is the portfolio code
                report_currency=schema.report_currency.value,
            )
            input_str = request_data.model_dump_json()

            # Make the API call
            result: PerformanceReport = (
                await self.client.performance_report.create_performance_report(
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
            output = (
                f"The FULL request to get Performance Report was: {input_str}\n\n\n"
            )

            display_portfolio_code = schema.portfolio_code
            output += f"RESPONSE:\nPerformance Report for Portfolio: {display_portfolio_code}\n"

            # Display period with actual dates from response
            if begin_date:
                output += f"Period: {begin_date} to {end_date}\n"
            else:
                # If begin_date was not provided, try to get actual begin date from response
                if result.begin_date:
                    output += f"Period: From portfolio inception ({result.begin_date}) to {end_date}\n"
                else:
                    output += f"Period: From portfolio inception to {end_date}\n"

            output += f"Report Currency: {schema.report_currency.value}\n"
            output += f"Calculation Method: Modified Dietz\n\n"

            output += "=" * 80 + "\n"
            output += "PORTFOLIO PERFORMANCE METRICS:\n"
            output += "=" * 80 + "\n\n"

            # Display key performance metrics

            # Beginning NAV
            if result.begin_nav:
                begin_nav_value = float(result.begin_nav) if result.begin_nav else 0
                output += f"Beginning Net Asset Value (NAV):\n"
                output += f"  {schema.report_currency.value} {begin_nav_value:,.2f}\n"
                output += f"  (Portfolio value at the start of the period)\n\n"
            else:
                output += "Beginning Net Asset Value (NAV): Not available\n\n"

            # Ending NAV
            if result.end_nav:
                end_nav_value = float(result.end_nav) if result.end_nav else 0
                output += f"Ending Net Asset Value (NAV):\n"
                output += f"  {schema.report_currency.value} {end_nav_value:,.2f}\n"
                output += f"  (Portfolio value at the end of the period)\n\n"
            else:
                output += "Ending Net Asset Value (NAV): Not available\n\n"

            # Portfolio Return
            if result.grand_return:
                return_value = (
                    float(result.grand_return) * 100 if result.grand_return else 0
                )
                output += f"Portfolio Return:\n"
                output += f"  {return_value:.2f}%\n"
                if return_value > 0:
                    output += f"  (Positive performance - portfolio gained value)\n\n"
                elif return_value < 0:
                    output += f"  (Negative performance - portfolio lost value)\n\n"
                else:
                    output += f"  (Neutral performance - portfolio value unchanged)\n\n"
            else:
                output += "Portfolio Return: Not available\n\n"

            # Absolute P&L
            if result.grand_absolute_pl:
                pl_value = (
                    float(result.grand_absolute_pl) if result.grand_absolute_pl else 0
                )
                output += f"Absolute Profit/Loss:\n"
                output += f"  {schema.report_currency.value} {pl_value:,.2f}\n"
                if pl_value > 0:
                    output += f"  (Net profit for the period)\n\n"
                elif pl_value < 0:
                    output += f"  (Net loss for the period)\n\n"
                else:
                    output += f"  (Break-even for the period)\n\n"
            else:
                output += "Absolute Profit/Loss: Not available\n\n"

            # Cash Flow Information (if available)
            output += "-" * 60 + "\n"
            output += "CASH FLOW INFORMATION:\n"
            output += "-" * 60 + "\n\n"

            if result.grand_cash_flow:
                cash_flow_value = (
                    float(result.grand_cash_flow) if result.grand_cash_flow else 0
                )
                output += f"Net Cash Flow: {schema.report_currency.value} {cash_flow_value:,.2f}\n"
            else:
                output += "Net Cash Flow: {schema.report_currency.value} 0.00\n"

            if result.grand_cash_inflow:
                inflow_value = (
                    float(result.grand_cash_inflow) if result.grand_cash_inflow else 0
                )
                output += f"Total Cash Inflows: {schema.report_currency.value} {inflow_value:,.2f}\n"
            else:
                output += "Total Cash Inflows: {schema.report_currency.value} 0.00\n"

            if result.grand_cash_outflow:
                outflow_value = (
                    float(result.grand_cash_outflow) if result.grand_cash_outflow else 0
                )
                output += f"Total Cash Outflows: {schema.report_currency.value} {outflow_value:,.2f}\n"
            else:
                output += "Total Cash Outflows: {schema.report_currency.value} 0.00\n"

            if result.grand_cash_flow_weighted:
                cf_weighted = (
                    float(result.grand_cash_flow_weighted)
                    if result.grand_cash_flow_weighted
                    else 0
                )
                output += f"Cash Flow Weighted Return: {cf_weighted:.2f}%\n"

            output += "\n" + "=" * 80 + "\n"
            output += "PERFORMANCE SUMMARY:\n"
            output += "=" * 80 + "\n"

            # Performance interpretation
            if result.grand_return and result.grand_absolute_pl:
                return_pct = float(result.grand_return) * 100
                abs_pl = float(result.grand_absolute_pl)

                output += f"\nThe portfolio '{display_portfolio_code}' "

                if begin_date:
                    output += f"from {begin_date} to {end_date} "
                else:
                    # Show actual inception date if available
                    if result.begin_date:
                        output += f"from inception ({result.begin_date}) to {end_date} "
                    else:
                        output += f"from inception to {end_date} "

                if return_pct > 0:
                    output += f"generated a positive return of {return_pct:.2f}%, "
                    output += f"resulting in a profit of {schema.report_currency.value} {abs_pl:,.2f}.\n"
                elif return_pct < 0:
                    output += f"had a negative return of {return_pct:.2f}%, "
                    output += f"resulting in a loss of {schema.report_currency.value} {abs(abs_pl):,.2f}.\n"
                else:
                    output += f"had a flat performance with 0% return.\n"

                # Add NAV change if both are available
                if result.begin_nav and result.end_nav:
                    begin_nav = float(result.begin_nav)
                    end_nav = float(result.end_nav)
                    nav_change = end_nav - begin_nav
                    nav_change_pct = (
                        (nav_change / begin_nav * 100) if begin_nav != 0 else 0
                    )

                    output += f"\nThe portfolio's Net Asset Value changed from "
                    output += f"{schema.report_currency.value} {begin_nav:,.2f} to "
                    output += f"{schema.report_currency.value} {end_nav:,.2f}, "
                    output += (
                        f"a change of {schema.report_currency.value} {nav_change:,.2f} "
                    )
                    output += f"({nav_change_pct:+.2f}%).\n"

            output += "\n" + "=" * 80 + "\n"
            output += (
                "Note: This performance report shows portfolio-level metrics only.\n"
            )
            output += "For individual instrument performance, please use the P&L Report tool.\n"

            # -------------------------------------------------------------
            # Enrich with Balance Report + Price History availability
            # -------------------------------------------------------------
            try:
                # Build a balance report request to discover instruments present in portfolio
                if ACTIVATE_PUBLIC_NAME:
                    account_mode = 1
                else:
                    # accumulate over all accounts
                    account_mode = 0

                bl_request = BackendBalanceReportItems(
                    account_mode=account_mode,
                    accounts=[],
                    accounts_cash=[],
                    accounts_position=[],
                    allocation_mode=0,
                    calculate_pl=True,
                    cost_method=1,
                    custom_fields_to_calculate="Asset Type",
                    date_field=DateField.transaction_date,
                    expression_iterations_count=1,
                    pl_first_date=None,
                    portfolio_mode=1,
                    portfolios=[schema.portfolio_code],
                    pricing_policy="com.finmars.standard-pricing:standard",
                    report_currency=schema.report_currency.value,
                    report_date=end_date,
                    report_type=1,
                    frontend_request_options={"groups_types": [], "groups_values": []},
                    strategies1=[],
                    strategies2=[],
                    strategies3=[],
                    strategy1_mode=0,
                    strategy2_mode=0,
                    strategy3_mode=0,
                    page=1,
                    page_size=500,
                    report_instance_id=None,
                )

                response_bl: BackendBalanceReportItems = (
                    await self.client.balance_report.get_balance_report_items(
                        bl_request
                    )
                )

                # Extract instrument ids and optional names from balance report items
                items_bl = response_bl.items or []
                if isinstance(items_bl, str):
                    try:
                        items_bl = json.loads(items_bl)
                    except Exception:
                        items_bl = []

                instrument_ids: list[int] = []
                inst_name_from_bl: dict[int, str] = {}
                for it in items_bl:
                    if not isinstance(it, dict):
                        continue
                    inst_id = it.get("instrument.id")
                    if inst_id is None:
                        continue
                    try:
                        inst_id = int(inst_id)
                    except Exception:
                        continue
                    if inst_id not in instrument_ids:
                        instrument_ids.append(inst_id)
                    # Prefer public_name, then name, then user_code
                    name = (
                        it.get("instrument.public_name")
                        or it.get("instrument.name")
                        or it.get("instrument.user_code")
                    )
                    if name:
                        inst_name_from_bl[inst_id] = name

                # If no instruments found, still show a section with empty state
                output += "\n" + "=" * 80 + "\n"
                output += "INSTRUMENT PRICE AVAILABILITY:\n"
                output += "=" * 80 + "\n\n"

                if not instrument_ids:
                    output += "No instrument positions detected from Balance Report; cannot check prices.\n"
                else:
                    # Query price history presence for the discovered instruments
                    price_info = await self.client.instrument_price_history.list_grouped_by_instruments(
                        begin_date=str(
                            begin_date or result.begin_date or schema.begin_date or ""
                        ),
                        end_date=str(end_date),
                        instrument_ids=instrument_ids,
                        pricing_policy_user_code=bl_request.pricing_policy,
                        page_size=10,
                        only_first_page=True,
                    )

                    gmap = price_info.get("grouped_by_instrument", {}) or {}
                    pp_code = price_info.get("pricing_policy_user_code")
                    if pp_code:
                        output += f"Pricing Policy for check: {pp_code}\n"

                    # Summary coverage metrics (binary only)
                    total_checked = len(instrument_ids)
                    with_prices = 0
                    without_prices = 0

                    for inst_id in instrument_ids:
                        group = gmap.get(inst_id) or {}
                        c = int(group.get("count", 0) or 0)
                        if c == 0:
                            without_prices += 1
                        else:
                            with_prices += 1

                    coverage_pct = (
                        (with_prices / total_checked * 100.0) if total_checked else 0.0
                    )

                    output += (
                        f"Checked instruments: {total_checked}. With prices: {with_prices} ({coverage_pct:.1f}%). "
                        f"Without prices: {without_prices}.\n\n"
                    )

                    for inst_id in instrument_ids:
                        group = gmap.get(inst_id) or {}
                        count = int(group.get("count", 0) or 0)
                        public_name = (
                            group.get("instrument_public_name")
                            or inst_name_from_bl.get(inst_id)
                            or f"Instrument {inst_id}"
                        )

                        output += f"- {public_name} (ID: {inst_id}):\n"
                        if count == 0:
                            output += "  Price history: no available prices for the selected period.\n"
                        else:
                            output += (
                                "  Price history: prices were present in the period.\n"
                            )

                    # If any instrument has no prices in the selected period, try to find feasible date ranges
                    if without_prices > 0:
                        output += "\n" + "-" * 60 + "\n"
                        output += (
                            "PRICE WINDOW SEARCH (all instruments must have prices):\n"
                        )
                        output += "-" * 60 + "\n\n"

                        # Helper to fetch earliest and latest price dates for each instrument
                        async def _fetch_bounds(iid: int):
                            try:
                                earliest_resp = await self.client.instrument_price_history.list_price_history(
                                    ordering="date",
                                    page=1,
                                    page_size=1,
                                    instrument=iid,
                                    pricing_policy=bl_request.pricing_policy,
                                )
                                latest_resp = await self.client.instrument_price_history.list_price_history(
                                    ordering="-date",
                                    page=1,
                                    page_size=1,
                                    instrument=iid,
                                    pricing_policy=bl_request.pricing_policy,
                                )
                                earliest_it = (earliest_resp.results or [None])[0]
                                latest_it = (latest_resp.results or [None])[0]
                                earliest_date_str = (
                                    str(getattr(earliest_it, "date", ""))
                                    if earliest_it
                                    else None
                                )
                                latest_date_str = (
                                    str(getattr(latest_it, "date", ""))
                                    if latest_it
                                    else None
                                )
                                total_cnt = int(
                                    earliest_resp.count or latest_resp.count or 0
                                )
                                return (
                                    iid,
                                    earliest_date_str,
                                    latest_date_str,
                                    total_cnt,
                                )
                            except Exception:
                                return iid, None, None, 0

                        bounds = await asyncio.gather(
                            *[_fetch_bounds(iid) for iid in instrument_ids]
                        )

                        # Prepare per-instrument summary and compute intersection window
                        earliest_map = {}
                        latest_map = {}
                        total_zero: list[int] = []

                        output += "Earliest/Latest price dates per instrument (by pricing policy):\n"
                        for iid, e_str, l_str, cnt in bounds:
                            public_name = (
                                (gmap.get(iid) or {}).get("instrument_public_name")
                                or inst_name_from_bl.get(iid)
                                or f"Instrument {iid}"
                            )
                            if cnt == 0 or not e_str or not l_str:
                                output += f"- {public_name} (ID: {iid}): no price history found at all.\n"
                                total_zero.append(iid)
                                earliest_map[iid] = None
                                latest_map[iid] = None
                                continue

                            # Parse dates to date objects
                            try:
                                e_dt = datetime.strptime(e_str, "%Y-%m-%d").date()
                            except Exception:
                                e_dt = None
                            try:
                                l_dt = datetime.strptime(l_str, "%Y-%m-%d").date()
                            except Exception:
                                l_dt = None

                            earliest_map[iid] = e_dt
                            latest_map[iid] = l_dt
                            output += f"- {public_name} (ID: {iid}): first={e_str or '-'}; last={l_str or '-'}\n"

                        if total_zero:
                            output += "\nAt least one instrument has no price history at all; cannot find a common period where ALL instruments have prices.\n"
                            output += "Please update pricing sources/policy or exclude problematic instruments to proceed.\n"
                        else:
                            # Compute global intersection window across all instruments
                            all_earliest = [
                                d for d in earliest_map.values() if d is not None
                            ]
                            all_latest = [
                                d for d in latest_map.values() if d is not None
                            ]

                            if all_earliest and all_latest:
                                intersect_start = max(all_earliest)
                                intersect_end = min(all_latest)

                                if intersect_start <= intersect_end:
                                    output += f"\nCommon price coverage across ALL instruments: {intersect_start} to {intersect_end}.\n"

                                    # Propose recommended dates by minimally adjusting the user's selection
                                    # If user provided begin_date -> clamp up to intersection start; else use intersection start
                                    recommended_begin = intersect_start
                                    if begin_date:
                                        recommended_begin = max(
                                            begin_date, intersect_start
                                        )

                                    # End date must not exceed intersection end
                                    recommended_end = min(end_date, intersect_end)

                                    if recommended_begin <= recommended_end:
                                        # Present ranges and how to run
                                        output += f"\nValid begin_date range: {intersect_start} .. {recommended_end}\n"
                                        output += f"Valid end_date range: {recommended_begin} .. {intersect_end}\n"
                                        output += "\nRecommended next step (no auto-rerun performed):\n"
                                        output += f"- Re-run Performance Report with begin_date={recommended_begin} and end_date={recommended_end}.\n"
                                        output += "- Keep the same portfolio, currency, and pricing policy.\n"
                                        # Provide a concrete invocation hint
                                        display_begin = recommended_begin.isoformat()
                                        display_end = recommended_end.isoformat()
                                        output += "\nHow to run (example):\n"
                                        output += f"  - Use get_performance_report with portfolio_code='{schema.portfolio_code}', report_currency='{schema.report_currency.value}', begin_date='{display_begin}', end_date='{display_end}'.\n"
                                    else:
                                        output += "\nNo feasible pair within the common coverage when respecting the current end_date. "
                                        output += f"Consider choosing end_date on or before {intersect_end} and begin_date on or after {intersect_start}.\n"
                                else:
                                    output += "\nNo overlap between instruments' price histories; cannot find a common period where ALL have prices.\n"
                                    output += "Adjust pricing policy or investigate missing price data for the listed instruments.\n"
                            else:
                                output += "\nInsufficient data to compute a common price window across instruments.\n"

            except Exception as e:
                logger.warning(
                    f"Balance/Price enrichment skipped due to error: {e}\n{traceback.format_exc()}"
                )

            return output, artifact

        except Exception as e:
            exc = traceback.format_exc()
            logger.error(exc)
            error_msg = f"Error getting performance report for portfolio {kwargs.get('portfolio_code')}: {str(e)}"
            if "input_str" in locals():
                error_msg += f"\n\nFull request sent:\n{input_str}"
            return error_msg, None


def build_performance_report_tools(
    finmars_token: str = None, space: str = None, realm: str = None
) -> List[BaseTool]:
    """Build and return performance report tools"""
    toolkit = PerformanceReportToolkit(
        finmars_token=finmars_token, space=space, realm=realm
    )

    tools = [
        StructuredTool.from_function(
            name="get_performance_report",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_performance_report(**kwargs)
            ),
            coroutine=toolkit._get_performance_report,
            description=(
                "Get a performance report showing portfolio-level performance metrics over a specified period. "
                "Use this tool to:\n"
                "- Analyze overall portfolio performance (NOT individual instruments)\n"
                "- Calculate portfolio returns and absolute profit/loss\n"
                "- Track Net Asset Value (NAV) changes\n"
                "- View cash flow impacts on performance\n"
                "- Measure portfolio performance from inception or a specific date\n"
                "\n"
                "The report provides:\n"
                "- Beginning NAV: Portfolio value at the start of the period\n"
                "- Ending NAV: Portfolio value at the end of the period\n"
                "- Portfolio Return: Percentage return for the period\n"
                "- Absolute P&L: Total profit or loss in the report currency\n"
                "- Cash Flow metrics: Inflows, outflows, and net cash flow\n"
                "\n"
                "IMPORTANT:\n"
                "- This tool shows PORTFOLIO-LEVEL performance only\n"
                "- For individual instrument/position performance, use the P&L Report tool\n"
                "- Begin date is optional - if not provided, performance is calculated from portfolio inception\n"
                "\n"
                "Example questions this tool can answer:\n"
                "- What is the performance of portfolio X for 2024?\n"
                "- How much profit/loss did the portfolio generate this year?\n"
                "- What is the portfolio return since inception?\n"
                "- What was the NAV change for the portfolio?\n"
                "- How did portfolio Y perform in Q1 2024?\n"
                "\n"
                "When to use this tool vs P&L Report:\n"
                "- Performance Report: Overall portfolio metrics, returns, NAV\n"
                "- P&L Report: Individual instrument performance, position-level P&L"
            ),
            args_schema=GetPerformanceReportSchema,
            response_format="content_and_artifact",
        ),
    ]

    return tools
