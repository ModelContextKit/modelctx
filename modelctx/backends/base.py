"""Base backend class for MCP server generators."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
from dataclasses import dataclass, field


@dataclass
class BackendConfig:
    """Configuration for a backend."""
    backend_type: str
    project_name: str
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "backend_type": self.backend_type,
            "project_name": self.project_name,
            "description": self.description,
            "parameters": self.parameters,
            "dependencies": self.dependencies,
            "optional_dependencies": self.optional_dependencies,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BackendConfig":
        """Create config from dictionary."""
        return cls(**data)


class BaseBackend(ABC):
    """Base class for all MCP backend implementations."""
    
    def __init__(self, config: BackendConfig):
        self.config = config
        self.template_vars: Dict[str, Any] = {}
        self._setup_template_vars()
    
    def _setup_template_vars(self) -> None:
        """Setup template variables for code generation."""
        self.template_vars = {
            "project_name": self.config.project_name,
            "backend_type": self.config.backend_type,
            "description": self.config.description,
            "parameters": self.config.parameters,
            "dependencies": self.config.dependencies,
            "optional_dependencies": self.config.optional_dependencies,
            "tools": self.get_tools(),
            "resources": self.get_resources(),
            "imports": self.get_imports(),
            "init_code": self.get_init_code(),
            "cleanup_code": self.get_cleanup_code(),
        }
    
    @classmethod
    @abstractmethod
    def get_backend_type(cls) -> str:
        """Return the backend type identifier."""
        pass
    
    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """Return a description of this backend."""
        pass
    
    @classmethod
    @abstractmethod
    def get_dependencies(cls) -> List[str]:
        """Return list of required dependencies."""
        pass
    
    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        """Return list of optional dependencies."""
        return []
    
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of MCP tools this backend provides."""
        pass
    
    @abstractmethod
    def get_resources(self) -> List[Dict[str, Any]]:
        """Return list of MCP resources this backend provides."""
        pass
    
    @abstractmethod
    def get_imports(self) -> List[str]:
        """Return list of import statements needed."""
        pass
    
    @abstractmethod
    def get_init_code(self) -> str:
        """Return initialization code for the backend."""
        pass
    
    def get_cleanup_code(self) -> str:
        """Return cleanup code for the backend (optional)."""
        return ""
    
    @abstractmethod
    def validate_config(self) -> List[str]:
        """Validate backend configuration. Return list of errors."""
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Return JSON schema for configuration validation."""
        return {
            "type": "object",
            "properties": {
                "backend_type": {"type": "string"},
                "project_name": {"type": "string"},
                "description": {"type": "string"},
                "parameters": {"type": "object"},
            },
            "required": ["backend_type", "project_name"]
        }
    
    def get_template_variables(self) -> Dict[str, Any]:
        """Get all template variables for code generation."""
        return self.template_vars.copy()
    
    def get_env_variables(self) -> Dict[str, str]:
        """Return environment variables needed by this backend."""
        return {}
    
    def get_config_prompts(self) -> List[Dict[str, Any]]:
        """Return list of configuration prompts for interactive setup."""
        return [
            {
                "name": "description",
                "type": "text",
                "message": f"Enter a description for your {self.get_backend_type()} MCP server:",
                "default": f"MCP server with {self.get_backend_type()} backend",
            }
        ]
    
    def generate_server_code(self) -> str:
        """Generate the main server.py code."""
        tools_code = self._generate_tools_code()
        resources_code = self._generate_resources_code()
        
        return f'''"""
{self.config.description}

This MCP server provides {self.get_backend_type()} integration capabilities.
Generated by MCP Quick Setup Tool.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.session import ServerSession
from mcp.server.stdio import stdio_server
{chr(10).join(self.get_imports())}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("{self.config.project_name}")

{self.get_init_code()}

{tools_code}

{resources_code}

async def main():
    """Main server entry point."""
    logger.info("Starting {self.config.project_name} MCP server...")
    
    try:
        # Start the server
        await stdio_server(mcp.app)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {{e}}")
    finally:
        {self.get_cleanup_code() or "pass"}

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    def _generate_tools_code(self) -> str:
        """Generate code for MCP tools."""
        tools = self.get_tools()
        if not tools:
            return "# No tools defined for this backend"
        
        code_lines = []
        for tool in tools:
            code_lines.append(f'''
@mcp.tool()
async def {tool["name"]}({tool.get("parameters", "")}) -> {tool.get("return_type", "str")}:
    """{tool["description"]}"""
    {tool["implementation"]}
''')
        
        return "\n".join(code_lines)
    
    def _generate_resources_code(self) -> str:
        """Generate code for MCP resources."""
        resources = self.get_resources()
        if not resources:
            return "# No resources defined for this backend"
        
        code_lines = []
        for resource in resources:
            code_lines.append(f'''
@mcp.resource("{resource["uri"]}")
async def {resource["name"]}({resource.get("parameters", "")}) -> str:
    """{resource["description"]}"""
    {resource["implementation"]}
''')
        
        return "\n".join(code_lines)
    
    def generate_config_file(self) -> str:
        """Generate YAML configuration file."""
        config_data = {
            "server": {
                "name": self.config.project_name,
                "description": self.config.description,
                "version": "1.0.0",
            },
            "backend": {
                "type": self.config.backend_type,
                **self.config.parameters,
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "security": {
                "validate_inputs": True,
                "log_requests": True,
                "timeout": 30,
            }
        }
        
        return yaml.dump(config_data, default_flow_style=False, indent=2)
    
    def generate_env_template(self) -> str:
        """Generate .env.template file."""
        env_vars = self.get_env_variables()
        lines = [
            "# Environment variables for MCP server",
            f"# Generated for {self.config.project_name}",
            "",
        ]
        
        for key, description in env_vars.items():
            lines.append(f"# {description}")
            lines.append(f"{key}=")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_requirements(self) -> str:
        """Generate requirements.txt content."""
        deps = ["mcp>=1.0.0"] + self.config.dependencies
        return "\n".join(sorted(deps))
    
    def generate_claude_desktop_config(self) -> Dict[str, Any]:
        """Generate Claude Desktop configuration."""
        env_vars = self.get_env_variables()
        
        return {
            "mcpServers": {
                self.config.project_name: {
                    "command": "python",
                    "args": ["server.py"],
                    "env": {key: f"${key}" for key in env_vars.keys()},
                }
            }
        }