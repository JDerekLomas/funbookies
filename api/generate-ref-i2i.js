/**
 * Vercel Serverless Function: Generate Reference Image via I2I
 *
 * Uses an existing image as style reference to generate a new reference.
 * Part of the cascade workflow:
 * - characters.png (T2I) → settings.png (I2I) → style.png (I2I)
 *
 * Cost: $0.03 per image via wan2.6-image
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
      prompt,
      referenceImage,  // The characters.png or other seed image
      referenceIsUrl,
      slug,
      refType  // 'settings' | 'style' | 'scene'
    } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'prompt is required' });
    }

    if (!referenceImage) {
      return res.status(400).json({ error: 'referenceImage is required for I2I' });
    }

    // Convert URL to base64 if needed
    let imageData = referenceImage;
    if (referenceIsUrl || (referenceImage.startsWith('http') || referenceImage.startsWith('/'))) {
      console.log(`Fetching reference image from URL: ${referenceImage}`);
      try {
        // Handle relative URLs
        const fullUrl = referenceImage.startsWith('/')
          ? `${req.headers.origin || 'https://funbookies.com'}${referenceImage}`
          : referenceImage;

        const imgResponse = await fetch(fullUrl);
        if (!imgResponse.ok) {
          throw new Error(`Failed to fetch reference: ${imgResponse.status}`);
        }
        const imgBuffer = await imgResponse.arrayBuffer();
        const base64 = Buffer.from(imgBuffer).toString('base64');
        const contentType = imgResponse.headers.get('content-type') || 'image/png';
        imageData = `data:${contentType};base64,${base64}`;
        console.log(`Converted to base64, length: ${imageData.length}`);
      } catch (fetchError) {
        console.error('Failed to fetch reference:', fetchError);
        throw new Error(`Could not fetch reference: ${fetchError.message}`);
      }
    }

    // Use wan2.6-image for I2I ($0.03)
    const endpoint = '/vendors/alibaba/v1/wan2.6-image/generation';
    const body = {
      prompt: enhancePrompt(prompt, refType),
      images: [imageData],
      size: '1024*1024',
      n: 1
    };

    console.log(`Generating ${refType || 'reference'} via I2I...`);

    const response = await fetch(`${MULEROUTER_API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(body)
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || result.message || `API error: ${response.status}`);
    }

    // Check for async task
    const taskId = result.task_id || result.task_info?.task_id;
    if (taskId) {
      return res.status(200).json({
        success: true,
        pending: true,
        taskId,
        statusEndpoint: endpoint,
        refType,
        slug,
        message: `${refType || 'Reference'} I2I generation started.`
      });
    }

    // Sync result
    const images = result.images || result.output?.images;
    if (images && images.length > 0) {
      return res.status(200).json({
        success: true,
        url: images[0].url || images[0],
        refType,
        slug,
        path: `${slug}_${refType || 'ref'}.png`
      });
    }

    throw new Error('No image returned');

  } catch (error) {
    console.error('I2I generation error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'I2I generation failed'
    });
  }
}

function enhancePrompt(prompt, refType) {
  const suffix = '\n\nMaintain exact style consistency with the reference image. CRITICAL: NO TEXT, NO WORDS, NO LETTERS.';

  switch (refType) {
    case 'settings':
      return `Environment/background reference: ${prompt}${suffix}`;
    case 'style':
      return `Style palette showing colors, textures, and mood: ${prompt}${suffix}`;
    case 'scene':
      return `Single scene illustration: ${prompt}${suffix}`;
    default:
      return `${prompt}${suffix}`;
  }
}
