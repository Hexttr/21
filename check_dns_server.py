#!/usr/bin/env python3
"""Check DNS and SSL status on server"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
DOMAIN = "21days.club"

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
        
        # Check DNS resolution from server
        print("=== Checking DNS resolution from server ===")
        execute_command(ssh, f"host {DOMAIN}")
        execute_command(ssh, f"host www.{DOMAIN}")
        execute_command(ssh, f"dig +short {DOMAIN}")
        execute_command(ssh, f"dig +short www.{DOMAIN}")
        
        # Check if domain points to this server
        print("\n=== Checking if domain points to this server ===")
        success, output = execute_command(ssh, f"hostname -I")
        server_ips = output.strip().split()
        print(f"Server IPs: {server_ips}")
        
        # Check SSL certificate status
        print("\n=== Checking SSL certificate status ===")
        execute_command(ssh, "certbot certificates")
        
        # Check Nginx configuration
        print("\n=== Checking Nginx server_name ===")
        execute_command(ssh, f"grep server_name /etc/nginx/sites-available/{DOMAIN}")
        
        # Try to get certificate (this will show DNS error if DNS is not configured)
        print("\n=== Testing SSL certificate request ===")
        print("(This will fail if DNS is not configured)")
        execute_command(ssh, f"certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --dry-run --non-interactive --agree-tos --email admin@{DOMAIN}", check=False)
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

