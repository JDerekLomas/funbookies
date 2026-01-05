// Vercel Serverless Function for Book Feedback Storage
// Uses Vercel Blob storage for persistence

export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // For now, store feedback in a simple in-memory approach
  // In production, this would use Vercel Blob or KV storage

  if (req.method === 'GET') {
    // Get feedback for a specific book or all feedback
    const { bookId } = req.query;

    try {
      // Try to fetch from Vercel Blob if configured
      const blobUrl = process.env.FEEDBACK_BLOB_URL;
      if (blobUrl) {
        const response = await fetch(blobUrl);
        if (response.ok) {
          const data = await response.json();
          if (bookId) {
            // Filter for specific book
            const filtered = {};
            Object.keys(data).forEach(key => {
              if (key.startsWith(bookId)) {
                filtered[key] = data[key];
              }
            });
            return res.status(200).json(filtered);
          }
          return res.status(200).json(data);
        }
      }

      // Return empty if no blob configured
      return res.status(200).json({});
    } catch (error) {
      console.error('Error fetching feedback:', error);
      return res.status(200).json({});
    }
  }

  if (req.method === 'POST') {
    try {
      const { bookId, feedback } = req.body;

      if (!feedback) {
        return res.status(400).json({ error: 'Feedback data is required' });
      }

      // If Vercel Blob is configured, store there
      const blobToken = process.env.BLOB_READ_WRITE_TOKEN;
      if (blobToken) {
        const { put } = await import('@vercel/blob');

        // Get existing feedback
        let existingFeedback = {};
        try {
          const existingUrl = process.env.FEEDBACK_BLOB_URL;
          if (existingUrl) {
            const existingRes = await fetch(existingUrl);
            if (existingRes.ok) {
              existingFeedback = await existingRes.json();
            }
          }
        } catch (e) {
          // Start fresh if no existing feedback
        }

        // Merge new feedback
        const merged = { ...existingFeedback, ...feedback };

        // Store to blob
        const blob = await put('feedback/book-feedback.json', JSON.stringify(merged), {
          access: 'public',
          addRandomSuffix: false,
        });

        return res.status(200).json({
          success: true,
          message: 'Feedback saved to cloud storage',
          url: blob.url
        });
      }

      // If no blob storage, just acknowledge and rely on client-side storage
      return res.status(200).json({
        success: true,
        message: 'Feedback acknowledged (using local storage - configure BLOB_READ_WRITE_TOKEN for cloud persistence)'
      });

    } catch (error) {
      console.error('Error saving feedback:', error);
      return res.status(500).json({ error: 'Failed to save feedback' });
    }
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
