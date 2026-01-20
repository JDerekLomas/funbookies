import { currentBook, bookSlug, currentPage } from './state.js';
import { getNextVersionNumber } from './page-versions.js';

// State for last generated image
let lastGeneratedUrl = null;
let lastGeneratedBlobUrl = null;
let lastGenerationMetadata = null;

export function getLastGeneratedBlobUrl() { return lastGeneratedBlobUrl; }

export async function showGeneratedImage(url, slug, pageNum, generationMetadata, renderPage, loadPageVersions) {
    const status = document.getElementById('generationStatus');
    const filename = `${slug}_page_${pageNum}.png`;
    lastGeneratedUrl = url;

    // Immediately download from MuleRouter and save to Vercel Blob
    // This avoids hotlinking and ensures we own the image
    status.className = 'generation-status';
    status.textContent = 'Downloading image to storage...';

    try {
        const versionNum = getNextVersionNumber();
        const actualPageNum = currentPage >= 0 ? (currentBook.pages[currentPage]?.page || currentPage + 1) : pageNum;

        const uploadResponse = await fetch('/api/upload-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                imageUrl: url,
                slug,
                pageNum: actualPageNum,
                version: versionNum
            })
        });

        const uploadResult = await uploadResponse.json();

        if (!uploadResult.success) {
            throw new Error(uploadResult.error || 'Upload failed');
        }

        lastGeneratedBlobUrl = uploadResult.url;

        // Store version metadata for later persistence
        lastGenerationMetadata = {
            url: lastGeneratedBlobUrl,
            version: versionNum,
            created_at: new Date().toISOString(),
            prompt: generationMetadata.prompt || '',
            model: generationMetadata.model || '',
            reference_used: generationMetadata.reference || null
        };

        status.className = 'generation-status success';
        status.innerHTML = `
            Image generated and saved (v${versionNum})!<br>
            <a href="${lastGeneratedBlobUrl}" target="_blank" style="color: inherit; text-decoration: underline;">View full size</a> |
            <a href="${lastGeneratedBlobUrl}" download="${filename}" style="color: inherit; text-decoration: underline;">Download</a>
            <div style="margin-top: 8px;">
                <img src="${lastGeneratedBlobUrl}" style="max-width: 200px; border-radius: 4px; cursor: pointer;" onclick="window.open('${lastGeneratedBlobUrl}', '_blank')">
            </div>
            <button onclick="window._useGeneratedImage()" style="margin-top: 8px; padding: 6px 12px; background: var(--color-sage); color: white; border: none; border-radius: 4px; cursor: pointer;">
                Use as Current Image
            </button>
        `;

        // Store metadata locally (will be added to version history when set as current)
        // We don't auto-save generations - only images that are actually used get saved

    } catch (error) {
        status.className = 'generation-status error';
        status.textContent = `Upload failed: ${error.message}`;
        // Fall back to showing MuleRouter URL if upload fails
        lastGeneratedBlobUrl = null;
    }
}

export async function useGeneratedImage(setImageAsCurrent) {
    console.log('useGeneratedImage called, lastGeneratedBlobUrl:', lastGeneratedBlobUrl);
    const status = document.getElementById('generationStatus');

    if (!lastGeneratedBlobUrl) {
        status.className = 'generation-status error';
        status.textContent = 'No saved image to use';
        return;
    }

    status.className = 'generation-status loading';
    status.textContent = 'Setting as current image...';

    await setImageAsCurrent(lastGeneratedBlobUrl);
}

export async function setImageAsCurrent(blobUrl, renderPage, loadPageVersions) {
    const status = document.getElementById('generationStatus');
    const slug = currentBook?._slug || bookSlug;
    const pageNum = currentPage;
    const page = currentBook?.pages[pageNum];

    console.log('setImageAsCurrent called:', { blobUrl, slug, pageNum, page: !!page });

    if (!page || pageNum < 0) {
        status.className = 'generation-status error';
        status.textContent = 'Cannot set image for this page type';
        console.error('Invalid page for setImageAsCurrent:', { pageNum, page });
        return;
    }

    status.className = 'generation-status loading';
    status.textContent = 'Saving to Supabase...';

    try {
        // Initialize versions array if needed
        if (!page.image_versions) page.image_versions = [];

        // Archive the OLD current image to version history (if it exists and isn't already in versions)
        const oldImage = page.image;
        if (oldImage && oldImage !== blobUrl) {
            const alreadyInVersions = page.image_versions.some(v => v.url === oldImage);
            if (!alreadyInVersions) {
                // Add old current image to version history with metadata
                const versionNum = page.image_versions.length + 1;
                page.image_versions.push({
                    url: oldImage,
                    version: versionNum,
                    created_at: new Date().toISOString(),
                    prompt: page.image_prompt || '',
                    model: 'unknown (previous)',
                    note: 'Archived when replaced'
                });
            }
        }

        // Add the NEW image to version history with its metadata
        const newVersionNum = page.image_versions.length + 1;
        const newVersionData = lastGenerationMetadata || {
            url: blobUrl,
            version: newVersionNum,
            created_at: new Date().toISOString(),
            prompt: document.getElementById('promptEditor')?.value || '',
            model: document.getElementById('modelSelect')?.value || 'unknown'
        };
        // Ensure URL is set correctly
        newVersionData.url = blobUrl;
        newVersionData.version = newVersionNum;

        // Only add if not already in versions
        if (!page.image_versions.some(v => v.url === blobUrl)) {
            page.image_versions.push(newVersionData);
        }

        const payload = {
            slug,
            pageIndex: pageNum,
            field: 'image_with_versions',
            value: {
                image: blobUrl,
                image_versions: page.image_versions
            }
        };
        console.log('Sending to /api/save-book:', payload);

        const response = await fetch('/api/save-book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        console.log('Response status:', response.status);
        const result = await response.json();
        console.log('Response body:', result);

        if (result.success) {
            page.image = blobUrl;
            status.className = 'generation-status success';
            status.textContent = 'Image saved and set as current!';
            renderPage();
            loadPageVersions();
        } else {
            throw new Error(result.error || 'Failed to update');
        }
    } catch (error) {
        console.error('setImageAsCurrent error:', error);
        status.className = 'generation-status error';
        status.textContent = `Error: ${error.message}`;
    }
}

// Save batch-generated image
export async function saveBatchImage(url, slug, pageNum, pageIndex) {
    // Upload to Vercel Blob storage
    try {
        const uploadResponse = await fetch('/api/upload-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                imageUrl: url,
                slug,
                pageNum,
                version: 1  // First version for batch-generated images
            })
        });

        const uploadResult = await uploadResponse.json();

        if (uploadResult.success) {
            // Update the book data
            currentBook.pages[pageIndex].image = uploadResult.url;

            // Update the gallery card image
            const cardImg = document.querySelector(`#gallery-card-${pageIndex} img`);
            if (cardImg) {
                cardImg.src = uploadResult.url;
            }
        }
    } catch (e) {
        console.error('Failed to save image:', e);
    }
}
