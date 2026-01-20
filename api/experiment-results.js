// Vercel Serverless Function for Experiment Results Storage
// Uses Vercel Blob storage for persistence

export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const BLOB_PATH = 'experiments/letter-sounds-results.json';

  if (req.method === 'GET') {
    try {
      const blobToken = process.env.BLOB_READ_WRITE_TOKEN;
      if (blobToken) {
        const { list } = await import('@vercel/blob');
        const { blobs } = await list({ prefix: 'experiments/' });
        const blob = blobs.find(b => b.pathname === BLOB_PATH);

        if (blob) {
          const response = await fetch(blob.url);
          if (response.ok) {
            const data = await response.json();
            return res.status(200).json(data);
          }
        }
      }
      return res.status(200).json({ results: [] });
    } catch (error) {
      console.error('Error fetching results:', error);
      return res.status(200).json({ results: [] });
    }
  }

  if (req.method === 'POST') {
    try {
      const { participant, selections, timestamp } = req.body;

      if (!participant || !selections) {
        return res.status(400).json({ error: 'Participant and selections are required' });
      }

      const newResult = {
        id: `result_${Date.now()}`,
        participant,
        selections,
        timestamp: timestamp || new Date().toISOString()
      };

      // Log results for now (Vercel function logs)
      console.log('EXPERIMENT_RESULT:', JSON.stringify(newResult));

      // Return success - results are logged to Vercel
      return res.status(200).json({
        success: true,
        message: 'Results recorded',
        resultId: newResult.id
      });

    } catch (error) {
      console.error('Error saving results:', error);
      return res.status(500).json({
        error: 'Failed to save results',
        details: error.message,
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
      });
    }
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
