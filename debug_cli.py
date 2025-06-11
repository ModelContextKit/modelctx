#!/usr/bin/env python3
"""Debug CLI to identify the issue."""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Original sys.argv:", sys.argv)

# Try importing components one by one
print("\n1. Testing backend import...")
try:
    from modelctx.backends import AVAILABLE_BACKENDS
    print(f"✓ Backends imported: {list(AVAILABLE_BACKENDS.keys())}")
    print("sys.argv after backend import:", sys.argv)
except Exception as e:
    print("✗ Backend import failed:", e)

print("\n2. Testing Click import...")
try:
    import click
    print("✓ Click imported")
    print("sys.argv after click import:", sys.argv)
except Exception as e:
    print("✗ Click import failed:", e)

print("\n3. Testing CLI module import...")
try:
    # Reset sys.argv to something clean
    sys.argv = ['debug_cli']
    print("Reset sys.argv to:", sys.argv)
    
    # Now try importing the CLI
    from modelctx.cli import cli
    print("✓ CLI imported successfully!")
    
except Exception as e:
    print("✗ CLI import failed:", e)
    import traceback
    traceback.print_exc()