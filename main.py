#!/usr/bin/env python3
"""
Main entry point for PostgreSQL MCP Server
Connects to PostgreSQL database via AWS Secrets Manager
Last modified: 2025-08-28
"""

import logging
import sys
import os

from mcp.server.stdio import stdio_server
from src.server import PostgreSQLMCPServer

def setup_logging():
    """Configure logging for the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )

def main():
    """Main entry point for the MCP server."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting PostgreSQL MCP Server")
        mcp_server = PostgreSQLMCPServer()
        server = mcp_server.get_server()
        
        # Run the server
        stdio_server(server)
        
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()