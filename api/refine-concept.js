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

## Main Character
- Name
- Age/type
- Visual description (specific details for illustration consistency)
- Personality traits

## Supporting Characters (if any)
Same details as main character

## Setting
Specific, visual description of the primary location(s)

## Story Arc
- Opening hook (page 1-2)
- Rising action (what happens, what's the problem)
- Climax (the turning point)
- Resolution (how it ends)
- Emotional journey (what the reader feels)

## Scene Ideas
List 6-8 key visual moments that would make great illustrations

## Style Notes
Art style suggestions (colors, mood, visual references)

Be specific and creative while staying within the level constraints.`;

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
