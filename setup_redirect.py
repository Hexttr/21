#!/usr/bin/env python3
"""Setup redirect from www to non-www (or vice versa) and test site"""

import paramiko
import requests
import webbrowser
import time

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
DOMAIN = "21day.club"

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
    print("=" * 60)
    print("SETTING UP REDIRECT AND TESTING SITE")
    print("=" * 60)
    print()
    
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Read current Nginx configuration
        print("=== Reading current Nginx configuration ===")
        success, config = execute_command(ssh, f"cat /etc/nginx/sites-available/{DOMAIN}")
        print()
        
        # Setup redirect: www -> non-www (21day.club is primary)
        print("=== Setting up redirect: www -> non-www ===")
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
    
    root /var/www/{DOMAIN}/dist;
    index index.html;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
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
        print()
        
        # Test Nginx configuration
        print("=== Testing Nginx configuration ===")
        execute_command(ssh, "nginx -t")
        print()
        
        # Reload Nginx
        print("=== Reloading Nginx ===")
        execute_command(ssh, "systemctl reload nginx")
        print()
        
        print("[OK] Redirect configured!")
        print("www.21day.club will redirect to 21day.club")
        print()
        
        ssh.close()
        
        # Test site accessibility
        print("=" * 60)
        print("TESTING SITE ACCESSIBILITY")
        print("=" * 60)
        print()
        
        urls = [
            f"https://{DOMAIN}",
            f"https://www.{DOMAIN}",
            f"http://{DOMAIN}",
            f"http://www.{DOMAIN}"
        ]
        
        for url in urls:
            try:
                print(f"Testing: {url}")
                response = requests.get(url, timeout=10, allow_redirects=True)
                print(f"  Status: {response.status_code}")
                print(f"  Final URL: {response.url}")
                if response.status_code == 200:
                    print(f"  [OK] Site is accessible!")
                    print(f"  Content length: {len(response.content)} bytes")
                print()
            except Exception as e:
                print(f"  [ERROR] {str(e)}")
                print()
        
        # Try to open in browser
        print("=" * 60)
        print("OPENING IN BROWSER")
        print("=" * 60)
        print()
        
        main_url = f"https://{DOMAIN}"
        print(f"Opening: {main_url}")
        try:
            webbrowser.open(main_url)
            print("[OK] Browser should open now!")
        except Exception as e:
            print(f"[WARNING] Could not open browser automatically: {str(e)}")
            print(f"Please open manually: {main_url}")
        
        print()
        print("=" * 60)
        print("[SUCCESS] Configuration complete!")
        print("=" * 60)
        print()
        print("Redirects configured:")
        print(f"  http://www.{DOMAIN} -> https://{DOMAIN}")
        print(f"  https://www.{DOMAIN} -> https://{DOMAIN}")
        print(f"  http://{DOMAIN} -> https://{DOMAIN}")
        print()
        print(f"Main site: https://{DOMAIN}")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

