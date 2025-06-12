"""MCP Quick Setup Tool - A comprehensive CLI tool for creating MCP servers."""

__version__ = "0.1.2"
__author__ = "MCP Setup Tool Contributors"
__description__ = "A comprehensive CLI tool for creating and configuring Model Context Protocol (MCP) servers"

from modelctx.core.generator import ProjectGenerator
from modelctx.core.config import ProjectConfig

__all__ = ["ProjectGenerator", "ProjectConfig", "__version__"]