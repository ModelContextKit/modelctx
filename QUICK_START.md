# MCP Quick Setup Tool - Quick Start Guide

> 🚀 Get up and running with MCP servers in 5 minutes!

## Installation (Choose Your Platform)

### 🐧 Linux & 🍎 macOS
```bash
# One-line installer
curl -fsSL https://raw.githubusercontent.com/ModelContextKit/modelctx/main/INSTALL.sh | bash

# Or manual clone and install
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools
./INSTALL.sh
```

### 🪟 Windows

#### Option 1: PowerShell (Recommended)
```powershell
# Download and run
irm https://raw.githubusercontent.com/ModelContextKit/modelctx/main/install.ps1 | iex

# Or from cloned repository
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools
.\install.ps1
```

#### Option 2: Command Prompt
```cmd
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools
install.bat
```

---

## Your First MCP Server

### Step 1: Activate Environment
```bash
# Linux/macOS
source ~/mcp-setup-tool/activate_mcp.sh

# Windows PowerShell
. $env:USERPROFILE\mcp-setup-tool\activate_mcp.ps1
```

### Step 2: Create Your First Server
```bash
# Interactive wizard (recommended for beginners)
mcp-setup wizard

# Or create directly
mcp-setup create my-first-server --backend database
```

### Step 3: Configure and Test
```bash
# Navigate to your project
cd my-first-server

# Configure environment (edit with your database details)
cp .env.template .env
# Edit .env file with your settings

# Test the server
python server.py
```

---

## Common Use Cases

### 📊 Database Integration
```bash
mcp-setup create sales-db --backend database
# Configure with PostgreSQL, MySQL, or SQLite
# Provides tools: execute_query, get_table_schema, list_tables
```

### 🌐 REST API Integration
```bash
mcp-setup create api-client --backend api
# Connect to any REST API with authentication
# Provides tools: api_request, get_api_status
```

### 📁 File System Access
```bash
mcp-setup create file-manager --backend filesystem
# Safe file operations with access controls
# Provides tools: read_file, write_file, list_directory
```

### 🕷️ Web Scraping
```bash
mcp-setup create web-scraper --backend webscraper
# Scrape websites with rate limiting and respect for robots.txt
# Provides tools: scrape_url, extract_links, take_screenshot
```

---

## Integration with Claude Desktop

After creating your MCP server:

### 1. Locate Claude Desktop Config
```bash
# Linux
~/.config/Claude/claude_desktop_config.json

# macOS
~/Library/Application Support/Claude/claude_desktop_config.json

# Windows
%APPDATA%\Claude\claude_desktop_config.json
```

### 2. Add Your Server
Copy the configuration from your project's `config/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-first-server": {
      "command": "python",
      "args": ["/path/to/my-first-server/server.py"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost/db"
      }
    }
  }
}
```

### 3. Restart Claude Desktop
Your MCP server will now be available in Claude Desktop!

---

## Testing Your Server

### With MCP Inspector (Recommended)
```bash
# Install Node.js if not already installed
# Then test your server:
npx @modelcontextprotocol/inspector python server.py
```

### With Built-in Tests
```bash
# Run the generated test suite
cd my-first-server
python -m pytest tests/
```

### Manual Testing
```bash
# Start server and test manually
python server.py
# Server runs on stdio - send MCP protocol messages
```

---

## Next Steps

### 🔧 Customize Your Server
- Edit `config/config.yaml` for server settings
- Modify `server.py` to add custom logic
- Add new tools by extending the backend class

### 📚 Learn More
- Read the full [Setup Guide](SETUP.md) for detailed instructions
- Check out [API Documentation](docs/API.md) for advanced usage
- Explore [Example Projects](examples/) for inspiration

### 🚀 Deploy Your Server
```bash
# Local deployment
python server.py

# Docker deployment (if Dockerfile generated)
docker build -t my-mcp-server .
docker run my-mcp-server

# Cloud deployment
mcp-setup deploy my-server --target cloud
```

---

## Troubleshooting

### ❌ Common Issues

#### Python Version Error
```bash
# Check Python version
python --version
# Must be 3.8 or higher

# Linux: sudo apt install python3.9
# macOS: brew install python@3.11
# Windows: Download from python.org
```

#### Permission Errors
```bash
# Don't use sudo with pip in virtual environments
# Recreate virtual environment if needed:
rm -rf mcp-env
python -m venv mcp-env
source mcp-env/bin/activate  # Linux/macOS
```

#### Import Errors
```bash
# Ensure virtual environment is activated
# Check if packages are installed:
pip list | grep mcp
```

#### Database Connection Issues
```bash
# Check database URL format:
# PostgreSQL: postgresql://user:password@host:port/database
# MySQL: mysql://user:password@host:port/database
# SQLite: sqlite:///path/to/database.db

# Test connection:
python -c "import psycopg2; print('PostgreSQL OK')"
```

### 🆘 Get Help
- 📖 [Detailed Setup Guide](SETUP.md)
- 🐛 [Report Issues](https://github.com/ModelContextKit/modelctx/issues)
- 💬 [Community Discussions](https://github.com/ModelContextKit/modelctx/discussions)
- 📧 Support: Create an issue for help

---

## Available Commands

```bash
# List all available backend types
mcp-setup list

# Create new project
mcp-setup create <name> --backend <type>

# Interactive project creation
mcp-setup wizard

# Manage templates
mcp-setup templates --list

# Generate documentation
mcp-setup docs <project-path>

# Deploy project (if configured)
mcp-setup deploy <project-name>

# Show help
mcp-setup --help
```

---

## Examples by Backend Type

### Database Backend
```bash
mcp-setup create inventory-db --backend database
# Use case: Inventory management system
# Tools: Query products, update stock, generate reports
```

### API Backend
```bash
mcp-setup create weather-api --backend api
# Use case: Weather data integration
# Tools: Get current weather, forecasts, alerts
```

### Filesystem Backend
```bash
mcp-setup create document-manager --backend filesystem
# Use case: Document management system
# Tools: Search documents, read content, organize files
```

### Web Scraper Backend
```bash
mcp-setup create news-scraper --backend webscraper
# Use case: News aggregation
# Tools: Scrape articles, extract headlines, get summaries
```

Ready to build amazing AI integrations? Start with `mcp-setup wizard`! 🚀