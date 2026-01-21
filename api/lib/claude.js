// Shared Claude API utilities
// Simplifies LLM calls across all endpoints

import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic();

/**
 * Call Claude and get a JSON response
 * Uses system prompt to ensure valid JSON output
 */
export async function callClaudeJSON(prompt, options = {}) {
    const {
        model = 'claude-sonnet-4-20250514',
        maxTokens = 4000,
        system = 'You are a helpful assistant. Always respond with valid JSON only, no markdown or explanation.'
    } = options;

    const message = await anthropic.messages.create({
        model,
        max_tokens: maxTokens,
        system,
        messages: [{ role: 'user', content: prompt }]
    });

    const text = message.content[0].text;

    // Clean up common issues
    let cleaned = text.trim();

    // Remove markdown code blocks if present
    if (cleaned.startsWith('```')) {
        cleaned = cleaned.replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '');
    }

    return JSON.parse(cleaned);
}

/**
 * Call Claude and get a text response
 */
export async function callClaudeText(prompt, options = {}) {
    const {
        model = 'claude-sonnet-4-20250514',
        maxTokens = 4000,
        system = 'You are a helpful assistant.'
    } = options;

    const message = await anthropic.messages.create({
        model,
        max_tokens: maxTokens,
        system,
        messages: [{ role: 'user', content: prompt }]
    });

    return message.content[0].text;
}

/**
 * Validate text against a reading level using LLM
 * Replaces 520 lines of regex/rule-based validation
 */
export async function validateTextForLevel(text, level, levelSpecs) {
    const prompt = `Analyze this children's book text for reading level ${level}.

TEXT:
${text}

LEVEL SPECS:
${JSON.stringify(levelSpecs, null, 2)}

Check:
1. Are all words decodable at this level?
2. Are sentences appropriate length?
3. Are there any words that are too advanced?

Return JSON:
{
  "valid": true/false,
  "decodabilityScore": 0-100,
  "issues": [{"word": "...", "reason": "...", "suggestion": "..."}],
  "sentenceIssues": [{"sentence": "...", "issue": "..."}],
  "summary": "Brief assessment"
}`;

    return callClaudeJSON(prompt);
}

/**
 * Validate book continuity (character states, props, logic)
 * Replaces manual state machine tracking
 */
export async function validateBookContinuity(book) {
    const pagesContext = book.pages.map((p, i) =>
        `Page ${i + 1}:\nText: "${p.text}"\nScene: ${p.scene || '(no scene)'}`
    ).join('\n\n');

    const prompt = `Review this children's book for continuity issues.

TITLE: ${book.title}
CHARACTER: ${book.characterName || 'Unknown'}
SETTING: ${book.setting || 'Unknown'}

PAGES:
${pagesContext}

Check for:
1. Physical state continuity (if character gets muddy, are they still muddy until cleaned?)
2. Prop continuity (if a ball is lost, is it found before being used again?)
3. Location continuity (does character teleport without transition?)
4. Time continuity (does time progress logically?)
5. Character presence (are characters where they should be?)

Return JSON:
{
  "valid": true/false,
  "issues": [
    {"page": 1, "type": "physical_state", "issue": "...", "suggestion": "..."}
  ],
  "summary": "Brief assessment"
}`;

    return callClaudeJSON(prompt);
}

/**
 * Enhance a scene description for image generation
 * Replaces multi-step prompt_enhancer.py pipeline
 */
export async function enhanceSceneForImage(book, pageIndex) {
    const page = book.pages[pageIndex];
    const totalPages = book.pages.length;

    const pagesContext = book.pages.map((p, i) =>
        `Page ${i + 1}: "${p.text}" - ${p.scene?.substring(0, 100) || '(no scene)'}...`
    ).join('\n');

    const prompt = `Enhance this scene description for AI image generation.

BOOK: "${book.title}"
CHARACTER: ${book.characterName || 'main character'}
SETTING: ${book.setting}
STYLE: ${book.style || 'warm watercolor children\'s book illustration'}

STORY CONTEXT (all pages):
${pagesContext}

CURRENT PAGE (${pageIndex + 1} of ${totalPages}):
Text: "${page.text}"
Scene: ${page.scene || '(needs scene description)'}

Write an enhanced image prompt that:
1. Describes the scene visually (WHO, WHERE, WHAT, HOW)
2. Uses physical descriptions (not emotions like "happy" - instead "wide smile, bright eyes")
3. Maintains character consistency with earlier pages
4. Specifies shot type (wide, medium, close-up)
5. Ends with "NO TEXT, NO WORDS, NO LETTERS anywhere in image."

Return JSON:
{
  "enhancedPrompt": "The full image generation prompt...",
  "charactersPresent": ["name1"],
  "charactersAbsent": ["name2"],
  "physicalState": "clean/muddy/wet/etc",
  "emotionalBeat": "what's happening emotionally",
  "shotType": "wide/medium/close-up"
}`;

    return callClaudeJSON(prompt);
}

/**
 * Generate scene descriptions for all pages
 * Replaces generate_scene_descriptions.py
 */
export async function generateAllScenes(book) {
    const pagesContext = book.pages.map((p, i) =>
        `Page ${i + 1}: "${p.text}"`
    ).join('\n');

    const prompt = `Generate scene descriptions for each page of this children's book.

TITLE: "${book.title}"
CHARACTER: ${book.characterName || 'main character'} - ${book.characterDescription || 'a friendly character'}
SETTING: ${book.setting}
STYLE: ${book.style || 'warm watercolor children\'s book illustration'}

PAGES:
${pagesContext}

For each page, write a detailed scene description that:
1. Starts with shot type (Wide shot: / Medium shot: / Close-up:)
2. Describes the character with consistent visual details
3. Shows the action happening in that moment
4. Describes the setting/background
5. Tracks physical state (if character gets wet/muddy, show it in later scenes until resolved)
6. Ends with style note and "NO TEXT, NO WORDS, NO LETTERS."

Return JSON:
{
  "scenes": [
    {"page": 1, "scene": "Wide shot: CharacterName, description, doing action in setting. Style note. NO TEXT..."},
    {"page": 2, "scene": "..."}
  ]
}`;

    return callClaudeJSON(prompt, { maxTokens: 8000 });
}

export default {
    callClaudeJSON,
    callClaudeText,
    validateTextForLevel,
    validateBookContinuity,
    enhanceSceneForImage,
    generateAllScenes
};
