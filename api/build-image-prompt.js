// Build image generation prompt for a single page
// Replaces template-based prompt building with LLM understanding

import { callClaudeText } from './lib/claude.js';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { book, pageIndex, referenceImage } = req.body;

        if (!book || pageIndex === undefined) {
            return res.status(400).json({ error: 'Book and pageIndex required' });
        }

        const page = book.pages[pageIndex];
        if (!page) {
            return res.status(400).json({ error: `Page ${pageIndex} not found` });
        }

        const prompt = await buildImagePrompt(book, page, pageIndex, referenceImage);

        return res.status(200).json({
            success: true,
            pageIndex,
            prompt
        });

    } catch (error) {
        console.error('Prompt building error:', error);
        return res.status(500).json({ error: error.message });
    }
}

async function buildImagePrompt(book, page, pageIndex, referenceImage) {
    // Get context from surrounding pages for state tracking
    const prevPages = book.pages.slice(Math.max(0, pageIndex - 2), pageIndex);
    const prevContext = prevPages.map((p, i) =>
        `Previous page ${pageIndex - prevPages.length + i + 1}: "${p.text}" - ${p.scene?.substring(0, 80) || 'no scene'}...`
    ).join('\n');

    const llmPrompt = `Write an image generation prompt for this children's book page.

BOOK INFO:
- Title: "${book.title}"
- Main Character: ${book.characterName || 'main character'}
- Character Description: ${book.characterDescription || 'a friendly character'}
- Setting: ${book.setting || 'colorful setting'}
- Art Style: ${book.style || 'warm watercolor children\'s book illustration'}

${prevContext ? `STORY CONTEXT (what happened before):\n${prevContext}\n` : ''}

CURRENT PAGE (page ${pageIndex + 1}):
Text: "${page.text}"
Scene description: ${page.scene || 'No scene description provided'}

${referenceImage ? 'NOTE: This will be generated with a reference image for style consistency.' : ''}

Write a complete image generation prompt that:
1. Starts with "Single scene illustration:" to prevent grid output
2. Describes the scene from the scene description
3. Includes a CHARACTER block with exact visual details (same every page)
4. Includes COMPOSITION guidance (one cohesive illustration, full-bleed)
5. Specifies the art style
6. Tracks any physical state from previous pages (if character was muddy, still muddy unless cleaned)
7. Ends with "CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere in image."

Output ONLY the prompt, no explanation.`;

    return callClaudeText(llmPrompt, {
        system: 'You are an expert at writing prompts for AI image generation. Write clear, specific prompts that produce consistent character illustrations.'
    });
}
