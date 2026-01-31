#!/usr/bin/env python3
"""Update backend to use correct database connection string"""

import paramiko

SERVER_IP = "195.133.63.34"
SERVER_USER = "root"
SERVER_PASSWORD = "hdp-k.PD6u8K7U"

# Original connection string from user
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
    if error.strip():
        print(f"Error: {error}")
    
    return exit_status == 0, output

def main():
    print("=" * 60)
    print("UPDATING BACKEND DATABASE CONNECTION")
    print("=" * 60)
    print()
    
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
        print("[OK] Connected!")
        print()
        
        # Update database.js to use connection string directly
        print("=" * 60)
        print("Updating database.js to use connection string")
        print("=" * 60)
        
        # Read current database.js
        sftp = ssh.open_sftp()
        try:
            with sftp.open('/var/www/21day.club-api/config/database.js', 'r') as f:
                current_content = f.read().decode('utf-8')
        except:
            current_content = ""
        sftp.close()
        
        # Create new database.js that uses connection string
        new_db_config = f"""import pg from 'pg';
import fs from 'fs';
import path from 'path';
import {{ fileURLToPath }} from 'url';
import os from 'os';

const {{ Pool }} = pg;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// SSL certificate path
const certPath = path.join(os.homedir(), '.cloud-certs', 'root.crt');

// Use connection string directly (password is URL encoded)
const connectionString = '{DB_CONNECTION_STRING}';

// Database connection configuration
const dbConfig = {{
  connectionString: connectionString,
  ssl: {{
    rejectUnauthorized: true,
    ca: fs.readFileSync(certPath).toString(),
  }},
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
}};

// Create connection pool
const pool = new Pool(dbConfig);

// Test connection
pool.on('connect', () => {{
  console.log('[DB] Connected to PostgreSQL');
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
"""
        
        # Write new database.js
        cmd = f"""cat > /var/www/21day.club-api/config/database.js << 'EOF'
{new_db_config}
EOF"""
        execute_command(ssh, cmd)
        print()
        
        # Test connection
        print("=" * 60)
        print("Testing database connection")
        print("=" * 60)
        
        cmd = """cd /var/www/21day.club-api && node -e "
import('./config/database.js').then(async (db) => {
  try {
    const result = await db.query('SELECT current_database(), current_user, version()');
    console.log('[OK] Connected successfully!');
    console.log('Database:', result.rows[0].current_database);
    console.log('User:', result.rows[0].current_user);
    
    // Try to list tables
    const tables = await db.query(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name LIMIT 10\");
    console.log('Tables found:', tables.rows.length);
    tables.rows.forEach(r => console.log('  -', r.table_name));
  } catch (e) {
    console.log('[ERROR] Connection failed:', e.message);
    console.log(e.stack);
  }
  process.exit(0);
}).catch(e => {
  console.log('[ERROR] Import failed:', e.message);
  process.exit(1);
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
        execute_command(ssh, "systemctl status 21day-api --no-pager | head -15")
        print()
        
        # Test API
        print("=" * 60)
        print("Testing API endpoint")
        print("=" * 60)
        execute_command(ssh, "curl -s http://localhost:3001/health || echo 'API not responding'")
        print()
        
        ssh.close()
        
        print("=" * 60)
        print("[INFO] Backend updated!")
        print("=" * 60)
        print()
        print("If connection still fails, you may need to:")
        print("1. Request CONNECT privilege for user 'gen_user' on database 'db_21day'")
        print("2. Or check if data is in a different database")
        print("3. Or verify the connection string with Timeweb support")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

