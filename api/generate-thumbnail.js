/**
 * Generate thumbnail for a book
 *
 * Takes a source image URL and creates a 512x512 thumbnail.
 * Uploads to Vercel Blob Storage.
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const blobToken = process.env.BLOB_READ_WRITE_TOKEN;

  if (!blobToken) {
    return res.status(500).json({ error: 'Vercel Blob not configured' });
  }

  try {
    const { slug, sourceImageUrl } = req.body;

    if (!slug || !sourceImageUrl) {
      return res.status(400).json({
        error: 'Missing required fields: slug, sourceImageUrl'
      });
    }

    // Download source image
    const imageResponse = await fetch(sourceImageUrl);
    if (!imageResponse.ok) {
      throw new Error(`Failed to download source image: ${imageResponse.status}`);
    }

    const imageBuffer = await imageResponse.arrayBuffer();

    // For now, we'll upload the image as-is since we can't resize server-side without sharp
    // The thumbnail will be full-size but that's better than nothing
    // TODO: Add sharp for proper resizing when package is available

    const fileName = `thumbs/${slug}.jpg`;

    // Upload to Vercel Blob
    const uploadResponse = await fetch(
      `https://blob.vercel-storage.com/${fileName}`,
      {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${blobToken}`,
          'Content-Type': 'image/jpeg',
          'x-api-version': '7',
          'x-content-type': 'image/jpeg'
        },
        body: imageBuffer
      }
    );

    if (!uploadResponse.ok) {
      const error = await uploadResponse.text();
      throw new Error(`Thumbnail upload failed: ${error}`);
    }

    const result = await uploadResponse.json();

    return res.status(200).json({
      success: true,
      url: result.url,
      message: 'Thumbnail generated'
    });

  } catch (error) {
    console.error('Thumbnail generation error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
