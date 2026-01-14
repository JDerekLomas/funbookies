/**
 * Refine Book Concept
 *
 * Takes a rough concept and level, returns an enhanced concept
 * with specific phonics targets, character details, and story elements.
 */

export const config = {
  maxDuration: 60
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
    const constraints = levelData.constraints || {};

    const systemPrompt = `You are a children's book development editor specializing in phonics-based decodable readers.

Your task is to take a rough book concept and enhance it into a detailed, production-ready concept that:
1. Aligns perfectly with the reading level constraints
2. Identifies specific target words featuring the phonics pattern
3. Develops memorable characters with clear visual descriptions
4. Creates an engaging story arc appropriate for the age group
5. Suggests specific scenes that will work well as illustrations

CHARACTER RULES:
- Maximum 2-3 recurring characters (ideally 2)
- Each recurring character needs consistent, detailed visual description
- One-off characters (appear in only 1 scene) don't count toward the limit
- Fewer characters = better illustration consistency and reader focus

STORY STRUCTURES (choose one that fits):

1. MINI HERO'S JOURNEY (most versatile)
   - Ordinary world → Call to adventure → Challenge/obstacle →
   - Lowest moment → Discovery/help → Triumph → Return transformed
   - Emotional arc: comfort → excitement → worry → despair → hope → joy → satisfaction

2. PROBLEM-SOLUTION
   - Character has a problem → Tries and fails → Tries differently → Succeeds
   - Emotional arc: frustration → determination → disappointment → persistence → relief/pride

3. WISH FULFILLMENT
   - Character wants something → Works/waits for it → Almost gets it → Gets it (or something better)
   - Emotional arc: longing → hope → anticipation → worry → joy

4. FRIENDSHIP STORY
   - Meet someone different → Misunderstanding/conflict → See their perspective → Become friends
   - Emotional arc: curiosity → confusion → hurt → understanding → warmth

5. DISCOVERY/LEARNING
   - Encounter something new → Fear or confusion → Explore carefully → Understand and appreciate
   - Emotional arc: uncertainty → caution → curiosity → wonder → confidence

6. HELPING OTHERS
   - See someone in need → Decide to help → Face difficulty helping → Succeed together
   - Emotional arc: concern → determination → struggle → teamwork → pride/gratitude

Choose the structure that best fits the concept. Every page should have a clear emotional beat.

Be specific and practical. The output will be used to generate a complete book.`;

    const userPrompt = `Enhance this rough book concept for level ${level}:

ROUGH CONCEPT:
${concept}

LEVEL: ${level} - ${levelData.name}
BAND: ${levelData.band} - ${bandData.name}
READER CAN: ${levelData.readerCan}

CONSTRAINTS:
- Words per sentence: ${constraints.wordsPerSentence || constraints.maxWordsPerSentence || 'flexible'}
- Total pages: ${constraints.pages || '12-20'}
- Decodability: ${constraints.decodability || '80%+'}
- Phonics patterns to feature: ${JSON.stringify(constraints.phonicsPatterns || [])}
- Sight words allowed (cumulative): ${constraints.sightWordsCumulative || 'unlimited'}
- Story guidance: ${levelData.storyGuidance || 'Age-appropriate narrative'}

Please provide an ENHANCED CONCEPT with:

## Title
A catchy, level-appropriate title

## Phonics Focus
The specific phonics patterns this book will practice, with 8-12 target words

## Premise
One paragraph describing the story (who, what, where, why, conflict, resolution)

## Characters (max 2-3 recurring, ideally 2)
For EACH recurring character provide:
- Name
- Age/type (child, animal, creature, etc.)
- Visual description (DETAILED: colors, clothing, distinctive features - must be consistent across all illustrations)
- Personality traits (1-2 key traits)

Note: One-off characters (appear once) don't need full descriptions.

## Setting
Specific, visual description of the primary location(s)

## Story Structure
Choose one: Mini Hero's Journey / Problem-Solution / Wish Fulfillment / Friendship / Discovery / Helping Others

## Story Arc (following your chosen structure)
- Opening hook (page 1-2): establish character + world + emotional starting point
- Rising action: what happens, what's the challenge
- Low point: the moment of maximum tension or doubt
- Turning point: the breakthrough or realization
- Resolution: how it ends, what changed
- Emotional journey: list the emotional beats page by page

## Scene Ideas
List 6-8 key visual moments that would make great illustrations

## Style Notes
Art style suggestions (colors, mood, visual references)

Be specific and creative while staying within the level constraints.`;

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
          max_tokens: 2000,
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

      res.write(`data: ${JSON.stringify({ done: true })}\n\n`);
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
        max_tokens: 2000,
        system: systemPrompt,
        messages: [{ role: 'user', content: userPrompt }]
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Claude API error: ${error}`);
    }

    const result = await response.json();
    const refinedConcept = result.content[0].text;

    return res.status(200).json({
      success: true,
      refinedConcept,
      level,
      levelData
    });

  } catch (error) {
    console.error('Refinement error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
