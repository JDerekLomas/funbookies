/**
 * Vercel Serverless Function: Generate Reference Images via Cascade
 *
 * Generates 3 reference images using cascade approach:
 * 1. characters.png - T2I ($0.15) - the seed
 * 2. settings.png - I2I ($0.03) - using characters as reference
 * 3. style.png - I2I ($0.03) - using characters as reference
 *
 * Total: $0.21 for 3 consistent reference images
 */

const MULEROUTER_API_URL = 'https://api.mulerouter.ai';

export default async function handler(req, res) {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.MULEROUTER_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'API key not configured' });
  }

  try {
    const {
      slug,
      charactersPrompt,
      settingsPrompt,
      stylePrompt,
      visualStyle,
      // Optional: skip generation if image already exists
      skipCharacters,
      skipSettings,
      skipStyle,
      // Optional: existing characters image to use as seed
      existingCharactersImage
    } = req.body;

    if (!slug) {
      return res.status(400).json({ error: 'slug is required' });
    }

    if (!charactersPrompt && !existingCharactersImage) {
      return res.status(400).json({ error: 'charactersPrompt or existingCharactersImage is required' });
    }

    const results = {
      characters: null,
      settings: null,
      style: null,
      tasks: {}
    };

    // Step 1: Generate characters.png via T2I (or use existing)
    let charactersImage = existingCharactersImage;

    if (!skipCharacters && !existingCharactersImage) {
      console.log('Step 1: Generating characters.png via T2I...');

      const t2iEndpoint = '/vendors/alibaba/v1/wan2.6-t2i/generation';
      const t2iBody = {
        prompt: buildCharactersPrompt(charactersPrompt, visualStyle),
        size: '1024*1024',
        n: 1
      };

      const t2iResponse = await fetch(`${MULEROUTER_API_URL}${t2iEndpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify(t2iBody)
      });

      const t2iResult = await t2iResponse.json();

      if (!t2iResponse.ok) {
        throw new Error(`Characters T2I failed: ${t2iResult.error || t2iResponse.status}`);
      }

      const taskId = t2iResult.task_id || t2iResult.task_info?.task_id;
      if (taskId) {
        results.tasks.characters = {
          taskId,
          endpoint: t2iEndpoint,
          status: 'pending'
        };
      }
    } else if (existingCharactersImage) {
      results.characters = existingCharactersImage;
    }

    // If characters task is pending, we need to wait or return for polling
    // For cascade, we return task IDs and let frontend poll
    // But we can also initiate settings/style tasks that depend on characters

    // Step 2 & 3: Generate settings.png and style.png via I2I
    // These need to wait for characters to complete
    // We'll return all task info for frontend to orchestrate

    if (!skipSettings && settingsPrompt) {
      results.tasks.settings = {
        prompt: buildSettingsPrompt(settingsPrompt, visualStyle),
        dependsOn: 'characters',
        status: 'waiting'
      };
    }

    if (!skipStyle && stylePrompt) {
      results.tasks.style = {
        prompt: buildStylePrompt(stylePrompt, visualStyle),
        dependsOn: 'characters',
        status: 'waiting'
      };
    }

    return res.status(200).json({
      success: true,
      slug,
      results,
      message: 'Cascade generation initiated. Poll for characters completion, then generate settings/style.',
      workflow: {
        step1: 'characters.png via T2I',
        step2: 'settings.png via I2I (uses characters as ref)',
        step3: 'style.png via I2I (uses characters as ref)'
      }
    });

  } catch (error) {
    console.error('Cascade generation error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Cascade generation failed'
    });
  }
}

function buildCharactersPrompt(userPrompt, visualStyle) {
  return `Character reference sheet for children's book:

${userPrompt}

STYLE: ${visualStyle || 'Soft watercolor children\'s book illustration, warm colors, friendly rounded shapes'}

LAYOUT: Show main character(s) in multiple poses/expressions:
- Front view with neutral expression
- Side view in action pose
- Happy/excited expression
- Sad/worried expression (if needed for story)

CRITICAL: NO TEXT, NO WORDS, NO LETTERS. Pure illustration only.
Maintain consistent character design across all poses.`;
}

function buildSettingsPrompt(userPrompt, visualStyle) {
  return `Environment/setting reference for children's book:

${userPrompt}

STYLE: ${visualStyle || 'Soft watercolor children\'s book illustration, warm colors, inviting atmosphere'}

Show the setting with:
- Clear spatial layout
- Key environmental details
- Appropriate lighting/mood
- Space for characters to inhabit

Match the style exactly from the character reference image.
CRITICAL: NO TEXT, NO WORDS, NO LETTERS. Pure illustration only.`;
}

function buildStylePrompt(userPrompt, visualStyle) {
  return `Style palette reference for children's book:

${userPrompt}

STYLE: ${visualStyle || 'Soft watercolor children\'s book illustration'}

Create a style reference showing:
- Color palette swatches
- Texture samples
- Lighting examples
- Mood/atmosphere samples

This should capture the overall visual feel to maintain consistency.
Match the style exactly from the character reference image.
CRITICAL: NO TEXT, NO WORDS, NO LETTERS. Pure illustration only.`;
}
