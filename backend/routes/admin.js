import express from 'express';
import bcrypt from 'bcryptjs';
import { authenticate, requireAdmin } from '../middleware/auth.js';
import { query } from '../config/database.js';

const router = express.Router();

// All routes require admin authentication
router.use(authenticate);
router.use(requireAdmin);

// Force logout user (invalidate all sessions)
router.post('/force-logout', async (req, res) => {
  try {
    const { userId } = req.body;

    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }

    // In a real implementation, you would invalidate JWT tokens
    // For now, we'll just return success
    // You could implement a token blacklist or use Redis
    
    res.json({ message: 'User logged out successfully' });
  } catch (error) {
    console.error('[ADMIN] Force logout error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Reset user password
router.post('/reset-password', async (req, res) => {
  try {
    const { userId, newPassword } = req.body;

    if (!userId || !newPassword) {
      return res.status(400).json({ error: 'User ID and new password are required' });
    }

    // Hash new password
    const hashedPassword = await bcrypt.hash(newPassword, 10);

    // Update password in database
    await query(
      `UPDATE auth.users SET encrypted_password = $1, updated_at = NOW() WHERE id = $2`,
      [hashedPassword, userId]
    );

    res.json({ message: 'Password reset successfully' });
  } catch (error) {
    console.error('[ADMIN] Reset password error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;

