// Generate reference image prompt using LLM
// Takes book data, returns a complete 9-panel reference prompt

import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic();

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { book } = req.body;

    if (!book || !book.pages) {
        return res.status(400).json({ error: 'Book data with pages required' });
    }

    try {
        // Build context from book data
        const bookContext = buildBookContext(book);

        const message = await anthropic.messages.create({
            model: 'claude-sonnet-4-20250514',
            max_tokens: 2000,
            messages: [{
                role: 'user',
                content: `You are an expert at writing prompts for AI image generation. Given this children's book, write a 9-panel character reference sheet prompt.

${bookContext}

Write a prompt for a 3x3 grid reference sheet that will help an image generator create consistent illustrations. The prompt should:

1. Clearly describe the main character's appearance based on the scene descriptions
2. Follow this 9-panel layout:
   - Row 1: [1] Character front view, [2] Character expressions (happy, surprised, sad), [3] Character in action pose
   - Row 2: [4] Secondary character or key prop, [5] KEY HERO SHOT - most important scene, [6] Important objects/props
   - Row 3: [7] Setting element 1, [8] Setting element 2, [9] Resolution/happy ending moment

3. Use specific visual details from the scenes (colors, features, clothing, etc.)
4. Specify the art style (warm watercolor, children's book illustration)
5. End with "NO TEXT, NO WORDS, NO LETTERS anywhere in image."

Output ONLY the prompt, no explanation or preamble.`
            }]
        });

        const prompt = message.content[0].text;

        return res.status(200).json({
            success: true,
            prompt: prompt
        });

    } catch (error) {
        console.error('Error generating reference prompt:', error);
        return res.status(500).json({
            error: error.message || 'Failed to generate reference prompt'
        });
    }
}

function buildBookContext(book) {
    const lines = [];

    lines.push(`TITLE: ${book.title || 'Untitled'}`);

    if (book.setting) {
        lines.push(`SETTING: ${book.setting}`);
    }

    if (book.characterName) {
        lines.push(`MAIN CHARACTER: ${book.characterName}`);
    }

    // Include art style
    const artStyle = book.visual_style || book.style;
    if (artStyle) {
        lines.push(`ART STYLE: ${artStyle}`);
    }

    // Include story type for context
    if (book.storyType) {
        lines.push(`STORY TYPE: ${book.storyType}`);
    }

    lines.push('');
    lines.push('PAGES:');

    book.pages.forEach((page, i) => {
        lines.push(`Page ${i + 1}:`);
        if (page.text) {
            lines.push(`  Text: "${page.text}"`);
        }
        if (page.scene) {
            lines.push(`  Scene: ${page.scene}`);
        }
        lines.push('');
    });

    return lines.join('\n');
}
