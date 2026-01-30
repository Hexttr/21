#!/usr/bin/env python3
"""Install SSL certificate for 21day.club"""

import paramiko

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
    print("INSTALLING SSL CERTIFICATE FOR 21day.club")
    print("=" * 60)
    print()
    
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Check current certificate status
        print("=== Checking current SSL certificates ===")
        execute_command(ssh, "certbot certificates")
        print()
        
        # Install SSL certificate
        print("=== Installing SSL certificate ===")
        certbot_cmd = f"certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email admin@{DOMAIN} --redirect"
        success, output = execute_command(ssh, certbot_cmd)
        
        if success:
            print()
            print("[OK] SSL certificate installed successfully!")
            print()
            
            # Verify certificate
            print("=== Verifying SSL certificate ===")
            execute_command(ssh, "certbot certificates")
            print()
            
            # Check Nginx configuration
            print("=== Checking Nginx SSL configuration ===")
            execute_command(ssh, f"grep -A 5 'listen 443' /etc/nginx/sites-available/{DOMAIN} | head -10")
            print()
            
            # Test Nginx configuration
            print("=== Testing Nginx configuration ===")
            execute_command(ssh, "nginx -t")
            print()
            
            # Reload Nginx
            print("=== Reloading Nginx ===")
            execute_command(ssh, "systemctl reload nginx")
            print()
            
            print("=" * 60)
            print("[SUCCESS] SSL certificate installed and configured!")
            print("=" * 60)
            print()
            print(f"Application is now available at:")
            print(f"  - https://{DOMAIN}")
            print(f"  - https://www.{DOMAIN}")
            print()
            print("HTTP requests will be automatically redirected to HTTPS.")
            
        else:
            print()
            print("[ERROR] SSL certificate installation failed!")
            print("Please check the error messages above.")
            print()
            print("Common issues:")
            print("1. DNS might not be fully propagated yet")
            print("2. Port 80 might not be accessible from internet")
            print("3. Firewall might be blocking connections")
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

