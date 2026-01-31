#!/usr/bin/env python3
"""Test database connection and check existing data"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

# Database connection details
DB_CONNECTION_STRING = "postgresql://gen_user:kQIXN6%3B%7DFrB3ZA@9558e7dd68bdade50224f6f1.twc1.net:5432/db_21day?sslmode=verify-full"

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
    print("TESTING DATABASE CONNECTION AND CHECKING DATA")
    print("=" * 60)
    print()
    
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Test 1: Check PostgreSQL version
        print("=" * 60)
        print("TEST 1: PostgreSQL version")
        print("=" * 60)
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT version();" """
        execute_command(ssh, cmd)
        print()
        
        # Test 2: List all databases
        print("=" * 60)
        print("TEST 2: List databases")
        print("=" * 60)
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "\\l" """
        execute_command(ssh, cmd)
        print()
        
        # Test 3: List all tables in db_21day
        print("=" * 60)
        print("TEST 3: List all tables in db_21day")
        print("=" * 60)
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "\\dt" """
        execute_command(ssh, cmd)
        print()
        
        # Test 4: List all schemas
        print("=" * 60)
        print("TEST 4: List all schemas")
        print("=" * 60)
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "\\dn" """
        execute_command(ssh, cmd)
        print()
        
        # Test 5: Check public schema tables
        print("=" * 60)
        print("TEST 5: Check public schema tables")
        print("=" * 60)
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;" """
        execute_command(ssh, cmd)
        print()
        
        # Test 6: Check auth schema (for Supabase)
        print("=" * 60)
        print("TEST 6: Check auth schema (Supabase)")
        print("=" * 60)
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('auth', 'storage', 'realtime');" """
        execute_command(ssh, cmd)
        print()
        
        # Test 7: Count records in key tables
        print("=" * 60)
        print("TEST 7: Check data in key tables")
        print("=" * 60)
        
        # Check if user_roles table exists
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_roles';" """
        execute_command(ssh, cmd)
        
        # Try to count records in user_roles if it exists
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT COUNT(*) FROM public.user_roles;" 2>&1 || echo "Table does not exist or no access" """
        execute_command(ssh, cmd)
        print()
        
        # Test 8: Check connection string format
        print("=" * 60)
        print("TEST 8: Connection string analysis")
        print("=" * 60)
        print(f"Connection string: {DB_CONNECTION_STRING}")
        print()
        print("Components:")
        print("  - User: gen_user")
        print("  - Password: kQIXN6%3B%7DFrB3ZA (URL encoded)")
        print("  - Host: 9558e7dd68bdade50224f6f1.twc1.net")
        print("  - Port: 5432")
        print("  - Database: db_21day")
        print("  - SSL mode: verify-full")
        print()
        
        ssh.close()
        
        print("=" * 60)
        print("[INFO] Database connection tests completed")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

