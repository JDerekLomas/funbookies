import { currentBook, bookSlug } from './state.js';

// Reference image state
export let selectedReference = null;
export let selectedReferences = []; // For multi-ref support
export let uploadedReferenceData = null;
let loadingReferencesFor = null; // Guard against concurrent loads

const MAX_REFS = 3; // wan2.6 limit

export function getSelectedReference() { return selectedReference; }
export function getSelectedReferences() { return selectedReferences; }
export function getUploadedReferenceData() { return uploadedReferenceData; }

export async function loadReferenceVersions() {
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

    // Also check for new-style multi-refs (style_guide, opening_scenes, closing_scenes)
    const newStyleRefs = [
        { key: 'style_guide', path: `/books/references/${slug}_multi/style_guide.png`, label: 'Style Guide' },
        { key: 'opening_scenes', path: `/books/references/${slug}_multi/opening_scenes.png`, label: 'Opening Scenes' },
        { key: 'closing_scenes', path: `/books/references/${slug}_multi/closing_scenes.png`, label: 'Closing Scenes' }
    ];

    // Check if new-style refs exist
    let hasNewStyleRefs = false;
    const existingNewRefs = [];
    for (const ref of newStyleRefs) {
        try {
            const resp = await fetch(ref.path, { method: 'HEAD' });
            if (resp.ok) {
                existingNewRefs.push(ref);
                hasNewStyleRefs = true;
            }
        } catch (e) {
            // Not found
        }
    }

    if (multiRefs && multiRefs.references) {
        // Display multi-ref images from manifest
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
                <button class="zoom-btn" onclick="event.stopPropagation(); window._openReferenceLightbox('${webPath}')">🔍</button>
                <img src="${webPath}" alt="${label}" onerror="this.parentElement.style.display='none'">
                <span class="version-label">${label}</span>
            `;
            div.onclick = () => toggleMultiReference(div);
            container.appendChild(div);
            if (isSelected) {
                selectedReferences.push(webPath);
            }
        });

        // Set selectedReference to first one for backwards compat
        selectedReference = selectedReferences[0] || null;
    } else if (hasNewStyleRefs) {
        // Display new-style multi-refs (no manifest needed)
        selectedReferences = [];

        existingNewRefs.forEach((ref, index) => {
            const div = document.createElement('div');
            div.className = 'reference-version active'; // Select all by default
            div.dataset.refKey = ref.key;
            div.dataset.refPath = ref.path;
            div.title = 'Click to select, double-click to view full size';
            div.innerHTML = `
                <button class="zoom-btn" onclick="event.stopPropagation(); window._openReferenceLightbox('${ref.path}')">🔍</button>
                <img src="${ref.path}" alt="${ref.label}" onerror="this.parentElement.style.display='none'">
                <span class="version-label">${ref.label}</span>
            `;
            div.onclick = () => toggleMultiReference(div);
            container.appendChild(div);
            selectedReferences.push(ref.path);
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
            div.title = 'Click to select';
            div.innerHTML = `
                <button class="zoom-btn" onclick="event.stopPropagation(); window._openReferenceLightbox('${v.path}')">🔍</button>
                <img src="${v.path}" alt="Reference ${v.label}" onerror="this.parentElement.style.display='none'">
                <span class="version-label">${v.label}${v.version === activeVersion ? ' ✓' : ''}</span>
            `;
            div.onclick = () => selectReference(v.path, v.version, div);
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

export function toggleMultiReference(element) {
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

export function selectReference(path, version, element) {
    selectedReference = path;
    uploadedReferenceData = null;

    // Update UI
    document.querySelectorAll('.reference-version').forEach(el => el.classList.remove('active'));
    element.classList.add('active');
}

export function handleReferenceUpload(event) {
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
        div.dataset.imgSrc = uploadedReferenceData;
        const zoomBtn = document.createElement('button');
        zoomBtn.className = 'zoom-btn';
        zoomBtn.textContent = '🔍';
        zoomBtn.onclick = (e) => { e.stopPropagation(); openReferenceLightbox(uploadedReferenceData); };

        const img = document.createElement('img');
        img.src = uploadedReferenceData;
        img.alt = 'Custom reference';

        const label = document.createElement('span');
        label.className = 'version-label';
        label.textContent = 'custom';

        div.appendChild(zoomBtn);
        div.appendChild(img);
        div.appendChild(label);
        div.onclick = () => selectReference(null, 'custom', div);
        container.insertBefore(div, uploadBtn);

        // Select this one
        document.querySelectorAll('.reference-version').forEach(el => el.classList.remove('active'));
        div.classList.add('active');
        selectedReference = null; // null means use uploaded data
    };
    reader.readAsDataURL(file);
}

// Lightbox functions
export function openReferenceLightbox(imagePath) {
    const lightbox = document.getElementById('referenceLightbox');
    const lightboxImg = document.getElementById('lightboxImage');
    if (lightbox && lightboxImg) {
        lightboxImg.src = imagePath;
        lightbox.style.display = 'flex';
        // Close on Escape key
        document.addEventListener('keydown', handleLightboxEscape);
    }
}

export function closeReferenceLightbox() {
    const lightbox = document.getElementById('referenceLightbox');
    if (lightbox) {
        lightbox.style.display = 'none';
        document.removeEventListener('keydown', handleLightboxEscape);
    }
}

function handleLightboxEscape(e) {
    if (e.key === 'Escape') {
        closeReferenceLightbox();
    }
}

// Expose lightbox functions globally for onclick handlers
window._openReferenceLightbox = openReferenceLightbox;
window.closeReferenceLightbox = closeReferenceLightbox;
