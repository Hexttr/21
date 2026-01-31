#!/usr/bin/env python3
"""Disable RLS via Supabase Management API or CLI"""

import requests
import subprocess
import os

# Supabase credentials
SUPABASE_URL = "https://uyymukgccsqzagpusswm.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV5eW11a2djY3NxemFncHVzc3dtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgxNTIzMDksImV4cCI6MjA4MzcyODMwOX0.IkUJbJPXO5zNuB-9oEZs0v38zHYrkoSc1ofniHSJM9M"
SUPABASE_PROJECT_ID = "uyymukgccsqzagpusswm"

def disable_rls_via_cli():
    """Try to disable RLS using Supabase CLI"""
    print("=" * 60)
    print("DISABLING RLS VIA SUPABASE CLI")
    print("=" * 60)
    print()
    
    # Check if Supabase CLI is installed
    try:
        result = subprocess.run(["supabase", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Supabase CLI installed: {result.stdout.strip()}")
        else:
            print("[WARNING] Supabase CLI not found or not working")
            return False
    except FileNotFoundError:
        print("[WARNING] Supabase CLI not installed")
        print("Install it with: npm install -g supabase")
        return False
    
    # SQL commands to disable RLS
    sql_commands = """
-- ВРЕМЕННОЕ РЕШЕНИЕ: Отключение RLS для backend доступа
ALTER TABLE IF EXISTS public.profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.lesson_content DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.practical_materials DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.student_progress DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.invitation_codes DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.waitlist DISABLE ROW LEVEL SECURITY;
"""
    
    # Write SQL to temp file
    with open("temp_disable_rls.sql", "w", encoding="utf-8") as f:
        f.write(sql_commands)
    
    print("SQL commands written to temp_disable_rls.sql")
    print()
    print("To execute via Supabase CLI:")
    print(f"1. Link project: supabase link --project-ref {SUPABASE_PROJECT_ID}")
    print("2. Execute SQL: supabase db execute -f temp_disable_rls.sql")
    print()
    print("Or use Supabase Dashboard:")
    print(f"1. Go to: https://supabase.com/dashboard/project/{SUPABASE_PROJECT_ID}")
    print("2. SQL Editor -> New Query")
    print("3. Paste SQL commands from temp_disable_rls.sql")
    print()
    
    return True

def disable_rls_via_api():
    """Try to disable RLS using Supabase REST API"""
    print("=" * 60)
    print("DISABLING RLS VIA SUPABASE REST API")
    print("=" * 60)
    print()
    
    # Supabase REST API doesn't support direct SQL execution
    # But we can use the PostgREST API to check if RLS is blocking
    
    print("[INFO] Supabase REST API doesn't support direct SQL execution")
    print("We need to use one of these methods:")
    print()
    print("Method 1: Supabase Dashboard (Easiest)")
    print(f"  1. Go to: https://supabase.com/dashboard/project/{SUPABASE_PROJECT_ID}")
    print("  2. SQL Editor -> New Query")
    print("  3. Execute SQL commands")
    print()
    print("Method 2: Supabase CLI")
    print("  1. Install: npm install -g supabase")
    print(f"  2. Link: supabase link --project-ref {SUPABASE_PROJECT_ID}")
    print("  3. Execute: supabase db execute -f disable_rls_temporary.sql")
    print()
    print("Method 3: Direct PostgreSQL connection")
    print("  Use connection string from Supabase Dashboard")
    print("  Settings -> Database -> Connection string")
    print()
    
    return False

def main():
    print("=" * 60)
    print("DISABLE RLS VIA SUPABASE")
    print("=" * 60)
    print()
    print("WARNING: This is a TEMPORARY solution for quick startup.")
    print("For production, use SECURITY DEFINER functions or proper RLS policies.")
    print()
    
    # Try CLI first
    if disable_rls_via_cli():
        print("[OK] Supabase CLI method available")
    else:
        print("[INFO] Supabase CLI not available, using Dashboard method")
    
    # Show API method info
    disable_rls_via_api()
    
    print()
    print("=" * 60)
    print("RECOMMENDED: Use Supabase Dashboard")
    print("=" * 60)
    print()
    print("1. Open: https://supabase.com/dashboard")
    print(f"2. Select project: {SUPABASE_PROJECT_ID}")
    print("3. Go to: SQL Editor")
    print("4. Click: New Query")
    print("5. Paste SQL from: disable_rls_temporary.sql")
    print("6. Click: Run")
    print()
    print("SQL commands are in: disable_rls_temporary.sql")
    print()

if __name__ == "__main__":
    main()

