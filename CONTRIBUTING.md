# Contributing to ModelContextKit

We welcome contributions to ModelContextKit! This document provides guidelines for contributing to the project.

## 🌟 Ways to Contribute

- 🐛 **Bug Reports**: Report issues you encounter
- 💡 **Feature Requests**: Suggest new features or improvements
- 🔧 **Code Contributions**: Submit bug fixes or new features
- 📚 **Documentation**: Improve documentation and examples
- 🧪 **Testing**: Add tests or improve test coverage
- 🎨 **Templates**: Create new backend templates

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of the Model Context Protocol (MCP)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/modelcontextkit.git
   cd modelcontextkit
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

4. **Run Tests**
   ```bash
   python -m pytest tests/ -v
   ```

5. **Validate Code Generation**
   ```bash
   # Test that generated servers are syntactically correct
   python -c "
   import subprocess
   result = subprocess.run(['python', '-m', 'modelctx.cli', 'create', 'test_server', '--backend', 'filesystem', '--no-install'], capture_output=True)
   print('Generator test:', 'PASSED' if result.returncode == 0 else 'FAILED')
   "
   ```

## 📝 Contributing Code

### Branch Naming

- `feature/description` - for new features
- `fix/description` - for bug fixes
- `docs/description` - for documentation updates
- `test/description` - for test improvements

### Code Style

We follow Python best practices:

- **PEP 8** style guide
- **Type hints** for function signatures
- **Docstrings** for all public functions and classes
- **Line length**: 88 characters (Black formatter)

### Code Quality Checks

Before submitting, ensure your code passes:

```bash
# Format code
black modelctx/

# Sort imports
isort modelctx/

# Lint code
flake8 modelctx/

# Type checking
mypy modelctx/

# Run tests
pytest tests/ -v
```

## 🧪 Testing Guidelines

### Writing Tests

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test backend generation end-to-end
3. **Syntax Validation**: Ensure generated code compiles
4. **MCP Compliance**: Verify generated servers follow MCP spec

### Test Structure

```python
def test_backend_generation():
    """Test that backend generates syntactically correct code."""
    # Arrange
    backend = FilesystemBackend(config)
    
    # Act
    generated_code = backend.generate_server_code()
    
    # Assert
    # Test that code compiles
    compile(generated_code, '<string>', 'exec')
    
    # Test that required functions are present
    assert 'async def list_tools()' in generated_code
    assert 'async def call_tool(' in generated_code
```

### Critical Test Areas

- **Code Generation**: All backends must generate valid Python
- **Template Rendering**: Templates must render without errors
- **MCP Schema**: Generated schemas must be valid
- **Configuration**: Config validation and error handling

## 🏗️ Adding New Backends

To add a new backend type:

1. **Create Backend Class**
   ```python
   # modelctx/backends/your_backend.py
   from modelctx.backends.base import BaseBackend
   
   class YourBackend(BaseBackend):
       @classmethod
       def get_backend_type(cls) -> str:
           return "your_backend"
           
       def get_tools(self) -> List[Dict[str, Any]]:
           # Define your tools
           pass
   ```

2. **Register Backend**
   ```python
   # modelctx/backends/__init__.py
   from .your_backend import YourBackend
   
   BACKENDS = {
       # ... existing backends
       "your_backend": YourBackend,
   }
   ```

3. **Create Templates**
   - Add templates in `modelctx/templates/your_backend/`
   - Include `.env.jinja2` for environment variables

4. **Add Tests**
   ```python
   def test_your_backend_generation():
       """Test your backend generates valid code."""
       # Test implementation
   ```

5. **Update Documentation**
   - Add backend to README.md
   - Document tools and configuration options

## 📚 Documentation Guidelines

### Documentation Standards

- **Clear Examples**: Provide working code examples
- **Configuration Details**: Document all configuration options
- **Error Scenarios**: Explain common issues and solutions
- **MCP Context**: Explain how features relate to MCP protocol

### Documentation Types

1. **Code Comments**: Explain complex logic
2. **Docstrings**: API documentation
3. **README Updates**: Feature descriptions
4. **Wiki Pages**: Detailed guides and tutorials

## 🐛 Bug Reports

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Test with latest version** to ensure bug still exists
3. **Minimal reproduction** case if possible

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Run command: `modelctx create ...`
2. Observe error: ...

**Expected Behavior**
What should have happened

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.9.0]
- ModelContextKit: [e.g., 0.1.2]

**Generated Code** (if applicable)
```python
# Include problematic generated code
```

**Error Output**
```
# Include full error traceback
```
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you considered

**Additional Context**
Any other relevant information
```

## 🔄 Pull Request Process

### Before Submitting

1. **Create Issue**: Discuss feature/fix before implementing
2. **Follow Standards**: Ensure code follows project standards
3. **Add Tests**: Include tests for new functionality
4. **Update Docs**: Update relevant documentation
5. **Test Generation**: Verify generated code still works

### Pull Request Checklist

- [ ] **Tests Pass**: All existing tests continue to pass
- [ ] **New Tests**: Added tests for new functionality
- [ ] **Code Quality**: Passes linting and formatting checks
- [ ] **Generated Code Works**: New changes don't break code generation
- [ ] **Documentation Updated**: README, docstrings, etc. updated
- [ ] **Backwards Compatible**: Changes don't break existing functionality

### PR Template

```markdown
**Description**
Brief description of changes

**Type of Change**
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix/feature causing existing functionality to change)
- [ ] Documentation update

**Testing**
- [ ] Tests pass locally
- [ ] Generated code compiles
- [ ] Manual testing completed

**Checklist**
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🏆 Recognition

Contributors will be recognized in:

- **GitHub Contributors**: Automatic recognition
- **Release Notes**: Major contributions highlighted
- **Website**: Contributors page (if applicable)

## 📞 Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Create issues for bugs and feature requests
- **Website**: Visit [modelcontextkit.com](https://modelcontextkit.com)

## 📋 Development Priorities

Current focus areas:

1. **Code Quality**: Ensuring generated code is always syntactically correct
2. **New Backends**: Adding support for more integration types
3. **Testing**: Improving test coverage and reliability
4. **Documentation**: Better examples and guides
5. **Performance**: Optimizing generation speed
6. **Security**: Enhanced security features in generated code

## 🎯 Coding Standards

### Code Generation Quality

Since ModelContextKit generates code, we have special requirements:

- **Generated Code Must Compile**: All generated Python must be syntactically correct
- **MCP Compliance**: Generated servers must follow MCP protocol exactly
- **Error Handling**: Generated code must handle errors gracefully
- **Type Safety**: Use proper type hints in generated code
- **Security**: Generated code must include input validation

### Template Guidelines

When creating or modifying templates:

- **Use Jinja2 Best Practices**: Proper escaping and formatting
- **Validate Output**: Test that templates render correctly
- **Handle Edge Cases**: Templates should work with various configurations
- **Maintain Indentation**: Ensure generated Python has correct indentation
- **Include Comments**: Generated code should be well-commented

Thank you for contributing to ModelContextKit! 🙏