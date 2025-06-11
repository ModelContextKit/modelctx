# ModelContextKit - Windows PowerShell Installation Script

param(
    [switch]$NoNodeJS,
    [switch]$Force,
    [string]$InstallPath = "$env:USERPROFILE\modelctx"
)

# Script configuration
$ErrorActionPreference = "Stop"
$PythonMinVersion = [Version]"3.8.0"
$RepoUrl = "https://github.com/ModelContextKit/modelctx.git"
$VenvName = "modelctx-env"

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    White = "White"
}

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Colors.Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Colors.Red
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-PythonVersion {
    param([string]$PythonExe)
    try {
        $versionOutput = & $PythonExe --version 2>&1
        if ($versionOutput -match "Python (\d+\.\d+\.\d+)") {
            $version = [Version]$matches[1]
            return $version -ge $PythonMinVersion
        }
        return $false
    }
    catch {
        return $false
    }
}

function Find-Python {
    Write-Status "Searching for Python $PythonMinVersion or higher..."
    
    # Try different Python commands
    $pythonCommands = @("python", "python3", "py")
    
    foreach ($cmd in $pythonCommands) {
        if (Test-Command $cmd) {
            if (Test-PythonVersion $cmd) {
                $version = & $cmd --version 2>&1
                Write-Success "Found Python: $cmd ($version)"
                return $cmd
            }
        }
    }
    
    # Try Python Launcher with specific versions
    if (Test-Command "py") {
        $versions = @("-3.11", "-3.10", "-3.9", "-3.8")
        foreach ($ver in $versions) {
            try {
                $versionCheck = & py $ver --version 2>&1
                if ($versionCheck -match "Python (\d+\.\d+\.\d+)") {
                    $version = [Version]$matches[1]
                    if ($version -ge $PythonMinVersion) {
                        Write-Success "Found Python: py $ver ($versionCheck)"
                        return "py $ver"
                    }
                }
            }
            catch {
                continue
            }
        }
    }
    
    return $null
}

function Install-Python {
    Write-Warning "Python $PythonMinVersion or higher not found."
    Write-Status "You can install Python from:"
    Write-Host "  1. Microsoft Store: " -NoNewline
    Write-Host "ms-windows-store://pdp/?ProductId=9NRWMJP3717K" -ForegroundColor $Colors.Blue
    Write-Host "  2. Python.org: " -NoNewline
    Write-Host "https://www.python.org/downloads/windows/" -ForegroundColor $Colors.Blue
    Write-Host "  3. Winget: " -NoNewline
    Write-Host "winget install Python.Python.3.11" -ForegroundColor $Colors.Blue
    
    $choice = Read-Host "Would you like to install Python 3.11 via winget? (y/n)"
    if ($choice -eq "y" -or $choice -eq "Y") {
        try {
            if (Test-Command "winget") {
                Write-Status "Installing Python 3.11 via winget..."
                winget install Python.Python.3.11 --silent
                
                # Refresh PATH
                $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::Machine) + ";" + [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::User)
                
                Write-Success "Python installation completed!"
                return Find-Python
            }
            else {
                Write-Error "winget not available. Please install Python manually."
                return $null
            }
        }
        catch {
            Write-Error "Failed to install Python via winget: $_"
            return $null
        }
    }
    else {
        Write-Status "Please install Python manually and re-run this script."
        return $null
    }
}

function Test-Git {
    if (Test-Command "git") {
        $version = git --version
        Write-Success "Git is available: $version"
        return $true
    }
    else {
        Write-Warning "Git not found."
        Write-Status "You can install Git from:"
        Write-Host "  1. Git website: " -NoNewline
        Write-Host "https://git-scm.com/download/win" -ForegroundColor $Colors.Blue
        Write-Host "  2. Winget: " -NoNewline
        Write-Host "winget install Git.Git" -ForegroundColor $Colors.Blue
        
        $choice = Read-Host "Would you like to install Git via winget? (y/n)"
        if ($choice -eq "y" -or $choice -eq "Y") {
            try {
                if (Test-Command "winget") {
                    Write-Status "Installing Git via winget..."
                    winget install Git.Git --silent
                    
                    # Refresh PATH
                    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::Machine) + ";" + [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::User)
                    
                    Write-Success "Git installation completed!"
                    return $true
                }
                else {
                    Write-Error "winget not available. Please install Git manually."
                    return $false
                }
            }
            catch {
                Write-Error "Failed to install Git via winget: $_"
                return $false
            }
        }
        else {
            Write-Status "Please install Git manually and re-run this script."
            return $false
        }
    }
}

function Install-NodeJS {
    if (Test-Command "node") {
        $version = node --version
        Write-Success "Node.js is available: $version"
        return
    }
    
    if (-not $NoNodeJS) {
        $choice = Read-Host "Install Node.js for MCP Inspector testing? (y/n)"
        if ($choice -eq "y" -or $choice -eq "Y") {
            try {
                if (Test-Command "winget") {
                    Write-Status "Installing Node.js via winget..."
                    winget install OpenJS.NodeJS --silent
                    
                    # Refresh PATH
                    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::Machine) + ";" + [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::User)
                    
                    Write-Success "Node.js installation completed!"
                }
                else {
                    Write-Warning "winget not available. Please install Node.js manually from https://nodejs.org/"
                }
            }
            catch {
                Write-Warning "Failed to install Node.js via winget. You can install it manually later."
            }
        }
    }
}

function Initialize-Repository {
    Write-Status "Setting up ModelContextKit repository..."
    
    # Remove existing directory if it exists
    if (Test-Path $InstallPath) {
        if ($Force) {
            Write-Warning "Removing existing installation at $InstallPath..."
            Remove-Item -Path $InstallPath -Recurse -Force
        }
        else {
            Write-Error "Directory $InstallPath already exists. Use -Force to overwrite."
            exit 1
        }
    }
    
    # Create parent directory if it doesn't exist
    $parentDir = Split-Path $InstallPath -Parent
    if (-not (Test-Path $parentDir)) {
        New-Item -Path $parentDir -ItemType Directory -Force | Out-Null
    }
    
    # Clone repository
    Write-Status "Cloning repository from $RepoUrl..."
    git clone $RepoUrl $InstallPath
    
    Write-Success "Repository cloned to $InstallPath"
}

function Install-ModelContextKit {
    param([string]$PythonCmd)
    
    Write-Status "Installing ModelContextKit..."
    
    # Change to installation directory
    Set-Location $InstallPath
    
    # Create virtual environment
    Write-Status "Creating virtual environment..."
    $pythonArgs = @("-m", "venv", $VenvName)
    if ($PythonCmd.Contains(" ")) {
        # Handle "py -3.11" style commands
        $parts = $PythonCmd.Split(" ")
        & $parts[0] $parts[1..($parts.Length-1)] $pythonArgs
    }
    else {
        & $PythonCmd $pythonArgs
    }
    
    # Activate virtual environment
    $activateScript = Join-Path $InstallPath "$VenvName\Scripts\Activate.ps1"
    
    # Check if activation script exists and set execution policy
    if (Test-Path $activateScript) {
        try {
            # Set execution policy for current user if needed
            $currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
            if ($currentPolicy -eq "Restricted") {
                Write-Status "Setting PowerShell execution policy to RemoteSigned for current user..."
                Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
            }
            
            Write-Status "Activating virtual environment..."
            & $activateScript
        }
        catch {
            Write-Warning "Failed to activate virtual environment with PowerShell script. Using fallback method."
            # Fallback: modify PATH directly
            $venvScripts = Join-Path $InstallPath "$VenvName\Scripts"
            $env:PATH = "$venvScripts;$env:PATH"
            $env:VIRTUAL_ENV = Join-Path $InstallPath $VenvName
        }
    }
    
    # Use pip from virtual environment
    $pipPath = Join-Path $InstallPath "$VenvName\Scripts\pip.exe"
    
    # Upgrade pip
    Write-Status "Upgrading pip..."
    & $pipPath install --upgrade pip
    
    # Install the tool
    Write-Status "Installing ModelContextKit and dependencies..."
    & $pipPath install -e .
    
    Write-Success "ModelContextKit installed successfully!"
}

function New-ActivationScript {
    $scriptPath = Join-Path $InstallPath "activate_modelctx.ps1"
    
    $scriptContent = @"
# ModelContextKit Activation Script for Windows PowerShell

Push-Location "$InstallPath"

# Activate virtual environment
`$activateScript = ".\$VenvName\Scripts\Activate.ps1"
if (Test-Path `$activateScript) {
    try {
        & `$activateScript
    }
    catch {
        # Fallback method
        `$venvScripts = ".\$VenvName\Scripts"
        `$env:PATH = "`$venvScripts;`$env:PATH"
        `$env:VIRTUAL_ENV = ".\$VenvName"
    }
}

Write-Host "🚀 ModelContextKit environment activated!" -ForegroundColor Green
Write-Host "📍 Location: $InstallPath" -ForegroundColor Blue
Write-Host "🐍 Python: `$(python --version)" -ForegroundColor Blue
Write-Host "🔧 ModelContextKit: `$(modelctx --version)" -ForegroundColor Blue
Write-Host ""
Write-Host "Usage examples:" -ForegroundColor Yellow
Write-Host "  modelctx list                    # List available backends"
Write-Host "  modelctx wizard                  # Interactive project creation"
Write-Host "  modelctx create my-db --backend database"
Write-Host ""
Write-Host "To deactivate: deactivate"
"@
    
    Set-Content -Path $scriptPath -Value $scriptContent
    Write-Success "Activation script created: $scriptPath"
}

function Test-Installation {
    Write-Status "Testing installation..."
    
    # Change to installation directory and test
    Set-Location $InstallPath
    
    # Test using the pip installation path
    $modelctxPath = Join-Path $InstallPath "$VenvName\Scripts\modelctx.exe"
    
    try {
        $version = & $modelctxPath --version 2>&1
        Write-Success "Installation test passed!"
        Write-Status "Installed version: $version"
        
        # List backends
        Write-Status "Available backends:"
        & $modelctxPath list
    }
    catch {
        Write-Error "Installation test failed: $_"
        Write-Status "Trying alternative test method..."
        
        # Alternative: activate environment and try again
        try {
            $activateScript = ".\$VenvName\Scripts\Activate.ps1"
            & $activateScript
            modelctx --version
            Write-Success "Installation test passed with activated environment!"
        }
        catch {
            Write-Error "Installation verification failed. Please check the installation manually."
            exit 1
        }
    }
}

function Show-Instructions {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                    🎉 Installation Complete! 🎉                ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Success "ModelContextKit has been installed successfully!"
    Write-Host ""
    Write-Host "📍 Installation directory: $InstallPath" -ForegroundColor Blue
    Write-Host "🐍 Virtual environment: $InstallPath\$VenvName" -ForegroundColor Blue
    Write-Host ""
    Write-Host "🚀 To get started:" -ForegroundColor Yellow
    Write-Host "   1. Activate the environment:" -ForegroundColor White
    Write-Host "      . $InstallPath\activate_modelctx.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   2. Create your first MCP server with ModelContextKit:" -ForegroundColor White
    Write-Host "      modelctx wizard" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   3. Or create directly:" -ForegroundColor White
    Write-Host "      modelctx create my-project --backend apidatabase" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📚 Documentation:" -ForegroundColor Yellow
    Write-Host "   • Setup Guide: $InstallPath\SETUP.md" -ForegroundColor White
    Write-Host "   • Examples: $InstallPath\examples\" -ForegroundColor White
    Write-Host "   • Documentation: https://github.com/ModelContextKit/modelctx/wiki" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Pro tip: Add this to your PowerShell profile for easy access:" -ForegroundColor Yellow
    Write-Host "   function modelctx-activate { . $InstallPath\activate_modelctx.ps1 }" -ForegroundColor Cyan
    Write-Host ""
}

# Main installation function
function Main {
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║          ModelContextKit - Windows Installation              ║" -ForegroundColor Blue
    Write-Host "║                                                                ║" -ForegroundColor Blue
    Write-Host "║  This script will install ModelContextKit and all            ║" -ForegroundColor Blue
    Write-Host "║  required dependencies on your Windows system.                ║" -ForegroundColor Blue
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
    
    # Check prerequisites
    Write-Status "Checking prerequisites..."
    
    # Check Git
    if (-not (Test-Git)) {
        Write-Error "Git is required but not available. Please install Git and re-run this script."
        exit 1
    }
    
    # Check Python
    $pythonCmd = Find-Python
    if (-not $pythonCmd) {
        $pythonCmd = Install-Python
        if (-not $pythonCmd) {
            Write-Error "Python installation failed or was cancelled."
            exit 1
        }
    }
    
    # Check Node.js (optional)
    Install-NodeJS
    
    # Initialize repository
    Initialize-Repository
    
    # Install the tool
    Install-ModelContextKit $pythonCmd
    
    # Create activation script
    New-ActivationScript
    
    # Test installation
    Test-Installation
    
    # Show final instructions
    Show-Instructions
}

# Handle Ctrl+C gracefully
trap {
    Write-Host ""
    Write-Warning "Installation cancelled by user."
    exit 1
}

# Check if running as administrator (warn but don't block)
$currentUser = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
$adminRole = [Security.Principal.WindowsBuiltInRole]::Administrator
$isAdmin = $currentUser.IsInRole($adminRole)

if ($isAdmin) {
    Write-Warning "Running as Administrator is not necessary and not recommended."
    $continue = Read-Host "Continue anyway? (y/n)"
    
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Status "Installation cancelled."
        exit 1
    }
}

# Run main installation
try {
    Main
}
catch {
    Write-Error "Installation failed: $_"
    Write-Status "Please check the error message above and try again."
    Write-Status "For manual installation instructions, see SETUP.md"
    exit 1
}