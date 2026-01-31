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

// Admin: Get all users with profiles and progress
router.get('/all', requireAdmin, async (req, res) => {
  try {
    // Get profiles
    const profilesResult = await query(
      `SELECT 
        user_id,
        name,
        email,
        blocked,
        invitation_code_id
       FROM public.profiles
       ORDER BY created_at DESC`
    );

    // Get invitation codes
    let codesResult;
    try {
      codesResult = await query(
        `SELECT id, comment FROM public.invitation_codes`
      );
    } catch (e) {
      codesResult = { rows: [] };
    }

    // Get progress
    const progressResult = await query(
      `SELECT 
        user_id,
        lesson_id,
        completed,
        quiz_completed
       FROM public.student_progress`
    );

    // Get roles
    const rolesResult = await query(
      `SELECT user_id, role FROM public.user_roles`
    );

    // Combine data
    const codeMap = new Map();
    codesResult.rows.forEach((c) => codeMap.set(c.id, c.comment));

    const progressMap = new Map();
    progressResult.rows.forEach((p) => {
      if (!progressMap.has(p.user_id)) {
        progressMap.set(p.user_id, []);
      }
      progressMap.get(p.user_id).push(p);
    });

    const rolesMap = new Map();
    rolesResult.rows.forEach((r) => {
      if (!rolesMap.has(r.user_id)) {
        rolesMap.set(r.user_id, []);
      }
      rolesMap.get(r.user_id).push(r.role);
    });

    const users = profilesResult.rows.map((profile) => {
      const userProgress = progressMap.get(profile.user_id) || [];
      const roles = rolesMap.get(profile.user_id) || [];
      
      return {
        user_id: profile.user_id,
        email: profile.email,
        name: profile.name,
        is_blocked: profile.blocked || false,
        invitation_code_comment: profile.invitation_code_id ? codeMap.get(profile.invitation_code_id) : null,
        completed_lessons: userProgress.filter((p) => p.completed).length,
        quiz_completed: userProgress.filter((p) => p.quiz_completed).length,
        roles: roles,
      };
    });

    res.json(users);
  } catch (error) {
    console.error('[USERS] Get all error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Admin: Update user profile
router.patch('/:userId/profile', requireAdmin, async (req, res) => {
  try {
    const { userId } = req.params;
    const { name, blocked } = req.body;

    const updates = [];
    const values = [];
    let paramIndex = 1;

    if (name !== undefined) {
      updates.push(`name = $${paramIndex++}`);
      values.push(name);
    }

    if (blocked !== undefined) {
      updates.push(`blocked = $${paramIndex++}`);
      values.push(blocked);
      if (blocked) {
        updates.push(`blocked_at = NOW()`);
      } else {
        updates.push(`blocked_at = NULL`);
      }
    }

    if (updates.length === 0) {
      return res.status(400).json({ error: 'No fields to update' });
    }

    values.push(userId);

    await query(
      `UPDATE public.profiles 
       SET ${updates.join(', ')}, updated_at = NOW()
       WHERE user_id = $${paramIndex}`,
      values
    );

    res.json({ message: 'Profile updated successfully' });
  } catch (error) {
    console.error('[USERS] Update profile error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;

