"""Template management for MCP project generation."""

import os
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

try:
    from jinja2.sandbox import SandboxedEnvironment
except ImportError:
    # Fallback for older versions of Jinja2
    SandboxedEnvironment = Environment


class TemplateManager:
    """Manages Jinja2 templates for project generation."""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates"
        # Use SandboxedEnvironment for security
        self.env = SandboxedEnvironment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),  # Don't autoescape Python files
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self._register_filters()
    
    def _register_filters(self) -> None:
        """Register custom Jinja2 filters."""
        
        def snake_case(value: str) -> str:
            """Convert string to snake_case."""
            import re
            return re.sub(r'[-\s]+', '_', value.lower())
        
        def kebab_case(value: str) -> str:
            """Convert string to kebab-case."""
            import re
            return re.sub(r'[_\s]+', '-', value.lower())
        
        def pascal_case(value: str) -> str:
            """Convert string to PascalCase."""
            import re
            words = re.split(r'[-_\s]+', value)
            return ''.join(word.capitalize() for word in words)
        
        def camel_case(value: str) -> str:
            """Convert string to camelCase."""
            pascal = pascal_case(value)
            return pascal[0].lower() + pascal[1:] if pascal else ''
        
        self.env.filters['snake_case'] = snake_case
        self.env.filters['kebab_case'] = kebab_case
        self.env.filters['pascal_case'] = pascal_case
        self.env.filters['camel_case'] = camel_case
    
    def get_template(self, template_name: str) -> Template:
        """Get a template by name."""
        return self.env.get_template(template_name)
    
    def render_template(self, template_name: str, **kwargs) -> str:
        """Render a template with given context."""
        template = self.get_template(template_name)
        return template.render(**kwargs)
    
    def list_templates(self) -> List[str]:
        """List all available templates."""
        templates = []
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith(('.j2', '.jinja', '.jinja2')):
                    rel_path = Path(root).relative_to(self.template_dir) / file
                    templates.append(str(rel_path))
        return sorted(templates)
    
    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists."""
        try:
            self.env.get_template(template_name)
            return True
        except:
            return False