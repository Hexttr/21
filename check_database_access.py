#!/usr/bin/env python3
"""Try different database connections"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

# Try different databases
DATABASES = [
    "db_21day",
    "postgres",  # Default PostgreSQL database
    "template1",  # Template database
]

DB_BASE = "postgresql://gen_user:kQIXN6%3B%7DFrB3ZA@9558e7dd68bdade50224f6f1.twc1.net:5432"

def execute_command(ssh, command):
    """Execute command on remote server via SSH"""
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    
    if output.strip():
        print(f"Output: {output}")
    if error.strip() and "FATAL" not in error:
        print(f"Error: {error}")
    
    return exit_status == 0, output

def main():
    print("=" * 60)
    print("CHECKING DATABASE ACCESS")
    print("=" * 60)
    print()
    
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Try each database
        for db_name in DATABASES:
            print("=" * 60)
            print(f"Testing database: {db_name}")
            print("=" * 60)
            
            conn_string = f"{DB_BASE}/{db_name}?sslmode=verify-full"
            cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string}' -c "SELECT current_database(), current_user;" 2>&1"""
            
            success, output = execute_command(ssh, cmd)
            
            if success and "FATAL" not in output:
                print(f"[OK] Successfully connected to {db_name}!")
                print()
                
                # Try to list tables
                print(f"Listing tables in {db_name}...")
                cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string}' -c "\\dt" 2>&1"""
                execute_command(ssh, cmd)
                print()
                break
            else:
                print(f"[FAILED] Cannot connect to {db_name}")
                print()
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

