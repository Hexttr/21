#!/usr/bin/env python3
"""Automated RLS disable via Supabase - try multiple methods"""

import subprocess
import sys
import os

SUPABASE_PROJECT_ID = "uyymukgccsqzagpusswm"
SUPABASE_URL = "https://uyymukgccsqzagpusswm.supabase.co"

def check_supabase_cli():
    """Check if Supabase CLI is installed"""
    try:
        result = subprocess.run(["supabase", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def install_supabase_cli():
    """Try to install Supabase CLI"""
    print("Attempting to install Supabase CLI...")
    try:
        # Try npm
        result = subprocess.run(["npm", "install", "-g", "supabase"], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Supabase CLI installed via npm")
            return True
    except:
        pass
    
    print("[WARNING] Could not install Supabase CLI automatically")
    print("Please install manually: npm install -g supabase")
    return False

def disable_rls_via_cli():
    """Disable RLS using Supabase CLI"""
    print("=" * 60)
    print("METHOD 1: Using Supabase CLI")
    print("=" * 60)
    print()
    
    if not check_supabase_cli():
        print("[INFO] Supabase CLI not installed")
        if input("Install Supabase CLI? (y/n): ").lower() == 'y':
            if not install_supabase_cli():
                return False
        else:
            return False
    
    # SQL commands
    sql_content = """-- ВРЕМЕННОЕ РЕШЕНИЕ: Отключение RLS
ALTER TABLE IF EXISTS public.profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.lesson_content DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.practical_materials DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.student_progress DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.invitation_codes DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.waitlist DISABLE ROW LEVEL SECURITY;
"""
    
    # Write to temp file
    with open("temp_rls_disable.sql", "w", encoding="utf-8") as f:
        f.write(sql_content)
    
    print("SQL file created: temp_rls_disable.sql")
    print()
    print("Steps to execute:")
    print(f"1. supabase login")
    print(f"2. supabase link --project-ref {SUPABASE_PROJECT_ID}")
    print(f"3. supabase db execute -f temp_rls_disable.sql")
    print()
    
    # Try to execute if user wants
    if input("Execute now? (y/n): ").lower() == 'y':
        try:
            # Login
            print("Logging in to Supabase...")
            subprocess.run(["supabase", "login"], check=False)
            
            # Link project
            print(f"Linking project {SUPABASE_PROJECT_ID}...")
            result = subprocess.run(
                ["supabase", "link", "--project-ref", SUPABASE_PROJECT_ID],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"[ERROR] Failed to link project: {result.stderr}")
                return False
            
            # Execute SQL
            print("Executing SQL to disable RLS...")
            result = subprocess.run(
                ["supabase", "db", "execute", "-f", "temp_rls_disable.sql"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("[OK] RLS disabled successfully!")
                print(result.stdout)
                return True
            else:
                print(f"[ERROR] Failed to execute SQL: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    return False

def show_dashboard_instructions():
    """Show instructions for Supabase Dashboard"""
    print("=" * 60)
    print("METHOD 2: Using Supabase Dashboard (RECOMMENDED)")
    print("=" * 60)
    print()
    print("1. Open: https://supabase.com/dashboard")
    print(f"2. Select project: {SUPABASE_PROJECT_ID}")
    print("3. Go to: SQL Editor (left menu)")
    print("4. Click: New Query")
    print("5. Paste the following SQL:")
    print()
    print("-" * 60)
    print("""
-- ВРЕМЕННОЕ РЕШЕНИЕ: Отключение RLS
ALTER TABLE IF EXISTS public.profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.lesson_content DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.practical_materials DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.student_progress DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.invitation_codes DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.waitlist DISABLE ROW LEVEL SECURITY;
""")
    print("-" * 60)
    print()
    print("6. Click: Run (or press Ctrl+Enter)")
    print()
    print("SQL is also saved in: disable_rls_temporary.sql")
    print()

def main():
    print("=" * 60)
    print("AUTOMATED RLS DISABLE VIA SUPABASE")
    print("=" * 60)
    print()
    print("WARNING: This is a TEMPORARY solution.")
    print("For production, use SECURITY DEFINER functions or proper RLS policies.")
    print()
    
    # Try CLI method first
    if check_supabase_cli():
        print("[OK] Supabase CLI detected")
        if disable_rls_via_cli():
            print()
            print("=" * 60)
            print("[SUCCESS] RLS disabled via Supabase CLI!")
            print("=" * 60)
            return
    
    # Show dashboard instructions
    show_dashboard_instructions()
    
    print()
    print("=" * 60)
    print("After disabling RLS, test backend:")
    print("=" * 60)
    print("python test_after_rls_disable.py")
    print()

if __name__ == "__main__":
    main()

