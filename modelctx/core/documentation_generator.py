"""Documentation generation for MCP servers."""

from pathlib import Path
from rich.console import Console

from modelctx.backends.base import BaseBackend
from modelctx.core.templates import TemplateManager

console = Console()


class DocumentationGenerator:
    """Generates documentation files for MCP projects."""
    
    def __init__(self, project_path: Path, verbose: bool = False):
        self.project_path = project_path
        self.verbose = verbose
        self.template_manager = TemplateManager()
    
    def generate_documentation(self, backend_instance: BaseBackend) -> None:
        """Generate all documentation files."""
        self._generate_readme(backend_instance)
        self._generate_api_docs(backend_instance)
        self._generate_deployment_docs(backend_instance)
    
    def _generate_readme(self, backend_instance: BaseBackend) -> None:
        """Generate README.md file."""
        readme_template = self.template_manager.get_template("base/README.md.j2")
        readme_content = readme_template.render(
            **backend_instance.get_template_variables()
        )
        with open(self.project_path / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _generate_api_docs(self, backend_instance: BaseBackend) -> None:
        """Generate API documentation."""
        api_doc_template = self.template_manager.get_template("base/API.md.j2")
        api_content = api_doc_template.render(
            **backend_instance.get_template_variables()
        )
        with open(self.project_path / "docs" / "API.md", 'w', encoding='utf-8') as f:
            f.write(api_content)
    
    def _generate_deployment_docs(self, backend_instance: BaseBackend) -> None:
        """Generate deployment documentation."""
        deploy_doc_template = self.template_manager.get_template("base/DEPLOYMENT.md.j2")
        deploy_content = deploy_doc_template.render(
            **backend_instance.get_template_variables()
        )
        with open(self.project_path / "docs" / "DEPLOYMENT.md", 'w', encoding='utf-8') as f:
            f.write(deploy_content)