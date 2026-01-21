// Simplified Text Validation using LLM
// Replaces 518 lines of regex/rule-based validation with ~80 lines

import { readFileSync } from 'fs';
import { join } from 'path';
import { callClaudeJSON } from './lib/claude.js';

function loadLevelSpecs() {
    try {
        const specsPath = join(process.cwd(), 'public', 'data', 'level-specs.json');
        return JSON.parse(readFileSync(specsPath, 'utf-8')).levels;
    } catch (error) {
        console.error('Error loading level specs:', error.message);
        return null;
    }
}

export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') return res.status(200).end();
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

    try {
        const { text, level } = req.body;

        if (!text || typeof text !== 'string') {
            return res.status(400).json({ error: 'Text is required' });
        }

        const levelSpecs = loadLevelSpecs();
        const levelSpec = levelSpecs?.[level];

        if (!levelSpec) {
            return res.status(400).json({
                error: `Invalid level: ${level}`,
                validLevels: Object.keys(levelSpecs || {})
            });
        }

        // Let Claude analyze the text
        const prompt = `Analyze this children's book text for reading level ${level} (${levelSpec.name}).

TEXT TO ANALYZE:
"${text}"

LEVEL REQUIREMENTS:
- Band: ${levelSpec.band}
- Focus: ${levelSpec.focus}
- Max words per sentence: ${levelSpec.constraints?.maxWordsPerSentence || 8}
- Decodability target: ${levelSpec.constraints?.decodability || '90%'}
${levelSpec.phonicsPatterns ? `- Phonics patterns allowed: ${levelSpec.phonicsPatterns.join(', ')}` : ''}

TASK:
1. Count total unique words
2. Identify words that are NOT decodable at this level (too advanced)
3. Check sentence lengths against max allowed
4. Calculate decodability score (% of words appropriate for level)

Return JSON:
{
  "totalWords": <number>,
  "uniqueWords": <number>,
  "decodableWords": <number matching level>,
  "sightWords": <number of common sight words>,
  "unknownWords": <number too advanced>,
  "decodabilityScore": <0-100>,
  "wordViolations": [
    {"word": "...", "reason": "why it's too advanced", "suggestion": "simpler alternative"}
  ],
  "sentenceViolations": [
    {"sentence": "...", "wordCount": <n>, "issue": "exceeds max of X words"}
  ],
  "passed": true/false,
  "summary": "Brief assessment of text appropriateness for level"
}`;

        const analysis = await callClaudeJSON(prompt);

        // Build response matching original API structure
        const response = {
            level,
            levelName: levelSpec.name,
            levelBand: levelSpec.band,
            analysis: {
                totalWords: analysis.totalWords,
                uniqueWords: analysis.uniqueWords,
                sentences: text.split(/[.!?]+/).filter(s => s.trim()).length
            },
            decodability: {
                score: analysis.decodabilityScore,
                decodableWords: analysis.decodableWords,
                sightWords: analysis.sightWords,
                unknownWords: analysis.unknownWords
            },
            constraints: {
                maxWordsPerSentence: levelSpec.constraints?.maxWordsPerSentence || 8,
                decodabilityTarget: levelSpec.constraints?.decodability || '90%'
            },
            sentenceCheck: {
                passed: (analysis.sentenceViolations || []).length === 0,
                maxAllowed: levelSpec.constraints?.maxWordsPerSentence || 8,
                violations: analysis.sentenceViolations || []
            },
            wordViolations: analysis.wordViolations || [],
            passed: analysis.passed,
            summary: analysis.summary
        };

        return res.status(200).json(response);

    } catch (error) {
        console.error('Validation error:', error);
        return res.status(500).json({ error: error.message });
    }
}
