import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

export const authenticate = (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'No token provided' });
    }

    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, JWT_SECRET);
    
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

export const requireAdmin = async (req, res, next) => {
  try {
    const { query } = await import('../config/database.js');
    const { userId } = req.user;

    const result = await query(
      `SELECT role FROM public.user_roles WHERE user_id = $1 AND role = 'admin'`,
      [userId]
    );

    if (result.rows.length === 0) {
      return res.status(403).json({ error: 'Admin access required' });
    }

    next();
  } catch (error) {
    console.error('[AUTH] Admin check error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

