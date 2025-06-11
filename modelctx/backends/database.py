"""Database backend implementation for MCP servers."""

from typing import Dict, List, Any
from modelctx.backends.base import BaseBackend


class DatabaseBackend(BaseBackend):
    """Backend for connecting to SQL databases (PostgreSQL, MySQL, SQLite)."""
    
    @classmethod
    def get_backend_type(cls) -> str:
        return "database"
    
    @classmethod
    def get_description(cls) -> str:
        return "Connect to SQL databases (PostgreSQL, MySQL, SQLite)"
    
    @classmethod
    def get_dependencies(cls) -> List[str]:
        return [
            "sqlalchemy>=2.0.0",
            "psycopg2-binary>=2.9.0",
            "pymysql>=1.0.0",
            "aiosqlite>=0.19.0",
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "execute_query",
                "description": "Execute a SQL query safely with parameter binding",
                "parameters": "query: str, parameters: dict = None",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Executing query: {query[:100]}...")
        
        # Validate query to prevent dangerous operations
        if not _validate_query(query):
            raise ValueError("Query contains potentially dangerous operations")
        
        async with get_db_connection() as conn:
            if parameters:
                result = await conn.execute(text(query), parameters)
            else:
                result = await conn.execute(text(query))
            
            if result.returns_rows:
                rows = await result.fetchall()
                columns = list(result.keys())
                return {
                    "success": True,
                    "columns": columns,
                    "rows": [dict(zip(columns, row)) for row in rows],
                    "row_count": len(rows)
                }
            else:
                await conn.commit()
                return {
                    "success": True,
                    "message": f"Query executed successfully. Rows affected: {result.rowcount}",
                    "rows_affected": result.rowcount
                }
                
    except Exception as e:
        logger.error(f"Database query error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
'''
            },
            {
                "name": "get_table_schema",
                "description": "Get the schema information for a specific table",
                "parameters": "table_name: str",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Getting schema for table: {table_name}")
        
        # Validate table name
        if not _validate_table_name(table_name):
            raise ValueError("Invalid table name")
        
        async with get_db_connection() as conn:
            # Query varies by database type
            db_type = get_database_type()
            
            if db_type == "postgresql":
                query = """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = :table_name
                    ORDER BY ordinal_position
                """
            elif db_type == "mysql":
                query = """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = :table_name
                    ORDER BY ordinal_position
                """
            else:  # SQLite
                query = f"PRAGMA table_info({table_name})"
            
            result = await conn.execute(text(query), {"table_name": table_name})
            columns = await result.fetchall()
            
            if not columns:
                return {
                    "success": False,
                    "error": f"Table '{table_name}' not found"
                }
            
            schema_info = []
            for col in columns:
                if db_type == "sqlite":
                    schema_info.append({
                        "column_name": col[1],
                        "data_type": col[2],
                        "is_nullable": not col[3],
                        "column_default": col[4]
                    })
                else:
                    schema_info.append({
                        "column_name": col[0],
                        "data_type": col[1],
                        "is_nullable": col[2] == "YES",
                        "column_default": col[3]
                    })
            
            return {
                "success": True,
                "table_name": table_name,
                "columns": schema_info
            }
                
    except Exception as e:
        logger.error(f"Schema query error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
'''
            },
            {
                "name": "list_tables",
                "description": "List all tables in the database",
                "parameters": "",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info("Listing all tables")
        
        async with get_db_connection() as conn:
            db_type = get_database_type()
            
            if db_type == "postgresql":
                query = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """
            elif db_type == "mysql":
                query = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE()
                    ORDER BY table_name
                """
            else:  # SQLite
                query = """
                    SELECT name as table_name 
                    FROM sqlite_master 
                    WHERE type='table'
                    ORDER BY name
                """
            
            result = await conn.execute(text(query))
            tables = await result.fetchall()
            
            table_list = [row[0] for row in tables]
            
            return {
                "success": True,
                "tables": table_list,
                "count": len(table_list)
            }
                
    except Exception as e:
        logger.error(f"List tables error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
'''
            },
            {
                "name": "get_table_stats",
                "description": "Get statistics for a specific table (row count, size, etc.)",
                "parameters": "table_name: str",
                "return_type": "dict",
                "implementation": '''
    try:
        logger.info(f"Getting stats for table: {table_name}")
        
        if not _validate_table_name(table_name):
            raise ValueError("Invalid table name")
        
        async with get_db_connection() as conn:
            # Get row count
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            result = await conn.execute(text(count_query))
            row_count = (await result.fetchone())[0]
            
            # Get table size (database-specific)
            db_type = get_database_type()
            size_info = {}
            
            if db_type == "postgresql":
                size_query = """
                    SELECT 
                        pg_size_pretty(pg_total_relation_size(:table_name)) as table_size,
                        pg_size_pretty(pg_relation_size(:table_name)) as data_size
                """
                size_result = await conn.execute(text(size_query), {"table_name": table_name})
                size_row = await size_result.fetchone()
                size_info = {
                    "total_size": size_row[0],
                    "data_size": size_row[1]
                }
            
            return {
                "success": True,
                "table_name": table_name,
                "row_count": row_count,
                "size_info": size_info
            }
                
    except Exception as e:
        logger.error(f"Table stats error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
'''
            }
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_database_tables",
                "uri": "db://tables",
                "description": "List of all database tables",
                "parameters": "",
                "implementation": '''
    try:
        async with get_db_connection() as conn:
            db_type = get_database_type()
            
            if db_type == "postgresql":
                query = """
                    SELECT table_name, table_type
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """
            elif db_type == "mysql":
                query = """
                    SELECT table_name, table_type
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE()
                    ORDER BY table_name
                """
            else:  # SQLite
                query = """
                    SELECT name as table_name, 'BASE TABLE' as table_type
                    FROM sqlite_master 
                    WHERE type='table'
                    ORDER BY name
                """
            
            result = await conn.execute(text(query))
            tables = await result.fetchall()
            
            table_info = []
            for row in tables:
                table_info.append({
                    "name": row[0],
                    "type": row[1]
                })
            
            return json.dumps({
                "database_type": db_type,
                "tables": table_info,
                "count": len(table_info)
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Resource error: {e}")
        return json.dumps({"error": str(e)})
'''
            },
            {
                "name": "get_table_schema_resource",
                "uri": "db://schema/{table_name}",
                "description": "Schema information for a specific table",
                "parameters": "table_name: str",
                "implementation": '''
    try:
        if not _validate_table_name(table_name):
            raise ValueError("Invalid table name")
        
        # Use the get_table_schema tool internally
        schema_result = await get_table_schema(table_name)
        return json.dumps(schema_result, indent=2)
        
    except Exception as e:
        logger.error(f"Schema resource error: {e}")
        return json.dumps({"error": str(e)})
'''
            }
        ]
    
    def get_imports(self) -> List[str]:
        return [
            "import json",
            "from contextlib import asynccontextmanager",
            "from sqlalchemy import create_engine, text, MetaData",
            "from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession",
            "from sqlalchemy.orm import sessionmaker",
            "import re",
            "import os",
        ]
    
    def get_init_code(self) -> str:
        db_url = self.config.parameters.get("database_url", "")
        pool_size = self.config.parameters.get("connection_pool_size", 5)
        pool_timeout = self.config.parameters.get("connection_timeout", 30)
        
        return f'''
# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "{db_url}")
POOL_SIZE = {pool_size}
POOL_TIMEOUT = {pool_timeout}

# Create database engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite async engine
    engine = create_async_engine(
        DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
        echo=False,
        pool_pre_ping=True,
    )
else:
    # PostgreSQL/MySQL async engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=POOL_SIZE,
        max_overflow=20,
        pool_timeout=POOL_TIMEOUT,
        pool_pre_ping=True,
    )

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@asynccontextmanager
async def get_db_connection():
    """Get database connection context manager."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def get_database_type() -> str:
    """Get the type of database being used."""
    if DATABASE_URL.startswith("postgresql"):
        return "postgresql"
    elif DATABASE_URL.startswith("mysql"):
        return "mysql"
    elif DATABASE_URL.startswith("sqlite"):
        return "sqlite"
    else:
        return "unknown"

def _validate_query(query: str) -> bool:
    """Validate SQL query for security."""
    query_lower = query.lower().strip()
    
    # Block dangerous operations
    dangerous_keywords = [
        "drop ", "delete ", "truncate ", "alter ", "create ",
        "insert ", "update ", "--", "/*", "*/", "xp_", "sp_"
    ]
    
    for keyword in dangerous_keywords:
        if keyword in query_lower:
            return False
    
    # Only allow SELECT statements for now
    return query_lower.startswith("select")

def _validate_table_name(table_name: str) -> bool:
    """Validate table name to prevent SQL injection."""
    if not table_name:
        return False
    
    # Only allow alphanumeric characters and underscores
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, table_name))
'''
    
    def get_cleanup_code(self) -> str:
        return '''
        # Close database connections
        await engine.dispose()
'''
    
    def validate_config(self) -> List[str]:
        errors = []
        
        # Check required parameters
        database_url = self.config.parameters.get("database_url")
        if not database_url:
            errors.append("database_url is required")
        else:
            # Basic URL validation
            if not any(database_url.startswith(prefix) for prefix in ["postgresql://", "mysql://", "sqlite:///"]):
                errors.append("database_url must be a valid database URL (postgresql://, mysql://, or sqlite:///)")
        
        # Validate pool size
        pool_size = self.config.parameters.get("connection_pool_size", 5)
        if not isinstance(pool_size, int) or pool_size < 1 or pool_size > 100:
            errors.append("connection_pool_size must be an integer between 1 and 100")
        
        # Validate timeout
        timeout = self.config.parameters.get("connection_timeout", 30)
        if not isinstance(timeout, int) or timeout < 5 or timeout > 300:
            errors.append("connection_timeout must be an integer between 5 and 300 seconds")
        
        return errors
    
    def get_env_variables(self) -> Dict[str, str]:
        return {
            "DATABASE_URL": "Database connection URL (e.g., postgresql://user:pass@host:port/dbname)",
            "DB_POOL_SIZE": "Database connection pool size (optional, default: 5)",
            "DB_TIMEOUT": "Database connection timeout in seconds (optional, default: 30)",
        }
    
    @classmethod
    def get_config_prompts(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": "description",
                "type": "text",
                "message": "Enter a description for your database MCP server:",
                "default": "MCP server with database backend",
            },
            {
                "name": "database_type",
                "type": "choice",
                "message": "Select database type:",
                "choices": ["postgresql", "mysql", "sqlite"],
                "default": "postgresql",
                "required": True,
            },
            {
                "name": "database_url",
                "type": "text",
                "message": "Enter database connection URL:",
                "default": "postgresql://user:password@localhost:5432/database",
                "required": True,
                "validator": "url",
            },
            {
                "name": "connection_pool_size",
                "type": "int",
                "message": "Enter connection pool size:",
                "default": 5,
            },
            {
                "name": "connection_timeout",
                "type": "int",
                "message": "Enter connection timeout (seconds):",
                "default": 30,
            },
            {
                "name": "read_only",
                "type": "bool",
                "message": "Enable read-only mode (only SELECT queries)?",
                "default": True,
            },
        ]