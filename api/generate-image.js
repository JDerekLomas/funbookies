/**
 * Vercel Serverless Function: Generate Image via MuleRouter
 *
 * Proxies image generation requests to MuleRouter API.
 * Returns the generated image URL (user downloads/saves manually).
 */

const MULEROUTER_API_URL = 'https://api.mulerouter.ai';

export default async function handler(req, res) {
  // Only allow POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.MULEROUTER_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'API key not configured' });
  }

  try {
    const { prompt, model, slug, page, reference } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    // Build the API endpoint based on model
    let endpoint;
    let body;

    switch (model) {
      case 'wan2.6-image':
        // Image-to-image with reference
        endpoint = '/vendors/alibaba/v1/wan2.6-image/generation';
        body = {
          prompt,
          images: reference ? [reference] : [],
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
        // Reference sheet generation
        endpoint = '/vendors/fal/nano-banana-pro/generation';
        body = {
          prompt,
          aspect_ratio: '1:1',
          num_images: 1
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

    const submitResult = await submitResponse.json();

    if (!submitResponse.ok) {
      throw new Error(submitResult.error || submitResult.message || 'API request failed');
    }

    // For async APIs, poll for result
    // Debug: check what's in task_info
    const taskInfo = submitResult.task_info;
    const taskId = submitResult.task_id || taskInfo?.task_id || taskInfo?.id;

    if (!taskId && taskInfo) {
      throw new Error(`task_info present but no task_id. task_info keys: ${Object.keys(taskInfo).join(', ')}`);
    }

    if (taskId) {
      const imageUrl = await pollForResult(taskId, endpoint, apiKey);
      return res.status(200).json({
        success: true,
        url: imageUrl,
        path: `${slug}_page_${page}.png`,
        message: 'Image generated. Right-click to save.'
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
