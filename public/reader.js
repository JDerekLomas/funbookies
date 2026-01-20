let currentBook = null;
let currentPage = 0;
let bookSlug = '';

// Single mode state: 'read' | 'edit' | 'gallery'
let currentMode = 'read';

// Get URL params
const urlParams = new URLSearchParams(window.location.search);
const bookId = urlParams.get('book');
const modeParam = urlParams.get('mode');
const pageParam = urlParams.get('page');
const actionParam = urlParams.get('action');

// Legacy support: convert old view=gallery to mode=gallery
const viewParam = urlParams.get('view');
if (viewParam === 'gallery') {
    currentMode = 'gallery';
} else if (modeParam === 'edit') {
    currentMode = 'edit';
} else if (modeParam === 'gallery') {
    currentMode = 'gallery';
} else {
    currentMode = 'read';
}

// Helper getters for backwards compatibility
function isEditMode() { return currentMode === 'edit'; }
function isGalleryMode() { return currentMode === 'gallery'; }
function isReadMode() { return currentMode === 'read'; }

// Unified URL update helper - keeps URL in sync with state
function updateUrl(options = {}) {
    const url = new URL(window.location);
    const slug = currentBook?._slug || bookSlug;

    // Always set book
    if (slug) url.searchParams.set('book', slug);

    // Mode (read is default, so omit from URL)
    if (currentMode === 'read') {
        url.searchParams.delete('mode');
    } else {
        url.searchParams.set('mode', currentMode);
    }

    // Page (skip for default pages)
    const defaultPage = currentMode === 'edit' ? -2 : 0;
    if (currentPage !== defaultPage || options.forcePage) {
        url.searchParams.set('page', currentPage);
    } else {
        url.searchParams.delete('page');
    }

    // Clear legacy view param
    url.searchParams.delete('view');

    // Clear action param after it's been processed
    url.searchParams.delete('action');

    history.replaceState({}, '', url);
}

// Set mode (read, edit, or gallery)
function setMode(newMode) {
    if (currentMode === newMode) return;

    const oldMode = currentMode;
    currentMode = newMode;

    // Update body classes
    document.body.classList.remove('mode-read', 'mode-edit', 'mode-gallery');
    document.body.classList.add(`mode-${currentMode}`);

    // Legacy class support
    document.body.classList.toggle('edit-mode', currentMode === 'edit');
    document.body.classList.toggle('gallery-mode', currentMode === 'gallery');

    // Update page title
    if (currentBook) {
        const suffix = currentMode === 'edit' ? ' (Edit)' : currentMode === 'gallery' ? ' (Gallery)' : '';
        document.title = `${currentBook.title} - FunBookies${suffix}`;
    }

    // Update mode buttons
    updateModeButtons();

    // Re-initialize edit mode UI if entering edit mode
    if (currentMode === 'edit') {
        initEditMode();
    }

    // Render appropriate view
    if (currentMode === 'gallery') {
        renderGallery();
    } else {
        renderPage();
    }

    updateUrl();
}

// Update mode button states
function updateModeButtons() {
    const readBtn = document.getElementById('readModeBtn');
    const editBtn = document.getElementById('editModeBtn');
    const galleryBtn = document.getElementById('galleryModeBtn');

    if (readBtn) readBtn.classList.toggle('active', currentMode === 'read');
    if (editBtn) editBtn.classList.toggle('active', currentMode === 'edit');
    if (galleryBtn) galleryBtn.classList.toggle('active', currentMode === 'gallery');

}

// Apply initial mode classes
document.body.classList.add(`mode-${currentMode}`);
if (currentMode === 'edit') {
    document.body.classList.add('edit-mode');
} else if (currentMode === 'gallery') {
    document.body.classList.add('gallery-mode');
}

// Legacy book registry for old books with custom image paths
const legacyImagePaths = {
    'dog_pink': { imageFolder: 'images', imagePrefix: 'dog_pink_page' },
    'pig_yellow': { imageFolder: 'images', imagePrefix: 'pig_yellow_page' },
    'volcano': { imageFolder: 'volcano_images', imagePrefix: 'page_' },
    'castle': { imageFolder: 'castle_images', imagePrefix: 'page_' },
    'elephant_red': { imageFolder: 'images', imagePrefix: 'elephant_red_page' },
    'fox_purple': { imageFolder: 'images', imagePrefix: 'fox_purple_page' },
    'snail_blue': { imageFolder: 'images', imagePrefix: 'snail_blue_page' },
    'owl_green': { imageFolder: 'images', imagePrefix: 'owl_green_page' },
    'mouse_gold': { imageFolder: 'images', imagePrefix: 'mouse_gold_page' },
    'puppy_silver': { imageFolder: 'images', imagePrefix: 'puppy_silver_page' }
};

async function loadBook() {
    if (!bookId) {
        document.getElementById('bookPage').innerHTML = `
            <div class="loading">No book specified. <a href="/books/" style="color: var(--color-sage);">Browse books</a></div>
        `;
        return;
    }

    bookSlug = bookId;

    try {
        // Try API first, then fall back to static JSON file
        let res = await fetch(`/api/get-book?slug=${bookId}`);
        let source = 'api';

        if (!res.ok) {
            // Fallback to static JSON file (for local dev without API)
            res = await fetch(`/books/${bookId}.json`);
            source = 'static';
            if (!res.ok) throw new Error('Failed to load book');
            currentBook = await res.json();
        } else {
            const data = await res.json();
            currentBook = data.book;
        }
        console.log(`Book loaded from ${source}`);
        currentBook._slug = bookId;
        // Use page from URL param, or default (edit mode: -2, otherwise: 0)
        if (pageParam !== null) {
            currentPage = parseInt(pageParam, 10);
        } else {
            currentPage = isEditMode() ? -2 : 0;
        }

        document.getElementById('bookTitle').textContent = currentBook.title;
        const modeSuffix = currentMode === 'edit' ? ' (Edit)' : currentMode === 'gallery' ? ' (Gallery)' : '';
        document.title = `${currentBook.title} - FunBookies${modeSuffix}`;

        // Initialize edit mode UI
        initEditMode();

        // Update mode buttons
        updateModeButtons();

        // Render appropriate view based on mode
        if (isGalleryMode()) {
            renderGallery();
        } else {
            renderPage();
        }

        // Handle action param (e.g., action=generate triggers image regeneration)
        if (actionParam === 'generate' && isEditMode()) {
            // Switch to edit mode if in gallery
            if (isGalleryMode()) {
                setMode('edit');
            }
            // Clear action from URL to prevent re-triggering on refresh
            updateUrl();
            // Small delay to let page render, then trigger generate
            setTimeout(() => regenerateImage(), 500);
        }
    } catch (e) {
        console.error('Error loading book:', e);
        document.getElementById('bookPage').innerHTML = `
            <div class="loading">Book not found. <a href="/books/" style="color: var(--color-sage);">Browse books</a></div>
        `;
    }
}

function getCoverImagePath() {
    const slug = currentBook._slug || bookSlug;
    return `/images/covers/${slug}.png`;
}

function getReferenceImagePath() {
    const slug = currentBook._slug || bookSlug;
    return `/books/references/${slug}_reference.png`;
}

function initEditMode() {
    const slug = currentBook?._slug || bookSlug;

    // Set initial edit info
    if (isEditMode() && currentBook) {
        document.getElementById('infoSlug').textContent = slug;
        document.getElementById('infoLevel').textContent = currentBook.level || 'N/A';
    }
}

function updateEditInfo() {
    if (!isEditMode() || !currentBook) return;

    let currentPrompt = '';
    let currentText = '';
    let showTextEditor = false;

    // Handle creation notes page (page -2)
    if (currentPage === -2) {
        document.getElementById('infoPage').textContent = `Creation Notes / ${currentBook.pages.length}`;
        // Show story_bible as JSON for editing
        const storyBible = currentBook.story_bible || {};
        currentPrompt = Object.keys(storyBible).length > 0
            ? JSON.stringify(storyBible, null, 2)
            : 'No story bible. Add a story_bible object with: premise, themes, character_arcs, setting, emotional_beats, level_adaptation';
    }
    // Handle reference page (page -1)
    else if (currentPage === -1) {
        document.getElementById('infoPage').textContent = `Reference / ${currentBook.pages.length}`;
        currentPrompt = currentBook.reference_prompt || 'No reference prompt available';
    } else {
        const page = currentBook.pages[currentPage];
        document.getElementById('infoPage').textContent = `${currentPage + 1} / ${currentBook.pages.length}`;
        // Show image_prompt first, fall back to scene, then text
        currentPrompt = page?.image_prompt || page?.scene || page?.text || 'No prompt available';

        // Check if this is a story page (has text field or is a story type)
        const pageType = page?.type;
        const isStoryPage = !pageType || pageType === 'story' || pageType === 'synthetic_cover';
        if (isStoryPage && pageType !== 'synthetic_cover') {
            showTextEditor = true;
            currentText = page?.text || '';
        }
    }

    // Update prompt editor
    const promptEditor = document.getElementById('promptEditor');
    if (promptEditor) {
        promptEditor.value = currentPrompt;
    }

    // Update text editor
    const textEditor = document.getElementById('textEditor');
    const textEditorPanel = document.getElementById('textEditorPanel');
    if (textEditor) {
        textEditor.value = currentText;
    }
    if (textEditorPanel) {
        textEditorPanel.style.display = showTextEditor ? 'block' : 'none';
    }

    // Clear status messages when navigating
    const textStatus = document.getElementById('textStatus');
    const promptStatus = document.getElementById('promptStatus');
    if (textStatus) textStatus.className = 'text-status';
    if (promptStatus) promptStatus.className = 'prompt-status';

    // Disable regenerate button on Creation Notes page
    const regenerateBtn = document.getElementById('regenerateBtn');
    if (regenerateBtn) {
        regenerateBtn.disabled = currentPage === -2;
        regenerateBtn.title = currentPage === -2 ? 'Navigate to a page to generate images' : '';
    }

    // Load reference versions
    loadReferenceVersions();

    // Load page image versions
    loadPageVersions();

    // Load feedback for current page
    loadFeedback();
    updateFeedbackCount();
}

// Image Editor Functions
let selectedReference = null;
let selectedReferences = []; // For multi-ref support
let uploadedReferenceData = null;
let loadingReferencesFor = null; // Guard against concurrent loads

async function loadReferenceVersions() {
    const container = document.getElementById('referenceVersions');
    if (!container || !currentBook) return;

    const slug = currentBook._slug || bookSlug;

    // Prevent concurrent loads for the same book - if already loading, skip
    if (loadingReferencesFor === slug) return;
    loadingReferencesFor = slug;

    container.innerHTML = '';

    // Try to load multi-ref manifest first
    const multiRefPath = `/books/references/${slug}_multi/manifest.json`;
    let multiRefs = null;
    try {
        const resp = await fetch(multiRefPath);
        if (resp.ok) {
            multiRefs = await resp.json();
        }
    } catch (e) {
        // No multi-ref available
    }

    if (multiRefs && multiRefs.references) {
        // Display multi-ref images
        const refs = multiRefs.references;
        selectedReferences = [];

        // Group by type: characters first, then environments
        const charRefs = Object.entries(refs).filter(([k]) => k.startsWith('char_'));
        const envRefs = Object.entries(refs).filter(([k]) => k.startsWith('env_'));
        const otherRefs = Object.entries(refs).filter(([k]) => !k.startsWith('char_') && !k.startsWith('env_'));

        const allRefs = [...charRefs, ...envRefs, ...otherRefs];
        const MAX_INITIAL_REFS = 3; // Only select first 3 by default

        allRefs.forEach(([key, localPath], index) => {
            // Convert local path to web path
            const filename = localPath.split('/').pop();
            const webPath = `/books/references/${slug}_multi/${filename}`;

            // Create nice label from key (char_jane_front -> Jane Front)
            const label = key
                .replace('char_', '')
                .replace('env_', '')
                .replace('style_', '')
                .split('_')
                .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                .join(' ');

            const isSelected = index < MAX_INITIAL_REFS;
            const div = document.createElement('div');
            div.className = `reference-version ${isSelected ? 'active' : ''}`;
            div.dataset.refKey = key;
            div.dataset.refPath = webPath;
            div.title = 'Click to select, double-click to view full size';
            div.innerHTML = `
                <img src="${webPath}" alt="${label}" onerror="this.parentElement.style.display='none'">
                <span class="version-label">${label}</span>
            `;
            div.onclick = () => toggleMultiReference(div);
            div.ondblclick = (e) => { e.stopPropagation(); window.open(webPath, '_blank'); };
            container.appendChild(div);
            if (isSelected) {
                selectedReferences.push(webPath);
            }
        });

        // Set selectedReference to first one for backwards compat
        selectedReference = selectedReferences[0] || null;
    } else {
        // Fall back to legacy v1/v2/v3 references
        const versions = [
            { path: `/books/references/${slug}_reference.png`, label: 'v1', version: 1 },
            { path: `/books/references/${slug}_reference_v2.png`, label: 'v2', version: 2 },
            { path: `/books/references/${slug}_reference_v3.png`, label: 'v3', version: 3 },
        ];

        const activeVersion = currentBook.active_reference_version || 1;

        versions.forEach(v => {
            const div = document.createElement('div');
            div.className = `reference-version ${v.version === activeVersion ? 'active' : ''}`;
            div.title = 'Click to select, double-click to view full size';
            div.innerHTML = `
                <img src="${v.path}" alt="Reference ${v.label}" onerror="this.parentElement.style.display='none'">
                <span class="version-label">${v.label}${v.version === activeVersion ? ' ✓' : ''}</span>
            `;
            div.onclick = () => selectReference(v.path, v.version, div);
            div.ondblclick = (e) => { e.stopPropagation(); window.open(v.path, '_blank'); };
            container.appendChild(div);
        });

        selectedReference = versions.find(v => v.version === activeVersion)?.path || versions[0].path;
        selectedReferences = [selectedReference];
    }

    // Add upload button
    const uploadBtn = document.createElement('div');
    uploadBtn.className = 'upload-reference';
    uploadBtn.innerHTML = '+';
    uploadBtn.title = 'Upload custom reference';
    uploadBtn.onclick = () => document.getElementById('uploadReferenceInput').click();
    container.appendChild(uploadBtn);

    // Clear the loading guard (allow future loads for different books)
    loadingReferencesFor = null;
}

const MAX_REFS = 3; // wan2.6 limit

function toggleMultiReference(element) {
    const path = element.dataset.refPath;
    const isActive = element.classList.contains('active');

    if (isActive) {
        element.classList.remove('active');
        selectedReferences = selectedReferences.filter(p => p !== path);
    } else {
        // Check limit before adding
        if (selectedReferences.length >= MAX_REFS) {
            alert(`Maximum ${MAX_REFS} references allowed for Wan 2.6`);
            return;
        }
        element.classList.add('active');
        selectedReferences.push(path);
    }

    // Update selectedReference for backwards compat
    selectedReference = selectedReferences[0] || null;
}

function selectReference(path, version, element) {
    selectedReference = path;
    uploadedReferenceData = null;

    // Update UI
    document.querySelectorAll('.reference-version').forEach(el => el.classList.remove('active'));
    element.classList.add('active');
}

async function handleReferenceUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        uploadedReferenceData = e.target.result;

        // Add to versions display
        const container = document.getElementById('referenceVersions');
        const uploadBtn = container.querySelector('.upload-reference');

        // Remove any existing custom upload
        const existingCustom = container.querySelector('.reference-version.custom');
        if (existingCustom) existingCustom.remove();

        const div = document.createElement('div');
        div.className = 'reference-version custom active';
        div.innerHTML = `
            <img src="${uploadedReferenceData}" alt="Custom reference">
            <span class="version-label">custom</span>
        `;
        div.onclick = () => selectReference(null, 'custom', div);
        container.insertBefore(div, uploadBtn);

        // Select this one
        document.querySelectorAll('.reference-version').forEach(el => el.classList.remove('active'));
        div.classList.add('active');
        selectedReference = null; // null means use uploaded data
    };
    reader.readAsDataURL(file);
}

// Page Image Versions
function loadPageVersions() {
    const section = document.getElementById('pageVersionsSection');
    const container = document.getElementById('pageVersions');
    if (!section || !container || !currentBook) return;

    // Only show for story pages (not reference, notes, or special pages)
    if (currentPage < 0) {
        section.style.display = 'none';
        return;
    }

    const page = currentBook.pages[currentPage];
    if (!page || ['cover', 'copyright', 'parent_guide', 'level_info', 'wordlist', 'wordsearch', 'series_info', 'back_cover'].includes(page.type)) {
        section.style.display = 'none';
        return;
    }

    // Get versions from page data
    const versions = page.image_versions || [];
    const currentImage = page.image || null;

    if (versions.length === 0 && !currentImage) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';
    container.innerHTML = '';

    // Helper to format version metadata for tooltip
    function formatVersionTooltip(v) {
        const parts = [];
        if (v.model) parts.push(`Model: ${v.model}`);
        if (v.prompt) {
            const shortPrompt = v.prompt.length > 100 ? v.prompt.slice(0, 100) + '...' : v.prompt;
            parts.push(`Prompt: ${shortPrompt}`);
        }
        if (v.created_at) {
            const date = new Date(v.created_at);
            parts.push(`Created: ${date.toLocaleDateString()} ${date.toLocaleTimeString()}`);
        }
        return parts.join('\n');
    }

    // Find current version metadata (if current image matches a version)
    const currentVersionData = versions.find(v => v.url === currentImage);

    // Add current image if it exists
    if (currentImage) {
        const div = document.createElement('div');
        div.className = 'page-version active';
        const tooltip = currentVersionData ? formatVersionTooltip(currentVersionData) : 'Current image';
        div.title = tooltip;
        div.innerHTML = `
            <img src="${currentImage}" alt="Current" onerror="this.parentElement.style.display='none'">
            <span class="version-label current">current</span>
        `;
        div.onclick = () => selectPageVersion(currentImage, div);
        container.appendChild(div);
    }

    // Add version history (reverse order to show newest first)
    const sortedVersions = [...versions].reverse();
    sortedVersions.forEach((v, idx) => {
        // Skip if this is already the current image
        if (v.url === currentImage) return;

        const versionNum = v.version || (versions.length - idx);
        const tooltip = formatVersionTooltip(v);

        const div = document.createElement('div');
        div.className = 'page-version';
        div.title = tooltip;
        div.innerHTML = `
            <img src="${v.url}" alt="v${versionNum}" onerror="this.parentElement.style.display='none'">
            <span class="version-label">v${versionNum}</span>
        `;
        div.onclick = () => selectPageVersion(v.url, div);
        container.appendChild(div);
    });
}

async function selectPageVersion(url, element) {
    if (!currentBook || currentPage < 0) return;

    // Update UI immediately
    document.querySelectorAll('.page-version').forEach(el => el.classList.remove('active'));
    element.classList.add('active');

    // Use shared function to set as current
    await setImageAsCurrent(url);
}

function getNextVersionNumber() {
    if (!currentBook || currentPage < 0) return 1;
    const page = currentBook.pages[currentPage];
    if (!page) return 1;

    const versions = page.image_versions || [];
    return versions.length + 1;
}

async function regenerateImage() {
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
        const slug = currentBook._slug || bookSlug;
        const pageNum = currentPage === -1 ? 'reference' : currentPage;

        // Prepare reference images - use URLs for hosted images, base64 only for uploads
        // Models that use reference images for style transfer
        const modelsWithReference = ['gemini-3-pro', 'gemini-flash', 'wan2.6-image', 'wan2.5-i2i'];
        let referenceData = null;
        let referenceIsUrl = false;
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

function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

// Compress image data URL to reduce payload size for uploads
function compressImageDataUrl(dataUrl, maxSize = 512, quality = 0.8) {
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

async function pollForImageResult(taskId, statusEndpoint, maxAttempts = 40) {
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

let lastGeneratedUrl = null;
let lastGeneratedBlobUrl = null;
let lastGenerationMetadata = null;

async function showGeneratedImage(url, slug, pageNum, generationMetadata = {}) {
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
            <button onclick="useGeneratedImage()" style="margin-top: 8px; padding: 6px 12px; background: var(--color-sage); color: white; border: none; border-radius: 4px; cursor: pointer;">
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

async function useGeneratedImage() {
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

async function setImageAsCurrent(blobUrl) {
    const status = document.getElementById('generationStatus');
    const slug = currentBook._slug || bookSlug;
    const pageNum = currentPage;
    const page = currentBook.pages[pageNum];

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

async function saveTextToBook() {
    const text = document.getElementById('textEditor').value;
    const status = document.getElementById('textStatus');

    if (currentPage < 0) {
        status.className = 'text-status error';
        status.textContent = 'Cannot edit text on this page type';
        return;
    }

    const slug = currentBook._slug || bookSlug;
    const pageNum = currentPage;

    status.className = 'text-status loading';
    status.textContent = 'Saving...';

    try {
        const response = await fetch('/api/save-book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                slug,
                pageIndex: pageNum,
                field: 'text',
                value: text
            })
        });

        const result = await response.json();

        if (result.success) {
            status.className = 'text-status success';
            status.textContent = 'Text saved!';
            // Update local book data
            if (currentBook.pages[pageNum]) {
                currentBook.pages[pageNum].text = text;
            }
            // Re-render to show the change
            renderPage();
        } else {
            throw new Error(result.error || 'Save failed');
        }
    } catch (error) {
        status.className = 'text-status error';
        status.textContent = `Error: ${error.message}`;
    }
}

async function savePromptToBook() {
    const prompt = document.getElementById('promptEditor').value;
    const status = document.getElementById('promptStatus');

    if (!prompt) {
        status.className = 'prompt-status error';
        status.textContent = 'No prompt to save';
        return;
    }

    const slug = currentBook._slug || bookSlug;
    const pageNum = currentPage;

    status.className = 'prompt-status loading';
    status.textContent = 'Saving...';

    try {
        const response = await fetch('/api/save-book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                slug,
                pageIndex: pageNum,
                field: pageNum === -1 ? 'reference_prompt' : 'image_prompt',
                value: prompt
            })
        });

        const result = await response.json();

        if (result.success) {
            status.className = 'prompt-status success';
            status.textContent = 'Prompt saved!';
            // Update local book data
            if (pageNum === -1) {
                currentBook.reference_prompt = prompt;
            } else if (currentBook.pages[pageNum]) {
                currentBook.pages[pageNum].image_prompt = prompt;
            }
        } else {
            throw new Error(result.error || 'Save failed');
        }
    } catch (error) {
        status.className = 'prompt-status error';
        status.textContent = `Error: ${error.message}`;
    }
}

function getImagePath(page) {
    // FIRST: Check if page has an explicit image URL saved (from regeneration)
    if (page.image) {
        // Support both full URLs and relative paths
        if (page.image.startsWith('http')) {
            return page.image;
        }
        return `/books/${page.image}`;
    }

    // For cover pages without explicit image, use the cover image
    if (page.type === 'cover' || (page.page === 1 && !page.type)) {
        return getCoverImagePath();
    }

    const pageNum = String(page.page || currentPage + 1).padStart(2, '0');
    const slug = currentBook._slug || bookSlug;

    // Check if this is a legacy book with custom image paths
    if (legacyImagePaths[slug]) {
        const info = legacyImagePaths[slug];
        return `/books/${info.imageFolder}/${info.imagePrefix}${pageNum}.png`;
    }

    // Default path for new curriculum books: /books/images/{slug}_page{nn}.png
    return `/books/images/${slug}_page${pageNum}.png`;
}

// Generate rich gold renaissance tapestry pattern
function generateCoverPattern(seed = 0) {
    // Rich gold/burgundy renaissance palette
    const baseGold = '#8B6914';
    const lightGold = '#C9A227';
    const darkGold = '#5C4510';
    const accent = '#6B1C23'; // deep burgundy

    // Damask/floral motif variations
    const motifs = [
        // Classic damask fleur
        `<g id="motif">
            <path d="M20 5 Q25 10 20 15 Q15 10 20 5" fill="${lightGold}" opacity="0.6"/>
            <path d="M20 5 Q25 10 20 15 Q15 10 20 5" fill="none" stroke="${darkGold}" stroke-width="0.5"/>
            <circle cx="20" cy="10" r="2" fill="${lightGold}" opacity="0.8"/>
            <path d="M15 10 Q20 5 25 10" fill="none" stroke="${lightGold}" stroke-width="1" opacity="0.5"/>
            <path d="M15 10 Q20 15 25 10" fill="none" stroke="${lightGold}" stroke-width="1" opacity="0.5"/>
        </g>`,
        // Ornate scroll
        `<g id="motif">
            <path d="M12 10 Q20 2 28 10 Q20 18 12 10" fill="${lightGold}" opacity="0.4"/>
            <circle cx="20" cy="10" r="3" fill="${lightGold}" opacity="0.6"/>
            <path d="M17 10 Q20 7 23 10 Q20 13 17 10" fill="${darkGold}" opacity="0.5"/>
            <path d="M10 10 L14 10 M26 10 L30 10" stroke="${lightGold}" stroke-width="1" opacity="0.4"/>
        </g>`,
        // Royal medallion
        `<g id="motif">
            <circle cx="20" cy="10" r="6" fill="none" stroke="${lightGold}" stroke-width="1" opacity="0.5"/>
            <circle cx="20" cy="10" r="3" fill="${lightGold}" opacity="0.5"/>
            <path d="M20 4 L20 6 M20 14 L20 16 M14 10 L16 10 M24 10 L26 10" stroke="${lightGold}" stroke-width="1.5" opacity="0.6"/>
            <path d="M15 5 L17 7 M23 7 L25 5 M15 15 L17 13 M23 13 L25 15" stroke="${lightGold}" stroke-width="1" opacity="0.4"/>
        </g>`,
        // Floral cross
        `<g id="motif">
            <ellipse cx="20" cy="6" rx="3" ry="4" fill="${lightGold}" opacity="0.5"/>
            <ellipse cx="20" cy="14" rx="3" ry="4" fill="${lightGold}" opacity="0.5"/>
            <ellipse cx="16" cy="10" rx="4" ry="3" fill="${lightGold}" opacity="0.5"/>
            <ellipse cx="24" cy="10" rx="4" ry="3" fill="${lightGold}" opacity="0.5"/>
            <circle cx="20" cy="10" r="2.5" fill="${darkGold}" opacity="0.6"/>
        </g>`
    ];

    const motifIndex = Math.abs(seed) % motifs.length;
    const motif = motifs[motifIndex];

    return `
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="tapestryPattern" width="40" height="20" patternUnits="userSpaceOnUse">
                    <rect width="40" height="20" fill="${baseGold}"/>
                    <!-- Subtle texture -->
                    <rect width="40" height="20" fill="url(#noise)" opacity="0.1"/>
                    ${motif}
                </pattern>
                <filter id="noise">
                    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" result="noise"/>
                    <feColorMatrix type="saturate" values="0"/>
                </filter>
                <!-- Gold gradient overlay -->
                <linearGradient id="goldSheen" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:${lightGold};stop-opacity:0.2"/>
                    <stop offset="50%" style="stop-color:${darkGold};stop-opacity:0.1"/>
                    <stop offset="100%" style="stop-color:${lightGold};stop-opacity:0.2"/>
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#tapestryPattern)"/>
            <rect width="100%" height="100%" fill="url(#goldSheen)"/>
            <!-- Top and bottom border lines -->
            <line x1="0" y1="2" x2="100%" y2="2" stroke="${lightGold}" stroke-width="1" opacity="0.6"/>
            <line x1="0" y1="98%" x2="100%" y2="98%" stroke="${lightGold}" stroke-width="1" opacity="0.6"/>
        </svg>
    `;
}

// Level readiness data with parent-friendly descriptions
const levelReadiness = {
    'pink': {
        name: 'Pink - Pre-Reader',
        ready: ['Knows letter names', 'Starting to learn letter sounds', 'Enjoys being read to'],
        learns: ['Letter-sound connections', 'Print concepts', 'Story structure'],
        examples: 'Simple words like: a, I, see, the',
        forKids: 'Best for children just starting to connect letters with sounds'
    },
    'yellow': {
        name: 'Yellow - Short Vowels',
        ready: ['Knows most letter sounds', 'Can blend a few sounds together'],
        learns: ['Short vowel sounds', 'Simple 3-letter words', 'Basic sight words'],
        examples: 'Words like: cat, sit, dog, run, bed',
        forKids: 'Best for children who can sound out simple 3-letter words'
    },
    'orange': {
        name: 'Orange - Building Skills',
        ready: ['Reads simple 3-letter words', 'Knows short vowel sounds'],
        learns: ['Letter pairs like sh, ch, th', 'More sight words'],
        examples: 'Words like: ship, chat, bath, wish, chop',
        forKids: 'Best for children comfortable with simple words, ready for letter pairs'
    },
    'red': {
        name: 'Red - Blends',
        ready: ['Reads words with sh, ch, th', 'Growing sight word vocabulary'],
        learns: ['Blend sounds like st, mp, nd', 'Longer sentences'],
        examples: 'Words like: stomp, jump, hand, best, crisp',
        forKids: 'Best for children ready for words with blended consonants'
    },
    'purple': {
        name: 'Purple - Growing Reader',
        ready: ['Reads blend words smoothly', 'Reads simple sentences well'],
        learns: ['More complex letter patterns', 'Reading with expression'],
        examples: 'Words like: splash, string, shrink',
        forKids: 'Best for children building reading fluency and confidence'
    },
    'blue': {
        name: 'Blue - Silent E',
        ready: ['Reads blends and digraphs', 'Good word recognition'],
        learns: ['Silent e makes vowels say their name', 'Long vowel sounds'],
        examples: 'Words like: cake, bike, hope, cute (the e is silent!)',
        forKids: 'Best for children ready to learn how silent e changes words'
    },
    'green': {
        name: 'Green - Vowel Teams',
        ready: ['Understands silent e pattern', 'Reads with good fluency'],
        learns: ['Vowel pairs that work together', 'More complex words'],
        examples: 'Words like: team, rain, boat, moon, play',
        forKids: 'Best for children ready for vowel combinations'
    },
    'gold': {
        name: 'Gold - Advanced',
        ready: ['Reads most common patterns', 'Strong comprehension'],
        learns: ['R-controlled vowels', 'Advanced word patterns'],
        examples: 'Words like: bird, farm, word, her, turn',
        forKids: 'Best for confident readers expanding their skills'
    }
};

// Generate word search grid
function generateWordsearchGrid(words, size = 8) {
    const grid = Array(size).fill(null).map(() => Array(size).fill(''));
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

    // Place words horizontally and vertically
    words.forEach(word => {
        const w = word.toUpperCase();
        const horizontal = Math.random() > 0.5;
        let placed = false;
        let attempts = 0;

        while (!placed && attempts < 50) {
            attempts++;
            if (horizontal && w.length <= size) {
                const row = Math.floor(Math.random() * size);
                const col = Math.floor(Math.random() * (size - w.length + 1));
                let canPlace = true;
                for (let i = 0; i < w.length; i++) {
                    if (grid[row][col + i] !== '' && grid[row][col + i] !== w[i]) {
                        canPlace = false;
                        break;
                    }
                }
                if (canPlace) {
                    for (let i = 0; i < w.length; i++) {
                        grid[row][col + i] = w[i];
                    }
                    placed = true;
                }
            } else if (w.length <= size) {
                const row = Math.floor(Math.random() * (size - w.length + 1));
                const col = Math.floor(Math.random() * size);
                let canPlace = true;
                for (let i = 0; i < w.length; i++) {
                    if (grid[row + i][col] !== '' && grid[row + i][col] !== w[i]) {
                        canPlace = false;
                        break;
                    }
                }
                if (canPlace) {
                    for (let i = 0; i < w.length; i++) {
                        grid[row + i][col] = w[i];
                    }
                    placed = true;
                }
            }
        }
    });

    // Fill empty cells with random letters
    for (let r = 0; r < size; r++) {
        for (let c = 0; c < size; c++) {
            if (grid[r][c] === '') {
                grid[r][c] = letters[Math.floor(Math.random() * 26)];
            }
        }
    }
    return grid;
}

function renderPage() {
    if (!currentBook) return;

    const bookPage = document.getElementById('bookPage');

    // Handle creation notes page (page -2) in edit mode
    if (currentPage === -2 && isEditMode()) {
        const storyBible = currentBook.story_bible || {};
        const hasStoryBible = Object.keys(storyBible).length > 0;

        bookPage.innerHTML = `
            <div class="page-story" style="padding: 24px; background: var(--color-cream); overflow-y: auto;">
                <h2 style="color: var(--color-sage); margin-bottom: 16px; font-size: 1.2rem;">Creation Notes</h2>

                ${hasStoryBible ? `
                    ${storyBible.premise ? `
                        <div style="margin-bottom: 16px;">
                            <h3 style="color: var(--color-terracotta); font-size: 0.9rem; margin-bottom: 6px;">Premise</h3>
                            <p style="font-size: 0.85rem; line-height: 1.5; color: var(--color-charcoal);">${storyBible.premise}</p>
                        </div>
                    ` : ''}

                    ${storyBible.themes ? `
                        <div style="margin-bottom: 16px;">
                            <h3 style="color: var(--color-terracotta); font-size: 0.9rem; margin-bottom: 6px;">Themes</h3>
                            <p style="font-size: 0.85rem; color: var(--color-charcoal);">${Array.isArray(storyBible.themes) ? storyBible.themes.join(', ') : storyBible.themes}</p>
                        </div>
                    ` : ''}

                    ${storyBible.character_arcs ? `
                        <div style="margin-bottom: 16px;">
                            <h3 style="color: var(--color-terracotta); font-size: 0.9rem; margin-bottom: 6px;">Character Arcs</h3>
                            ${Object.entries(storyBible.character_arcs).map(([char, arc]) =>
                                `<p style="font-size: 0.85rem; color: var(--color-charcoal); margin-bottom: 4px;"><strong>${char}:</strong> ${arc}</p>`
                            ).join('')}
                        </div>
                    ` : ''}

                    ${storyBible.setting ? `
                        <div style="margin-bottom: 16px;">
                            <h3 style="color: var(--color-terracotta); font-size: 0.9rem; margin-bottom: 6px;">Setting</h3>
                            <p style="font-size: 0.85rem; line-height: 1.5; color: var(--color-charcoal);">${storyBible.setting}</p>
                        </div>
                    ` : ''}

                    ${storyBible.emotional_beats ? `
                        <div style="margin-bottom: 16px;">
                            <h3 style="color: var(--color-terracotta); font-size: 0.9rem; margin-bottom: 6px;">Emotional Beats</h3>
                            ${storyBible.emotional_beats.map(beat =>
                                `<p style="font-size: 0.8rem; color: var(--color-charcoal); margin-bottom: 4px;">
                                    <span style="color: var(--color-sage);">Page ${beat.page}:</span> ${beat.beat}
                                </p>`
                            ).join('')}
                        </div>
                    ` : ''}

                    ${storyBible.level_adaptation ? `
                        <div style="margin-bottom: 16px;">
                            <h3 style="color: var(--color-terracotta); font-size: 0.9rem; margin-bottom: 6px;">Level Adaptation Notes</h3>
                            <p style="font-size: 0.85rem; line-height: 1.5; color: var(--color-charcoal);">${storyBible.level_adaptation}</p>
                        </div>
                    ` : ''}
                ` : `
                    <div style="text-align: center; color: var(--color-text-muted); padding: 40px 20px;">
                        <p style="margin-bottom: 12px;">No story bible available for this book.</p>
                        <p style="font-size: 0.8rem;">Add a <code>story_bible</code> field to the book JSON to enable creation notes.</p>
                    </div>
                `}
            </div>
        `;
        updateNavigationState();
        updateEditInfo();
        return;
    }

    // Handle reference page (page -1) in edit mode
    if (currentPage === -1 && isEditMode()) {
        const refPath = getReferenceImagePath();
        bookPage.innerHTML = `
            <div class="page-story" style="display: flex; align-items: center; justify-content: center; background: var(--color-charcoal);">
                <img src="${refPath}" alt="Reference Image" style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 8px;"
                     onerror="this.parentElement.innerHTML='<div style=\\'text-align:center; color: var(--color-text-muted);\\'>No reference image available</div>'">
            </div>
        `;
        updateNavigationState();
        updateEditInfo();
        return;
    }

    const page = currentBook.pages[currentPage];
    // Support both 'color' and 'level' fields
    const colorRaw = currentBook.color || currentBook.level || 'orange';
    const color = colorRaw.toLowerCase();
    const colorDisplay = colorRaw.charAt(0).toUpperCase() + colorRaw.slice(1).toLowerCase();

    // Determine page type - if first page has no type, treat as synthetic cover
    let pageType = page.type;
    if (currentPage === 0 && !pageType) {
        pageType = 'synthetic_cover';
    }

    // Handle different page types
    switch (pageType) {
        case 'synthetic_cover':
            // Generate a cover for books that don't have one
            const synthPatternSeed = (currentBook.title || '').length;
            const synthPatternSvg = generateCoverPattern(synthPatternSeed);
            const synthTitle = currentBook.title || 'Untitled';
            const synthScene = page.scene || currentBook.summary || '';
            bookPage.innerHTML = `
                <div class="page-cover">
                    <div class="cover-corner-tab">
                        <div class="corner-ribbon">
                            <span class="brand-name">FunBookies</span>
                            <span class="level-text">${currentBook.level || ''} Level</span>
                        </div>
                    </div>
                    <div class="cover-logo">
                        <img src="/images/funbookies_icon.png" alt="FunBookies">
                    </div>
                    <div class="cover-image">
                        <div class="page-image-placeholder" style="display: flex;">
                            <div class="scene-icon">📖</div>
                            ${synthScene ? `<div class="scene-text">${synthScene}</div>` : ''}
                        </div>
                    </div>
                    <div class="cover-pattern-banner">
                        <div class="cover-pattern">${synthPatternSvg}</div>
                        <div class="cover-title-frame">
                            <h1>${synthTitle}</h1>
                        </div>
                    </div>
                </div>
            `;
            break;

        case 'copyright':
            const copyrightYear = currentBook.created ? currentBook.created.split('-')[0] : new Date().getFullYear();
            const bookSlug = currentBook.slug || currentBook.id || '';
            bookPage.innerHTML = `
                <div class="page-copyright">
                    <div class="copyright-logo">
                        <img src="/images/funbookies_icon.png" alt="FunBookies">
                    </div>
                    <div class="brand-wordmark">FunBookies</div>
                    <div class="copyright-divider"></div>
                    <div class="copyright-text">
                        <strong>${currentBook.title || 'Untitled'}</strong><br><br>
                        Text & illustrations © ${copyrightYear} FunBookies<br>
                        All rights reserved.<br><br>
                        Published by FunBookies<br>
                        <strong>funbookies.com</strong>
                    </div>
                    ${bookSlug ? `<div class="book-id">${bookSlug}</div>` : ''}
                </div>
            `;
            break;

        case 'parent_guide':
            const tips = currentBook.parent_tips;
            if (tips && (tips.before_reading || tips.during_reading || tips.after_reading)) {
                // Book-specific parent tips
                bookPage.innerHTML = `
                    <div class="page-parent-guide">
                        <div class="guide-header">
                            <div class="guide-icon">
                                <img src="/images/funbookies_icon.png" alt="">
                            </div>
                            <h3>Reading Tips</h3>
                        </div>
                        <div class="tips-box">
                            ${tips.before_reading ? `
                                <div style="margin-bottom: 10px;">
                                    <h4 style="color: var(--color-sage);">📖 Before Reading</h4>
                                    <p style="font-size: 0.8rem; color: var(--color-charcoal); line-height: 1.4; margin: 0;">${tips.before_reading}</p>
                                </div>
                            ` : ''}
                            ${tips.during_reading ? `
                                <div style="margin-bottom: 10px;">
                                    <h4 style="color: var(--color-terracotta);">📚 During Reading</h4>
                                    <p style="font-size: 0.8rem; color: var(--color-charcoal); line-height: 1.4; margin: 0;">${tips.during_reading}</p>
                                </div>
                            ` : ''}
                            ${tips.after_reading ? `
                                <div>
                                    <h4 style="color: var(--color-sage);">💬 After Reading</h4>
                                    <p style="font-size: 0.8rem; color: var(--color-charcoal); line-height: 1.4; margin: 0;">${tips.after_reading}</p>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            } else {
                // Generic tips fallback
                bookPage.innerHTML = `
                    <div class="page-parent-guide">
                        <div class="guide-header">
                            <div class="guide-icon">
                                <img src="/images/funbookies_icon.png" alt="">
                            </div>
                            <h3>Read Together!</h3>
                        </div>
                        <p class="parent-intro">
                            Reading with your child is one of the most valuable things you can do.
                            Be patient, be encouraging, and have fun!
                        </p>
                        <div class="tips-box">
                            <h4>Quick Tips</h4>
                            <ul>
                                <li>Point to each word as you read</li>
                                <li>Give time to sound out words</li>
                                <li>Praise effort, not just answers</li>
                                <li>Re-reading builds confidence</li>
                                <li>Keep it short and positive</li>
                            </ul>
                        </div>
                    </div>
                `;
            }
            break;

        case 'level_info':
            const lvlInfo = levelReadiness[color] || levelReadiness['orange'];
            const targetPhonics = currentBook.targetPhonics || currentBook.skill || 'Reading practice';
            const skillDesc = currentBook.skill_description || lvlInfo.forKids || '';
            bookPage.innerHTML = `
                <div class="page-level-info">
                    <div class="level-header">
                        <span class="level-badge ${color}">${colorDisplay} Level</span>
                        <h3>Get Ready to Read!</h3>
                    </div>
                    <div class="skill-card">
                        <div class="skill-label">This book focuses on</div>
                        <div class="skill-title">${targetPhonics}</div>
                        ${skillDesc ? `<div class="skill-desc">${skillDesc}</div>` : ''}
                    </div>
                    <div class="ready-text">
                        Let's read <strong>${currentBook.title}</strong>!
                    </div>
                </div>
            `;
            break;

        case 'wordlist':
            const wl = currentBook.word_list || {};
            // Count total words to determine if compact mode needed
            const totalWords = (wl.sound_out?.length || 0) + (wl.sight?.length || 0) + (wl.new?.length || 0);
            const compactClass = totalWords > 15 ? 'compact' : '';
            bookPage.innerHTML = `
                <div class="page-wordlist">
                    <h3 class="wordlist-title">Words to Know</h3>
                    ${wl.sound_out?.length ? `
                        <div class="wordlist-section ${compactClass}">
                            <h4>Sound Out</h4>
                            <div class="words">${wl.sound_out.map(w => `<span class="word-box">${w}</span>`).join('')}</div>
                        </div>
                    ` : ''}
                    ${wl.sight?.length ? `
                        <div class="wordlist-section ${compactClass}">
                            <h4>Sight Words</h4>
                            <div class="words">${wl.sight.map(w => `<span class="word-box">${w}</span>`).join('')}</div>
                        </div>
                    ` : ''}
                    ${wl.new?.length ? `
                        <div class="wordlist-section ${compactClass}">
                            <h4>New Words</h4>
                            <div class="words">${wl.new.map(w => `<span class="word-box">${w}</span>`).join('')}</div>
                        </div>
                    ` : ''}
                </div>
            `;
            break;

        case 'wordsearch':
            // Use sound_out words from word_list if available
            const wsWordList = currentBook.word_list?.sound_out || [];
            const wsWords = wsWordList.length > 0 ? wsWordList.slice(0, 6) : (currentBook.wordsearch_words || page.words || ['cat', 'sat', 'mat']);
            const gridSize = wsWords.length <= 4 ? 6 : 8;
            const grid = generateWordsearchGrid(wsWords, gridSize);
            bookPage.innerHTML = `
                <div class="page-wordsearch">
                    <div class="ws-header">
                        <span class="ws-icon">🔍</span>
                        <h3>Find the Words!</h3>
                    </div>
                    <div class="wordsearch-grid" style="grid-template-columns: repeat(${gridSize}, 1fr);">
                        ${grid.flat().map(letter => `<span>${letter}</span>`).join('')}
                    </div>
                    <div class="word-bank">
                        ${wsWords.map(w => `<span>${w}</span>`).join('')}
                    </div>
                </div>
            `;
            break;

        case 'end':
            const endImgPath = getImagePath(page);
            const endText = page.text || 'The End';
            bookPage.innerHTML = `
                <div class="page-end">
                    <div class="end-image">
                        <img src="${endImgPath}" alt="${endText}" decoding="async">
                        <div class="end-overlay">
                            <div class="end-star">⭐</div>
                            <div class="end-text">${endText}</div>
                        </div>
                    </div>
                    <div class="end-actions">
                        <button class="end-btn" onclick="goToPage(0)">Read Again</button>
                        <button class="end-btn primary" onclick="window.location.href='/books/'">More Books</button>
                    </div>
                </div>
            `;
            break;

        case 'series_info':
            const levels = ['pink', 'yellow', 'orange', 'red', 'purple', 'blue', 'green', 'gold'];
            const levelNames = ['Pink', 'Yellow', 'Orange', 'Red', 'Purple', 'Blue', 'Green', 'Gold'];
            const currentLevelIdx = levels.indexOf(color);
            bookPage.innerHTML = `
                <div class="page-series-info">
                    <div class="series-logo">
                        <img src="/images/funbookies_icon.png" alt="FunBookies">
                    </div>
                    <h3>FunBookies</h3>
                    <div class="tagline">Books that grow with your reader</div>
                    <div class="level-ladder">
                        ${levels.slice(0, 5).map((lvl, i) => `
                            <div class="level-rung ${lvl === color ? 'current' : ''}">
                                <span class="rung-badge level-badge ${lvl}">${levelNames[i]}</span>
                                ${lvl === color ? '<span class="rung-arrow">← You are here!</span>' : ''}
                            </div>
                        `).join('')}
                    </div>
                    <div class="series-cta">
                        Find more books at <strong>funbookies.com</strong>
                    </div>
                </div>
            `;
            break;

        case 'back_cover':
            // Use back cover image, or fall back to cover image
            const backImgPath = page.image ? getImagePath(page) : getCoverImagePath();
            // Use book-specific blurb from back_cover page, or summary, or generate from premise
            const backBlurb = page.text || currentBook.summary ||
                (currentBook.story_bible?.premise ? currentBook.story_bible.premise.split('.')[0] + '.' : 'A fun story for beginning readers!');
            // Get actual words from this book's word list
            const bcWordList = currentBook.word_list || {};
            const bcWords = [...(bcWordList.sound_out || []).slice(0, 6), ...(bcWordList.new || []).slice(0, 2)];
            bookPage.innerHTML = `
                <div class="page-back-cover">
                    <div class="back-cover-image">
                        <img src="${backImgPath}" alt="" decoding="async">
                    </div>
                    <div class="back-cover-content">
                        <div class="back-cover-header">
                            <div class="bc-logo">
                                <img src="/images/funbookies_icon.png" alt="FunBookies">
                            </div>
                            <div class="bc-info">
                                <div class="bc-title">${currentBook.title}</div>
                                <span class="level-badge ${color}" style="font-size: 0.55rem; padding: 2px 8px;">${colorDisplay} Level</span>
                            </div>
                        </div>
                        <div class="back-cover-blurb">${backBlurb}</div>
                        ${bcWords.length > 0 ? `
                            <div class="back-cover-words">
                                <h5>Words in this book</h5>
                                <div class="word-chips">
                                    ${bcWords.map(w => `<span class="word-chip">${w}</span>`).join('')}
                                </div>
                            </div>
                        ` : ''}
                        <div class="back-cover-tagline">
                            <div class="tagline">"Every child can learn to read."</div>
                            <div class="features">
                                <span class="feature"><span class="feature-dot"></span> Decodable</span>
                                <span class="feature"><span class="feature-dot"></span> Phonics-based</span>
                                <span class="feature"><span class="feature-dot"></span> Research-backed</span>
                            </div>
                        </div>
                        <div class="back-cover-footer">
                            <div class="bc-brand">
                                <div class="bc-brand-logo">
                                    <img src="/images/funbookies_icon.png" alt="">
                                </div>
                                <span class="bc-brand-text">FunBookies</span>
                            </div>
                            <span class="bc-url">funbookies.com</span>
                        </div>
                    </div>
                </div>
            `;
            break;

        case 'cover':
            const coverImgPath = getImagePath(page);
            const coverScene = page.scene || currentBook.summary || '';
            const coverPlaceholderId = `cover-placeholder`;
            const coverTitle = page.text || currentBook.title || 'Untitled';
            const authorName = currentBook.author || '';
            bookPage.innerHTML = `
                <div class="page-cover" style="display: block; position: relative;">
                    <div class="cover-corner-tab">
                        <div class="corner-ribbon">
                            <span class="brand-name">FunBookies</span>
                            <span class="level-text">${colorDisplay} Level</span>
                        </div>
                    </div>
                    <div class="cover-logo">
                        <img src="/images/funbookies_icon.png" alt="FunBookies">
                    </div>
                    <div class="cover-image" style="height: 100%;">
                        <img src="${coverImgPath}" alt="${coverTitle}" decoding="async" fetchpriority="high" onerror="document.getElementById('${coverPlaceholderId}').style.display='flex'; this.style.display='none';">
                        <div id="${coverPlaceholderId}" class="page-image-placeholder" style="display: none;">
                            <div class="scene-icon">📚</div>
                            ${coverScene ? `<div class="scene-text">${coverScene}</div>` : ''}
                        </div>
                        <div class="cover-title-overlay">
                            <h1>${coverTitle}</h1>
                            ${authorName ? `<div class="author">by ${authorName}</div>` : ''}
                        </div>
                    </div>
                </div>
            `;
            break;

        default:
            // Regular story page with image and text
            const storyImgPath = getImagePath(page);
            const sceneDesc = page.scene || '';
            const placeholderId = `placeholder-${currentPage}`;
            const bookBand = currentBook.band || (currentBook.level ? currentBook.level.charAt(0) : 'A');
            const isLongForm = bookBand === 'C' || bookBand === 'D';
            const storyPageNum = page.story_page || '';

            if (isLongForm) {
                // Long-form layout for C/D band: text left, image right
                bookPage.classList.add('long-form');
                bookPage.innerHTML = `
                    <div class="page-watermark">
                        <img src="/images/funbookies_icon.png" alt="">
                    </div>
                    <div class="page-long-form">
                        <div class="long-form-text">
                            <p>${page.text || ''}</p>
                            ${storyPageNum ? `<div class="page-number">Page ${storyPageNum}</div>` : ''}
                        </div>
                        <div class="long-form-image">
                            <img src="${storyImgPath}" alt="" decoding="async" fetchpriority="high" onerror="document.getElementById('${placeholderId}').style.display='flex'; this.style.display='none';">
                            <div id="${placeholderId}" class="page-image-placeholder" style="display: none;">
                                <div class="scene-icon">🎨</div>
                                ${sceneDesc ? `<div class="scene-text">${sceneDesc}</div>` : ''}
                            </div>
                        </div>
                    </div>
                `;
            } else {
                // Standard layout for A/B band: image top, text bottom
                bookPage.classList.remove('long-form');
                bookPage.innerHTML = `
                    <div class="page-watermark">
                        <img src="/images/funbookies_icon.png" alt="">
                    </div>
                    <div class="page-image">
                        <img src="${storyImgPath}" alt="" decoding="async" fetchpriority="high" onerror="document.getElementById('${placeholderId}').style.display='flex'; this.style.display='none';">
                        <div id="${placeholderId}" class="page-image-placeholder" style="display: none;">
                            <div class="scene-icon">🎨</div>
                            ${sceneDesc ? `<div class="scene-text">${sceneDesc}</div>` : ''}
                            <div class="coming-soon">Illustration coming soon</div>
                        </div>
                    </div>
                    <div class="page-text">
                        <p>${page.text || ''}</p>
                    </div>
                `;
            }
    }

    // Update navigation state
    updateNavigationState();

    // Update edit mode info
    updateEditInfo();

    // Preload adjacent pages for faster navigation
    preloadAdjacentPages();
}

function prevPage() {
    // In edit mode, allow going to page -1 (reference)
    const minPage = isEditMode() ? -2 : 0;
    if (currentPage > minPage) {
        const bookPage = document.getElementById('bookPage');
        bookPage.classList.add('slide-right');
        setTimeout(() => {
            currentPage--;
            renderPage();
            updateUrl();
            bookPage.classList.remove('slide-right');
            bookPage.classList.add('fade-in');
            setTimeout(() => bookPage.classList.remove('fade-in'), 300);
        }, 150);
    }
}

function nextPage() {
    if (currentBook && currentPage < currentBook.pages.length - 1) {
        const bookPage = document.getElementById('bookPage');
        bookPage.classList.add('slide-left');
        setTimeout(() => {
            currentPage++;
            renderPage();
            updateUrl();
            bookPage.classList.remove('slide-left');
            bookPage.classList.add('fade-in');
            setTimeout(() => bookPage.classList.remove('fade-in'), 300);

            // Check if we just reached the last page
            if (currentPage === currentBook.pages.length - 1) {
                // Show completion overlay after a brief delay
                setTimeout(() => showBookComplete(), 1500);
            }
        }, 150);
    }
}

// Gallery View Functions
function renderGallery() {
    if (!currentBook) return;

    const grid = document.getElementById('galleryGrid');
    const stats = document.getElementById('galleryStats');
    const generateAllBtn = document.getElementById('generateAllBtn');
    const slug = currentBook._slug || bookSlug;

    let withImages = 0;
    let needImages = 0;

    // Build gallery cards
    const cards = currentBook.pages.map((page, index) => {
        const pageNum = page.page || (index + 1);
        const pageType = page.type || (index === 0 ? 'cover' : 'story');

        // Check if image exists
        const imagePath = pageType === 'cover'
            ? `/images/covers/${slug}.png`
            : `/books/images/${slug}_page${String(pageNum).padStart(2, '0')}.png`;

        // Get scene description (what we show when no image)
        const scene = page.scene || page.image_prompt || 'No scene description';
        const text = page.text || '';

        // For tracking - we'll update this via image load/error
        const cardId = `gallery-card-${index}`;

        return `
            <div class="gallery-card" id="${cardId}" data-page="${index}" onclick="goToPage(${index})">
                <div class="gallery-card-image">
                    <img src="${imagePath}"
                         alt="Page ${pageNum}"
                         onload="markCardHasImage('${cardId}')"
                         onerror="markCardNoImage('${cardId}')">
                </div>
                <div class="gallery-card-scene">
                    <div class="scene-label">Scene Description</div>
                    ${scene}
                </div>
                <div class="gallery-card-content">
                    <div class="gallery-card-page">${pageType === 'cover' ? 'Cover' : `Page ${pageNum}`}</div>
                    <div class="gallery-card-text">${text || '(No text)'}</div>
                </div>
                <div class="gallery-card-actions">
                    <button class="edit-btn" onclick="event.stopPropagation(); goToPageEdit(${index})">Edit</button>
                    <button class="generate-btn" onclick="event.stopPropagation(); generatePageFromGallery(${index})">Generate</button>
                </div>
            </div>
        `;
    }).join('');

    grid.innerHTML = cards;

    // Show generate all button in edit mode (gallery mode can show edit actions)
    generateAllBtn.style.display = 'inline-block';

    // Stats will be updated by markCardHasImage/markCardNoImage callbacks
    updateGalleryStats();
}

function markCardHasImage(cardId) {
    const card = document.getElementById(cardId);
    if (card) {
        card.classList.add('has-image');
        card.classList.remove('no-image');
    }
    updateGalleryStats();
}

function markCardNoImage(cardId) {
    const card = document.getElementById(cardId);
    if (card) {
        card.classList.add('no-image');
        card.classList.remove('has-image');
    }
    updateGalleryStats();
}

function updateGalleryStats() {
    const hasImage = document.querySelectorAll('.gallery-card.has-image').length;
    const noImage = document.querySelectorAll('.gallery-card.no-image').length;
    const stats = document.getElementById('galleryStats');
    stats.innerHTML = `
        <span class="has-image">${hasImage} with images</span>
        <span class="no-image">${noImage} need images</span>
    `;
}

function goToPage(pageIndex) {
    // From gallery, go to read mode; otherwise stay in current mode
    if (isGalleryMode()) {
        currentMode = 'read';
        document.body.classList.remove('mode-gallery', 'gallery-mode');
        document.body.classList.add('mode-read');
        updateModeButtons();
    }

    currentPage = pageIndex;
    renderPage();
    updateUrl();
}

function goToPageEdit(pageIndex) {
    // Switch to edit mode and go to page
    currentPage = pageIndex;
    setMode('edit');
}

function generatePageFromGallery(pageIndex) {
    // Go to page in edit mode and trigger regeneration
    goToPageEdit(pageIndex);
    // Small delay to let page render, then trigger generate
    setTimeout(() => regenerateImage(), 300);
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
    const originalStats = statsEl.innerHTML;

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
            if (!batchGenerating) updateGalleryStats();
        }, 5000);
    }
}

function buildBatchPrompt(scene, book) {
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

async function saveBatchImage(url, slug, pageNum, pageIndex) {
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

function updateNavigationState() {
    const minPage = isEditMode() ? -2 : 0;
    document.getElementById('prevBtn').disabled = currentPage <= minPage;
    document.getElementById('nextBtn').disabled = !currentBook || currentPage >= currentBook.pages.length - 1;

    // Update page indicators (both top and bottom)
    let pageText;
    if (currentPage === -2) {
        pageText = `Notes / ${currentBook?.pages.length || 0}`;
    } else if (currentPage === -1) {
        pageText = `Ref / ${currentBook?.pages.length || 0}`;
    } else {
        pageText = `${currentPage + 1} / ${currentBook?.pages.length || 0}`;
    }
    document.getElementById('pageIndicator').textContent = pageText;
    const bottomIndicator = document.getElementById('bottomPageIndicator');
    if (bottomIndicator) bottomIndicator.textContent = pageText;
}

// Keyboard navigation (skip when editing text)
document.addEventListener('keydown', (e) => {
    // Don't navigate if user is typing in an input or textarea
    const activeEl = document.activeElement;
    const isEditing = activeEl && (
        activeEl.tagName === 'INPUT' ||
        activeEl.tagName === 'TEXTAREA' ||
        activeEl.isContentEditable
    );

    if (isEditing && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
        return; // Let the text cursor move normally
    }

    if (e.key === 'ArrowLeft') prevPage();
    if (e.key === 'ArrowRight') nextPage();
    if (e.key === 'Escape') window.location.href = '/books/';
});

// Touch swipe support
let touchStartX = 0;
document.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
});

document.addEventListener('touchend', (e) => {
    const touchEndX = e.changedTouches[0].clientX;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > 50) {
        if (diff > 0) nextPage();
        else prevPage();
    }
});

// Image preloading cache
const imageCache = new Map();

function preloadImage(src) {
    if (!src || imageCache.has(src)) return;
    const img = new Image();
    img.src = src;
    imageCache.set(src, img);
}

function preloadAdjacentPages() {
    if (!currentBook) return;

    // Preload next 2 and previous 1 pages
    const pagesToPreload = [currentPage - 1, currentPage + 1, currentPage + 2];

    for (const pageIdx of pagesToPreload) {
        if (pageIdx >= 0 && pageIdx < currentBook.pages.length) {
            const page = currentBook.pages[pageIdx];
            const imgPath = getImagePathForPage(page, pageIdx);
            if (imgPath) preloadImage(imgPath);
        }
    }

    // Also preload cover image
    preloadImage(getCoverImagePath());
}

function getImagePathForPage(page, pageIdx) {
    if (page.type === 'cover' || (pageIdx === 0 && !page.type)) {
        return getCoverImagePath();
    }
    if (page.type && ['copyright', 'parent_guide', 'level_info', 'wordlist', 'wordsearch', 'series_info'].includes(page.type)) {
        return null; // These pages don't have images
    }
    if (page.image) {
        return `/books/${page.image}`;
    }
    const pageNum = String(page.page || pageIdx + 1).padStart(2, '0');
    const slug = currentBook._slug || bookSlug;
    if (legacyImagePaths[slug]) {
        const info = legacyImagePaths[slug];
        return `/books/${info.imageFolder}/${info.imagePrefix}${pageNum}.png`;
    }
    return `/books/images/${slug}_page${pageNum}.png`;
}

// Feedback system
let currentRating = null;

function getFeedbackKey(bookSlug, pageNum) {
    return `feedback_${bookSlug}_page${pageNum}`;
}

function getAllFeedbackKey() {
    return 'funbookies_all_feedback';
}

function setRating(rating) {
    const upBtn = document.getElementById('thumbsUp');
    const downBtn = document.getElementById('thumbsDown');

    if (currentRating === rating) {
        // Toggle off if clicking same button
        currentRating = null;
        upBtn.classList.remove('selected');
        downBtn.classList.remove('selected');
    } else {
        currentRating = rating;
        upBtn.classList.toggle('selected', rating === 'up');
        downBtn.classList.toggle('selected', rating === 'down');
    }
}

function saveFeedback() {
    if (!currentBook || !isEditMode()) return;

    const comment = document.getElementById('feedbackComment').value;
    const pageNum = currentPage + 1;
    const page = currentBook.pages[currentPage];

    const feedback = {
        bookSlug: bookSlug,
        bookTitle: currentBook.title,
        pageNumber: pageNum,
        pageType: page.type || 'story',
        pageText: page.text || '',
        scene: page.scene || '',
        rating: currentRating,
        comment: comment,
        timestamp: new Date().toISOString()
    };

    // Save individual page feedback
    const key = getFeedbackKey(bookSlug, pageNum);
    localStorage.setItem(key, JSON.stringify(feedback));

    // Also update the master feedback list
    let allFeedback = JSON.parse(localStorage.getItem(getAllFeedbackKey()) || '{}');
    if (!allFeedback[bookSlug]) {
        allFeedback[bookSlug] = {
            title: currentBook.title,
            level: currentBook.level,
            pages: {}
        };
    }
    allFeedback[bookSlug].pages[pageNum] = feedback;
    localStorage.setItem(getAllFeedbackKey(), JSON.stringify(allFeedback));

    // Show status and update count
    const status = document.getElementById('feedbackStatus');
    status.textContent = `Saved! (${new Date().toLocaleTimeString()})`;
    setTimeout(() => { status.textContent = ''; }, 3000);
    updateFeedbackCount();
}

function loadFeedback() {
    if (!currentBook || !isEditMode()) return;

    const pageNum = currentPage + 1;
    const key = getFeedbackKey(bookSlug, pageNum);
    const saved = localStorage.getItem(key);

    const upBtn = document.getElementById('thumbsUp');
    const downBtn = document.getElementById('thumbsDown');
    const commentBox = document.getElementById('feedbackComment');

    if (saved) {
        const feedback = JSON.parse(saved);
        currentRating = feedback.rating;
        upBtn.classList.toggle('selected', feedback.rating === 'up');
        downBtn.classList.toggle('selected', feedback.rating === 'down');
        commentBox.value = feedback.comment || '';
    } else {
        currentRating = null;
        upBtn.classList.remove('selected');
        downBtn.classList.remove('selected');
        commentBox.value = '';
    }
}

function submitToGitHub() {
    const allFeedback = JSON.parse(localStorage.getItem(getAllFeedbackKey()) || '{}');

    if (Object.keys(allFeedback).length === 0) {
        alert('No feedback saved yet! Rate some pages first.');
        return;
    }

    // Build issue body
    let body = `## Book Feedback\n\n`;
    body += `Submitted: ${new Date().toLocaleString()}\n\n`;

    for (const [slug, bookData] of Object.entries(allFeedback)) {
        body += `### ${bookData.title || slug}\n`;
        body += `**Level:** ${bookData.level || 'N/A'}\n\n`;

        const pages = Object.entries(bookData.pages || {}).sort((a, b) => Number(a[0]) - Number(b[0]));

        for (const [pageNum, feedback] of pages) {
            const rating = feedback.rating === 'up' ? '👍' : feedback.rating === 'down' ? '👎' : '—';
            body += `**Page ${pageNum}** ${rating}\n`;
            if (feedback.pageType && feedback.pageType !== 'story') {
                body += `- Type: ${feedback.pageType}\n`;
            }
            if (feedback.comment) {
                body += `- ${feedback.comment}\n`;
            }
            body += `\n`;
        }
    }

    // Get list of book slugs for labels
    const bookSlugs = Object.keys(allFeedback);
    const labels = ['feedback', ...bookSlugs.map(s => `book:${s}`)].join(',');

    // Build GitHub issue URL
    const title = bookSlugs.length === 1
        ? `[Feedback] ${allFeedback[bookSlugs[0]].title || bookSlugs[0]}`
        : `[Feedback] ${bookSlugs.length} books`;

    const issueUrl = `https://github.com/JDerekLomas/funbookies/issues/new?` +
        `title=${encodeURIComponent(title)}&` +
        `body=${encodeURIComponent(body)}&` +
        `labels=${encodeURIComponent(labels)}`;

    window.open(issueUrl, '_blank');

    const status = document.getElementById('feedbackStatus');
    status.textContent = 'Opened GitHub issue!';
    setTimeout(() => { status.textContent = ''; }, 3000);
}

function clearAllFeedback() {
    if (!confirm('Clear all saved feedback? This cannot be undone.')) return;

    // Clear all feedback keys from localStorage
    const allFeedback = JSON.parse(localStorage.getItem(getAllFeedbackKey()) || '{}');
    for (const [slug, bookData] of Object.entries(allFeedback)) {
        for (const pageNum of Object.keys(bookData.pages || {})) {
            localStorage.removeItem(getFeedbackKey(slug, pageNum));
        }
    }
    localStorage.removeItem(getAllFeedbackKey());

    // Reset UI
    loadFeedback();
    updateFeedbackCount();

    const status = document.getElementById('feedbackStatus');
    status.textContent = 'Feedback cleared';
    setTimeout(() => { status.textContent = ''; }, 3000);
}

function updateFeedbackCount() {
    if (!isEditMode()) return;

    const allFeedback = JSON.parse(localStorage.getItem(getAllFeedbackKey()) || '{}');
    let totalPages = 0;
    for (const bookData of Object.values(allFeedback)) {
        totalPages += Object.keys(bookData.pages || {}).length;
    }

    const countEl = document.getElementById('feedbackCount');
    if (totalPages > 0) {
        countEl.textContent = `${totalPages} page${totalPages !== 1 ? 's' : ''} with feedback`;
    } else {
        countEl.textContent = '';
    }
}

function showAllFeedback() {
    const allFeedback = JSON.parse(localStorage.getItem(getAllFeedbackKey()) || '{}');

    if (Object.keys(allFeedback).length === 0) {
        alert('No feedback saved yet! Rate some pages first.');
        return;
    }

    // Build text output
    let text = `# Book Feedback\n`;
    text += `Generated: ${new Date().toLocaleString()}\n\n`;

    for (const [slug, bookData] of Object.entries(allFeedback)) {
        text += `## ${bookData.title || slug}\n`;
        text += `Level: ${bookData.level || 'N/A'}\n\n`;

        const pages = Object.entries(bookData.pages || {}).sort((a, b) => Number(a[0]) - Number(b[0]));

        for (const [pageNum, feedback] of pages) {
            const rating = feedback.rating === 'up' ? '👍 Good' : feedback.rating === 'down' ? '👎 Needs Work' : '— No rating';
            text += `### Page ${pageNum} - ${rating}\n`;
            if (feedback.pageType && feedback.pageType !== 'story') {
                text += `Type: ${feedback.pageType}\n`;
            }
            if (feedback.scene) {
                text += `Prompt: ${feedback.scene.substring(0, 100)}...\n`;
            }
            if (feedback.comment) {
                text += `Comment: ${feedback.comment}\n`;
            }
            text += `\n`;
        }
    }

    // Show modal
    document.getElementById('feedbackModalText').value = text;
    document.getElementById('feedbackModal').style.display = 'flex';
}

function closeFeedbackModal() {
    document.getElementById('feedbackModal').style.display = 'none';
}

function copyFeedback() {
    const textarea = document.getElementById('feedbackModalText');
    textarea.select();
    document.execCommand('copy');

    // Show feedback
    const status = document.getElementById('feedbackStatus');
    status.textContent = 'Copied to clipboard!';
    setTimeout(() => { status.textContent = ''; }, 3000);

    closeFeedbackModal();
}

// Activity recommendations based on level
const levelActivities = {
    'A': [
        { icon: '🔤', name: 'Letter Sounds', desc: 'Practice letter sounds', url: '/activities/early-reader/letter-sounds.html' },
        { icon: '🎯', name: 'First Sounds', desc: 'Identify beginning sounds', url: '/activities/early-reader/first-sounds.html' },
        { icon: '🎵', name: 'Rhyme Time', desc: 'Find rhyming words', url: '/activities/early-reader/rhyme-time.html' },
    ],
    'B1': [
        { icon: '🔊', name: 'Blend It Out', desc: 'Blend sounds into words', url: '/activities/voice-blend.html' },
        { icon: '✂️', name: 'Chop It Up', desc: 'Segment words into sounds', url: '/activities/chop-it-up.html' },
        { icon: '🧱', name: 'Word Builder', desc: 'Build CVC words', url: '/activities/word-builder.html' },
    ],
    'B2': [
        { icon: '🔊', name: 'Blend It Out', desc: 'Practice blending', url: '/activities/voice-blend.html' },
        { icon: '👨‍👩‍👧', name: 'Word Families', desc: 'Practice -at, -ig patterns', url: '/activities/word-families.html' },
        { icon: '🎤', name: 'Read Aloud', desc: 'Practice fluency', url: '/activities/read-aloud.html' },
    ],
    'B3': [
        { icon: '🔊', name: 'Blend It Out (B3)', desc: 'Practice consonant blends', url: '/activities/voice-blend.html' },
        { icon: '💬', name: 'Say the Sound', desc: 'Blend sounds practice', url: '/activities/say-the-sound.html' },
        { icon: '🎤', name: 'Read Aloud', desc: 'Track your fluency', url: '/activities/read-aloud.html' },
    ],
    'B5': [
        { icon: '💬', name: 'Say the Sound (B5)', desc: 'Practice digraphs: sh, ch, th', url: '/activities/say-the-sound.html' },
        { icon: '✂️', name: 'Chop It Up', desc: 'Segment digraph words', url: '/activities/chop-it-up.html' },
        { icon: '🎤', name: 'Read Aloud', desc: 'Build fluency', url: '/activities/read-aloud.html' },
    ],
    'B6': [
        { icon: '🔊', name: 'Blend It Out (B6)', desc: 'Practice silent-e words', url: '/activities/voice-blend.html' },
        { icon: '🎤', name: 'Read Aloud', desc: 'Build fluency', url: '/activities/read-aloud.html' },
        { icon: '👁️', name: 'Sight Words', desc: 'Learn high-frequency words', url: '/activities/sight-words.html' },
    ],
    'B7': [
        { icon: '💬', name: 'Say the Sound (B7)', desc: 'Practice r-controlled vowels', url: '/activities/say-the-sound.html' },
        { icon: '🎤', name: 'Read Aloud', desc: 'Track WCPM', url: '/activities/read-aloud.html' },
        { icon: '✂️', name: 'Chop It Up', desc: 'Segment complex words', url: '/activities/chop-it-up.html' },
    ],
    'B8': [
        { icon: '🔊', name: 'Blend It Out (B8)', desc: 'Practice vowel teams', url: '/activities/voice-blend.html' },
        { icon: '🎤', name: 'Read Aloud', desc: 'Build fluency', url: '/activities/read-aloud.html' },
        { icon: '👁️', name: 'Sight Words', desc: 'Expand vocabulary', url: '/activities/sight-words.html' },
    ],
    'C': [
        { icon: '🎤', name: 'Read Aloud', desc: 'Track fluency progress', url: '/activities/read-aloud.html' },
        { icon: '✂️', name: 'Chop It Up (C)', desc: 'Multi-syllable words', url: '/activities/chop-it-up.html' },
        { icon: '👁️', name: 'Sight Words', desc: 'Advanced words', url: '/activities/sight-words.html' },
    ],
    'D': [
        { icon: '🎤', name: 'Read Aloud', desc: 'Master fluency', url: '/activities/read-aloud.html' },
        { icon: '👁️', name: 'Sight Words', desc: 'Advanced vocabulary', url: '/activities/sight-words.html' },
    ],
};

function getActivitiesForLevel(level) {
    if (!level) return levelActivities['A'];

    // Check exact match first
    if (levelActivities[level]) return levelActivities[level];

    // Fall back to band (first character)
    const band = level.charAt(0);
    if (levelActivities[band]) return levelActivities[band];

    return levelActivities['A'];
}

function showBookComplete() {
    if (!currentBook || isEditMode()) return;

    // Count story pages (exclude front/back matter)
    const storyPages = currentBook.pages.filter(p =>
        !['cover', 'copyright', 'parent_guide', 'level_info', 'wordlist', 'series_info', 'back_cover'].includes(p.type)
    ).length;

    // Update overlay content
    document.getElementById('completeBookTitle').textContent = currentBook.title;
    document.getElementById('completePages').textContent = storyPages;
    document.getElementById('completeLevel').textContent = currentBook.level || 'A1';

    // Get and render activity suggestions
    const activities = getActivitiesForLevel(currentBook.level);
    const activitiesContainer = document.getElementById('practiceActivities');
    activitiesContainer.innerHTML = activities.map(a => `
        <a href="${a.url}" class="practice-link">
            <span class="icon">${a.icon}</span>
            <div class="text">
                <div class="name">${a.name}</div>
                <div class="desc">${a.desc}</div>
            </div>
            <span class="arrow">→</span>
        </a>
    `).join('');

    // Show overlay
    document.getElementById('bookCompleteOverlay').classList.remove('hidden');

    // Save reading history
    saveReadingHistory();

    // Save session state
    saveSessionState();
}

function closeCompleteOverlay() {
    document.getElementById('bookCompleteOverlay').classList.add('hidden');
    // Reset to first page
    currentPage = 0;
    renderPage();
}

async function saveReadingHistory() {
    if (!currentBook || !window.FunBookiesDB) return;

    try {
        // Get current student from session
        const sessionData = JSON.parse(localStorage.getItem('funbookies_session') || '{}');
        const studentId = sessionData.currentStudentId;

        if (studentId) {
            await window.FunBookiesDB.saveReadingHistory({
                studentId: studentId,
                bookSlug: bookSlug,
                bookTitle: currentBook.title,
                level: currentBook.level,
                coverImage: getCoverImagePath(),
                pagesRead: currentBook.pages.length,
                completedAt: new Date().toISOString()
            });
        }
    } catch (e) {
        console.error('Failed to save reading history:', e);
    }
}

function saveSessionState() {
    const session = JSON.parse(localStorage.getItem('funbookies_session') || '{}');
    session.lastActivity = {
        type: 'book',
        bookSlug: bookSlug,
        bookTitle: currentBook.title,
        level: currentBook.level,
        timestamp: new Date().toISOString()
    };
    localStorage.setItem('funbookies_session', JSON.stringify(session));
}

// Modify nextPage to detect book completion
const originalNextPage = function() {
    if (currentBook && currentPage < currentBook.pages.length - 1) {
        const bookPage = document.getElementById('bookPage');
        bookPage.classList.add('slide-left');
        setTimeout(() => {
            currentPage++;
            renderPage();
            bookPage.classList.remove('slide-left');
            bookPage.classList.add('fade-in');
            setTimeout(() => bookPage.classList.remove('fade-in'), 300);

            // Check if we just reached the last page
            if (currentPage === currentBook.pages.length - 1) {
                // Show completion overlay after a brief delay
                setTimeout(() => showBookComplete(), 1500);
            }
        }, 150);
    }
};

// Load book on page load
loadBook();
