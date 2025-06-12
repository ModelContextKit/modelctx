"""Project structure management for MCP servers."""

from pathlib import Path
from typing import List


class ProjectStructureManager:
    """Manages the directory structure and file creation for MCP projects."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def create_directory_structure(self) -> None:
        """Create the project directory structure.
        
        Creates a standard MCP server project layout with organized directories
        for configuration, source code, tests, documentation, and scripts.
        Python package directories automatically get __init__.py files.
        """
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
    
    def get_required_files(self) -> List[str]:
        """Get list of required files for project validation.
        
        Returns:
            List of relative file paths that must exist in a valid project.
        """
        return [
            "server.py",
            "requirements.txt",
            "README.md",
            "config/config.yaml",
            ".env.template",
        ]
    
    def validate_structure(self) -> List[str]:
        """Validate that all required files exist.
        
        Returns:
            List of error messages for missing required files. Empty list
            indicates a valid project structure.
        """
        errors = []
        
        for file_path in self.get_required_files():
            if not (self.project_path / file_path).exists():
                errors.append(f"Required file missing: {file_path}")
        
        return errors