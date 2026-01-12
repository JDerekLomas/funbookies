/**
 * Vercel Serverless Function: Update Book via GitHub API
 *
 * Updates book JSON files by committing directly to the GitHub repo.
 * This triggers a Vercel redeploy with the new content.
 */

const GITHUB_REPO = 'JDerekLomas/funbookies';
const GITHUB_BRANCH = 'main';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const githubToken = process.env.GITHUB_TOKEN;
  if (!githubToken) {
    return res.status(500).json({
      error: 'GitHub token not configured',
      help: 'Add GITHUB_TOKEN to Vercel environment variables'
    });
  }

  try {
    const { slug, pageIndex, field, value } = req.body;

    if (!slug || pageIndex === undefined || !field || value === undefined) {
      return res.status(400).json({
        error: 'Missing required fields: slug, pageIndex, field, value'
      });
    }

    const filePath = `public/books/${slug}.json`;

    // Get current file content and SHA
    const fileResponse = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/contents/${filePath}?ref=${GITHUB_BRANCH}`,
      {
        headers: {
          'Authorization': `Bearer ${githubToken}`,
          'Accept': 'application/vnd.github.v3+json'
        }
      }
    );

    if (!fileResponse.ok) {
      const error = await fileResponse.json();
      throw new Error(`Failed to get file: ${error.message}`);
    }

    const fileData = await fileResponse.json();
    const currentContent = Buffer.from(fileData.content, 'base64').toString('utf-8');
    const book = JSON.parse(currentContent);

    // Update the specified field
    if (pageIndex === -1) {
      // Book-level field (e.g., reference_prompt)
      book[field] = value;
    } else if (book.pages && book.pages[pageIndex]) {
      // Page-level field
      book.pages[pageIndex][field] = value;

      // If saving image, update generation metadata
      if (field === 'image') {
        book.pages[pageIndex].generation_metadata = {
          generated_at: new Date().toISOString(),
          model: 'wan2.6-image',
          used_reference: true,
          saved_via: 'web_ui'
        };
      }
    } else {
      return res.status(400).json({ error: `Invalid page index: ${pageIndex}` });
    }

    // Commit the updated file
    const newContent = JSON.stringify(book, null, 2);
    const commitMessage = `Update ${field} for ${slug} page ${pageIndex + 1} via web UI`;

    const updateResponse = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/contents/${filePath}`,
      {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${githubToken}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: commitMessage,
          content: Buffer.from(newContent).toString('base64'),
          sha: fileData.sha,
          branch: GITHUB_BRANCH
        })
      }
    );

    if (!updateResponse.ok) {
      const error = await updateResponse.json();
      throw new Error(`Failed to update file: ${error.message}`);
    }

    const updateResult = await updateResponse.json();

    return res.status(200).json({
      success: true,
      message: `Updated ${field} and committed to GitHub`,
      commitUrl: updateResult.commit?.html_url,
      note: 'Vercel will redeploy automatically in ~30 seconds'
    });

  } catch (error) {
    console.error('GitHub update error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Update failed'
    });
  }
}
