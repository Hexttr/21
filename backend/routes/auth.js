import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { query } from '../config/database.js';

const router = express.Router();
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

// Helper to generate JWT token
const generateToken = (userId, email) => {
  return jwt.sign(
    { userId, email },
    JWT_SECRET,
    { expiresIn: '7d' }
  );
};

// Sign in
router.post('/signin', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    // Get user from database using SECURITY DEFINER function or direct query
    // Try using function first, fallback to direct query
    let userResult;
    try {
      userResult = await query(
        `SELECT * FROM api.get_user_by_email($1)`,
        [email.toLowerCase()]
      );
    } catch (e) {
      // Fallback: direct query (may need RLS bypass)
      userResult = await query(
        `SELECT id, email, encrypted_password, email_confirmed_at 
         FROM auth.users 
         WHERE email = $1`,
        [email.toLowerCase()]
      );
    }

    if (userResult.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const user = userResult.rows[0];

    // Check if user is blocked using function or direct query
    let blockedResult;
    try {
      blockedResult = await query(
        `SELECT blocked FROM api.get_user_profile($1)`,
        [user.id]
      );
    } catch (e) {
      // Fallback: direct query
      blockedResult = await query(
        `SELECT blocked FROM public.profiles WHERE user_id = $1`,
        [user.id]
      );
    }

    if (blockedResult.rows.length > 0 && blockedResult.rows[0].blocked) {
      return res.status(403).json({ error: 'Account is blocked' });
    }

    // Verify password (assuming bcrypt hash)
    // Note: You may need to adjust password verification based on your setup
    const isValidPassword = await bcrypt.compare(password, user.encrypted_password);

    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    // Check admin role using function or direct query
    let isAdmin = false;
    try {
      const roleResult = await query(
        `SELECT api.user_has_role($1, 'admin') as is_admin`,
        [user.id]
      );
      isAdmin = roleResult.rows[0]?.is_admin || false;
    } catch (e) {
      // Fallback: direct query
      const roleResult = await query(
        `SELECT role FROM public.user_roles WHERE user_id = $1 AND role = 'admin'`,
        [user.id]
      );
      isAdmin = roleResult.rows.length > 0;
    }

    // Generate token
    const token = generateToken(user.id, user.email);

    res.json({
      user: {
        id: user.id,
        email: user.email,
        isAdmin,
      },
      token,
    });
  } catch (error) {
    console.error('[AUTH] Sign in error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Sign up
router.post('/signup', async (req, res) => {
  try {
    const { email, password, name, invitationCode } = req.body;

    if (!email || !password || !name || !invitationCode) {
      return res.status(400).json({ error: 'All fields are required' });
    }

    // Validate invitation code
    // Note: invitation_codes table might not exist, check structure first
    let codeResult;
    try {
      codeResult = await query(
        `SELECT id, used FROM public.invitation_codes WHERE code = $1`,
        [invitationCode]
      );
    } catch (e) {
      // If table doesn't exist, create a simple validation
      // For now, return error - you may need to create this table
      return res.status(400).json({ error: 'Invitation code validation not available' });
    }

    if (codeResult.rows.length === 0) {
      return res.status(400).json({ error: 'Invalid invitation code' });
    }

    if (codeResult.rows[0].used) {
      return res.status(400).json({ error: 'Invitation code already used' });
    }

    // Check if user already exists
    const existingUser = await query(
      `SELECT id FROM auth.users WHERE email = $1`,
      [email.toLowerCase()]
    );

    if (existingUser.rows.length > 0) {
      return res.status(400).json({ error: 'User already exists' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user (you may need to adjust based on your auth.users schema)
    const userResult = await query(
      `INSERT INTO auth.users (email, encrypted_password, email_confirmed_at, created_at)
       VALUES ($1, $2, NOW(), NOW())
       RETURNING id, email`,
      [email.toLowerCase(), hashedPassword]
    );

    const user = userResult.rows[0];

    // Mark invitation code as used
    await query(
      `UPDATE public.invitation_codes SET used = true, used_by = $1, used_at = NOW() WHERE code = $2`,
      [user.id, invitationCode]
    );

    // Create user profile (using profiles table structure)
    await query(
      `INSERT INTO public.profiles (user_id, name, email, created_at, updated_at)
       VALUES ($1, $2, $3, NOW(), NOW())
       ON CONFLICT (user_id) DO UPDATE SET name = $2, email = $3, updated_at = NOW()`,
      [user.id, name, email.toLowerCase()]
    );

    // Create user role (default: student)
    await query(
      `INSERT INTO public.user_roles (user_id, role, created_at)
       VALUES ($1, 'student', NOW())`,
      [user.id]
    );

    // Generate token
    const token = generateToken(user.id, user.email);

    res.json({
      user: {
        id: user.id,
        email: user.email,
        isAdmin: false,
      },
      token,
    });
  } catch (error) {
    console.error('[AUTH] Sign up error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Sign out (client-side token removal, but we can add server-side invalidation)
router.post('/signout', async (req, res) => {
  res.json({ message: 'Signed out successfully' });
});

// Validate invitation code
router.post('/validate-code', async (req, res) => {
  try {
    const { code } = req.body;

    if (!code) {
      return res.status(400).json({ error: 'Code is required' });
    }

    const result = await query(
      `SELECT id, used FROM public.invitation_codes WHERE code = $1`,
      [code]
    );

    if (result.rows.length === 0) {
      return res.json({ valid: false, error: 'Invalid code' });
    }

    if (result.rows[0].used) {
      return res.json({ valid: false, error: 'Code already used' });
    }

    return res.json({ valid: true, codeId: result.rows[0].id });
  } catch (error) {
    console.error('[AUTH] Validate code error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;

