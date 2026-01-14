/**
 * Generate Book XML from Concept
 *
 * Takes a concept and level, returns complete book XML
 * following level-specs.json constraints.
 */

export const config = {
  maxDuration: 120 // 2 minutes for AI generation
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

    // Build the generation prompt
    const systemPrompt = buildSystemPrompt(levelSpecs);
    const userPrompt = buildUserPrompt(concept, level, levelData, bandData);

    // Check if client wants streaming
    const wantsStream = req.query.stream === 'true';

    if (wantsStream) {
      // Set up SSE headers
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');

      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': anthropicKey,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 8000,
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
                res.write(`data: ${JSON.stringify({ text: parsed.delta.text })}\n\n`);
              }
            } catch (e) {
              // Skip unparseable lines
            }
          }
        }
      }

      res.write(`data: ${JSON.stringify({ done: true, level, levelData })}\n\n`);
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
        max_tokens: 8000,
        system: systemPrompt,
        messages: [{ role: 'user', content: userPrompt }]
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Claude API error: ${error}`);
    }

    const result = await response.json();
    const xmlContent = result.content[0].text;

    // Extract XML from response (in case there's extra text)
    const xmlMatch = xmlContent.match(/<\?xml[\s\S]*<\/book>/);
    const cleanXml = xmlMatch ? xmlMatch[0] : xmlContent;

    return res.status(200).json({
      success: true,
      xml: cleanXml,
      level: level,
      levelData: levelData
    });

  } catch (error) {
    console.error('Generation error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}

function buildSystemPrompt(levelSpecs) {
  return `You are a children's book author specializing in phonics-based decodable readers. You create books that follow strict Science of Reading principles.

Your task is to generate a complete book in XML format following the FunBookies schema.

CRITICAL PROCESS - Follow this order:
1. First, write a detailed STORY SUMMARY in <story_summary> showing:
   - Page-by-page breakdown (what happens on each page)
   - Emotional arc progression
   - Where target words appear
   - Key visual moments
2. Then write the actual story pages with text and prompts

CRITICAL RULES:
1. Follow the level constraints EXACTLY - word counts, sentence lengths, phonics patterns
2. Target words must appear 4+ times for orthographic mapping
3. Text must be age-appropriate and engaging
4. Use <br/> for line breaks within page text
5. Each page should have scene description AND full image_prompt
6. Reference prompt must describe a 9-panel reference sheet
7. NO text should appear in images - prompts must say "NO TEXT"
8. Story should have clear beginning, middle, end with emotional arc

CHARACTER RULES:
- Maximum 2-3 recurring characters (ideally 2)
- Each recurring character needs DETAILED, CONSISTENT visual description
- One-off characters (appear in only 1 scene) don't count toward the limit
- Fewer characters = better illustration consistency and reader focus
- Character descriptions must include: colors, clothing, distinctive features

BAND CHARACTERISTICS:
- Band A (A0-A4): Pre-reading. Simple labels, pattern books. UPPERCASE early, then lowercase.
- Band B (B1-B9): Phonics foundation. CVC → blends → digraphs → silent e → vowel teams → r-controlled.
- Band C (C1-C8): Word study. Syllabication, morphology, prefixes/suffixes.
- Band D (D1-D6): Fluent reading. Complex sentences, dialogue, literary devices.

OUTPUT FORMAT:
Return ONLY valid XML starting with <?xml version="1.0"?> and ending with </book>.
Include <story_summary> BEFORE <story> with detailed page-by-page outline.
End with complete <reference_prompt> for the 9-panel style sheet.
Do not include any explanation or commentary outside the XML.`;
}

function buildUserPrompt(concept, level, levelData, bandData) {
  const constraints = levelData.constraints || {};

  return `Create a complete book XML for this concept:

CONCEPT: ${concept}

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

Generate the complete XML in this EXACT order:

1. <metadata> - title, slug, band, level
2. <level_constraints> - from the constraints above
3. <targets> - phonics_focus, target_words (8-12 words featuring the pattern), sight_words_used
4. <story_bible> - premise, setting, characters (MAX 2-3 recurring, each with DETAILED visual descriptions: colors, clothing, distinctive features), themes, emotional_arc
5. <author_notes> - phonics notes, pacing notes, style notes

6. <story_summary> - CRITICAL: Write a DETAILED page-by-page outline BEFORE the actual story:
   - List each page number
   - What happens on that page
   - What target words appear
   - The emotional beat (wonder, concern, joy, etc.)
   - Key visual moment for illustration
   This ensures story coherence before writing actual text.

7. <story> - all pages with:
   - text (using <br/> for line breaks)
   - scene (brief description)
   - image_prompt (full, detailed prompt for generation)
   - shot_type (wide, medium, close, detail)

8. <reference_prompt> - LAST: Complete 9-panel reference sheet prompt:
   - Style description (colors, mood, art style)
   - Panel 1-3: Main character in different poses/expressions
   - Panel 4-6: Supporting characters and key objects
   - Panel 7-9: Settings and key story moments
   - End with "TECHNICAL: Pure visual reference only, NO TEXT anywhere in image."

For image prompts:
- Include character descriptions matching story_bible exactly
- Include style description matching reference
- Include shot type (wide, medium, close)
- Always end with "NO TEXT in image."

Generate the full XML now:`;
}
