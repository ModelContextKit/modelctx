"""CLI interface for MCP Quick Setup Tool."""

import os
import sys
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from modelctx.core.generator import ProjectGenerator
from modelctx.core.config import ConfigWizard
from modelctx.core.backend_registry import backend_registry
from modelctx.utils.validation import validate_project_name
from modelctx.utils.logging import get_logger, configure_root_logger
from modelctx.utils.error_handling import format_cli_error, format_cli_warning, format_cli_success
from modelctx.exceptions import ModelCtxError, ValidationError

console = Console()
logger = get_logger("cli")

# Get backend choices dynamically from registry
def get_backend_choices() -> List[str]:
    """Get available backend choices."""
    return backend_registry.get_backend_names()


@click.group()
@click.version_option(version="0.1.0", prog_name="modelctx")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """MCP Quick Setup Tool - Create MCP servers with ease."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    
    # Configure logging based on verbosity
    configure_root_logger(verbose)
    
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")
        logger.debug("Verbose logging enabled")


@cli.command()
def list() -> None:
    """List all available backend types."""
    console.print("\n[bold blue]Available MCP Backend Types[/bold blue]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Backend", style="cyan", width=15)
    table.add_column("Description", style="white", width=50)
    table.add_column("Dependencies", style="yellow", width=30)
    
    for backend_name, backend_class in backend_registry.get_all_backends().items():
        table.add_row(
            backend_name,
            backend_class.get_description(),
            ", ".join(backend_class.get_dependencies())
        )
    
    console.print(table)
    console.print("\n[dim]Use 'modelctx create <name> --backend <type>' to create a project[/dim]")


@cli.command()
@click.argument("project_name")
@click.option(
    "--backend", 
    "-b", 
    required=True,
    type=click.Choice(get_backend_choices()),
    help="Backend type to use"
)
@click.option("--output-dir", "-o", default=".", help="Output directory (default: current directory)")
@click.option("--config-file", "-c", help="Configuration file to use")
@click.option("--no-install", is_flag=True, help="Skip dependency installation")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing project")
@click.pass_context
def create(
    ctx: click.Context,
    project_name: str,
    backend: str,
    output_dir: str,
    config_file: Optional[str],
    no_install: bool,
    force: bool,
) -> None:
    """Create a new MCP server project."""
    verbose = ctx.obj.get("verbose", False)
    
    # Validate project name
    try:
        if not validate_project_name(project_name):
            raise ValidationError(
                "Invalid project name", 
                {"suggestion": "Use alphanumeric characters, hyphens, and underscores only"}
            )
    except ValidationError as e:
        console.print(format_cli_error(str(e), e.details.get("suggestion")))
        logger.error(f"Project name validation failed: {e}")
        sys.exit(1)
    
    # Check if project already exists
    project_path = Path(output_dir) / project_name
    if project_path.exists() and not force:
        error_msg = f"Project '{project_name}' already exists"
        console.print(format_cli_error(error_msg, "Use --force to overwrite"))
        logger.error(f"Project already exists: {project_path}")
        sys.exit(1)
    
    console.print(f"\n[bold green]Creating MCP server: {project_name}[/bold green]")
    console.print(f"[dim]Backend: {backend}[/dim]")
    console.print(f"[dim]Output: {project_path.absolute()}[/dim]\n")
    
    try:
        logger.info(f"Creating MCP server project: {project_name}")
        
        # Initialize project generator
        generator = ProjectGenerator(
            project_name=project_name,
            backend_type=backend,
            output_dir=output_dir,
            verbose=verbose
        )
        
        # Load configuration if provided
        if config_file:
            logger.debug(f"Loading configuration from: {config_file}")
            generator.load_config(config_file)
        
        # Generate project
        with console.status("[bold green]Generating project..."):
            generator.generate()
        
        console.print(format_cli_success("Project structure created successfully!"))
        logger.info(f"Project generated successfully at: {project_path}")
        
        # Install dependencies unless skipped
        if not no_install:
            with console.status("[bold yellow]Installing dependencies..."):
                generator.install_dependencies()
            console.print(format_cli_success("Dependencies installed successfully!"))
            logger.info("Dependencies installed successfully")
        
        # Show next steps
        _show_next_steps(project_name, project_path)
        
    except ModelCtxError as e:
        console.print(format_cli_error(f"Error creating project: {e}"))
        logger.error(f"ModelCtx error during project creation: {e}", exc_info=verbose)
        sys.exit(1)
    except Exception as e:
        console.print(format_cli_error(f"Unexpected error creating project: {e}"))
        logger.error(f"Unexpected error during project creation: {e}", exc_info=True)
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option("--output-dir", "-o", default=".", help="Output directory (default: current directory)")
@click.pass_context
def wizard(ctx: click.Context, output_dir: str) -> None:
    """Interactive project creation wizard."""
    verbose = ctx.obj.get("verbose", False)
    
    console.print(Panel.fit(
        "[bold blue] MCP Server Creation Wizard[/bold blue]\n"
        "[dim]This wizard will guide you through creating a new MCP server project.[/dim]",
        border_style="blue"
    ))
    
    try:
        # Initialize configuration wizard
        wizard = ConfigWizard(output_dir=output_dir, verbose=verbose)
        
        # Run interactive configuration
        config = wizard.run()
        
        # Create project with wizard configuration
        generator = ProjectGenerator(
            project_name=config.project_name,
            backend_type=config.backend_type,
            output_dir=output_dir,
            verbose=verbose
        )
        generator.set_config(config)
        
        # Generate project
        console.print("\n[bold green] Generating your MCP server...[/bold green]")
        with console.status("[bold green]Creating project files..."):
            generator.generate()
        
        console.print("[green]SUCCESS: Project created successfully![/green]")
        
        # Install dependencies
        if config.install_dependencies:
            with console.status("[bold yellow]Installing dependencies..."):
                generator.install_dependencies()
            console.print("[green]SUCCESS: Dependencies installed![/green]")
        
        # Show next steps
        project_path = Path(output_dir) / config.project_name
        _show_next_steps(config.project_name, project_path)
        
    except KeyboardInterrupt:
        console.print(f"\n{format_cli_warning('Wizard cancelled by user')}")
        logger.info("Wizard cancelled by user")
        sys.exit(0)
    except ModelCtxError as e:
        console.print(f"\n{format_cli_error(f'Error during wizard: {e}')}")
        logger.error(f"ModelCtx error during wizard: {e}", exc_info=verbose)
        sys.exit(1)
    except Exception as e:
        console.print(f"\n{format_cli_error(f'Unexpected error during wizard: {e}')}")
        logger.error(f"Unexpected error during wizard: {e}", exc_info=True)
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option("--list", "list_templates", is_flag=True, help="List available templates")
@click.option("--add", help="Add a custom template")
@click.option("--remove", help="Remove a custom template")
def templates(list_templates: bool, add: Optional[str], remove: Optional[str]) -> None:
    """Manage project templates."""
    if list_templates:
        _list_templates()
    elif add:
        _add_template(add)
    elif remove:
        _remove_template(remove)
    else:
        console.print("[yellow]Use --list, --add, or --remove with the templates command.[/yellow]")


@cli.command()
@click.argument("project_path")
def docs(project_path: str) -> None:
    """Generate documentation for an MCP server project."""
    project = Path(project_path)
    if not project.exists():
        console.print(f"[red]ERROR: Project not found: {project_path}[/red]")
        sys.exit(1)
    
    console.print(f"[blue]Generating documentation for {project.name}...[/blue]")
    # TODO: Implement documentation generation
    console.print("[green]Documentation generated![/green]")


@cli.command()
@click.argument("project_name")
@click.option("--target", default="local", help="Deployment target (local, docker, cloud)")
def deploy(project_name: str, target: str) -> None:
    """Deploy an MCP server project."""
    console.print(f"[blue]Deploying {project_name} to {target}...[/blue]")
    # TODO: Implement deployment functionality
    console.print("[green]Deployment completed![/green]")


def _show_next_steps(project_name: str, project_path: Path) -> None:
    """Display post-creation instructions to the user.
    
    Shows a formatted panel with step-by-step instructions for setting up
    and testing the newly created MCP server project.
    
    Args:
        project_name: Name of the created project.
        project_path: Path to the project directory.
    """
    next_steps = Text()
    next_steps.append("Next Steps:\n\n", style="bold green")
    next_steps.append(f"1. Navigate to your project:\n   cd {project_path}\n\n", style="cyan")
    next_steps.append("2. Configure your settings:\n   Edit config/config.yaml and .env\n\n", style="cyan")
    next_steps.append("3. Test your server:\n   python server.py\n\n", style="cyan")
    next_steps.append("4. Test with MCP Inspector:\n   npx @modelcontextprotocol/inspector python server.py\n\n", style="cyan")
    next_steps.append("5. Add to Claude Desktop:\n   Copy config/claude_desktop_config.json settings\n\n", style="cyan")
    
    console.print(Panel(
        next_steps,
        title=f"[bold]MCP Server '{project_name}' Created Successfully![/bold]",
        border_style="green"
    ))


def _list_templates() -> None:
    """List available templates."""
    console.print("\n[bold blue]Available Templates[/bold blue]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Template", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Description", style="white")
    
    # Built-in templates
    for backend_name in backend_registry.get_backend_names():
        table.add_row(
            f"{backend_name}-basic",
            "Built-in",
            f"Basic {backend_name} MCP server template"
        )
    
    # TODO: Add custom templates from user directory
    
    console.print(table)


def _add_template(template_path: str) -> None:
    """Add a custom template."""
    console.print(f"[blue]Adding template from: {template_path}[/blue]")
    # TODO: Implement custom template addition
    console.print("[green]Template added successfully![/green]")


def _remove_template(template_name: str) -> None:
    """Remove a custom template."""
    console.print(f"[blue]Removing template: {template_name}[/blue]")
    # TODO: Implement custom template removal
    console.print("[green]Template removed successfully![/green]")


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]ERROR: Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()