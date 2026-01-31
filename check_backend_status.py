#!/usr/bin/env python3
"""Check backend API status"""

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
    print("CHECKING BACKEND API STATUS")
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
        execute_command(ssh, "systemctl status 21day-api --no-pager | head -15")
        print()
        
        # Check if service is running
        print("=== Service Active Check ===")
        execute_command(ssh, "systemctl is-active 21day-api")
        print()
        
        # Check logs
        print("=== Recent Logs ===")
        execute_command(ssh, "journalctl -u 21day-api -n 20 --no-pager")
        print()
        
        # Test API endpoint
        print("=== Testing API Health ===")
        execute_command(ssh, "curl -s http://localhost:3001/health || echo 'API not responding'")
        print()
        
        # Check database connection
        print("=== Testing Database Connection ===")
        execute_command(ssh, "cd /var/www/21day.club-api && node -e \"import('./config/database.js').then(m => m.query('SELECT 1').then(() => console.log('DB OK')).catch(e => console.log('DB Error:', e.message)))\" 2>&1")
        print()
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

