/**
 * Vercel Serverless Function: Download and Save Image
 *
 * Downloads an image from URL and saves to public/books/images/{slug}/
 * Works locally; production is read-only.
 */

import fs from 'fs/promises';
import path from 'path';
import https from 'https';
import http from 'http';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { imageUrl, slug, pageNum } = req.body;

    if (!imageUrl || !slug || pageNum === undefined) {
      return res.status(400).json({
        error: 'Missing required fields: imageUrl, slug, pageNum'
      });
    }

    // Check if we're in a writable environment
    const isWritable = process.env.NODE_ENV !== 'production' ||
                       process.env.ALLOW_FILE_WRITES === 'true';

    if (!isWritable) {
      return res.status(200).json({
        success: false,
        readonly: true,
        message: 'Production is read-only. Download image manually.',
        imageUrl
      });
    }

    // Construct output path
    const pageNumStr = String(pageNum).padStart(2, '0');
    const imageDir = path.join(process.cwd(), 'public', 'books', 'images', slug);
    const imagePath = path.join(imageDir, `page${pageNumStr}.png`);

    // Ensure directory exists
    await fs.mkdir(imageDir, { recursive: true });

    // Download image
    const imageBuffer = await downloadImage(imageUrl);

    // Save image
    await fs.writeFile(imagePath, imageBuffer);

    // Return the relative path for the book JSON
    const relativePath = `images/${slug}/page${pageNumStr}.png`;

    return res.status(200).json({
      success: true,
      message: `Image saved to ${relativePath}`,
      imagePath: relativePath
    });

  } catch (error) {
    console.error('Save image error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Save failed'
    });
  }
}

function downloadImage(url) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;

    protocol.get(url, (response) => {
      // Handle redirects
      if (response.statusCode === 301 || response.statusCode === 302) {
        downloadImage(response.headers.location).then(resolve).catch(reject);
        return;
      }

      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }

      const chunks = [];
      response.on('data', chunk => chunks.push(chunk));
      response.on('end', () => resolve(Buffer.concat(chunks)));
      response.on('error', reject);
    }).on('error', reject);
  });
}
