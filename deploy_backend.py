#!/usr/bin/env python3
"""Deploy backend API to server"""

import paramiko
import os

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
DOMAIN = "21day.club"
APP_DIR = f"/var/www/{DOMAIN}"
BACKEND_DIR = f"/var/www/{DOMAIN}-api"

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

def upload_directory(sftp, local_dir, remote_dir):
    """Upload directory to server"""
    print(f"\n=== Uploading {local_dir} to {remote_dir} ===")
    
    # Create remote directory
    try:
        sftp.mkdir(remote_dir)
    except:
        pass
    
    for root, dirs, files in os.walk(local_dir):
        # Skip node_modules and .git
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git']]
        
        for dir_name in dirs:
            rel_path = os.path.relpath(os.path.join(root, dir_name), local_dir)
            remote_path = os.path.join(remote_dir, rel_path).replace("\\", "/")
            try:
                sftp.mkdir(remote_path)
            except:
                pass
        
        for file_name in files:
            local_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(local_path, local_dir)
            remote_path = os.path.join(remote_dir, rel_path).replace("\\", "/")
            
            print(f"Uploading: {rel_path}")
            try:
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"Warning: {e}")

def main():
    print("=" * 60)
    print("DEPLOYING BACKEND API")
    print("=" * 60)
    print()
    
    if not os.path.exists('backend'):
        print("[ERROR] backend directory not found!")
        return False
    
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Create backend directory
        print("=== Creating backend directory ===")
        execute_command(ssh, f"mkdir -p {BACKEND_DIR}")
        print()
        
        # Upload backend files
        print("=== Uploading backend files ===")
        sftp = ssh.open_sftp()
        upload_directory(sftp, 'backend', BACKEND_DIR)
        sftp.close()
        print()
        
        # Install dependencies
        print("=== Installing dependencies ===")
        execute_command(ssh, f"cd {BACKEND_DIR} && npm install")
        print()
        
        # Create .env file
        print("=== Creating .env file ===")
        env_content = f"""# Database
DB_HOST=9558e7dd68bdade50224f6f1.twc1.net
DB_PORT=5432
DB_NAME=db_21day
DB_USER=gen_user
DB_PASSWORD=kQIXN6%3B%7DFrB3ZA

# JWT
JWT_SECRET=change-this-secret-key-in-production-{os.urandom(16).hex()}

# OpenAI (set your key)
OPENAI_API_KEY=your-openai-api-key

# Server
PORT=3001
NODE_ENV=production
FRONTEND_URL=https://{DOMAIN}
"""
        cmd = f"""cat > {BACKEND_DIR}/.env << 'EOF'
{env_content}
EOF"""
        execute_command(ssh, cmd)
        print()
        
        # Create systemd service
        print("=== Creating systemd service ===")
        service_content = f"""[Unit]
Description=21day API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={BACKEND_DIR}
Environment="NODE_ENV=production"
ExecStart=/usr/bin/node {BACKEND_DIR}/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        cmd = f"""cat > /etc/systemd/system/21day-api.service << 'EOF'
{service_content}
EOF"""
        execute_command(ssh, cmd)
        
        # Reload systemd and start service
        execute_command(ssh, "systemctl daemon-reload")
        execute_command(ssh, "systemctl enable 21day-api")
        execute_command(ssh, "systemctl restart 21day-api")
        execute_command(ssh, "systemctl status 21day-api --no-pager | head -10")
        print()
        
        # Update Nginx to proxy API requests
        print("=== Updating Nginx configuration ===")
        nginx_config = f"""# Redirect www to non-www
server {{
    listen 80;
    listen [::]:80;
    server_name www.{DOMAIN};
    return 301 http://{DOMAIN}$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.{DOMAIN};
    
    ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    return 301 https://{DOMAIN}$request_uri;
}}

# Main server block
server {{
    listen 80;
    listen [::]:80;
    server_name {DOMAIN};
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {DOMAIN};
    
    root {APP_DIR}/dist;
    index index.html;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # API proxy
    location /api {{
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }}
    
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
        execute_command(ssh, "nginx -t")
        execute_command(ssh, "systemctl reload nginx")
        print()
        
        print("=" * 60)
        print("[OK] Backend API deployed!")
        print("=" * 60)
        print()
        print(f"API available at: https://{DOMAIN}/api")
        print(f"Backend directory: {BACKEND_DIR}")
        print()
        print("Next steps:")
        print("1. Set OPENAI_API_KEY in .env file")
        print("2. Update JWT_SECRET in .env file")
        print("3. Restart service: systemctl restart 21day-api")
        
        ssh.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

if __name__ == "__main__":
    main()

