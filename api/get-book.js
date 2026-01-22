/**
 * Get book data - merges Supabase and static file for best result
 *
 * Strategy:
 * 1. Fetch from both Supabase and static file
 * 2. If only one exists, use that
 * 3. If both exist, merge: Supabase base + static file images/multiRefs
 *    (CLI scripts update static files, wizard updates Supabase)
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
    let supabaseBook = null;
    let staticBook = null;

    // Fetch from Supabase if configured
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
          supabaseBook = rows[0].data;
        }
      }
    }

    // Fetch from static file
    const staticUrl = `https://funbookies.com/books/${slug}.json`;
    const staticResponse = await fetch(staticUrl);

    if (staticResponse.ok) {
      staticBook = await staticResponse.json();
    }

    // Determine what to return
    if (!supabaseBook && !staticBook) {
      return res.status(404).json({ error: `Book not found: ${slug}` });
    }

    if (!supabaseBook) {
      // Only static exists
      return res.status(200).json({
        source: 'static',
        book: staticBook
      });
    }

    if (!staticBook) {
      // Only Supabase exists
      return res.status(200).json({
        source: 'supabase',
        book: supabaseBook
      });
    }

    // Both exist - merge them
    // Base: Supabase (has wizard state, user edits)
    // Overlay: static file images and multiRefs (CLI-generated)
    const mergedBook = mergeBooks(supabaseBook, staticBook);

    return res.status(200).json({
      source: 'merged',
      book: mergedBook
    });

  } catch (error) {
    console.error('Get book error:', error);
    return res.status(500).json({ error: error.message });
  }
}

/**
 * Merge Supabase book with static file content
 * Supabase is the base (wizard state), static provides CLI-generated content
 */
function mergeBooks(supabaseBook, staticBook) {
  const merged = { ...supabaseBook };

  // Merge multiRefs from static if Supabase lacks them
  if (staticBook.multiRefs && !supabaseBook.multiRefs) {
    merged.multiRefs = staticBook.multiRefs;
  }

  // Merge page images from static file
  if (staticBook.pages && merged.pages) {
    // If static has more pages, use static pages array as base
    if (staticBook.pages.length > merged.pages.length) {
      merged.pages = staticBook.pages.map((staticPage, i) => {
        const supabasePage = supabaseBook.pages[i];
        if (supabasePage) {
          // Merge: Supabase base + static image if Supabase lacks it
          return {
            ...staticPage,
            ...supabasePage,
            image: supabasePage.image || staticPage.image
          };
        }
        return staticPage;
      });
    } else {
      // Same or fewer pages in static - merge images into Supabase pages
      merged.pages = merged.pages.map((page, i) => {
        const staticPage = staticBook.pages[i];
        if (staticPage && staticPage.image && !page.image) {
          return { ...page, image: staticPage.image };
        }
        return page;
      });
    }
  }

  // Use static reference metadata if Supabase lacks it
  if (staticBook.multi_reference_metadata && !supabaseBook.multi_reference_metadata) {
    merged.multi_reference_metadata = staticBook.multi_reference_metadata;
  }

  if (staticBook.reference_metadata && !supabaseBook.reference_metadata) {
    merged.reference_metadata = staticBook.reference_metadata;
  }

  return merged;
}
