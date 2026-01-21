/**
 * Batch Book Evaluation API
 *
 * POST /api/evaluate-batch
 * Body: { slugs?: string[], all?: boolean, skipCached?: boolean }
 *
 * Evaluates multiple books. If `all` is true, evaluates all books in manifest.
 * Returns progress updates via streaming or final results.
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { slugs, all = false, skipCached = true } = req.body;

  if (!slugs && !all) {
    return res.status(400).json({ error: 'Provide slugs array or set all=true' });
  }

  try {
    // Get list of books to evaluate
    let booksToEvaluate = slugs || [];

    if (all) {
      // Fetch manifest
      const manifestRes = await fetch('https://funbookies.com/books/manifest.json');
      const manifest = await manifestRes.json();
      booksToEvaluate = manifest.map(b => b.slug);
    }

    // Filter out system slugs
    booksToEvaluate = booksToEvaluate.filter(s => !s.startsWith('_'));

    // If skipCached, check which ones already have evaluations
    if (skipCached) {
      const evalsRes = await fetch(`https://${req.headers.host}/api/get-evaluations`);
      const evalsData = await evalsRes.json();
      const cached = Object.keys(evalsData.evaluations || {});
      booksToEvaluate = booksToEvaluate.filter(s => !cached.includes(s));
    }

    if (booksToEvaluate.length === 0) {
      return res.status(200).json({
        success: true,
        message: 'All books already evaluated',
        evaluated: 0
      });
    }

    // Evaluate books sequentially to avoid rate limits
    const results = {
      success: [],
      failed: [],
      total: booksToEvaluate.length
    };

    for (const slug of booksToEvaluate) {
      try {
        const evalRes = await fetch(`https://${req.headers.host}/api/evaluate-book`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ slug })
        });

        const evalData = await evalRes.json();

        if (evalData.success) {
          results.success.push({
            slug,
            score: evalData.evaluation.overall?.score,
            verdict: evalData.evaluation.overall?.verdict
          });
        } else {
          results.failed.push({ slug, error: evalData.error });
        }
      } catch (err) {
        results.failed.push({ slug, error: err.message });
      }

      // Small delay to avoid rate limits
      await new Promise(r => setTimeout(r, 500));
    }

    return res.status(200).json({
      success: true,
      evaluated: results.success.length,
      failed: results.failed.length,
      results
    });

  } catch (error) {
    console.error('Batch evaluation error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}

export const config = {
  maxDuration: 300 // 5 minutes for batch processing
};
