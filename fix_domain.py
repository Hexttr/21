#!/usr/bin/env python3
"""Fix domain name from 21days.club to 21day.club in all configurations"""

import paramiko
import re

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
OLD_DOMAIN = "21days.club"
NEW_DOMAIN = "21day.club"
APP_DIR = f"/var/www/{OLD_DOMAIN}"
NEW_APP_DIR = f"/var/www/{NEW_DOMAIN}"

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

def main():
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!\n")
        
        # Rename application directory
        print("=== Renaming application directory ===")
        execute_command(ssh, f"mv {APP_DIR} {NEW_APP_DIR}")
        
        # Update Nginx configuration
        print("\n=== Updating Nginx configuration ===")
        nginx_config = f"""server {{
    listen 80;
    server_name {NEW_DOMAIN} www.{NEW_DOMAIN};
    
    root {NEW_APP_DIR}/dist;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
    
    location / {{
        try_files $uri $uri/ /index.html;
    }}
    
    # Cache static assets
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}}"""
        
        cmd = f"""cat > /etc/nginx/sites-available/{NEW_DOMAIN} << 'EOF'
{nginx_config}
EOF"""
        execute_command(ssh, cmd)
        
        # Remove old Nginx config and create symlink
        print("\n=== Updating Nginx symlinks ===")
        execute_command(ssh, f"rm -f /etc/nginx/sites-enabled/{OLD_DOMAIN}")
        execute_command(ssh, f"rm -f /etc/nginx/sites-available/{OLD_DOMAIN}")
        execute_command(ssh, f"ln -sf /etc/nginx/sites-available/{NEW_DOMAIN} /etc/nginx/sites-enabled/")
        
        # Test and reload Nginx
        print("\n=== Testing and reloading Nginx ===")
        execute_command(ssh, "nginx -t")
        execute_command(ssh, "systemctl reload nginx")
        
        # Check DNS
        print("\n=== Checking DNS for new domain ===")
        execute_command(ssh, f"host {NEW_DOMAIN}")
        execute_command(ssh, f"host www.{NEW_DOMAIN}")
        execute_command(ssh, f"dig +short {NEW_DOMAIN}")
        
        print("\n[OK] Domain updated to 21day.club!")
        print(f"\nApplication directory: {NEW_APP_DIR}")
        print(f"Nginx config: /etc/nginx/sites-available/{NEW_DOMAIN}")
        print(f"\nTo install SSL certificate:")
        print(f"  certbot --nginx -d {NEW_DOMAIN} -d www.{NEW_DOMAIN} --non-interactive --agree-tos --email admin@{NEW_DOMAIN} --redirect")
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

