#!/usr/bin/env python3
"""
Fix jest.setup.js module path issues
Usage: python3 patch.py
"""

import os
import sys

def fix_jest_setup():
    file_path = 'backend/jest.setup.js'
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found")
        sys.exit(1)
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    print("Current jest.setup.js content (first 10 lines):")
    print("=" * 60)
    lines = content.split('\n')[:10]
    for i, line in enumerate(lines, 1):
        print(f"{i}: {line}")
    print("=" * 60)
    
    # Check for various patterns
    patterns = [
        ("./src/config/db", "./src/config/database"),
        ("./src/config/database'", "./src/config/database'"),
    ]
    
    fixed = False
    for old_pattern, new_pattern in patterns:
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print(f"✅ Fixed: '{old_pattern}' → '{new_pattern}'")
            fixed = True
    
    if not fixed:
        print("⚠️  No patterns matching './src/config/db' or './src/config/database' found")
        print("\nLooking for any jest.mock lines:")
        for i, line in enumerate(lines, 1):
            if 'jest.mock' in line:
                print(f"Line {i}: {line}")
        sys.exit(0)
    
    # Write the file back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"\n✅ Successfully updated: {file_path}")

if __name__ == '__main__':
    fix_jest_setup()
