/**
 * Book Quality Evaluation API
 *
 * POST /api/evaluate-book
 * Body: { slug: string, forceRefresh?: boolean }
 *
 * Evaluates a book on multiple factors using LLM + programmatic checks.
 * Results are cached in Supabase.
 */

const EVALUATIONS_SLUG = '_book-evaluations';

const EVALUATION_PROMPT = `You are a HARSH CRITIC evaluating children's early reader books. Your job is to find problems, not to be nice. Most books have serious flaws - identify them.

**Book Title:** {title}
**Reading Level:** {level}
**Target Age:** Early readers (ages 4-7)

**Story Text (all pages):**
{story_text}

**Story Bible/Background (if available):**
{story_bible}

## SCORING RULES - BE STRICT

Score 1-5 where 3 is AVERAGE, 4 is GOOD, 5 is EXCEPTIONAL (rare).
Default to 2-3 unless the story genuinely excels. A score of 4+ requires clear justification.

### COHERENCE (Does the story make logical sense?)
- Score 1-2 if: Characters appear without introduction, events happen for no reason, setting is unclear, "what is happening?" moments
- Score 3 if: Basic logic holds but connections are weak
- Score 4-5 if: Every element is clearly connected and motivated

### ENGAGEMENT (Would a child want to hear this again?)
- Score 1-2 if: Nothing happens, no tension/curiosity, just characters existing
- Score 3 if: Some mild interest but forgettable
- Score 4-5 if: Genuine hooks, surprises, or emotional moments

### CLARITY (Is it clear what's happening?)
- Score 1-2 if: Reader must guess what characters are doing, vague actions like "went" without destination, unclear relationships
- Score 3 if: Followable but requires effort
- Score 4-5 if: Crystal clear on every page

### EMOTIONAL_ARC (Beginning, middle, end with progression?)
- Score 1-2 if: No change occurs, characters end where they started, no problem/resolution
- Score 3 if: Minimal arc exists
- Score 4-5 if: Clear setup, development, and satisfying resolution

### AGE_APPROPRIATE
- Score based on vocabulary and concept fit for ages 4-7
- This is the ONE category where being simple is good

### EDUCATIONAL_VALUE
- Score 1-2 if: No lesson, no skill reinforcement, just filler
- Score 3 if: Basic reading practice only
- Score 4-5 if: Teaches concepts, models behavior, or builds specific skills

## EXAMPLES OF BAD STORIES (should score 2-3 overall):
- Characters sitting around talking with no plot
- "Zee went slow. Pip went fast." - went WHERE? doing WHAT?
- Random events that don't connect: "ZIP! A bird!" with no relevance
- Stories that are just descriptions of scenes with no conflict

## VERDICT THRESHOLDS
- "good": Average score 4.0+ (genuinely well-crafted story)
- "needs_improvement": Average score 2.5-3.9 (functional but flawed)
- "poor": Average score below 2.5 (fundamental problems)

Be specific in your issues. Don't say "could be more engaging" - say exactly what's wrong: "Character Pip appears on page 4 with no introduction" or "The story has no conflict - characters just sit and talk."

Respond in this exact JSON format:
{
  "scores": {
    "coherence": <1-5>,
    "engagement": <1-5>,
    "clarity": <1-5>,
    "emotional_arc": <1-5>,
    "age_appropriate": <1-5>,
    "educational_value": <1-5>
  },
  "overall_score": <1-5 average>,
  "verdict": "good" | "needs_improvement" | "poor",
  "strengths": ["strength 1", "strength 2"],
  "issues": ["specific issue 1", "specific issue 2"],
  "summary": "One paragraph honest assessment - lead with the problems"
}`;

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { slug, forceRefresh = false } = req.body;

  if (!slug) {
    return res.status(400).json({ error: 'Missing slug' });
  }

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
  const anthropicKey = process.env.ANTHROPIC_API_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return res.status(500).json({ error: 'Supabase not configured' });
  }

  if (!anthropicKey) {
    return res.status(500).json({ error: 'Anthropic API not configured' });
  }

  try {
    // Check for cached evaluation
    if (!forceRefresh) {
      const cached = await getCachedEvaluation(supabaseUrl, supabaseKey, slug);
      if (cached) {
        return res.status(200).json({
          success: true,
          cached: true,
          evaluation: cached
        });
      }
    }

    // Load book data
    const book = await loadBook(supabaseUrl, supabaseKey, slug);
    if (!book) {
      return res.status(404).json({ error: `Book not found: ${slug}` });
    }

    // Run evaluations
    const [storyEval, technicalEval, phonicsEval] = await Promise.all([
      evaluateStory(anthropicKey, book),
      evaluateTechnical(book, slug),
      evaluatePhonics(book)
    ]);

    // Combine results
    const evaluation = {
      slug,
      title: book.title,
      level: book.level,
      evaluated_at: new Date().toISOString(),
      story: storyEval,
      technical: technicalEval,
      phonics: phonicsEval,
      overall: calculateOverall(storyEval, technicalEval, phonicsEval)
    };

    // Cache results
    await saveEvaluation(supabaseUrl, supabaseKey, slug, evaluation);

    return res.status(200).json({
      success: true,
      cached: false,
      evaluation
    });

  } catch (error) {
    console.error('Evaluation error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}

async function loadBook(supabaseUrl, supabaseKey, slug) {
  // Try Supabase first
  const response = await fetch(
    `${supabaseUrl}/rest/v1/books?slug=eq.${slug}&select=data`,
    {
      headers: {
        'Authorization': `Bearer ${supabaseKey}`,
        'apikey': supabaseKey
      }
    }
  );

  const data = await response.json();
  if (data && data.length > 0 && data[0].data) {
    return data[0].data;
  }

  // Fallback to static file
  const staticRes = await fetch(`https://funbookies.com/books/${slug}.json`);
  if (staticRes.ok) {
    return await staticRes.json();
  }

  return null;
}

async function getCachedEvaluation(supabaseUrl, supabaseKey, slug) {
  const response = await fetch(
    `${supabaseUrl}/rest/v1/books?slug=eq.${EVALUATIONS_SLUG}&select=data`,
    {
      headers: {
        'Authorization': `Bearer ${supabaseKey}`,
        'apikey': supabaseKey
      }
    }
  );

  const data = await response.json();
  if (data && data.length > 0 && data[0].data?.evaluations?.[slug]) {
    return data[0].data.evaluations[slug];
  }
  return null;
}

async function saveEvaluation(supabaseUrl, supabaseKey, slug, evaluation) {
  // Get existing evaluations
  const response = await fetch(
    `${supabaseUrl}/rest/v1/books?slug=eq.${EVALUATIONS_SLUG}&select=data`,
    {
      headers: {
        'Authorization': `Bearer ${supabaseKey}`,
        'apikey': supabaseKey
      }
    }
  );

  const data = await response.json();
  const existing = data?.[0]?.data?.evaluations || {};

  // Update with new evaluation
  existing[slug] = evaluation;

  // Save back
  await fetch(
    `${supabaseUrl}/rest/v1/books`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${supabaseKey}`,
        'apikey': supabaseKey,
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
      },
      body: JSON.stringify({
        slug: EVALUATIONS_SLUG,
        data: { evaluations: existing },
        updated_at: new Date().toISOString()
      })
    }
  );
}

async function evaluateStory(anthropicKey, book) {
  // Extract story text from pages
  const storyPages = (book.pages || [])
    .filter(p => p.type === 'story' || p.type === 'cover')
    .map((p, i) => `Page ${i + 1}: ${p.text || '(no text)'}`)
    .join('\n');

  if (!storyPages.trim()) {
    return {
      error: 'No story text found',
      scores: null,
      verdict: 'poor'
    };
  }

  // Build prompt
  const prompt = EVALUATION_PROMPT
    .replace('{title}', book.title || 'Untitled')
    .replace('{level}', book.level || 'Unknown')
    .replace('{story_text}', storyPages)
    .replace('{story_bible}', book.story_bible ? JSON.stringify(book.story_bible, null, 2) : 'Not available');

  // Call Claude
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': anthropicKey,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      messages: [{ role: 'user', content: prompt }]
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Claude API error: ${error}`);
  }

  const result = await response.json();
  const text = result.content[0].text;

  // Parse JSON from response
  try {
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
  } catch (e) {
    console.error('Failed to parse story evaluation:', e);
  }

  return {
    error: 'Failed to parse evaluation',
    raw: text,
    verdict: 'needs_improvement'
  };
}

function evaluateTechnical(book, slug) {
  const pages = book.pages || [];
  const storyPages = pages.filter(p => p.type === 'story' || p.type === 'cover');

  const checks = {
    has_story_bible: !!book.story_bible,
    has_characters: !!book.characters && Object.keys(book.characters).length > 0,
    has_summary: !!book.summary,
    has_reference_prompt: !!book.reference_prompt,
    scene_descriptions: {
      total: storyPages.length,
      with_scenes: storyPages.filter(p => p.scene && p.scene.length > 50 && !p.scene.startsWith('Illustration for:')).length,
      placeholder: storyPages.filter(p => p.scene?.startsWith('Illustration for:')).length
    },
    word_count: storyPages.reduce((sum, p) => sum + (p.text || '').split(/\s+/).filter(Boolean).length, 0),
    page_count: storyPages.length
  };

  // Calculate technical score
  let score = 0;
  if (checks.has_story_bible) score += 1;
  if (checks.has_characters) score += 1;
  if (checks.has_reference_prompt) score += 1;
  if (checks.scene_descriptions.with_scenes === checks.scene_descriptions.total) score += 2;
  else if (checks.scene_descriptions.with_scenes > checks.scene_descriptions.total / 2) score += 1;

  return {
    score: Math.min(5, score),
    checks,
    issues: [
      !checks.has_story_bible && 'Missing story bible',
      !checks.has_characters && 'Missing character definitions',
      !checks.has_reference_prompt && 'Missing reference prompt',
      checks.scene_descriptions.placeholder > 0 && `${checks.scene_descriptions.placeholder} placeholder scenes`,
      checks.scene_descriptions.with_scenes < checks.scene_descriptions.total && 'Some pages missing scene descriptions'
    ].filter(Boolean)
  };
}

function evaluatePhonics(book) {
  const level = book.level || '';
  const band = level[0] || '?';

  const pages = book.pages || [];
  const allText = pages
    .filter(p => p.type === 'story')
    .map(p => p.text || '')
    .join(' ')
    .toLowerCase();

  const words = allText.split(/\s+/).filter(w => w.match(/^[a-z]+$/));
  const uniqueWords = [...new Set(words)];

  // Simple CVC detection (consonant-vowel-consonant)
  const cvcPattern = /^[bcdfghjklmnpqrstvwxyz][aeiou][bcdfghjklmnpqrstvwxyz]$/;
  const cvcWords = uniqueWords.filter(w => cvcPattern.test(w));

  // Sight words (common high-frequency words)
  const sightWords = ['the', 'a', 'is', 'it', 'in', 'on', 'at', 'to', 'and', 'he', 'she', 'we', 'me', 'be', 'no', 'go', 'so', 'do', 'i', 'you', 'was', 'are', 'have', 'has', 'had', 'said', 'they', 'there', 'this', 'that', 'with', 'for', 'not', 'but', 'what', 'all', 'were', 'when', 'can', 'an', 'your', 'which', 'their', 'will', 'each', 'about', 'how', 'up', 'out', 'them', 'then', 'many', 'some', 'her', 'would', 'make', 'like', 'him', 'into', 'time', 'look', 'two', 'more', 'see', 'way', 'could', 'my', 'than', 'been', 'call', 'who', 'its', 'now', 'find', 'long', 'down', 'day', 'get', 'come', 'made', 'may', 'part'];
  const usedSightWords = uniqueWords.filter(w => sightWords.includes(w));

  // Band-appropriate complexity check
  const avgWordLength = words.length > 0 ? words.reduce((s, w) => s + w.length, 0) / words.length : 0;

  let complexityScore = 3;
  if (band === 'A' && avgWordLength > 4) complexityScore = 2;
  if (band === 'B' && avgWordLength > 5) complexityScore = 2;
  if (band === 'A' && avgWordLength <= 3.5) complexityScore = 4;
  if (cvcWords.length > uniqueWords.length * 0.3) complexityScore += 1;

  return {
    score: Math.min(5, complexityScore),
    stats: {
      total_words: words.length,
      unique_words: uniqueWords.length,
      avg_word_length: Math.round(avgWordLength * 10) / 10,
      cvc_words: cvcWords.length,
      sight_words_used: usedSightWords.length
    },
    level_appropriate: complexityScore >= 3
  };
}

function calculateOverall(story, technical, phonics) {
  const storyScore = story.scores?.coherence
    ? (story.scores.coherence + story.scores.engagement + story.scores.clarity +
       story.scores.emotional_arc + story.scores.age_appropriate + story.scores.educational_value) / 6
    : 2;

  const techScore = technical.score || 2;
  const phonicsScore = phonics.score || 3;

  // Weighted average: story 50%, technical 25%, phonics 25%
  const overall = (storyScore * 0.5) + (techScore * 0.25) + (phonicsScore * 0.25);

  let verdict = 'needs_improvement';
  if (overall >= 4) verdict = 'good';
  else if (overall < 2.5) verdict = 'poor';

  return {
    score: Math.round(overall * 10) / 10,
    verdict,
    breakdown: {
      story: Math.round(storyScore * 10) / 10,
      technical: techScore,
      phonics: phonicsScore
    }
  };
}
