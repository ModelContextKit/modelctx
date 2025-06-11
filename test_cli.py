#!/usr/bin/env python3
"""Test script for the CLI functionality."""

import sys
import os
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_backend_imports():
    """Test that all backends can be imported."""
    print("Testing backend imports...")
    try:
        from modelctx.backends import AVAILABLE_BACKENDS
        print(f"✓ Successfully imported {len(AVAILABLE_BACKENDS)} backends:")
        for name in AVAILABLE_BACKENDS.keys():
            print(f"  - {name}")
        return True
    except Exception as e:
        print(f"✗ Backend import failed: {e}")
        return False

def test_cli_import():
    """Test that CLI can be imported without execution."""
    print("\nTesting CLI import...")
    try:
        # Save original argv
        original_argv = sys.argv[:]
        sys.argv = ['test']  # Set minimal argv
        
        from modelctx.cli import cli
        print("✓ CLI imported successfully")
        
        # Restore argv
        sys.argv = original_argv
        return True
    except Exception as e:
        print(f"✗ CLI import failed: {e}")
        sys.argv = original_argv
        return False

def test_core_imports():
    """Test core module imports."""
    print("\nTesting core module imports...")
    try:
        from modelctx.core.generator import ProjectGenerator
        from modelctx.core.config import ConfigWizard, ProjectConfig
        print("✓ Core modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Core module import failed: {e}")
        return False

def test_validation():
    """Test validation functions."""
    print("\nTesting validation...")
    try:
        from modelctx.utils.validation import validate_project_name
        
        # Test valid names
        valid_names = ["my-project", "test_server", "api123", "a"]
        for name in valid_names:
            if not validate_project_name(name):
                print(f"✗ Valid name '{name}' failed validation")
                return False
        
        # Test invalid names
        invalid_names = ["", "-invalid", "invalid-", "a" * 51, "invalid name"]
        for name in invalid_names:
            if validate_project_name(name):
                print(f"✗ Invalid name '{name}' passed validation")
                return False
        
        print("✓ Validation functions work correctly")
        return True
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing MCP Setup Tool Components\n")
    
    tests = [
        test_backend_imports,
        test_core_imports,
        test_validation,
        test_cli_import,
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The MCP Setup Tool is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())