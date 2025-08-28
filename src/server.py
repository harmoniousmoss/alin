"""
MCP Server implementation for PostgreSQL database access
Provides secure read-only access to PostgreSQL database
Last modified: 2025-08-28
"""

import logging
from typing import Any, List, Dict
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp import types
from src.config import Config
from src.database import DatabaseManager
from src.security import QueryValidator

logger = logging.getLogger(__name__)

class PostgreSQLMCPServer:
    """MCP Server for PostgreSQL database operations."""
    
    def __init__(self):
        self.config = Config()
        self.config.validate()
        self.db_manager = DatabaseManager(
            secret_arn=self.config.secret_arn,
            region_name=self.config.aws_region
        )
        self.server = Server("postgres-local-mcp-server")
        self._register_tools()
    
    def _register_tools(self):
        """Register all available MCP tools."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List all available tools."""
            return [
                types.Tool(
                    name="execute_select",
                    description="Execute a SELECT query on the PostgreSQL database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL SELECT query to execute"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of rows to return (default: 1000)",
                                "default": 1000,
                                "maximum": 10000
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_tables",
                    description="Get list of all tables in the database",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="describe_table",
                    description="Get schema information for a specific table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table to describe"
                            }
                        },
                        "required": ["table_name"]
                    }
                ),
                types.Tool(
                    name="count_records",
                    description="Count the number of records in a specific table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table to count records"
                            }
                        },
                        "required": ["table_name"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls."""
            try:
                if name == "execute_select":
                    return await self._execute_select(arguments)
                elif name == "get_tables":
                    return await self._get_tables(arguments)
                elif name == "describe_table":
                    return await self._describe_table(arguments)
                elif name == "count_records":
                    return await self._count_records(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def _execute_select(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute a SELECT query with security validation."""
        query = arguments.get("query", "")
        limit = min(arguments.get("limit", 1000), self.config.max_query_rows)
        
        # Validate query
        is_valid, error_msg = QueryValidator.validate_query(query)
        if not is_valid:
            return [types.TextContent(
                type="text",
                text=f"Query validation failed: {error_msg}"
            )]
        
        try:
            results = self.db_manager.execute_query(query, limit=limit)
            return [types.TextContent(
                type="text",
                text=f"Query executed successfully. Returned {len(results)} rows:\n{results}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Query execution failed: {str(e)}"
            )]
    
    async def _get_tables(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get list of all tables in the database."""
        try:
            tables = self.db_manager.get_table_names()
            return [types.TextContent(
                type="text",
                text=f"Database tables:\n{tables}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to get tables: {str(e)}"
            )]
    
    async def _describe_table(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get schema information for a specific table."""
        table_name = arguments.get("table_name", "")
        
        # Validate table name
        is_valid, error_msg = QueryValidator.sanitize_table_name(table_name)
        if not is_valid:
            return [types.TextContent(
                type="text",
                text=f"Table name validation failed: {error_msg}"
            )]
        
        try:
            schema = self.db_manager.describe_table(table_name)
            return [types.TextContent(
                type="text",
                text=f"Schema for table '{table_name}':\n{schema}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to describe table: {str(e)}"
            )]
    
    async def _count_records(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Count records in a specific table."""
        table_name = arguments.get("table_name", "")
        
        # Validate table name
        is_valid, error_msg = QueryValidator.sanitize_table_name(table_name)
        if not is_valid:
            return [types.TextContent(
                type="text",
                text=f"Table name validation failed: {error_msg}"
            )]
        
        try:
            count = self.db_manager.count_table_records(table_name)
            return [types.TextContent(
                type="text",
                text=f"Table '{table_name}' has {count} records"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to count records: {str(e)}"
            )]
    
    def get_server(self) -> Server:
        """Get the MCP server instance."""
        return self.server