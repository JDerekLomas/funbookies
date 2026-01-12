/**
 * Vercel Serverless Function: Save Book Changes
 *
 * Saves prompt or image path changes to book JSON.
 * Works locally; production would need GitHub API.
 */

import fs from 'fs/promises';
import path from 'path';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { slug, pageIndex, field, value } = req.body;

    if (!slug || pageIndex === undefined || !field) {
      return res.status(400).json({
        error: 'Missing required fields: slug, pageIndex, field'
      });
    }

    // In production (Vercel), filesystem is read-only
    // Check if we're in a writable environment
    const isWritable = process.env.NODE_ENV !== 'production' ||
                       process.env.ALLOW_FILE_WRITES === 'true';

    if (!isWritable) {
      return res.status(200).json({
        success: false,
        readonly: true,
        message: 'Production environment is read-only. Download JSON to save changes.',
        field,
        value
      });
    }

    // Construct path to book JSON
    const bookPath = path.join(process.cwd(), 'public', 'books', `${slug}.json`);

    // Read current book
    const bookContent = await fs.readFile(bookPath, 'utf-8');
    const book = JSON.parse(bookContent);

    // Update the specified field
    if (pageIndex === -1) {
      // Reference prompt (book-level)
      if (field === 'reference_prompt') {
        book.reference_prompt = value;
      }
    } else if (book.pages && book.pages[pageIndex]) {
      // Page-level field
      book.pages[pageIndex][field] = value;

      // If saving image, also update generation_metadata
      if (field === 'image') {
        book.pages[pageIndex].generation_metadata = {
          generated_at: new Date().toISOString(),
          model: 'wan2.6-image',
          used_reference: true,
          regenerated_via_ui: true
        };
      }
    } else {
      return res.status(400).json({
        error: `Invalid page index: ${pageIndex}`
      });
    }

    // Write updated book
    await fs.writeFile(bookPath, JSON.stringify(book, null, 2));

    return res.status(200).json({
      success: true,
      message: `Saved ${field} for page ${pageIndex + 1}`
    });

  } catch (error) {
    console.error('Save error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Save failed'
    });
  }
}
