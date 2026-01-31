#!/usr/bin/env python3
"""Fix database connection - decode password and try different databases"""

import paramiko
import urllib.parse

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

# Decode password from URL encoding
ENCODED_PASSWORD = "kQIXN6%3B%7DFrB3ZA"
DECODED_PASSWORD = urllib.parse.unquote(ENCODED_PASSWORD)

print(f"Encoded password: {ENCODED_PASSWORD}")
print(f"Decoded password: {DECODED_PASSWORD}")
print()

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
    print("FIXING DATABASE CONNECTION")
    print("=" * 60)
    print()
    
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Try db_21day with decoded password
        print("=" * 60)
        print("TEST: db_21day with decoded password")
        print("=" * 60)
        
        # Escape password for shell
        escaped_password = DECODED_PASSWORD.replace("'", "'\\''").replace(";", "\\;").replace("}", "\\}")
        conn_string = f"postgresql://gen_user:{escaped_password}@9558e7dd68bdade50224f6f1.twc1.net:5432/db_21day?sslmode=verify-full"
        
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string}' -c "SELECT current_database(), current_user;" 2>&1"""
        
        success, output = execute_command(ssh, cmd)
        
        if success and "FATAL" not in output and "permission denied" not in output.lower():
            print("[OK] Successfully connected to db_21day!")
            
            # List tables
            print("\nListing tables...")
            cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string}' -c "\\dt" 2>&1"""
            execute_command(ssh, cmd)
            
            # List schemas
            print("\nListing schemas...")
            cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string}' -c "\\dn" 2>&1"""
            execute_command(ssh, cmd)
            
            # Check key tables
            print("\nChecking key tables...")
            for table in ["user_roles", "lessons", "user_profiles", "invitation_codes"]:
                cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string}' -c "SELECT COUNT(*) FROM public.{table};" 2>&1"""
                execute_command(ssh, cmd)
            
            # Update backend .env with decoded password
            print("\n" + "=" * 60)
            print("Updating backend .env file")
            print("=" * 60)
            
            # Escape for .env file
            env_password = DECODED_PASSWORD.replace("\\", "\\\\").replace("$", "\\$").replace("`", "\\`")
            
            env_update = f"""# Update DB_PASSWORD in .env
cd /var/www/21day.club-api && \
sed -i 's|^DB_PASSWORD=.*|DB_PASSWORD={env_password}|' .env && \
cat .env | grep DB_PASSWORD"""
            
            execute_command(ssh, env_update)
            
            # Test backend connection
            print("\n" + "=" * 60)
            print("Testing backend connection")
            print("=" * 60)
            
            cmd = """cd /var/www/21day.club-api && node -e "
import('./config/database.js').then(async (db) => {
  try {
    const result = await db.query('SELECT current_database(), version()');
    console.log('[OK] Backend connected:', result.rows[0]);
  } catch (e) {
    console.log('[ERROR] Backend connection failed:', e.message);
  }
  process.exit(0);
}).catch(e => {
  console.log('[ERROR] Import failed:', e.message);
  process.exit(1);
});
" 2>&1"""
            execute_command(ssh, cmd)
            
            # Restart backend
            print("\nRestarting backend service...")
            execute_command(ssh, "systemctl restart 21day-api")
            execute_command(ssh, "sleep 2 && systemctl status 21day-api --no-pager | head -10")
            
        else:
            print("[FAILED] Still cannot connect to db_21day")
            print("You may need to request CONNECT privilege from Timeweb admin")
            print()
            print("Try connecting to template1 and check if data is there:")
            conn_string_template1 = f"postgresql://gen_user:{escaped_password}@9558e7dd68bdade50224f6f1.twc1.net:5432/template1?sslmode=verify-full"
            cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{conn_string_template1}' -c "SELECT schemaname, tablename FROM pg_tables WHERE schemaname IN ('public', 'auth') LIMIT 20;" 2>&1"""
            execute_command(ssh, cmd)
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

