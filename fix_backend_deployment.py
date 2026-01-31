#!/usr/bin/env python3
"""Fix backend deployment - upload missing files"""

import paramiko
import os

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
BACKEND_DIR = "/var/www/21day.club-api"

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
    print("FIXING BACKEND DEPLOYMENT")
    print("=" * 60)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        sftp = ssh.open_sftp()
        
        # Upload missing files
        print("=== Uploading missing files ===")
        files_to_upload = [
            ('backend/routes/admin.js', f'{BACKEND_DIR}/routes/admin.js'),
            ('backend/routes/users.js', f'{BACKEND_DIR}/routes/users.js'),
        ]
        
        for local, remote in files_to_upload:
            if os.path.exists(local):
                upload_file(sftp, local, remote)
            else:
                print(f"[WARNING] File not found: {local}")
        
        sftp.close()
        print()
        
        # Restart backend
        print("=== Restarting backend ===")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart 21day-api")
        stdout.channel.recv_exit_status()
        time.sleep(3)
        
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active 21day-api")
        status = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"Service status: {status}")
        print()
        
        # Check logs
        print("=== Recent logs ===")
        stdin, stdout, stderr = ssh.exec_command("journalctl -u 21day-api -n 10 --no-pager | tail -10")
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        print()
        
        # Test API
        print("=== Testing API ===")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:3001/health")
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        print()
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import time
    main()

