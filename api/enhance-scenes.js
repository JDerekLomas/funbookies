// Generate or enhance scene descriptions for a book
// Replaces generate_scene_descriptions.py and prompt_enhancer.py

import { callClaudeJSON } from './lib/claude.js';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { book, mode = 'generate' } = req.body;

        if (!book || !book.pages) {
            return res.status(400).json({ error: 'Book with pages required' });
        }

        if (mode === 'generate') {
            // Generate scenes from scratch
            const result = await generateScenes(book);
            return res.status(200).json(result);
        } else if (mode === 'enhance') {
            // Enhance existing scenes
            const result = await enhanceScenes(book);
            return res.status(200).json(result);
        } else if (mode === 'single') {
            // Enhance a single page
            const { pageIndex } = req.body;
            const result = await enhanceSingleScene(book, pageIndex);
            return res.status(200).json(result);
        }

        return res.status(400).json({ error: 'Invalid mode. Use: generate, enhance, or single' });

    } catch (error) {
        console.error('Scene generation error:', error);
        return res.status(500).json({ error: error.message });
    }
}

async function generateScenes(book) {
    const pagesText = book.pages.map((p, i) =>
        `Page ${i + 1}: "${p.text}"`
    ).join('\n');

    const prompt = `Generate detailed scene descriptions for this children's book.

TITLE: "${book.title}"
CHARACTER: ${book.characterName || 'main character'}
CHARACTER DESCRIPTION: ${book.characterDescription || 'a friendly character with expressive features'}
SETTING: ${book.setting || 'colorful setting'}
ART STYLE: ${book.style || 'warm watercolor children\'s book illustration, soft edges, gentle colors'}

STORY TEXT:
${pagesText}

For EACH page, write a scene description that:
1. Starts with shot type: "Wide shot:", "Medium shot:", or "Close-up:"
2. Names the character and describes their appearance CONSISTENTLY across all pages
3. Describes the specific ACTION happening (use -ing verbs)
4. Describes the SETTING/BACKGROUND with visual details
5. Uses PHYSICAL descriptions for emotions (not "happy" but "wide smile, bright eyes")
6. TRACKS PHYSICAL STATE: if character gets wet/muddy, they stay that way until cleaned
7. Ends with art style and "NO TEXT, NO WORDS, NO LETTERS anywhere in image."

CRITICAL RULES:
- Same character details on every page (if cat has orange fur and green eyes, always mention it)
- State persistence (muddy on page 3 = still muddy on page 4 unless bathed)
- No negations ("no ball" makes the AI draw a ball - only describe what IS there)

Return JSON:
{
  "characterDescription": "Full visual description of main character for consistency",
  "scenes": [
    {
      "page": 1,
      "scene": "Wide shot: [Character name], [consistent visual description], [action] in [setting]. [Physical emotional cues]. [Art style]. NO TEXT, NO WORDS, NO LETTERS anywhere in image.",
      "shotType": "wide",
      "emotionalBeat": "what's happening emotionally",
      "physicalState": "clean/muddy/wet/etc"
    }
  ]
}`;

    return callClaudeJSON(prompt, { maxTokens: 8000 });
}

async function enhanceScenes(book) {
    const pagesContext = book.pages.map((p, i) =>
        `Page ${i + 1}:\nText: "${p.text}"\nCurrent scene: ${p.scene || '(missing)'}`
    ).join('\n\n');

    const prompt = `Review and enhance these scene descriptions for AI image generation.

TITLE: "${book.title}"
CHARACTER: ${book.characterName || 'main character'}
SETTING: ${book.setting}
STYLE: ${book.style || 'warm watercolor children\'s book illustration'}

CURRENT SCENES:
${pagesContext}

For each scene, check and fix:
1. Is character described consistently? (same visual details each time)
2. Is shot type specified? (Wide/Medium/Close-up)
3. Are emotions physical? ("scared" → "eyes wide, mouth open")
4. Is physical state tracked? (wet stays wet until dried)
5. Does it end with "NO TEXT, NO WORDS, NO LETTERS"?
6. Is it specific enough for image generation?

Return JSON:
{
  "scenes": [
    {
      "page": 1,
      "original": "the original scene",
      "enhanced": "the improved scene description",
      "changes": ["what was fixed/improved"]
    }
  ],
  "summary": "Overall assessment of improvements made"
}`;

    return callClaudeJSON(prompt, { maxTokens: 8000 });
}

async function enhanceSingleScene(book, pageIndex) {
    const page = book.pages[pageIndex];
    const totalPages = book.pages.length;

    // Include surrounding pages for context
    const contextPages = book.pages
        .slice(Math.max(0, pageIndex - 2), Math.min(totalPages, pageIndex + 3))
        .map((p, i) => {
            const actualIndex = Math.max(0, pageIndex - 2) + i;
            const marker = actualIndex === pageIndex ? '>>> CURRENT PAGE <<<' : '';
            return `Page ${actualIndex + 1} ${marker}:\nText: "${p.text}"\nScene: ${p.scene || '(missing)'}`;
        })
        .join('\n\n');

    const prompt = `Enhance this single scene description for AI image generation.

BOOK: "${book.title}"
CHARACTER: ${book.characterName}
STYLE: ${book.style || 'warm watercolor children\'s book illustration'}

CONTEXT (surrounding pages):
${contextPages}

Enhance the CURRENT PAGE scene to:
1. Match character appearance from other pages
2. Use physical descriptions for emotions
3. Track any physical state from previous pages
4. Be specific and detailed for image generation
5. End with "NO TEXT, NO WORDS, NO LETTERS anywhere in image."

Return JSON:
{
  "page": ${pageIndex + 1},
  "enhanced": "The complete enhanced scene description",
  "shotType": "wide/medium/close-up",
  "charactersPresent": ["list"],
  "physicalState": "clean/muddy/wet/etc based on story so far",
  "emotionalBeat": "what's happening emotionally",
  "changes": ["what was improved"]
}`;

    return callClaudeJSON(prompt);
}
