# MCP Quick Setup Tool - Installation & Usage Guide

> 🚀 Complete setup guide for Linux, macOS, and Windows

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Linux](#linux-installation)
  - [macOS](#macos-installation)
  - [Windows](#windows-installation)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Troubleshooting](#troubleshooting)
- [Platform-Specific Notes](#platform-specific-notes)

## Prerequisites

### Required Software
- **Python 3.8 or higher** (3.9+ recommended)
- **pip** (Python package installer)
- **Git** (for cloning and version control)

### Optional but Recommended
- **Virtual environment tools** (`venv`, `virtualenv`, or `conda`)
- **Node.js** (for MCP Inspector testing)
- **Docker** (for containerized deployment)

---

## Installation

### Linux Installation

#### Ubuntu/Debian
```bash
# Update package lists
sudo apt update

# Install Python 3.9+ and pip
sudo apt install python3.9 python3.9-pip python3.9-venv git

# Verify installation
python3 --version
pip3 --version

# Clone the MCP Setup Tool
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools

# Create virtual environment
python3 -m venv mcp-env
source mcp-env/bin/activate

# Install the tool
pip install -e .

# Verify installation
mcp-setup --version
```

#### CentOS/RHEL/Fedora
```bash
# For CentOS/RHEL 8+
sudo dnf install python3.9 python3.9-pip python3.9-venv git

# For older versions, use yum
sudo yum install python3 python3-pip git

# Clone and install (same as Ubuntu)
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools
python3 -m venv mcp-env
source mcp-env/bin/activate
pip install -e .
```

#### Arch Linux
```bash
# Install prerequisites
sudo pacman -S python python-pip git

# Clone and install
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools
python -m venv mcp-env
source mcp-env/bin/activate
pip install -e .
```

### macOS Installation

#### Using Homebrew (Recommended)
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Git
brew install python@3.11 git

# Verify installation
python3 --version
pip3 --version

# Clone the repository
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools

# Create virtual environment
python3 -m venv mcp-env
source mcp-env/bin/activate

# Install the tool
pip install -e .

# Verify installation
mcp-setup --version
```

#### Using Python.org Installer
```bash
# 1. Download Python 3.11+ from https://www.python.org/downloads/macos/
# 2. Install the downloaded package
# 3. Open Terminal and verify:
python3 --version

# Install Git if not present
xcode-select --install

# Clone and install
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools
python3 -m venv mcp-env
source mcp-env/bin/activate
pip install -e .
```

### Windows Installation

#### Using Python.org Installer (Recommended)
```powershell
# 1. Download Python 3.11+ from https://www.python.org/downloads/windows/
# 2. Run installer with "Add Python to PATH" checked
# 3. Open Command Prompt or PowerShell and verify:
python --version
pip --version

# Install Git from https://git-scm.com/download/win
# Or use winget:
winget install Git.Git

# Clone the repository
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools

# Create virtual environment
python -m venv mcp-env
mcp-env\Scripts\activate

# Install the tool
pip install -e .

# Verify installation
mcp-setup --version
```

#### Using Windows Subsystem for Linux (WSL)
```bash
# Install WSL2 and Ubuntu
wsl --install

# Follow Linux (Ubuntu) installation steps
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv git

# Clone and install
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools
python3 -m venv mcp-env
source mcp-env/bin/activate
pip install -e .
```

#### Using Conda (Cross-platform alternative)
```bash
# Install Miniconda or Anaconda
# Download from https://docs.conda.io/en/latest/miniconda.html

# Create conda environment
conda create -n mcp-env python=3.11
conda activate mcp-env

# Clone and install
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools
pip install -e .
```

---

## Quick Start

### 1. Basic Usage
```bash
# Activate virtual environment
# Linux/macOS:
source mcp-env/bin/activate
# Windows:
mcp-env\Scripts\activate

# List available backends
mcp-setup list

# Create your first MCP server (interactive wizard)
mcp-setup wizard

# Or create directly
mcp-setup create my-db-server --backend database
```

### 2. Example: Database MCP Server
```bash
# Create a database MCP server
mcp-setup create my-postgres-server --backend database

# Navigate to the project
cd my-postgres-server

# Configure environment variables
cp .env.template .env
# Edit .env with your database credentials

# Install project dependencies
pip install -r requirements.txt

# Test the server
python server.py

# Test with MCP Inspector (requires Node.js)
npx @modelcontextprotocol/inspector python server.py
```

### 3. Integration with Claude Desktop

#### Linux/macOS
```bash
# Find Claude Desktop config location
# Linux: ~/.config/Claude/claude_desktop_config.json
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json

# Copy generated config
cp config/claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json

# Or merge with existing config
```

#### Windows
```powershell
# Find Claude Desktop config location
# %APPDATA%\Claude\claude_desktop_config.json

# Copy generated config
copy config\claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
```

---

## Development Setup

### Setting up for Development
```bash
# Clone with development dependencies
git clone https://github.com/ModelContextKit/modelctx.git
cd mcp-setup-tools

# Create development environment
python -m venv dev-env
source dev-env/bin/activate  # Linux/macOS
# dev-env\Scripts\activate    # Windows

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
black .
ruff check .
mypy mcp_setup/
```

### Building and Testing
```bash
# Run full test suite
pytest tests/ -v

# Test specific backend
pytest tests/test_database_backend.py

# Generate coverage report
pytest --cov=mcp_setup tests/

# Build wheel
python -m build

# Test installation from wheel
pip install dist/mcp_setup_tool-*.whl
```

---

## Troubleshooting

### Common Issues

#### Python Version Issues
```bash
# Check Python version
python --version
# or
python3 --version

# If version is too old, install newer Python:
# Ubuntu/Debian: sudo apt install python3.11
# macOS: brew install python@3.11
# Windows: Download from python.org
```

#### Permission Errors (Linux/macOS)
```bash
# Don't use sudo with pip in virtual environments
# Instead, ensure virtual environment is activated:
source mcp-env/bin/activate

# If you see permission errors, recreate virtual environment:
rm -rf mcp-env
python3 -m venv mcp-env
source mcp-env/bin/activate
pip install -e .
```

#### Windows Path Issues
```powershell
# If 'python' command not found:
# 1. Reinstall Python with "Add to PATH" checked
# 2. Or add Python to PATH manually:
# Add: C:\Users\YourName\AppData\Local\Programs\Python\Python311
# Add: C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts

# Verify PATH:
echo $env:PATH
```

#### Virtual Environment Issues
```bash
# If virtual environment activation fails:

# Linux/macOS - try different shells:
source mcp-env/bin/activate      # bash/zsh
source mcp-env/bin/activate.csh  # csh
source mcp-env/bin/activate.fish # fish

# Windows - try different terminals:
mcp-env\Scripts\activate.bat     # Command Prompt
mcp-env\Scripts\Activate.ps1     # PowerShell
```

#### Database Connection Issues
```bash
# PostgreSQL connection test:
python -c "import psycopg2; print('PostgreSQL driver OK')"

# MySQL connection test:
python -c "import pymysql; print('MySQL driver OK')"

# SQLite test:
python -c "import sqlite3; print('SQLite OK')"

# If database drivers fail to install:
# Linux: sudo apt install libpq-dev python3-dev
# macOS: brew install postgresql
# Windows: Usually works out of the box
```

### Getting Help
```bash
# Show help for main command
mcp-setup --help

# Show help for specific commands
mcp-setup create --help
mcp-setup wizard --help

# Enable verbose output for debugging
mcp-setup create my-server --backend database --verbose
```

---

## Platform-Specific Notes

### Linux
- **Distributions**: Tested on Ubuntu 20.04+, Debian 11+, CentOS 8+, Fedora 35+
- **Dependencies**: May need `python3-dev` and `libpq-dev` for PostgreSQL
- **Permissions**: Never use `sudo` with pip in virtual environments
- **Systemd**: Can create systemd services for MCP servers

### macOS
- **Versions**: Tested on macOS 11+ (Big Sur and newer)
- **Architecture**: Works on both Intel and Apple Silicon (M1/M2)
- **Homebrew**: Recommended for dependency management
- **Xcode**: May need Command Line Tools for some dependencies

### Windows
- **Versions**: Tested on Windows 10 and Windows 11
- **PowerShell vs CMD**: Both work, PowerShell recommended
- **WSL**: Full Linux experience available via WSL2
- **Antivirus**: Some antivirus software may interfere with Python execution

### Performance Notes
- **SSD recommended** for development with many projects
- **RAM**: 4GB minimum, 8GB+ recommended for development
- **CPU**: Any modern processor sufficient
- **Network**: Required for package installation and database connections

---

## Next Steps

After successful installation:

1. **Create your first MCP server** with `mcp-setup wizard`
2. **Read the generated README.md** in your project directory
3. **Configure environment variables** in the `.env` file
4. **Test with MCP Inspector** to verify functionality
5. **Integrate with Claude Desktop** using the generated config
6. **Explore advanced backends** like API, filesystem, and web scraper

For more detailed documentation, see:
- [API Documentation](docs/API.md)
- [Backend Development Guide](docs/BACKENDS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guide](CONTRIBUTING.md)

---

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/ModelContextKit/modelctx/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ModelContextKit/modelctx/discussions)
- 📚 **Documentation**: [GitHub Wiki](https://github.com/ModelContextKit/modelctx/wiki)
- 📧 **Support**: Create an issue for help