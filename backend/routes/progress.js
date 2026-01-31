import express from 'express';
import { authenticate } from '../middleware/auth.js';
import { query } from '../config/database.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// Get user progress
router.get('/me', async (req, res) => {
  try {
    const { userId } = req.user;

    const result = await query(
      `SELECT 
        id,
        user_id,
        lesson_id,
        completed,
        quiz_completed,
        completed_at,
        created_at
       FROM public.student_progress 
       WHERE user_id = $1
       ORDER BY lesson_id`,
      [userId]
    );

    res.json(result.rows);
  } catch (error) {
    console.error('[PROGRESS] Get progress error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update progress
router.post('/:lessonId', async (req, res) => {
  try {
    const { userId } = req.user;
    const { lessonId } = req.params;
    const { completed, quiz_completed } = req.body;

    const result = await query(
      `INSERT INTO public.student_progress (user_id, lesson_id, completed, quiz_completed, completed_at)
       VALUES ($1, $2, $3, $4, CASE WHEN $3 = true THEN NOW() ELSE NULL END)
       ON CONFLICT (user_id, lesson_id) 
       DO UPDATE SET 
         completed = COALESCE(EXCLUDED.completed, student_progress.completed),
         quiz_completed = COALESCE(EXCLUDED.quiz_completed, student_progress.quiz_completed),
         completed_at = CASE WHEN EXCLUDED.completed = true THEN NOW() ELSE student_progress.completed_at END
       RETURNING *`,
      [userId, lessonId, completed || false, quiz_completed || false]
    );

    res.json(result.rows[0]);
  } catch (error) {
    console.error('[PROGRESS] Update progress error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;

