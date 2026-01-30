#!/usr/bin/env python3
"""Check DNS and install SSL for 21day.club"""

import paramiko
import socket

SERVER_IP = "195.133.63.34"
DOMAIN = "21day.club"

def check_dns(domain):
    """Check DNS resolution"""
    try:
        ip = socket.gethostbyname(domain)
        print(f"{domain} -> {ip}")
        if ip == SERVER_IP:
            print(f"[OK] DNS correctly points to {SERVER_IP}")
            return True
        else:
            print(f"[WARNING] DNS points to {ip}, but server is at {SERVER_IP}")
            print(f"Please update DNS A record: {domain} -> {SERVER_IP}")
            return False
    except socket.gaierror as e:
        print(f"[ERROR] DNS resolution failed: {e}")
        return False

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
    print("DNS CHECK FOR 21day.club")
    print("=" * 60)
    print()
    
    # Check DNS
    print("=== Checking DNS ===")
    main_ok = check_dns(DOMAIN)
    print()
    www_ok = check_dns(f"www.{DOMAIN}")
    print()
    
    if not main_ok or not www_ok:
        print("[WARNING] DNS is not pointing to the correct server!")
        print(f"Current DNS: points to different IP")
        print(f"Server IP: {SERVER_IP}")
        print()
        print("Please update DNS records:")
        print(f"  A record: {DOMAIN} -> {SERVER_IP}")
        print(f"  A record: www.{DOMAIN} -> {SERVER_IP}")
        print()
        print("After updating DNS, wait 5-30 minutes and run this script again.")
        return
    
    print("[OK] DNS is correctly configured!")
    print()
    
    # Connect to server and install SSL
    print("=== Connecting to server ===")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username="root", password="hdp-k.PD6u8K7U", timeout=30)
        print("[OK] Connected!")
        print()
        
        # Install SSL certificate
        print("=== Installing SSL certificate ===")
        certbot_cmd = f"certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email admin@{DOMAIN} --redirect"
        success, output = execute_command(ssh, certbot_cmd, check=False)
        
        if success:
            print()
            print("[OK] SSL certificate installed successfully!")
            print(f"Application is now available at https://{DOMAIN}")
        else:
            print()
            print("[WARNING] SSL installation might have failed.")
            print("This could be because:")
            print("1. DNS is still propagating (wait a bit longer)")
            print("2. DNS is not pointing to this server")
            print("3. Port 80 is not accessible from internet")
            print()
            print("You can try manually:")
            print(f"  ssh root@{SERVER_IP}")
            print(f"  {certbot_cmd}")
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

