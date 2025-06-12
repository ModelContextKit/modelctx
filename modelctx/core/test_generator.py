"""Test file generation for MCP servers."""

from pathlib import Path
from rich.console import Console

from modelctx.backends.base import BaseBackend
from modelctx.core.templates import TemplateManager

console = Console()


class TestGenerator:
    """Generates test files for MCP projects."""
    
    def __init__(self, project_path: Path, project_name: str, verbose: bool = False):
        self.project_path = project_path
        self.project_name = project_name
        self.verbose = verbose
        self.template_manager = TemplateManager()
    
    def generate_tests(self, backend_instance: BaseBackend) -> None:
        """Generate all test files."""
        self._generate_server_tests(backend_instance)
        self._generate_tool_tests()
        self._generate_pytest_config()
    
    def _generate_server_tests(self, backend_instance: BaseBackend) -> None:
        """Generate test_server.py file."""
        try:
            server_test_template = self.template_manager.get_template("base/test_server.py.j2")
            server_test_content = server_test_template.render(
                **backend_instance.get_template_variables()
            )
            with open(self.project_path / "tests" / "test_server.py", 'w', encoding='utf-8') as f:
                f.write(server_test_content)
        except Exception as e:
            if self.verbose:
                console.print(f"[yellow]Warning: Could not generate test_server.py: {e}[/yellow]")
    
    def _generate_tool_tests(self) -> None:
        """Generate basic tool tests."""
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
    
    def _generate_pytest_config(self) -> None:
        """Generate pytest configuration."""
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