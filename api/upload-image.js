/**
 * Upload generated image to Vercel Blob Storage
 *
 * Downloads image from URL and uploads to Vercel Blob.
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
    const { imageUrl, slug, pageNum, version } = req.body;

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
    // Include version in filename if provided (e.g., page01_v2.png)
    const versionSuffix = version ? `_v${version}` : '';
    const fileName = `books/${slug}/page${pageNumStr}${versionSuffix}.png`;

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
      message: 'Image uploaded to Vercel Blob'
    });

  } catch (error) {
    console.error('Upload error:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
