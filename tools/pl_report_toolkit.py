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
        description="The currency for the report (USD or EUR)"
    )
    pl_first_date: str = Field(
        description="The start date for P/L calculation in YYYY-MM-DD format (e.g., '2024-01-01')"
    )
    report_date: Optional[str] = Field(
        default=None,
        description="The end date for P/L calculation in YYYY-MM-DD format (e.g., '2024-12-31'). If not provided, today's date will be used."
    )
    sort_by: Optional[SortBy] = Field(
        default=None,
        description="Sort results by instrument_name, position_size, amount_invested, market_value, principle, or return_percentage"
    )
    descending: bool = Field(
        default=True,
        description="Sort in descending order (highest to lowest). Set to false for ascending order."
    )
    min_return_percentage: Optional[float] = Field(
        default=None,
        description="Filter to show only positions with return percentage above this threshold (e.g., 10.0 for 10%)"
    )
    max_return_percentage: Optional[float] = Field(
        default=None,
        description="Filter to show only positions with return percentage below this threshold (e.g., -10.0 for -10%)"
    )


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
                pl_first_date = datetime.strptime(schema.pl_first_date, "%Y-%m-%d").date()
            except ValueError:
                return f"Error: Invalid pl_first_date format. Please use YYYY-MM-DD format (e.g., '2024-01-01')", None
            
            if schema.report_date:
                try:
                    report_date = datetime.strptime(schema.report_date, "%Y-%m-%d").date()
                except ValueError:
                    return f"Error: Invalid report_date format. Please use YYYY-MM-DD format (e.g., '2024-12-31')", None
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
                pricing_policy="com.finmars.standard-pricing:master",
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
            )
            input_str = request_data.model_dump_json()
            
            # Make the API call
            result: PLReportItems = await self.client.pl_report.create_pl_report(request_data)
            
            # Create artifacts
            request_dict = json.loads(request_data.model_dump_json())
            cleaned_request = drop_empty_fields(request_dict)
            response_dict = json.loads(result.model_dump_json())
            
            # Create the artifact in the required format
            artifact = {
                "request_data": cleaned_request,
                "response_data": response_dict
            }

            report_currency = result.report_currency

            # Post-process: Extract the required information
            items = result.items if hasattr(result, 'items') else []
            
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
                output += "No positions found in this portfolio for the specified period.\n"
                return output, artifact
            
            output += "Profit & Loss Analysis:\n"
            output += "=" * 100 + "\n\n"
            
            total_invested = 0.0
            total_market_value = 0.0
            total_principle = 0.0
            positions = []

            # Process each item to extract P/L information
            for item in items:
                if isinstance(item, dict):
                    # Extract instrument information
                    instrument_code = item.get("instrument.user_code")
                    if instrument_code is None:
                        continue
                    instrument_name = item.get("instrument.name", "Unknown")
                    
                    # Extract P/L fields according to the instructions
                    position_size = item.get("position_size", 0)  # number of shares/bonds
                    net_cost_price = item.get("net_cost_price", 0)  # price at which we bought
                    amount_invested = item.get("amount_invested_fixed", 0)  # total amount invested (negative for long)
                    market_value = item.get("market_value", 0)  # current position value
                    principle = item.get("principle", 0)  # profit/loss (market_value - amount_invested)
                    
                    # Additional useful fields
                    realized_pl = item.get("realized_pl", 0)
                    unrealized_pl = item.get("unrealized_pl", 0)
                    total_pl = item.get("total", principle)  # sometimes labeled as 'total'
                    current_price = item.get("current_price", 0)
                    
                    # Calculate return percentage
                    return_percentage = 0.0
                    if amount_invested != 0:
                        # Note: amount_invested is negative for long positions
                        return_percentage = (principle / abs(amount_invested)) * 100
                    
                    # Apply filters if specified
                    if schema.min_return_percentage is not None and return_percentage < schema.min_return_percentage:
                        continue
                    if schema.max_return_percentage is not None and return_percentage > schema.max_return_percentage:
                        continue
                    
                    positions.append({
                        "code": instrument_code,
                        "name": instrument_name,
                        "position_size": position_size,
                        "net_cost_price": net_cost_price,
                        "current_price": current_price,
                        "amount_invested": amount_invested,
                        "market_value": market_value,
                        "principle": principle,
                        "realized_pl": realized_pl,
                        "unrealized_pl": unrealized_pl,
                        "return_percentage": return_percentage
                    })
                    
                    # Accumulate totals
                    if isinstance(amount_invested, (int, float)):
                        total_invested += amount_invested
                    if isinstance(market_value, (int, float)):
                        total_market_value += market_value
                    if isinstance(principle, (int, float)):
                        total_principle += principle
            
            # Sort positions if requested
            if schema.sort_by:
                def sort_key(pos):
                    if schema.sort_by == SortBy.INSTRUMENT_NAME:
                        return pos['name'].lower()
                    elif schema.sort_by == SortBy.POSITION_SIZE:
                        return pos['position_size'] if isinstance(pos['position_size'], (int, float)) else -float('inf')
                    elif schema.sort_by == SortBy.AMOUNT_INVESTED:
                        return abs(pos['amount_invested']) if isinstance(pos['amount_invested'], (int, float)) else -float('inf')
                    elif schema.sort_by == SortBy.MARKET_VALUE:
                        return pos['market_value'] if isinstance(pos['market_value'], (int, float)) else -float('inf')
                    elif schema.sort_by == SortBy.PRINCIPLE:
                        return pos['principle'] if isinstance(pos['principle'], (int, float)) else -float('inf')
                    elif schema.sort_by == SortBy.RETURN_PERCENTAGE:
                        return pos['return_percentage'] if isinstance(pos['return_percentage'], (int, float)) else -float('inf')
                    return 0
                
                positions.sort(key=sort_key, reverse=schema.descending if schema.sort_by != SortBy.INSTRUMENT_NAME else not schema.descending)
                
                # Add sorting info to output
                output += f"Sorted by: {schema.sort_by.value} ({'descending' if schema.descending else 'ascending'})\n"
                if schema.min_return_percentage is not None or schema.max_return_percentage is not None:
                    output += f"Filtered by return percentage: "
                    if schema.min_return_percentage is not None:
                        output += f"min={schema.min_return_percentage}%"
                    if schema.max_return_percentage is not None:
                        if schema.min_return_percentage is not None:
                            output += ", "
                        output += f"max={schema.max_return_percentage}%"
                    output += "\n"
                output += "=" * 100 + "\n\n"
            
            # Format output for each position
            for pos in positions:
                # Parse instrument name to extract bond characteristics
                instrument_name = pos['name']
                instrument_code = pos['code']
                
                # Extract bond features if present in name
                bond_features = []
                if '<' in instrument_name and '>' in instrument_name:
                    features_start = instrument_name.find('<')
                    features_end = instrument_name.find('>')
                    features_str = instrument_name[features_start+1:features_end]
                    bond_features = [f.strip() for f in features_str.split(',')]
                    clean_name = instrument_name[:features_start].strip()
                else:
                    clean_name = instrument_name
                
                output += f"Instrument: {clean_name}\n"
                output += f"  - Security Code: {instrument_code}\n"
                
                # Explain bond features if present
                if bond_features:
                    output += "  - Bond Features:\n"
                    for feature in bond_features:
                        if feature.lower() == 'unsec':
                            output += "    • Unsecured (unsec): No collateral backing the bond\n"
                        elif feature.lower() == 'sink':
                            output += "    • Sinking Fund (sink): Issuer periodically retires portions of the bond\n"
                        elif feature.lower() == 'step-up':
                            output += "    • Step-Up Coupon (step-up): Interest rate increases over time\n"
                        elif 'step cpn' in feature.lower():
                            output += "    • Step Coupon (step cpn): Variable interest rate structure\n"
                        elif feature.lower() == 'restruct':
                            output += "    • Restructured (restruct): Bond terms have been modified\n"
                        else:
                            output += f"    • {feature}\n"
                
                # Position details
                if isinstance(pos['position_size'], (int, float)):
                    if pos['position_size'] == 0:
                        output += f"  - Position Status: CLOSED (0 shares/units held)\n"
                    else:
                        output += f"  - Position Size: {pos['position_size']:,.2f} shares/units"
                        if pos['position_size'] < 0:
                            output += " (SHORT POSITION)\n"
                        else:
                            output += " (LONG POSITION)\n"
                
                # Cost basis
                if isinstance(pos['net_cost_price'], (int, float)) and pos['net_cost_price'] != 0:
                    output += f"  - Average Cost Price: ${pos['net_cost_price']:,.2f}"
                    output += " (price per unit when purchased)\n"
                
                if isinstance(pos['current_price'], (int, float)) and pos['current_price'] != 0:
                    output += f"  - Current Market Price: ${pos['current_price']:,.2f}"
                    output += " (latest market price per unit)\n"
                
                # Investment amount
                if isinstance(pos['amount_invested'], (int, float)):
                    if pos['amount_invested'] == 0 and pos['position_size'] == 0:
                        output += "  - Amount Invested: $0.00 (position closed)\n"
                    else:
                        output += f"  - Total Amount Invested: ${pos['amount_invested']:,.2f}"
                        if pos['amount_invested'] < 0:
                            output += "\n    (Negative = money paid out for long position)\n"
                        elif pos['amount_invested'] > 0:
                            output += "\n    (Positive = money received for short position)\n"
                        else:
                            output += "\n"
                
                # Current value
                if isinstance(pos['market_value'], (int, float)):
                    output += f"  - Current Market Value: ${pos['market_value']:,.2f}"
                    if pos['position_size'] != 0:
                        output += " (position_size × current_price)\n"
                    else:
                        output += " (position closed)\n"
                
                # P/L information
                if isinstance(pos['principle'], (int, float)):
                    output += f"  - Total Profit/Loss: ${pos['principle']:,.2f}"
                    if pos['principle'] > 0:
                        output += " ✓ PROFIT"
                    elif pos['principle'] < 0:
                        output += " ✗ LOSS"
                    else:
                        output += " = BREAK EVEN"
                    
                    if pos['position_size'] == 0 and pos['principle'] == 0:
                        output += " (closed position, no P/L during period)\n"
                    else:
                        output += "\n    (Calculated as: market_value - amount_invested)\n"
                
                # Return percentage
                output += f"  - Return Percentage: {pos['return_percentage']:.2f}%"
                if pos['amount_invested'] != 0:
                    output += " (profit/loss ÷ |amount_invested| × 100)\n"
                else:
                    output += " (no investment base for calculation)\n"
                
                # Realized vs Unrealized
                if isinstance(pos['realized_pl'], (int, float)) and pos['realized_pl'] != 0:
                    output += f"  - Realized P/L: ${pos['realized_pl']:,.2f}"
                    output += " (gains/losses from completed transactions)\n"
                if isinstance(pos['unrealized_pl'], (int, float)) and pos['unrealized_pl'] != 0:
                    output += f"  - Unrealized P/L: ${pos['unrealized_pl']:,.2f}"
                    output += " (paper gains/losses on current holdings)\n"
                
                output += "\n"
            
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
            
            # Calculate overall return
            if total_invested != 0:
                overall_return = (total_principle / abs(total_invested)) * 100
                output += f"Overall Return: {overall_return:.2f}%\n"
            
            output += f"Number of Positions: {len(positions)}\n"
            
            # Performance summary
            profitable_positions = [p for p in positions if p['principle'] > 0]
            losing_positions = [p for p in positions if p['principle'] < 0]
            
            output += f"\nPerformance Summary:\n"
            output += f"- Profitable Positions: {len(profitable_positions)}\n"
            output += f"- Losing Positions: {len(losing_positions)}\n"
            output += f"- Break Even Positions: {len(positions) - len(profitable_positions) - len(losing_positions)}\n"
            
            if profitable_positions:
                best_performer = max(profitable_positions, key=lambda x: x['return_percentage'])
                output += f"- Best Performer: {best_performer['name']} ({best_performer['return_percentage']:.2f}%)\n"
            
            if losing_positions:
                worst_performer = min(losing_positions, key=lambda x: x['return_percentage'])
                output += f"- Worst Performer: {worst_performer['name']} ({worst_performer['return_percentage']:.2f}%)\n"
            
            return output, artifact
            
        except Exception as e:
            exc = traceback.format_exc()
            logger.error(exc)
            return f"Error getting P/L report for portfolio {kwargs.get('portfolio_code')}: {str(e)}", None


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
                "- Filter positions by return percentage thresholds\n"
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
                "- sort_by: Sort results by various metrics\n"
                "- min_return_percentage/max_return_percentage: Filter by returns\n"
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
                "- principle: Total P/L (market_value - amount_invested), positive = profit\n"
                "- return_percentage: (principle / |amount_invested|) × 100"
            ),
            args_schema=GetPLReportSchema,
            response_format="content_and_artifact",
        ),
    ]
    
    return tools