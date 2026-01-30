#!/usr/bin/env python3
"""Check if build completed and fix if needed"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
APP_DIR = "/var/www/21days.club"

def execute_command(ssh, command):
    """Execute command on remote server via SSH"""
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    
    if output:
        print(f"Output: {output}")
    if error:
        print(f"Error: {error}")
    
    return exit_status == 0, output, error

def main():
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        
        # Check if dist exists
        print("\n=== Checking build status ===")
        success, output, _ = execute_command(ssh, f"test -d {APP_DIR}/dist && echo 'EXISTS' || echo 'NOT_EXISTS'")
        
        if "EXISTS" in output:
            print("[OK] Build directory exists!")
            execute_command(ssh, f"ls -la {APP_DIR}/dist")
            execute_command(ssh, f"du -sh {APP_DIR}/dist")
        else:
            print("[WARNING] Build directory not found. Building now...")
            execute_command(ssh, f"cd {APP_DIR} && npm run build")
            execute_command(ssh, f"ls -la {APP_DIR}/dist")
        
        # Check Nginx
        print("\n=== Checking Nginx ===")
        execute_command(ssh, "nginx -t")
        execute_command(ssh, "systemctl status nginx --no-pager | head -5")
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

