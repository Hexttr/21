#!/usr/bin/env python3
"""Test database connection from server"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

DB_CONNECTION_STRING = "postgresql://gen_user:kQIXN6%3B%7DFrB3ZA@9558e7dd68bdade50224f6f1.twc1.net:5432/db_21day?sslmode=verify-full"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected to server!")
        print()
        
        # Test connection
        print("=== Testing database connection ===")
        cmd = f'export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && psql "{DB_CONNECTION_STRING}" -c "SELECT version();"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='ignore')
        error_output = stderr.read().decode('utf-8', errors='ignore')
        
        if exit_status == 0:
            print(output)
            print("[OK] Connection successful!")
        else:
            print("[ERROR] Connection failed:")
            print(error_output)
            if output:
                print("Output:", output)
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

