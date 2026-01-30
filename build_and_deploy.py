#!/usr/bin/env python3
"""Build and deploy React/Vite application on server"""

import paramiko
import os

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

def main():
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected successfully!")
        
        # Check Node.js version
        print("\n=== Checking Node.js ===")
        success, output, _ = execute_command(ssh, "node --version", check=False)
        if not success:
            print("Node.js not found. Installing Node.js...")
            # Install Node.js 20.x
            execute_command(ssh, "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -")
            execute_command(ssh, "apt install -y nodejs")
        else:
            print(f"Node.js version: {output.strip()}")
        
        # Check npm version
        print("\n=== Checking npm ===")
        execute_command(ssh, "npm --version", check=False)
        
        # Navigate to app directory
        print(f"\n=== Building application in {APP_DIR} ===")
        
        # Install dependencies
        print("\n--- Installing dependencies ---")
        execute_command(ssh, f"cd {APP_DIR} && npm install", check=False)
        
        # Build application
        print("\n--- Building application ---")
        success, output, error = execute_command(ssh, f"cd {APP_DIR} && npm run build", check=False)
        
        if not success:
            print("[WARNING] Build might have failed. Checking dist directory...")
            execute_command(ssh, f"ls -la {APP_DIR}/dist", check=False)
        else:
            print("[OK] Build completed!")
            execute_command(ssh, f"ls -la {APP_DIR}/dist", check=False)
        
        # Update Nginx configuration to serve from dist
        print("\n=== Updating Nginx configuration ===")
        nginx_config = f"""server {{
    listen 80;
    server_name {DOMAIN} www.{DOMAIN};
    
    root {APP_DIR}/dist;
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
        
        cmd = f"""cat > /etc/nginx/sites-available/{DOMAIN} << 'EOF'
{nginx_config}
EOF"""
        execute_command(ssh, cmd)
        
        # Test and reload Nginx
        print("\n=== Testing Nginx configuration ===")
        execute_command(ssh, "nginx -t")
        
        print("\n=== Reloading Nginx ===")
        execute_command(ssh, "systemctl reload nginx")
        
        print("\n[OK] Application deployed and Nginx configured!")
        print(f"Application should be available at http://{DOMAIN}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed: {str(e)}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

