/**
 * Vercel Serverless Function: Generate Image via MuleRouter
 *
 * Proxies image generation requests to MuleRouter API.
 * Returns the generated image URL (user downloads/saves manually).
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

  // Only allow POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.MULEROUTER_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'API key not configured' });
  }

  try {
    const { prompt, model, slug, page, reference, referenceIsUrl } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    // Build the API endpoint based on model
    let endpoint;
    let body;

    switch (model) {
      case 'gemini-3-pro':
        // Google Gemini 3 Pro Image (Nano Banana Pro) - newest, best quality
      case 'gemini-flash':
        // Google Gemini 2.5 Flash Image
        const googleApiKey = process.env.GOOGLE_AI_API_KEY;
        if (!googleApiKey) {
          return res.status(500).json({ error: 'Google API key not configured' });
        }

        // If reference is a URL, fetch it and convert to base64
        let imagenRef = reference;
        if (reference && referenceIsUrl) {
          console.log(`Fetching reference image from URL for Imagen 3: ${reference}`);
          try {
            const imgResponse = await fetch(reference);
            if (!imgResponse.ok) {
              throw new Error(`Failed to fetch reference image: ${imgResponse.status}`);
            }
            const imgBuffer = await imgResponse.arrayBuffer();
            imagenRef = Buffer.from(imgBuffer).toString('base64');
          } catch (fetchError) {
            console.error('Failed to fetch reference image:', fetchError);
            throw new Error(`Could not fetch reference image: ${fetchError.message}`);
          }
        } else if (imagenRef && imagenRef.startsWith('data:')) {
          // Strip data URL prefix for Gemini API
          imagenRef = imagenRef.split(',')[1];
        }

        // Select model based on user choice
        const geminiModel = model === 'gemini-3-pro' ? 'gemini-3-pro-image-preview' : 'gemini-2.5-flash-image';

        // Add reference image if provided (for style guidance in prompt)
        if (imagenRef) {
          // Use selected Gemini model for image-to-image with style reference
          const geminiFlashUrl = `https://generativelanguage.googleapis.com/v1beta/models/${geminiModel}:generateContent?key=${googleApiKey}`;

          const flashBody = {
            contents: [{
              parts: [
                {
                  inline_data: {
                    mime_type: "image/png",
                    data: imagenRef
                  }
                },
                {
                  text: `Based on the style of this reference image, generate a new image with this description: ${prompt}. Output only the generated image.`
                }
              ]
            }],
            generationConfig: {
              responseModalities: ["image", "text"],
              responseMimeType: "text/plain"
            }
          };

          const flashResponse = await fetch(geminiFlashUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(flashBody)
          });

          const flashResult = await flashResponse.json();

          if (!flashResponse.ok) {
            throw new Error(flashResult.error?.message || `Gemini error: ${flashResponse.status}`);
          }

          // Extract image from response
          const candidates = flashResult.candidates;
          if (candidates && candidates[0]?.content?.parts) {
            for (const part of candidates[0].content.parts) {
              if (part.inlineData) {
                // Return as data URL
                const imageUrl = `data:${part.inlineData.mimeType};base64,${part.inlineData.data}`;
                return res.status(200).json({
                  success: true,
                  url: imageUrl,
                  path: `${slug}_page_${page}.png`,
                  message: 'Image generated with Gemini Flash. Right-click to save.'
                });
              }
            }
          }
          throw new Error('No image in Gemini response');
        }

        // No reference - use selected Gemini model for text-to-image
        const t2iUrl = `https://generativelanguage.googleapis.com/v1beta/models/${geminiModel}:generateContent?key=${googleApiKey}`;
        const t2iBody = {
          contents: [{
            parts: [{ text: prompt }]
          }],
          generationConfig: {
            responseModalities: ["image", "text"]
          }
        };

        const t2iResponse = await fetch(t2iUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(t2iBody)
        });

        const t2iResult = await t2iResponse.json();

        if (!t2iResponse.ok) {
          throw new Error(t2iResult.error?.message || `Gemini error: ${t2iResponse.status}`);
        }

        // Extract image from response
        const t2iCandidates = t2iResult.candidates;
        if (t2iCandidates && t2iCandidates[0]?.content?.parts) {
          for (const part of t2iCandidates[0].content.parts) {
            if (part.inlineData) {
              const imageUrl = `data:${part.inlineData.mimeType};base64,${part.inlineData.data}`;
              return res.status(200).json({
                success: true,
                url: imageUrl,
                path: `${slug}_page_${page}.png`,
                message: 'Image generated with Gemini 2.5 Flash. Right-click to save.'
              });
            }
          }
        }
        throw new Error('No image in Gemini response');

      case 'wan2.6-image':
        // Image-to-image with reference(s) - supports up to 3
        endpoint = '/vendors/alibaba/v1/wan2.6-image/generation';

        // Handle array of references or single reference
        let referenceImages = [];
        const refArray = Array.isArray(reference) ? reference : (reference ? [reference] : []);

        for (const ref of refArray.slice(0, 3)) { // Max 3 refs for wan2.6
          if (referenceIsUrl) {
            console.log(`Fetching reference image from URL: ${ref}`);
            try {
              const imgResponse = await fetch(ref);
              if (!imgResponse.ok) {
                throw new Error(`Failed to fetch reference image: ${imgResponse.status}`);
              }
              const imgBuffer = await imgResponse.arrayBuffer();
              const base64 = Buffer.from(imgBuffer).toString('base64');
              const contentType = imgResponse.headers.get('content-type') || 'image/png';
              referenceImages.push(`data:${contentType};base64,${base64}`);
              console.log(`Converted URL to base64, length: ${referenceImages[referenceImages.length-1].length}`);
            } catch (fetchError) {
              console.error('Failed to fetch reference image:', fetchError);
              throw new Error(`Could not fetch reference image: ${fetchError.message}`);
            }
          } else {
            referenceImages.push(ref);
          }
        }
        console.log(`Using ${referenceImages.length} reference image(s) for wan2.6`);

        body = {
          prompt,
          images: referenceImages,
          size: '1024*1024',
          n: 1
        };
        break;

      case 'wan2.6-t2i':
        // Text-to-image only
        endpoint = '/vendors/alibaba/v1/wan2.6-t2i/generation';
        body = {
          prompt,
          size: '1024*1024',
          n: 1
        };
        break;

      case 'nano-banana-pro':
        // Image-to-image with reference (softer, friendlier style)
        endpoint = reference ? '/vendors/google/v1/nano-banana-pro/edit' : '/vendors/google/v1/nano-banana-pro/generation';

        // If reference is a URL, fetch it and convert to base64
        let nanoBananaRef = reference;
        if (reference && referenceIsUrl) {
          console.log(`Fetching reference image from URL for nano-banana: ${reference}`);
          try {
            const imgResponse = await fetch(reference);
            if (!imgResponse.ok) {
              throw new Error(`Failed to fetch reference image: ${imgResponse.status}`);
            }
            const imgBuffer = await imgResponse.arrayBuffer();
            const base64 = Buffer.from(imgBuffer).toString('base64');
            const contentType = imgResponse.headers.get('content-type') || 'image/png';
            nanoBananaRef = `data:${contentType};base64,${base64}`;
          } catch (fetchError) {
            console.error('Failed to fetch reference image:', fetchError);
            throw new Error(`Could not fetch reference image: ${fetchError.message}`);
          }
        }

        body = {
          prompt,
          aspect_ratio: '1:1',
          resolution: '2K'
        };
        if (nanoBananaRef) {
          body.images = [nanoBananaRef];
        }
        break;

      case 'wan2.5-i2i':
        // Wan 2.5 Image-to-Image (preview model)
        endpoint = '/vendors/alibaba/v1/wan2.5-i2i-preview/generation';

        // If reference is a URL, fetch it and convert to base64
        let wan25Ref = reference;
        if (reference && referenceIsUrl) {
          console.log(`Fetching reference image from URL for wan2.5: ${reference}`);
          try {
            const imgResponse = await fetch(reference);
            if (!imgResponse.ok) {
              throw new Error(`Failed to fetch reference image: ${imgResponse.status}`);
            }
            const imgBuffer = await imgResponse.arrayBuffer();
            const base64 = Buffer.from(imgBuffer).toString('base64');
            const contentType = imgResponse.headers.get('content-type') || 'image/png';
            wan25Ref = `data:${contentType};base64,${base64}`;
          } catch (fetchError) {
            console.error('Failed to fetch reference image:', fetchError);
            throw new Error(`Could not fetch reference image: ${fetchError.message}`);
          }
        }

        body = {
          prompt,
          images: wan25Ref ? [wan25Ref] : [],
          size: '1024*1024',
          n: 1
        };
        break;

      default:
        return res.status(400).json({ error: `Unknown model: ${model}` });
    }

    // Submit the generation task
    const submitResponse = await fetch(`${MULEROUTER_API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(body)
    });

    let submitResult;
    try {
      const responseText = await submitResponse.text();
      if (!responseText) {
        throw new Error(`MuleRouter returned empty response (status ${submitResponse.status})`);
      }
      submitResult = JSON.parse(responseText);
    } catch (parseError) {
      throw new Error(`MuleRouter response parse error: ${parseError.message}`);
    }

    if (!submitResponse.ok) {
      throw new Error(submitResult.error || submitResult.message || `MuleRouter error: ${submitResponse.status}`);
    }

    // For async APIs, poll for result
    // Debug: check what's in task_info
    const taskInfo = submitResult.task_info;
    const taskId = submitResult.task_id || taskInfo?.task_id || taskInfo?.id;

    if (!taskId && taskInfo) {
      throw new Error(`task_info present but no task_id. task_info keys: ${Object.keys(taskInfo).join(', ')}`);
    }

    if (taskId) {
      // Return task info for frontend polling (Vercel has timeout limits)
      // Status is checked by GET {endpoint}/{taskId} - append taskId to generation endpoint
      return res.status(200).json({
        success: true,
        pending: true,
        taskId: taskId,
        statusEndpoint: endpoint,  // Keep the generation endpoint, taskId appended by check-status
        message: 'Image generation started. Polling for result...'
      });
    }

    // For sync APIs, result is immediate - check various response formats
    const images = submitResult.images || submitResult.output?.images || submitResult.data?.images;
    if (images && images.length > 0) {
      return res.status(200).json({
        success: true,
        url: images[0].url || images[0],
        path: `${slug}_page_${page}.png`,
        message: 'Image generated. Right-click to save.'
      });
    }

    // Return debug info if no images found
    throw new Error(`No image returned. Response keys: ${Object.keys(submitResult).join(', ')}`);

  } catch (error) {
    console.error('Generation error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Generation failed'
    });
  }
}

async function pollForResult(taskId, endpoint, apiKey, maxWait = 120000) {
  const statusEndpoint = endpoint.replace('/generation', '/status');
  const startTime = Date.now();

  while (Date.now() - startTime < maxWait) {
    await sleep(3000);

    const statusResponse = await fetch(`${MULEROUTER_API_URL}${statusEndpoint}?task_id=${taskId}`, {
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
    });

    const statusResult = await statusResponse.json();
    const status = statusResult.status || statusResult.task_info?.status;

    if (status === 'succeeded' || status === 'completed' || status === 'SUCCEEDED') {
      // Check various possible image locations
      const images = statusResult.images ||
                    statusResult.result?.images ||
                    statusResult.output?.images ||
                    statusResult.task_info?.output?.images;

      if (images && images.length > 0) {
        // Handle both string URLs and object with url property
        return typeof images[0] === 'string' ? images[0] : images[0].url;
      }
      throw new Error(`Task completed but no image found. Keys: ${Object.keys(statusResult).join(', ')}`);
    }

    if (status === 'failed' || status === 'FAILED') {
      throw new Error(statusResult.error || statusResult.task_info?.error || 'Task failed');
    }

    // Still pending, continue polling
  }

  throw new Error('Timeout waiting for image generation');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
