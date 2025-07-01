#!/usr/bin/env python3
"""
HTTP-based MCP Ask DBA Server - Python Implementation
Provides both MCP Server-Sent Events endpoint and direct REST API
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import signal
import os

import pyodbc
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent
import mcp.types as types

# Import our connection manager from the main server
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ask-dba-http-server")

# Pydantic models for API
class QueryRequest(BaseModel):
    server: str = Field(..., description="SQL Server hostname or IP address")
    database: str = Field(..., description="Database name to connect to")
    user: str = Field(..., description="Username for database authentication")
    password: str = Field(..., description="Password for database authentication")
    query: str = Field(..., description="SQL query to execute")
    port: int = Field(1433, description="Port number")
    encrypt: bool = Field(True, description="Enable encryption for the connection")
    trustServerCertificate: bool = Field(False, description="Trust server certificate")

class PerformanceReportRequest(BaseModel):
    server: str = Field(..., description="SQL Server hostname or IP address")
    database: str = Field(..., description="Database name to connect to")
    user: str = Field(..., description="Username for database authentication")
    password: str = Field(..., description="Password for database authentication")
    from_date: str = Field(..., description="Start date for the report (YYYY-MM-DD format)")
    to_date: str = Field(..., description="End date for the report (YYYY-MM-DD format)")
    product_list: List[str] = Field(..., description="List of product names/IDs to include in the report")
    procedure_name: str = Field("sp_GeneratePerformanceReport", description="Name of the stored procedure to call")
    port: int = Field(1433, description="Port number")
    encrypt: bool = Field(True, description="Enable encryption for the connection")
    trustServerCertificate: bool = Field(False, description="Trust server certificate")

class QueryResponse(BaseModel):
    success: bool
    rowsAffected: Optional[int] = None
    recordset: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    error: Optional[str] = None
    queryExecutedAt: str
    connectionInfo: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    server_info: Dict[str, Any]

class AskDBAHTTPServer:
    """HTTP-based MCP server with REST API endpoints"""
    
    def __init__(self, host: str = "localhost", port: int = 3000):
        self.host = host
        self.port = port
        self.app = FastAPI(
            title="MCP Ask DBA Server",
            description="MCP server with Ask DBA tool for Microsoft SQL Server database queries",
            version="0.1.0"
        )
        self.connection_manager = ConnectionManager()
        self.mcp_server = Server("ask-dba-http-server")
        
        self._setup_middleware()
        self._setup_routes()
        self._setup_mcp_handlers()
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint with server information"""
            return {
                "name": "MCP Ask DBA Server",
                "version": "0.1.0",
                "description": "HTTP-based MCP server for SQL Server database queries",
                "endpoints": {
                    "health": "/health",
                    "query": "/query",
                    "performance-report": "/performance-report",
                    "mcp": "/mcp"
                }
            }
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            return HealthResponse(
                status="healthy",
                timestamp=datetime.now().isoformat(),
                server_info={
                    "host": self.host,
                    "port": self.port,
                    "active_connections": len(self.connection_manager.connections),
                    "available_drivers": [d for d in pyodbc.drivers() if "SQL Server" in d]
                }
            )
        
        @self.app.post("/query", response_model=QueryResponse)
        async def execute_query(request: QueryRequest):
            """Direct query execution endpoint"""
            try:
                config = DatabaseConfig(
                    server=request.server,
                    database=request.database,
                    user=request.user,
                    password=request.password,
                    port=request.port,
                    encrypt=request.encrypt,
                    trust_cert=request.trustServerCertificate
                )
                
                result = await self.connection_manager.execute_query(config, request.query)
                
                return QueryResponse(
                    success=result["success"],
                    rowsAffected=result.get("rowsAffected"),
                    recordset=result.get("recordset"),
                    columns=result.get("columns"),
                    queryExecutedAt=result["queryExecutedAt"],
                    connectionInfo=result.get("connectionInfo")
                )
                
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                return QueryResponse(
                    success=False,
                    error=str(e),
                    queryExecutedAt=datetime.now().isoformat()
                )
        
        @self.app.post("/performance-report", response_model=QueryResponse)
        async def generate_performance_report(request: PerformanceReportRequest):
            """Generate performance report using stored procedure"""
            try:
                config = DatabaseConfig(
                    server=request.server,
                    database=request.database,
                    user=request.user,
                    password=request.password,
                    port=request.port,
                    encrypt=request.encrypt,
                    trust_cert=request.trustServerCertificate
                )
                
                # Build the stored procedure call
                product_list_str = "'" + "','".join(request.product_list) + "'"
                sp_call = f"""
                DECLARE @ProductList TABLE (ProductName NVARCHAR(255))
                INSERT INTO @ProductList VALUES {', '.join([f"('{product}')" for product in request.product_list])}
                
                EXEC {request.procedure_name} 
                    @FromDate = '{request.from_date}',
                    @ToDate = '{request.to_date}',
                    @ProductList = @ProductList
                """
                
                product_names = ",".join(request.product_list)
                sp_call = f"""
                EXEC {request.procedure_name}
                    @FromDate = '{request.from_date}',
                    @ToDate = '{request.to_date}',
                    @ProductNames = '{product_names}'
                """
                
                result = await self.connection_manager.execute_query(config, sp_call)
                
                return QueryResponse(
                    success=result["success"],
                    rowsAffected=result.get("rowsAffected"),
                    recordset=result.get("recordset"),
                    columns=result.get("columns"),
                    queryExecutedAt=result["queryExecutedAt"],
                    connectionInfo=result.get("connectionInfo")
                )
                
            except Exception as e:
                logger.error(f"Performance report generation failed: {e}")
                return QueryResponse(
                    success=False,
                    error=str(e),
                    queryExecutedAt=datetime.now().isoformat()
                )
        
        @self.app.get("/mcp")
        async def mcp_endpoint(request: Request):
            """MCP Server-Sent Events endpoint"""
            return StreamingResponse(
                self._mcp_stream_generator(request),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control",
                }
            )
        
        @self.app.get("/tools")
        async def list_tools():
            """List available MCP tools"""
            tools = await self._get_mcp_tools()
            return {"tools": [tool.dict() if hasattr(tool, 'dict') else tool for tool in tools]}
        
        @self.app.post("/tools/call")
        async def call_tool(request: Dict[str, Any]):
            """Call an MCP tool directly"""
            try:
                tool_name = request.get("name")
                arguments = request.get("arguments", {})
                
                if tool_name == "ask_dba":
                    result = await self._execute_ask_dba_tool(arguments)
                elif tool_name == "generate_performance_report":
                    result = await self._execute_performance_report_tool(arguments)
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
                
                return {"result": result}
                
            except Exception as e:
                logger.error(f"Tool call failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _setup_mcp_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.mcp_server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return await self._get_mcp_tools()
        
        @self.mcp_server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
            """Handle tool calls"""
            if name == "ask_dba":
                result = await self._execute_ask_dba_tool(arguments)
            elif name == "generate_performance_report":
                result = await self._execute_performance_report_tool(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )
            ]
    
    async def _get_mcp_tools(self) -> List[Tool]:
        """Get list of available MCP tools"""
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
    
    async def _execute_ask_dba_tool(self, arguments: dict) -> dict:
        """Execute the ask_dba tool"""
        # Validate required parameters
        required_params = ["server", "database", "user", "password", "query"]
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
            
            result = await self.connection_manager.execute_query(config, arguments["query"])
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "queryExecutedAt": datetime.now().isoformat()
            }
    
    async def _execute_performance_report_tool(self, arguments: dict) -> dict:
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
            DECLARE @ProductList TABLE (ProductName NVARCHAR(255))
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
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "queryExecutedAt": datetime.now().isoformat()
            }
    
    async def _mcp_stream_generator(self, request: Request):
        """Generate MCP Server-Sent Events stream"""
        try:
            # This is a simplified SSE implementation
            # In a full implementation, you'd handle the MCP protocol properly
            yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"
            
            # Keep connection alive
            while True:
                if await request.is_disconnected():
                    break
                
                # Send heartbeat
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"SSE stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    async def run(self):
        """Run the HTTP server"""
        logger.info(f"Starting Ask DBA HTTP server on {self.host}:{self.port}")
        logger.info(f"Endpoints:")
        logger.info(f"  - Health check: http://{self.host}:{self.port}/health")
        logger.info(f"  - Direct query: http://{self.host}:{self.port}/query")
        logger.info(f"  - Performance report: http://{self.host}:{self.port}/performance-report")
        logger.info(f"  - MCP endpoint: http://{self.host}:{self.port}/mcp")
        logger.info(f"  - API docs: http://{self.host}:{self.port}/docs")
        
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            asyncio.create_task(self.cleanup())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            await server.serve()
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up connections...")
        await self.connection_manager.close_all()
        logger.info("Cleanup completed")

async def main():
    """Main entry point"""
    # Parse command line arguments
    host = os.getenv("ASK_DBA_HOST", "localhost")
    port = int(os.getenv("ASK_DBA_PORT", "3000"))
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--host" and len(sys.argv) > 2:
            host = sys.argv[2]
        elif sys.argv[1] == "--port" and len(sys.argv) > 2:
            port = int(sys.argv[2])
    
    server = AskDBAHTTPServer(host=host, port=port)
    
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Server startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())