# MCP MSSQL Report Tool

## Overview

This project provides a Model Context Protocol (MCP) server and tools for generating performance reports from Microsoft SQL Server databases. It supports both direct HTTP API and MCP tool calls, allowing you to execute SQL queries and stored procedures with flexible parameters such as date ranges and product filters.

## Features

- Date range and product filtering for reports
- Calls configurable stored procedures for custom reporting
- Secure database connection with SSL/TLS by default
- Comprehensive error handling and logging
- Available as both HTTP API and MCP tool

## Folder Structure

- `src/` — MCP server and core logic
- `test/` — Example clients and test scripts
- `docs/` — Documentation and usage guides

## Requirements

- Python 3.9+
- Microsoft SQL Server (with required stored procedures)
- ODBC Driver for SQL Server (17/18 recommended)
- See `requirements.txt` for Python dependencies

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r python_requirements.txt
   ```
2. Ensure you have the correct ODBC driver installed for SQL Server.

## Usage

### 1. Start the MCP Server

```bash
cd src
python python_mcp_server.py
```

### 2. Run Example Client

```bash
cd test
python mcp_client_example.py
```

### 3. Generate a Performance Report (HTTP API)

Send a POST request to your HTTP server (if implemented) with the following JSON body:

```json
{
  "server": "localhost",
  "database": "SalesDB",
  "user": "username",
  "password": "password",
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "product_list": ["Product A", "Product B"],
  "procedure_name": "sp_GeneratePerformanceReport"
}
```

### 4. Generate a Performance Report (MCP Tool Call)

Send a tool call with:

```json
{
  "name": "generate_performance_report",
  "arguments": {
    "server": "localhost",
    "database": "SalesDB",
    "user": "username",
    "password": "password",
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "product_list": ["Product A", "Product B"],
    "procedure_name": "sp_GeneratePerformanceReport"
  }
}
```

## Stored Procedure Requirements

Your SQL Server must have a stored procedure like:

```sql
CREATE PROCEDURE [dbo].[sp_GeneratePerformanceReport]
    @FromDate DATE,
    @ToDate DATE,
    @ProductList dbo.ProductListType READONLY
AS
BEGIN
    -- Your report logic here
END
```

## Error Handling

- Validates required parameters and date formats
- Handles connection and SQL execution errors
- Escapes product names to prevent SQL injection

## Security

- Credentials required for each request
- SSL/TLS enabled by default
- Product names are escaped to prevent SQL injection

## Testing

1. Update the database configuration in the test script (`test/performance_report_example.py`)
2. Ensure your database has the required stored procedure
3. Start the server before running tests

```bash
cd test
python performance_report_example.py
```

## Troubleshooting

- Check all required parameters are present
- Use YYYY-MM-DD for dates
- Ensure stored procedure exists and user has EXECUTE permission
- Check logs for detailed error messages

## Future Enhancements

- Authentication and authorization
- Report scheduling and caching
- Multiple output formats (CSV, Excel, PDF)
- Async report generation
- Email delivery of reports

---

For more details, see the documentation in the `docs/` folder.
