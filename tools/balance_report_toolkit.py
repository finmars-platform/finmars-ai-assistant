import asyncio
import json
import traceback
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool

from libs.client.finmars_client import FinmarsPortfolioClient
from libs.logger.logger import logger
from libs.schema.via_data_model_codegen.report_schema import BackendBalanceReportItems, DateField


class ReportCurrency(str, Enum):
    """Supported report currencies"""
    USD = "USD"
    EUR = "EUR"


class GetBalanceReportSchema(BaseModel):
    """Input schema for getting balance report"""
    
    portfolio_code: str = Field(
        description="The portfolio user code (user_code from portfolio)"
    )
    report_currency: ReportCurrency = Field(
        default=ReportCurrency.USD,
        description="The currency for the report (USD or EUR)"
    )


class BalanceReportToolkit:
    """Toolkit for balance report operations using the Finmars API"""
    
    def __init__(self):
        self.client = FinmarsPortfolioClient()
        
    async def _get_balance_report(self, **kwargs) -> str:
        """Get balance report with portfolio holdings information"""
        try:
            schema = GetBalanceReportSchema(**kwargs)
            
            # Pre-process: Build the request according to requirements
            report_date = datetime.now().date()
            
            request_data = BackendBalanceReportItems(
                account_mode=1,
                accounts=[],
                accounts_cash=[],
                accounts_position=[],
                #allocation_detailing=True,
                allocation_mode=0,
                #approach_multiplier=0.5,
                calculate_pl=True,
                #complex_transaction_statuses_filter="booked",
                cost_method=1,
                custom_fields_to_calculate="Asset Type",
                # date_field="transaction_date",
                date_field=DateField.transaction_date,
                #depth_level="base_transaction",
                expression_iterations_count=1,
                pl_first_date=None,
                #pl_include_zero=False,
                portfolio_mode=1,
                portfolios=[schema.portfolio_code],
                pricing_policy="com.finmars.standard-pricing:standard",
                report_currency=schema.report_currency.value,
                report_date=report_date,
                report_type=1,
                #show_balance_exposure_details=True,
                #show_transaction_details=True,
                frontend_request_options={"groups_types": [], "groups_values": []},
                strategies1=[],
                strategies2=[],
                strategies3=[],
                strategy1_mode=0,
                strategy2_mode=0,
                strategy3_mode=0,
                #table_font_size="small",
                #transaction_classes=[],
                page=1,
                page_size=40,
                report_instance_id=None,
                #portfolios_table_data_items=[]
            )
            
            # Make the API call
            result: BackendBalanceReportItems = await self.client.balance_report.get_balance_report_items(request_data)

            report_currency = result.report_currency

            # Post-process: Extract the required information
            items = result.items if hasattr(result, 'items') else []
            
            # If items is a string (JSON), parse it
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except:
                    return f"Error: Could not parse items from response"
            
            # Extract portfolio information
            output = f"Balance Report for Portfolio: {schema.portfolio_code}\n"
            output += f"Report Date: {report_date}\n"
            output += f"Currency: {report_currency}\n\n"
            
            if not items:
                output += "No holdings found in this portfolio.\n"
                return output
            
            output += "Portfolio Holdings:\n"
            output += "=" * 80 + "\n\n"
            
            total_value = 0.0
            holdings = []
            
            # Process each item to extract instrument info
            for item in items:
                if isinstance(item, dict):
                    # Extract instrument information
                    instrument_code = item.get("instrument.user_code")
                    if instrument_code is None:
                        continue
                    instrument_name = item.get("instrument.name", "Unknown")
                    
                    # Extract shares and value information from actual API response
                    shares = item.get("position_size", 0.0) # Count of акций

                    # Выдавать
                    market_value = item.get("market_value", 0.0) # market_value, why sometimes is empty?? `position_size * price`
                    exposure = item.get("exposure", 0.0) # exposure, why sometimes is empty??

                    # Если вдруг чего-то нет, агент должен предложить другую дату и тп
                    # Данные предыдущие, шаг назад, где данные есть
                    # Какие именно шаги нужны, чтобы это получить
                    # `item` <- позиции долларов портфеля
                    
                    if shares != 0:  # Can be negative for short positions
                        holdings.append({
                            "code": instrument_code,
                            "name": instrument_name,
                            "shares": shares,
                            "value": market_value
                        })
                        if shares > 0:
                            total_value += market_value

                    # output += "-" * 80 + "\n"
                    # output += f"Source:\n"
                    # output += json.dumps(item, ensure_ascii=False)
                    # output += "\n" + "-" * 80 + "\n"

            # Calculate allocations and format output
            for holding in holdings:
                output += f"Instrument: {holding['name']} ({holding['code']})\n"
                output += f"  - Shares: {holding['shares']:,.2f}\n"
                output += f"  - Market Value: ${holding['value']:,.2f}\n"
                if holding['value'] > 0:
                    allocation = (holding["value"] / total_value * 100) if total_value > 0 else 0
                    output += f"  - Allocation: {allocation:.2f}%\n\n"
                else:
                    output += f"  - Allocation: Short Position\n\n"
            
            output += "-" * 80 + "\n"
            output += f"Total Portfolio Value: ${total_value:,.2f}\n"
            output += f"Number of Holdings: {len(holdings)}\n"
            return output
            
        except Exception as e:
            exc = traceback.format_exc()
            logger.error(exc)
            return f"Error getting balance report for portfolio {kwargs.get('portfolio_code')}: {str(e)}"


def build_balance_report_tools() -> List[BaseTool]:
    """Build and return balance report tools"""
    toolkit = BalanceReportToolkit()
    
    tools = [
        StructuredTool.from_function(
            name="get_balance_report",
            func=lambda **kwargs: asyncio.run(toolkit._get_balance_report(**kwargs)),
            coroutine=toolkit._get_balance_report,
            description=(
                "The balance report entity represents a report that shows the current balance and holdings of a user's accounts and assets. "
                "This report can be used to provide an overview of the user's financial status at a given point in time. "
                "Each balance report object includes details such as the date and time of the report, "
                "the total balance of the user's accounts and assets, and a list of account "
                "and asset objects with their individual balances."
                "Get balance report for a portfolio showing:\n"
                "- What companies/instruments are in the portfolio\n"
                "- What allocation (%) of each instrument\n"
                "- How many shares for each company/instrument\n"
                "- Total portfolio value and number of holdings\n"
                "- Any other questions related to Balance Report\n"
                "Returns a formatted report with all holdings details."
            ),
            args_schema=GetBalanceReportSchema,
            response_format="content",
        ),
    ]
    
    return tools