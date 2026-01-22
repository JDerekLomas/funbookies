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

        // Filter out special slugs (start with _), drafts, and extract metadata from data JSONB
        // Only show published books (status === 'published') or legacy books without status field
        // Also filter out incomplete books (no level, level is '?'/'unknown', or no story pages)
        const books = rows
          .filter(row => row.slug && !row.slug.startsWith('_') && row.data)
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
          })
          .map(row => ({
            slug: row.slug,
            jsonFile: `${row.slug}.json`,
            title: row.data.title || row.slug,
            level: row.data.level || '?',
            band: row.data.band || null,
            skill: row.data.skill || row.data.targetPhonics || '',
            coverImg: row.data.coverImage || `/images/covers/${row.slug}.png`,
            created: row.data.created || null,
            updated_at: row.updated_at
          }));

        return res.status(200).json(books);
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
          coverImg: book.coverImg || `/images/covers/${book.slug}.png`
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
