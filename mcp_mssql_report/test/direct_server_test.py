#!/usr/bin/env python3
"""
Simple test script for the MCP Ask DBA Server
Tests both tools by running the server directly
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path to import the server
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from python_mcp_server import AskDBAServer, DatabaseConfig, ConnectionManager
    print("✅ Successfully imported MCP server components")
except ImportError as e:
    print(f"❌ Failed to import server components: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Example database configuration (update with your actual values)
DB_CONFIG = {
    "server": "127.0.0.1",
    "database": "sample_db",
    "user": "sa",
    "password": "admin",
    "port": 1433,
    "encrypt": False,
    "trustServerCertificate": False
}

async def test_ask_dba_tool():
    """Test the ask_dba tool directly"""
    print("=== Testing ask_dba tool ===")
    
    server = AskDBAServer()
    
    # Sample SQL query
    query = "SELECT TOP 10 * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
    
    arguments = {
        **DB_CONFIG,
        "query": query
    }
    
    try:
        result = await server._execute_ask_dba_tool(arguments)
        print("✅ ask_dba tool call successful!")
        
        if result and len(result) > 0:
            content = result[0]
            if hasattr(content, 'text'):
                response_data = json.loads(content.text)
                print(f"Success: {response_data.get('success')}")
                if response_data.get('recordset'):
                    print(f"Records returned: {len(response_data['recordset'])}")
                    print(f"Columns: {response_data.get('columns')}")
                    for i, row in enumerate(response_data['recordset'], 1):
                        print(f"Row {i}: {row}")
                if response_data.get('error'):
                    print(f"❌ Error: {response_data['error']}")
        
    except Exception as e:
        print(f"❌ ask_dba tool call failed: {e}")
    finally:
        await server.cleanup()

async def test_performance_report_tool():
    """Test the generate_performance_report tool directly"""
    print("\n=== Testing generate_performance_report tool ===")
    
    server = AskDBAServer()
    
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Sample product list
    products = ["Widget A", "Widget B", "Product C"]
    
    arguments = {
        **DB_CONFIG,
        "from_date": start_date.strftime("%Y-%m-%d"),
        "to_date": end_date.strftime("%Y-%m-%d"),
        "product_list": products,
        #"procedure_name": "sp_GeneratePerformanceReport"
        "procedure_name": "sp_GeneratePerformanceReportSimple"
    }
    
    try:
        result = await server._execute_performance_report_tool(arguments)
        print("✅ generate_performance_report tool call successful!")
        print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"Products: {products}")

        if result and len(result) > 0:
            content = result[0]
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
    finally:
        await server.cleanup()

async def test_connection_manager():
    """Test the connection manager functionality"""
    print("\n=== Testing Connection Manager ===")
    
    connection_manager = ConnectionManager()
    
    try:
        config = DatabaseConfig(
            server=DB_CONFIG["server"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"],
            encrypt=DB_CONFIG["encrypt"],
            trust_cert=DB_CONFIG["trustServerCertificate"]
        )
        
        # Test simple query
        result = await connection_manager.execute_query(config, "SELECT 1 as TestValue")
        print("✅ Connection manager test successful!")
        print(f"Test query result: {result}")
        
    except Exception as e:
        print(f"❌ Connection manager test failed: {e}")
        print("This is expected if you haven't configured valid database credentials")
    finally:
        await connection_manager.close_all()

async def list_tools_schema():
    """Show the tool schemas"""
    print("\n=== Tool Schemas ===")
    
    server = AskDBAServer()
    
    try:
        # Get the tools using the handler
        tools = await server._setup_handlers.__code__.co_names
        print("Tools available in the server:")
        print("1. ask_dba - Execute SQL queries")
        print("2. generate_performance_report - Generate performance reports")
        
        print("\nTool schemas have been defined with the following capabilities:")
        print("- ask_dba: Requires server, database, user, password, query")
        print("- generate_performance_report: Requires server, database, user, password, from_date, to_date, product_list")
        
    except Exception as e:
        print(f"Note: {e}")

def validate_environment():
    """Validate the environment setup"""
    print("=== Environment Validation ===")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check required modules
    required_modules = ['pyodbc', 'mcp']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} is available")
        except ImportError:
            print(f"❌ {module} is not available - install with: pip install {module}")
    
    # Check if server file exists
    server_file = os.path.join(os.path.dirname(__file__), '..', 'src', 'python_mcp_server.py')
    if os.path.exists(server_file):
        print(f"✅ Server file found: {server_file}")
    else:
        print(f"❌ Server file not found: {server_file}")

async def main():
    """Main function to run all tests"""
    print("MCP Ask DBA Server Direct Test Suite")
    print("=" * 50)
    
    # Validate environment
    validate_environment()
    
    # Show tool schemas
    await list_tools_schema()
    
    # Test connection manager
    await test_connection_manager()
    
    # Test tools (these will fail without proper DB config, but show the structure)
    await test_ask_dba_tool()
    await test_performance_report_tool()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
    print("\nNOTE: To test with actual database:")
    print("1. Update the DB_CONFIG dictionary with your actual database credentials")
    print("2. Ensure your database has the required stored procedure (sp_GeneratePerformanceReport)")
    print("3. Install required dependencies: pip install pyodbc mcp")

if __name__ == "__main__":
    asyncio.run(main())
