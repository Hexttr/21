#!/usr/bin/env python3
"""Update backend to use Supabase PostgreSQL connection"""

import paramiko
import os

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"
BACKEND_DIR = "/var/www/21day.club-api"

def update_database_config(ssh, connection_string):
    """Update database.js with Supabase connection"""
    print("=" * 60)
    print("UPDATING BACKEND FOR SUPABASE POSTGRESQL")
    print("=" * 60)
    print()
    
    # Read current database.js
    sftp = ssh.open_sftp()
    
    # Read current file
    try:
        with sftp.open(f"{BACKEND_DIR}/config/database.js", "r") as f:
            current_content = f.read().decode('utf-8')
    except:
        print("[ERROR] Could not read database.js")
        return False
    
    # Create new content with Supabase connection
    new_content = f'''import pg from 'pg';
import fs from 'fs';
import path from 'path';
import {{ fileURLToPath }} from 'url';
import os from 'os';

const {{ Pool }} = pg;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Supabase PostgreSQL connection string
// Get from: Supabase Dashboard -> Settings -> Database -> Connection string -> URI
const connectionString = process.env.DATABASE_URL || '{connection_string}';

// Database connection configuration
const dbConfig = {{
  connectionString: connectionString,
  ssl: {{
    rejectUnauthorized: true,
  }},
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
}};

// Create connection pool
const pool = new Pool(dbConfig);

// Test connection
pool.on('connect', () => {{
  console.log('[DB] Connected to Supabase PostgreSQL');
}});

pool.on('error', (err) => {{
  console.error('[DB] Unexpected error on idle client', err);
  process.exit(-1);
}});

// Helper function to execute queries
export const query = async (text, params) => {{
  const start = Date.now();
  try {{
    const res = await pool.query(text, params);
    const duration = Date.now() - start;
    console.log('[DB] Executed query', {{ text: text.substring(0, 50), duration, rows: res.rowCount }});
    return res;
  }} catch (error) {{
    console.error('[DB] Query error', {{ text: text.substring(0, 50), error: error.message }});
    throw error;
  }}
}};

// Helper to get a client from the pool
export const getClient = () => {{
  return pool.connect();
}};

export default pool;
'''
    
    # Write new file
    try:
        with sftp.open(f"{BACKEND_DIR}/config/database.js", "w") as f:
            f.write(new_content.encode('utf-8'))
        print("[OK] database.js updated")
    except Exception as e:
        print(f"[ERROR] Could not write database.js: {e}")
        return False
    
    sftp.close()
    return True

def update_env_file(ssh, connection_string, jwt_secret):
    """Update .env file on server"""
    print()
    print("=== Updating .env file ===")
    
    env_content = f'''# Database
DATABASE_URL={connection_string}

# JWT Secret
JWT_SECRET={jwt_secret}

# OpenAI API Key (optional)
OPENAI_API_KEY=

# Server Port
PORT=3001
'''
    
    sftp = ssh.open_sftp()
    try:
        with sftp.open(f"{BACKEND_DIR}/.env", "w") as f:
            f.write(env_content.encode('utf-8'))
        print("[OK] .env file updated")
    except Exception as e:
        print(f"[ERROR] Could not write .env: {e}")
        return False
    
    sftp.close()
    return True

def restart_backend(ssh):
    """Restart backend service"""
    print()
    print("=== Restarting backend ===")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart 21day-api")
    stdout.channel.recv_exit_status()
    
    import time
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command("systemctl is-active 21day-api")
    status = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"Service status: {status}")
    
    if status == "active":
        print("[OK] Backend restarted successfully")
        return True
    else:
        print("[ERROR] Backend failed to start")
        # Show logs
        stdin, stdout, stderr = ssh.exec_command("journalctl -u 21day-api -n 20 --no-pager | tail -20")
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        return False

def main():
    print("=" * 60)
    print("UPDATE BACKEND FOR SUPABASE POSTGRESQL")
    print("=" * 60)
    print()
    print("Please provide:")
    print("1. PostgreSQL connection string from Supabase Dashboard")
    print("   (Settings -> Database -> Connection string -> URI)")
    print("2. JWT secret for backend")
    print()
    
    connection_string = input("Enter PostgreSQL connection string: ").strip()
    if not connection_string:
        print("[ERROR] Connection string is required")
        return
    
    jwt_secret = input("Enter JWT secret (or press Enter to use default): ").strip()
    if not jwt_secret:
        jwt_secret = "your-secret-key-change-in-production"
        print(f"[INFO] Using default JWT secret: {jwt_secret}")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected to server!")
        print()
        
        # Update files
        if update_database_config(ssh, connection_string):
            if update_env_file(ssh, connection_string, jwt_secret):
                if restart_backend(ssh):
                    print()
                    print("=" * 60)
                    print("[SUCCESS] Backend updated for Supabase PostgreSQL!")
                    print("=" * 60)
                else:
                    print()
                    print("=" * 60)
                    print("[ERROR] Backend restart failed")
                    print("=" * 60)
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

