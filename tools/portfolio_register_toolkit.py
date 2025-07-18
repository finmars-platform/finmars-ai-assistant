import asyncio
import json
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool

from libs.client.finmars_client import FinmarsPortfolioClient


class ListPortfolioRegistersSchema(BaseModel):
    """Input schema for listing portfolio registers"""

    ordering: Optional[str] = Field(
        default=None,
        description="Field to use for ordering results (e.g., 'id', '-created_at')",
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page (max 100)"
    )


class GetPortfolioRegisterSchema(BaseModel):
    """Input schema for getting a specific portfolio register"""

    register_id: int = Field(description="The ID of the portfolio register to retrieve")


class ListPortfolioRegisterRecordsSchema(BaseModel):
    """Input schema for listing portfolio register records"""

    ordering: Optional[str] = Field(
        default=None, description="Field to use for ordering results"
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page"
    )


class GetPortfolioRegisterRecordSchema(BaseModel):
    """Input schema for getting a specific portfolio register record"""

    record_id: int = Field(
        description="The ID of the portfolio register record to retrieve"
    )


class ListPortfolioRegisterAttributeTypesSchema(BaseModel):
    """Input schema for listing portfolio register attribute types"""

    ordering: Optional[str] = Field(
        default=None, description="Field to use for ordering results"
    )
    page: Optional[int] = Field(default=1, description="Page number for pagination")
    page_size: Optional[int] = Field(
        default=10, description="Number of results per page"
    )


class GetPortfolioRegisterAttributeTypeSchema(BaseModel):
    """Input schema for getting a specific portfolio register attribute type"""

    attribute_type_id: int = Field(
        description="The ID of the register attribute type to retrieve"
    )


class GetRegisterObjectsToRecalculateSchema(BaseModel):
    """Input schema for getting objects to recalculate for a register attribute type"""

    attribute_type_id: int = Field(description="The ID of the register attribute type")


class PortfolioRegisterToolkit:
    """Toolkit for portfolio register-related operations using the Finmars API"""

    def __init__(self):
        self.client = FinmarsPortfolioClient()

    async def _list_portfolio_registers(self, **kwargs) -> tuple[str, dict | list | None]:
        """List all portfolio registers with pagination and filtering"""
        try:
            schema = ListPortfolioRegistersSchema(**kwargs)
            result = await self.client.portfolio_registers.list_portfolio_registers(
                ordering=schema.ordering, page=schema.page, page_size=schema.page_size
            )
            result_json = json.loads(result.model_dump_json())
            return result.model_dump_json(), result_json

            # output = f"Found {result.count} total portfolio registers.\n"
            # if result.results:
            #     output += f"Showing {len(result.results)} registers on page {schema.page}:\n\n"
            #     for register in result.results:
            #         output += f"ID: {register.id}\n"
            #         output += f"Name: {register.name}\n"
            #         if register.description:
            #             output += f"Description: {register.description}\n"
            #         output += f"Portfolio: {register.portfolio}\n"
            #         output += f"Created: {register.created_at}\n"
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No portfolio registers found.\n"
            #
            # if result.next:
            #     output += (
            #         f"\nNext page available. Use page={schema.page + 1} to continue."
            #     )
            #
            # return output
        except Exception as e:
            return f"Error listing portfolio registers: {str(e)}", None

    async def _get_portfolio_register(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get a specific portfolio register by ID"""
        try:
            schema = GetPortfolioRegisterSchema(**kwargs)
            register = await self.client.portfolio_registers.get_portfolio_register(
                schema.register_id
            )
            register_json = json.loads(register.model_dump_json())
            return register.model_dump_json(), register_json

            # output = f"Portfolio Register Details:\n"
            # output += f"ID: {register.id}\n"
            # output += f"Name: {register.name}\n"
            # if register.description:
            #     output += f"Description: {register.description}\n"
            # output += f"Portfolio: {register.portfolio}\n"
            # output += f"Created: {register.created_at}\n"
            # if register.updated_at:
            #     output += f"Updated: {register.updated_at}\n"
            #
            # return output
        except Exception as e:
            return f"Error getting portfolio register {kwargs.get('register_id')}: {str(e)}", None

    async def _list_portfolio_register_records(self, **kwargs) -> tuple[str, dict | list | None]:
        """List all portfolio register records"""
        try:
            schema = ListPortfolioRegisterRecordsSchema(**kwargs)
            result = (
                await self.client.portfolio_registers.list_portfolio_register_records(
                    ordering=schema.ordering,
                    page=schema.page,
                    page_size=schema.page_size,
                )
            )
            result_json = json.loads(result.model_dump_json())
            return result.model_dump_json(), result_json

            # output = f"Found {result.count} total portfolio register records.\n"
            # if result.results:
            #     output += (
            #         f"Showing {len(result.results)} records on page {schema.page}:\n\n"
            #     )
            #     for record in result.results:
            #         output += f"ID: {record.id}\n"
            #         output += f"Register: {record.register}\n"
            #         if hasattr(record, "value") and record.value:
            #             output += f"Value: {record.value}\n"
            #         output += f"Created: {record.created_at}\n"
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No portfolio register records found.\n"
            #
            # if result.next:
            #     output += (
            #         f"\nNext page available. Use page={schema.page + 1} to continue."
            #     )
            #
            # return output
        except Exception as e:
            return f"Error listing portfolio register records: {str(e)}", None

    async def _get_portfolio_register_record(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get a specific portfolio register record by ID"""
        try:
            schema = GetPortfolioRegisterRecordSchema(**kwargs)
            record = (
                await self.client.portfolio_registers.get_portfolio_register_record(
                    schema.record_id
                )
            )
            record_json = json.loads(record.model_dump_json())
            return record.model_dump_json(), record_json

            # output = f"Portfolio Register Record Details:\n"
            # output += f"ID: {record.id}\n"
            # output += f"Register: {record.register}\n"
            # if hasattr(record, "value") and record.value:
            #     output += f"Value: {record.value}\n"
            # output += f"Created: {record.created_at}\n"
            # if record.updated_at:
            #     output += f"Updated: {record.updated_at}\n"
            #
            # return output
        except Exception as e:
            return f"Error getting portfolio register record {kwargs.get('record_id')}: {str(e)}", None

    async def _list_portfolio_register_attribute_types(self, **kwargs) -> tuple[str, dict | list | None]:
        """List portfolio register attribute types"""
        try:
            schema = ListPortfolioRegisterAttributeTypesSchema(**kwargs)
            result = await self.client.portfolio_registers.list_portfolio_register_attribute_types(
                ordering=schema.ordering, page=schema.page, page_size=schema.page_size
            )
            result_json = json.loads(result.model_dump_json())
            return result.model_dump_json(), result_json

            # output = f"Found {result.count} total portfolio register attribute types.\n"
            # if result.results:
            #     output += f"Showing {len(result.results)} attribute types on page {schema.page}:\n\n"
            #     for attr_type in result.results:
            #         output += f"ID: {attr_type.id}\n"
            #         output += f"Name: {attr_type.name}\n"
            #         if attr_type.description:
            #             output += f"Description: {attr_type.description}\n"
            #         output += "-" * 40 + "\n"
            # else:
            #     output += "No portfolio register attribute types found.\n"
            #
            # return output
        except Exception as e:
            return f"Error listing portfolio register attribute types: {str(e)}", None

    async def _get_portfolio_register_attribute_type(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get a specific portfolio register attribute type by ID"""
        try:
            schema = GetPortfolioRegisterAttributeTypeSchema(**kwargs)
            attr_type = await self.client.portfolio_registers.get_portfolio_register_attribute_type(
                schema.attribute_type_id
            )
            attr_type_json = json.loads(attr_type.model_dump_json())
            return attr_type.model_dump_json(), attr_type_json

            # output = f"Portfolio Register Attribute Type Details:\n"
            # output += f"ID: {attr_type.id}\n"
            # output += f"Name: {attr_type.name}\n"
            # if attr_type.description:
            #     output += f"Description: {attr_type.description}\n"
            #
            # return output
        except Exception as e:
            return f"Error getting portfolio register attribute type {kwargs.get('attribute_type_id')}: {str(e)}", None

    async def _get_register_objects_to_recalculate(self, **kwargs) -> tuple[str, dict | list | None]:
        """Get objects to recalculate for a portfolio register attribute type"""
        try:
            schema = GetRegisterObjectsToRecalculateSchema(**kwargs)
            result = await self.client.portfolio_registers.get_portfolio_register_attribute_type_objects_to_recalculate(
                schema.attribute_type_id
            )
            result_json = json.loads(result.model_dump_json())
            return result.model_dump_json(), result_json

            # output = f"Objects to recalculate for register attribute type {schema.attribute_type_id}:\n"
            # if hasattr(result, "portfolios") and result.portfolios:
            #     output += f"Portfolios: {len(result.portfolios)} items\n"
            # if hasattr(result, "registers") and result.registers:
            #     output += f"Registers: {len(result.registers)} items\n"
            #
            # return output
        except Exception as e:
            return f"Error getting objects to recalculate for register attribute type {kwargs.get('attribute_type_id')}: {str(e)}", None


def build_portfolio_register_tools() -> List[BaseTool]:
    """Build and return portfolio register-related tools"""
    toolkit = PortfolioRegisterToolkit()

    tools = [
        StructuredTool.from_function(
            name="list_portfolio_registers",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_portfolio_registers(**kwargs)
            ),
            coroutine=toolkit._list_portfolio_registers,
            description=(
                "List all portfolio registers with optional filtering and pagination. "
                "Returns register details including ID, name, description, portfolio, and creation date. "
                "Supports ordering by various fields and pagination for large datasets."
            ),
            args_schema=ListPortfolioRegistersSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_register",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_portfolio_register(**kwargs)
            ),
            coroutine=toolkit._get_portfolio_register,
            description=(
                "Get detailed information about a specific portfolio register by its ID. "
                "Returns complete register details including name, description, portfolio, and timestamps."
            ),
            args_schema=GetPortfolioRegisterSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="list_portfolio_register_records",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_portfolio_register_records(**kwargs)
            ),
            coroutine=toolkit._list_portfolio_register_records,
            description=(
                "List all portfolio register records with pagination. "
                "Returns record details including ID, register, value, and timestamps. "
                "Useful for analyzing register data and history."
            ),
            args_schema=ListPortfolioRegisterRecordsSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_register_record",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_portfolio_register_record(**kwargs)
            ),
            coroutine=toolkit._get_portfolio_register_record,
            description=(
                "Get detailed information about a specific portfolio register record. "
                "Returns complete record details including register, value, and timestamps."
            ),
            args_schema=GetPortfolioRegisterRecordSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="list_portfolio_register_attribute_types",
            func=lambda **kwargs: asyncio.run(
                toolkit._list_portfolio_register_attribute_types(**kwargs)
            ),
            coroutine=toolkit._list_portfolio_register_attribute_types,
            description=(
                "List portfolio register attribute types with pagination. "
                "Returns attribute types that can be used with portfolio registers."
            ),
            args_schema=ListPortfolioRegisterAttributeTypesSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_portfolio_register_attribute_type",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_portfolio_register_attribute_type(**kwargs)
            ),
            coroutine=toolkit._get_portfolio_register_attribute_type,
            description=(
                "Get detailed information about a specific portfolio register attribute type. "
                "Returns attribute type details including name and description."
            ),
            args_schema=GetPortfolioRegisterAttributeTypeSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
        StructuredTool.from_function(
            name="get_register_attribute_objects_to_recalculate",
            func=lambda **kwargs: asyncio.run(
                toolkit._get_register_objects_to_recalculate(**kwargs)
            ),
            coroutine=toolkit._get_register_objects_to_recalculate,
            description=(
                "Get objects that need recalculation for a portfolio register attribute type. "
                "Useful for maintenance and data consistency operations on registers."
            ),
            args_schema=GetRegisterObjectsToRecalculateSchema,
            # response_format="content_and_artifact",
            response_format="content_and_artifact",
        ),
    ]

    return tools
