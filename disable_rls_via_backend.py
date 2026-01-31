#!/usr/bin/env python3
"""Disable RLS via backend API (if backend has admin access)"""

import requests
import json

API_URL = "https://21day.club/api"

def execute_sql_via_backend(sql_commands):
    """Try to execute SQL via backend admin endpoint"""
    # This would require a special admin endpoint in backend
    # For now, we'll create instructions for manual execution
    
    print("=" * 60)
    print("TEMPORARY SOLUTION: Disable RLS")
    print("=" * 60)
    print()
    print("WARNING: This is a TEMPORARY solution for quick startup.")
    print("   For production, use SECURITY DEFINER functions or proper RLS policies.")
    print()
    print("=" * 60)
    print("INSTRUCTIONS:")
    print("=" * 60)
    print()
    print("Option 1: Execute SQL via Timeweb Control Panel")
    print("1. Log in to Timeweb Control Panel")
    print("2. Go to Databases -> PostgreSQL")
    print("3. Select database 'db_21day'")
    print("4. Open SQL Console")
    print("5. Execute the SQL commands from 'disable_rls_temporary.sql'")
    print()
    print("Option 2: Grant CONNECT privilege first")
    print("Ask Timeweb support to grant CONNECT privilege to gen_user")
    print("Then run: python disable_rls.py")
    print()
    print("Option 3: Execute via backend (if admin endpoint exists)")
    print("Create an admin endpoint in backend that can execute SQL")
    print()
    print("=" * 60)
    print("SQL COMMANDS TO EXECUTE:")
    print("=" * 60)
    print()
    
    with open("disable_rls_temporary.sql", "r", encoding="utf-8") as f:
        print(f.read())

if __name__ == "__main__":
    execute_sql_via_backend(None)

