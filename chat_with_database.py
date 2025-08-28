#!/usr/bin/env python3
"""
Interactive chat interface with PostgreSQL database via MCP server
Chat with your database using natural language powered by Ollama
Last modified: 2025-08-28
"""

import asyncio
import json
import re
import requests
from typing import List, Dict, Any
from src.server import PostgreSQLMCPServer

class DatabaseChatBot:
    """Interactive chatbot that can query database via MCP server."""
    
    def __init__(self):
        self.mcp_server = PostgreSQLMCPServer()
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3:latest"
        self.conversation_history = []
        self.available_tables = []
        
    async def initialize(self):
        """Initialize the chatbot and get database info."""
        try:
            # Get list of tables for context
            tables_result = await self.mcp_server._get_tables({})
            tables_text = tables_result[0].text
            # Extract table names from the response
            if "['web_items'" in tables_text:
                self.available_tables = ['web_items', 'web_raw_content', 'web_translated_content']
            print("🤖 Database chatbot initialized successfully!")
            print(f"📊 Available tables: {', '.join(self.available_tables)}")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize database connection: {e}")
    
    def call_ollama_streaming(self, prompt: str):
        """Call Ollama API with streaming support."""
        try:
            response = requests.post(self.ollama_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }, timeout=60, stream=True)
            
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'response' in data:
                                chunk = data['response']
                                print(chunk, end='', flush=True)
                                full_response += chunk
                                if data.get('done', False):
                                    break
                        except json.JSONDecodeError:
                            continue
                return full_response
            else:
                error_msg = f"Error: {response.status_code}"
                print(error_msg)
                return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {e}"
            print(error_msg)
            return error_msg
    
    async def execute_database_query(self, tool_name: str, params: dict) -> str:
        """Execute database query via MCP server."""
        try:
            if tool_name == "get_tables":
                result = await self.mcp_server._get_tables(params)
            elif tool_name == "describe_table":
                result = await self.mcp_server._describe_table(params)
            elif tool_name == "get_all_schemas":
                # Get schemas for all tables to compare column counts
                all_schemas = {}
                for table in self.available_tables:
                    result = await self.mcp_server._describe_table({"table_name": table})
                    all_schemas[table] = result[0].text
                
                # Format results for AI to analyze
                schema_summary = "Table schemas:\n\n"
                for table, schema in all_schemas.items():
                    # Extract column count from schema
                    import ast
                    schema_start = schema.find('[')
                    if schema_start > 0:
                        try:
                            schema_data = ast.literal_eval(schema[schema_start:])
                            column_count = len(schema_data)
                            schema_summary += f"{table}: {column_count} columns\n"
                        except:
                            schema_summary += f"{table}: schema parsing error\n"
                
                return schema_summary
            elif tool_name == "count_records":
                result = await self.mcp_server._count_records(params)
            elif tool_name == "execute_select":
                result = await self.mcp_server._execute_select(params)
            else:
                return f"Unknown tool: {tool_name}"
            
            return result[0].text if result else "No results"
        except Exception as e:
            return f"Database error: {e}"
    
    def detect_database_intent(self, user_input: str) -> tuple[str, dict]:
        """Detect if user wants to query database and determine appropriate tool."""
        user_lower = user_input.lower()
        
        # Database query patterns - check most specific patterns first
        
        # Table-related queries (check before generic "how many")
        if any(phrase in user_lower for phrase in ["how many table", "number of table", "what tables", "list tables"]) or user_lower == "tables":
            return "get_tables", {}
        
        # Column/schema queries
        elif any(word in user_lower for word in ["schema", "structure", "columns", "describe", "column", "most column"]):
            # Check if asking for comparison across tables
            if any(word in user_lower for word in ["most", "all", "compare", "which"]):
                # User wants to compare tables - describe all tables
                return "get_all_schemas", {}
            # Try to extract specific table name
            for table in self.available_tables:
                if table in user_lower:
                    return "describe_table", {"table_name": table}
            return "describe_table", {"table_name": "web_items"}  # Default
        
        # Record count queries (after table queries to avoid conflict)
        elif any(word in user_lower for word in ["count", "how many", "records", "rows"]) and not "table" in user_lower:
            # Try to extract table name
            for table in self.available_tables:
                if table in user_lower:
                    return "count_records", {"table_name": table}
            return "count_records", {"table_name": "web_items"}  # Default
        
        elif any(word in user_lower for word in ["select", "show", "find", "search", "get data", "sample"]):
            # Generate appropriate SELECT query
            if "title" in user_lower:
                query = "SELECT title, url FROM web_items LIMIT 5"
            elif "recent" in user_lower or "latest" in user_lower:
                query = "SELECT title, url, created_at FROM web_items ORDER BY created_at DESC LIMIT 5"
            else:
                query = "SELECT title, url FROM web_items LIMIT 5"
            return "execute_select", {"query": query}
        
        return None, {}
    
    async def process_user_input(self, user_input: str) -> str:
        """Process user input and generate response."""
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Check if this is a database query
        tool_name, tool_params = self.detect_database_intent(user_input)
        
        if tool_name:
            print(f"🔍 Detected database query: {tool_name}")
            print("⏳ Querying database...", end="", flush=True)
            
            # Execute database query
            db_result = await self.execute_database_query(tool_name, tool_params)
            print("\r📊 Database query completed! Generating response...\n", end="", flush=True)
            
            # Use AI to format the response
            format_prompt = f"""
You are a helpful database assistant. A user asked: "{user_input}"

I queried the database and got this result:
{db_result}

Please provide a clear, helpful, and conversational response to the user based on this database information. Be friendly and concise.
"""
            
            ai_response = self.call_ollama_streaming(format_prompt)
            
        else:
            # Non-database query - redirect to database functionality
            redirect_prompt = f"""
You are a database assistant specialized in PostgreSQL database queries. The user asked: "{user_input}"

This question is not related to database operations. Please politely redirect them to use the database functionality.

Available database tables: {', '.join(self.available_tables)}

Respond briefly and suggest they ask database-related questions like:
- "What tables are available?"
- "Show me the structure of [table_name]"  
- "How many records are in [table_name]?"
- "Show me sample data from [table_name]"

Be helpful but keep the focus on database operations only.
"""
            
            ai_response = self.call_ollama_streaming(redirect_prompt)
        
        # Add AI response to history
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response
    
    def print_help(self):
        """Print help information."""
        print("""
💡 Database Chat Help:
━━━━━━━━━━━━━━━━━━━━━━

🗣️  General Commands:
• Type naturally - ask questions about the database
• Type 'help' for this menu
• Type 'quit' or 'exit' to end chat

🗃️  Database Queries You Can Ask:
• "What tables are available?"
• "Show me the structure of web_items table"
• "How many records are in web_items?"
• "Show me some sample data"
• "Find recent items"
• "Search for titles with [keyword]"

📊 Available Tables: {0}

💬 Just chat naturally - I'll detect when you want database info!
        """.format(', '.join(self.available_tables)))

async def main():
    """Main chat loop."""
    print("🚀 Database Chat Interface")
    print("=" * 50)
    print("💬 Chat with your PostgreSQL database using natural language!")
    print("🤖 Powered by Ollama + MCP Server")
    print("Type 'help' for commands, 'quit' to exit")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = DatabaseChatBot()
    await chatbot.initialize()
    
    print("\n💡 Try asking: 'What tables do we have?' or 'Show me some data'")
    print("🗣️  You can also just chat normally!\n")
    
    while True:
        try:
            # Get user input
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Thanks for chatting!")
                break
                
            if user_input.lower() in ['help', '?']:
                chatbot.print_help()
                continue
            
            # Process input and get response with streaming
            print("🤖 Assistant: ", end="", flush=True)
            response = await chatbot.process_user_input(user_input)
            # Response is already printed via streaming, just add newlines
            print("\n")  # Add blank lines for readability
            
        except KeyboardInterrupt:
            print("\n👋 Chat ended by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'help' for assistance.\n")

if __name__ == "__main__":
    asyncio.run(main())