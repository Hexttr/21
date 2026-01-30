#!/usr/bin/env python3
"""Copy repository using GitHub token or manual upload"""

import paramiko
import os
import sys

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
DOMAIN = "21days.club"
APP_DIR = f"/var/www/{DOMAIN}"

def execute_command(ssh, command, check=True):
    """Execute command on remote server via SSH"""
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if output:
        print(f"Output: {output}")
    if error:
        print(f"Error: {error}")
    
    if check and exit_status != 0:
        print(f"Command failed with exit status {exit_status}")
        return False, output, error
    
    return True, output, error

def clone_with_token(ssh, token):
    """Clone repository using GitHub token"""
    SOURCE_REPO = "https://github.com/luckyit-test/day21.git"
    # Replace token in URL
    repo_url = SOURCE_REPO.replace("https://", f"https://{token}@")
    success, output, error = execute_command(
        ssh,
        f"cd /root && rm -rf day21 && git clone {repo_url} day21",
        check=False
    )
    return success

def upload_local_files(ssh, local_dir="day21_files"):
    """Upload files from local directory"""
    if not os.path.exists(local_dir):
        print(f"[ERROR] Directory {local_dir} not found!")
        print("Please create this directory and put repository files there.")
        return False
    
    print(f"\n=== Uploading files from {local_dir} ===")
    sftp = ssh.open_sftp()
    
    try:
        # Create app directory
        execute_command(ssh, f"mkdir -p {APP_DIR}")
        
        # Upload files recursively
        for root, dirs, files in os.walk(local_dir):
            for dir_name in dirs:
                remote_dir = os.path.join(APP_DIR, os.path.relpath(os.path.join(root, dir_name), local_dir)).replace("\\", "/")
                try:
                    sftp.mkdir(remote_dir)
                except:
                    pass  # Directory might already exist
            
            for file_name in files:
                local_path = os.path.join(root, file_name)
                remote_path = os.path.join(APP_DIR, os.path.relpath(local_path, local_dir)).replace("\\", "/")
                
                print(f"Uploading: {local_path} -> {remote_path}")
                sftp.put(local_path, remote_path)
        
        # Set permissions
        execute_command(ssh, f"chown -R www-data:www-data {APP_DIR}")
        execute_command(ssh, f"find {APP_DIR} -type f -exec chmod 644 {{}} \\;")
        execute_command(ssh, f"find {APP_DIR} -type d -exec chmod 755 {{}} \\;")
        
        sftp.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Upload failed: {str(e)}")
        sftp.close()
        return False

def main():
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected successfully!")
        
        # Try method 1: GitHub token (if provided)
        if len(sys.argv) > 1:
            token = sys.argv[1]
            print("\n=== Trying to clone with token ===")
            if clone_with_token(ssh, token):
                print("[OK] Repository cloned with token!")
                # Copy to app directory
                execute_command(ssh, f"cp -r /root/day21/* {APP_DIR}/ 2>/dev/null || true")
                execute_command(ssh, f"chown -R www-data:www-data {APP_DIR}")
                return True
        
        # Try method 2: Upload local files
        print("\n=== Trying to upload local files ===")
        if upload_local_files(ssh):
            print("[OK] Files uploaded successfully!")
            return True
        
        print("\n[INFO] No files copied. Options:")
        print("1. Provide GitHub token: python copy_repo_with_token.py YOUR_TOKEN")
        print("2. Create 'day21_files' directory and put repository files there")
        print("3. Manually upload files to server")
        
        return False
        
    except Exception as e:
        print(f"[ERROR] Failed: {str(e)}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

