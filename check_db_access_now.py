#!/usr/bin/env python3
"""Check current database access status"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

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
    if error.strip() and "FATAL" not in error and "ERROR" not in error:
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
        print("[OK] Connected to server!")
        print()
        
        # Test 1: Direct psql connection
        print("=" * 60)
        print("TEST 1: Direct psql connection to db_21day")
        print("=" * 60)
        
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT current_database(), current_user, version();" 2>&1"""
        
        success, output = execute_command(ssh, cmd)
        
        if success and "FATAL" not in output and "permission denied" not in output.lower():
            print("\n[OK] Direct connection successful!")
            
            # List tables
            print("\nListing tables...")
            cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "\\dt" 2>&1"""
            execute_command(ssh, cmd)
            
            # List schemas
            print("\nListing schemas...")
            cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "\\dn" 2>&1"""
            execute_command(ssh, cmd)
            
            # Check key tables
            print("\nChecking key tables...")
            for table in ["user_roles", "lessons", "user_profiles", "invitation_codes", "auth.users"]:
                if "." in table:
                    schema, tbl = table.split(".")
                    cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT COUNT(*) as count FROM {schema}.{tbl};" 2>&1"""
                else:
                    cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT COUNT(*) as count FROM public.{table};" 2>&1"""
                execute_command(ssh, cmd)
        else:
            print("\n[FAILED] Cannot connect to db_21day")
            print("Error details in output above")
            print()
        
        # Test 2: Backend API connection
        print("\n" + "=" * 60)
        print("TEST 2: Backend API database connection")
        print("=" * 60)
        
        cmd = """cd /var/www/21day.club-api && node -e "
import('./config/database.js').then(async (db) => {
  try {
    const result = await db.query('SELECT current_database(), current_user');
    console.log('[OK] Backend connected successfully!');
    console.log('Database:', result.rows[0].current_database);
    console.log('User:', result.rows[0].current_user);
    
    // Try to query a table
    try {
      const tables = await db.query(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5\");
      console.log('Tables found:', tables.rows.length);
    } catch (e) {
      console.log('Cannot list tables:', e.message);
    }
  } catch (e) {
    console.log('[ERROR] Backend connection failed:', e.message);
  }
  process.exit(0);
});
" 2>&1"""
        execute_command(ssh, cmd)
        print()
        
        # Test 3: API health endpoint
        print("=" * 60)
        print("TEST 3: API health endpoint")
        print("=" * 60)
        execute_command(ssh, "curl -s http://localhost:3001/health")
        print()
        
        ssh.close()
        
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print()
        print("If both tests show connection errors:")
        print("  - Need CONNECT privilege for user 'gen_user' on database 'db_21day'")
        print("  - Or data might be in a different database")
        print("  - Or connection string might need adjustment")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

