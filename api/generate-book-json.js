/**
 * Generate Complete Book JSON from Refined Concept
 *
 * Takes a refined concept and level, returns complete book JSON
 * following BOOK_TEMPLATE.md structure with front/back matter.
 *
 * Output JSON structure:
 * - title, slug, level, band
 * - author, illustrator
 * - characters, setting_context
 * - word_list (sound_out, sight, heart)
 * - wordsearch_words
 * - pages (cover, copyright, parent_guide, level_info, wordlist, story pages, wordsearch, series_info, back_cover)
 * - reference_prompt
 */

export const config = {
  maxDuration: 180 // 3 minutes for full book generation
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const anthropicKey = process.env.ANTHROPIC_API_KEY;
  if (!anthropicKey) {
    return res.status(500).json({ error: 'ANTHROPIC_API_KEY not configured' });
  }

  try {
    const { concept, level } = req.body;

    if (!concept || !level) {
      return res.status(400).json({ error: 'Missing concept or level' });
    }

    // Load level specs
    const levelSpecsResponse = await fetch('https://funbookies.com/data/level-specs.json');
    const levelSpecs = await levelSpecsResponse.json();

    const levelData = levelSpecs.levels[level];
    if (!levelData) {
      return res.status(400).json({ error: `Invalid level: ${level}` });
    }

    const bandData = levelSpecs.bands[levelData.band];

    // Build the generation prompts
    const systemPrompt = buildSystemPrompt(levelSpecs, level, levelData, bandData);
    const userPrompt = buildUserPrompt(concept, level, levelData, bandData);

    // Check if client wants streaming
    const wantsStream = req.query.stream === 'true';

    if (wantsStream) {
      // Set up SSE headers
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');

      // Send prompts first for visibility
      res.write(`data: ${JSON.stringify({
        type: 'prompts',
        systemPrompt,
        userPrompt
      })}\n\n`);

      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': anthropicKey,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 12000,
          stream: true,
          system: systemPrompt,
          messages: [{ role: 'user', content: userPrompt }]
        })
      });

      if (!response.ok) {
        const error = await response.text();
        res.write(`data: ${JSON.stringify({ error: error })}\n\n`);
        res.end();
        return;
      }

      // Stream the response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;

            try {
              const parsed = JSON.parse(data);
              if (parsed.type === 'content_block_delta' && parsed.delta?.text) {
                fullText += parsed.delta.text;
                res.write(`data: ${JSON.stringify({ type: 'text', text: parsed.delta.text })}\n\n`);
              }
            } catch (e) {
              // Skip unparseable lines
            }
          }
        }
      }

      // Parse the complete JSON and add front/back matter
      try {
        const bookData = extractAndParseJSON(fullText);
        const completeBook = wrapWithFrontBackMatter(bookData, level, levelData, bandData);

        res.write(`data: ${JSON.stringify({
          type: 'complete',
          book: completeBook,
          level,
          levelData
        })}\n\n`);
      } catch (parseError) {
        res.write(`data: ${JSON.stringify({
          type: 'parse_error',
          error: parseError.message,
          rawText: fullText
        })}\n\n`);
      }

      res.write(`data: ${JSON.stringify({ type: 'done' })}\n\n`);
      res.end();
      return;
    }

    // Non-streaming response
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': anthropicKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 12000,
        system: systemPrompt,
        messages: [{ role: 'user', content: userPrompt }]
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Claude API error: ${error}`);
    }

    const result = await response.json();
    const fullText = result.content[0].text;

    // Parse the JSON and add front/back matter
    const bookData = extractAndParseJSON(fullText);
    const completeBook = wrapWithFrontBackMatter(bookData, level, levelData, bandData);

    return res.status(200).json({
      success: true,
      book: completeBook,
      level: level,
      levelData: levelData,
      prompts: { systemPrompt, userPrompt }
    });

  } catch (error) {
    console.error('Generation error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}

function buildSystemPrompt(levelSpecs, level, levelData, bandData) {
  return `You are a children's book author specializing in phonics-based decodable readers. You create books that follow strict Science of Reading principles.

Your task is to generate a COMPLETE book in JSON format following the FunBookies schema.

CRITICAL PROCESS - Follow this order:
1. First, create detailed CHARACTERS with FULL visual descriptions
2. Define the SETTING_CONTEXT with specific visual elements
3. Write a STORY_BIBLE with premise, themes, and emotional arc
4. Plan the story page-by-page with target word placement
5. Write all story pages with text, scene descriptions, and image prompts
6. Create the 9-panel reference_prompt for style consistency

CRITICAL RULES:
1. Follow the level constraints EXACTLY - word counts, sentence lengths, phonics patterns
2. Target words must appear 4+ times for orthographic mapping
3. Text must be age-appropriate and engaging
4. Each story page MUST have both scene (brief) AND image_prompt (detailed)
5. NO text should appear in images - prompts must say "NO TEXT"
6. Story should have clear beginning, middle, end with emotional arc

CHARACTER RULES:
- Maximum 2-3 recurring characters (ideally 2)
- Each recurring character needs DETAILED, CONSISTENT visual description
- Include: species/type, colors, clothing, distinctive features, personality traits
- One-off characters (appear in only 1 scene) don't count toward the limit

STORY STRUCTURES (use the one that fits best):

1. MINI HERO'S JOURNEY: Ordinary world -> Call to adventure -> Challenge -> Lowest moment -> Discovery/help -> Triumph -> Return transformed
   Emotions: comfort -> excitement -> worry -> despair -> hope -> joy -> satisfaction

2. PROBLEM-SOLUTION: Has problem -> Tries and fails -> Tries differently -> Succeeds
   Emotions: frustration -> determination -> disappointment -> persistence -> relief/pride

3. WISH FULFILLMENT: Wants something -> Works for it -> Almost gets it -> Gets it (or better)
   Emotions: longing -> hope -> anticipation -> worry -> joy

4. FRIENDSHIP: Meet someone different -> Misunderstanding -> See their view -> Become friends
   Emotions: curiosity -> confusion -> hurt -> understanding -> warmth

5. DISCOVERY: Encounter new thing -> Fear/confusion -> Explore -> Understand and appreciate
   Emotions: uncertainty -> caution -> curiosity -> wonder -> confidence

6. HELPING OTHERS: See need -> Decide to help -> Difficulty -> Succeed together
   Emotions: concern -> determination -> struggle -> teamwork -> pride

Every page MUST have a clear emotional beat from the chosen arc.

TEXT DENSITY BY BAND (keep it minimal!):
- Band A: 1-4 words per page (labels, single words, very short phrases)
- Band B: 1 line per page (one short sentence, 3-6 words)
- Band C: 2-3 lines per page (1-2 sentences)
- Band D: 4-8 lines per page (paragraph-level text)

More white space = less overwhelming for young readers. When in doubt, use fewer words.

IMAGE PROMPT GUIDELINES:
- NEVER use character names in prompts - the model doesn't know them
- ALWAYS describe the character visually: "A small plover bird with sandy-brown feathers and black eye-stripe"
- Include setting details in every prompt
- End with shot type and style: "Medium shot. Simple stylized children's book illustration, bold shapes, flat colors."
- Always end with "NO TEXT in image."

CRITICAL - PROP TRACKING IN SCENES:
Image generators FILL IN unspecified details - often incorrectly! Every scene MUST explicitly state:
1. WHERE important props are (ball, toy, special object)
2. IF a prop moved to a location, EVERY subsequent scene until retrieval must state its location
3. Example: If ball rolled into tunnel on page 4, pages 5-7 must say "ball visible INSIDE dark tunnel"
4. Even close-up shots must mention prop location: "Dark tunnel behind him, ball visible as small red dot inside"

CHARACTER EXCLUSION IN SCENES:
If a character is ALONE in a scene, explicitly state who is NOT present:
- "ONLY Rex visible - Rosie NOT in scene"
- "Character enters alone - no other characters present"

AVOID TEMPLATE TEXT:
- NO generic openings like "[X] and [Y] were pals. They had fun in the sun!"
- NO "One sunny day..." or "Once upon a time..."
- Each opening must be SPECIFIC to this story and characters
- Start with action, dialogue, or specific scene-setting

OUTPUT FORMAT:
Return ONLY valid JSON starting with { and ending with }
Do not include markdown code blocks or any text outside the JSON.`;
}

function buildUserPrompt(concept, level, levelData, bandData) {
  const constraints = levelData.constraints || {};

  return `Create a complete book JSON for this refined concept:

CONCEPT:
${concept}

LEVEL: ${level} - ${levelData.name}
BAND: ${bandData.name}
READER CAN: ${levelData.readerCan}

CONSTRAINTS:
- Words per sentence: ${constraints.wordsPerSentence || constraints.maxWordsPerSentence || 'flexible'}
- Pages: ${constraints.pages || '12-20'}
- Decodability: ${constraints.decodability || '80%+'}
- Phonics patterns: ${JSON.stringify(constraints.phonicsPatterns || [])}
- Sight words allowed: ${JSON.stringify(constraints.sightWords || [])} (cumulative: ${constraints.sightWordsCumulative || 'unlimited'})
- Fluency target: ${levelData.fluencyTarget || 'N/A'}

STORY GUIDANCE: ${levelData.storyGuidance || 'Age-appropriate narrative with clear arc'}

Generate the complete JSON with this structure:

{
  "title": "Book Title",
  "slug": "book-slug-lowercase-with-dashes",
  "summary": "One paragraph summary of the story",

  "characters": {
    "main": "Full visual description: A small plover bird with sandy-brown and white feathers, a black band across her eyes like a mask, orange legs, and a sharp little beak. Bold and brave despite her small size.",
    "secondary": "Full visual description of secondary character if any..."
  },

  "setting_context": "Full visual description of the primary setting: Sandy riverbank in Africa with warm golden sand, slow green river water, some reeds and rocks. Hot sunny day.",

  "story_bible": {
    "premise": "What the story is about",
    "themes": ["trust", "friendship", "helping others"],
    "emotional_arc": "curiosity -> worry -> courage -> joy -> satisfaction",
    "target_words": ["word1", "word2", "...8-12 words featuring the phonics pattern"]
  },

  "word_list": {
    "sound_out": ["all", "decodable", "words", "in", "story"],
    "sight": ["the", "a", "is", "high", "frequency", "words"],
    "heart": ["any", "words", "above", "level", "that", "must", "be", "taught"]
  },

  "wordsearch_words": ["8-10", "key", "words", "for", "activity"],

  "pages": [
    {
      "page": 1,
      "story_page": 1,
      "type": "story",
      "text": "The story text for this page.",
      "scene": "Brief scene description",
      "shot_type": "wide|medium|close|detail",
      "image_prompt": "Full detailed prompt: A small plover bird with sandy-brown feathers and black eye-stripe stands on golden sand looking hungry, head tilted. Green river, big sun. Simple stylized children's book illustration, bold shapes, flat colors. NO TEXT in image."
    }
  ],

  "reference_prompt": "9-PANEL STYLE REFERENCE SHEET for children's picture book..."
}

IMPORTANT:
- Generate ONLY the story pages (type: "story") - front/back matter will be added automatically
- Number story pages starting from 1
- Include story_page number on each page
- Make sure target words appear 4+ times across the story
- Each image_prompt must be self-contained (no character names, full visual descriptions)

Generate the complete JSON now:`;
}

function extractAndParseJSON(text) {
  // Try to extract JSON from the response
  // First, try to find JSON object
  let jsonStr = text.trim();

  // Remove markdown code blocks if present
  if (jsonStr.startsWith('```json')) {
    jsonStr = jsonStr.slice(7);
  } else if (jsonStr.startsWith('```')) {
    jsonStr = jsonStr.slice(3);
  }
  if (jsonStr.endsWith('```')) {
    jsonStr = jsonStr.slice(0, -3);
  }
  jsonStr = jsonStr.trim();

  // Find the JSON object
  const startIdx = jsonStr.indexOf('{');
  const endIdx = jsonStr.lastIndexOf('}');

  if (startIdx === -1 || endIdx === -1) {
    throw new Error('No valid JSON object found in response');
  }

  jsonStr = jsonStr.slice(startIdx, endIdx + 1);

  try {
    return JSON.parse(jsonStr);
  } catch (e) {
    throw new Error(`Failed to parse JSON: ${e.message}`);
  }
}

function wrapWithFrontBackMatter(bookData, level, levelData, bandData) {
  const storyPages = bookData.pages || [];
  const now = new Date().toISOString().split('T')[0];

  // Create the cover image prompt
  const coverPrompt = storyPages[0]?.image_prompt ||
    `Children's book cover illustration. ${bookData.setting_context || 'Colorful scene'}.
    ${bookData.characters?.main ? bookData.characters.main : 'Main character'}.
    Simple stylized children's book illustration, bold shapes, warm colors.
    NO TEXT in image.`;

  // Build complete pages array with front and back matter
  const allPages = [
    // Page 1: Cover
    {
      page: 1,
      type: "cover",
      text: bookData.title,
      scene: `Cover image for ${bookData.title}`,
      image_prompt: coverPrompt
    },
    // Page 2: Copyright
    {
      page: 2,
      type: "copyright",
      text: "FunBookies 2025"
    },
    // Page 3: Parent Guide
    {
      page: 3,
      type: "parent_guide",
      text: "Parent Guide"
    },
    // Page 4: Level Info
    {
      page: 4,
      type: "level_info",
      text: `Level ${level}: ${levelData.name}`
    },
    // Page 5: Word List
    {
      page: 5,
      type: "wordlist",
      text: formatWordList(bookData.word_list)
    }
  ];

  // Add story pages (renumbered starting from page 6)
  storyPages.forEach((page, idx) => {
    allPages.push({
      page: 6 + idx,
      story_page: idx + 1,
      type: "story",
      text: page.text,
      scene: page.scene,
      shot_type: page.shot_type,
      image_prompt: page.image_prompt
    });
  });

  const lastStoryPage = 5 + storyPages.length;

  // Add back matter
  // End page
  allPages.push({
    page: lastStoryPage + 1,
    type: "end",
    text: "The End"
  });

  // Word search
  allPages.push({
    page: lastStoryPage + 2,
    type: "wordsearch"
  });

  // Comprehension (optional)
  allPages.push({
    page: lastStoryPage + 3,
    type: "comprehension"
  });

  // Build the complete book object
  return {
    id: bookData.slug || generateSlug(bookData.title, level),
    title: bookData.title,
    slug: bookData.slug || generateSlug(bookData.title, level),
    level: level,
    band: levelData.band,
    targetPhonics: levelData.name,
    skill: levelData.name,
    skill_description: levelData.readerCan,
    age_range: getAgeRange(levelData.band),
    created: now,
    author: "FunBookies",
    illustrator: "AI Generated",
    summary: bookData.summary || "",
    characters: bookData.characters || {},
    setting_context: bookData.setting_context || "",
    story_bible: bookData.story_bible || {},
    word_list: bookData.word_list || { sound_out: [], sight: [], heart: [] },
    wordsearch_words: bookData.wordsearch_words || [],
    pages: allPages,
    reference_prompt: bookData.reference_prompt || "",
    parent_tips: generateParentTips(bookData, levelData),
    comprehension_questions: bookData.comprehension_questions || []
  };
}

function generateSlug(title, level) {
  const cleanTitle = title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
  return `${level.toLowerCase()}-${cleanTitle}`;
}

function formatWordList(wordList) {
  if (!wordList) return "Words to Practice";

  const parts = [];
  if (wordList.sound_out?.length) {
    parts.push(`Sound Out: ${wordList.sound_out.slice(0, 12).join(', ')}`);
  }
  if (wordList.sight?.length) {
    parts.push(`Sight Words: ${wordList.sight.slice(0, 8).join(', ')}`);
  }
  if (wordList.heart?.length) {
    parts.push(`Heart Words: ${wordList.heart.join(', ')}`);
  }

  return parts.length ? `Words to Practice:\n${parts.join('\n')}` : "Words to Practice";
}

function getAgeRange(band) {
  const ranges = {
    'A': '3-5',
    'B': 'K-1',
    'C': '1-3',
    'D': '3-6'
  };
  return ranges[band] || 'K-2';
}

function generateParentTips(bookData, levelData) {
  return {
    before_reading: `Look at the cover together. What do you think this story is about? Point out the characters and setting.`,
    during_reading: `Help your child sound out the focus words. At this level, they're practicing: ${levelData.name}`,
    after_reading: `Talk about what happened in the story. What was the character's problem? How did they solve it?`
  };
}
