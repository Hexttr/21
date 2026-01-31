#!/usr/bin/env python3
"""Deploy updated backend to server"""

import paramiko
import os

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
BACKEND_DIR = "/var/www/21day.club-api"

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

def upload_file(sftp, local_path, remote_path):
    """Upload a file to server"""
    print(f"Uploading: {local_path} -> {remote_path}")
    try:
        sftp.put(local_path, remote_path)
        return True
    except Exception as e:
        print(f"Error uploading {local_path}: {e}")
        return False

def main():
    print("=" * 60)
    print("DEPLOYING UPDATED BACKEND")
    print("=" * 60)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        sftp = ssh.open_sftp()
        
        # Upload updated files
        print("=== Uploading updated files ===")
        files_to_upload = [
            ('backend/routes/auth.js', f'{BACKEND_DIR}/routes/auth.js'),
            ('backend/routes/lessons.js', f'{BACKEND_DIR}/routes/lessons.js'),
            ('backend/routes/progress.js', f'{BACKEND_DIR}/routes/progress.js'),
            ('backend/server.js', f'{BACKEND_DIR}/server.js'),
        ]
        
        for local, remote in files_to_upload:
            if os.path.exists(local):
                upload_file(sftp, local, remote)
        
        sftp.close()
        print()
        
        # Restart backend
        print("=== Restarting backend ===")
        execute_command(ssh, "systemctl restart 21day-api")
        execute_command(ssh, "sleep 3")
        execute_command(ssh, "systemctl is-active 21day-api && echo 'Service is running' || echo 'Service failed'")
        print()
        
        # Check logs
        print("=== Recent logs ===")
        execute_command(ssh, "journalctl -u 21day-api -n 15 --no-pager | tail -15")
        print()
        
        # Test API
        print("=== Testing API ===")
        execute_command(ssh, "curl -s http://localhost:3001/health")
        print()
        
        ssh.close()
        
        print("=" * 60)
        print("[OK] Backend deployed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

