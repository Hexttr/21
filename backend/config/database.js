import pg from 'pg';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';

const { Pool } = pg;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// SSL certificate path
const certPath = path.join(os.homedir(), '.cloud-certs', 'root.crt');

// Database connection configuration
// Using existing PostgreSQL database on Timeweb
const dbConfig = {
  host: process.env.DB_HOST || '9558e7dd68bdade50224f6f1.twc1.net',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'db_21day',
  user: process.env.DB_USER || 'gen_user',
  password: process.env.DB_PASSWORD || 'kQIXN6%3B%7DFrB3ZA',
  ssl: {
    rejectUnauthorized: true,
    ca: fs.existsSync(certPath) ? fs.readFileSync(certPath).toString() : undefined,
  },
  max: 20, // Maximum number of clients in the pool
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
};

// Create connection pool
const pool = new Pool(dbConfig);

// Test connection
pool.on('connect', () => {
  console.log('[DB] Connected to PostgreSQL (Timeweb)');
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

