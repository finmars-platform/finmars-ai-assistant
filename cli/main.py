#!/usr/bin/env python3
"""
Finmars Portfolio API CLI Runner

A simple command-line interface for interacting with the Finmars Portfolio API.

Usage:
    python cli/main.py <command> [options]

Environment Variables:
    FINMARS_EXPERT_TOKEN: API authentication token (required)
    FINMARS_BASE_URL: API base URL (optional, defaults to https://api.finmars.com)
    FINMARS_REALM: Realm code (optional, defaults to realm0v4ry)
    FINMARS_SPACE: Space code (optional, defaults to space0ihxm)

Commands:
    list-portfolios         List all portfolios
    get-portfolio          Get a specific portfolio by ID
    list-portfolio-types   List all portfolio types
    list-history          List portfolio history
    portfolio-status      Get portfolio reconciliation status

Examples:
    python cli/main.py list-portfolios --page 1 --page-size 10
    python cli/main.py get-portfolio --id 123
    python cli/main.py list-portfolio-types
"""
from dotenv import load_dotenv
load_dotenv()

import os
import sys
import asyncio
import argparse
import json
from typing import Optional, Any, Dict

from libs.client import FinmarsPortfolioClient


class FinmarsCLI:
    """Command-line interface for Finmars Portfolio API."""

    def __init__(self):
        """Initialize the CLI with environment configuration."""
        self.base_url = os.environ.get("FINMARS_BASE_URL", "https://api.finmars.com")
        self.realm = os.environ.get("FINMARS_REALM", "realm0v4ry")
        self.space = os.environ.get("FINMARS_SPACE", "space0ihxm")
        self.api_key = os.environ.get("FINMARS_EXPERT_TOKEN")

        if not self.api_key:
            print("Error: FINMARS_EXPERT_TOKEN environment variable is required")
            sys.exit(1)

        self.client = FinmarsPortfolioClient(
            base_url=self.base_url,
            realm=self.realm,
            space=self.space,
            api_key=self.api_key,
        )

    async def list_portfolios(self, args: argparse.Namespace) -> None:
        """List all portfolios."""
        try:
            result = await self.client.portfolios.list_portfolios(
                page=args.page, page_size=args.page_size, ordering=args.ordering
            )

            print(f"\nTotal portfolios: {result.count}")
            print("-" * 80)

            for portfolio in result.results:
                print(f"ID: {portfolio.id}")
                print(f"User Code: {portfolio.user_code}")
                print(f"Name: {portfolio.name}")
                print(f"Short Name: {portfolio.short_name}")
                print(f"Public Name: {portfolio.public_name}")
                print("-" * 40)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    async def get_portfolio(self, args: argparse.Namespace) -> None:
        """Get a specific portfolio by ID."""
        try:
            portfolio = await self.client.portfolios.get_portfolio(args.id)

            print(f"\nPortfolio Details:")
            print("-" * 80)
            print(f"ID: {portfolio.id}")
            print(f"User Code: {portfolio.user_code}")
            print(f"Name: {portfolio.name}")
            print(f"Short Name: {portfolio.short_name}")
            print(f"Public Name: {portfolio.public_name}")

            if hasattr(portfolio, "portfolio_type"):
                print(f"Portfolio Type: {portfolio.portfolio_type}")

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    async def list_portfolio_types(self, args: argparse.Namespace) -> None:
        """List all portfolio types."""
        try:
            result = await self.client.portfolio_types.list_portfolio_types(
                page=args.page, page_size=args.page_size, ordering=args.ordering
            )

            print(f"\nTotal portfolio types: {result.count}")
            print("-" * 80)

            for portfolio_type in result.results:
                print(f"ID: {portfolio_type.id}")
                print(f"User Code: {portfolio_type.user_code}")
                print(f"Configuration Code: {portfolio_type.configuration_code}")
                print(f"Name: {portfolio_type.name}")
                if hasattr(portfolio_type, "short_name"):
                    print(f"Short Name: {portfolio_type.short_name}")
                print("-" * 40)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    async def list_history(self, args: argparse.Namespace) -> None:
        """List portfolio history."""
        try:
            result = await self.client.portfolio_history.list_portfolio_history(
                page=args.page, page_size=args.page_size, ordering=args.ordering
            )

            print(f"\nTotal history records: {result.count}")
            print("-" * 80)

            for history in result.results:
                print(f"ID: {history.id}")
                if hasattr(history, "portfolio"):
                    print(f"Portfolio: {history.portfolio}")
                if hasattr(history, "date"):
                    print(f"Date: {history.date}")
                if hasattr(history, "description"):
                    print(f"Description: {history.description}")
                print("-" * 40)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    async def portfolio_status(self, args: argparse.Namespace) -> None:
        """Get portfolio reconciliation status."""
        try:
            status = (
                await self.client.portfolio_reconcile.get_portfolio_reconcile_status()
            )

            print(f"\nPortfolio Reconciliation Status:")
            print("-" * 80)

            if args.json:
                print(json.dumps(status, indent=2))
            else:
                for key, value in status.items():
                    print(f"{key}: {value}")

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def run(self) -> None:
        """Run the CLI application."""
        parser = argparse.ArgumentParser(
            description="Finmars Portfolio API CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=__doc__,
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # List portfolios command
        list_portfolios_parser = subparsers.add_parser(
            "list-portfolios", help="List all portfolios"
        )
        list_portfolios_parser.add_argument(
            "--page", type=int, default=1, help="Page number (default: 1)"
        )
        list_portfolios_parser.add_argument(
            "--page-size", type=int, default=10, help="Page size (default: 10)"
        )
        list_portfolios_parser.add_argument(
            "--ordering", type=str, help="Field to order by"
        )

        # Get portfolio command
        get_portfolio_parser = subparsers.add_parser(
            "get-portfolio", help="Get a specific portfolio by ID"
        )
        get_portfolio_parser.add_argument(
            "--id", type=int, required=True, help="Portfolio ID"
        )

        # List portfolio types command
        list_types_parser = subparsers.add_parser(
            "list-portfolio-types", help="List all portfolio types"
        )
        list_types_parser.add_argument(
            "--page", type=int, default=1, help="Page number (default: 1)"
        )
        list_types_parser.add_argument(
            "--page-size", type=int, default=10, help="Page size (default: 10)"
        )
        list_types_parser.add_argument("--ordering", type=str, help="Field to order by")

        # List history command
        list_history_parser = subparsers.add_parser(
            "list-history", help="List portfolio history"
        )
        list_history_parser.add_argument(
            "--page", type=int, default=1, help="Page number (default: 1)"
        )
        list_history_parser.add_argument(
            "--page-size", type=int, default=10, help="Page size (default: 10)"
        )
        list_history_parser.add_argument(
            "--ordering", type=str, help="Field to order by"
        )

        # Portfolio status command
        status_parser = subparsers.add_parser(
            "portfolio-status", help="Get portfolio reconciliation status"
        )
        status_parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            sys.exit(1)

        # Map commands to methods
        command_map = {
            "list-portfolios": self.list_portfolios,
            "get-portfolio": self.get_portfolio,
            "list-portfolio-types": self.list_portfolio_types,
            "list-history": self.list_history,
            "portfolio-status": self.portfolio_status,
        }

        # Run the appropriate command
        command_func = command_map.get(args.command)
        if command_func:
            asyncio.run(command_func(args))
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)


def main():
    """Main entry point."""
    cli = FinmarsCLI()
    cli.run()


if __name__ == "__main__":
    main()
