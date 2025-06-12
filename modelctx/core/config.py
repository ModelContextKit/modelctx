"""Configuration management and interactive wizard for MCP setup."""

import os
import yaml
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional, Type

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.table import Table

from modelctx.backends import AVAILABLE_BACKENDS, get_backend_class
from modelctx.backends.base import BackendConfig, BaseBackend
from modelctx.utils.validation import validate_project_name, validate_url, validate_file_path

console = Console()


@dataclass
class ProjectConfig:
    """Main project configuration."""
    project_name: str
    backend_type: str
    description: str = ""
    output_dir: str = "."
    install_dependencies: bool = True
    backend_config: Optional[BackendConfig] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        if self.backend_config:
            data["backend_config"] = self.backend_config.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectConfig":
        """Create from dictionary."""
        backend_config_data = data.pop("backend_config", None)
        config = cls(**data)
        if backend_config_data:
            config.backend_config = BackendConfig.from_dict(backend_config_data)
        return config


class ConfigWizard:
    """Interactive configuration wizard."""
    
    def __init__(self, output_dir: str = ".", verbose: bool = False):
        self.output_dir = output_dir
        self.verbose = verbose
        self.config: Optional[ProjectConfig] = None
    
    def run(self) -> ProjectConfig:
        """Run the interactive configuration wizard."""
        console.print("\n[bold blue]Welcome to the MCP Server Setup Wizard![/bold blue]\n")
        
        # Step 1: Project basics
        project_name = self._get_project_name()
        backend_type = self._get_backend_type()
        description = self._get_project_description(project_name, backend_type)
        
        # Step 2: Backend-specific configuration
        backend_class = get_backend_class(backend_type)
        backend_config = self._configure_backend(backend_class, project_name)
        
        # Step 3: Installation preferences
        install_deps = self._get_installation_preferences()
        
        # Create final configuration
        self.config = ProjectConfig(
            project_name=project_name,
            backend_type=backend_type,
            description=description,
            output_dir=self.output_dir,
            install_dependencies=install_deps,
            backend_config=backend_config
        )
        
        # Step 4: Show summary and confirm
        self._show_configuration_summary()
        
        if not Confirm.ask("\n[bold]Create project with this configuration?[/bold]", default=True):
            console.print("[yellow]Configuration cancelled.[/yellow]")
            raise KeyboardInterrupt()
        
        return self.config
    
    def _get_project_name(self) -> str:
        """Get and validate project name."""
        while True:
            name = Prompt.ask(
                "[bold cyan]📝 Enter project name[/bold cyan]",
                default="my-mcp-server"
            )
            
            if validate_project_name(name):
                # Check if project already exists
                project_path = Path(self.output_dir) / name
                if project_path.exists():
                    if Confirm.ask(f"[yellow]Project '{name}' already exists. Overwrite?[/yellow]", default=False):
                        return name
                    continue
                return name
            
            console.print("[red]❌ Invalid project name. Use alphanumeric characters, hyphens, and underscores only.[/red]")
    
    def _get_backend_type(self) -> str:
        """Get backend type selection."""
        console.print("\n[bold cyan]🔧 Select backend type:[/bold cyan]")
        
        # Display available backends in a table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Backend", style="yellow", width=12)
        table.add_column("Description", style="white")
        
        backend_list = list(AVAILABLE_BACKENDS.items())
        for i, (backend_type, backend_class) in enumerate(backend_list, 1):
            table.add_row(
                str(i),
                backend_type,
                backend_class.get_description()
            )
        
        console.print(table)
        
        while True:
            choice = IntPrompt.ask(
                "\n[bold]Enter option number[/bold]",
                default=1,
                choices=[str(i) for i in range(1, len(backend_list) + 1)]
            )
            
            backend_type = backend_list[choice - 1][0]
            console.print(f"[green]✅ Selected: {backend_type}[/green]")
            return backend_type
    
    def _get_project_description(self, project_name: str, backend_type: str) -> str:
        """Get project description."""
        default_desc = f"MCP server with {backend_type} backend"
        return Prompt.ask(
            "\n[bold cyan]📋 Enter project description[/bold cyan]",
            default=default_desc
        )
    
    def _configure_backend(self, backend_class: Type[BaseBackend], project_name: str) -> BackendConfig:
        """Configure backend-specific settings."""
        console.print(f"\n[bold cyan]⚙️ Configuring {backend_class.get_backend_type()} backend:[/bold cyan]")
        
        # Get configuration prompts from backend
        prompts = backend_class.get_config_prompts()
        parameters = {}
        
        for prompt_config in prompts:
            parameters.update(self._handle_prompt(prompt_config))
        
        # Create backend configuration
        backend_config = BackendConfig(
            backend_type=backend_class.get_backend_type(),
            project_name=project_name,
            description=parameters.get("description", ""),
            parameters=parameters,
            dependencies=backend_class.get_dependencies(),
            optional_dependencies=backend_class.get_optional_dependencies()
        )
        
        # Validate configuration
        errors = backend_class(backend_config).validate_config()
        if errors:
            console.print("[red]❌ Configuration errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            console.print("[yellow]Please fix these issues and try again.[/yellow]")
            return self._configure_backend(backend_class, project_name)
        
        return backend_config
    
    def _handle_prompt(self, prompt_config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a single configuration prompt."""
        prompt_type = prompt_config.get("type", "text")
        name = prompt_config["name"]
        message = prompt_config["message"]
        default = prompt_config.get("default")
        choices = prompt_config.get("choices")
        required = prompt_config.get("required", False)
        validator = prompt_config.get("validator")
        
        while True:
            if prompt_type == "text":
                value = Prompt.ask(message, default=default)
            elif prompt_type == "int":
                value = IntPrompt.ask(message, default=default)
            elif prompt_type == "bool":
                value = Confirm.ask(message, default=default)
            elif prompt_type == "choice":
                if choices:
                    console.print(f"\nChoices for {name}:")
                    for i, choice in enumerate(choices, 1):
                        console.print(f"  {i}. {choice}")
                    
                    choice_idx = IntPrompt.ask(
                        "Select option",
                        choices=[str(i) for i in range(1, len(choices) + 1)]
                    )
                    value = choices[choice_idx - 1]
                else:
                    value = Prompt.ask(message, default=default)
            else:
                value = Prompt.ask(message, default=default)
            
            # Validate input
            if required and not value:
                console.print("[red]❌ This field is required.[/red]")
                continue
            
            if validator:
                if validator == "url" and value and not validate_url(value):
                    console.print("[red]❌ Invalid URL format.[/red]")
                    continue
                elif validator == "file_path" and value and not validate_file_path(value):
                    console.print("[red]❌ Invalid file path.[/red]")
                    continue
            
            break
        
        return {name: value}
    
    def _get_installation_preferences(self) -> bool:
        """Get installation preferences."""
        return Confirm.ask(
            "\n[bold cyan]📦 Install dependencies automatically?[/bold cyan]",
            default=True
        )
    
    def _show_configuration_summary(self) -> None:
        """Show configuration summary."""
        if not self.config:
            return
        
        summary_text = f"""[bold]Project Name:[/bold] {self.config.project_name}
[bold]Backend Type:[/bold] {self.config.backend_type}
[bold]Description:[/bold] {self.config.description}
[bold]Output Directory:[/bold] {Path(self.config.output_dir).absolute()}
[bold]Install Dependencies:[/bold] {self.config.install_dependencies}

[bold]Backend Configuration:[/bold]"""
        
        if self.config.backend_config:
            for key, value in self.config.backend_config.parameters.items():
                # Hide sensitive values
                if any(secret in key.lower() for secret in ["password", "token", "key", "secret"]):
                    value = "*" * len(str(value)) if value else ""
                summary_text += f"\n  {key}: {value}"
        
        console.print(Panel(
            summary_text,
            title="[bold blue]Configuration Summary[/bold blue]",
            border_style="blue"
        ))
    
    def save_config(self, config_path: str) -> None:
        """Save configuration to file."""
        if not self.config:
            raise ValueError("No configuration to save")
        
        config_data = self.config.to_dict()
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
        
        console.print(f"[green]✅ Configuration saved to {config_path}[/green]")
    
    @classmethod
    def load_config(cls, config_path: str) -> ProjectConfig:
        """Load configuration from file."""
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return ProjectConfig.from_dict(config_data)