/**
 * Get book data - checks Supabase first, falls back to static file
 */

export default async function handler(req, res) {
  // Prevent browser caching of API responses
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');
  res.setHeader('Pragma', 'no-cache');

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { slug } = req.query;

  if (!slug) {
    return res.status(400).json({ error: 'Missing slug parameter' });
  }

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  try {
    // Try Supabase first if configured
    if (supabaseUrl && supabaseKey) {
      const supabaseResponse = await fetch(
        `${supabaseUrl}/rest/v1/books?slug=eq.${slug}&select=data`,
        {
          headers: {
            'Authorization': `Bearer ${supabaseKey}`,
            'apikey': supabaseKey
          }
        }
      );

      if (supabaseResponse.ok) {
        const rows = await supabaseResponse.json();
        if (rows && rows.length > 0 && rows[0].data) {
          return res.status(200).json({
            source: 'supabase',
            book: rows[0].data
          });
        }
      }
    }

    // Fall back to static file
    const staticUrl = `https://funbookies.com/books/${slug}.json`;
    const staticResponse = await fetch(staticUrl);

    if (!staticResponse.ok) {
      return res.status(404).json({ error: `Book not found: ${slug}` });
    }

    const book = await staticResponse.json();
    return res.status(200).json({
      source: 'static',
      book
    });

  } catch (error) {
    console.error('Get book error:', error);
    return res.status(500).json({ error: error.message });
  }
}
