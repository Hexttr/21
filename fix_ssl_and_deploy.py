#!/usr/bin/env python3
"""Fix SSL certificate issue and redeploy backend"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

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
    print("FIXING SSL AND REDEPLOYING BACKEND")
    print("=" * 60)
    print()
    
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Update database.js to fix SSL certificate issue
        print("=" * 60)
        print("Fixing SSL certificate configuration")
        print("=" * 60)
        
        new_db_config = """import pg from 'pg';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';

const { Pool } = pg;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// SSL certificate path
const certPath = path.join(os.homedir(), '.cloud-certs', 'root.crt');

// Use connection string directly (password is URL encoded)
const connectionString = 'postgresql://gen_user:kQIXN6%3B%7DFrB3ZA@9558e7dd68bdade50224f6f1.twc1.net:5432/db_21day?sslmode=verify-full';

// Database connection configuration
const dbConfig = {
  connectionString: connectionString,
  ssl: {
    rejectUnauthorized: true,
    ca: fs.existsSync(certPath) ? fs.readFileSync(certPath).toString() : undefined,
  },
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
};

// Create connection pool
const pool = new Pool(dbConfig);

// Test connection
pool.on('connect', () => {
  console.log('[DB] Connected to PostgreSQL');
});

pool.on('error', (err) => {
  console.error('[DB] Unexpected error on idle client', err);
  process.exit(-1);
});

// Helper function to execute queries
export const query = async (text, params) => {
  const start = Date.now();
  try {
    const res = await pool.query(text, params);
    const duration = Date.now() - start;
    console.log('[DB] Executed query', { text: text.substring(0, 50), duration, rows: res.rowCount });
    return res;
  } catch (error) {
    console.error('[DB] Query error', { text: text.substring(0, 50), error: error.message });
    throw error;
  }
};

// Helper to get a client from the pool
export const getClient = () => {
  return pool.connect();
};

export default pool;
"""
        
        cmd = f"""cat > /var/www/21day.club-api/config/database.js << 'EOF'
{new_db_config}
EOF"""
        execute_command(ssh, cmd)
        print()
        
        # Upload fixed ai.js
        print("=" * 60)
        print("Uploading fixed ai.js")
        print("=" * 60)
        
        # Read local ai.js
        with open('backend/routes/ai.js', 'r', encoding='utf-8') as f:
            ai_content = f.read()
        
        sftp = ssh.open_sftp()
        with sftp.open('/var/www/21day.club-api/routes/ai.js', 'w') as f:
            f.write(ai_content)
        sftp.close()
        print("[OK] ai.js uploaded")
        print()
        
        # Test connection with better error handling
        print("=" * 60)
        print("Testing database connection")
        print("=" * 60)
        
        cmd = """cd /var/www/21day.club-api && node -e "
import('./config/database.js').then(async (db) => {
  try {
    const result = await db.query('SELECT current_database(), current_user');
    console.log('[OK] Connected!');
    console.log('Database:', result.rows[0].current_database);
    console.log('User:', result.rows[0].current_user);
  } catch (e) {
    console.log('[ERROR]', e.message);
    if (e.message.includes('permission denied')) {
      console.log('Need CONNECT privilege for user gen_user on database db_21day');
    }
  }
  process.exit(0);
});
" 2>&1"""
        execute_command(ssh, cmd)
        print()
        
        # Restart backend
        print("=" * 60)
        print("Restarting backend service")
        print("=" * 60)
        execute_command(ssh, "systemctl restart 21day-api")
        execute_command(ssh, "sleep 3")
        execute_command(ssh, "systemctl is-active 21day-api && echo 'Service is running' || echo 'Service failed'")
        print()
        
        # Check logs
        print("=" * 60)
        print("Recent logs")
        print("=" * 60)
        execute_command(ssh, "journalctl -u 21day-api -n 10 --no-pager | tail -10")
        print()
        
        ssh.close()
        
        print("=" * 60)
        print("[INFO] Backend updated!")
        print("=" * 60)
        print()
        print("If you see 'permission denied' error:")
        print("  - Request CONNECT privilege for user 'gen_user' on database 'db_21day'")
        print("  - Or check if data is in a different database")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

