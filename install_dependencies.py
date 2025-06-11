"""
Script to install dependencies for all MCP servers
"""

import os
import subprocess
import sys

def install_dependencies(server_dir):
    """Install dependencies for a server"""
    req_file = os.path.join(server_dir, "requirements.txt")
    if os.path.exists(req_file):
        print(f"Installing dependencies for {os.path.basename(server_dir)}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
            print(f"Successfully installed dependencies for {os.path.basename(server_dir)}")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies for {os.path.basename(server_dir)}: {e}")
    else:
        print(f"No requirements.txt found in {server_dir}")

def main():
    """Main function"""
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp-servers")
    
    if not os.path.exists(base_dir):
        print(f"Directory not found: {base_dir}")
        return
    
    # Install common MCP dependencies
    print("Installing common MCP dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp>=1.0.0", "aiofiles"])
    
    # Install dependencies for each server
    for server_dir in os.listdir(base_dir):
        server_path = os.path.join(base_dir, server_dir)
        if os.path.isdir(server_path):
            install_dependencies(server_path)

if __name__ == "__main__":
    main()
