#!/usr/bin/env python3
"""
Example commands for the Finmars Portfolio API CLI.

This module provides example usage patterns for common operations.
"""
import traceback

from dotenv import load_dotenv

load_dotenv()

import asyncio
import os
import sys
from datetime import datetime

from libs.client import FinmarsPortfolioClient

FINMARS_BASE_URL = os.getenv("FINMARS_BASE_URL")
REALM = os.getenv("FINMARS_REALM")
SPACE = os.getenv("FINMARS_SPACE")


async def example_list_portfolios():
    """Example: List portfolios with pagination."""
    print("=== Example: List Portfolios ===")

    client = FinmarsPortfolioClient(
        base_url=FINMARS_BASE_URL,
        realm=REALM,
        space=SPACE,
        # API key will be loaded from FINMARS_EXPERT_TOKEN environment variable
    )

    try:
        # Get first page of portfolios
        portfolios = await client.portfolios.list_portfolios(page=1, page_size=5)

        print(f"Total portfolios: {portfolios.count}")
        print(f"Showing page 1 with {len(portfolios.results)} results\n")

        for portfolio in portfolios.results:
            print(
                f"- {portfolio.name} (ID: {portfolio.id}, Code: {portfolio.user_code})"
            )

    except Exception as e:
        exc = traceback.format_exc()
        print(exc)
        print(f"Error: {e}")


async def example_get_portfolio_details():
    """Example: Get detailed portfolio information."""
    print("\n=== Example: Get Portfolio Details ===")

    client = FinmarsPortfolioClient(base_url=FINMARS_BASE_URL, realm=REALM, space=SPACE)

    try:
        # Replace with actual portfolio ID
        portfolio_id = 1

        # Get portfolio details
        portfolio = await client.portfolios.get_portfolio(portfolio_id)

        print(f"Portfolio: {portfolio.name}")
        print(f"  ID: {portfolio.id}")
        print(f"  User Code: {portfolio.user_code}")
        print(f"  Short Name: {portfolio.short_name}")
        print(f"  Public Name: {portfolio.public_name}")

        # Get portfolio attributes
        attributes_response = await client.portfolios.list_portfolio_attributes(
            page_size=3
        )
        if attributes_response.results:
            print(f"\n  Attributes ({attributes_response.count} total):")
            for portfolio in attributes_response.results[
                :3
            ]:  # Show first 3 portfolios with attributes
                if hasattr(portfolio, "attributes") and portfolio.attributes:
                    print(f"    Portfolio {portfolio.name}:")
                    for attr in portfolio.attributes[
                        :2
                    ]:  # Show first 2 attributes per portfolio
                        print(
                            f"      - {attr.attribute_type}: {attr.value_string or attr.value_float or attr.value_date}"
                        )

    except Exception as e:
        exc = traceback.format_exc()
        print(exc)
        print(f"Error: {e}")


async def example_portfolio_types():
    """Example: Work with portfolio types."""
    print("\n=== Example: Portfolio Types ===")

    client = FinmarsPortfolioClient(base_url=FINMARS_BASE_URL, realm=REALM, space=SPACE)

    try:
        # List portfolio types
        types = await client.portfolio_types.list_portfolio_types(page_size=5)

        print(f"Total portfolio types: {types.count}")

        for ptype in types.results:
            print(f"\nPortfolio Type: {ptype.name}")
            print(f"  ID: {ptype.id}")
            print(f"  User Code: {ptype.user_code}")
            print(f"  Configuration Code: {ptype.configuration_code}")

            # Get light version for comparison
            light_types = await client.portfolio_types.list_portfolio_types_light()
            print(f"\n  Light version available with {light_types.count} types")

            break  # Just show one example

    except Exception as e:
        exc = traceback.format_exc()
        print(exc)
        print(f"Error: {e}")


async def example_portfolio_history():
    """Example: Access portfolio history."""
    print("\n=== Example: Portfolio History ===")

    client = FinmarsPortfolioClient(base_url=FINMARS_BASE_URL, realm=REALM, space=SPACE)

    try:
        # List portfolio history
        history = await client.portfolio_history.list_portfolio_history(
            page=1, page_size=5, ordering="-id"  # Order by ID descending
        )

        print(f"Total history records: {history.count}")

        for record in history.results:
            print(f"\nHistory Record ID: {record.id}")
            # Print available fields based on the actual model
            for field, value in record.model_dump().items():
                if value is not None and field != "id":
                    print(f"  {field}: {value}")

    except Exception as e:
        exc = traceback.format_exc()
        print(exc)
        print(f"Error: {e}")


async def example_reconciliation():
    """Example: Portfolio reconciliation operations."""
    print("\n=== Example: Portfolio Reconciliation ===")

    client = FinmarsPortfolioClient(base_url=FINMARS_BASE_URL, realm=REALM, space=SPACE)

    try:
        # List reconciliation status
        status = await client.portfolio_reconcile.list_portfolio_reconcile_status(
            page=1, page_size=5
        )

        print(f"Reconciliation Status: {status.count} total records")
        for record in status.results:
            print(f"  - Status ID: {record.id}")

        # List reconciliation groups
        groups = await client.portfolio_reconcile.list_portfolio_reconcile_groups(
            page=1, page_size=3
        )

        print(f"\nReconciliation Groups: {groups.count} total")
        for group in groups.results:
            print(f"  - Group ID: {group.id}")

    except Exception as e:
        exc = traceback.format_exc()
        print(exc)
        print(f"Error: {e}")


async def example_first_transaction_dates():
    """Example: Get first transaction dates."""
    print("\n=== Example: First Transaction Dates ===")

    client = FinmarsPortfolioClient(base_url=FINMARS_BASE_URL, realm=REALM, space=SPACE)

    try:
        # List first transaction dates
        dates = await client.portfolios.list_first_transaction_dates(
            page=1, page_size=5
        )

        print(f"First transaction dates for {dates.count} portfolios:")

        for date_info in dates.results:
            print(f"  Portfolio: {date_info.portfolio}")
            if hasattr(date_info, "date_field"):
                print(f"    Date Field: {date_info.date_field}")

    except Exception as e:
        exc = traceback.format_exc()
        print(exc)
        print(f"Error: {e}")


async def run_all_examples():
    """Run all examples in sequence."""
    print("Running Finmars Portfolio API Examples")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(
        f"API Key loaded: {'Yes' if os.environ.get('FINMARS_EXPERT_TOKEN') else 'No'}"
    )
    print("=" * 50)

    # Check for API key
    if not os.environ.get("FINMARS_EXPERT_TOKEN"):
        print("\nError: FINMARS_EXPERT_TOKEN environment variable not set!")
        print("Please set it before running examples:")
        print("  export FINMARS_EXPERT_TOKEN='your-api-key'")
        return

    # Run examples
    await example_list_portfolios()
    await example_get_portfolio_details()
    await example_portfolio_types()
    await example_portfolio_history()
    # await example_reconciliation()
    # await example_first_transaction_dates()

    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    # Run all examples
    asyncio.run(run_all_examples())
