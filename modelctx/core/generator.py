"""Project generator for MCP servers."""

from pathlib import Path
from typing import List, Optional

from rich.console import Console

from modelctx.exceptions import ProjectGenerationError, ConfigurationError
from modelctx.utils.logging import get_logger

from modelctx.backends import get_backend_class
from modelctx.backends.base import BaseBackend, BackendConfig
from modelctx.core.config import ProjectConfig, ConfigWizard
from modelctx.core.project_structure import ProjectStructureManager
from modelctx.core.config_generator import ConfigGenerator
from modelctx.core.documentation_generator import DocumentationGenerator
from modelctx.core.test_generator import TestGenerator
from modelctx.core.script_generator import ScriptGenerator
from modelctx.core.dependency_manager import DependencyManager
from modelctx.core.templates import TemplateManager

console = Console()
logger = get_logger("generator")


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
        
        # Initialize component managers
        self.structure_manager = ProjectStructureManager(self.project_path)
        self.config_generator = ConfigGenerator(self.project_path)
        self.documentation_generator = DocumentationGenerator(self.project_path, verbose)
        self.test_generator = TestGenerator(self.project_path, project_name, verbose)
        self.script_generator = ScriptGenerator(self.project_path, project_name)
        self.dependency_manager = DependencyManager(self.project_path, verbose)
        self.template_manager = TemplateManager()
        
        # Initialize backend with minimal config
        self._init_backend()
    
    def _init_backend(self) -> None:
        """Initialize backend instance with minimal configuration.
        
        Creates a BackendConfig with default values and instantiates the
        appropriate backend class. This is called during ProjectGenerator
        initialization to set up the backend for code generation.
        
        Raises:
            ProjectGenerationError: If backend initialization fails due to
                invalid configuration or missing dependencies.
        """
        try:
            backend_config = BackendConfig(
                backend_type=self.backend_type,
                project_name=self.project_name,
                description=f"MCP server with {self.backend_type} backend",
                dependencies=self.backend_class.get_dependencies(),
                optional_dependencies=self.backend_class.get_optional_dependencies()
            )
            self.backend_instance = self.backend_class(backend_config)
            logger.debug(f"Initialized {self.backend_type} backend")
        except Exception as e:
            raise ProjectGenerationError(
                f"Failed to initialize {self.backend_type} backend: {str(e)}"
            ) from e
    
    def set_config(self, config: ProjectConfig) -> None:
        """Set project configuration and reinitialize backend if needed.
        
        Args:
            config: Complete project configuration including backend settings.
                   If backend_config is provided, the backend instance will be
                   recreated with the new configuration.
        """
        self.config = config
        if config.backend_config:
            self.backend_instance = self.backend_class(config.backend_config)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from a YAML file and apply it.
        
        Args:
            config_path: Path to the configuration file (YAML format).
                        The file should contain project settings and backend
                        configuration parameters.
        
        Raises:
            ConfigurationError: If the configuration file is invalid or missing
                              required parameters.
            FileNotFoundError: If the configuration file doesn't exist.
        """
        self.config = ConfigWizard.load_config(config_path)
        if self.config.backend_config:
            self.backend_instance = self.backend_class(self.config.backend_config)
    
    def generate(self) -> None:
        """Generate the complete MCP server project.
        
        Creates a fully functional MCP server project with the following components:
        - Project directory structure with organized folders
        - Main server.py file with MCP protocol implementation
        - Configuration files (config.yaml, .env template, logging.yaml)
        - Documentation (README.md, API docs, deployment guide)
        - Test files and pytest configuration
        - Build/dependency files (requirements.txt, pyproject.toml)
        - Setup and deployment scripts
        - Claude Desktop integration configuration
        
        Raises:
            ProjectGenerationError: If any step of the generation process fails.
        """
        if self.verbose:
            console.print(f"[dim]Generating project in {self.project_path}[/dim]")
        
        # Create project directory structure
        self.structure_manager.create_directory_structure()
        
        # Generate core files
        self._generate_server_file()
        self.config_generator.generate_config_files(self.backend_instance)
        self.dependency_manager.generate_requirements(self.backend_instance)
        self._generate_project_metadata()
        self.documentation_generator.generate_documentation(self.backend_instance)
        self.test_generator.generate_tests(self.backend_instance)
        self.script_generator.generate_scripts()
        self.config_generator.generate_claude_desktop_config(self.backend_instance)
        
        if self.verbose:
            console.print("[dim]Project generation completed[/dim]")
    
    
    def _generate_server_file(self) -> None:
        """Generate the main server.py file."""
        if not self.backend_instance:
            raise ProjectGenerationError("Backend instance not initialized")
        
        try:
            logger.debug("Generating server.py file")
            server_code = self.backend_instance.generate_server_code()
            server_path = self.project_path / "server.py"
            
            with open(server_path, 'w', encoding='utf-8') as f:
                f.write(server_code)
            
            # Make server executable
            server_path.chmod(0o755)
            logger.debug(f"Server file created at: {server_path}")
            
        except Exception as e:
            raise ProjectGenerationError(f"Failed to generate server file: {str(e)}") from e
    
    
    
    def _generate_project_metadata(self) -> None:
        """Generate project metadata files."""
        if not self.backend_instance:
            raise ValueError("Backend instance not initialized")
        
        # Generate .gitignore
        gitignore_template = self.template_manager.get_template("base/.gitignore.j2")
        gitignore_content = gitignore_template.render()
        with open(self.project_path / ".gitignore", 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
    
    
    
    
    
    def install_dependencies(self) -> None:
        """Install project dependencies."""
        self.dependency_manager.install_dependencies()
    
    def validate_project(self) -> List[str]:
        """Validate the generated project."""
        errors = []
        
        # Validate project structure
        structure_errors = self.structure_manager.validate_structure()
        errors.extend(structure_errors)
        
        # Validate backend configuration if available
        if self.backend_instance:
            backend_errors = self.backend_instance.validate_config()
            errors.extend(backend_errors)
        
        return errors