#!/usr/bin/env python3
"""Upload files to server via SFTP"""

import paramiko
import os

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
DOMAIN = "21days.club"
APP_DIR = f"/var/www/{DOMAIN}"

def upload_file(sftp, local_path, remote_path):
    """Upload a file to the server"""
    print(f"Uploading {local_path} to {remote_path}")
    sftp.put(local_path, remote_path)
    print(f"[OK] Uploaded {local_path}")

def main():
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected successfully!")
        
        sftp = ssh.open_sftp()
        
        # Upload index.html
        if os.path.exists("index.html"):
            upload_file(sftp, "index.html", f"{APP_DIR}/index.html")
            # Set permissions
            ssh.exec_command(f"chown www-data:www-data {APP_DIR}/index.html")
            ssh.exec_command(f"chmod 644 {APP_DIR}/index.html")
        
        sftp.close()
        print("\n[OK] Files uploaded successfully!")
        
    except Exception as e:
        print(f"[ERROR] Failed: {str(e)}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

