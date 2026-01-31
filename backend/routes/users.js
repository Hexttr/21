import express from 'express';
import { authenticate, requireAdmin } from '../middleware/auth.js';
import { query } from '../config/database.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// Get current user profile
router.get('/me', async (req, res) => {
  try {
    const { userId } = req.user;

    const result = await query(
      `SELECT 
        u.id,
        u.email,
        up.name,
        up.blocked,
        EXISTS(SELECT 1 FROM public.user_roles WHERE user_id = $1 AND role = 'admin') as is_admin
       FROM auth.users u
       LEFT JOIN public.user_profiles up ON u.id = up.user_id
       WHERE u.id = $1`,
      [userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('[USERS] Get me error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Admin: Get all users
router.get('/all', requireAdmin, async (req, res) => {
  try {
    const result = await query(
      `SELECT 
        u.id,
        u.email,
        up.name,
        up.blocked,
        u.created_at,
        ARRAY_AGG(ur.role) as roles
       FROM auth.users u
       LEFT JOIN public.user_profiles up ON u.id = up.user_id
       LEFT JOIN public.user_roles ur ON u.id = ur.user_id
       GROUP BY u.id, u.email, up.name, up.blocked, u.created_at
       ORDER BY u.created_at DESC`
    );

    res.json(result.rows);
  } catch (error) {
    console.error('[USERS] Get all error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;

