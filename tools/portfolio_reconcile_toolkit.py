import asyncio
import json
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool

from libs.client.finmars_client import FinmarsPortfolioClient
from .shared_models import drop_empty_fields


class ListPortfolioReconcileGroupsSchema(BaseModel):
    """Input schema for listing portfolio reconcile groups"""

    ordering: Optional[str] = Field(
        default=None,
        description="Field to use for ordering results (e.g., 'id', '-created_at')",
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page (max 100)"
    )


class GetPortfolioReconcileGroupSchema(BaseModel):
    """Input schema for getting a specific portfolio reconcile group"""

    group_id: int = Field(
        description="The ID of the portfolio reconcile group to retrieve"
    )


class ListPortfolioReconcileHistorySchema(BaseModel):
    """Input schema for listing portfolio reconcile history records"""

    ordering: Optional[str] = Field(
        default=None, description="Field to use for ordering results"
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page"
    )


class GetPortfolioReconcileHistorySchema(BaseModel):
    """Input schema for getting a specific portfolio reconcile history record"""

    history_id: int = Field(
        description="The ID of the portfolio reconcile history record to retrieve"
    )


class ListPortfolioReconcileStatusSchema(BaseModel):
    """Input schema for listing portfolio reconcile status"""

    ordering: Optional[str] = Field(
        default=None, description="Field to use for ordering results"
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page"
    )


class PortfolioReconcileToolkit:
    """Toolkit for portfolio reconciliation-related operations using the Finmars API"""

    def __init__(self):
        self.client = FinmarsPortfolioClient()

    async def _list_portfolio_reconcile_groups(
        self, **kwargs
    ) -> tuple[str, dict | list | None]:
        """List all portfolio reconcile groups with pagination and filtering"""
        try:
            schema = ListPortfolioReconcileGroupsSchema(**kwargs)

            # Extract request parameters
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size,
            }
            cleaned_request = drop_empty_fields(request_data)

            result = (
                await self.client.portfolio_reconcile.list_portfolio_reconcile_groups(
                    ordering=schema.ordering,
                    page=schema.page,
                    page_size=schema.page_size,
                )
            )
            result_json = json.loads(result.model_dump_json())

            # Create artifact
            artifact = {"request_data": cleaned_request, "response_data": result_json}

            return result.model_dump_json(), artifact

            # output = f"Found {result.count} total portfolio reconcile groups.\n"
            # if result.results:
            #     output += f"Showing {len(result.results)} reconcile groups on page {schema.page}:\n\n"
            #     for group in result.results:
            #         output += f"ID: {group.id}\n"
            #         output += f"Name: {group.name}\n"
            #         if group.description:
            #             output += f"Description: {group.description}\n"
            #         if hasattr(group, "status") and group.status:
            #             output += f"Status: {group.status}\n"
            #         output += f"Created: {group.created_at}\n"
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No portfolio reconcile groups found.\n"
            #
            # if result.next:
            #     output += (
            #         f"\nNext page available. Use page={schema.page + 1} to continue."
            #     )
            #
            # return output
        except Exception as e:
            error_msg = f"Error listing portfolio reconcile groups: {str(e)}"
            error_msg += f"\n\nRequest parameters: ordering={kwargs.get('ordering')}, page={kwargs.get('page', 1)}, page_size={kwargs.get('page_size', 10)}"
            return error_msg, None

    async def _get_portfolio_reconcile_group(
        self, **kwargs
    ) -> tuple[str, dict | list | None]:
        """Get a specific portfolio reconcile group by ID"""
        try:
            schema = GetPortfolioReconcileGroupSchema(**kwargs)

            # Extract request parameters
            request_data = {"group_id": schema.group_id}
            cleaned_request = drop_empty_fields(request_data)

            group = await self.client.portfolio_reconcile.get_portfolio_reconcile_group(
                schema.group_id
            )
            group_json = json.loads(group.model_dump_json())

            # Create artifact
            artifact = {"request_data": cleaned_request, "response_data": group_json}

            return group.model_dump_json(), artifact

            # output = f"Portfolio Reconcile Group Details:\n"
            # output += f"ID: {group.id}\n"
            # output += f"Name: {group.name}\n"
            # if group.description:
            #     output += f"Description: {group.description}\n"
            # if hasattr(group, "status") and group.status:
            #     output += f"Status: {group.status}\n"
            # if hasattr(group, "portfolios") and group.portfolios:
            #     output += f"Portfolios: {len(group.portfolios)} items\n"
            # output += f"Created: {group.created_at}\n"
            # if group.updated_at:
            #     output += f"Updated: {group.updated_at}\n"
            #
            # return output
        except Exception as e:
            error_msg = f"Error getting portfolio reconcile group {kwargs.get('group_id')}: {str(e)}"
            error_msg += f"\n\nRequest parameters: group_id={kwargs.get('group_id')}"
            return error_msg, None

    async def _list_portfolio_reconcile_history(
        self, **kwargs
    ) -> tuple[str, dict | list | None]:
        """List all portfolio reconcile history records"""
        try:
            schema = ListPortfolioReconcileHistorySchema(**kwargs)

            # Extract request parameters
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size,
            }
            cleaned_request = drop_empty_fields(request_data)

            result = (
                await self.client.portfolio_reconcile.list_portfolio_reconcile_history(
                    ordering=schema.ordering,
                    page=schema.page,
                    page_size=schema.page_size,
                )
            )
            result_json = json.loads(result.model_dump_json())

            # Create artifact
            artifact = {"request_data": cleaned_request, "response_data": result_json}

            return result.model_dump_json(), artifact

            # output = (
            #     f"Found {result.count} total portfolio reconcile history records.\n"
            # )
            # if result.results:
            #     output += f"Showing {len(result.results)} history records on page {schema.page}:\n\n"
            #     for history in result.results:
            #         output += f"ID: {history.id}\n"
            #         if hasattr(history, "group") and history.group:
            #             output += f"Group: {history.group}\n"
            #         if hasattr(history, "portfolio") and history.portfolio:
            #             output += f"Portfolio: {history.portfolio}\n"
            #         if hasattr(history, "status") and history.status:
            #             output += f"Status: {history.status}\n"
            #         if hasattr(history, "reconcile_date") and history.reconcile_date:
            #             output += f"Reconcile Date: {history.reconcile_date}\n"
            #         output += f"Created: {history.created_at}\n"
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No portfolio reconcile history records found.\n"
            #
            # if result.next:
            #     output += (
            #         f"\nNext page available. Use page={schema.page + 1} to continue."
            #     )
            #
            # return output
        except Exception as e:
            error_msg = f"Error listing portfolio reconcile history: {str(e)}"
            error_msg += f"\n\nRequest parameters: ordering={kwargs.get('ordering')}, page={kwargs.get('page', 1)}, page_size={kwargs.get('page_size', 10)}"
            return error_msg, None

    async def _get_portfolio_reconcile_history(
        self, **kwargs
    ) -> tuple[str, dict | list | None]:
        """Get a specific portfolio reconcile history record by ID"""
        try:
            schema = GetPortfolioReconcileHistorySchema(**kwargs)

            # Extract request parameters
            request_data = {"history_id": schema.history_id}
            cleaned_request = drop_empty_fields(request_data)

            history = (
                await self.client.portfolio_reconcile.get_portfolio_reconcile_history(
                    schema.history_id
                )
            )
            history_json = json.loads(history.model_dump_json())

            # Create artifact
            artifact = {"request_data": cleaned_request, "response_data": history_json}

            return history.model_dump_json(), artifact

            # output = f"Portfolio Reconcile History Record Details:\n"
            # output += f"ID: {history.id}\n"
            # if hasattr(history, "group") and history.group:
            #     output += f"Group: {history.group}\n"
            # if hasattr(history, "portfolio") and history.portfolio:
            #     output += f"Portfolio: {history.portfolio}\n"
            # if hasattr(history, "status") and history.status:
            #     output += f"Status: {history.status}\n"
            # if hasattr(history, "reconcile_date") and history.reconcile_date:
            #     output += f"Reconcile Date: {history.reconcile_date}\n"
            # if hasattr(history, "discrepancies") and history.discrepancies:
            #     output += f"Discrepancies: {history.discrepancies}\n"
            # output += f"Created: {history.created_at}\n"
            # if history.updated_at:
            #     output += f"Updated: {history.updated_at}\n"
            #
            # return output
        except Exception as e:
            error_msg = f"Error getting portfolio reconcile history record {kwargs.get('history_id')}: {str(e)}"
            error_msg += f"\n\nRequest parameters: history_id={kwargs.get('history_id')}"
            return error_msg, None

    async def _list_portfolio_reconcile_status(
        self, **kwargs
    ) -> tuple[str, dict | list | None]:
        """List portfolio reconcile status"""
        try:
            schema = ListPortfolioReconcileStatusSchema(**kwargs)

            # Extract request parameters
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size,
            }
            cleaned_request = drop_empty_fields(request_data)

            status = (
                await self.client.portfolio_reconcile.list_portfolio_reconcile_status(
                    ordering=schema.ordering,
                    page=schema.page,
                    page_size=schema.page_size,
                )
            )
            status_json = json.loads(status.model_dump_json())

            # Create artifact
            artifact = {"request_data": cleaned_request, "response_data": status_json}

            return status.model_dump_json(), artifact

            # output = f"Portfolio Reconcile Status:\n"
            # if (
            #     hasattr(status, "pending_reconciliations")
            #     and status.pending_reconciliations is not None
            # ):
            #     output += f"Pending Reconciliations: {status.pending_reconciliations}\n"
            # if (
            #     hasattr(status, "completed_reconciliations")
            #     and status.completed_reconciliations is not None
            # ):
            #     output += (
            #         f"Completed Reconciliations: {status.completed_reconciliations}\n"
            #     )
            # if (
            #     hasattr(status, "failed_reconciliations")
            #     and status.failed_reconciliations is not None
            # ):
            #     output += f"Failed Reconciliations: {status.failed_reconciliations}\n"
            # if (
            #     hasattr(status, "total_reconciliations")
            #     and status.total_reconciliations is not None
            # ):
            #     output += f"Total Reconciliations: {status.total_reconciliations}\n"
            # if hasattr(status, "last_updated") and status.last_updated:
            #     output += f"Last Updated: {status.last_updated}\n"
            #
            # return output
        except Exception as e:
            error_msg = f"Error getting portfolio reconcile status: {str(e)}"
            error_msg += f"\n\nRequest parameters: ordering={kwargs.get('ordering')}, page={kwargs.get('page', 1)}, page_size={kwargs.get('page_size', 10)}"
            return error_msg, None


def build_portfolio_reconcile_tools() -> List[BaseTool]:
    """Build and return portfolio reconciliation-related tools"""
    toolkit = PortfolioReconcileToolkit()

    tools = [
        StructuredTool.from_function(
            name="list_portfolio_reconcile_groups",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_portfolio_reconcile_groups(**kwargs)
            ),
            coroutine=toolkit._list_portfolio_reconcile_groups,
            description=(
                "List all portfolio reconcile groups with optional filtering and pagination. "
                "Returns reconcile group details including ID, name, description, status, "
                "and timestamps. Supports ordering by various fields and pagination for large datasets. "
                "Useful for managing and monitoring portfolio reconciliation configurations."
            ),
            args_schema=ListPortfolioReconcileGroupsSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_reconcile_group",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_portfolio_reconcile_group(**kwargs)
            ),
            coroutine=toolkit._get_portfolio_reconcile_group,
            description=(
                "Get detailed information about a specific portfolio reconcile group by its ID. "
                "Returns complete reconcile group details including name, description, status, "
                "portfolios, and timestamps. Useful for detailed analysis of reconciliation group configurations."
            ),
            args_schema=GetPortfolioReconcileGroupSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="list_portfolio_reconcile_history",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_portfolio_reconcile_history(**kwargs)
            ),
            coroutine=toolkit._list_portfolio_reconcile_history,
            description=(
                "List all portfolio reconcile history records with pagination. "
                "Returns historical reconciliation data including ID, group, portfolio, status, "
                "reconcile date, and timestamps. Useful for tracking reconciliation activities "
                "and analyzing reconciliation trends over time."
            ),
            args_schema=ListPortfolioReconcileHistorySchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_reconcile_history",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_portfolio_reconcile_history(**kwargs)
            ),
            coroutine=toolkit._get_portfolio_reconcile_history,
            description=(
                "Get detailed information about a specific portfolio reconcile history record. "
                "Returns complete history details including group, portfolio, status, reconcile date, "
                "discrepancies, and timestamps. Useful for detailed analysis of specific reconciliation events."
            ),
            args_schema=GetPortfolioReconcileHistorySchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_reconcile_status",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_portfolio_reconcile_status(**kwargs)
            ),
            coroutine=toolkit._list_portfolio_reconcile_status,
            description=(
                "Get current portfolio reconcile status information. "
                "Returns status summary including pending, completed, failed, and total reconciliations, "
                "along with last update timestamp. Useful for monitoring overall reconciliation health "
                "and system status."
            ),
            args_schema=ListPortfolioReconcileStatusSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
    ]

    return tools
