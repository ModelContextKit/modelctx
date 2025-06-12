# Changelog

All notable changes to ModelContextKit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Official website at [modelcontextkit.com](https://modelcontextkit.com)
- Comprehensive CONTRIBUTING.md with development guidelines
- Pre-commit hooks for code quality
- Development requirements file
- Enhanced quality assurance documentation

### Fixed
- **Critical**: Fixed indentation issues in generated MCP server code
- **Critical**: Corrected MCP schema format from `inputSchema` to `input_schema`
- Fixed resource URI template issues that caused syntax errors
- Improved test generation to use modern MCP patterns
- Fixed webscraper backend circular dependencies
- Resolved argument extraction issues in tool implementations

### Changed
- Updated test templates to use correct server imports
- Simplified resource implementations to avoid template complications
- Enhanced error handling in generated code
- Improved code generation reliability across all backends

### Security
- Enhanced input validation in generated servers
- Improved argument sanitization in tool implementations

## [0.1.2] - 2025-06-13

### Added
- Multiple backend support (database, API, filesystem, webscraper, email, cloud storage)
- Interactive wizard for project setup
- Comprehensive project templates
- Claude Desktop integration
- Security features and input validation
- Auto-generated documentation
- Test suite generation

### Features
- CLI interface with multiple commands
- Configuration through YAML files and environment variables
- Production-ready code generation
- MCP protocol compliance

## [0.1.1] - 2025-06-12

### Added
- Initial release with basic functionality
- Core CLI framework
- Basic template system

## [0.1.0] - 2025-06-10

### Added
- Project initialization
- Basic structure setup