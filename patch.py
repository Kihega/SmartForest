#!/usr/bin/env python3
"""
Create the missing backend/src/config/database.js file
Usage: python3 patch.py
"""

import os

def create_database_config():
    file_path = 'backend/src/config/database.js'
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    content = '''// Database configuration and connection pool
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://localhost/smartforest'
});

module.exports = {
  query: (text, params) => pool.query(text, params),
  execute: (text, params) => pool.query(text, params),
  pool
};
'''
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Created {file_path}")
    print("   This file exports query/execute functions that Jest can mock")

if __name__ == '__main__':
    create_database_config()
