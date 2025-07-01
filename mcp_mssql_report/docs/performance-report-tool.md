# Performance Report Tool Documentation

## Overview

The Performance Report Tool is a new feature that allows you to generate performance reports by calling stored procedures with date ranges and product filters. This tool extends the existing Ask DBA server functionality to provide specialized reporting capabilities.

## Features

- **Date Range Filtering**: Specify start and end dates for report generation
- **Product Filtering**: Include specific products in the report using a product list
- **Stored Procedure Integration**: Calls configurable stored procedures to generate reports
- **Multiple API Access Methods**: Available via direct HTTP API and MCP tool calls
- **Flexible Configuration**: Customizable procedure names and parameters

## API Endpoints

### 1. Direct HTTP API

**Endpoint**: `POST /performance-report`

**Request Body**:
```json
{
  "server": "localhost",
  "database": "SalesDB",
  "user": "username",
  "password": "password",
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "product_list": ["Product A", "Product B", "Product C"],
  "procedure_name": "sp_GeneratePerformanceReport",
  "port": 1433,
  "encrypt": true,
  "trustServerCertificate": false
}
```

**Response**:
```json
{
  "success": true,
  "rowsAffected": null,
  "recordset": [
    {
      "ProductName": "Product A",
      "TotalOrders": 150,
      "TotalRevenue": 25000.00,
      "AverageUnitPrice": 166.67
    }
  ],
  "columns": ["ProductName", "TotalOrders", "TotalRevenue", "AverageUnitPrice"],
  "queryExecutedAt": "2024-01-15T10:30:00.000Z",
  "connectionInfo": {...}
}
```

### 2. MCP Tool Call API

**Endpoint**: `POST /tools/call`

**Request Body**:
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

**Response**:
```json
{
  "result": {
    "success": true,
    "recordset": [...],
    "columns": [...],
    "queryExecutedAt": "2024-01-15T10:30:00.000Z",
    "report_metadata": {
      "from_date": "2024-01-01",
      "to_date": "2024-12-31",
      "product_count": 2,
      "products": ["Product A", "Product B"],
      "procedure_name": "sp_GeneratePerformanceReport"
    }
  }
}
```

## Parameters

### Required Parameters

- **server**: SQL Server hostname or IP address
- **database**: Database name to connect to
- **user**: Username for database authentication
- **password**: Password for database authentication
- **from_date**: Start date for the report (YYYY-MM-DD format)
- **to_date**: End date for the report (YYYY-MM-DD format)
- **product_list**: Array of product names/IDs to include in the report

### Optional Parameters

- **procedure_name**: Name of the stored procedure to call (default: "sp_GeneratePerformanceReport")
- **port**: Port number (default: 1433)
- **encrypt**: Enable encryption for the connection (default: true)
- **trustServerCertificate**: Trust server certificate (default: false)

## Stored Procedure Requirements

The stored procedure should accept the following parameters:

1. **@FromDate**: DATE parameter for the start of the reporting period
2. **@ToDate**: DATE parameter for the end of the reporting period
3. **@ProductList**: Table-valued parameter containing the list of products

### Example Stored Procedure Signature

```sql
CREATE PROCEDURE [dbo].[sp_GeneratePerformanceReport]
    @FromDate DATE,
    @ToDate DATE,
    @ProductList dbo.ProductListType READONLY
AS
BEGIN
    -- Your report generation logic here
END
```

## Usage Examples

### Python Example

```python
import requests

# Configuration
server_url = "http://localhost:3000"
db_config = {
    "server": "localhost",
    "database": "SalesDB",
    "user": "username",
    "password": "password"
}

# Generate performance report
payload = {
    **db_config,
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "product_list": ["Widget A", "Gadget B", "Tool C"]
}

response = requests.post(f"{server_url}/performance-report", json=payload)
result = response.json()

if result["success"]:
    print(f"Report generated successfully!")
    print(f"Records: {len(result['recordset'])}")
    for record in result["recordset"]:
        print(f"Product: {record['ProductName']}, Revenue: {record['TotalRevenue']}")
else:
    print(f"Error: {result['error']}")
```

### cURL Example

```bash
curl -X POST "http://localhost:3000/performance-report" \
  -H "Content-Type: application/json" \
  -d '{
    "server": "localhost",
    "database": "SalesDB",
    "user": "username",
    "password": "password",
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "product_list": ["Product A", "Product B"]
  }'
```

## Error Handling

The tool includes comprehensive error handling for:

- **Missing Parameters**: Validates that all required parameters are provided
- **Date Format Validation**: Ensures dates are in YYYY-MM-DD format
- **Database Connection Issues**: Handles connection failures gracefully
- **SQL Execution Errors**: Reports stored procedure execution errors
- **SQL Injection Prevention**: Properly escapes product names in the generated SQL

## Security Considerations

- Product names are properly escaped to prevent SQL injection
- Database credentials are required for each request (consider implementing token-based authentication for production use)
- SSL/TLS encryption is enabled by default for database connections
- CORS is configured to allow cross-origin requests (review for production environments)

## Testing

Use the provided test script to verify functionality:

```bash
cd test
python performance_report_example.py
```

Make sure to:
1. Update the database configuration in the test script
2. Ensure your database has the required stored procedure
3. Start the HTTP server before running tests

## Troubleshooting

### Common Issues

1. **"Missing required parameters" error**: Ensure all required parameters are included in the request
2. **Date format errors**: Use YYYY-MM-DD format for date parameters
3. **Stored procedure not found**: Verify the procedure exists and the name is correct
4. **Connection failures**: Check database server, credentials, and network connectivity
5. **Permission errors**: Ensure the database user has EXECUTE permissions on the stored procedure

### Logging

The server logs all requests and errors. Check the console output for detailed error information when troubleshooting issues.

## Future Enhancements

Potential improvements for future versions:

- Authentication and authorization mechanisms
- Report caching and scheduling
- Multiple output formats (CSV, Excel, PDF)
- Report templates and customization
- Async report generation for large datasets
- Email delivery of generated reports
