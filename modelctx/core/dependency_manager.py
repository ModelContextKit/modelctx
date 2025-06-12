"""Dependency management for MCP servers."""

import os
import subprocess
from pathlib import Path
from rich.console import Console

from modelctx.utils.security import validate_file_path, escape_shell_argument

from modelctx.backends.base import BaseBackend
from modelctx.core.templates import TemplateManager

console = Console()


class DependencyManager:
    """Manages dependencies and requirements for MCP projects."""
    
    def __init__(self, project_path: Path, verbose: bool = False):
        self.project_path = project_path
        self.verbose = verbose
        self.template_manager = TemplateManager()
    
    def generate_requirements(self, backend_instance: BaseBackend) -> None:
        """Generate requirements.txt and pyproject.toml."""
        # Generate requirements.txt
        requirements_content = backend_instance.generate_requirements()
        with open(self.project_path / "requirements.txt", 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        # Generate pyproject.toml
        pyproject_template = self.template_manager.get_template("base/pyproject.toml.j2")
        pyproject_content = pyproject_template.render(
            **backend_instance.get_template_variables()
        )
        with open(self.project_path / "pyproject.toml", 'w', encoding='utf-8') as f:
            f.write(pyproject_content)
    
    def install_dependencies(self) -> None:
        """Install project dependencies."""
        if self.verbose:
            console.print("[dim]Installing dependencies...[/dim]")
        
        # Validate project path for security
        safe_project_path = validate_file_path(self.project_path)
        
        # Create virtual environment - use validated path
        venv_path = safe_project_path / "venv"
        subprocess.run([
            "python", "-m", "venv", str(venv_path)
        ], check=True, cwd=safe_project_path)
        
        # Determine pip path
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix-like
            pip_path = venv_path / "bin" / "pip"
        
        # Validate pip path exists and is safe
        validate_file_path(pip_path, base_dir=venv_path)
        
        # Install dependencies - validate requirements file path
        requirements_file = safe_project_path / "requirements.txt"
        validate_file_path(requirements_file, base_dir=safe_project_path)
        
        subprocess.run([
            str(pip_path), "install", "-r", str(requirements_file)
        ], check=True, cwd=safe_project_path)
        
        if self.verbose:
            console.print("[dim]Dependencies installed successfully[/dim]")