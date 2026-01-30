#!/usr/bin/env python3
"""Test SSH connection to server"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

print("Testing SSH connection...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
    print("[OK] Connected successfully!")
    
    stdin, stdout, stderr = ssh.exec_command("uname -a")
    output = stdout.read().decode('utf-8')
    print(f"System info: {output}")
    
    ssh.close()
    print("[OK] Connection test passed!")
except Exception as e:
    print(f"[ERROR] Connection failed: {str(e)}")

