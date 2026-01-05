// Vercel Serverless Function for serving book evaluations
// Lists and returns evaluation JSON files

import { promises as fs } from 'fs';
import path from 'path';

export default async function handler(req, res) {
  // Only allow GET
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { slug } = req.query;

  try {
    // In production, evaluations would be stored in a database or file storage
    // For now, we return mock data or read from local files

    // If specific evaluation requested
    if (slug) {
      // Return mock evaluation for the book
      const evaluation = getMockEvaluation(slug);
      if (evaluation) {
        return res.status(200).json(evaluation);
      }
      return res.status(404).json({ error: 'Evaluation not found' });
    }

    // List all evaluations
    const evaluations = getAllMockEvaluations();
    return res.status(200).json(evaluations);

  } catch (error) {
    console.error('Error fetching evaluations:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

function getMockEvaluation(slug) {
  const evaluations = getAllMockEvaluations();
  return evaluations.find(e => e.book_slug === slug);
}

function getAllMockEvaluations() {
  return [
    {
      book_slug: "castle",
      title: "Rats in the Castle",
      level: 3,
      overall_score: 4.2,
      overall_image_score: 4.3,
      overall_text_score: 4.0,
      summary: "Very Good quality (4.2/5.0). Images: 4.3/5.0, Text: 4.0/5.0",
      recommendations: [
        "Consider simplifying 'castle' - may be difficult for level 3",
        "Page 12 image could be clearer"
      ],
      evaluated_at: "2025-01-05T15:30:00Z",
      image_evaluations: [
        {
          page_id: "page_06",
          image_path: "castle_images/page_03_sun.png",
          scores: {
            character_consistency: 5,
            style_consistency: 4,
            text_illustration_match: 5,
            child_appropriate: 5,
            visual_clarity: 4
          },
          overall_score: 4.6,
          feedback: "Excellent illustration with consistent character design.",
          issues: [],
          suggestions: []
        }
      ],
      text_evaluation: {
        scores: {
          reading_level_accuracy: 4,
          decodability: 4,
          engagement: 5,
          sentence_structure: 4
        },
        overall_score: 4.0,
        word_analysis: {
          total_unique_words: 45,
          decodable_words: 40,
          sight_words: 12,
          problematic_words: ["castle"]
        },
        issues: ["'castle' may be challenging for level 3"],
        suggestions: ["Consider using 'big home' instead of 'castle'"]
      }
    },
    {
      book_slug: "pig_mud",
      title: "Pig in the Mud",
      level: 2,
      overall_score: 4.5,
      overall_image_score: 4.6,
      overall_text_score: 4.3,
      summary: "Excellent quality (4.5/5.0). Images: 4.6/5.0, Text: 4.3/5.0",
      recommendations: [
        "All images show good character consistency",
        "Text perfectly matches level 2 phonics"
      ],
      evaluated_at: "2025-01-06T00:10:00Z",
      image_evaluations: [
        {
          page_id: "page_01",
          image_path: "pig_mud_images/page_01_cover.png",
          scores: {
            character_consistency: 5,
            style_consistency: 5,
            text_illustration_match: 5,
            child_appropriate: 5,
            visual_clarity: 4
          },
          overall_score: 4.8,
          feedback: "Excellent cover with cheerful pig character.",
          issues: [],
          suggestions: []
        },
        {
          page_id: "page_06",
          image_path: "pig_mud_images/page_06_pip_sat.png",
          scores: {
            character_consistency: 5,
            style_consistency: 4,
            text_illustration_match: 5,
            child_appropriate: 5,
            visual_clarity: 5
          },
          overall_score: 4.7,
          feedback: "Great opening scene with consistent character.",
          issues: [],
          suggestions: []
        }
      ],
      text_evaluation: {
        scores: {
          reading_level_accuracy: 5,
          decodability: 4,
          engagement: 4,
          sentence_structure: 5
        },
        overall_score: 4.3,
        word_analysis: {
          total_unique_words: 32,
          decodable_words: 28,
          sight_words: 8,
          problematic_words: []
        },
        issues: [],
        suggestions: []
      }
    }
  ];
}
