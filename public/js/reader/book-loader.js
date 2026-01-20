import {
    currentBook, setCurrentBook,
    currentPage, setCurrentPage,
    bookSlug, setBookSlug,
    bookId, pageParam, actionParam,
    isEditMode, isGalleryMode,
    updateModeButtons, currentMode
} from './state.js';

// Load book and initialize the reader
// Takes callbacks for rendering to avoid circular dependencies
export async function loadBook({ initEditMode, renderPage, renderGallery, regenerateImage }) {
    if (!bookId) {
        document.getElementById('bookPage').innerHTML = `
            <div class="loading">No book specified. <a href="/books/" style="color: var(--color-sage);">Browse books</a></div>
        `;
        return;
    }

    setBookSlug(bookId);

    try {
        // Try API first, then fall back to static JSON file
        let res = await fetch(`/api/get-book?slug=${bookId}`);
        let source = 'api';
        let book;

        if (!res.ok) {
            // Fallback to static JSON file (for local dev without API)
            res = await fetch(`/books/${bookId}.json`);
            source = 'static';
            if (!res.ok) throw new Error('Failed to load book');
            book = await res.json();
        } else {
            const data = await res.json();
            book = data.book;
        }

        console.log(`Book loaded from ${source}`);
        book._slug = bookId;
        setCurrentBook(book);

        // Use page from URL param, or default (edit mode: -2, otherwise: 0)
        if (pageParam !== null) {
            setCurrentPage(parseInt(pageParam, 10));
        } else {
            setCurrentPage(isEditMode() ? -2 : 0);
        }

        document.getElementById('bookTitle').textContent = book.title;
        const modeSuffix = currentMode === 'edit' ? ' (Edit)' : currentMode === 'gallery' ? ' (Gallery)' : '';
        document.title = `${book.title} - FunBookies${modeSuffix}`;

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
