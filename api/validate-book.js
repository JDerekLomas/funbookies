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

  // Cross-page validation: physical state continuity
  const continuityWarnings = validatePhysicalStateContinuity(book.pages);
  warnings.push(...continuityWarnings);

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
  // These are ERRORS because image models can't render emotions - only physical states
  const emotionalWords = [
    'happy', 'sad', 'scared', 'worried', 'angry', 'excited', 'nervous', 'anxious',
    'joyful', 'panicked', 'surprised', 'determined', 'tired', 'lonely', 'confused'
  ];
  const emotionalTranslations = {
    'happy': 'wide smile showing teeth, eyes crinkled, cheeks raised',
    'sad': 'downturned mouth, eyebrows furrowed inward, shoulders slumped',
    'scared': 'eyes wide open, mouth agape, eyebrows raised high, body leaning back',
    'worried': 'furrowed brow, tight lips, hunched shoulders',
    'angry': 'furrowed brows, clenched jaw, tense posture',
    'excited': 'wide eyes, open mouth smile, raised arms, bouncing posture',
    'nervous': 'fidgeting hands, darting eyes, tense shoulders',
    'anxious': 'biting lip, wringing hands, hunched posture',
    'joyful': 'beaming smile, arms raised, light bouncing step',
    'panicked': 'wide eyes, open mouth, hands near face, body recoiling',
    'surprised': 'mouth O-shaped, eyebrows raised, hands up near face',
    'determined': 'jaw set, eyes focused, chin up, chest out',
    'tired': 'drooping eyelids, slouched posture, yawning',
    'lonely': 'slumped shoulders, downcast eyes, arms wrapped around self',
    'confused': 'tilted head, furrowed brow, one eyebrow raised'
  };
  emotionalWords.forEach(word => {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    if (regex.test(scene)) {
      const suggestion = emotionalTranslations[word] || 'physical description';
      errors.push(`Page ${pageNum}: Uses emotional word "${word}" - replace with: "${suggestion}"`);
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

/**
 * Validate physical state continuity across pages.
 * If a character gets muddy/wet/etc on page N, they should still be in that state
 * on page N+1 unless explicitly cleaned/dried/etc.
 */
function validatePhysicalStateContinuity(pages) {
  const warnings = [];

  // Physical states to track (state → what clears it)
  const stateTransitions = {
    'muddy': ['clean', 'washed', 'bath', 'dried', 'towel'],
    'wet': ['dry', 'dried', 'towel', 'sun'],
    'dirty': ['clean', 'washed', 'bath'],
    'soaked': ['dry', 'dried', 'towel'],
    'splattered': ['clean', 'washed', 'wiped'],
    'covered in': ['clean', 'washed', 'wiped', 'removed']
  };

  // Track active states
  const activeStates = new Map(); // state -> page where it started

  pages.forEach((page, index) => {
    const pageNum = page.page || index + 1;
    const scene = (page.scene || '').toLowerCase();
    const text = (page.text || '').toLowerCase();
    const combined = scene + ' ' + text;

    // Check for new states being introduced
    for (const [state, clearers] of Object.entries(stateTransitions)) {
      // Check if this state is introduced
      if (combined.includes(state) && !activeStates.has(state)) {
        activeStates.set(state, pageNum);
      }

      // Check if this state is cleared
      if (activeStates.has(state)) {
        const isCleared = clearers.some(clearer => combined.includes(clearer));
        if (isCleared) {
          activeStates.delete(state);
        }
      }
    }

    // For pages after the first, check if active states are mentioned in scene
    if (index > 0 && activeStates.size > 0) {
      for (const [state, startPage] of activeStates.entries()) {
        // Only warn if the state started on a previous page and isn't in current scene
        if (startPage < pageNum && !scene.includes(state)) {
          warnings.push(
            `Page ${pageNum}: Character was "${state}" on page ${startPage} - ` +
            `scene should show this state or show it being cleared`
          );
        }
      }
    }
  });

  return warnings;
}
