import asyncio
import json
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool

from libs.client.finmars_client import FinmarsPortfolioClient
from .shared_models import drop_empty_fields


class ListPortfolioTypesSchema(BaseModel):
    """Input schema for listing portfolio types"""

    ordering: Optional[str] = Field(
        default=None,
        description="Field to use for ordering results (e.g., 'id', '-name')",
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page (max 100)"
    )


class GetPortfolioTypeSchema(BaseModel):
    """Input schema for getting a specific portfolio type"""

    portfolio_type_id: int = Field(
        description="The ID of the portfolio type to retrieve"
    )


class ListPortfolioTypesLightSchema(BaseModel):
    """Input schema for listing portfolio types in light format"""

    ordering: Optional[str] = Field(
        default=None, description="Field to use for ordering results"
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page"
    )


class ListPortfolioAttributeTypesSchema(BaseModel):
    """Input schema for listing portfolio attribute types"""

    ordering: Optional[str] = Field(
        default=None, description="Field to use for ordering results"
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page"
    )


class GetPortfolioAttributeTypeSchema(BaseModel):
    """Input schema for getting a specific portfolio attribute type"""

    attribute_type_id: int = Field(
        description="The ID of the attribute type to retrieve"
    )


class GetObjectsToRecalculateSchema(BaseModel):
    """Input schema for getting objects to recalculate for an attribute type"""

    attribute_type_id: int = Field(description="The ID of the attribute type")


class ListPortfolioTypeAttributeTypesSchema(BaseModel):
    """Input schema for listing portfolio type attribute types"""

    ordering: Optional[str] = Field(
        default=None, description="Field to use for ordering results"
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page"
    )


class GetPortfolioTypeAttributeTypeSchema(BaseModel):
    """Input schema for getting a specific portfolio type attribute type"""

    attribute_type_id: int = Field(
        description="The ID of the portfolio type attribute type to retrieve"
    )


class GetPortfolioTypeAttributesSchema(BaseModel):
    """Input schema for getting portfolio type attributes - no parameters required"""

    pass


class PortfolioTypeToolkit:
    """Toolkit for portfolio type-related operations using the Finmars API"""

    def __init__(self):
        self.client = FinmarsPortfolioClient()

    async def _list_portfolio_types(self, **kwargs) -> tuple[str, dict | list | None]:
        """List all portfolio types with pagination and filtering"""
        try:
            schema = ListPortfolioTypesSchema(**kwargs)
            
            # Extract request parameters
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size
            }
            cleaned_request = drop_empty_fields(request_data)
            
            result = await self.client.portfolio_types.list_portfolio_types(
                ordering=schema.ordering, page=schema.page, page_size=schema.page_size
            )
            result_json = json.loads(result.model_dump_json())
            
            # Create artifact
            artifact = {
                "request_data": cleaned_request,
                "response_data": result_json
            }
            
            return result.model_dump_json(), artifact

            # output = f"Found {result.count} total portfolio types.\n"
            # if result.results:
            #     output += f"Showing {len(result.results)} portfolio types on page {schema.page}:\n\n"
            #     for ptype in result.results:
            #         output += f"ID: {ptype.id}\n"
            #         output += f"Name: {ptype.name}\n"
            #         if ptype.description:
            #             output += f"Description: {ptype.description}\n"
            #         output += f"Created: {ptype.created_at}\n"
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No portfolio types found.\n"
            #
            # if result.next:
            #     output += (
            #         f"\nNext page available. Use page={schema.page + 1} to continue."
            #     )
            #
            # return output
        except Exception as e:
            return f"Error listing portfolio types: {str(e)}", None

    async def _get_portfolio_type(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get a specific portfolio type by ID"""
        try:
            schema = GetPortfolioTypeSchema(**kwargs)
            
            # Extract request parameters
            request_data = {
                "portfolio_type_id": schema.portfolio_type_id
            }
            cleaned_request = drop_empty_fields(request_data)
            
            ptype = await self.client.portfolio_types.get_portfolio_type(
                schema.portfolio_type_id
            )
            ptype_json = json.loads(ptype.model_dump_json())
            
            # Create artifact
            artifact = {
                "request_data": cleaned_request,
                "response_data": ptype_json
            }
            
            return ptype.model_dump_json(), artifact

            # output = f"Portfolio Type Details:\n"
            # output += f"ID: {ptype.id}\n"
            # output += f"Name: {ptype.name}\n"
            # if ptype.description:
            #     output += f"Description: {ptype.description}\n"
            # output += f"Created: {ptype.created_at}\n"
            # if ptype.updated_at:
            #     output += f"Updated: {ptype.updated_at}\n"
            #
            # return output
        except Exception as e:
            return f"Error getting portfolio type {kwargs.get('portfolio_type_id')}: {str(e)}", None

    async def _list_portfolio_types_light(self, **kwargs) -> tuple[str, dict | list | None]:
        """List portfolio types in light format (minimal data)"""
        try:
            schema = ListPortfolioTypesLightSchema(**kwargs)
            
            # Extract request parameters
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size
            }
            cleaned_request = drop_empty_fields(request_data)
            
            result = await self.client.portfolio_types.list_portfolio_types_light(
                ordering=schema.ordering, page=schema.page, page_size=schema.page_size
            )
            result_json = json.loads(result.model_dump_json())
            
            # Create artifact
            artifact = {
                "request_data": cleaned_request,
                "response_data": result_json
            }
            
            return result.model_dump_json(), artifact

            # output = f"Found {result.count} total portfolio types (light format).\n"
            # if result.results:
            #     output += f"Showing {len(result.results)} portfolio types on page {schema.page}:\n\n"
            #     for ptype in result.results:
            #         output += f"ID: {ptype.id} | Name: {ptype.name}\n"
            # else:
            #     output += "No portfolio types found.\n"
            #
            # return output
        except Exception as e:
            return f"Error listing portfolio types (light): {str(e)}", None

    async def _get_portfolio_type_attributes(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get portfolio type attributes"""
        try:
            # No request parameters for this endpoint
            request_data = {}
            cleaned_request = drop_empty_fields(request_data)
            
            attributes = (
                await self.client.portfolio_types.get_portfolio_type_attributes()
            )
            attributes_json = json.loads(attributes.model_dump_json())
            
            # Create artifact
            artifact = {
                "request_data": cleaned_request,
                "response_data": attributes_json
            }
            
            return attributes.model_dump_json(), artifact

            # output = f"Found {len(attributes)} portfolio type attributes:\n\n"
            # for attr in attributes:
            #     output += f"Name: {attr.name}\n"
            #     if attr.value:
            #         output += f"Value: {attr.value}\n"
            #     if attr.attribute_type:
            #         output += f"Type: {attr.attribute_type}\n"
            #     output += "-" * 40 + "\n"
            #
            # return output
        except Exception as e:
            return f"Error getting portfolio type attributes: {str(e)}", None

    async def _list_portfolio_attribute_types(self, **kwargs) -> tuple[str, dict | list | None]:
        """List portfolio attribute types"""
        try:
            schema = ListPortfolioAttributeTypesSchema(**kwargs)
            
            # Extract request parameters
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size
            }
            cleaned_request = drop_empty_fields(request_data)
            
            result = await self.client.portfolio_types.list_portfolio_attribute_types(
                ordering=schema.ordering, page=schema.page, page_size=schema.page_size
            )
            result_json = json.loads(result.model_dump_json())
            
            # Create artifact
            artifact = {
                "request_data": cleaned_request,
                "response_data": result_json
            }
            
            return result.model_dump_json(), artifact

            # output = f"Found {result.count} total portfolio attribute types.\n"
            # if result.results:
            #     output += f"Showing {len(result.results)} attribute types on page {schema.page}:\n\n"
            #     for attr_type in result.results:
            #         output += f"ID: {attr_type.id}\n"
            #         output += f"Name: {attr_type.name}\n"
            #         if attr_type.description:
            #             output += f"Description: {attr_type.description}\n"
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No portfolio attribute types found.\n"
            #
            # return output
        except Exception as e:
            return f"Error listing portfolio attribute types: {str(e)}", None

    async def _get_portfolio_attribute_type(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get a specific portfolio attribute type by ID"""
        try:
            schema = GetPortfolioAttributeTypeSchema(**kwargs)
            
            # Extract request parameters
            request_data = {
                "attribute_type_id": schema.attribute_type_id
            }
            cleaned_request = drop_empty_fields(request_data)
            
            attr_type = await self.client.portfolio_types.get_portfolio_attribute_type(
                schema.attribute_type_id
            )
            attr_type_json = json.loads(attr_type.model_dump_json())
            
            # Create artifact
            artifact = {
                "request_data": cleaned_request,
                "response_data": attr_type_json
            }
            
            return attr_type.model_dump_json(), artifact

            # output = f"Portfolio Attribute Type Details:\n"
            # output += f"ID: {attr_type.id}\n"
            # output += f"Name: {attr_type.name}\n"
            # if attr_type.description:
            #     output += f"Description: {attr_type.description}\n"
            #
            # return output
        except Exception as e:
            return f"Error getting portfolio attribute type {kwargs.get('attribute_type_id')}: {str(e)}", None

    async def _get_objects_to_recalculate(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get objects to recalculate for a portfolio attribute type"""
        try:
            schema = GetObjectsToRecalculateSchema(**kwargs)
            
            # Extract request parameters
            request_data = {
                "attribute_type_id": schema.attribute_type_id
            }
            cleaned_request = drop_empty_fields(request_data)
            
            result = await self.client.portfolio_types.get_portfolio_attribute_type_objects_to_recalculate(
                schema.attribute_type_id
            )
            result_json = json.loads(result.model_dump_json())
            
            # Create artifact
            artifact = {
                "request_data": cleaned_request,
                "response_data": result_json
            }
            
            return result.model_dump_json(), artifact

            # output = f"Objects to recalculate for attribute type {schema.attribute_type_id}:\n"
            # if hasattr(result, "portfolios") and result.portfolios:
            #     output += f"Portfolios: {len(result.portfolios)} items\n"
            # if hasattr(result, "portfolio_types") and result.portfolio_types:
            #     output += f"Portfolio Types: {len(result.portfolio_types)} items\n"
            #
            # return output
        except Exception as e:
            return f"Error getting objects to recalculate for attribute type {kwargs.get('attribute_type_id')}: {str(e)}", None

    async def _list_portfolio_type_attribute_types(self, **kwargs) -> tuple[str, dict | list | None]:
        """List portfolio type attribute types"""
        try:
            schema = ListPortfolioTypeAttributeTypesSchema(**kwargs)
            
            # Extract request parameters
            request_data = {
                "ordering": schema.ordering,
                "page": schema.page,
                "page_size": schema.page_size
            }
            cleaned_request = drop_empty_fields(request_data)
            
            result = (
                await self.client.portfolio_types.list_portfolio_type_attribute_types(
                    ordering=schema.ordering,
                    page=schema.page,
                    page_size=schema.page_size,
                )
            )
            result_json = json.loads(result.model_dump_json())
            
            # Create artifact
            artifact = {
                "request_data": cleaned_request,
                "response_data": result_json
            }
            
            return result.model_dump_json(), artifact

            # output = f"Found {result.count} total portfolio type attribute types.\n"
            # if result.results:
            #     output += f"Showing {len(result.results)} attribute types on page {schema.page}:\n\n"
            #     for attr_type in result.results:
            #         output += f"ID: {attr_type.id}\n"
            #         output += f"Name: {attr_type.name}\n"
            #         if attr_type.description:
            #             output += f"Description: {attr_type.description}\n"
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No portfolio type attribute types found.\n"
            #
            # return output
        except Exception as e:
            return f"Error listing portfolio type attribute types: {str(e)}", None

    async def _get_portfolio_type_attribute_type(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get a specific portfolio type attribute type by ID"""
        try:
            schema = GetPortfolioTypeAttributeTypeSchema(**kwargs)
            
            # Extract request parameters
            request_data = {
                "attribute_type_id": schema.attribute_type_id
            }
            cleaned_request = drop_empty_fields(request_data)
            
            attr_type = (
                await self.client.portfolio_types.get_portfolio_type_attribute_type(
                    schema.attribute_type_id
                )
            )
            attr_type_json = json.loads(attr_type.model_dump_json())
            
            # Create artifact
            artifact = {
                "request_data": cleaned_request,
                "response_data": attr_type_json
            }
            
            return attr_type.model_dump_json(), artifact

            # output = f"Portfolio Type Attribute Type Details:\n"
            # output += f"ID: {attr_type.id}\n"
            # output += f"Name: {attr_type.name}\n"
            # if attr_type.description:
            #     output += f"Description: {attr_type.description}\n"
            #
            # return output
        except Exception as e:
            return f"Error getting portfolio type attribute type {kwargs.get('attribute_type_id')}: {str(e)}", None

    async def _get_portfolio_type_objects_to_recalculate(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get objects to recalculate for a portfolio type attribute type"""
        try:
            schema = GetObjectsToRecalculateSchema(**kwargs)
            
            # Extract request parameters
            request_data = {
                "attribute_type_id": schema.attribute_type_id
            }
            cleaned_request = drop_empty_fields(request_data)
            
            result = await self.client.portfolio_types.get_portfolio_type_attribute_type_objects_to_recalculate(
                schema.attribute_type_id
            )
            result_json = json.loads(result.model_dump_json())
            
            # Create artifact
            artifact = {
                "request_data": cleaned_request,
                "response_data": result_json
            }
            
            return result.model_dump_json(), artifact

            # output = f"Objects to recalculate for portfolio type attribute type {schema.attribute_type_id}:\n"
            # if hasattr(result, "portfolios") and result.portfolios:
            #     output += f"Portfolios: {len(result.portfolios)} items\n"
            # if hasattr(result, "portfolio_types") and result.portfolio_types:
            #     output += f"Portfolio Types: {len(result.portfolio_types)} items\n"
            #
            # return output
        except Exception as e:
            return f"Error getting objects to recalculate for portfolio type attribute type {kwargs.get('attribute_type_id')}: {str(e)}", None


def build_portfolio_type_tools() -> List[BaseTool]:
    """Build and return portfolio type-related tools"""
    toolkit = PortfolioTypeToolkit()

    tools = [
        StructuredTool.from_function(
            name="list_portfolio_types",
            func=lambda **kwargs: asyncio.run(toolkit._list_portfolio_types(**kwargs)),
            coroutine=toolkit._list_portfolio_types,
            description=(
                "List all portfolio types with optional filtering and pagination. "
                "Returns portfolio type details including ID, name, description, and creation date. "
                "Supports ordering by various fields and pagination for large datasets."
            ),
            args_schema=ListPortfolioTypesSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_type",
            func=lambda **kwargs: asyncio.run(toolkit._get_portfolio_type(**kwargs)),
            coroutine=toolkit._get_portfolio_type,
            description=(
                "Get detailed information about a specific portfolio type by its ID. "
                "Returns complete portfolio type details including name, description, and timestamps."
            ),
            args_schema=GetPortfolioTypeSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="list_portfolio_types_light",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_portfolio_types_light(**kwargs)
            ),
            coroutine=toolkit._list_portfolio_types_light,
            description=(
                "List portfolio types in light format with minimal data (ID and name only). "
                "Useful for quick overviews or when you need a simple list of available portfolio types."
            ),
            args_schema=ListPortfolioTypesLightSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_type_attributes",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_portfolio_type_attributes(**kwargs)
            ),
            coroutine=toolkit._get_portfolio_type_attributes,
            description=(
                "Get portfolio type attributes. "
                "Returns attribute information for portfolio type configuration and analysis."
            ),
            args_schema=GetPortfolioTypeAttributesSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="list_portfolio_attribute_types",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_portfolio_attribute_types(**kwargs)
            ),
            coroutine=toolkit._list_portfolio_attribute_types,
            description=(
                "List portfolio attribute types with pagination. "
                "Returns available attribute types that can be used with portfolios."
            ),
            args_schema=ListPortfolioAttributeTypesSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_attribute_type",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_portfolio_attribute_type(**kwargs)
            ),
            coroutine=toolkit._get_portfolio_attribute_type,
            description=(
                "Get detailed information about a specific portfolio attribute type. "
                "Returns attribute type details including name and description."
            ),
            args_schema=GetPortfolioAttributeTypeSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_attribute_objects_to_recalculate",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_objects_to_recalculate(**kwargs)
            ),
            coroutine=toolkit._get_objects_to_recalculate,
            description=(
                "Get objects that need recalculation for a portfolio attribute type. "
                "Useful for maintenance and data consistency operations."
            ),
            args_schema=GetObjectsToRecalculateSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="list_portfolio_type_attribute_types",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_portfolio_type_attribute_types(**kwargs)
            ),
            coroutine=toolkit._list_portfolio_type_attribute_types,
            description=(
                "List portfolio type attribute types with pagination. "
                "Returns attribute types specific to portfolio type configurations."
            ),
            args_schema=ListPortfolioTypeAttributeTypesSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_type_attribute_type",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_portfolio_type_attribute_type(**kwargs)
            ),
            coroutine=toolkit._get_portfolio_type_attribute_type,
            description=(
                "Get detailed information about a specific portfolio type attribute type. "
                "Returns attribute type details for portfolio type configuration."
            ),
            args_schema=GetPortfolioTypeAttributeTypeSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_type_attribute_objects_to_recalculate",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_portfolio_type_objects_to_recalculate(**kwargs)
            ),
            coroutine=toolkit._get_portfolio_type_objects_to_recalculate,
            description=(
                "Get objects that need recalculation for a portfolio type attribute type. "
                "Useful for maintenance and data consistency operations on portfolio types."
            ),
            args_schema=GetObjectsToRecalculateSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
    ]

    return tools
