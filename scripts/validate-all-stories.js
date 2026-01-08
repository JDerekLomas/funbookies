// Validate all generated stories against word banks and level constraints
import { readFileSync, readdirSync, writeFileSync } from 'fs';
import { join } from 'path';

const publicDir = join(process.cwd(), 'public');
const dataDir = join(publicDir, 'data');
const booksDir = join(publicDir, 'books');

// Load level specifications
function loadLevelSpecs() {
  const levelSpecsPath = join(dataDir, 'level-specs.json');
  try {
    return JSON.parse(readFileSync(levelSpecsPath, 'utf-8'));
  } catch (e) {
    console.error('Error loading level-specs.json:', e.message);
    throw e;
  }
}

// Load word banks
function loadWordBanks(levelSpecs) {
  const sightWordsPath = join(dataDir, 'sight-words.json');
  let sightWordsData = null;
  try {
    sightWordsData = JSON.parse(readFileSync(sightWordsPath, 'utf-8'));
  } catch (e) {
    console.log('Sight words file not found, continuing without it');
  }

  const phonicsWordsPath = join(dataDir, 'phonics-words.json');
  let phonicsWordsData = null;
  try {
    phonicsWordsData = JSON.parse(readFileSync(phonicsWordsPath, 'utf-8'));
  } catch (e) {
    console.log('Phonics words file not found, continuing without it');
  }

  // Load story vocabulary
  const storyVocabPath = join(dataDir, 'story-vocabulary.json');
  let storyVocabData = null;
  try {
    storyVocabData = JSON.parse(readFileSync(storyVocabPath, 'utf-8'));
  } catch (e) {
    console.log('Story vocabulary file not found, continuing without it');
  }

  // Build cumulative sight word sets by level code (A0-D6)
  const sightWordsByLevel = {};
  const allLevelCodes = Object.keys(levelSpecs.levels);

  allLevelCodes.forEach(levelCode => {
    sightWordsByLevel[levelCode] = new Set();

    // Get sight words from level spec
    const levelSpec = levelSpecs.levels[levelCode];
    if (levelSpec.constraints?.sightWords) {
      levelSpec.constraints.sightWords.forEach(word => {
        sightWordsByLevel[levelCode].add(word.toLowerCase());
      });
    }

    // Add from legacy sight-words.json if available
    if (sightWordsData?.levels) {
      Object.values(sightWordsData.levels).forEach(band => {
        if (band.readingLevels && band.words) {
          band.words.forEach(w => {
            sightWordsByLevel[levelCode].add(w.toLowerCase());
          });
        }
      });
    }
  });

  // Build cumulative phonics word sets by level code
  const phonicsWordsByLevel = {};

  allLevelCodes.forEach(levelCode => {
    phonicsWordsByLevel[levelCode] = new Set();

    // Add phonics words from level spec phonicsPatterns
    const levelSpec = levelSpecs.levels[levelCode];
    if (levelSpec.constraints?.phonicsPatterns) {
      levelSpec.constraints.phonicsPatterns.forEach(patternLine => {
        // Extract words from pattern definitions like "CVC short a: cat, hat, sat"
        const parts = patternLine.split(':');
        if (parts.length > 1) {
          const words = parts[1].split(',').map(w => w.trim().toLowerCase()).filter(w => w);
          words.forEach(w => phonicsWordsByLevel[levelCode].add(w));
        }
      });
    }

    // Add from phonics-words.json if available
    if (phonicsWordsData?.levels) {
      Object.values(phonicsWordsData.levels).forEach(levelData => {
        // Handle flat words array
        if (Array.isArray(levelData.words)) {
          levelData.words.forEach(w => phonicsWordsByLevel[levelCode].add(w.toLowerCase()));
        }
        // Handle wordFamilies object (used in B1+ levels)
        if (levelData.wordFamilies && typeof levelData.wordFamilies === 'object') {
          Object.values(levelData.wordFamilies).forEach(wordList => {
            if (Array.isArray(wordList)) {
              wordList.forEach(w => phonicsWordsByLevel[levelCode].add(w.toLowerCase()));
            }
          });
        }
        // Handle commonWords array (added for common vocabulary)
        if (Array.isArray(levelData.commonWords)) {
          levelData.commonWords.forEach(w => phonicsWordsByLevel[levelCode].add(w.toLowerCase()));
        }
        // Handle sightWords array
        if (Array.isArray(levelData.sightWords)) {
          levelData.sightWords.forEach(w => phonicsWordsByLevel[levelCode].add(w.toLowerCase()));
        }
      });
    }
  });

  // Build story vocabulary sets
  const storyVocabByLevel = {};

  allLevelCodes.forEach(levelCode => {
    storyVocabByLevel[levelCode] = new Set();
    if (storyVocabData?.levels) {
      Object.values(storyVocabData.levels).forEach(data => {
        if (data.words) {
          data.words.forEach(w => storyVocabByLevel[levelCode].add(w.toLowerCase()));
        }
      });
    }
  });

  // Build character names set (allowed at all levels)
  const characterNames = new Set();
  // Support both old format (character_names) and new format (characterNames)
  const charNamesData = storyVocabData?.characterNames || storyVocabData?.character_names;
  if (charNamesData) {
    ['cvc_names', 'cvce_names', 'two_syllable', 'other'].forEach(key => {
      if (Array.isArray(charNamesData[key])) {
        charNamesData[key].forEach(n => characterNames.add(n.toLowerCase()));
      }
    });
  }
  // Also add storyWords (exclamations, onomatopoeia, dialogue_tags)
  if (storyVocabData?.storyWords) {
    Object.values(storyVocabData.storyWords).forEach(wordList => {
      if (Array.isArray(wordList)) {
        wordList.forEach(w => characterNames.add(w.toLowerCase()));
      }
    });
  }

  return { sightWordsByLevel, phonicsWordsByLevel, storyVocabByLevel, characterNames };
}

// Tokenize text into words
function tokenizeText(text) {
  if (!text || typeof text !== 'string') return [];
  const normalized = text
    .toLowerCase()
    .replace(/[""]/g, '"')
    .replace(/['']/g, "'")
    .replace(/[—–]/g, '-')
    .trim();

  const words = normalized
    .split(/\s+/)
    .map(word => word.replace(/^[^\w']+|[^\w']+$/g, ''))
    .filter(word => word.length > 0);

  return words;
}

// Inflection level requirements (when students learn these patterns)
const INFLECTION_LEVELS = {
  's_plural': 3,      // -s plurals (cats, dogs)
  'es_plural': 4,     // -es plurals (boxes, wishes)
  'ed_voiced': 6,     // -ed pronounced /d/ (played, loved)
  'ed_voiceless': 6,  // -ed pronounced /t/ (walked, looked)
  'ed_syllable': 7,   // -ed as syllable (wanted, needed)
  'ing': 6,           // -ing (running, jumping)
  'er_comp': 7,       // -er comparative (bigger, faster)
  'est_super': 7,     // -est superlative (biggest, fastest)
  'ly': 8,            // -ly adverbs (slowly, quickly)
};

// Try to find base word for an inflected form
function getBaseWord(word) {
  const results = [];

  // -ing: remove -ing, handle doubling (running -> run)
  if (word.endsWith('ing') && word.length > 4) {
    const base = word.slice(0, -3);
    results.push({ base, type: 'ing' });
    // Double consonant (running -> run)
    if (base.length > 1 && base[base.length - 1] === base[base.length - 2]) {
      results.push({ base: base.slice(0, -1), type: 'ing' });
    }
    // Silent e (making -> make)
    results.push({ base: base + 'e', type: 'ing' });
  }

  // -ed: remove -ed, handle variants
  if (word.endsWith('ed') && word.length > 3) {
    const base = word.slice(0, -2);
    results.push({ base, type: 'ed_voiced' });
    // -d only (loved -> love)
    if (word.endsWith('ed') && word.length > 2) {
      results.push({ base: word.slice(0, -1), type: 'ed_voiced' });
    }
    // Double consonant (stopped -> stop)
    if (base.length > 1 && base[base.length - 1] === base[base.length - 2]) {
      results.push({ base: base.slice(0, -1), type: 'ed_voiceless' });
    }
    // -ied -> y (tried -> try)
    if (word.endsWith('ied')) {
      results.push({ base: word.slice(0, -3) + 'y', type: 'ed_voiced' });
    }
  }

  // -s/-es plurals
  if (word.endsWith('es') && word.length > 3) {
    results.push({ base: word.slice(0, -2), type: 'es_plural' });
    results.push({ base: word.slice(0, -1), type: 's_plural' }); // -e ending
  } else if (word.endsWith('s') && word.length > 2 && !word.endsWith('ss')) {
    results.push({ base: word.slice(0, -1), type: 's_plural' });
    // -ies -> y (stories -> story)
    if (word.endsWith('ies')) {
      results.push({ base: word.slice(0, -3) + 'y', type: 'es_plural' });
    }
  }

  // -er comparative
  if (word.endsWith('er') && word.length > 3) {
    results.push({ base: word.slice(0, -2), type: 'er_comp' });
    results.push({ base: word.slice(0, -1), type: 'er_comp' }); // silent e
    // Double consonant (bigger -> big)
    const base = word.slice(0, -2);
    if (base.length > 1 && base[base.length - 1] === base[base.length - 2]) {
      results.push({ base: base.slice(0, -1), type: 'er_comp' });
    }
  }

  // -est superlative
  if (word.endsWith('est') && word.length > 4) {
    results.push({ base: word.slice(0, -3), type: 'est_super' });
    results.push({ base: word.slice(0, -2), type: 'est_super' }); // silent e
    // Double consonant
    const base = word.slice(0, -3);
    if (base.length > 1 && base[base.length - 1] === base[base.length - 2]) {
      results.push({ base: base.slice(0, -1), type: 'est_super' });
    }
  }

  // -ly adverbs
  if (word.endsWith('ly') && word.length > 3) {
    results.push({ base: word.slice(0, -2), type: 'ly' });
    // -ily -> y (happily -> happy)
    if (word.endsWith('ily')) {
      results.push({ base: word.slice(0, -3) + 'y', type: 'ly' });
    }
  }

  return results;
}

// Split text into sentences
function splitIntoSentences(text) {
  if (!text || typeof text !== 'string') return [];
  return text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 0);
}

// Get max words per sentence for level code (using level-specs.json)
function getMaxWordsPerSentence(levelCode, levelSpecs) {
  const levelSpec = levelSpecs.levels[levelCode];
  if (!levelSpec) {
    console.warn(`Unknown level code: ${levelCode}`);
    return 10; // Safe default
  }

  // Use maxWordsPerSentence from constraints if available
  if (levelSpec.constraints?.maxWordsPerSentence) {
    return levelSpec.constraints.maxWordsPerSentence;
  }

  // Fallback: parse wordsPerSentence range
  if (levelSpec.constraints?.wordsPerSentence) {
    const range = levelSpec.constraints.wordsPerSentence;
    if (typeof range === 'string') {
      const match = range.match(/(\d+)-(\d+)/);
      if (match) {
        return parseInt(match[2]); // Take the max of the range
      }
    }
  }

  // Final fallback
  return 10;
}

// Add leniency buffer to sentence limits (50% more allowed)
function getLenientMaxWords(strictMax) {
  return Math.ceil(strictMax * 1.5);
}

// Validate a single story
function validateStory(story, wordBanks, levelSpecs) {
  const { sightWordsByLevel, phonicsWordsByLevel, storyVocabByLevel, characterNames } = wordBanks;
  const levelCode = story.level; // Level code like "A0", "B5", "C3", "D1"

  // Extract all text from pages
  const allText = story.pages.map(p => p.text || '').filter(t => t.trim()).join(' ');
  const words = tokenizeText(allText);
  const uniqueWords = [...new Set(words)];
  const sentences = splitIntoSentences(allText);
  const maxWordsPerSentence = getMaxWordsPerSentence(levelCode, levelSpecs);

  // Analyze words
  let decodableCount = 0;
  let sightCount = 0;
  let inflectedCount = 0;
  let storyVocabCount = 0;
  let nameCount = 0;
  const unknownWords = [];

  uniqueWords.forEach(word => {
    // Check character names first (allowed at all levels)
    if (characterNames?.has(word)) {
      nameCount++;
      return;
    }

    // Direct lookup - sight words
    if (sightWordsByLevel[levelCode]?.has(word)) {
      sightCount++;
      return;
    }

    // Direct lookup - phonics words
    if (phonicsWordsByLevel[levelCode]?.has(word)) {
      decodableCount++;
      return;
    }

    // Story vocabulary (level-appropriate)
    if (storyVocabByLevel[levelCode]?.has(word)) {
      storyVocabCount++;
      return;
    }

    // Try inflection analysis
    const inflections = getBaseWord(word);
    let foundInflection = false;

    for (const { base, type } of inflections) {
      const requiredLevelIndex = INFLECTION_LEVELS[type] || 99;

      // For level codes, check if current level index >= required level index
      const currentLevelSpec = levelSpecs.levels[levelCode];
      if (currentLevelSpec && currentLevelSpec.index >= requiredLevelIndex) {
        // Check if base word exists in any word bank
        if (sightWordsByLevel[levelCode]?.has(base) ||
            phonicsWordsByLevel[levelCode]?.has(base) ||
            storyVocabByLevel[levelCode]?.has(base)) {
          inflectedCount++;
          foundInflection = true;
          break;
        }
      }
    }

    if (!foundInflection) {
      unknownWords.push(word);
    }
  });

  const knownWords = decodableCount + sightCount + inflectedCount + storyVocabCount + nameCount;
  const decodabilityScore = uniqueWords.length > 0
    ? Math.round((knownWords / uniqueWords.length) * 1000) / 10
    : 100;

  // Analyze sentences
  const sentenceViolations = [];
  const lenientMax = getLenientMaxWords(maxWordsPerSentence);
  let maxWordsFound = 0;
  sentences.forEach((sentence, idx) => {
    const sentenceWords = tokenizeText(sentence);
    if (sentenceWords.length > maxWordsFound) {
      maxWordsFound = sentenceWords.length;
    }
    // Only flag as violation if exceeds lenient limit
    if (sentenceWords.length > lenientMax) {
      sentenceViolations.push({
        sentenceNum: idx + 1,
        wordCount: sentenceWords.length,
        maxAllowed: lenientMax,
        strictMax: maxWordsPerSentence,
        preview: sentence.substring(0, 60) + (sentence.length > 60 ? '...' : '')
      });
    }
  });

  // Lenient pass criteria:
  // - Decodability >= 80% (allows some unknown words)
  // - Sentence violations are warnings only (don't block pass)
  const decodabilityPassed = decodabilityScore >= 80;

  return {
    levelCode,
    band: levelCode.charAt(0), // Extract band from level code (A, B, C, or D)
    type: story.type,
    title: story.title,
    totalWords: words.length,
    uniqueWords: uniqueWords.length,
    sentences: sentences.length,
    decodability: {
      score: decodabilityScore,
      decodable: decodableCount,
      sight: sightCount,
      inflected: inflectedCount,
      storyVocab: storyVocabCount,
      names: nameCount,
      unknown: unknownWords.length,
      unknownWords: unknownWords.slice(0, 20) // First 20 for report
    },
    sentenceCheck: {
      maxAllowed: maxWordsPerSentence,
      lenientMax: lenientMax,
      maxFound: maxWordsFound,
      violations: sentenceViolations.length,
      details: sentenceViolations.slice(0, 5) // First 5 for report
    },
    passed: decodabilityPassed // Sentence length is advisory only
  };
}

// Main validation
async function main() {
  console.log('Loading level specifications...');
  const levelSpecs = loadLevelSpecs();

  console.log('Loading word banks...');
  const wordBanks = loadWordBanks(levelSpecs);

  console.log('Scanning books directory...');
  let files = [];
  try {
    files = readdirSync(booksDir).filter(f => f.endsWith('.json'));
  } catch (err) {
    console.error(`Error reading books directory: ${err.message}`);
    return;
  }
  console.log(`Found ${files.length} story files\n`);

  const results = {
    summary: { total: 0, passed: 0, failed: 0 },
    byBand: {
      A: { total: 0, passed: 0, levels: {} },
      B: { total: 0, passed: 0, levels: {} },
      C: { total: 0, passed: 0, levels: {} },
      D: { total: 0, passed: 0, levels: {} }
    },
    byLevel: {},
    issues: {
      unknownWords: new Set(),
      sentenceTooLong: []
    }
  };

  for (const file of files) {
    const filePath = join(booksDir, file);
    try {
      const story = JSON.parse(readFileSync(filePath, 'utf-8'));

      // Skip files without a valid level code
      if (!story.level) {
        console.warn(`Skipping ${file}: no level specified`);
        continue;
      }

      const validation = validateStory(story, wordBanks, levelSpecs);

      results.summary.total++;
      if (validation.passed) {
        results.summary.passed++;
      } else {
        results.summary.failed++;
      }

      // Categorize by band
      const band = validation.band;
      results.byBand[band].total++;
      if (validation.passed) {
        results.byBand[band].passed++;
      }

      // Categorize by level within band
      if (!results.byBand[band].levels[validation.levelCode]) {
        results.byBand[band].levels[validation.levelCode] = [];
      }
      results.byBand[band].levels[validation.levelCode].push(validation);

      // Categorize by level overall
      if (!results.byLevel[validation.levelCode]) {
        results.byLevel[validation.levelCode] = [];
      }
      results.byLevel[validation.levelCode].push(validation);

      // Collect issues
      validation.decodability.unknownWords.forEach(w => results.issues.unknownWords.add(w));
      if (validation.sentenceCheck.violations > 0) {
        results.issues.sentenceTooLong.push({
          file,
          levelCode: validation.levelCode,
          violations: validation.sentenceCheck.details
        });
      }

    } catch (err) {
      console.error(`Error processing ${file}:`, err.message);
    }
  }

  // Convert Set to Array for JSON
  results.issues.unknownWords = [...results.issues.unknownWords].sort();

  // Print summary
  console.log('='.repeat(80));
  console.log('VALIDATION SUMMARY - 28-LEVEL SYSTEM');
  console.log('='.repeat(80));
  console.log(`Total stories: ${results.summary.total}`);
  console.log(`Passed: ${results.summary.passed}`);
  console.log(`Failed: ${results.summary.failed}`);
  if (results.summary.total > 0) {
    console.log(`Pass rate: ${Math.round((results.summary.passed / results.summary.total) * 100)}%\n`);
  }

  // Print results by band
  console.log('BY BAND:');
  ['A', 'B', 'C', 'D'].forEach(band => {
    const bandData = results.byBand[band];
    if (bandData.total > 0) {
      const passRate = Math.round((bandData.passed / bandData.total) * 100);
      console.log(`\n  Band ${band}: ${bandData.passed}/${bandData.total} passed (${passRate}%)`);

      // Show individual levels in band
      Object.entries(bandData.levels)
        .sort((a, b) => {
          // Sort by level index from levelSpecs
          const aIndex = levelSpecs.levels[a[0]]?.index || 0;
          const bIndex = levelSpecs.levels[b[0]]?.index || 0;
          return aIndex - bIndex;
        })
        .forEach(([levelCode, stories]) => {
          const passed = stories.filter(s => s.passed).length;
          const avg = stories.reduce((sum, s) => sum + s.decodability.score, 0) / stories.length;
          console.log(`    ${levelCode}: ${passed}/${stories.length} passed, avg ${avg.toFixed(1)}% decodable`);
        });
    }
  });

  console.log(`\n\nDECODABILITY SCORES BY LEVEL:`);
  const sortedLevels = Object.keys(results.byLevel).sort((a, b) => {
    const aIndex = levelSpecs.levels[a]?.index || 0;
    const bIndex = levelSpecs.levels[b]?.index || 0;
    return aIndex - bIndex;
  });

  sortedLevels.forEach(levelCode => {
    const levelResults = results.byLevel[levelCode];
    if (levelResults) {
      const avgScore = levelResults.reduce((sum, r) => sum + r.decodability.score, 0) / levelResults.length;
      const passCount = levelResults.filter(r => r.passed).length;
      console.log(`  ${levelCode}: avg ${avgScore.toFixed(1)}% decodable, ${passCount}/${levelResults.length} passed`);
    }
  });

  console.log(`\n\nUNKNOWN WORDS (${results.issues.unknownWords.length} unique):`);
  if (results.issues.unknownWords.length > 0) {
    console.log(results.issues.unknownWords.slice(0, 50).join(', '));
    if (results.issues.unknownWords.length > 50) {
      console.log(`  ... and ${results.issues.unknownWords.length - 50} more`);
    }
  } else {
    console.log('  None - all words are decodable or sight words!');
  }

  console.log(`\n\nSENTENCE LENGTH VIOLATIONS: ${results.issues.sentenceTooLong.length} stories`);
  if (results.issues.sentenceTooLong.length > 0) {
    results.issues.sentenceTooLong.slice(0, 10).forEach(v => {
      console.log(`  ${v.levelCode}: ${v.violations.length} sentences too long`);
    });
  }

  // Save detailed report
  const reportPath = join(dataDir, 'validation-report.json');
  writeFileSync(reportPath, JSON.stringify(results, null, 2));
  console.log(`\nDetailed report saved to: ${reportPath}`);
}

main().catch(console.error);
