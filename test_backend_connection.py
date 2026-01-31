#!/usr/bin/env python3
"""Test backend connection to PostgreSQL database"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

def test_backend_connection():
    """Test if backend can connect to database"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected to server!")
        print()
        
        # Check backend logs
        print("=== Checking backend logs ===")
        stdin, stdout, stderr = ssh.exec_command("journalctl -u 21day-api -n 30 --no-pager | tail -30")
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        print()
        
        # Test API health endpoint
        print("=== Testing API health endpoint ===")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:3001/health")
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        print()
        
        # Test database connection via backend
        print("=== Testing database connection via backend ===")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:3001/api/health 2>&1 || echo 'Endpoint not available'")
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backend_connection()

