"""Script generation for MCP servers."""

import os
from pathlib import Path


class ScriptGenerator:
    """Generates setup and deployment scripts for MCP projects."""
    
    def __init__(self, project_path: Path, project_name: str):
        self.project_path = project_path
        self.project_name = project_name
    
    def generate_scripts(self) -> None:
        """Generate all project scripts."""
        self._generate_setup_script()
        self._generate_deploy_script()
    
    def _generate_setup_script(self) -> None:
        """Generate setup.sh script."""
        setup_script = f'''#!/bin/bash
# Setup script for {self.project_name}

echo "Setting up {self.project_name}..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
if [ ! -f .env ]; then
    cp .env.template .env
    echo "Please edit .env file with your configuration"
fi

echo "Setup completed!"
echo "Activate virtual environment with: source venv/bin/activate"
echo "Run server with: python server.py"
'''
        setup_path = self.project_path / "scripts" / "setup.sh"
        with open(setup_path, 'w', encoding='utf-8') as f:
            f.write(setup_script)
        setup_path.chmod(0o755)
    
    def _generate_deploy_script(self) -> None:
        """Generate deploy.sh script."""
        deploy_script = f'''#!/bin/bash
# Deployment script for {self.project_name}

echo "Deploying {self.project_name}..."

# Run tests
python -m pytest tests/

# Build if needed
# docker build -t {self.project_name} .

echo "Deployment completed!"
'''
        deploy_path = self.project_path / "scripts" / "deploy.sh"
        with open(deploy_path, 'w', encoding='utf-8') as f:
            f.write(deploy_script)
        deploy_path.chmod(0o755)