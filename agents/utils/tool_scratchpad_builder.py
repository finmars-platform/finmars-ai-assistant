"""Tool Scratchpad Builder for generating prompt strings for available tools"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
import json


class ToolScratchpadBuilder:
    """Builds formatted tool descriptions for LLM prompts"""
    
    def __init__(self):
        self.tools: List[BaseTool] = []
        
    def add_tool(self, tool: BaseTool) -> None:
        """Add a tool to the scratchpad builder"""
        self.tools.append(tool)
        
    def add_tools(self, tools: List[BaseTool]) -> None:
        """Add multiple tools to the scratchpad builder"""
        self.tools.extend(tools)
        
    def build(self) -> str:
        """Build the formatted tool scratchpad string"""
        if not self.tools:
            return "No tools available."
            
        scratchpad_lines = []
        scratchpad_lines.append("Here are the tools available to help you:")
        scratchpad_lines.append("")
        
        for idx, tool in enumerate(self.tools, 1):
            # Add tool header
            scratchpad_lines.append(f"{idx}. tool_name='{tool.name}'")
            scratchpad_lines.append("WARNING: Can be used as tool call!")
            
            # Add tool description
            if tool.description:
                scratchpad_lines.append(f"tool_description='{tool.description}'")
            
            # Add input schema if available
            if hasattr(tool, 'args_schema') and tool.args_schema:
                schema_json = self._get_pydantic_schema_json(tool.args_schema)
                if schema_json:
                    scratchpad_lines.append(f"Input Schema:")
                    scratchpad_lines.append(schema_json)
                    
            # # Add output/response format information if available
            # if hasattr(tool, 'response_format') and tool.response_format:
            #     scratchpad_lines.append(f"Response Format: {tool.response_format}")
                
            # Add separator
            scratchpad_lines.append("=" * 150)
            scratchpad_lines.append("")
            
        return "\n".join(scratchpad_lines)
    
    def _get_pydantic_schema_json(self, schema_class: Any) -> str:
        """Get JSON schema from Pydantic model"""
        try:
            if hasattr(schema_class, 'model_json_schema'):
                # Get the JSON schema from Pydantic model
                schema_dict = schema_class.model_json_schema()
                # Format with indentation for readability
                return json.dumps(schema_dict, indent=2)
            elif hasattr(schema_class, 'schema'):
                # Fallback for older Pydantic versions
                schema_dict = schema_class.schema()
                return json.dumps(schema_dict, indent=2)
        except Exception as e:
            # If we can't get the schema, return a simple string
            return f"Schema parsing error: {str(e)}"
            
        return ""


def create_tool_scratchpad(tools: List[BaseTool]) -> str:
    """Convenience function to create a tool scratchpad from a list of tools"""
    builder = ToolScratchpadBuilder()
    builder.add_tools(tools)
    return builder.build()