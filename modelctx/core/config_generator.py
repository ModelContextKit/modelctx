"""Configuration file generation for MCP servers."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any

from modelctx.backends.base import BaseBackend


class ConfigGenerator:
    """Generates configuration files for MCP projects."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def generate_config_files(self, backend_instance: BaseBackend) -> None:
        """Generate all configuration files."""
        # Generate main config.yaml
        config_content = backend_instance.generate_config_file()
        with open(self.project_path / "config" / "config.yaml", 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # Generate .env template
        env_content = backend_instance.generate_env_template()
        with open(self.project_path / ".env.template", 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        # Generate logging configuration
        self._generate_logging_config()
    
    def _generate_logging_config(self) -> None:
        """Generate logging configuration file."""
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "level": "INFO",
                    "formatter": "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "level": "DEBUG",
                    "formatter": "standard",
                    "class": "logging.FileHandler",
                    "filename": "mcp_server.log",
                    "mode": "a"
                }
            },
            "loggers": {
                "": {
                    "handlers": ["default", "file"],
                    "level": "INFO",
                    "propagate": False
                }
            }
        }
        
        with open(self.project_path / "config" / "logging.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(logging_config, f, default_flow_style=False, indent=2)
    
    def generate_claude_desktop_config(self, backend_instance: BaseBackend) -> None:
        """Generate Claude Desktop configuration."""
        claude_config = backend_instance.generate_claude_desktop_config()
        
        with open(self.project_path / "config" / "claude_desktop_config.json", 'w', encoding='utf-8') as f:
            json.dump(claude_config, f, indent=2)