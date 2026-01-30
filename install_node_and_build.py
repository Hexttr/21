#!/usr/bin/env python3
"""Install Node.js and build React/Vite application on server"""

import paramiko
import time

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
DOMAIN = "21days.club"
APP_DIR = f"/var/www/{DOMAIN}"

def execute_command(ssh, command, check=True, wait_for_completion=True):
    """Execute command on remote server via SSH"""
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    
    if wait_for_completion:
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        if output:
            print(f"Output: {output}")
        if error:
            print(f"Error: {error}")
        
        if check and exit_status != 0:
            print(f"Command failed with exit status {exit_status}")
            return False, output, error
        
        return True, output, error
    else:
        return True, "", ""

def main():
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected successfully!")
        
        # Install Node.js 20.x
        print("\n=== Installing Node.js 20.x ===")
        execute_command(ssh, "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -")
        execute_command(ssh, "apt install -y nodejs")
        
        # Verify installation
        print("\n=== Verifying Node.js installation ===")
        execute_command(ssh, "node --version")
        execute_command(ssh, "npm --version")
        
        # Navigate to app directory and install dependencies
        print(f"\n=== Installing dependencies in {APP_DIR} ===")
        print("This may take a few minutes...")
        success, output, error = execute_command(ssh, f"cd {APP_DIR} && npm install --production=false", check=False)
        
        if not success:
            print("[WARNING] npm install had issues, but continuing...")
        
        # Build application
        print("\n=== Building application ===")
        print("This may take a few minutes...")
        success, output, error = execute_command(ssh, f"cd {APP_DIR} && npm run build", check=False)
        
        if success:
            print("[OK] Build completed!")
            # Check dist directory
            execute_command(ssh, f"ls -la {APP_DIR}/dist", check=False)
            execute_command(ssh, f"du -sh {APP_DIR}/dist", check=False)
        else:
            print("[ERROR] Build failed!")
            print("Error output:", error)
            return False
        
        # Set permissions
        print("\n=== Setting permissions ===")
        execute_command(ssh, f"chown -R www-data:www-data {APP_DIR}")
        
        # Test Nginx
        print("\n=== Testing Nginx configuration ===")
        execute_command(ssh, "nginx -t")
        
        # Reload Nginx
        print("\n=== Reloading Nginx ===")
        execute_command(ssh, "systemctl reload nginx")
        
        print("\n[OK] Application built and deployed successfully!")
        print(f"Application should be available at http://{DOMAIN}")
        print("\nNote: You may need to configure environment variables for Supabase:")
        print("  - VITE_SUPABASE_URL")
        print("  - VITE_SUPABASE_PUBLISHABLE_KEY")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed: {str(e)}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

