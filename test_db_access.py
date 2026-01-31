#!/usr/bin/env python3
"""Test database access with different approaches"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

DB_CONNECTION_STRING = "postgresql://gen_user:kQIXN6%3B%7DFrB3ZA@9558e7dd68bdade50224f6f1.twc1.net:5432"

def execute_command(ssh, command):
    """Execute command on remote server via SSH"""
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    
    if output.strip():
        print(f"Output: {output}")
    if error.strip() and "FATAL" not in error and "ERROR" not in error:
        print(f"Error: {error}")
    
    return exit_status == 0, output

def main():
    print("=" * 60)
    print("TESTING DATABASE ACCESS")
    print("=" * 60)
    print()
    
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Try to list all databases user can access
        print("=" * 60)
        print("TEST 1: List all databases")
        print("=" * 60)
        
        # Try connecting to postgres database first
        for db_name in ["postgres", "template1", "db_21day"]:
            print(f"\nTrying database: {db_name}")
            conn_string = f"{DB_CONNECTION_STRING}/{db_name}?sslmode=verify-full"
            cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string}' -c "SELECT current_database(), current_user;" 2>&1"""
            
            success, output = execute_command(ssh, cmd)
            
            if success and "FATAL" not in output and "permission denied" not in output.lower():
                print(f"[OK] Successfully connected to {db_name}!")
                
                # Try to list tables
                print(f"\nListing tables in {db_name}...")
                cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string}' -c "\\dt" 2>&1"""
                execute_command(ssh, cmd)
                
                # Try to list schemas
                print(f"\nListing schemas in {db_name}...")
                cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string}' -c "\\dn" 2>&1"""
                execute_command(ssh, cmd)
                
                # Try to query user_roles table
                print(f"\nChecking user_roles table...")
                cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string}' -c "SELECT COUNT(*) FROM public.user_roles;" 2>&1"""
                execute_command(ssh, cmd)
                
                # Try to query auth.users table
                print(f"\nChecking auth.users table...")
                cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string}' -c "SELECT COUNT(*) FROM auth.users;" 2>&1"""
                execute_command(ssh, cmd)
                
                print(f"\n[SUCCESS] Database {db_name} is accessible!")
                print(f"Use this database: {db_name}")
                break
            else:
                print(f"[FAILED] Cannot connect to {db_name}")
        
        # Test backend connection
        print("\n" + "=" * 60)
        print("TEST 2: Backend API database connection")
        print("=" * 60)
        
        # Check if backend can connect
        cmd = """cd /var/www/21day.club-api && node -e "
import('./config/database.js').then(async (db) => {
  try {
    const result = await db.query('SELECT current_database(), version()');
    console.log('Connected:', result.rows[0]);
  } catch (e) {
    console.log('Error:', e.message);
  }
  process.exit(0);
}).catch(e => {
  console.log('Import error:', e.message);
  process.exit(1);
});
" 2>&1"""
        execute_command(ssh, cmd)
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

