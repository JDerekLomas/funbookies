import { currentBook, bookSlug, currentPage } from './state.js';
import { getSelectedReference, getSelectedReferences, getUploadedReferenceData } from './references.js';
import { getNextVersionNumber } from './page-versions.js';

// Compress image data URL to reduce payload size for uploads
export function compressImageDataUrl(dataUrl, maxSize = 512, quality = 0.8) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            let width = img.width;
            let height = img.height;

            // Scale down if larger than maxSize
            if (width > maxSize || height > maxSize) {
                if (width > height) {
                    height = Math.round(height * maxSize / width);
                    width = maxSize;
                } else {
                    width = Math.round(width * maxSize / height);
                    height = maxSize;
                }
            }

            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);
            resolve(canvas.toDataURL('image/jpeg', quality));
        };
        img.onerror = reject;
        img.src = dataUrl;
    });
}

export function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

export async function pollForImageResult(taskId, statusEndpoint, maxAttempts = 40) {
    const status = document.getElementById('generationStatus');

    for (let i = 0; i < maxAttempts; i++) {
        await new Promise(r => setTimeout(r, 3000)); // Wait 3 seconds

        status.textContent = `Polling for result... (${i + 1}/${maxAttempts})`;

        const response = await fetch(`/api/check-status?taskId=${taskId}&endpoint=${encodeURIComponent(statusEndpoint)}`);
        const result = await response.json();

        if (result.completed && result.url) {
            return result.url;
        }

        if (!result.success && result.error) {
            const errMsg = typeof result.error === 'object' ? JSON.stringify(result.error) : result.error;
            throw new Error(errMsg);
        }

        // Still pending, continue polling
    }

    throw new Error('Timeout waiting for image generation');
}

export async function regenerateImage(showGeneratedImage) {
    const status = document.getElementById('generationStatus');
    const btn = document.getElementById('regenerateBtn');

    // Can't regenerate on Creation Notes page (story_bible editing)
    if (currentPage === -2) {
        status.className = 'generation-status error';
        status.textContent = 'Navigate to a page or reference sheet to generate images';
        return;
    }

    const prompt = document.getElementById('promptEditor').value;
    const model = document.getElementById('modelSelect').value;

    if (!prompt) {
        status.className = 'generation-status error';
        status.textContent = 'Please enter a prompt';
        return;
    }

    // Show loading
    status.className = 'generation-status loading';
    status.textContent = 'Generating image... This may take 30-60 seconds.';
    btn.disabled = true;

    try {
        const slug = currentBook?._slug || bookSlug;
        const pageNum = currentPage === -1 ? 'reference' : currentPage;

        // Prepare reference images - use URLs for hosted images, base64 only for uploads
        // Models that use reference images for style transfer
        const modelsWithReference = ['gemini-3-pro', 'gemini-flash', 'wan2.6-image', 'wan2.5-i2i'];
        let referenceData = null;
        let referenceIsUrl = false;
        const selectedReferences = getSelectedReferences();
        const selectedReference = getSelectedReference();
        const uploadedReferenceData = getUploadedReferenceData();

        if (modelsWithReference.includes(model)) {
            if (uploadedReferenceData) {
                // Custom upload - compress and send as base64
                referenceData = await compressImageDataUrl(uploadedReferenceData, 512, 0.8);
            } else if (selectedReferences.length > 0) {
                // Multiple hosted references - send as array of full URLs
                referenceData = selectedReferences.map(ref => window.location.origin + ref);
                referenceIsUrl = true;
            } else if (selectedReference) {
                // Single hosted reference (legacy fallback)
                referenceData = window.location.origin + selectedReference;
                referenceIsUrl = true;
            }
        }

        // Call API
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt,
                model,
                slug,
                page: pageNum,
                reference: referenceData,
                referenceIsUrl: referenceIsUrl
            })
        });

        // Handle non-JSON or empty responses
        let result;
        try {
            const text = await response.text();
            if (!text) {
                throw new Error(`Empty response from server (status ${response.status})`);
            }
            result = JSON.parse(text);
        } catch (parseError) {
            throw new Error(`Server error (${response.status}): ${parseError.message}`);
        }

        if (!response.ok) {
            const errMsg = typeof result.error === 'object' ? JSON.stringify(result.error) : result.error;
            throw new Error(errMsg || `Server error: ${response.status}`);
        }

        // Build metadata for this generation
        const generationMetadata = {
            prompt,
            model,
            reference: selectedReference || (uploadedReferenceData ? 'custom_upload' : null)
        };

        if (result.success && result.pending) {
            // Poll for result
            status.textContent = 'Generation started. Polling for result...';
            const imageUrl = await pollForImageResult(result.taskId, result.statusEndpoint);
            showGeneratedImage(imageUrl, slug, pageNum, generationMetadata);
        } else if (result.success && result.url) {
            showGeneratedImage(result.url, slug, pageNum, generationMetadata);
        } else {
            const errMsg = typeof result.error === 'object' ? JSON.stringify(result.error) : result.error;
            throw new Error(errMsg || 'Generation failed');
        }
    } catch (error) {
        status.className = 'generation-status error';
        const errText = error.message || (typeof error === 'object' ? JSON.stringify(error) : String(error));
        status.textContent = `Error: ${errText}`;
    } finally {
        btn.disabled = false;
    }
}

// Build enhanced prompt for batch generation
export function buildBatchPrompt(scene, book) {
    // Add composition instructions to prevent grid output
    const prefix = 'Single scene illustration: ';
    const suffix = `

COMPOSITION: One cohesive illustration filling the entire canvas.
Full-bleed image with the scene filling edge to edge.

CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere in the image. Pure illustration only.`;

    // Check if scene already has these instructions
    if (scene.includes('Single scene') || scene.includes('COMPOSITION:')) {
        return scene;
    }

    return prefix + scene + suffix;
}
