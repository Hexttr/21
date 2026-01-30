#!/usr/bin/env python3
"""Download repository as ZIP and deploy to server"""

import paramiko
import os
import zipfile
import tempfile
import urllib.request
import shutil

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
DOMAIN = "21days.club"
SOURCE_REPO = "https://github.com/luckyit-test/day21"
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

def download_repo_zip():
    """Download repository as ZIP archive"""
    zip_url = f"{SOURCE_REPO}/archive/refs/heads/main.zip"
    # Try main branch first, then master
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "repo.zip")
    
    print(f"Downloading repository from {zip_url}...")
    try:
        urllib.request.urlretrieve(zip_url, zip_path)
        print("[OK] Repository downloaded!")
        return zip_path, temp_dir
    except Exception as e:
        print(f"Trying master branch...")
        zip_url = f"{SOURCE_REPO}/archive/refs/heads/master.zip"
        try:
            urllib.request.urlretrieve(zip_url, zip_path)
            print("[OK] Repository downloaded!")
            return zip_path, temp_dir
        except Exception as e2:
            print(f"[ERROR] Failed to download: {str(e2)}")
            return None, temp_dir

def extract_zip(zip_path, extract_to):
    """Extract ZIP archive"""
    print(f"Extracting to {extract_to}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    # Find extracted directory
    extracted_dirs = [d for d in os.listdir(extract_to) if os.path.isdir(os.path.join(extract_to, d))]
    if extracted_dirs:
        return os.path.join(extract_to, extracted_dirs[0])
    return extract_to

def upload_directory(ssh, local_dir):
    """Upload directory to server"""
    print(f"\n=== Uploading files from {local_dir} ===")
    sftp = ssh.open_sftp()
    
    try:
        # Create app directory
        execute_command(ssh, f"mkdir -p {APP_DIR}")
        
        # Upload files recursively
        for root, dirs, files in os.walk(local_dir):
            # Skip .git directory
            dirs[:] = [d for d in dirs if d != '.git']
            
            for dir_name in dirs:
                rel_path = os.path.relpath(os.path.join(root, dir_name), local_dir)
                remote_dir = os.path.join(APP_DIR, rel_path).replace("\\", "/")
                try:
                    sftp.mkdir(remote_dir)
                except:
                    pass  # Directory might already exist
            
            for file_name in files:
                local_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(local_path, local_dir)
                remote_path = os.path.join(APP_DIR, rel_path).replace("\\", "/")
                
                print(f"Uploading: {rel_path}")
                try:
                    sftp.put(local_path, remote_path)
                except Exception as e:
                    print(f"Warning: Failed to upload {rel_path}: {str(e)}")
        
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
    print("=== Downloading and deploying repository ===\n")
    
    # Download repository
    zip_path, temp_dir = download_repo_zip()
    if not zip_path:
        print("\n[ERROR] Could not download repository.")
        print("Please ensure you have access to the repository.")
        return False
    
    try:
        # Extract
        extracted_dir = extract_zip(zip_path, temp_dir)
        print(f"[OK] Extracted to {extracted_dir}")
        
        # Connect to server
        print("\nConnecting to server...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
            print("[OK] Connected successfully!")
            
            # Upload files
            if upload_directory(ssh, extracted_dir):
                print("\n[OK] Files uploaded successfully!")
                
                # Show what was uploaded
                print(f"\n=== Files in {APP_DIR} ===")
                execute_command(ssh, f"ls -la {APP_DIR}", check=False)
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"[ERROR] Server connection failed: {str(e)}")
            return False
        finally:
            ssh.close()
            
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\nCleaned up temporary files")

if __name__ == "__main__":
    main()

