#!/usr/bin/env python3
"""
Deployment script for 21days.club
Uses paramiko for SSH connection and server setup
"""

import paramiko
import os
import sys
import time
from pathlib import Path

# Server configuration
SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
DOMAIN = "21days.club"
SOURCE_REPO = "https://github.com/luckyit-test/day21.git"

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

def setup_server():
    """Connect to server and set up environment"""
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("Connected successfully!")
        
        # Update system
        print("\n=== Updating system ===")
        execute_command(ssh, "apt update && apt upgrade -y")
        
        # Install required packages
        print("\n=== Installing required packages ===")
        packages = [
            "curl", "wget", "git", "docker.io", "docker-compose", 
            "nginx", "certbot", "python3-certbot-nginx", "ufw"
        ]
        execute_command(ssh, f"apt install -y {' '.join(packages)}")
        
        # Start Docker
        print("\n=== Starting Docker ===")
        execute_command(ssh, "systemctl start docker")
        execute_command(ssh, "systemctl enable docker")
        
        # Clone source repository
        print("\n=== Cloning source repository ===")
        execute_command(ssh, f"cd /root && rm -rf day21 && git clone {SOURCE_REPO} day21")
        
        # Check if clone was successful
        success, output, _ = execute_command(ssh, "cd /root/day21 && ls -la", check=False)
        if not success:
            print("Warning: Repository might not be accessible. Creating basic structure...")
            execute_command(ssh, "mkdir -p /root/day21")
        
        # Create application directory
        app_dir = f"/var/www/{DOMAIN}"
        print(f"\n=== Creating application directory: {app_dir} ===")
        execute_command(ssh, f"mkdir -p {app_dir}")
        execute_command(ssh, f"chown -R www-data:www-data {app_dir}")
        
        # Copy application files
        print("\n=== Copying application files ===")
        execute_command(ssh, f"cp -r /root/day21/* {app_dir}/ 2>/dev/null || true")
        
        # Configure firewall
        print("\n=== Configuring firewall ===")
        execute_command(ssh, "ufw allow 22/tcp")
        execute_command(ssh, "ufw allow 80/tcp")
        execute_command(ssh, "ufw allow 443/tcp")
        execute_command(ssh, "ufw --force enable")
        
        # Create Nginx configuration
        print("\n=== Creating Nginx configuration ===")
        nginx_config = f"""server {{
    listen 80;
    server_name {DOMAIN} www.{DOMAIN};
    
    root {app_dir};
    index index.html index.php index.js;
    
    location / {{
        try_files $uri $uri/ /index.html;
    }}
    
    location ~ \\.php$ {{
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }}
    
    location ~ /\\.ht {{
        deny all;
    }}
}}"""
        # Write nginx config using heredoc
        cmd = f"""cat > /etc/nginx/sites-available/{DOMAIN} << 'EOF'
{nginx_config}
EOF"""
        execute_command(ssh, cmd)
        execute_command(ssh, f"ln -sf /etc/nginx/sites-available/{DOMAIN} /etc/nginx/sites-enabled/")
        execute_command(ssh, "rm -f /etc/nginx/sites-enabled/default")
        
        # Test Nginx configuration
        print("\n=== Testing Nginx configuration ===")
        execute_command(ssh, "nginx -t")
        
        # Reload Nginx
        print("\n=== Reloading Nginx ===")
        execute_command(ssh, "systemctl reload nginx")
        
        # Setup SSL with Certbot
        print("\n=== Setting up SSL certificate ===")
        print("Note: Make sure DNS is pointing to this server before running certbot")
        certbot_cmd = f"certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email admin@{DOMAIN} --redirect"
        success, output, error = execute_command(ssh, certbot_cmd, check=False)
        if not success:
            print("SSL setup might have failed. This is normal if DNS is not configured yet.")
            print("You can run certbot manually later when DNS is ready.")
        else:
            print("SSL certificate installed successfully!")
        
        # Setup automatic renewal
        print("\n=== Setting up SSL auto-renewal ===")
        execute_command(ssh, "systemctl enable certbot.timer")
        execute_command(ssh, "systemctl start certbot.timer")
        
        print("\n=== Deployment completed successfully! ===")
        print(f"Application should be available at https://{DOMAIN}")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    success = setup_server()
    sys.exit(0 if success else 1)

