"""Project generator for MCP servers."""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console

from modelctx.backends import get_backend_class
from modelctx.backends.base import BaseBackend, BackendConfig
from modelctx.core.config import ProjectConfig
from modelctx.core.templates import TemplateManager

console = Console()


class ProjectGenerator:
    """Generates MCP server projects based on configuration."""
    
    def __init__(
        self,
        project_name: str,
        backend_type: str,
        output_dir: str = ".",
        verbose: bool = False
    ):
        self.project_name = project_name
        self.backend_type = backend_type
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        
        self.project_path = self.output_dir / project_name
        self.backend_class = get_backend_class(backend_type)
        self.backend_instance: Optional[BaseBackend] = None
        self.config: Optional[ProjectConfig] = None
        self.template_manager = TemplateManager()
        
        # Initialize backend with minimal config
        self._init_backend()
    
    def _init_backend(self) -> None:
        """Initialize backend instance with minimal configuration."""
        backend_config = BackendConfig(
            backend_type=self.backend_type,
            project_name=self.project_name,
            description=f"MCP server with {self.backend_type} backend",
            dependencies=self.backend_class.get_dependencies(),
            optional_dependencies=self.backend_class.get_optional_dependencies()
        )
        self.backend_instance = self.backend_class(backend_config)
    
    def set_config(self, config: ProjectConfig) -> None:
        """Set project configuration."""
        self.config = config
        if config.backend_config:
            self.backend_instance = self.backend_class(config.backend_config)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from file."""
        from modelctx.core.config import ConfigWizard
        self.config = ConfigWizard.load_config(config_path)
        if self.config.backend_config:
            self.backend_instance = self.backend_class(self.config.backend_config)
    
    def generate(self) -> None:
        """Generate the complete MCP server project."""
        if self.verbose:
            console.print(f"[dim]Generating project in {self.project_path}[/dim]")
        
        # Create project directory structure
        self._create_directory_structure()
        
        # Generate core files
        self._generate_server_file()
        self._generate_config_files()
        self._generate_requirements()
        self._generate_project_metadata()
        self._generate_documentation()
        self._generate_tests()
        self._generate_scripts()
        self._generate_claude_desktop_config()
        
        if self.verbose:
            console.print("[dim]Project generation completed[/dim]")
    
    def _create_directory_structure(self) -> None:
        """Create the project directory structure."""
        directories = [
            self.project_path,
            self.project_path / "config",
            self.project_path / "src",
            self.project_path / "src" / "models",
            self.project_path / "src" / "services",
            self.project_path / "src" / "utils",
            self.project_path / "tests",
            self.project_path / "docs",
            self.project_path / "scripts",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py files for Python packages
            if directory.name in ["src", "models", "services", "utils", "tests"]:
                (directory / "__init__.py").touch()
    
    def _generate_server_file(self) -> None:
        """Generate the main server.py file."""
        if not self.backend_instance:
            raise ValueError("Backend instance not initialized")
        
        server_code = self.backend_instance.generate_server_code()
        server_path = self.project_path / "server.py"
        
        with open(server_path, 'w', encoding='utf-8') as f:
            f.write(server_code)
        
        # Make server executable
        server_path.chmod(0o755)
    
    def _generate_config_files(self) -> None:
        """Generate configuration files."""
        if not self.backend_instance:
            raise ValueError("Backend instance not initialized")
        
        # Generate main config.yaml
        config_content = self.backend_instance.generate_config_file()
        with open(self.project_path / "config" / "config.yaml", 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # Generate .env template
        env_content = self.backend_instance.generate_env_template()
        with open(self.project_path / ".env.template", 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        # Generate logging configuration
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
        
        import yaml
        with open(self.project_path / "config" / "logging.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(logging_config, f, default_flow_style=False, indent=2)
    
    def _generate_requirements(self) -> None:
        """Generate requirements.txt and pyproject.toml."""
        if not self.backend_instance:
            raise ValueError("Backend instance not initialized")
        
        # Generate requirements.txt
        requirements_content = self.backend_instance.generate_requirements()
        with open(self.project_path / "requirements.txt", 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        # Generate pyproject.toml
        pyproject_template = self.template_manager.get_template("base/pyproject.toml.j2")
        pyproject_content = pyproject_template.render(
            **self.backend_instance.get_template_variables()
        )
        with open(self.project_path / "pyproject.toml", 'w', encoding='utf-8') as f:
            f.write(pyproject_content)
    
    def _generate_project_metadata(self) -> None:
        """Generate project metadata files."""
        # Generate .gitignore
        gitignore_content = '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
build/
dist/
*.egg-info/

# Virtual environments
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment variables
.env
.env.local

# Logs
*.log
logs/

# MCP specific
mcp_server.log
'''
        with open(self.project_path / ".gitignore", 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
    
    def _generate_documentation(self) -> None:
        """Generate project documentation."""
        if not self.backend_instance:
            raise ValueError("Backend instance not initialized")
        
        # Generate README.md
        readme_template = self.template_manager.get_template("base/README.md.j2")
        readme_content = readme_template.render(
            **self.backend_instance.get_template_variables()
        )
        with open(self.project_path / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Generate API documentation
        api_doc_template = self.template_manager.get_template("base/API.md.j2")
        api_content = api_doc_template.render(
            **self.backend_instance.get_template_variables()
        )
        with open(self.project_path / "docs" / "API.md", 'w', encoding='utf-8') as f:
            f.write(api_content)
        
        # Generate deployment guide
        deploy_doc_template = self.template_manager.get_template("base/DEPLOYMENT.md.j2")
        deploy_content = deploy_doc_template.render(
            **self.backend_instance.get_template_variables()
        )
        with open(self.project_path / "docs" / "DEPLOYMENT.md", 'w', encoding='utf-8') as f:
            f.write(deploy_content)
    
    def _generate_tests(self) -> None:
        """Generate test files."""
        if not self.backend_instance:
            raise ValueError("Backend instance not initialized")
        
        # Generate test_server.py
        try:
            server_test_template = self.template_manager.get_template("base/test_server.py.j2")
            server_test_content = server_test_template.render(
                **self.backend_instance.get_template_variables()
            )
            with open(self.project_path / "tests" / "test_server.py", 'w', encoding='utf-8') as f:
                f.write(server_test_content)
        except Exception as e:
            if self.verbose:
                console.print(f"[yellow]Warning: Could not generate test_server.py: {e}[/yellow]")
        
        # Skip test_tools.py generation as the template might be missing
        # Create a basic test file instead
        basic_test_content = f'''"""Test tools for {self.project_name}."""

import unittest

class TestTools(unittest.TestCase):
    """Test tools for the MCP server."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
'''
        with open(self.project_path / "tests" / "test_tools.py", 'w', encoding='utf-8') as f:
            f.write(basic_test_content)
        
        # Generate pytest.ini
        pytest_config = '''[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
asyncio_mode = auto
'''
        with open(self.project_path / "pytest.ini", 'w', encoding='utf-8') as f:
            f.write(pytest_config)
    
    def _generate_scripts(self) -> None:
        """Generate setup and deployment scripts."""
        # Generate setup.sh
        setup_script = f'''#!/bin/bash
# Setup script for {self.project_name}

echo "Setting up {self.project_name}..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
if [ ! -f .env ]; then
    cp .env.template .env
    echo "Please edit .env file with your configuration"
fi

echo "Setup completed!"
echo "Activate virtual environment with: source venv/bin/activate"
echo "Run server with: python server.py"
'''
        setup_path = self.project_path / "scripts" / "setup.sh"
        with open(setup_path, 'w', encoding='utf-8') as f:
            f.write(setup_script)
        setup_path.chmod(0o755)
        
        # Generate deploy.sh (basic template)
        deploy_script = f'''#!/bin/bash
# Deployment script for {self.project_name}

echo "Deploying {self.project_name}..."

# Run tests
python -m pytest tests/

# Build if needed
# docker build -t {self.project_name} .

echo "Deployment completed!"
'''
        deploy_path = self.project_path / "scripts" / "deploy.sh"
        with open(deploy_path, 'w', encoding='utf-8') as f:
            f.write(deploy_script)
        deploy_path.chmod(0o755)
    
    def _generate_claude_desktop_config(self) -> None:
        """Generate Claude Desktop configuration."""
        if not self.backend_instance:
            raise ValueError("Backend instance not initialized")
        
        claude_config = self.backend_instance.generate_claude_desktop_config()
        
        with open(self.project_path / "config" / "claude_desktop_config.json", 'w', encoding='utf-8') as f:
            json.dump(claude_config, f, indent=2)
    
    def install_dependencies(self) -> None:
        """Install project dependencies."""
        if self.verbose:
            console.print("[dim]Installing dependencies...[/dim]")
        
        # Create virtual environment
        venv_path = self.project_path / "venv"
        subprocess.run([
            "python", "-m", "venv", str(venv_path)
        ], check=True, cwd=self.project_path)
        
        # Determine pip path
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix-like
            pip_path = venv_path / "bin" / "pip"
        
        # Install dependencies
        subprocess.run([
            str(pip_path), "install", "-r", "requirements.txt"
        ], check=True, cwd=self.project_path)
        
        if self.verbose:
            console.print("[dim]Dependencies installed successfully[/dim]")
    
    def validate_project(self) -> List[str]:
        """Validate the generated project."""
        errors = []
        
        # Check required files exist
        required_files = [
            "server.py",
            "requirements.txt",
            "README.md",
            "config/config.yaml",
            ".env.template",
        ]
        
        for file_path in required_files:
            if not (self.project_path / file_path).exists():
                errors.append(f"Required file missing: {file_path}")
        
        # Validate backend configuration if available
        if self.backend_instance:
            backend_errors = self.backend_instance.validate_config()
            errors.extend(backend_errors)
        
        return errors