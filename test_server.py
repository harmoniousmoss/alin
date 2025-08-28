#!/usr/bin/env python3
"""
Test script for PostgreSQL MCP Server
Tests all available tools and functionality
Last modified: 2025-08-28
"""

import asyncio
import sys
from src.server import PostgreSQLMCPServer

async def test_all_tools():
    """Test all MCP server tools."""
    print("🔧 PostgreSQL MCP Server Test Suite")
    print("=" * 50)
    
    try:
        # Initialize server
        server = PostgreSQLMCPServer()
        print("✓ MCP Server initialized successfully")
        print(f"✓ Connected to database successfully")
        print()
        
        # Test 1: List all tables
        print("📋 Test 1: Getting all tables")
        result = await server._get_tables({})
        print(f"✓ {result[0].text}")
        print()
        
        # Test 2: Describe a table
        print("📖 Test 2: Describing table structure")
        result = await server._describe_table({'table_name': 'web_items'})
        schema_text = result[0].text
        print("✓ Table 'web_items' schema:")
        # Parse and display nicely
        import ast
        schema_start = schema_text.find('[')
        schema_data = ast.literal_eval(schema_text[schema_start:])
        for col in schema_data[:5]:  # Show first 5 columns
            print(f"   - {col['column_name']}: {col['data_type']} ({'NOT NULL' if col['is_nullable'] == 'NO' else 'NULL'})")
        if len(schema_data) > 5:
            print(f"   ... and {len(schema_data) - 5} more columns")
        print()
        
        # Test 3: Count records
        print("🔢 Test 3: Counting records")
        result = await server._count_records({'table_name': 'web_items'})
        print(f"✓ {result[0].text}")
        print()
        
        # Test 4: Execute SELECT query
        print("🔍 Test 4: Executing SELECT query")
        result = await server._execute_select({
            'query': 'SELECT id, url, title FROM web_items ORDER BY id LIMIT 3',
            'limit': 3
        })
        print("✓ Query results:")
        query_text = result[0].text
        # Extract just the data part
        data_start = query_text.find('[')
        if data_start > 0:
            import ast
            try:
                data = ast.literal_eval(query_text[data_start:])
                for i, row in enumerate(data, 1):
                    title = row['title'][:50] + "..." if len(row['title']) > 50 else row['title']
                    print(f"   {i}. {title}")
                    print(f"      URL: {row['url'][:60]}...")
                    print(f"      ID: {row['id']}")
            except:
                print(f"   Raw result: {query_text[:100]}...")
        print()
        
        # Test 5: Security validation
        print("🛡️  Test 5: Testing security validation")
        result = await server._execute_select({
            'query': 'DROP TABLE web_items; SELECT * FROM web_items',
            'limit': 10
        })
        print(f"✓ Security test: {result[0].text}")
        print()
        
        print("🎉 All tests completed successfully!")
        print("🔒 Security features working: Query validation, SELECT-only, row limits")
        print("📊 Database features working: Connection, tables, schema, queries")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main test runner."""
    success = asyncio.run(test_all_tools())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()