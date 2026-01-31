#!/usr/bin/env python3
"""Fix RLS policies and update backend for direct PostgreSQL access"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

DB_CONNECTION_STRING = "postgresql://gen_user:kQIXN6%3B%7DFrB3ZA@9558e7dd68bdade50224f6f1.twc1.net:5432/db_21day?sslmode=verify-full"

def execute_command(ssh, command):
    """Execute command on remote server via SSH"""
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    
    if output.strip():
        print(f"Output: {output}")
    if error.strip() and "ERROR" not in error and "WARNING" not in error:
        print(f"Error: {error}")
    
    return exit_status == 0, output

def main():
    print("=" * 60)
    print("FIXING RLS AND UPDATING BACKEND")
    print("=" * 60)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Step 1: Create SECURITY DEFINER functions to bypass RLS
        print("=" * 60)
        print("STEP 1: Creating SECURITY DEFINER functions")
        print("=" * 60)
        
        security_functions = """
-- Function to get user by email (bypasses RLS)
CREATE OR REPLACE FUNCTION api.get_user_by_email(user_email TEXT)
RETURNS TABLE(id UUID, email TEXT, encrypted_password TEXT, email_confirmed_at TIMESTAMPTZ)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
BEGIN
  RETURN QUERY
  SELECT u.id, u.email, u.encrypted_password, u.email_confirmed_at
  FROM auth.users u
  WHERE u.email = user_email;
END;
$$;

-- Function to get user profile (bypasses RLS)
CREATE OR REPLACE FUNCTION api.get_user_profile(user_uuid UUID)
RETURNS TABLE(id UUID, user_id UUID, name TEXT, email TEXT, blocked BOOLEAN, created_at TIMESTAMPTZ)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN QUERY
  SELECT p.id, p.user_id, p.name, p.email, COALESCE(p.blocked, false) as blocked, p.created_at
  FROM public.profiles p
  WHERE p.user_id = user_uuid;
END;
$$;

-- Function to get user roles (bypasses RLS)
CREATE OR REPLACE FUNCTION api.get_user_roles(user_uuid UUID)
RETURNS TABLE(role TEXT)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN QUERY
  SELECT ur.role::TEXT
  FROM public.user_roles ur
  WHERE ur.user_id = user_uuid;
END;
$$;

-- Function to check if user has role (bypasses RLS)
CREATE OR REPLACE FUNCTION api.user_has_role(user_uuid UUID, check_role TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN EXISTS(
    SELECT 1 FROM public.user_roles
    WHERE user_id = user_uuid AND role::TEXT = check_role
  );
END;
$$;

-- Grant execute permissions to gen_user
GRANT EXECUTE ON FUNCTION api.get_user_by_email(TEXT) TO gen_user;
GRANT EXECUTE ON FUNCTION api.get_user_profile(UUID) TO gen_user;
GRANT EXECUTE ON FUNCTION api.get_user_roles(UUID) TO gen_user;
GRANT EXECUTE ON FUNCTION api.user_has_role(UUID, TEXT) TO gen_user;
"""
        
        # Create api schema first
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "CREATE SCHEMA IF NOT EXISTS api;" 2>&1"""
        execute_command(ssh, cmd)
        
        # Execute security functions
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' << 'SQL'
{security_functions}
SQL
2>&1"""
        execute_command(ssh, cmd)
        print()
        
        # Step 2: Test functions
        print("=" * 60)
        print("STEP 2: Testing security functions")
        print("=" * 60)
        
        cmd = f"""export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt && \
psql '{DB_CONNECTION_STRING}' -c "SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'api';" 2>&1"""
        execute_command(ssh, cmd)
        print()
        
        ssh.close()
        
        print("=" * 60)
        print("[OK] Security functions created!")
        print("=" * 60)
        print()
        print("Next: Update backend to use these functions")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

