#!/usr/bin/env python3
"""
Example MCP Client for Ask DBA Server
This demonstrates how to use both the ask_dba and generate_performance_report tools
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Any, Dict

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    print("✅ Successfully imported MCP client components")
except ImportError:
    print("MCP client library not found. Install with: pip install mcp")
    sys.exit(1)

# Example database configuration (update with your actual values)
DB_CONFIG = {
    "server": "127.0.0.1",
    "database": "sample_db",
    "user": "sa",
    "password": "@admin!",
    "port": 1433,
    "encrypt": False,
    "trustServerCertificate": False
}

async def test_ask_dba_tool(session: ClientSession):
    """Test the ask_dba tool"""
    print("=== Testing ask_dba tool ===")
    
    # Sample SQL query
    query = "SELECT TOP 5 * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
    
    try:
        result = await session.call_tool(
            "ask_dba",
            arguments={
                **DB_CONFIG,
                "query": query
            }
        )
        
        print("✅ ask_dba tool call successful!")
        if result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    response_data = json.loads(content.text)
                    print(f"Success: {response_data.get('success')}")
                    if response_data.get('recordset'):
                        print(f"Records returned: {len(response_data['recordset'])}")
                        print(f"Columns: {response_data.get('columns')}")
                    if response_data.get('error'):
                        print(f"❌ Error: {response_data['error']}")
        
    except Exception as e:
        print(f"❌ ask_dba tool call failed: {e}")

async def test_performance_report_tool(session: ClientSession):
    """Test the generate_performance_report tool"""
    print("\n=== Testing generate_performance_report tool ===")
    
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Sample product list
    products = ["Product A", "Product B", "Product C"]
    
    try:
        result = await session.call_tool(
            "generate_performance_report",
            arguments={
                **DB_CONFIG,
                "from_date": start_date.strftime("%Y-%m-%d"),
                "to_date": end_date.strftime("%Y-%m-%d"),
                "product_list": products,
                "procedure_name": "sp_GeneratePerformanceReport"
            }
        )
        
        print("✅ generate_performance_report tool call successful!")
        print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"Products: {products}")
        
        if result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    response_data = json.loads(content.text)
                    print(f"Success: {response_data.get('success')}")
                    if response_data.get('recordset'):
                        print(f"Records returned: {len(response_data['recordset'])}")
                        print(f"Columns: {response_data.get('columns')}")
                    if response_data.get('report_metadata'):
                        metadata = response_data['report_metadata']
                        print(f"Report metadata: {json.dumps(metadata, indent=2)}")
                    if response_data.get('error'):
                        print(f"❌ Error: {response_data['error']}")
        
    except Exception as e:
        print(f"❌ generate_performance_report tool call failed: {e}")

async def list_available_tools(session: ClientSession):
    """List all available tools"""
    print("=== Available Tools ===")
    
    try:
        tools = await session.list_tools()
        print(f"Found {len(tools.tools)} tools:")
        for i, tool in enumerate(tools.tools, 1):
            print(f"{i}. {tool.name}: {tool.description}")
            
    except Exception as e:
        print(f"❌ Failed to list tools: {e}")

import os
async def main():
    """Main function to run MCP client tests"""
    print("MCP Ask DBA Server Client Test")
    print("=" * 50)
    
    # Add the src directory to the path to import the server
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    # Server parameters - adjust path as needed
    server_params = StdioServerParameters(
        command="python",
        args=["D:\\AI\\GenAI_Solution\\mcp_mssql_report\\src\\python_mcp_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                init_result = await session.initialize()
                print(f"✅ Session initialized: {init_result}")
                
                # List available tools
                await list_available_tools(session)
                
                # Test both tools
                await test_ask_dba_tool(session)
                await test_performance_report_tool(session)
                
    except Exception as e:
        print(f"❌ MCP session failed: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("Make sure the MCP server is working and the path is correct")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nNOTE: Update the DB_CONFIG dictionary with your actual database credentials.")
    print("Also ensure your database has the required stored procedure (sp_GeneratePerformanceReport).")

if __name__ == "__main__":
    asyncio.run(main())
