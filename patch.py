#!/usr/bin/env python3
"""
Fix jest.setup.js by removing the non-existent database module mock
Usage: python3 patch.py
"""

import os

def fix_jest_setup():
    file_path = 'backend/jest.setup.js'
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Remove lines 55-58 (the database mock that references non-existent module)
    # Keep everything else
    new_lines = []
    skip_until_line = None
    
    for i, line in enumerate(lines, 1):
        # Skip the database mock block (lines 55-58)
        if i >= 55 and i <= 58:
            continue
        new_lines.append(line)
    
    with open(file_path, 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Removed non-existent database mock from jest.setup.js")
    print("Lines 55-58 deleted (jest.mock('./src/config/database', ...))")

if __name__ == '__main__':
    fix_jest_setup()
