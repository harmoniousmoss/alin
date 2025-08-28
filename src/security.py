"""
Security validation layer for PostgreSQL MCP Server
Implements query validation and SQL injection prevention
Last modified: 2025-08-28
"""

import re
from typing import List, Set

class QueryValidator:
    """Validates SQL queries for security and compliance."""
    
    # Allowed SQL keywords for SELECT queries only
    ALLOWED_KEYWORDS: Set[str] = {
        'SELECT', 'FROM', 'WHERE', 'ORDER', 'BY', 'GROUP', 'HAVING',
        'LIMIT', 'OFFSET', 'AS', 'AND', 'OR', 'NOT', 'IN', 'LIKE',
        'BETWEEN', 'IS', 'NULL', 'DISTINCT', 'COUNT', 'SUM', 'AVG',
        'MIN', 'MAX', 'INNER', 'LEFT', 'RIGHT', 'OUTER', 'JOIN', 'ON'
    }
    
    # Dangerous keywords that should be blocked
    BLOCKED_KEYWORDS: Set[str] = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', 'CALL',
        'PROCEDURE', 'FUNCTION', 'TRIGGER', 'SCHEMA', 'DATABASE'
    }
    
    # Suspicious patterns that might indicate SQL injection
    INJECTION_PATTERNS: List[str] = [
        r";\s*(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER|TRUNCATE)",
        r"--",  # SQL comments
        r"/\*.*\*/",  # Multi-line comments
        r"UNION\s+SELECT",
        r"'\s*OR\s*'",
        r"'\s*;\s*",
        r"xp_cmdshell",
        r"sp_executesql"
    ]
    
    @classmethod
    def validate_query(cls, query: str) -> tuple[bool, str]:
        """
        Validate a SQL query for security compliance.
        Returns (is_valid, error_message).
        """
        if not query or not query.strip():
            return False, "Empty query not allowed"
        
        query_upper = query.upper().strip()
        
        # Check if query starts with SELECT
        if not query_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
        
        # Check for blocked keywords
        for keyword in cls.BLOCKED_KEYWORDS:
            if keyword in query_upper:
                return False, f"Blocked keyword '{keyword}' found in query"
        
        # Check for injection patterns
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"Potentially malicious pattern detected"
        
        # Check for multiple statements (basic check)
        if query.count(';') > 1:
            return False, "Multiple statements not allowed"
        
        return True, ""
    
    @classmethod
    def sanitize_table_name(cls, table_name: str) -> tuple[bool, str]:
        """
        Validate and sanitize table name.
        Returns (is_valid, error_message).
        """
        if not table_name:
            return False, "Table name cannot be empty"
        
        # Allow only alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            return False, "Invalid table name format"
        
        # Check length
        if len(table_name) > 63:  # PostgreSQL limit
            return False, "Table name too long"
        
        return True, ""