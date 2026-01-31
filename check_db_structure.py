#!/usr/bin/env python3
"""Check database structure and available tables"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

DB_CONNECTION_STRING = "postgresql://gen_user:kQIXN6%3B%7DFrB3ZA@9558e7dd68bdade50224f6f1.twc1.net:5432/db_21day?sslmode=verify-full"

def execute_command(ssh, command):
    """Execute command on remote server via SSH"""
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    
    if output.strip():
        print(f"{output}")
    if error.strip() and "FATAL" not in error and "ERROR" not in error:
        print(f"Error: {error}")
    
    return exit_status == 0, output

def main():
    print("=" * 60)
    print("CHECKING DATABASE STRUCTURE")
    print("=" * 60)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        
        # Get table structures
        print("=== Available Tables ===")
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT table_name, table_type FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;" 2>&1"""
        execute_command(ssh, cmd)
        print()
        
        # Check each table structure
        tables = ["profiles", "user_roles", "lesson_content", "practical_materials", "student_progress"]
        
        for table in tables:
            print(f"=== Table: {table} ===")
            # Try to get column info
            cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "\\d public.{table}" 2>&1"""
            execute_command(ssh, cmd)
            print()
            
            # Try to count rows (if we have permission)
            cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT COUNT(*) as count FROM public.{table};" 2>&1"""
            execute_command(ssh, cmd)
            print()
        
        # Check auth schema
        print("=== Auth Schema ===")
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'auth' ORDER BY table_name;" 2>&1"""
        execute_command(ssh, cmd)
        print()
        
        ssh.close()
        
        print("=" * 60)
        print("[OK] Database structure checked!")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

