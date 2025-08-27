import asyncio
import json
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool

from libs.client.finmars_client import FinmarsPortfolioClient
from .shared_models import drop_empty_fields


class ListPortfoliosSchema(BaseModel):
    """Input schema for listing portfolios"""

    ordering: Optional[str] = Field(
        default=None,
        description="Field to use for ordering results (e.g., 'id', '-created_at')",
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page (max 100)"
    )


class GetPortfolioSchema(BaseModel):
    """Input schema for getting a specific portfolio"""

    portfolio_id: int = Field(description="The ID of the portfolio to retrieve")


class ListPortfoliosLightSchema(BaseModel):
    """Input schema for listing portfolios in light format"""

    ordering: Optional[str] = Field(
        default=None, description="Field to use for ordering results"
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page"
    )


class ListPortfolioAttributesSchema(BaseModel):
    """Input schema for listing portfolio attributes"""

    ordering: Optional[str] = Field(
        default=None, description="Field to use for ordering results"
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page"
    )


class ListFirstTransactionDatesSchema(BaseModel):
    """Input schema for listing first transaction dates"""

    ordering: Optional[str] = Field(
        default=None, description="Field to use for ordering results"
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page"
    )


class GetFirstTransactionDateSchema(BaseModel):
    """Input schema for getting first transaction date of a specific portfolio"""

    portfolio_id: int = Field(description="The ID of the portfolio")


class GetInceptionDateSchema(BaseModel):
    """Input schema for getting portfolio inception date - no parameters required"""

    pass


class PortfolioToolkit:
    """Toolkit for portfolio-related operations using the Finmars API"""

    def __init__(self, finmars_token: str = None, space: str = None, realm: str = None):
        self.client = FinmarsPortfolioClient(api_key=finmars_token, space=space, realm=realm)

    async def _list_portfolios(self, **kwargs) -> tuple[str, dict | list | None]:
        """List all portfolios with pagination and filtering"""
        try:
            schema = ListPortfoliosSchema(**kwargs)

            # Extract request parameters
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size,
            }
            cleaned_request = drop_empty_fields(request_data)

            result = await self.client.portfolios.list_portfolios(
                ordering=schema.ordering, page=schema.page, page_size=schema.page_size
            )
            result_json = json.loads(result.model_dump_json())

            # Create artifact
            artifact = {"request_data": cleaned_request, "response_data": result_json}

            return result.model_dump_json(), artifact
            # output = f"Found {result.count} total portfolios.\n"
            # if result.results:
            #     output += f"Showing {len(result.results)} portfolios on page {schema.page}:\n\n"
            #     for portfolio in result.results:
            #         output += f"ID: {portfolio.id}\n"
            #         output += f"Name: {portfolio.name}\n"
            #         if portfolio.description:
            #             output += f"Description: {portfolio.description}\n"
            #         output += f"Portfolio Type: {portfolio.portfolio_type}\n"
            #         output += f"Created: {portfolio.created_at}\n"
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No portfolios found.\n"
            #
            # if result.next:
            #     output += (
            #         f"\nNext page available. Use page={schema.page + 1} to continue."
            #     )
            # return output
        except Exception as e:
            error_msg = f"Error listing portfolios: {str(e)}"
            error_msg += f"\n\nRequest parameters: ordering={kwargs.get('ordering')}, page={kwargs.get('page', 1)}, page_size={kwargs.get('page_size', 10)}"
            return error_msg, None

    async def _get_portfolio(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get a specific portfolio by ID"""
        try:
            schema = GetPortfolioSchema(**kwargs)

            # Extract request parameters
            request_data = {"portfolio_id": schema.portfolio_id}
            cleaned_request = drop_empty_fields(request_data)

            portfolio = await self.client.portfolios.get_portfolio(schema.portfolio_id)
            portfolio_json = json.loads(portfolio.model_dump_json())

            # Create artifact
            artifact = {
                "request_data": cleaned_request,
                "response_data": portfolio_json,
            }

            return portfolio.model_dump_json(), artifact

            # output = f"Portfolio Details:\n"
            # output += f"ID: {portfolio.id}\n"
            # output += f"Name: {portfolio.name}\n"
            # if portfolio.description:
            #     output += f"Description: {portfolio.description}\n"
            # output += f"Portfolio Type: {portfolio.portfolio_type}\n"
            # output += f"Currency: {portfolio.currency}\n"
            # output += f"Created: {portfolio.created_at}\n"
            # if portfolio.updated_at:
            #     output += f"Updated: {portfolio.updated_at}\n"
            #
            # return output
        except Exception as e:
            error_msg = f"Error getting portfolio {kwargs.get('portfolio_id')}: {str(e)}"
            error_msg += f"\n\nRequest parameters: portfolio_id={kwargs.get('portfolio_id')}"
            return error_msg, None

    async def _list_portfolios_light(self, **kwargs) -> tuple[str, dict | list | None]:
        """List portfolios in light format (minimal data)"""
        try:
            schema = ListPortfoliosLightSchema(**kwargs)

            # Extract request parameters
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size,
            }
            cleaned_request = drop_empty_fields(request_data)

            result = await self.client.portfolios.list_portfolios_light(
                ordering=schema.ordering, page=schema.page, page_size=schema.page_size
            )
            result_json = json.loads(result.model_dump_json())

            # Create artifact
            artifact = {"request_data": cleaned_request, "response_data": result_json}

            return result.model_dump_json(), artifact

            # output = f"Found {result.count} total portfolios (light format).\n"
            # if result.results:
            #     output += f"Showing {len(result.results)} portfolios on page {schema.page}:\n\n"
            #     for portfolio in result.results:
            #         output += f"ID: {portfolio.id} | Name: {portfolio.name}\n"
            # else:
            #     output += "No portfolios found.\n"
            #
            # return output
        except Exception as e:
            error_msg = f"Error listing portfolios (light): {str(e)}"
            error_msg += f"\n\nRequest parameters: ordering={kwargs.get('ordering')}, page={kwargs.get('page', 1)}, page_size={kwargs.get('page_size', 10)}"
            return error_msg, None

    async def _list_portfolio_attributes(
        self, **kwargs
    ) -> tuple[str, dict | list | None]:
        """List portfolio attributes"""
        try:
            schema = ListPortfolioAttributesSchema(**kwargs)

            # Extract request parameters
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size,
            }
            cleaned_request = drop_empty_fields(request_data)

            result = await self.client.portfolios.list_portfolio_attributes(
                ordering=schema.ordering, page=schema.page, page_size=schema.page_size
            )
            result_json = json.loads(result.model_dump_json())

            # Create artifact
            artifact = {"request_data": cleaned_request, "response_data": result_json}

            return result.model_dump_json(), artifact

            # output = f"Found {result.count} total portfolio attributes.\n"
            # if result.results:
            #     output += f"Showing {len(result.results)} attributes on page {schema.page}:\n\n"
            #     for attr in result.results:
            #         output += f"Portfolio ID: {attr.id}\n"
            #         output += f"Name: {attr.name}\n"
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No portfolio attributes found.\n"
            #
            # return output
        except Exception as e:
            error_msg = f"Error listing portfolio attributes: {str(e)}"
            error_msg += f"\n\nRequest parameters: ordering={kwargs.get('ordering')}, page={kwargs.get('page', 1)}, page_size={kwargs.get('page_size', 10)}"
            return error_msg, None

    async def _get_inception_date(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get portfolio inception date information"""
        try:
            # No request parameters for this endpoint
            request_data = {}
            cleaned_request = drop_empty_fields(request_data)

            result = await self.client.portfolios.get_inception_date()

            # Create artifact - handle if result is a string or object
            if isinstance(result, str):
                response_data = {"inception_date": result}
            else:
                response_data = (
                    json.loads(result.model_dump_json())
                    if hasattr(result, "model_dump_json")
                    else result
                )

            artifact = {"request_data": cleaned_request, "response_data": response_data}

            return f"Portfolio inception date information: {result}", artifact
        except Exception as e:
            error_msg = f"Error getting inception date: {str(e)}"
            error_msg += f"\n\nRequest parameters: None"
            return error_msg, None

    async def _list_first_transaction_dates(
        self, **kwargs
    ) -> tuple[str, dict | list | None]:
        """List first transaction dates for portfolios"""
        try:
            schema = ListFirstTransactionDatesSchema(**kwargs)

            # Extract request parameters
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size,
            }
            cleaned_request = drop_empty_fields(request_data)

            result = await self.client.portfolios.list_first_transaction_dates(
                ordering=schema.ordering, page=schema.page, page_size=schema.page_size
            )
            result_json = json.loads(result.model_dump_json())

            # Create artifact
            artifact = {"request_data": cleaned_request, "response_data": result_json}

            return result.model_dump_json(), artifact

            # output = f"Found {result.count} total first transaction date records.\n"
            # if result.results:
            #     output += (
            #         f"Showing {len(result.results)} records on page {schema.page}:\n\n"
            #     )
            #     for record in result.results:
            #         output += f"Portfolio ID: {record.portfolio}\n"
            #         output += (
            #             f"First Transaction Date: {record.first_transaction_date}\n"
            #         )
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No first transaction date records found.\n"
            # return output
        except Exception as e:
            error_msg = f"Error listing first transaction dates: {str(e)}"
            error_msg += f"\n\nRequest parameters: ordering={kwargs.get('ordering')}, page={kwargs.get('page', 1)}, page_size={kwargs.get('page_size', 10)}"
            return error_msg, None

    async def _get_first_transaction_date(
        self, **kwargs
    ) -> tuple[str, dict | list | None]:
        """Get first transaction date for a specific portfolio"""
        try:
            schema = GetFirstTransactionDateSchema(**kwargs)

            # Extract request parameters
            request_data = {"portfolio_id": schema.portfolio_id}
            cleaned_request = drop_empty_fields(request_data)

            result = await self.client.portfolios.get_first_transaction_date(
                schema.portfolio_id
            )
            result_json = json.loads(result.model_dump_json())

            # Create artifact
            artifact = {"request_data": cleaned_request, "response_data": result_json}

            return result.model_dump_json(), artifact

            # output = f"First Transaction Date for Portfolio {schema.portfolio_id}:\n"
            # output += f"Portfolio: {result.portfolio}\n"
            # output += f"First Transaction Date: {result.first_transaction_date}\n"
            #
            # return output
        except Exception as e:
            error_msg = f"Error getting first transaction date for portfolio {kwargs.get('portfolio_id')}: {str(e)}"
            error_msg += f"\n\nRequest parameters: portfolio_id={kwargs.get('portfolio_id')}"
            return error_msg, None


def build_portfolio_tools(
    finmars_token: str = None, space: str = None, realm: str = None
) -> List[BaseTool]:
    """Build and return portfolio-related tools"""
    toolkit = PortfolioToolkit(finmars_token=finmars_token, space=space, realm=realm)

    tools = [
        StructuredTool.from_function(
            name="list_portfolios",
            func=lambda **kwargs: asyncio.run(toolkit._list_portfolios(**kwargs)),
            coroutine=toolkit._list_portfolios,
            description=(
                "List all portfolios with optional filtering and pagination. "
                "Returns portfolio details including ID, name, description, type, and creation date. "
                "Supports ordering by various fields and pagination for large datasets."
            ),
            args_schema=ListPortfoliosSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio",
            func=lambda **kwargs: asyncio.run(toolkit._get_portfolio(**kwargs)),
            coroutine=toolkit._get_portfolio,
            description=(
                "Get detailed information about a specific portfolio by its ID. "
                "Returns complete portfolio details including name, description, type, currency, "
                "and timestamps."
            ),
            args_schema=GetPortfolioSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="list_portfolios_light",
            func=lambda **kwargs: asyncio.run(toolkit._list_portfolios_light(**kwargs)),
            coroutine=toolkit._list_portfolios_light,
            description=(
                "List portfolios in light format with minimal data (ID and name only). "
                "Useful for quick overviews or when you need a simple list of available portfolios."
            ),
            args_schema=ListPortfoliosLightSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="list_portfolio_attributes",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_portfolio_attributes(**kwargs)
            ),
            coroutine=toolkit._list_portfolio_attributes,
            description=(
                "List portfolio attributes with pagination. "
                "Returns portfolio attribute information for analysis and reporting."
            ),
            args_schema=ListPortfolioAttributesSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_inception_date",
            func=lambda **kwargs: asyncio.run(toolkit._get_inception_date(**kwargs)),
            coroutine=toolkit._get_inception_date,
            description=(
                "Get portfolio inception date information. "
                "Returns inception date details for portfolio analysis."
            ),
            args_schema=GetInceptionDateSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="list_first_transaction_dates",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_first_transaction_dates(**kwargs)
            ),
            coroutine=toolkit._list_first_transaction_dates,
            description=(
                "List first transaction dates for all portfolios. "
                "Useful for understanding portfolio history and timeline analysis."
            ),
            args_schema=ListFirstTransactionDatesSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_first_transaction_date",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_first_transaction_date(**kwargs)
            ),
            coroutine=toolkit._get_first_transaction_date,
            description=(
                "Get the first transaction date for a specific portfolio. "
                "Returns the earliest transaction date for timeline and history analysis."
            ),
            args_schema=GetFirstTransactionDateSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
    ]

    return tools
