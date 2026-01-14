/**
 * Save book updates to Supabase
 *
 * Stores book JSON in a simple key-value table.
 * Falls back to static files if no Supabase entry exists.
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return res.status(500).json({ error: 'Supabase not configured' });
  }

  try {
    const { slug, pageIndex, field, value } = req.body;

    if (!slug || pageIndex === undefined || !field || value === undefined) {
      return res.status(400).json({
        error: 'Missing required fields: slug, pageIndex, field, value'
      });
    }

    // First, get current book data (from Supabase or fetch static file)
    let book;

    // Try to get from Supabase first
    const getResponse = await fetch(
      `${supabaseUrl}/rest/v1/books?slug=eq.${slug}&select=data`,
      {
        headers: {
          'Authorization': `Bearer ${supabaseKey}`,
          'apikey': supabaseKey
        }
      }
    );

    const existing = await getResponse.json();

    if (existing && existing.length > 0) {
      book = existing[0].data;
    } else {
      // Fetch from static file
      const staticResponse = await fetch(`https://funbookies.com/books/${slug}.json`);
      if (!staticResponse.ok) {
        throw new Error(`Book not found: ${slug}`);
      }
      book = await staticResponse.json();
    }

    // Update the field
    if (pageIndex === -1) {
      book[field] = value;
    } else if (book.pages && book.pages[pageIndex]) {
      // Handle special case for saving image with versions
      if (field === 'image_with_versions' && typeof value === 'object') {
        book.pages[pageIndex].image = value.image;
        book.pages[pageIndex].image_versions = value.image_versions;
        book.pages[pageIndex].generation_metadata = {
          generated_at: new Date().toISOString(),
          saved_via: 'supabase'
        };
      } else {
        book.pages[pageIndex][field] = value;

        if (field === 'image') {
          book.pages[pageIndex].generation_metadata = {
            generated_at: new Date().toISOString(),
            saved_via: 'supabase'
          };
        }
      }
    } else {
      return res.status(400).json({ error: `Invalid page index: ${pageIndex}` });
    }

    // Upsert to Supabase
    const upsertResponse = await fetch(
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
          slug: slug,
          data: book,
          updated_at: new Date().toISOString()
        })
      }
    );

    if (!upsertResponse.ok) {
      const error = await upsertResponse.text();
      throw new Error(`Save failed: ${error}`);
    }

    return res.status(200).json({
      success: true,
      message: `Saved ${field} to Supabase`
    });

  } catch (error) {
    console.error('Save error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
