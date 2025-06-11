@echo off
REM MCP Quick Setup Tool - Windows Batch Installation Script
REM This is a simple wrapper that calls the PowerShell installation script

setlocal enabledelayedexpansion

echo.
echo ===============================================================================
echo                MCP Quick Setup Tool - Windows Installation
echo ===============================================================================
echo.
echo This script will install the MCP Quick Setup Tool on your Windows system.
echo.

REM Check if PowerShell is available
powershell -Command "Get-Host" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is not available or not accessible.
    echo Please ensure PowerShell is installed and try again.
    echo.
    echo Alternatively, you can follow the manual installation instructions in SETUP.md
    pause
    exit /b 1
)

REM Check execution policy
for /f "tokens=*" %%i in ('powershell -Command "Get-ExecutionPolicy"') do set EXEC_POLICY=%%i

if "%EXEC_POLICY%"=="Restricted" (
    echo WARNING: PowerShell execution policy is set to Restricted.
    echo This may prevent the installation script from running.
    echo.
    echo You can change this by running PowerShell as Administrator and executing:
    echo Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    echo.
    set /p CONTINUE="Continue with installation anyway? (y/n): "
    if /i not "!CONTINUE!"=="y" (
        echo Installation cancelled.
        pause
        exit /b 1
    )
)

echo Starting PowerShell installation script...
echo.

REM Run the PowerShell installation script
powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*

if errorlevel 1 (
    echo.
    echo ERROR: PowerShell installation script failed.
    echo.
    echo Troubleshooting tips:
    echo 1. Ensure you have internet connectivity
    echo 2. Check that Python 3.8+ is installed
    echo 3. Verify that Git is installed
    echo 4. Try running the PowerShell script directly:
    echo    powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"
    echo.
    echo For manual installation, see SETUP.md
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo Run the activation script to get started:
echo.
echo    %USERPROFILE%\mcp-setup-tool\activate_mcp.ps1
echo.
pause