/**
 * Upload generated image to Supabase Storage
 *
 * Downloads image from URL and uploads to Supabase Storage bucket.
 * Returns permanent Supabase URL.
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
    const { imageUrl, slug, pageNum } = req.body;

    if (!imageUrl || !slug || pageNum === undefined) {
      return res.status(400).json({
        error: 'Missing required fields: imageUrl, slug, pageNum'
      });
    }

    // Download image from MuleRouter URL
    const imageResponse = await fetch(imageUrl);
    if (!imageResponse.ok) {
      throw new Error(`Failed to download image: ${imageResponse.status}`);
    }

    const imageBuffer = await imageResponse.arrayBuffer();
    const pageNumStr = String(pageNum).padStart(2, '0');
    const fileName = `${slug}/page${pageNumStr}.png`;

    // Upload to Supabase Storage
    const uploadResponse = await fetch(
      `${supabaseUrl}/storage/v1/object/book-images/${fileName}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${supabaseKey}`,
          'Content-Type': 'image/png',
          'x-upsert': 'true'  // Overwrite if exists
        },
        body: imageBuffer
      }
    );

    if (!uploadResponse.ok) {
      const error = await uploadResponse.text();
      throw new Error(`Upload failed: ${error}`);
    }

    // Return public URL
    const publicUrl = `${supabaseUrl}/storage/v1/object/public/book-images/${fileName}`;

    return res.status(200).json({
      success: true,
      url: publicUrl,
      message: 'Image uploaded to Supabase'
    });

  } catch (error) {
    console.error('Upload error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
