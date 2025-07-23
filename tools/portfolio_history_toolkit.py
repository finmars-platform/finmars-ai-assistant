import asyncio
import json
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool

from libs.client.finmars_client import FinmarsPortfolioClient
from .shared_models import drop_empty_fields


class ListPortfolioHistorySchema(BaseModel):
    """Input schema for listing portfolio history records"""

    ordering: Optional[str] = Field(
        default=None,
        description="Field to use for ordering results (e.g., 'id', '-created_at', 'portfolio')",
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page (max 100)"
    )


class GetPortfolioHistorySchema(BaseModel):
    """Input schema for getting a specific portfolio history record"""

    history_id: int = Field(
        description="The ID of the portfolio history record to retrieve"
    )


class PortfolioHistoryToolkit:
    """Toolkit for portfolio history-related operations using the Finmars API"""

    def __init__(self):
        self.client = FinmarsPortfolioClient()

    async def _list_portfolio_history(self, **kwargs) -> tuple[str, dict | list | None]:
        """List all portfolio history records with pagination and filtering"""
        try:
            schema = ListPortfolioHistorySchema(**kwargs)
            result = await self.client.portfolio_history.list_portfolio_history(
                ordering=schema.ordering, page=schema.page, page_size=schema.page_size
            )

            # Create artifacts
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size,
            }
            cleaned_request = drop_empty_fields(request_data)
            response_dict = json.loads(result.model_dump_json())

            # Create the artifact in the required format
            artifact = {"request_data": cleaned_request, "response_data": response_dict}

            return result.model_dump_json(), artifact

            # output = f"Found {result.count} total portfolio history records.\n"
            # if result.results:
            #     output += f"Showing {len(result.results)} history records on page {schema.page}:\n\n"
            #     for history in result.results:
            #         output += f"ID: {history.id}\n"
            #         output += f"Portfolio: {history.portfolio}\n"
            #         output += f"Currency: {history.currency}\n"
            #         if hasattr(history, "date") and history.date:
            #             output += f"Date: {history.date}\n"
            #         if hasattr(history, "value") and history.value is not None:
            #             output += f"Value: {history.value}\n"
            #         output += f"Created: {history.created_at}\n"
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No portfolio history records found.\n"
            #
            # if result.next:
            #     output += (
            #         f"\nNext page available. Use page={schema.page + 1} to continue."
            #     )
            #
            # return output
        except Exception as e:
            return f"Error listing portfolio history: {str(e)}", None

    async def _get_portfolio_history(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get a specific portfolio history record by ID"""
        try:
            schema = GetPortfolioHistorySchema(**kwargs)
            history = await self.client.portfolio_history.get_portfolio_history(
                schema.history_id
            )

            # Create artifacts
            request_data = {"history_id": schema.history_id}
            cleaned_request = drop_empty_fields(request_data)
            response_dict = json.loads(history.model_dump_json())

            # Create the artifact in the required format
            artifact = {"request_data": cleaned_request, "response_data": response_dict}

            return history.model_dump_json(), artifact

            # output = f"Portfolio History Record Details:\n"
            # output += f"ID: {history.id}\n"
            # output += f"Portfolio: {history.portfolio}\n"
            # output += f"Currency: {history.currency}\n"
            # if hasattr(history, "date") and history.date:
            #     output += f"Date: {history.date}\n"
            # if hasattr(history, "value") and history.value is not None:
            #     output += f"Value: {history.value}\n"
            # if hasattr(history, "nav") and history.nav is not None:
            #     output += f"NAV: {history.nav}\n"
            # if hasattr(history, "nav_per_share") and history.nav_per_share is not None:
            #     output += f"NAV Per Share: {history.nav_per_share}\n"
            # if (
            #     hasattr(history, "shares_outstanding")
            #     and history.shares_outstanding is not None
            # ):
            #     output += f"Shares Outstanding: {history.shares_outstanding}\n"
            # output += f"Created: {history.created_at}\n"
            # if history.updated_at:
            #     output += f"Updated: {history.updated_at}\n"
            #
            # return output
        except Exception as e:
            return (
                f"Error getting portfolio history record {kwargs.get('history_id')}: {str(e)}",
                None,
            )


def build_portfolio_history_tools() -> List[BaseTool]:
    """Build and return portfolio history-related tools"""
    toolkit = PortfolioHistoryToolkit()

    tools = [
        StructuredTool.from_function(
            name="list_portfolio_history",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_portfolio_history(**kwargs)
            ),
            coroutine=toolkit._list_portfolio_history,
            description=(
                "List all portfolio history records with optional filtering and pagination. "
                "Returns historical portfolio data including ID, portfolio, currency, date, value, "
                "and timestamps. Supports ordering by various fields and pagination for large datasets. "
                "Useful for analyzing portfolio performance over time and historical trends."
            ),
            args_schema=ListPortfolioHistorySchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_history",
            func=lambda **kwargs: asyncio.run(toolkit._get_portfolio_history(**kwargs)),
            coroutine=toolkit._get_portfolio_history,
            description=(
                "Get detailed information about a specific portfolio history record by its ID. "
                "Returns complete historical data including portfolio, currency, date, value, "
                "NAV information, shares outstanding, and timestamps. Useful for detailed "
                "analysis of specific portfolio states at particular points in time."
            ),
            args_schema=GetPortfolioHistorySchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
    ]

    return tools
