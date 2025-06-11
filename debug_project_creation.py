#!/usr/bin/env python3
"""Debug project creation."""

import sys
from pathlib import Path
import traceback
import tempfile

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_project_creation():
    """Test project creation with detailed error reporting."""
    print("🔍 Testing project creation...")
    
    try:
        from modelctx.core.generator import ProjectGenerator
        from modelctx.core.config import ProjectConfig
        from modelctx.backends.base import BackendConfig
        
        print("✓ Imports successful")
        
        # Create project generator
        generator = ProjectGenerator(
            project_name="test-project",
            backend_type="api",
            output_dir="/tmp",
            verbose=True
        )
        print("✓ Generator created")
        
        # Create basic config
        backend_config = BackendConfig(
            backend_type="api",
            project_name="test-project",
            description="Test API MCP server",
            dependencies=["httpx>=0.24.0"],
            parameters={
                "base_url": "https://api.example.com",
                "auth_type": "bearer",
                "rate_limit_requests_per_minute": 60,
                "request_timeout": 30
            }
        )
        
        config = ProjectConfig(
            project_name="test-project",
            backend_type="api",
            description="Test API MCP server",
            backend_config=backend_config
        )
        
        generator.set_config(config)
        print("✓ Config set")
        
        # Test the problematic part - getting init code
        print("Testing init code generation...")
        init_code = generator.backend_instance.get_init_code()
        print("✓ Init code generated successfully")
        print("First 500 chars of init code:")
        print(init_code[:500])
        
        # Try generating the project
        print("\nGenerating project...")
        generator.generate()
        print("✓ Project generation completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_project_creation()