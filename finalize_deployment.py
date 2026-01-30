#!/usr/bin/env python3
"""Finalize deployment - fix permissions and verify setup"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
DOMAIN = "21days.club"
APP_DIR = "/var/www/21days.club"

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
    
    return exit_status == 0

def main():
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        
        # Fix permissions
        print("\n=== Fixing permissions ===")
        execute_command(ssh, f"chown -R www-data:www-data {APP_DIR}")
        execute_command(ssh, f"find {APP_DIR} -type f -exec chmod 644 {{}} \\;")
        execute_command(ssh, f"find {APP_DIR} -type d -exec chmod 755 {{}} \\;")
        
        # Verify dist directory
        print("\n=== Verifying build ===")
        execute_command(ssh, f"ls -la {APP_DIR}/dist")
        execute_command(ssh, f"test -f {APP_DIR}/dist/index.html && echo 'index.html exists' || echo 'index.html missing'")
        
        # Check Nginx configuration
        print("\n=== Verifying Nginx configuration ===")
        execute_command(ssh, "nginx -t")
        
        # Check if Nginx is serving from correct directory
        print("\n=== Checking Nginx root directory ===")
        execute_command(ssh, f"grep -A 2 'root' /etc/nginx/sites-available/{DOMAIN} | head -3")
        
        # Reload Nginx
        print("\n=== Reloading Nginx ===")
        execute_command(ssh, "systemctl reload nginx")
        
        # Check Nginx status
        print("\n=== Nginx status ===")
        execute_command(ssh, "systemctl is-active nginx")
        
        print("\n[OK] Deployment finalized!")
        print(f"\nApplication should be available at:")
        print(f"  - http://{DOMAIN}")
        print(f"  - http://www.{DOMAIN}")
        print(f"\nNote: SSL certificate will be installed after DNS is configured.")
        print(f"To install SSL, run:")
        print(f"  certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email admin@{DOMAIN} --redirect")
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

