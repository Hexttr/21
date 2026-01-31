import express from 'express';
import { authenticate } from '../middleware/auth.js';
import { query } from '../config/database.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// Get published lessons
router.get('/published', async (req, res) => {
  try {
    const result = await query(
      `SELECT * FROM public.lessons WHERE published = true ORDER BY week_number, day_number`
    );

    res.json(result.rows);
  } catch (error) {
    console.error('[LESSONS] Get published error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get lesson by ID
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query(
      `SELECT * FROM public.lessons WHERE id = $1`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Lesson not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('[LESSONS] Get lesson error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;

