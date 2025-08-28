"""
Configuration management for PostgreSQL MCP Server
Handles environment variables and application settings
Last modified: 2025-08-28
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the MCP server."""
    
    def __init__(self):
        self.secret_arn = os.getenv('SECRET_ARN')
        self.aws_region = os.getenv('AWS_REGION', 'ap-southeast-3')
        self.mcp_server_name = os.getenv('MCP_SERVER_NAME', 'postgres-local-mcp-server')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.max_query_rows = int(os.getenv('MAX_QUERY_ROWS', '1000'))
        self.connection_timeout = int(os.getenv('CONNECTION_TIMEOUT', '30'))
    
    def validate(self) -> bool:
        """Validate required configuration values."""
        if not self.secret_arn:
            raise ValueError("SECRET_ARN environment variable is required")
        if not self.aws_region:
            raise ValueError("AWS_REGION environment variable is required")
        return True