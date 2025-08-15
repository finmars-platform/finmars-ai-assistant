import asyncio
import json
import traceback
from datetime import datetime
from typing import List, Optional

from langchain_core.tools import StructuredTool, BaseTool
from pydantic import BaseModel, Field

from libs.client.finmars_client import FinmarsPortfolioClient
from libs.logger.logger import logger
from libs.schema.via_data_model_codegen.report_schema import PerformanceReport
from .shared_models import ReportCurrency, drop_empty_fields


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

    def __init__(self):
        self.client = FinmarsPortfolioClient()

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
            output += f"RESPONSE:\nPerformance Report for Portfolio: {schema.portfolio_code}\n"

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

                output += f"\nThe portfolio '{schema.portfolio_code}' "

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

            return output, artifact

        except Exception as e:
            exc = traceback.format_exc()
            logger.error(exc)
            error_msg = f"Error getting performance report for portfolio {kwargs.get('portfolio_code')}: {str(e)}"
            if "input_str" in locals():
                error_msg += f"\n\nFull request sent:\n{input_str}"
            return error_msg, None


def build_performance_report_tools() -> List[BaseTool]:
    """Build and return performance report tools"""
    toolkit = PerformanceReportToolkit()

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
