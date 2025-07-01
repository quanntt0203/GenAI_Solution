#!/usr/bin/env python3
"""
MCP Ask DBA Server - Python Implementation
A Model Context Protocol server for executing SQL queries on Microsoft SQL Server databases.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime
import signal
import os

import pyodbc
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl
import mcp.types as types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("ask-dba-server")

class DatabaseConfig:
    """Database configuration class"""
    def __init__(self, server: str, database: str, user: str, password: str, 
                 port: int = 1433, encrypt: bool = True, trust_cert: bool = False):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.encrypt = encrypt
        self.trust_cert = trust_cert

class ConnectionManager:
    """Manages database connections and connection pooling"""
    
    def __init__(self):
        self.connections: Dict[str, pyodbc.Connection] = {}
        self.connection_strings: Dict[str, str] = {}
    
    def _build_connection_string(self, config: DatabaseConfig) -> str:
        """Build ODBC connection string"""
        # Try to find the best available SQL Server driver
        drivers = [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server", 
            "ODBC Driver 13 for SQL Server",
            "SQL Server Native Client 11.0",
            "SQL Server"
        ]
        
        available_drivers = [d for d in pyodbc.drivers() if any(driver in d for driver in drivers)]
        if not available_drivers:
            raise Exception("No suitable SQL Server ODBC driver found. Please install ODBC Driver for SQL Server.")
        
        driver = available_drivers[0]
        
        connection_parts = [
            f"DRIVER={{{driver}}}",
            f"SERVER={config.server},{config.port}",
            f"DATABASE={config.database}",
            f"UID={config.user}",
            f"PWD={config.password}"
        ]
        
        if config.encrypt:
            connection_parts.append("Encrypt=yes")
        else:
            connection_parts.append("Encrypt=no")
            
        if config.trust_cert:
            connection_parts.append("TrustServerCertificate=yes")
        else:
            connection_parts.append("TrustServerCertificate=no")
            
        return ";".join(connection_parts)
    
    def get_connection_key(self, config: DatabaseConfig) -> str:
        """Generate a unique key for the connection"""
        return f"{config.server}_{config.database}_{config.user}_{config.port}"
    
    async def get_connection(self, config: DatabaseConfig) -> pyodbc.Connection:
        """Get or create a database connection"""
        connection_key = self.get_connection_key(config)
        
        if connection_key in self.connections:
            try:
                # Test the connection
                conn = self.connections[connection_key]
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return conn
            except Exception as e:
                logger.warning(f"Connection test failed for {connection_key}: {e}")
                # Remove the failed connection
                if connection_key in self.connections:
                    try:
                        self.connections[connection_key].close()
                    except:
                        pass
                    del self.connections[connection_key]
        
        # Create new connection
        try:
            connection_string = self._build_connection_string(config)
            self.connection_strings[connection_key] = connection_string
            
            # Run connection in thread pool since pyodbc is synchronous
            loop = asyncio.get_event_loop()
            conn = await loop.run_in_executor(None, pyodbc.connect, connection_string)
            
            self.connections[connection_key] = conn
            logger.info(f"Created new connection: {connection_key}")
            return conn
            
        except Exception as e:
            logger.error(f"Failed to create connection {connection_key}: {e}")
            raise
    
    async def execute_query(self, config: DatabaseConfig, query: str) -> Dict[str, Any]:
        """Execute a SQL query and return results"""
        connection = await self.get_connection(config)
        
        try:
            loop = asyncio.get_event_loop()
            
            def _execute():
                cursor = connection.cursor()
                cursor.execute(query)
                
                # Get column information
                columns = [column[0] for column in cursor.description] if cursor.description else []
                
                # Fetch results
                rows = cursor.fetchall()
                
                # Convert rows to list of dictionaries
                recordset = []
                for row in rows:
                    record = {}
                    for i, value in enumerate(row):
                        column_name = columns[i] if i < len(columns) else f"column_{i}"
                        # Handle datetime objects
                        if hasattr(value, 'isoformat'):
                            record[column_name] = value.isoformat()
                        else:
                            record[column_name] = value
                    recordset.append(record)
                
                rows_affected = cursor.rowcount
                cursor.close()
                
                return {
                    "success": True,
                    "rowsAffected": rows_affected,
                    "recordset": recordset,
                    "columns": columns,
                    "queryExecutedAt": datetime.now().isoformat(),
                    "connectionInfo": {
                        "server": config.server,
                        "database": config.database,
                        "user": config.user,
                        "port": config.port
                    }
                }
            
            result = await loop.run_in_executor(None, _execute)
            return result
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            # Remove the failed connection
            connection_key = self.get_connection_key(config)
            if connection_key in self.connections:
                try:
                    self.connections[connection_key].close()
                except:
                    pass
                del self.connections[connection_key]
            raise
    
    async def close_all(self):
        """Close all connections"""
        for key, conn in self.connections.items():
            try:
                conn.close()
                logger.info(f"Closed connection: {key}")
            except Exception as e:
                logger.error(f"Error closing connection {key}: {e}")
        self.connections.clear()
        self.connection_strings.clear()

class AskDBAServer:
    """Main MCP server class"""
    
    def __init__(self):
        self.server = Server("ask-dba-server")
        self.connection_manager = ConnectionManager()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP request handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="ask_dba",
                    description="Execute SQL queries on Microsoft SQL Server databases. Supports connection management and query execution.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server": {
                                "type": "string",
                                "description": "SQL Server hostname or IP address"
                            },
                            "database": {
                                "type": "string", 
                                "description": "Database name to connect to"
                            },
                            "user": {
                                "type": "string",
                                "description": "Username for database authentication"
                            },
                            "password": {
                                "type": "string",
                                "description": "Password for database authentication"
                            },
                            "port": {
                                "type": "integer",
                                "description": "Port number (default: 1433)",
                                "default": 1433
                            },
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute"
                            },
                            "encrypt": {
                                "type": "boolean", 
                                "description": "Enable encryption for the connection (default: true)",
                                "default": True
                            },
                            "trustServerCertificate": {
                                "type": "boolean",
                                "description": "Trust server certificate (default: false)", 
                                "default": False
                            }
                        },
                        "required": ["server", "database", "user", "password", "query"]
                    }
                ),
                Tool(
                    name="generate_performance_report",
                    description="Generate performance reports by calling stored procedures with date range and product filters.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server": {
                                "type": "string",
                                "description": "SQL Server hostname or IP address"
                            },
                            "database": {
                                "type": "string",
                                "description": "Database name to connect to"
                            },
                            "user": {
                                "type": "string",
                                "description": "Username for database authentication"
                            },
                            "password": {
                                "type": "string",
                                "description": "Password for database authentication"
                            },
                            "from_date": {
                                "type": "string",
                                "description": "Start date for the report in YYYY-MM-DD format"
                            },
                            "to_date": {
                                "type": "string",
                                "description": "End date for the report in YYYY-MM-DD format"
                            },
                            "product_list": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of product names/IDs to include in the report"
                            },
                            "procedure_name": {
                                "type": "string",
                                "description": "Name of the stored procedure to call (default: sp_GeneratePerformanceReport)",
                                "default": "sp_GeneratePerformanceReport"
                            },
                            "port": {
                                "type": "integer",
                                "description": "Port number (default: 1433)",
                                "default": 1433
                            },
                            "encrypt": {
                                "type": "boolean",
                                "description": "Enable encryption for the connection (default: true)",
                                "default": True
                            },
                            "trustServerCertificate": {
                                "type": "boolean",
                                "description": "Trust server certificate (default: false)",
                                "default": False
                            }
                        },
                        "required": ["server", "database", "user", "password", "from_date", "to_date", "product_list"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls"""
            if name == "ask_dba":
                return await self._execute_ask_dba_tool(arguments)
            elif name == "generate_performance_report":
                return await self._execute_performance_report_tool(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _execute_ask_dba_tool(self, arguments: dict) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Execute the ask_dba tool"""
        # Validate required parameters
        required_params = ["server", "database", "user", "password", "query"]
        missing_params = [param for param in required_params if param not in arguments]
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
        
        try:
            # Create database configuration
            config = DatabaseConfig(
                server=arguments["server"],
                database=arguments["database"], 
                user=arguments["user"],
                password=arguments["password"],
                port=arguments.get("port", 1433),
                encrypt=arguments.get("encrypt", True),
                trust_cert=arguments.get("trustServerCertificate", False)
            )
            
            # Execute query
            result = await self.connection_manager.execute_query(config, arguments["query"])
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )
            ]
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "queryExecutedAt": datetime.now().isoformat()
            }
            return [
                types.TextContent(
                    type="text", 
                    text=json.dumps(error_result, indent=2)
                )
            ]
    
    async def _execute_performance_report_tool(self, arguments: dict) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Execute the performance report tool"""
        # Validate required parameters
        required_params = ["server", "database", "user", "password", "from_date", "to_date", "product_list"]
        missing_params = [param for param in required_params if param not in arguments]
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
        
        try:
            config = DatabaseConfig(
                server=arguments["server"],
                database=arguments["database"],
                user=arguments["user"],
                password=arguments["password"],
                port=arguments.get("port", 1433),
                encrypt=arguments.get("encrypt", True),
                trust_cert=arguments.get("trustServerCertificate", False)
            )
            
            # Get parameters
            from_date = arguments["from_date"]
            to_date = arguments["to_date"]
            product_list = arguments["product_list"]
            procedure_name = arguments.get("procedure_name", "sp_GeneratePerformanceReport")
            
            # Validate date format (basic validation)
            try:
                datetime.strptime(from_date, "%Y-%m-%d")
                datetime.strptime(to_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date parameters must be in YYYY-MM-DD format")
            
            # Build the stored procedure call with table-valued parameter
            # This approach uses a table variable to pass the product list
            product_inserts = ", ".join([f"('{product.replace(chr(39), chr(39)+chr(39))}')" for product in product_list])
            
            sp_call = f"""
            DECLARE @ProductList dbo.ProductListType;
            INSERT INTO @ProductList VALUES {product_inserts}
            
            EXEC {procedure_name} 
                @FromDate = '{from_date}',
                @ToDate = '{to_date}',
                @ProductList = @ProductList
            """
            product_names = ",".join(product_list)
            sp_call = f"""
            EXEC {procedure_name}
                @FromDate = '{from_date}',
                @ToDate = '{to_date}',
                @ProductNames = '{product_names}'
            """
            
            result = await self.connection_manager.execute_query(config, sp_call)
            
            # Add metadata about the report
            if result.get("success"):
                result["report_metadata"] = {
                    "from_date": from_date,
                    "to_date": to_date,
                    "product_count": len(product_list),
                    "products": product_list,
                    "procedure_name": procedure_name
                }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )
            ]
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "queryExecutedAt": datetime.now().isoformat()
            }
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(error_result, indent=2)
                )
            ]
    
    async def run(self):
        """Run the MCP server"""
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            asyncio.create_task(self.cleanup())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Ask DBA MCP server starting...")
        

        logger.info("Ask DBA MCP server running on stdio")
        try:
            await self.server.run(
                sys.stdin.buffer,
                sys.stdout.buffer,
                InitializationOptions(
                    server_name="ask-dba-server",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
        except Exception as e:
            logger.error(f"Unhandled server error: {e}", exc_info=True)
            await self.cleanup()
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up connections...")
        await self.connection_manager.close_all()
        logger.info("Cleanup completed")

async def main():
    """Main entry point"""
    server = AskDBAServer()
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())