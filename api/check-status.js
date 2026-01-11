/**
 * Vercel Serverless Function: Check Image Generation Status
 */

const MULEROUTER_API_URL = 'https://api.mulerouter.ai';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.MULEROUTER_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'API key not configured' });
  }

  const { taskId, endpoint } = req.query;

  if (!taskId || !endpoint) {
    return res.status(400).json({ error: 'taskId and endpoint required' });
  }

  try {
    const statusResponse = await fetch(`${MULEROUTER_API_URL}${endpoint}?task_id=${taskId}`, {
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
    });

    const statusResult = await statusResponse.json();
    const status = statusResult.status || statusResult.task_info?.status;

    if (status === 'succeeded' || status === 'completed' || status === 'SUCCEEDED') {
      const images = statusResult.images ||
                    statusResult.result?.images ||
                    statusResult.output?.images ||
                    statusResult.task_info?.output?.images;

      if (images && images.length > 0) {
        const url = typeof images[0] === 'string' ? images[0] : images[0].url;
        return res.status(200).json({
          success: true,
          completed: true,
          url: url
        });
      }
      return res.status(200).json({
        success: false,
        error: `Completed but no image. Keys: ${Object.keys(statusResult).join(', ')}`
      });
    }

    if (status === 'failed' || status === 'FAILED') {
      return res.status(200).json({
        success: false,
        error: statusResult.error || statusResult.task_info?.error || 'Task failed'
      });
    }

    // Still pending
    return res.status(200).json({
      success: true,
      pending: true,
      status: status || 'unknown'
    });

  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
