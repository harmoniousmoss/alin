# Alin

Alin is an MCP (Model Context Protocol) Server with Llama 3/Ollama integration that provides secure PostgreSQL database access via AWS Secrets Manager. It enables natural language database queries through an intelligent chat interface powered by Llama 3, while maintaining strict security controls.

## Features

- 🔐 **Secure Access**: Uses AWS Secrets Manager for database credentials (no hardcoded passwords)
- 🛡️ **Query Safety**: Only allows SELECT operations with built-in SQL injection protection
- 🔌 **MCP Architecture**: Built on Model Context Protocol for extensible tool integration
- 📊 **Database Tools**: List tables, describe schemas, count records, and execute safe queries
- 🎯 **Row Limiting**: Automatic query result limiting to prevent resource exhaustion
- 🧠 **AI-Powered**: Llama 3 via Ollama for natural language understanding
- 💬 **Interactive Chat**: Conversational database interface with intelligent query detection

## Prerequisites

- Python 3.8+
- Ollama installed and running locally
- Llama 3 model available in Ollama (`ollama pull llama3:latest`)
- AWS CLI configured with appropriate permissions
- PostgreSQL database accessible from your environment
- AWS Secrets Manager secret containing database credentials


## Available MCP Tools

- **get_tables**: List all database tables
- **describe_table**: Get table schema and column information
- **count_records**: Count rows in a specific table  
- **execute_select**: Run safe SELECT queries with automatic limiting

## Security Features

- ✅ **SELECT-only queries**: Only SELECT statements are allowed
- ✅ **SQL injection protection**: Query validation and sanitization
- ✅ **Row limiting**: Automatic LIMIT clause enforcement (max 1000 rows)
- ✅ **Credential security**: No database credentials in code or logs
- ✅ **AWS integration**: Leverages AWS IAM and Secrets Manager

## Example Conversations

Once configured, you can have natural conversations with your database via Llama 3:

**You:** "What tables are in the database?"  
**Llama 3:** "I found 3 tables in your database: web_items, web_raw_content, and web_translated_content."

**You:** "Show me the structure of the web_items table"  
**Llama 3:** "The web_items table has 5 columns: id (integer, primary key), title (text), url (text), created_at (timestamp), and content (text)."

**You:** "How many records are there?"  
**Llama 3:** "There are 1,247 records in the web_items table."

**You:** "Show me some recent items"  
**Llama 3:** "Here are the 5 most recent items: [displays formatted results with titles and URLs]"

## Project Structure

```
alin/
├── src/
│   ├── __init__.py
│   ├── server.py          # Main MCP server implementation
│   ├── database.py        # PostgreSQL connection manager
│   ├── security.py        # Query validation and security
│   └── config.py          # Configuration management
├── main.py                # MCP server entry point
├── chat_with_database.py  # Interactive chat interface
├── test_server.py         # Test suite
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```
