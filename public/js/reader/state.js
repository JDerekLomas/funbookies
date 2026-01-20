// Global state
export let currentBook = null;
export let currentPage = 0;
export let bookSlug = '';
export let currentMode = 'read'; // 'read' | 'edit' | 'gallery'

// State setters
export function setCurrentBook(book) { currentBook = book; }
export function setCurrentPage(page) { currentPage = page; }
export function setBookSlug(slug) { bookSlug = slug; }

// Get URL params
const urlParams = new URLSearchParams(window.location.search);
export const bookId = urlParams.get('book');
export const modeParam = urlParams.get('mode');
export const pageParam = urlParams.get('page');
export const actionParam = urlParams.get('action');

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
export function isEditMode() { return currentMode === 'edit'; }
export function isGalleryMode() { return currentMode === 'gallery'; }
export function isReadMode() { return currentMode === 'read'; }

// Unified URL update helper - keeps URL in sync with state
export function updateUrl(options = {}) {
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

// Update mode button states
export function updateModeButtons() {
    const readBtn = document.getElementById('readModeBtn');
    const editBtn = document.getElementById('editModeBtn');
    const galleryBtn = document.getElementById('galleryModeBtn');

    if (readBtn) readBtn.classList.toggle('active', currentMode === 'read');
    if (editBtn) editBtn.classList.toggle('active', currentMode === 'edit');
    if (galleryBtn) galleryBtn.classList.toggle('active', currentMode === 'gallery');
}

// Set mode (read, edit, or gallery)
// Note: renderPage and renderGallery are passed in to avoid circular dependency
export function setMode(newMode, { initEditMode, renderPage, renderGallery }) {
    if (currentMode === newMode) return;

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

// Apply initial mode classes
document.body.classList.add(`mode-${currentMode}`);
if (currentMode === 'edit') {
    document.body.classList.add('edit-mode');
} else if (currentMode === 'gallery') {
    document.body.classList.add('gallery-mode');
}
