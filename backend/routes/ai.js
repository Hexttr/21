import express from 'express';
import { authenticate } from '../middleware/auth.js';
import OpenAI from 'openai';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// Initialize OpenAI (you'll need to set OPENAI_API_KEY in environment)
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// AI Chat
router.post('/chat', async (req, res) => {
  try {
    const { message, context } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Call OpenAI API
    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: 'You are a helpful assistant for a 21-day course.' },
        ...(context || []),
        { role: 'user', content: message },
      ],
    });

    res.json({
      response: completion.choices[0].message.content,
    });
  } catch (error) {
    console.error('[AI] Chat error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// AI Quiz
router.post('/quiz', async (req, res) => {
  try {
    const { topic, difficulty } = req.body;

    if (!topic) {
      return res.status(400).json({ error: 'Topic is required' });
    }

    // Generate quiz using OpenAI
    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        {
          role: 'system',
          content: 'Generate a quiz question with 4 multiple choice answers in JSON format.',
        },
        {
          role: 'user',
          content: `Generate a quiz question about: ${topic}. Difficulty: ${difficulty || 'medium'}`,
        },
      ],
    });

    res.json({
      quiz: JSON.parse(completion.choices[0].message.content),
    });
  } catch (error) {
    console.error('[AI] Quiz error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// AI Image Generation
router.post('/image', async (req, res) => {
  try {
    const { prompt } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    // Generate image using DALL-E
    const image = await openai.images.generate({
      model: 'dall-e-3',
      prompt: prompt,
      n: 1,
      size: '1024x1024',
    });

    res.json({
      imageUrl: image.data[0].url,
    });
  } catch (error) {
    console.error('[AI] Image error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;

