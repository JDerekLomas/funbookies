/**
 * Book Quality Ratings API
 *
 * GET - Load all book ratings
 * POST - Save all book ratings
 *
 * Uses existing Supabase `books` table with special slug `_quality-ratings`
 */

const RATINGS_SLUG = '_quality-ratings';

export default async function handler(req, res) {
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return res.status(500).json({ error: 'Supabase not configured' });
  }

  // GET - Load ratings
  if (req.method === 'GET') {
    try {
      const response = await fetch(
        `${supabaseUrl}/rest/v1/books?slug=eq.${RATINGS_SLUG}&select=data,updated_at`,
        {
          headers: {
            'Authorization': `Bearer ${supabaseKey}`,
            'apikey': supabaseKey
          }
        }
      );

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Fetch failed: ${error}`);
      }

      const data = await response.json();

      if (data && data.length > 0 && data[0].data) {
        return res.status(200).json({
          success: true,
          ratings: data[0].data.ratings || {},
          updated_at: data[0].updated_at
        });
      }

      // No ratings yet
      return res.status(200).json({
        success: true,
        ratings: {},
        updated_at: null
      });

    } catch (error) {
      console.error('Load ratings error:', error);
      return res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  // POST - Save ratings
  if (req.method === 'POST') {
    try {
      const { ratings } = req.body;

      if (!ratings || typeof ratings !== 'object') {
        return res.status(400).json({ error: 'Missing or invalid ratings object' });
      }

      const response = await fetch(
        `${supabaseUrl}/rest/v1/books`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${supabaseKey}`,
            'apikey': supabaseKey,
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates'
          },
          body: JSON.stringify({
            slug: RATINGS_SLUG,
            data: { ratings },
            updated_at: new Date().toISOString()
          })
        }
      );

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Save failed: ${error}`);
      }

      return res.status(200).json({
        success: true,
        message: 'Ratings saved'
      });

    } catch (error) {
      console.error('Save ratings error:', error);
      return res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
