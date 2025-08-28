"""
PostgreSQL database manager with AWS Secrets Manager integration
Handles secure database connections and query execution
Last modified: 2025-08-28
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List
import boto3
import psycopg
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages PostgreSQL database connections using AWS Secrets Manager."""
    
    def __init__(self, secret_arn: str, region_name: str, max_retries: int = 3):
        self.secret_arn = secret_arn
        self.region_name = region_name
        self.max_retries = max_retries
        self.secrets_client = boto3.client('secretsmanager', region_name=region_name)
        self._connection = None
        self._db_credentials = None
    
    def get_secret(self) -> Dict[str, Any]:
        """Retrieve database credentials from AWS Secrets Manager with retry logic."""
        if self._db_credentials:
            return self._db_credentials
            
        for attempt in range(self.max_retries):
            try:
                response = self.secrets_client.get_secret_value(SecretId=self.secret_arn)
                self._db_credentials = json.loads(response['SecretString'])
                return self._db_credentials
            except ClientError as e:
                logger.error(f"Attempt {attempt + 1}: Failed to retrieve secret: {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to retrieve secret after {self.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def get_connection(self):
        """Get or create a PostgreSQL connection with retry logic."""
        if self._connection and not self._connection.closed:
            return self._connection
            
        credentials = self.get_secret()
        
        for attempt in range(self.max_retries):
            try:
                self._connection = psycopg.connect(
                    host=credentials['host'],
                    port=credentials.get('port', 5432),
                    dbname=credentials['dbname'],
                    user=credentials['username'],
                    password=credentials['password'],
                    connect_timeout=30
                )
                return self._connection
            except psycopg.Error as e:
                logger.error(f"Attempt {attempt + 1}: Failed to connect to database: {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to connect to database after {self.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)
    
    def execute_query(self, query: str, params: Optional[tuple] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results with row limit."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # Clean up query and add LIMIT clause if not present
                query = query.strip().rstrip(';')
                if 'LIMIT' not in query.upper():
                    query = f"{query} LIMIT {limit}"
                
                cursor.execute(query, params)
                columns = [desc.name for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except psycopg.Error as e:
            conn.rollback()
            raise Exception(f"Query execution failed: {e}")
    
    def get_table_names(self) -> List[str]:
        """Get list of all tables in the current database."""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
        """
        results = self.execute_query(query)
        return [row['table_name'] for row in results]
    
    def describe_table(self, table_name: str) -> List[Dict[str, Any]]:
        """Get table schema information."""
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = %s AND table_schema = 'public'
        ORDER BY ordinal_position;
        """
        return self.execute_query(query, (table_name,))
    
    def count_table_records(self, table_name: str) -> int:
        """Count records in a specific table."""
        # Sanitize table name to prevent SQL injection
        if not table_name.replace('_', '').isalnum():
            raise ValueError("Invalid table name")
        
        query = f"SELECT COUNT(*) as count FROM {table_name};"
        result = self.execute_query(query)
        return result[0]['count']
    
    def close(self):
        """Close the database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()