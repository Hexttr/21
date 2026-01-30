#!/usr/bin/env python3
"""
Deploy local repository files to server
Usage: 
1. Clone repository locally: git clone https://github.com/luckyit-test/day21.git
2. Run: python deploy_local_repo.py
   Or specify path: python deploy_local_repo.py path/to/day21
"""

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

def upload_directory(ssh, local_dir):
    """Upload directory to server via SFTP"""
    print(f"\n=== Uploading files from {local_dir} ===")
    sftp = ssh.open_sftp()
    
    try:
        # Create app directory
        execute_command(ssh, f"mkdir -p {APP_DIR}")
        
        # Clear existing files (optional - comment out if you want to keep them)
        # execute_command(ssh, f"rm -rf {APP_DIR}/*", check=False)
        
        uploaded_count = 0
        skipped_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
        
        # Upload files recursively
        for root, dirs, files in os.walk(local_dir):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in skipped_dirs]
            
            # Create directories
            for dir_name in dirs:
                rel_path = os.path.relpath(os.path.join(root, dir_name), local_dir)
                remote_dir = os.path.join(APP_DIR, rel_path).replace("\\", "/")
                try:
                    sftp.mkdir(remote_dir)
                except:
                    pass  # Directory might already exist
            
            # Upload files
            for file_name in files:
                local_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(local_path, local_dir)
                remote_path = os.path.join(APP_DIR, rel_path).replace("\\", "/")
                
                # Skip certain files
                if any(skip in rel_path for skip in ['.git', '__pycache__', '.pyc', '.env']):
                    continue
                
                print(f"Uploading: {rel_path}")
                try:
                    # Create parent directory if needed
                    remote_parent = os.path.dirname(remote_path)
                    try:
                        sftp.mkdir(remote_parent)
                    except:
                        pass
                    
                    sftp.put(local_path, remote_path)
                    uploaded_count += 1
                except Exception as e:
                    print(f"Warning: Failed to upload {rel_path}: {str(e)}")
        
        # Set permissions
        print("\n=== Setting permissions ===")
        execute_command(ssh, f"chown -R www-data:www-data {APP_DIR}")
        execute_command(ssh, f"find {APP_DIR} -type f -exec chmod 644 {{}} \\;")
        execute_command(ssh, f"find {APP_DIR} -type d -exec chmod 755 {{}} \\;")
        
        # Make scripts executable if needed
        execute_command(ssh, f"find {APP_DIR} -name '*.sh' -exec chmod +x {{}} \\;", check=False)
        execute_command(ssh, f"find {APP_DIR} -name '*.py' -exec chmod +x {{}} \\;", check=False)
        
        sftp.close()
        print(f"\n[OK] Uploaded {uploaded_count} files successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Upload failed: {str(e)}")
        sftp.close()
        return False

def main():
    # Determine source directory
    if len(sys.argv) > 1:
        local_dir = sys.argv[1]
    else:
        # Try common locations
        possible_dirs = [
            "day21",
            "../day21",
            "./day21",
            os.path.join(os.path.expanduser("~"), "day21")
        ]
        local_dir = None
        for dir_path in possible_dirs:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                local_dir = dir_path
                break
    
    if not local_dir or not os.path.exists(local_dir):
        print("[ERROR] Repository directory not found!")
        print("\nPlease either:")
        print("1. Clone repository: git clone https://github.com/luckyit-test/day21.git")
        print("2. Run script with path: python deploy_local_repo.py path/to/day21")
        return False
    
    print(f"Using repository directory: {local_dir}")
    
    # Connect to server
    print("\nConnecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected successfully!")
        
        # Upload files
        if upload_directory(ssh, local_dir):
            print("\n[OK] Deployment completed successfully!")
            
            # Show what was uploaded
            print(f"\n=== Files in {APP_DIR} ===")
            execute_command(ssh, f"ls -la {APP_DIR}", check=False)
            
            # Show directory structure
            print(f"\n=== Directory structure ===")
            execute_command(ssh, f"find {APP_DIR} -type f | head -20", check=False)
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed: {str(e)}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

