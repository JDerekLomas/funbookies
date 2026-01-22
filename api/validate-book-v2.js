// Simplified Book Validation using LLM
// Replaces manual state tracking with semantic understanding

import { callClaudeJSON } from './lib/claude.js';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { book } = req.body;

        if (!book || !book.pages) {
            return res.status(400).json({
                valid: false,
                errors: ['Book data with pages is required']
            });
        }

        // Quick structural checks (these are fast, no LLM needed)
        const structuralErrors = [];
        if (!book.title) structuralErrors.push('Book is missing a title');
        if (book.pages.length === 0) structuralErrors.push('Book has no pages');

        book.pages.forEach((page, i) => {
            if (!page.text?.trim()) structuralErrors.push(`Page ${i + 1}: Missing text`);
            if (!page.scene?.trim()) structuralErrors.push(`Page ${i + 1}: Missing scene description`);
            if (page.scene?.includes('Illustration for:')) {
                structuralErrors.push(`Page ${i + 1}: Has placeholder scene (not generated)`);
            }
        });

        // If structural issues, return early (no need for LLM)
        if (structuralErrors.length > 0) {
            return res.status(200).json({
                valid: false,
                errors: structuralErrors,
                warnings: [],
                pageCount: book.pages.length
            });
        }

        // Skip LLM validation if no API key or if explicitly disabled
        if (!process.env.ANTHROPIC_API_KEY) {
            return res.status(200).json({
                valid: true,
                errors: [],
                warnings: ['LLM validation skipped (no API key)'],
                pageCount: book.pages.length,
                assessment: 'Structural validation passed. LLM validation not available.'
            });
        }

        // Use LLM for semantic validation (continuity, logic, etc.)
        const pagesContext = book.pages.map((p, i) =>
            `Page ${i + 1}:\nText: "${p.text}"\nScene: ${p.scene}`
        ).join('\n\n');

        const prompt = `Validate this children's book for image generation readiness.

TITLE: ${book.title}
CHARACTER: ${book.characterName || 'main character'}
SETTING: ${book.setting || 'various'}

PAGES:
${pagesContext}

Check for these issues:

1. PHYSICAL STATE CONTINUITY
   - If character gets muddy/wet/dirty, do they stay that way until cleaned?
   - Example issue: "Gets muddy on page 3, appears clean on page 4 with no bath/cleaning"

2. PROP/OBJECT CONTINUITY
   - If an object is lost, is it found before being used?
   - If something breaks, does it stay broken?

3. LOCATION CONTINUITY
   - Does character teleport without transition?
   - Are locations consistent within scenes?

4. SCENE DESCRIPTION QUALITY
   - Are scenes specific enough for image generation?
   - Do they include WHO, WHERE, WHAT, and visual details?
   - Do scenes avoid emotional words that image generators can't show?

5. CHARACTER CONSISTENCY
   - Is the character described consistently across scenes?
   - Are visual details (colors, features) maintained?

Return JSON:
{
  "errors": [{"page": 1, "issue": "critical problem that will cause bad images"}],
  "warnings": [{"page": 1, "issue": "minor issue or suggestion"}],
  "continuityIssues": [{"pages": [3,4], "issue": "state discontinuity explanation"}],
  "sceneQuality": {
    "good": [1, 2, 5],
    "needsWork": [{"page": 3, "issue": "too vague", "suggestion": "add more detail"}]
  },
  "overallAssessment": "Brief summary of book's readiness for image generation"
}`;

        const analysis = await callClaudeJSON(prompt);

        // Combine structural and semantic issues
        const allErrors = [
            ...structuralErrors,
            ...(analysis.errors || []).map(e => `Page ${e.page}: ${e.issue}`)
        ];

        const allWarnings = [
            ...(analysis.warnings || []).map(w => `Page ${w.page}: ${w.issue}`),
            ...(analysis.continuityIssues || []).map(c => `Pages ${c.pages.join('-')}: ${c.issue}`)
        ];

        return res.status(200).json({
            valid: allErrors.length === 0,
            errors: allErrors,
            warnings: allWarnings,
            pageCount: book.pages.length,
            sceneQuality: analysis.sceneQuality,
            assessment: analysis.overallAssessment,
            summary: {
                totalIssues: allErrors.length + allWarnings.length,
                criticalIssues: allErrors.length,
                minorIssues: allWarnings.length
            }
        });

    } catch (error) {
        console.error('Validation error:', error);
        // Return valid=true on API errors so user can proceed
        // Local validation in the client will catch obvious issues
        return res.status(200).json({
            valid: true,
            errors: [],
            warnings: [`LLM validation unavailable: ${error.message}`],
            pageCount: req.body?.book?.pages?.length || 0,
            assessment: 'Structural validation passed. LLM validation encountered an error but local checks passed.'
        });
    }
}
