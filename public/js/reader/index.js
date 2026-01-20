// Reader Module Entry Point
// This file wires together all the modular components

import {
    currentBook, currentPage, setCurrentPage, bookSlug,
    isEditMode, isGalleryMode, updateUrl, setMode, updateModeButtons
} from './state.js';

import { loadBook } from './book-loader.js';
import { handleReferenceUpload } from './references.js';
import { loadPageVersions } from './page-versions.js';
import { regenerateImage, buildBatchPrompt, pollForImageResult } from './image-gen.js';
import { showGeneratedImage, useGeneratedImage, setImageAsCurrent, saveBatchImage } from './image-save.js';
import { saveTextToBook, savePromptToBook } from './text-editing.js';
import {
    renderPage, renderGallery, initEditMode, updateEditInfo,
    goToPage, goToPageEdit, markCardHasImage, markCardNoImage
} from './render.js';
import { prevPage, nextPage, setupKeyboardNavigation, setupTouchNavigation } from './navigation.js';
import {
    setRating, saveFeedback, loadFeedback, submitToGitHub,
    clearAllFeedback, showAllFeedback, closeFeedbackModal, copyFeedback
} from './feedback.js';
import { showBookComplete, closeCompleteOverlay } from './completion.js';

// Create bound functions that inject dependencies
// This avoids circular dependencies between modules

function boundRenderPage() {
    renderPage(boundSetImageAsCurrent);
}

function boundRenderGallery() {
    renderGallery(
        boundRegenerateImage,
        boundGoToPage,
        boundGoToPageEdit,
        boundGeneratePageFromGallery
    );
}

function boundSetMode(newMode) {
    setMode(newMode, {
        initEditMode,
        renderPage: boundRenderPage,
        renderGallery: boundRenderGallery
    });
}

function boundSetImageAsCurrent(blobUrl) {
    return setImageAsCurrent(blobUrl, boundRenderPage, boundLoadPageVersions);
}

function boundLoadPageVersions() {
    loadPageVersions(boundSetImageAsCurrent);
}

function boundShowGeneratedImage(url, slug, pageNum, metadata) {
    showGeneratedImage(url, slug, pageNum, metadata, boundRenderPage, boundLoadPageVersions);
}

function boundRegenerateImage() {
    regenerateImage(boundShowGeneratedImage);
}

function boundUseGeneratedImage() {
    useGeneratedImage(boundSetImageAsCurrent);
}

function boundPrevPage() {
    prevPage(boundRenderPage);
}

function boundNextPage() {
    nextPage(boundRenderPage, boundShowBookComplete);
}

function boundGoToPage(pageIndex) {
    goToPage(pageIndex, boundRenderPage);
}

function boundGoToPageEdit(pageIndex) {
    goToPageEdit(pageIndex, boundSetMode);
}

function boundGeneratePageFromGallery(pageIndex) {
    // Go to page in edit mode and trigger regeneration
    boundGoToPageEdit(pageIndex);
    // Small delay to let page render, then trigger generate
    setTimeout(() => boundRegenerateImage(), 300);
}

function boundShowBookComplete() {
    showBookComplete(boundRenderPage);
}

function boundCloseCompleteOverlay() {
    closeCompleteOverlay(setCurrentPage, boundRenderPage);
}

function boundSaveTextToBook() {
    saveTextToBook(boundRenderPage);
}

// Batch generation state
let batchGenerating = false;
let batchAborted = false;

async function generateAllMissing() {
    if (batchGenerating) {
        // Already running - abort
        batchAborted = true;
        return;
    }

    // Find all pages missing images
    const missingCards = document.querySelectorAll('.gallery-card.no-image');
    if (missingCards.length === 0) {
        alert('All pages already have images!');
        return;
    }

    // Get page indices from cards
    const missingIndices = Array.from(missingCards).map(card =>
        parseInt(card.dataset.page, 10)
    ).filter(idx => {
        // Only generate for pages that have scene descriptions
        const page = currentBook.pages[idx];
        return page && (page.scene || page.image_prompt);
    });

    if (missingIndices.length === 0) {
        alert('No pages with scene descriptions to generate. Add scene descriptions first.');
        return;
    }

    // Confirm with user
    const estimatedCost = (missingIndices.length * 0.03).toFixed(2);
    const proceed = confirm(
        `Generate ${missingIndices.length} missing images?\n\n` +
        `Estimated cost: ~$${estimatedCost} (using wan2.6-image)\n\n` +
        `This may take ${missingIndices.length * 30}-${missingIndices.length * 60} seconds.\n\n` +
        `Click OK to start, or Cancel to abort.`
    );
    if (!proceed) return;

    // Setup batch state
    batchGenerating = true;
    batchAborted = false;
    const btn = document.getElementById('generateAllBtn');
    const originalText = btn.textContent;
    btn.textContent = 'Stop Generation';
    btn.classList.remove('primary');
    btn.classList.add('danger');

    // Create progress display
    const statsEl = document.getElementById('galleryStats');
    const slug = currentBook._slug || bookSlug;

    // Determine reference to use
    let referenceData = null;
    let referenceIsUrl = false;

    // Try to find a reference image
    const refPath = `/books/references/${slug}_reference.png`;
    try {
        const refCheck = await fetch(refPath, { method: 'HEAD' });
        if (refCheck.ok) {
            referenceData = window.location.origin + refPath;
            referenceIsUrl = true;
        }
    } catch (e) {
        // No reference available
    }

    const model = referenceData ? 'wan2.6-image' : 'nano-banana-pro';
    let completed = 0;
    let failed = 0;

    // Generate each missing page
    for (const pageIndex of missingIndices) {
        if (batchAborted) {
            statsEl.innerHTML = `<span style="color: var(--color-terracotta);">Aborted after ${completed} images</span>`;
            break;
        }

        const page = currentBook.pages[pageIndex];
        const pageNum = page.page || (pageIndex + 1);
        const prompt = page.image_prompt || page.scene || '';

        if (!prompt) {
            failed++;
            continue;
        }

        // Update progress
        statsEl.innerHTML = `
            <span>Generating ${completed + 1}/${missingIndices.length}...</span>
            <span style="color: var(--color-sage);">${completed} done</span>
            ${failed > 0 ? `<span style="color: var(--color-terracotta);">${failed} failed</span>` : ''}
        `;

        // Highlight current card
        const cardId = `gallery-card-${pageIndex}`;
        const card = document.getElementById(cardId);
        if (card) card.style.outline = '3px solid var(--color-sage)';

        try {
            // Build enhanced prompt with composition instructions
            const enhancedPrompt = buildBatchPrompt(prompt, currentBook);

            // Call API
            const response = await fetch('/api/generate-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: enhancedPrompt,
                    model,
                    slug,
                    page: pageNum,
                    reference: referenceData,
                    referenceIsUrl
                })
            });

            const result = await response.json();

            if (result.success && result.pending) {
                // Poll for async result
                const imageUrl = await pollForImageResult(result.taskId, result.statusEndpoint);
                await saveBatchImage(imageUrl, slug, pageNum, pageIndex);
                completed++;
                markCardHasImage(cardId);
            } else if (result.success && result.url) {
                await saveBatchImage(result.url, slug, pageNum, pageIndex);
                completed++;
                markCardHasImage(cardId);
            } else {
                console.error(`Failed page ${pageNum}:`, result.error);
                failed++;
            }
        } catch (error) {
            console.error(`Error generating page ${pageNum}:`, error);
            failed++;
        } finally {
            // Remove highlight
            if (card) card.style.outline = '';
        }

        // Small delay between requests
        await new Promise(r => setTimeout(r, 1000));
    }

    // Restore UI
    batchGenerating = false;
    btn.textContent = originalText;
    btn.classList.remove('danger');
    btn.classList.add('primary');

    // Final status
    if (!batchAborted) {
        statsEl.innerHTML = `
            <span style="color: var(--color-sage);">✓ Generated ${completed} images</span>
            ${failed > 0 ? `<span style="color: var(--color-terracotta);">${failed} failed</span>` : ''}
        `;

        // Restore normal stats after a delay
        setTimeout(() => {
            if (!batchGenerating) {
                const hasImage = document.querySelectorAll('.gallery-card.has-image').length;
                const noImage = document.querySelectorAll('.gallery-card.no-image').length;
                statsEl.innerHTML = `
                    <span class="has-image">${hasImage} with images</span>
                    <span class="no-image">${noImage} need images</span>
                `;
            }
        }, 5000);
    }
}

// Expose functions to window for onclick handlers in HTML
// These are used by gallery cards (dynamically created)
window._goToPage = boundGoToPage;
window._goToPageEdit = boundGoToPageEdit;
window._generatePageFromGallery = boundGeneratePageFromGallery;
window._markCardHasImage = markCardHasImage;
window._markCardNoImage = markCardNoImage;
window._useGeneratedImage = boundUseGeneratedImage;

// These are used by static HTML onclick attributes
window.setMode = boundSetMode;
window.prevPage = boundPrevPage;
window.nextPage = boundNextPage;
window.saveTextToBook = boundSaveTextToBook;
window.regenerateImage = boundRegenerateImage;
window.savePromptToBook = savePromptToBook;
window.handleReferenceUpload = handleReferenceUpload;
window.setRating = setRating;
window.saveFeedback = saveFeedback;
window.showAllFeedback = showAllFeedback;
window.clearAllFeedback = clearAllFeedback;
window.closeFeedbackModal = closeFeedbackModal;
window.copyFeedback = copyFeedback;
window.generateAllMissing = generateAllMissing;
window.closeCompleteOverlay = boundCloseCompleteOverlay;

// Wire up event handlers for buttons
function setupEventHandlers() {
    // Navigation buttons
    document.getElementById('prevBtn')?.addEventListener('click', boundPrevPage);
    document.getElementById('nextBtn')?.addEventListener('click', boundNextPage);

    // Mode buttons
    document.getElementById('readModeBtn')?.addEventListener('click', () => boundSetMode('read'));
    document.getElementById('editModeBtn')?.addEventListener('click', () => boundSetMode('edit'));
    document.getElementById('galleryModeBtn')?.addEventListener('click', () => boundSetMode('gallery'));

    // Edit mode buttons
    document.getElementById('regenerateBtn')?.addEventListener('click', boundRegenerateImage);
    document.getElementById('savePromptBtn')?.addEventListener('click', savePromptToBook);
    document.getElementById('saveTextBtn')?.addEventListener('click', boundSaveTextToBook);

    // Reference upload
    document.getElementById('uploadReferenceInput')?.addEventListener('change', handleReferenceUpload);

    // Feedback buttons
    document.getElementById('thumbsUp')?.addEventListener('click', () => setRating('up'));
    document.getElementById('thumbsDown')?.addEventListener('click', () => setRating('down'));
    document.getElementById('saveFeedbackBtn')?.addEventListener('click', saveFeedback);
    document.getElementById('submitGitHubBtn')?.addEventListener('click', submitToGitHub);
    document.getElementById('clearFeedbackBtn')?.addEventListener('click', clearAllFeedback);
    document.getElementById('showAllFeedbackBtn')?.addEventListener('click', showAllFeedback);
    document.getElementById('closeFeedbackModalBtn')?.addEventListener('click', closeFeedbackModal);
    document.getElementById('copyFeedbackBtn')?.addEventListener('click', copyFeedback);

    // Gallery buttons
    document.getElementById('generateAllBtn')?.addEventListener('click', generateAllMissing);

    // Completion overlay
    document.getElementById('closeCompleteBtn')?.addEventListener('click', boundCloseCompleteOverlay);

    // Setup keyboard and touch navigation
    setupKeyboardNavigation(boundPrevPage, boundNextPage);
    setupTouchNavigation(boundPrevPage, boundNextPage);
}

// Initialize the reader
function init() {
    setupEventHandlers();
    loadBook({
        initEditMode,
        renderPage: boundRenderPage,
        renderGallery: boundRenderGallery,
        regenerateImage: boundRegenerateImage
    });
}

// Start on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
