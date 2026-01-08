// Vercel Serverless Function for Text Validation
// Validates text against reading level requirements using sight words and phonics word banks

import { readFileSync } from 'fs';
import { join } from 'path';

/**
 * Load level specifications and build level code to index mapping
 * Returns levelSpecs object with levels keyed by code (A0-D6)
 */
function loadLevelSpecs() {
  try {
    const publicDir = join(process.cwd(), 'public', 'data');
    const specsPath = join(publicDir, 'level-specs.json');
    const specsData = JSON.parse(readFileSync(specsPath, 'utf-8'));
    return specsData.levels;
  } catch (error) {
    console.error('Error loading level specs:', error.message);
    return null;
  }
}

/**
 * Load word banks from JSON files
 * Returns { sightWords, phonicsWords } or null if files don't exist yet
 */
function loadWordBanks() {
  try {
    const publicDir = join(process.cwd(), 'public', 'data');

    // Load sight words (high-frequency words by band)
    const sightWordsPath = join(publicDir, 'sight-words.json');
    const sightWordsData = JSON.parse(readFileSync(sightWordsPath, 'utf-8'));

    // Load phonics words (decodable words by phonics pattern/level)
    const phonicsWordsPath = join(publicDir, 'phonics-words.json');
    const phonicsWordsData = JSON.parse(readFileSync(phonicsWordsPath, 'utf-8'));

    // Build cumulative sight word sets by numeric level (for compatibility)
    const sightWordsByLevel = {};
    const bands = Object.values(sightWordsData.levels);
    for (let level = 0; level <= 23; level++) {
      sightWordsByLevel[level] = new Set();
      bands.forEach(band => {
        if (band.readingLevels && band.readingLevels.some(l => l <= level)) {
          band.words.forEach(w => sightWordsByLevel[level].add(w.toLowerCase()));
        }
      });
    }

    // Build cumulative phonics word sets by numeric level (for compatibility)
    const phonicsWordsByLevel = {};
    for (let level = 0; level <= 23; level++) {
      phonicsWordsByLevel[level] = new Set();
      // Add all words from levels 0 through current level
      for (let l = 0; l <= Math.min(level, 12); l++) {
        const levelData = phonicsWordsData.levels[String(l)];
        if (levelData && levelData.words) {
          Object.values(levelData.words).forEach(wordList => {
            wordList.forEach(w => phonicsWordsByLevel[level].add(w.toLowerCase()));
          });
        }
      }
    }

    return { sightWordsByLevel, phonicsWordsByLevel };
  } catch (error) {
    console.error('Error loading word banks:', error.message);
    return null;
  }
}

/**
 * Convert level code (A0-D6) to numeric index (0-27) for word bank lookups
 * @param {string} levelCode - The level code (e.g., "B5", "C3", "D1")
 * @returns {number|null} - The numeric index or null if invalid
 */
function levelCodeToIndex(levelCode) {
  const specs = loadLevelSpecs();
  if (!specs || !specs[levelCode]) {
    return null;
  }
  return specs[levelCode].index;
}

/**
 * Validate level code format (A0-D6)
 * @param {string} levelCode - The level code to validate
 * @returns {boolean} - True if valid format
 */
function isValidLevelCode(levelCode) {
  const levelCodePattern = /^[A-D]\d+$/;
  if (!levelCodePattern.test(levelCode)) return false;

  const band = levelCode[0];
  const number = parseInt(levelCode.substring(1), 10);

  // Check valid ranges per band
  if (band === 'A' && number >= 0 && number <= 4) return true;
  if (band === 'B' && number >= 1 && number <= 9) return true;
  if (band === 'C' && number >= 1 && number <= 8) return true;
  if (band === 'D' && number >= 1 && number <= 6) return true;

  return false;
}

/**
 * Tokenize text into words
 * Handles punctuation, capitalization, and returns clean word array
 * @param {string} text - The text to tokenize
 * @returns {string[]} - Array of lowercase words
 */
function tokenizeText(text) {
  if (!text || typeof text !== 'string') return [];

  // Remove punctuation and normalize
  // Keep apostrophes for contractions (can't, won't, etc.)
  const normalized = text
    .toLowerCase()
    .replace(/[""]/g, '"')  // Normalize quotes
    .replace(/['']/g, "'")  // Normalize apostrophes
    .replace(/[—–]/g, '-')  // Normalize dashes
    .trim();

  // Split on whitespace and clean each word
  const words = normalized
    .split(/\s+/)
    .map(word => {
      // Remove leading/trailing punctuation but keep internal apostrophes
      return word.replace(/^[^\w']+|[^\w']+$/g, '');
    })
    .filter(word => word.length > 0);

  return words;
}

/**
 * Split text into sentences
 * @param {string} text - The text to split
 * @returns {string[]} - Array of sentences
 */
function splitIntoSentences(text) {
  if (!text || typeof text !== 'string') return [];

  // Split on sentence endings: . ! ?
  // Handle common abbreviations and edge cases
  const sentences = text
    .split(/[.!?]+/)
    .map(s => s.trim())
    .filter(s => s.length > 0);

  return sentences;
}

/**
 * Check if a word is valid at the given reading level
 * @param {string} word - The word to check
 * @param {string} levelCode - The level code (e.g., "B5", "C3")
 * @param {object} wordBanks - { sightWordsByLevel, phonicsWordsByLevel }
 * @returns {object} - { valid, type, reason }
 */
function checkWordLevel(word, levelCode, wordBanks) {
  if (!wordBanks) {
    return { valid: false, type: 'unknown', reason: 'Word banks not loaded' };
  }

  // Convert level code to numeric index for word bank lookup
  const numericLevel = levelCodeToIndex(levelCode);
  if (numericLevel === null) {
    return { valid: false, type: 'unknown', reason: `Invalid level code: ${levelCode}` };
  }

  const { sightWordsByLevel, phonicsWordsByLevel } = wordBanks;
  const lowerWord = word.toLowerCase();

  // Check sight words for this level
  if (sightWordsByLevel[numericLevel] && sightWordsByLevel[numericLevel].has(lowerWord)) {
    return { valid: true, type: 'sight', levelCode };
  }

  // Check phonics/decodable words for this level
  if (phonicsWordsByLevel[numericLevel] && phonicsWordsByLevel[numericLevel].has(lowerWord)) {
    return { valid: true, type: 'decodable', levelCode };
  }

  // Word not found in word banks for this level
  return { valid: false, type: 'unknown', reason: `Not in word bank for level ${levelCode}` };
}

/**
 * Analyze sentence lengths and check for violations
 * @param {string} text - The text to analyze
 * @param {number} maxWords - Maximum words allowed per sentence
 * @returns {object} - { passed, violations, avgWordsPerSentence, maxWordsInSentence }
 */
function analyzeSentences(text, maxWords) {
  const sentences = splitIntoSentences(text);
  const violations = [];
  let totalWords = 0;
  let maxWordsFound = 0;

  sentences.forEach((sentence, index) => {
    const words = tokenizeText(sentence);
    const wordCount = words.length;
    totalWords += wordCount;

    if (wordCount > maxWordsFound) {
      maxWordsFound = wordCount;
    }

    if (wordCount > maxWords) {
      violations.push({
        sentenceNumber: index + 1,
        wordCount: wordCount,
        maxAllowed: maxWords,
        text: sentence.substring(0, 50) + (sentence.length > 50 ? '...' : '')
      });
    }
  });

  const avgWordsPerSentence = sentences.length > 0 ? totalWords / sentences.length : 0;

  return {
    passed: violations.length === 0,
    violations,
    avgWordsPerSentence: Math.round(avgWordsPerSentence * 10) / 10,
    maxWordsInSentence: maxWordsFound,
    totalSentences: sentences.length
  };
}

/**
 * Suggest a simpler alternative for a word
 * @param {string} word - The word to find an alternative for
 * @param {string} levelCode - The target reading level code (e.g., "B5")
 * @param {object} wordBanks - { sightWordsByLevel, phonicsWordsByLevel }
 * @returns {string|null} - Suggested alternative or null
 */
function suggestAlternative(word, levelCode, wordBanks) {
  if (!wordBanks) return null;

  // Common word substitutions for early readers
  const commonAlternatives = {
    // Past tense to present
    'jumped': 'jump',
    'walked': 'walk',
    'looked': 'look',
    'played': 'play',
    'wanted': 'want',
    'needed': 'need',
    'helped': 'help',
    'asked': 'ask',
    'called': 'call',
    'turned': 'turn',
    'moved': 'move',
    'opened': 'open',
    'closed': 'close',

    // Complex to simple
    'beautiful': 'nice',
    'delicious': 'good',
    'enormous': 'big',
    'tiny': 'small',
    'quickly': 'fast',
    'slowly': 'slow',
    'angry': 'mad',
    'happy': 'glad',
    'sad': 'sad',
    'frightened': 'scared',

    // Multi-syllable to simpler
    'animal': 'pet',
    'together': 'with',
    'because': 'so',
    'different': 'not same',
    'important': 'big',
    'favorite': 'best',
  };

  // Check if we have a direct substitution
  if (commonAlternatives[word]) {
    const alternative = commonAlternatives[word];
    const check = checkWordLevel(alternative, levelCode, wordBanks);
    if (check.valid) {
      return alternative;
    }
  }

  // Try removing common suffixes
  const suffixes = ['ed', 'ing', 's', 'es', 'er', 'est', 'ly'];
  for (const suffix of suffixes) {
    if (word.endsWith(suffix)) {
      const base = word.slice(0, -suffix.length);
      const check = checkWordLevel(base, levelCode, wordBanks);
      if (check.valid) {
        return base;
      }
    }
  }

  return null;
}

/**
 * Get maximum words per sentence for a given level code
 * Reads from level-specs.json constraints
 * @param {string} levelCode - The level code (e.g., "B5", "C3")
 * @returns {number} - Maximum words allowed per sentence
 */
function getMaxWordsPerSentence(levelCode) {
  const specs = loadLevelSpecs();
  if (!specs || !specs[levelCode]) {
    // Fallback defaults if specs not available
    return 10;
  }

  const levelSpec = specs[levelCode];
  if (levelSpec.constraints && typeof levelSpec.constraints.maxWordsPerSentence === 'number') {
    return levelSpec.constraints.maxWordsPerSentence;
  }

  // Fallback to default if constraint not specified
  return 10;
}

/**
 * Analyze which phonics rules are violated
 * @param {string} word - The word to analyze
 * @param {number} level - The current reading level
 * @returns {string|null} - Violation reason or null
 */
function analyzePhonicsViolation(word, level) {
  // Level-specific phonics rules
  const rules = [
    { maxLevel: 14, pattern: /ed$/, reason: 'Contains -ed suffix (Level 14+)' },
    { maxLevel: 14, pattern: /ing$/, reason: 'Contains -ing suffix (Level 14+)' },
    { maxLevel: 10, pattern: /tion$/, reason: 'Contains -tion suffix (Level 10+)' },
    { maxLevel: 10, pattern: /sion$/, reason: 'Contains -sion suffix (Level 10+)' },
    { maxLevel: 8, pattern: /er$/, reason: 'Contains -er suffix (Level 8+)' },
    { maxLevel: 8, pattern: /est$/, reason: 'Contains -est suffix (Level 8+)' },
    { maxLevel: 6, pattern: /ly$/, reason: 'Contains -ly suffix (Level 6+)' },
    { maxLevel: 12, pattern: /[aeiou]{3,}/, reason: 'Contains complex vowel pattern (Level 12+)' },
  ];

  for (const rule of rules) {
    if (level < rule.maxLevel && rule.pattern.test(word)) {
      return rule.reason;
    }
  }

  return null;
}

/**
 * Main validation handler
 * Accepts POST with { text: "...", level: "B5" }
 * Returns validation results with decodability score, violations, and constraints
 */
export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed. Use POST.' });
  }

  try {
    const { text, level } = req.body;

    // Validate inputs
    if (!text || typeof text !== 'string') {
      return res.status(400).json({ error: 'Text is required and must be a string' });
    }

    if (typeof level !== 'string') {
      return res.status(400).json({
        error: 'Level must be a string',
        example: 'level: "B5" or level: "C3"',
        validLevels: ['A0', 'A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6']
      });
    }

    // Validate level code format
    if (!isValidLevelCode(level)) {
      return res.status(400).json({
        error: `Invalid level code: ${level}`,
        message: 'Level must be a valid code (A0-A4, B1-B9, C1-C8, D1-D6)',
        validLevels: ['A0', 'A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6']
      });
    }

    // Load word banks
    const wordBanks = loadWordBanks();

    if (!wordBanks) {
      return res.status(503).json({
        error: 'Word banks not available yet',
        message: 'The word bank files (sight-words.json, phonics-words.json) need to be present. Please check deployment.'
      });
    }

    // Load level specifications to get constraints
    const specs = loadLevelSpecs();
    if (!specs) {
      return res.status(503).json({
        error: 'Level specifications not available',
        message: 'The level-specs.json file needs to be present. Please check deployment.'
      });
    }

    // Tokenize text
    const words = tokenizeText(text);
    const uniqueWords = [...new Set(words)];
    const sentences = splitIntoSentences(text);

    // Get max words per sentence for this level (from specs)
    const maxWordsPerSentence = getMaxWordsPerSentence(level);
    const levelSpec = specs[level];

    // Analyze basic text statistics
    const analysis = {
      totalWords: words.length,
      uniqueWords: uniqueWords.length,
      sentences: sentences.length,
      avgWordsPerSentence: sentences.length > 0
        ? Math.round((words.length / sentences.length) * 10) / 10
        : 0,
      maxWordsInSentence: 0
    };

    // Analyze each sentence
    const sentenceCheck = analyzeSentences(text, maxWordsPerSentence);
    analysis.maxWordsInSentence = sentenceCheck.maxWordsInSentence;

    // Analyze word-level decodability
    let decodableWords = 0;
    let sightWords = 0;
    const unknownWords = [];
    const violations = [];

    uniqueWords.forEach(word => {
      const check = checkWordLevel(word, level, wordBanks);

      if (check.valid) {
        if (check.type === 'sight') {
          sightWords++;
        } else if (check.type === 'decodable') {
          decodableWords++;
        }
      } else {
        unknownWords.push(word);

        // Try to determine why it's unknown and suggest alternatives
        const numericLevel = levelCodeToIndex(level);
        const phonicsViolation = analyzePhonicsViolation(word, numericLevel);
        const suggestion = suggestAlternative(word, level, wordBanks);

        violations.push({
          word,
          reason: phonicsViolation || check.reason || 'Word not in level word bank',
          suggestion: suggestion || undefined
        });
      }
    });

    // Calculate decodability score
    const totalUniqueWords = uniqueWords.length;
    const knownWords = decodableWords + sightWords;
    const decodabilityScore = totalUniqueWords > 0
      ? Math.round((knownWords / totalUniqueWords) * 1000) / 10
      : 100;

    const decodability = {
      score: decodabilityScore,
      decodableWords,
      sightWords,
      unknownWords: unknownWords.length
    };

    // Overall pass/fail
    const passed = violations.length === 0 && sentenceCheck.passed;

    // Build response with level spec info
    const response = {
      level,
      levelName: levelSpec?.name,
      levelBand: levelSpec?.band,
      analysis,
      decodability,
      constraints: {
        maxWordsPerSentence: maxWordsPerSentence,
        decodabilityTarget: levelSpec?.constraints?.decodability || 'N/A'
      },
      sentenceCheck: {
        passed: sentenceCheck.passed,
        maxAllowed: maxWordsPerSentence,
        violations: sentenceCheck.violations
      },
      wordViolations: violations,
      passed
    };

    return res.status(200).json(response);

  } catch (error) {
    console.error('Validation error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
}
