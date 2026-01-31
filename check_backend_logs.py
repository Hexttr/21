#!/usr/bin/env python3
"""Check backend logs for database connection"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

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
    print("CHECKING BACKEND LOGS")
    print("=" * 60)
    print()
    
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Check service status
        print("=== Service Status ===")
        execute_command(ssh, "systemctl is-active 21day-api && echo 'Service is running' || echo 'Service is not running'")
        print()
        
        # Get recent logs
        print("=== Recent Logs (last 30 lines) ===")
        execute_command(ssh, "journalctl -u 21day-api -n 30 --no-pager | tail -30")
        print()
        
        # Test simple connection
        print("=== Testing Simple Connection ===")
        cmd = """cd /var/www/21day.club-api && node -e "
import('./config/database.js').then(async (db) => {
  try {
    const result = await db.query('SELECT 1 as test');
    console.log('SUCCESS: Connected to database');
    console.log('Test query result:', result.rows[0]);
  } catch (e) {
    console.log('ERROR:', e.message);
  }
  process.exit(0);
});
" 2>&1"""
        execute_command(ssh, cmd)
        print()
        
        # Test API health endpoint
        print("=== Testing API Health Endpoint ===")
        execute_command(ssh, "curl -s http://localhost:3001/health | head -5 || echo 'API not responding'")
        print()
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

