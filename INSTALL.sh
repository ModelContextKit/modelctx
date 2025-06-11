#!/bin/bash

# ModelContextKit - Automated Installation Script
# Supports Linux and macOS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
PYTHON_MIN_VERSION="3.8"
REPO_URL="https://github.com/ModelContextKit/modelctx.git"
INSTALL_DIR="$HOME/modelctx"
VENV_NAME="modelctx-env"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare version numbers
version_compare() {
    local version1=$1
    local version2=$2
    
    # Convert versions to comparable format
    v1=$(echo "$version1" | sed 's/[^0-9.]//g')
    v2=$(echo "$version2" | sed 's/[^0-9.]//g')
    
    # Compare versions
    if [ "$(printf '%s\n' "$v1" "$v2" | sort -V | head -n1)" = "$v1" ]; then
        if [ "$v1" != "$v2" ]; then
            return 1  # v1 < v2
        else
            return 0  # v1 == v2
        fi
    else
        return 0  # v1 > v2
    fi
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Function to detect Linux distribution
detect_linux_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/redhat-release ]; then
        echo "rhel"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

# Function to install Python on Linux
install_python_linux() {
    local distro=$(detect_linux_distro)
    
    print_status "Installing Python 3.9+ on Linux ($distro)..."
    
    case $distro in
        "ubuntu"|"debian")
            sudo apt update
            sudo apt install -y python3.9 python3.9-pip python3.9-venv python3.9-dev
            ;;
        "fedora")
            sudo dnf install -y python3.9 python3.9-pip python3.9-devel
            ;;
        "centos"|"rhel")
            sudo dnf install -y python39 python39-pip python39-devel
            ;;
        "arch"|"manjaro")
            sudo pacman -S python python-pip
            ;;
        *)
            print_error "Unsupported Linux distribution: $distro"
            print_status "Please install Python 3.9+ manually and re-run this script"
            exit 1
            ;;
    esac
}

# Function to install Python on macOS
install_python_macos() {
    print_status "Installing Python 3.9+ on macOS..."
    
    if command_exists brew; then
        print_status "Using Homebrew to install Python..."
        brew install python@3.11
    else
        print_warning "Homebrew not found."
        print_status "Please install Python 3.9+ from https://www.python.org/downloads/macos/"
        print_status "Or install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
}

# Function to check and install Python
check_python() {
    local python_cmd=""
    
    # Try different Python commands
    for cmd in python3.11 python3.10 python3.9 python3 python; do
        if command_exists $cmd; then
            local version=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
            if version_compare "$version" "$PYTHON_MIN_VERSION"; then
                python_cmd=$cmd
                break
            fi
        fi
    done
    
    if [ -z "$python_cmd" ]; then
        print_warning "Python $PYTHON_MIN_VERSION or higher not found."
        
        local os=$(detect_os)
        case $os in
            "linux")
                install_python_linux
                ;;
            "macos")
                install_python_macos
                ;;
            *)
                print_error "Unsupported operating system: $os"
                exit 1
                ;;
        esac
        
        # Re-check after installation
        for cmd in python3.11 python3.10 python3.9 python3 python; do
            if command_exists $cmd; then
                local version=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
                if version_compare "$version" "$PYTHON_MIN_VERSION"; then
                    python_cmd=$cmd
                    break
                fi
            fi
        done
        
        if [ -z "$python_cmd" ]; then
            print_error "Failed to install Python. Please install manually."
            exit 1
        fi
    fi
    
    print_success "Found Python: $python_cmd ($($python_cmd --version))"
    echo "$python_cmd"
}

# Function to check and install Git
check_git() {
    if ! command_exists git; then
        print_warning "Git not found. Installing..."
        
        local os=$(detect_os)
        case $os in
            "linux")
                local distro=$(detect_linux_distro)
                case $distro in
                    "ubuntu"|"debian")
                        sudo apt install -y git
                        ;;
                    "fedora"|"centos"|"rhel")
                        sudo dnf install -y git
                        ;;
                    "arch"|"manjaro")
                        sudo pacman -S git
                        ;;
                    *)
                        print_error "Please install Git manually for your distribution"
                        exit 1
                        ;;
                esac
                ;;
            "macos")
                if command_exists brew; then
                    brew install git
                else
                    print_status "Installing Xcode Command Line Tools (includes Git)..."
                    xcode-select --install
                fi
                ;;
            *)
                print_error "Please install Git manually for your operating system"
                exit 1
                ;;
        esac
    fi
    
    print_success "Git is available: $(git --version)"
}

# Function to install Node.js (optional, for MCP Inspector)
install_nodejs() {
    if ! command_exists node; then
        print_status "Node.js not found. Installing for MCP Inspector support..."
        
        local os=$(detect_os)
        case $os in
            "linux")
                # Install Node.js via NodeSource
                curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                sudo apt-get install -y nodejs
                ;;
            "macos")
                if command_exists brew; then
                    brew install node
                else
                    print_warning "Please install Node.js manually from https://nodejs.org/"
                fi
                ;;
        esac
    else
        print_success "Node.js is available: $(node --version)"
    fi
}

# Function to create directory and clone repository
setup_repository() {
    print_status "Setting up ModelContextKit repository..."
    
    # Remove existing directory if it exists
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Directory $INSTALL_DIR already exists. Removing..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Clone repository
    print_status "Cloning repository from $REPO_URL..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    
    # Change to installation directory
    cd "$INSTALL_DIR"
    
    print_success "Repository cloned to $INSTALL_DIR"
}

# Function to create virtual environment and install
install_modelctx() {
    local python_cmd=$1
    
    print_status "Creating virtual environment..."
    
    # Create virtual environment
    $python_cmd -m venv "$VENV_NAME"
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install the tool
    print_status "Installing ModelContextKit..."
    pip install -e .
    
    print_success "ModelContextKit installed successfully!"
}

# Function to create activation script
create_activation_script() {
    local script_path="$INSTALL_DIR/activate_modelctx.sh"
    
    cat > "$script_path" << EOF
#!/bin/bash
# ModelContextKit Activation Script

cd "$INSTALL_DIR"
source "$VENV_NAME/bin/activate"

echo "🚀 ModelContextKit environment activated!"
echo "📍 Location: $INSTALL_DIR"
echo "🐍 Python: \$(python --version)"
echo "🔧 ModelContextKit: \$(modelctx --version)"
echo ""
echo "Usage examples:"
echo "  modelctx list                    # List available backends"
echo "  modelctx wizard                  # Interactive project creation"
echo "  modelctx create my-db --backend database"
echo ""
echo "To deactivate: deactivate"
EOF
    
    chmod +x "$script_path"
    
    print_success "Activation script created: $script_path"
}

# Function to test installation
test_installation() {
    print_status "Testing installation..."
    
    # Activate environment
    source "$VENV_NAME/bin/activate"
    
    # Test command
    if modelctx --version >/dev/null 2>&1; then
        print_success "Installation test passed!"
        
        # Show version
        local version=$(modelctx --version)
        print_status "Installed version: $version"
        
        # List backends
        print_status "Available backends:"
        mcp-setup list
    else
        print_error "Installation test failed!"
        exit 1
    fi
}

# Function to show post-installation instructions
show_instructions() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 Installation Complete! 🎉                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    print_success "MCP Quick Setup Tool has been installed successfully!"
    echo ""
    echo "📍 Installation directory: $INSTALL_DIR"
    echo "🐍 Virtual environment: $INSTALL_DIR/$VENV_NAME"
    echo ""
    echo "🚀 To get started:"
    echo "   1. Activate the environment:"
    echo "      source $INSTALL_DIR/activate_mcp.sh"
    echo ""
    echo "   2. Create your first MCP server:"
    echo "      mcp-setup wizard"
    echo ""
    echo "   3. Or create directly:"
    echo "      mcp-setup create my-server --backend database"
    echo ""
    echo "📚 Documentation:"
    echo "   • Setup Guide: $INSTALL_DIR/SETUP.md"
    echo "   • Examples: $INSTALL_DIR/examples/"
    echo "   • Documentation: https://github.com/ModelContextKit/modelctx/wiki"
    echo ""
    echo "💡 Pro tip: Add this to your ~/.bashrc or ~/.zshrc for easy access:"
    echo "   alias mcp-activate='source $INSTALL_DIR/activate_mcp.sh'"
    echo ""
}

# Main installation function
main() {
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║            MCP Quick Setup Tool - Installation Script          ║"
    echo "║                                                                ║"
    echo "║  This script will install the MCP Quick Setup Tool and all    ║"
    echo "║  required dependencies on your system.                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Check operating system
    local os=$(detect_os)
    print_status "Detected operating system: $os"
    
    if [ "$os" = "unknown" ]; then
        print_error "Unsupported operating system. This script supports Linux and macOS only."
        print_status "For Windows, please use the manual installation instructions in SETUP.md"
        exit 1
    fi
    
    # Check for required tools and install if missing
    print_status "Checking prerequisites..."
    
    check_git
    local python_cmd=$(check_python)
    
    # Optional: Install Node.js for MCP Inspector
    if command_exists node; then
        print_success "Node.js is available for MCP Inspector testing"
    else
        read -p "Install Node.js for MCP Inspector testing? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_nodejs
        else
            print_warning "Skipping Node.js installation. You can install it later for MCP Inspector testing."
        fi
    fi
    
    # Setup repository
    setup_repository
    
    # Install the tool
    install_modelctx "$python_cmd"
    
    # Create activation script
    create_activation_script
    
    # Test installation
    test_installation
    
    # Show final instructions
    show_instructions
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Installation cancelled by user.${NC}"; exit 1' INT

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root is not recommended."
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installation cancelled."
        exit 1
    fi
fi

# Run main installation
main "$@"