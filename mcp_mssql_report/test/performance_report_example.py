#!/usr/bin/env python3
"""
Example usage of the Performance Report functionality
This demonstrates how to call the performance report tool via HTTP API
"""

import asyncio
import json
import requests
from datetime import datetime, timedelta

# Server configuration
SERVER_URL = "http://localhost:3000"
PERFORMANCE_REPORT_ENDPOINT = f"{SERVER_URL}/performance-report"
TOOLS_CALL_ENDPOINT = f"{SERVER_URL}/tools/call"

# Example database configuration (update with your actual values)
DB_CONFIG = {
    "server": "localhost",
    "database": "sample_db",
    "user": "sa",
    "password": "@admin!",
    "port": 1433,
    "encrypt": False,
    "trustServerCertificate": False
}

def test_performance_report_direct_api():
    """Test performance report using direct HTTP API"""
    print("=== Testing Performance Report via Direct API ===")
    
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Sample product list
    products = ["Product A", "Product B", "Product C"]
    
    # Prepare request payload
    payload = {
        **DB_CONFIG,
        "from_date": start_date.strftime("%Y-%m-%d"),
        "to_date": end_date.strftime("%Y-%m-%d"),
        "product_list": products,
        "procedure_name": "sp_GeneratePerformanceReportSimple"  # Optional, uses default if not specified
    }
    
    try:
        print(f"Calling {PERFORMANCE_REPORT_ENDPOINT}")
        print(f"Date range: {payload['from_date']} to {payload['to_date']}")
        print(f"Products: {products}")
        
        response = requests.post(PERFORMANCE_REPORT_ENDPOINT, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Performance report generated successfully!")
            print(f"Success: {result.get('success')}")
            if result.get('recordset'):
                print(f"Records returned: {len(result['recordset'])}")
                print(f"Columns: {result.get('columns')}")
            if result.get('error'):
                print(f"❌ Error: {result['error']}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_performance_report_mcp_tool():
    """Test performance report using MCP tool call API"""
    print("\n=== Testing Performance Report via MCP Tool Call ===")
    
    # Calculate date range (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Sample product list
    products = ["Widget X", "Gadget Y"]
    
    # Prepare MCP tool call payload
    payload = {
        "name": "generate_performance_report",
        "arguments": {
            **DB_CONFIG,
            "from_date": start_date.strftime("%Y-%m-%d"),
            "to_date": end_date.strftime("%Y-%m-%d"),
            "product_list": products,
            "procedure_name": "sp_GeneratePerformanceReportSimple"
        }
    }
    
    try:
        print(f"Calling {TOOLS_CALL_ENDPOINT}")
        print(f"Tool: {payload['name']}")
        print(f"Date range: {payload['arguments']['from_date']} to {payload['arguments']['to_date']}")
        print(f"Products: {products}")
        
        response = requests.post(TOOLS_CALL_ENDPOINT, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCP tool call successful!")
            tool_result = result.get('result', {})
            print(f"Success: {tool_result.get('success')}")
            if tool_result.get('recordset'):
                print(f"Records returned: {len(tool_result['recordset'])}")
            if tool_result.get('report_metadata'):
                metadata = tool_result['report_metadata']
                print(f"Report metadata: {json.dumps(metadata, indent=2)}")
            if tool_result.get('error'):
                print(f"❌ Error: {tool_result['error']}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_server_health():
    """Test if the server is running and responsive"""
    print("=== Testing Server Health ===")
    
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Server is healthy!")
            print(f"Status: {health_data.get('status')}")
            print(f"Active connections: {health_data.get('server_info', {}).get('active_connections', 0)}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running with: python src/python_http_server.py")
        return False

def list_available_tools():
    """List all available MCP tools"""
    print("\n=== Available MCP Tools ===")
    
    try:
        response = requests.get(f"{SERVER_URL}/tools", timeout=5)
        if response.status_code == 200:
            tools_data = response.json()
            tools = tools_data.get('tools', [])
            print(f"Found {len(tools)} tools:")
            for i, tool in enumerate(tools, 1):
                name = tool.get('name', 'Unknown')
                description = tool.get('description', 'No description')
                print(f"{i}. {name}: {description}")
        else:
            print(f"❌ Failed to list tools: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    """Main function to run all tests"""
    print("Performance Report Tool Test Suite")
    print("=" * 50)
    
    # Test server health first
    if not test_server_health():
        return
    
    # List available tools
    list_available_tools()
    
    # Test both API methods
    test_performance_report_direct_api()
    test_performance_report_mcp_tool()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
    print("\nNOTE: Update the DB_CONFIG dictionary with your actual database credentials before running.")
    print("Also ensure your database has the required stored procedure (sp_GeneratePerformanceReport).")

if __name__ == "__main__":
    main()
