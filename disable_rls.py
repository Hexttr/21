#!/usr/bin/env python3
"""Temporary solution: Disable RLS for backend access"""

import paramiko
import os

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

# Database connection
DB_CONNECTION_STRING = "postgresql://gen_user:kQIXN6%3B%7DFrB3ZA@9558e7dd68bdade50224f6f1.twc1.net:5432/db_21day?sslmode=verify-full"
CERT_PATH = "~/.cloud-certs/root.crt"

def execute_sql(ssh, sql_file):
    """Execute SQL file on server"""
    print("=" * 60)
    print("TEMPORARY SOLUTION: Disabling RLS for backend access")
    print("=" * 60)
    print()
    print("WARNING: This is a TEMPORARY solution for quick startup.")
    print("   For production, use SECURITY DEFINER functions or proper RLS policies.")
    print()
    
    # Read SQL file
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Upload SQL file to server
    print("=== Uploading SQL script ===")
    sftp = ssh.open_sftp()
    remote_sql_path = "/tmp/disable_rls.sql"
    sftp.put(sql_file, remote_sql_path)
    sftp.close()
    print("[OK] SQL script uploaded")
    print()
    
    # Execute SQL
    print("=== Executing SQL script ===")
    cmd = f'export PGSSLROOTCERT={CERT_PATH} && psql "{DB_CONNECTION_STRING}" -f {remote_sql_path}'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    error_output = stderr.read().decode('utf-8', errors='ignore')
    
    if exit_status == 0:
        print(output)
        print()
        print("[OK] RLS disabled successfully!")
        print()
        print("REMEMBER: This is a temporary solution.")
        print("   Plan to implement proper RLS policies or SECURITY DEFINER functions.")
    else:
        print("[ERROR] Failed to execute SQL:")
        print(error_output)
        if output:
            print("Output:", output)
    
    # Cleanup
    ssh.exec_command(f"rm -f {remote_sql_path}")
    
    return exit_status == 0

def test_connection(ssh):
    """Test database connection after RLS disable"""
    print("=== Testing database access ===")
    
    test_query = '''
    SELECT 
        (SELECT COUNT(*) FROM public.profiles) as profiles_count,
        (SELECT COUNT(*) FROM public.user_roles) as roles_count,
        (SELECT COUNT(*) FROM public.lesson_content) as lessons_count,
        (SELECT COUNT(*) FROM public.student_progress) as progress_count;
    '''
    
    cmd = f'export PGSSLROOTCERT={CERT_PATH} && psql "{DB_CONNECTION_STRING}" -c "{test_query}"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    
    if exit_status == 0:
        print(output)
        print("[OK] Database access test successful!")
    else:
        error_output = stderr.read().decode('utf-8', errors='ignore')
        print("[ERROR] Database access test failed:")
        print(error_output)
    
    return exit_status == 0

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected to server!")
        print()
        
        # Execute SQL
        success = execute_sql(ssh, "disable_rls_temporary.sql")
        
        if success:
            # Test connection
            test_connection(ssh)
            print()
            print("=" * 60)
            print("[SUCCESS] RLS disabled. Backend should now have access.")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print("[ERROR] Failed to disable RLS")
            print("=" * 60)
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

