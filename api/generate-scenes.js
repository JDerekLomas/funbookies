/**
 * Vercel Serverless Function: Generate Scene Descriptions
 *
 * Takes a book JSON and generates detailed scene descriptions for each page
 * following the WHO/WHERE/WHAT/STATE framework from PROMPTING_CHEATSHEET.md
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'API key not configured' });
  }

  try {
    const { book } = req.body;

    if (!book || !book.pages) {
      return res.status(400).json({ error: 'Book data with pages is required' });
    }

    const prompt = buildScenePrompt(book);

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-haiku-20240307',
        max_tokens: 4096,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ]
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Claude API error:', response.status, errorText);
      return res.status(response.status).json({
        error: 'Failed to generate scenes',
        details: errorText
      });
    }

    const data = await response.json();
    const content = data.content[0].text;

    // Parse the JSON response
    let scenesData;
    try {
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        scenesData = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error('No JSON found in response');
      }
    } catch (parseError) {
      console.error('Failed to parse scenes JSON:', parseError);
      return res.status(500).json({
        error: 'Failed to parse scenes',
        raw: content
      });
    }

    return res.status(200).json(scenesData);

  } catch (error) {
    console.error('Error generating scenes:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

function buildScenePrompt(book) {
  const character = book.characterName || 'the main character';
  const characterType = book.character || 'animal';
  const setting = book.setting || 'the story setting';

  const pagesText = book.pages.map(p =>
    `Page ${p.page}: "${p.text}"`
  ).join('\n');

  return `You are creating detailed scene descriptions for a children's book illustrator. Each scene description will be used to generate an image with AI.

BOOK INFO:
- Title: ${book.title}
- Level: ${book.level}
- Main Character: ${character} the ${characterType}
- Setting: ${setting}

STORY PAGES:
${pagesText}

RULES FOR SCENE DESCRIPTIONS:

1. USE THE WHO/WHERE/WHAT/STATE FRAMEWORK:
   [Shot type]: [WHO with visual details] [WHAT action verb-ing] [WHERE with specifics].
   [STATE: character's physical condition]. [Mood/atmosphere]. [Style]. NO TEXT.

2. PHYSICAL OVER EMOTIONAL - Never use mood words. Translate emotions to physical descriptions:
   - scared → "eyes wide open, mouth agape, eyebrows raised high, body leaning back"
   - happy → "wide smile showing teeth, eyes crinkled, cheeks raised"
   - sad → "downturned mouth, eyebrows furrowed inward, shoulders slumped"
   - surprised → "mouth O-shaped, eyebrows raised, hands up near face"

3. NEVER USE NEGATIONS - Don't say what ISN'T there. Only describe what IS there.
   BAD: "no ball", "without tractor", "not raining"
   GOOD: Only describe what you want to see

4. TRACK PHYSICAL STATE - If character got muddy on page 3, they're STILL muddy on page 4 unless cleaned.

5. EXPLICIT CHARACTER PRESENCE - Always say who IS in the scene.

6. END EVERY SCENE WITH: "NO TEXT, NO WORDS, NO LETTERS anywhere in image."

SHOT TYPES:
- Wide shot: Establishing location, multiple characters
- Medium shot: Character interaction, main action
- Close-up: Emotion, detail, dramatic moment

EXAMPLE GOOD SCENE:
"Medium shot: ${character}, a round-bodied ${characterType} with bright eyes and floppy ears, splashing joyfully in a muddy puddle with legs extended and water droplets flying. ${character}'s fur is already mud-splattered from previous splash. Warm afternoon sunlight, dusty farm ground, wooden fence in background. Soft watercolor style with warm earth tones. NO TEXT, NO WORDS, NO LETTERS anywhere in image."

OUTPUT FORMAT (JSON):
{
  "pages": [
    {"page": 1, "scene": "Scene description here..."},
    {"page": 2, "scene": "Scene description here..."},
    ...
  ]
}

Generate detailed scene descriptions for ALL ${book.pages.length} pages. Return ONLY the JSON.`;
}
