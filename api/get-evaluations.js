/**
 * Get Book Evaluations API
 *
 * GET /api/get-evaluations - Get all cached evaluations
 * GET /api/get-evaluations?slug=xxx - Get single book evaluation
 */

const EVALUATIONS_SLUG = '_book-evaluations';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return res.status(500).json({ error: 'Supabase not configured' });
  }

  try {
    const response = await fetch(
      `${supabaseUrl}/rest/v1/books?slug=eq.${EVALUATIONS_SLUG}&select=data,updated_at`,
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
    const evaluations = data?.[0]?.data?.evaluations || {};
    const updated_at = data?.[0]?.updated_at;

    // If specific slug requested
    const { slug } = req.query;
    if (slug) {
      const evaluation = evaluations[slug];
      if (!evaluation) {
        return res.status(404).json({ error: `No evaluation found for: ${slug}` });
      }
      return res.status(200).json({
        success: true,
        evaluation
      });
    }

    // Return all evaluations with summary stats
    const evalList = Object.values(evaluations);
    const stats = {
      total: evalList.length,
      good: evalList.filter(e => e.overall?.verdict === 'good').length,
      needs_improvement: evalList.filter(e => e.overall?.verdict === 'needs_improvement').length,
      poor: evalList.filter(e => e.overall?.verdict === 'poor').length,
      avg_score: evalList.length > 0
        ? Math.round(evalList.reduce((s, e) => s + (e.overall?.score || 0), 0) / evalList.length * 10) / 10
        : 0
    };

    return res.status(200).json({
      success: true,
      stats,
      evaluations,
      updated_at
    });

  } catch (error) {
    console.error('Get evaluations error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
