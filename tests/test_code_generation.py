"""Test code generation functionality."""

import ast
import tempfile
import shutil
from pathlib import Path
import pytest

from modelctx.cli import main
from modelctx.core.generator import ProjectGenerator
from modelctx.backends.filesystem import FilesystemBackend
from modelctx.backends.api import ApiBackend
from modelctx.backends.database import DatabaseBackend
from modelctx.backends.base import BackendConfig


class TestCodeGeneration:
    """Test that generated code is syntactically correct."""

    def test_filesystem_backend_syntax(self):
        """Test filesystem backend generates valid Python code."""
        config = BackendConfig(
            backend_type="filesystem",
            project_name="test_fs",
            description="Test filesystem server"
        )
        backend = FilesystemBackend(config)
        
        # Generate server code
        server_code = backend.generate_server_code()
        
        # Verify it compiles
        try:
            ast.parse(server_code)
        except SyntaxError as e:
            pytest.fail(f"Generated filesystem code has syntax errors: {e}")
        
        # Verify required functions are present
        assert "async def list_tools()" in server_code
        assert "async def call_tool(" in server_code
        assert "async def list_resources()" in server_code
        assert "async def read_resource(" in server_code

    def test_api_backend_syntax(self):
        """Test API backend generates valid Python code."""
        config = BackendConfig(
            backend_type="api",
            project_name="test_api",
            description="Test API server"
        )
        backend = ApiBackend(config)
        
        # Generate server code
        server_code = backend.generate_server_code()
        
        # Verify it compiles
        try:
            ast.parse(server_code)
        except SyntaxError as e:
            pytest.fail(f"Generated API code has syntax errors: {e}")
        
        # Verify required functions are present
        assert "async def list_tools()" in server_code
        assert "async def call_tool(" in server_code

    def test_database_backend_syntax(self):
        """Test database backend generates valid Python code."""
        config = BackendConfig(
            backend_type="database",
            project_name="test_db",
            description="Test database server"
        )
        backend = DatabaseBackend(config)
        
        # Generate server code
        server_code = backend.generate_server_code()
        
        # Verify it compiles
        try:
            ast.parse(server_code)
        except SyntaxError as e:
            pytest.fail(f"Generated database code has syntax errors: {e}")
        
        # Verify required functions are present
        assert "async def list_tools()" in server_code
        assert "async def call_tool(" in server_code

    def test_mcp_schema_format(self):
        """Test that generated tools use correct MCP schema format."""
        config = BackendConfig(
            backend_type="filesystem",
            project_name="test_schema",
            description="Test schema format"
        )
        backend = FilesystemBackend(config)
        
        # Generate server code
        server_code = backend.generate_server_code()
        
        # Verify it uses input_schema (not inputSchema)
        assert "input_schema=" in server_code
        assert "inputSchema=" not in server_code

    def test_project_generator_creates_valid_structure(self):
        """Test that ProjectGenerator creates a valid project structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Generate a filesystem project
            generator = ProjectGenerator(
                project_name="test_project",
                backend_type="filesystem",
                output_dir=str(temp_path),
                verbose=False
            )
            
            generator.generate()
            
            project_path = temp_path / "test_project"
            
            # Verify project structure exists
            assert project_path.exists()
            assert (project_path / "server.py").exists()
            assert (project_path / "requirements.txt").exists()
            assert (project_path / "config" / "config.yaml").exists()
            assert (project_path / "tests" / "test_server.py").exists()
            
            # Verify generated server.py is syntactically correct
            server_file = project_path / "server.py"
            with open(server_file, 'r') as f:
                server_code = f.read()
            
            try:
                ast.parse(server_code)
            except SyntaxError as e:
                pytest.fail(f"Generated project server.py has syntax errors: {e}")

    def test_tool_implementations_have_proper_indentation(self):
        """Test that tool implementations have correct indentation."""
        config = BackendConfig(
            backend_type="filesystem",
            project_name="test_indent",
            description="Test indentation"
        )
        backend = FilesystemBackend(config)
        
        # Generate server code
        server_code = backend.generate_server_code()
        
        # Verify no indentation errors by parsing
        try:
            ast.parse(server_code)
        except IndentationError as e:
            pytest.fail(f"Generated code has indentation errors: {e}")
        
        # Check that tool implementations are properly indented
        lines = server_code.split('\n')
        in_tool_impl = False
        for line in lines:
            if 'elif name ==' in line:
                in_tool_impl = True
            elif in_tool_impl and line.strip().startswith('try:'):
                # Tool implementation should be properly indented
                assert line.startswith('        try:'), f"Improper indentation: {line}"
                in_tool_impl = False

    def test_generated_tests_import_correctly(self):
        """Test that generated test files import the server correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Generate a project
            generator = ProjectGenerator(
                project_name="test_imports",
                backend_type="api",
                output_dir=str(temp_path),
                verbose=False
            )
            
            generator.generate()
            
            project_path = temp_path / "test_imports"
            test_file = project_path / "tests" / "test_server.py"
            
            # Verify test file exists and is syntactically correct
            assert test_file.exists()
            
            with open(test_file, 'r') as f:
                test_code = f.read()
            
            try:
                ast.parse(test_code)
            except SyntaxError as e:
                pytest.fail(f"Generated test file has syntax errors: {e}")
            
            # Verify it imports server correctly
            assert "from server import server" in test_code
            assert "from server import mcp" not in test_code  # Old incorrect import