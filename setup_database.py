#!/usr/bin/env python3
"""
Setup database connection and apply migrations
"""

import paramiko
import os

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
DOMAIN = "21day.club"
APP_DIR = f"/var/www/{DOMAIN}"

# Database connection details
DB_HOST = "9558e7dd68bdade50224f6f1.twc1.net"
DB_PORT = "5432"
DB_NAME = "db_21day"
DB_USER = "gen_user"
DB_PASSWORD = "kQIXN6%3B%7DFrB3ZA"  # URL encoded, but we'll use it as is in connection string
DB_CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=verify-full"

def execute_command(ssh, command):
    """Execute command on remote server via SSH"""
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    
    if output.strip():
        print(f"Output: {output}")
    if error.strip():
        print(f"Error: {error}")
    
    return exit_status == 0, output

def main():
    print("=" * 60)
    print("DATABASE SETUP FOR 21day.club")
    print("=" * 60)
    print()
    
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Step 1: Install certificate
        print("=" * 60)
        print("STEP 1: Installing SSL certificate for database")
        print("=" * 60)
        print()
        
        execute_command(ssh, "mkdir -p ~/.cloud-certs")
        execute_command(ssh, 'curl -o ~/.cloud-certs/root.crt "https://st.timeweb.com/cloud-static/ca.crt"')
        execute_command(ssh, "chmod 0600 ~/.cloud-certs/root.crt")
        execute_command(ssh, "ls -la ~/.cloud-certs/")
        print()
        
        # Step 2: Install PostgreSQL client
        print("=" * 60)
        print("STEP 2: Installing PostgreSQL client")
        print("=" * 60)
        print()
        
        execute_command(ssh, "apt update")
        execute_command(ssh, "apt install -y postgresql-client")
        execute_command(ssh, "psql --version")
        print()
        
        # Step 3: Test database connection
        print("=" * 60)
        print("STEP 3: Testing database connection")
        print("=" * 60)
        print()
        
        # Set environment variable for SSL certificate
        test_cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT version();" """
        success, output = execute_command(ssh, test_cmd)
        
        if success:
            print("[OK] Database connection successful!")
        else:
            print("[ERROR] Database connection failed!")
            print("Please check connection details.")
            return False
        print()
        
        # Step 4: List migrations
        print("=" * 60)
        print("STEP 4: Checking migrations")
        print("=" * 60)
        print()
        
        execute_command(ssh, f"ls -la {APP_DIR}/supabase/migrations/ | head -20")
        print()
        
        # Step 5: Apply migrations (manual step - need to review first)
        print("=" * 60)
        print("STEP 5: Ready to apply migrations")
        print("=" * 60)
        print()
        print("[INFO] Migrations found. To apply them, you need to:")
        print("1. Review migration files")
        print("2. Apply them in order using psql")
        print()
        print("Example command:")
        print(f"  export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt")
        print(f"  psql '{DB_CONNECTION_STRING}' -f migration_file.sql")
        print()
        
        # Step 6: Check if Supabase is needed
        print("=" * 60)
        print("STEP 6: Important notes about Supabase")
        print("=" * 60)
        print()
        print("[WARNING] This application uses Supabase client which requires:")
        print("  - Supabase API endpoint (VITE_SUPABASE_URL)")
        print("  - Supabase Auth service")
        print("  - Supabase Edge Functions")
        print()
        print("Direct PostgreSQL connection is not enough!")
        print()
        print("Options:")
        print("1. Use Supabase Cloud and connect external PostgreSQL")
        print("2. Deploy Supabase self-hosted")
        print("3. Modify application to use direct PostgreSQL (complex)")
        print()
        
        ssh.close()
        
        print("=" * 60)
        print("[INFO] Database setup script completed")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Review and apply migrations")
        print("2. Set up Supabase (Cloud or self-hosted)")
        print("3. Configure environment variables:")
        print("   - VITE_SUPABASE_URL")
        print("   - VITE_SUPABASE_PUBLISHABLE_KEY")
        print("4. Rebuild application with environment variables")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

if __name__ == "__main__":
    main()

