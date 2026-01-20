/**
 * Save generated reference sheet to Vercel Blob Storage
 *
 * Downloads image from URL and uploads to Vercel Blob in the multi-ref format.
 * Returns permanent Blob URL.
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const blobToken = process.env.BLOB_READ_WRITE_TOKEN;

  if (!blobToken) {
    return res.status(500).json({ error: 'Vercel Blob not configured. Add BLOB_READ_WRITE_TOKEN.' });
  }

  try {
    const { imageUrl, slug, sheetType } = req.body;

    if (!imageUrl || !slug || !sheetType) {
      return res.status(400).json({
        error: 'Missing required fields: imageUrl, slug, sheetType'
      });
    }

    // Validate sheet type
    const validTypes = ['characters', 'settings', 'style'];
    if (!validTypes.includes(sheetType)) {
      return res.status(400).json({
        error: `Invalid sheetType. Must be one of: ${validTypes.join(', ')}`
      });
    }

    // Download image from generation URL
    const imageResponse = await fetch(imageUrl);
    if (!imageResponse.ok) {
      throw new Error(`Failed to download image: ${imageResponse.status}`);
    }

    const imageBuffer = await imageResponse.arrayBuffer();

    // Save to multi-ref format: books/references/{slug}_multi/{slug}_{sheetType}.png
    const fileName = `books/references/${slug}_multi/${slug}_${sheetType}.png`;

    // Upload to Vercel Blob using REST API
    const uploadResponse = await fetch(
      `https://blob.vercel-storage.com/${fileName}`,
      {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${blobToken}`,
          'Content-Type': 'image/png',
          'x-api-version': '7',
          'x-content-type': 'image/png'
        },
        body: imageBuffer
      }
    );

    if (!uploadResponse.ok) {
      const error = await uploadResponse.text();
      throw new Error(`Upload failed: ${error}`);
    }

    const result = await uploadResponse.json();

    return res.status(200).json({
      success: true,
      url: result.url,
      path: `/books/references/${slug}_multi/${slug}_${sheetType}.png`,
      message: `${sheetType} reference saved to Vercel Blob`
    });

  } catch (error) {
    console.error('Save reference error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
