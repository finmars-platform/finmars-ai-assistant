"""
Calculator Toolkit using Python's numexpr library.

This toolkit provides a safe calculator tool for mathematical expressions
using the numexpr library for efficient and secure evaluation.
"""

import asyncio
import math
import traceback

import numexpr
from typing import List
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    """Input schema for calculator tool."""

    expression: str = Field(
        ...,
        description=(
            "Mathematical expression to evaluate. "
            "Examples: '37593 * 67', '37593**(1/5)', '2*pi*10', 'sqrt(16)'"
        ),
    )


class CalculatorToolkit:
    """Calculator toolkit using numexpr for safe expression evaluation."""

    async def calculator_python_numexpr(self, expression: str) -> str:
        """
        Calculate expression using Python's numexpr library.

        Expression should be a single line mathematical expression
        that solves the problem.

        Args:
            expression: Mathematical expression to evaluate

        Returns:
            String representation of the calculated result

        Examples:
            "37593 * 67" for "37593 times 67"
            "37593**(1/5)" for "37593^(1/5)"
            "2 * pi * 10" for "2π × 10"
        """
        try:
            # Provide common mathematical constants
            local_dict = {"pi": math.pi, "e": math.e}

            # Evaluate the expression safely
            result = numexpr.evaluate(
                expression.strip(),
                global_dict={},  # restrict access to globals
                local_dict=local_dict,  # add common mathematical functions
            )

            return str(result)
        except SyntaxError as e:
            # Extract the relevant part of the syntax error
            tb = traceback.format_exc()
            # Find the part with the actual syntax error details
            if "<expr>" in tb:
                lines = tb.split("\n")
                relevant_lines = []
                capture = False
                for line in lines:
                    if "<expr>" in line:
                        capture = True
                    if capture:
                        relevant_lines.append(line)
                error_detail = "\n".join(relevant_lines).strip()
            else:
                error_detail = str(e)

            return f"Invalid expression syntax: {expression}\n{error_detail}"
        except Exception as e:
            return f"Error evaluating expression '{expression}': {str(e)}"


def build_calculator_tools() -> List[StructuredTool]:
    """
    Build LangChain tools for calculator operations.

    Returns:
        List of StructuredTool instances for calculator operations
    """
    toolkit = CalculatorToolkit()

    tools = [
        StructuredTool.from_function(
            name="calculator_python_numexpr",
            func=lambda expression: asyncio.run(
                toolkit.calculator_python_numexpr(expression)
            ),
            coroutine=toolkit.calculator_python_numexpr,
            description=(
                "Calculate mathematical expression using Python's numexpr library. "
                "Supports basic arithmetic, exponents, and common mathematical constants (pi, e). "
                "Examples: '37593 * 67', '37593**(1/5)', '2*pi*10'"
            ),
            args_schema=CalculatorInput,
        ),
    ]

    return tools
