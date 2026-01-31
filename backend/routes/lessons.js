import express from 'express';
import { authenticate } from '../middleware/auth.js';
import { query } from '../config/database.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// Get published lessons
router.get('/published', async (req, res) => {
  try {
    // Use lesson_content table structure
    const result = await query(
      `SELECT 
        id,
        lesson_id,
        custom_description as description,
        video_urls,
        additional_materials,
        is_published,
        ai_prompt,
        pdf_urls,
        created_at,
        updated_at
       FROM public.lesson_content 
       WHERE is_published = true 
       ORDER BY lesson_id`
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
      `SELECT 
        id,
        lesson_id,
        custom_description as description,
        video_urls,
        additional_materials,
        is_published,
        ai_prompt,
        pdf_urls,
        created_at,
        updated_at
       FROM public.lesson_content 
       WHERE id = $1 OR lesson_id = $1`,
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

// Get practical materials
router.get('/materials/published', async (req, res) => {
  try {
    const result = await query(
      `SELECT 
        id,
        title,
        description,
        video_url,
        sort_order,
        is_published,
        created_at,
        updated_at
       FROM public.practical_materials 
       WHERE is_published = true 
       ORDER BY sort_order, created_at`
    );

    res.json(result.rows);
  } catch (error) {
    console.error('[LESSONS] Get materials error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
