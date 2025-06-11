# ModelContextKit

> 🚀 A comprehensive CLI tool for rapidly creating, configuring, and deploying Model Context Protocol (MCP) servers

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## What is MCP?

The Model Context Protocol (MCP) is an open standard developed by Anthropic that enables AI applications (like Claude) to connect with external tools, data sources, and APIs in a standardized way. Think of it as "USB-C for AI applications" - it provides a universal connector between AI models and external systems.

## Features

✨ **Quick Setup**: Generate production-ready MCP servers in minutes, not hours  
🔧 **Multiple Backends**: Support for databases, APIs, filesystems, web scrapers, email, and cloud storage  
🎯 **Interactive Wizard**: Guided setup with intelligent configuration prompts  
📚 **Comprehensive Templates**: Pre-built templates following MCP best practices  
🔒 **Security First**: Built-in security features and input validation  
🧪 **Testing Ready**: Generated projects include test suites and examples  
📖 **Auto Documentation**: Comprehensive documentation generation  
🎨 **Claude Desktop Integration**: Automatic configuration for Claude Desktop  

## Installation

```bash
# Install base package
pip install modelcontextkit

# Install with specific backend support
pip install modelcontextkit[database]
pip install modelcontextkit[api]
pip install modelcontextkit[filesystem]
pip install modelcontextkit[webscraper]
pip install modelcontextkit[email]
pip install modelcontextkit[cloudstorage]

# Install with all backends
pip install modelcontextkit[all]
```

## Quick Start

### Interactive Wizard (Recommended)

```bash
modelctx wizard
```

### Command Line Interface

```bash
# List available backend types
modelctx list

# Create a database MCP server
modelctx create my-db-server --backend database

# Create an API integration server
modelctx create my-api-server --backend api

# View templates
modelctx templates
```

## Supported Backends

### 🗄️ Database Backend
Connect to SQL databases (PostgreSQL, MySQL, SQLite) with built-in connection pooling and security.

**Generated Tools:**
- `execute_query(query: str)` - Execute SQL queries safely
- `get_table_schema(table_name: str)` - Get table structure
- `list_tables()` - List all tables

**Configuration:**
- Database connection parameters
- Connection pooling settings
- Query timeout and limits

### 🌐 REST API Backend
Integrate with REST APIs with authentication, rate limiting, and error handling.

**Generated Tools:**
- `api_request(endpoint: str, method: str, data: dict)` - Make HTTP requests
- `get_api_status()` - Check API health

**Authentication Support:**
- Bearer tokens
- API keys
- OAuth2 flows

### 📁 Filesystem Backend
Access and manipulate local files and directories with security controls.

**Generated Tools:**
- `read_file(file_path: str)` - Read file contents
- `write_file(file_path: str, content: str)` - Write to files
- `list_directory(dir_path: str)` - List directory contents
- `search_files(pattern: str, directory: str)` - Search for files

### 🕷️ Web Scraper Backend
Scrape and parse web content with respect for robots.txt and rate limiting.

**Generated Tools:**
- `scrape_url(url: str)` - Extract content from web pages
- `extract_links(url: str)` - Get all links from a page
- `take_screenshot(url: str)` - Capture page screenshots

### 📧 Email Backend
Send and receive emails via SMTP/IMAP with support for attachments.

**Generated Tools:**
- `send_email(to: str, subject: str, body: str)` - Send emails
- `list_emails(folder: str, limit: int)` - List emails from folder
- `read_email(email_id: str)` - Read specific email

### ☁️ Cloud Storage Backend
Connect to cloud storage services (AWS S3, Google Cloud Storage, Azure Blob).

**Generated Tools:**
- `upload_file(local_path: str, remote_key: str)` - Upload files
- `download_file(remote_key: str, local_path: str)` - Download files
- `list_objects(prefix: str)` - List stored objects
- `delete_object(key: str)` - Delete objects

## Generated Project Structure

```
my-mcp-server/
├── server.py                 # Main MCP server file
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Python project metadata
├── README.md                # Project documentation
├── .env.template            # Environment variables template
├── .gitignore              # Git ignore rules
├── config/
│   ├── config.yaml         # Main configuration file
│   ├── claude_desktop_config.json  # Claude Desktop integration
│   └── logging.yaml        # Logging configuration
├── src/
│   ├── __init__.py
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_server.py      # Server tests
│   └── test_tools.py       # Tool-specific tests
├── docs/
│   ├── API.md              # API documentation
│   └── DEPLOYMENT.md       # Deployment guide
└── scripts/
    ├── setup.sh            # Setup script
    └── deploy.sh           # Deployment script
```

## Configuration

The tool supports flexible configuration through:

- **Interactive prompts** during wizard mode
- **Configuration files** (YAML/JSON)
- **Environment variables** for sensitive data
- **Command-line arguments** for automation

Example configuration:
```yaml
# config/config.yaml
server:
  name: "my-api-server"
  description: "API integration MCP server"
  
backend:
  type: "api"
  base_url: "https://api.example.com"
  auth_type: "bearer"
  rate_limit: 60
  
security:
  validate_inputs: true
  log_requests: true
  timeout: 30
```

## Claude Desktop Integration

Generated servers automatically include configuration for Claude Desktop:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["/path/to/my-mcp-server/server.py"],
      "env": {
        "API_KEY": "your-api-key",
        "DATABASE_URL": "your-db-connection"
      }
    }
  }
}
```

## Development and Testing

Each generated project includes:

- **Unit tests** with pytest
- **Integration tests** with real MCP client
- **Mock data** for development
- **Development server** with hot-reload
- **MCP Inspector integration** for testing

```bash
# Run tests
cd my-mcp-server
python -m pytest

# Start development server
python server.py --dev

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python server.py
```

## Security Features

- 🔒 **Input validation** and sanitization
- 🛡️ **Access controls** and permission systems
- 📝 **Audit logging** for all operations
- 🔐 **Secure credential management**
- 🚫 **SQL injection prevention**
- 🌐 **CORS and rate limiting**

## CLI Reference

```bash
# Create new MCP server
modelctx create <project-name> --backend <type> [options]

# Interactive wizard
modelctx wizard

# List available backends
modelctx list

# Manage templates
modelctx templates [list|add|remove]

# Generate documentation
modelctx docs <project-path>

# Deploy server (if configured)
modelctx deploy <project-name>
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📚 [Documentation](https://github.com/ModelContextKit/modelctx/wiki)
- 🐛 [Bug Reports](https://github.com/ModelContextKit/modelctx/issues)
- 💬 [Discussions](https://github.com/ModelContextKit/modelctx/discussions)
- 📧 Create an issue for support

---

Made with ❤️ for the MCP community