/**
 * Vercel Serverless Function: Validate Book for Image Generation
 *
 * Checks book data for common issues before spending credits on image generation.
 * Based on validation rules from PROMPTING_CHEATSHEET.md
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { book } = req.body;

    if (!book || !book.pages) {
      return res.status(400).json({
        valid: false,
        errors: ['Book data with pages is required']
      });
    }

    const validation = validateBook(book);

    return res.status(200).json(validation);

  } catch (error) {
    console.error('Error validating book:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

function validateBook(book) {
  const errors = [];
  const warnings = [];

  // Check title
  if (!book.title) {
    errors.push('Book is missing a title');
  }

  // Check pages array
  if (!Array.isArray(book.pages) || book.pages.length === 0) {
    errors.push('Book has no pages');
    return { valid: false, errors, warnings };
  }

  // Validate each page
  book.pages.forEach((page, index) => {
    const pageNum = page.page || index + 1;
    const pageErrors = validatePage(page, pageNum);
    errors.push(...pageErrors.errors);
    warnings.push(...pageErrors.warnings);
  });

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    pageCount: book.pages.length,
    summary: {
      totalIssues: errors.length + warnings.length,
      criticalIssues: errors.length,
      minorIssues: warnings.length
    }
  };
}

function validatePage(page, pageNum) {
  const errors = [];
  const warnings = [];

  // Check for scene description
  if (!page.scene) {
    errors.push(`Page ${pageNum}: Missing scene description`);
    return { errors, warnings };
  }

  const scene = page.scene;

  // Check minimum length
  if (scene.length < 50) {
    errors.push(`Page ${pageNum}: Scene too short (${scene.length} chars, need 50+)`);
  }

  // Check for placeholder text
  if (scene.toLowerCase().includes('illustration for:') ||
      scene.toLowerCase().includes('[scene description]') ||
      scene.toLowerCase().includes('to be added')) {
    errors.push(`Page ${pageNum}: Contains placeholder text`);
  }

  // Check for negations (except "NO TEXT" which is required)
  const negationPatterns = [
    /\bno\s+(?!text|words|letters)/gi,
    /\bnot\s+/gi,
    /\bwithout\s+/gi,
    /\bnever\s+/gi,
    /\bisn't\s+/gi,
    /\bwon't\s+/gi,
    /\bdon't\s+/gi,
    /\bcan't\s+/gi
  ];

  negationPatterns.forEach(pattern => {
    const match = scene.match(pattern);
    if (match) {
      errors.push(`Page ${pageNum}: Contains negation "${match[0].trim()}" - describe what IS there instead`);
    }
  });

  // Check for "NO TEXT" ending
  if (!scene.toLowerCase().includes('no text')) {
    warnings.push(`Page ${pageNum}: Missing "NO TEXT" instruction`);
  }

  // Check for single scene emphasis (Golden Rule #4)
  if (!/single scene|one cohesive|full-bleed|filling the entire/i.test(scene)) {
    warnings.push(`Page ${pageNum}: Consider adding "Single scene illustration" for clarity`);
  }

  // Check for emotional words (should be physical descriptions)
  const emotionalWords = [
    'happy', 'sad', 'scared', 'worried', 'angry', 'excited', 'nervous', 'anxious',
    'joyful', 'panicked', 'surprised', 'determined', 'tired', 'lonely', 'confused'
  ];
  emotionalWords.forEach(word => {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    if (regex.test(scene)) {
      warnings.push(`Page ${pageNum}: Uses emotional word "${word}" - use physical description instead`);
    }
  });

  // Check for WHO/WHERE/WHAT components
  const hasCharacter = /\b(shot|view|close-up|medium|wide)\b/i.test(scene) ||
                       scene.includes(page.character) ||
                       /\b(he|she|they|the \w+)\b/i.test(scene);
  if (!hasCharacter) {
    warnings.push(`Page ${pageNum}: Scene may be missing clear character reference`);
  }

  // Check for style/mood
  if (!/\b(style|watercolor|illustration|soft|warm|bright)\b/i.test(scene)) {
    warnings.push(`Page ${pageNum}: Consider adding style guidance`);
  }

  return { errors, warnings };
}
