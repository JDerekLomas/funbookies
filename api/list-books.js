/**
 * List all available books
 *
 * Returns array of book metadata from Supabase.
 * Books are stored with slug as key and full book JSON in `data` column.
 */

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
    const includeDrafts = req.query.includeDrafts === 'true';

    if (supabaseUrl && supabaseKey) {
      // Fetch all books from Supabase
      // Data is stored in JSONB `data` column, so we select slug, data, updated_at
      const response = await fetch(
        `${supabaseUrl}/rest/v1/books?select=slug,data,updated_at&order=updated_at.desc`,
        {
          headers: {
            'apikey': supabaseKey,
            'Authorization': `Bearer ${supabaseKey}`
          }
        }
      );

      if (response.ok) {
        const rows = await response.json();

        // Filter out special slugs (start with _) and extract metadata from data JSONB
        let books = rows
          .filter(row => row.slug && !row.slug.startsWith('_') && row.data);

        if (!includeDrafts) {
          // Default behavior: Only show published books or legacy books without status
          // Also filter out incomplete books
          books = books
            .filter(row => !row.data.status || row.data.status === 'published')
            .filter(row => row.data.level && row.data.level !== '?' && row.data.level !== 'unknown')
            .filter(row => {
              // Must have pages array with at least one story page
              const pages = row.data.pages || [];
              return pages.some(p => p.type === 'story' && p.text);
            })
            .filter(row => {
              // Exclude specific incomplete books (have content but no images)
              const incompleteBooks = ['kittens-hidden-basket', 'friends-at-the-pond', 'game-quest', 'fern_gust_orange_bible'];
              return !incompleteBooks.includes(row.slug);
            });
        }

        const result = books.map(row => ({
          slug: row.slug,
          jsonFile: `${row.slug}.json`,
          title: row.data.title || row.slug,
          level: row.data.level || '?',
          band: row.data.band || null,
          skill: row.data.skill || row.data.targetPhonics || '',
          coverImg: row.data.coverImage || row.data.thumbnail || `/images/thumbs/${row.slug}.jpg`,
          created: row.data.created || null,
          updated_at: row.updated_at,
          status: row.data.status || 'published',
          wizardPhase: row.data.wizardPhase || null
        }));

        return res.status(200).json(result);
      } else {
        console.error('Supabase query failed:', await response.text());
      }
    }

    // Fallback: fetch from static manifest
    try {
      const manifestResponse = await fetch('https://funbookies.com/books/manifest.json');
      if (manifestResponse.ok) {
        const manifest = await manifestResponse.json();
        const books = manifest.map(book => ({
          slug: book.slug,
          jsonFile: book.jsonFile || `${book.slug}.json`,
          title: book.title,
          level: book.level,
          band: book.band,
          skill: book.skill || '',
          coverImg: book.coverImg || `/images/thumbs/${book.slug}.jpg`
        }));
        return res.status(200).json(books);
      }
    } catch (e) {
      console.error('Manifest fallback failed:', e);
    }

    // Final fallback: empty array
    return res.status(200).json([]);

  } catch (error) {
    console.error('List books error:', error);
    return res.status(500).json({
      error: error.message
    });
  }
}
