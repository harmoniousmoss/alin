![Jiso](https://icbotbz40ngrmv6r.public.blob.vercel-storage.com/jiso.png)

## Jiso - Model Context Protocol Specialized Database Assistant

Jiso is a specialized database assistant that combines MCP (Model Context Protocol) server architecture with Llama 3/Ollama integration. It provides secure PostgreSQL database access via AWS Secrets Manager and enables natural language database queries through an intelligent streaming chat interface, while maintaining strict security controls and database-focused conversations.

## Features

- 🔐 **Secure Access**: Uses AWS Secrets Manager for database credentials (no hardcoded passwords)
- 🛡️ **Query Safety**: Only allows SELECT operations with built-in SQL injection protection
- 🔌 **MCP Architecture**: Built on Model Context Protocol for extensible tool integration
- 📊 **Database Tools**: List tables, describe schemas, count records, and execute safe queries
- 🎯 **Row Limiting**: Automatic query result limiting to prevent resource exhaustion
- 🧠 **AI-Powered**: Llama 3 via Ollama for natural language understanding
- 💬 **Streaming Chat**: Real-time conversational interface like ChatGPT/Claude with intelligent query detection
- 🎯 **Database Focused**: Redirects non-database queries to maintain professional scope
- 🔍 **Smart Intent Detection**: Automatically detects and routes database vs general queries

## Prerequisites

- Python 3.8+
- Ollama installed and running locally
- Llama 3 model available in Ollama (`ollama pull llama3:latest`)
- AWS CLI configured with appropriate permissions
- PostgreSQL database accessible from your environment
- AWS Secrets Manager secret containing database credentials


## Core Functionality

### Interactive Chat Interface
The primary feature is the intelligent chat interface (`python chat_with_database.py`):

- **Natural Language Processing**: Ask questions in plain English
- **Real-time Streaming**: Responses appear word-by-word like modern AI assistants  
- **Database Focus**: Automatically redirects non-database queries back to database operations
- **Smart Detection**: Recognizes different types of database queries and routes appropriately

### Available Database Operations

- **Table Discovery**: "What tables are available?" or "How many tables are there?"
- **Schema Analysis**: "Show me the structure of web_items" or "Which table has the most columns?"
- **Record Counting**: "How many records are in web_items?"
- **Data Retrieval**: "Show me 10 latest data from web_items" or "Find recent items"

### MCP Server Tools

- **get_tables**: List all database tables
- **describe_table**: Get table schema and column information  
- **get_all_schemas**: Compare schemas across multiple tables
- **count_records**: Count rows in a specific table
- **execute_select**: Run safe SELECT queries with automatic limiting

## Security Features

- ✅ **SELECT-only queries**: Only SELECT statements are allowed
- ✅ **SQL injection protection**: Query validation with word-boundary keyword detection
- ✅ **Row limiting**: Automatic LIMIT clause enforcement (max 1000 rows)
- ✅ **Credential security**: No database credentials in code or logs
- ✅ **AWS integration**: Leverages AWS IAM and Secrets Manager

## Example Conversations

### Database Queries (Streamed Responses)
```
👤 You: What tables are in the database?
🔍 Detected database query: get_tables
⏳ Querying database...
📊 Database query completed! Generating response...

🤖 Assistant: I found 3 tables in your database: web_items, web_raw_content, 
and web_translated_content. Each table serves a different purpose for storing 
web content and translations.
```

```
👤 You: List all the table with the most column  
🔍 Detected database query: get_all_schemas
⏳ Querying database...
📊 Database query completed! Generating response...

🤖 Assistant: After analyzing all tables, here's the column count comparison:
- web_items: 23 columns (most columns)
- web_raw_content: 8 columns  
- web_translated_content: 6 columns

The web_items table has the most columns with 23 total columns.
```

### Non-Database Queries (Focused Redirection)
```
👤 You: who is barack obama?
🤖 Assistant: Hello! I'm happy to help, but I must politely redirect you. 
The question "who is barack obama?" is not related to our PostgreSQL database queries.

Instead, let's explore some exciting database-related questions! Here are a few suggestions:
- What tables are available?
- Show me the structure of [table_name]
- How many records are in [table_name]?
- Show me sample data from [table_name]
```

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
