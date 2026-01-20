/**
 * List all available books
 *
 * Returns array of book metadata for the wizard book selector.
 */

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // In production, this would fetch from Supabase or scan the filesystem
    // For now, return a static list based on known books

    // Fetch the books index from the static file
    const baseUrl = process.env.VERCEL_URL
      ? `https://${process.env.VERCEL_URL}`
      : 'http://localhost:3000';

    // Try to get list of books from filesystem via glob
    // Since we're on Vercel, we need to use a different approach
    // For now, hardcode some known books or return empty

    // Check if we have Supabase configured
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (supabaseUrl && supabaseKey) {
      // Fetch from Supabase
      const response = await fetch(
        `${supabaseUrl}/rest/v1/books?select=slug,title,level&order=title`,
        {
          headers: {
            'apikey': supabaseKey,
            'Authorization': `Bearer ${supabaseKey}`
          }
        }
      );

      if (response.ok) {
        const books = await response.json();
        return res.status(200).json(books);
      }
    }

    // Fallback: return known books from recent generation
    const knownBooks = [
      { slug: 'mud-pup-fun', title: 'Mud Pup Fun', level: 'B1' },
      { slug: 'pip-gets-a-hit', title: 'Pip Gets a Hit', level: 'B1' },
      { slug: 'pup-in-mud', title: 'Pup in Mud', level: 'B1' },
      { slug: 'the-big-pig', title: 'The Big Pig', level: 'B1' },
      { slug: 'sam-the-cat', title: 'Sam the Cat', level: 'B1' },
    ];

    return res.status(200).json(knownBooks);

  } catch (error) {
    console.error('List books error:', error);
    return res.status(500).json({
      error: error.message
    });
  }
}
