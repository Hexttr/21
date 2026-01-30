#!/usr/bin/env python3
"""Copy repository from source to server"""

import paramiko
import os

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
DOMAIN = "21days.club"
SOURCE_REPO = "https://github.com/luckyit-test/day21.git"
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

def main():
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected successfully!")
        
        # Clone repository
        print("\n=== Cloning source repository ===")
        success, output, error = execute_command(
            ssh, 
            f"cd /root && rm -rf day21 && git clone {SOURCE_REPO} day21",
            check=False
        )
        
        if not success:
            print("\n[WARNING] Repository clone failed. Trying alternative methods...")
            # Try with different authentication methods
            print("Please ensure you have access to the repository.")
            print("You may need to:")
            print("1. Add SSH key to GitHub")
            print("2. Use personal access token")
            print("3. Or manually upload files")
            return False
        
        # Check what was cloned
        print("\n=== Checking cloned repository ===")
        success, output, _ = execute_command(ssh, "cd /root/day21 && ls -la", check=False)
        if success:
            print("Repository structure:")
            print(output)
        
        # Copy files to application directory
        print(f"\n=== Copying files to {APP_DIR} ===")
        execute_command(ssh, f"mkdir -p {APP_DIR}")
        execute_command(ssh, f"cp -r /root/day21/* {APP_DIR}/ 2>/dev/null || true")
        execute_command(ssh, f"chown -R www-data:www-data {APP_DIR}")
        execute_command(ssh, f"find {APP_DIR} -type f -exec chmod 644 {{}} \\;")
        execute_command(ssh, f"find {APP_DIR} -type d -exec chmod 755 {{}} \\;")
        
        # Show what was copied
        print(f"\n=== Files in {APP_DIR} ===")
        execute_command(ssh, f"ls -la {APP_DIR}", check=False)
        
        print("\n[OK] Repository copied successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed: {str(e)}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

