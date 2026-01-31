#!/usr/bin/env python3
"""Test backend after RLS is disabled"""

import paramiko
import requests
import json

SERVER_IP = "195.133.63.34"
API_URL = "https://21day.club/api"

def test_backend_after_rls_disable():
    """Test if backend can access database after RLS is disabled"""
    print("=" * 60)
    print("TESTING BACKEND AFTER RLS DISABLE")
    print("=" * 60)
    print()
    
    # Test 1: Health endpoint
    print("=== Test 1: Health endpoint ===")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Health endpoint works")
            print(f"Response: {response.json()}")
        else:
            print(f"[WARNING] Health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Health endpoint failed: {e}")
    print()
    
    # Test 2: Check backend logs
    print("=== Test 2: Backend logs ===")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username="root", password="hdp-k.PD6u8K7U", timeout=30)
        
        # Check for database connection errors
        stdin, stdout, stderr = ssh.exec_command("journalctl -u 21day-api -n 50 --no-pager | grep -i 'error\\|connected\\|query' | tail -20")
        output = stdout.read().decode('utf-8', errors='ignore')
        
        if output:
            print("Recent database-related logs:")
            print(output)
        else:
            print("[INFO] No recent database errors found")
        
        # Test database connection via backend (if endpoint exists)
        print()
        print("=== Test 3: Database access test ===")
        print("After RLS is disabled, backend should be able to:")
        print("  - Read from profiles table")
        print("  - Read from lesson_content table")
        print("  - Read from student_progress table")
        print()
        print("You can test this by calling API endpoints:")
        print(f"  GET {API_URL}/users/me (requires auth)")
        print(f"  GET {API_URL}/lessons/published")
        print()
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
    
    print()
    print("=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. If RLS is disabled, backend should work")
    print("2. Test API endpoints to verify data access")
    print("3. Continue migrating components to API")
    print("=" * 60)

if __name__ == "__main__":
    test_backend_after_rls_disable()

