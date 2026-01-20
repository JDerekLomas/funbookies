import { currentBook, currentPage, setCurrentPage, isEditMode, updateUrl } from './state.js';
import { getImagePathForPage, getCoverImagePath } from './image-paths.js';

// Image preloading cache
const imageCache = new Map();

function preloadImage(src) {
    if (!src || imageCache.has(src)) return;
    const img = new Image();
    img.src = src;
    imageCache.set(src, img);
}

export function preloadAdjacentPages() {
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

export function updateNavigationState() {
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

export function prevPage(renderPage) {
    // In edit mode, allow going to page -1 (reference)
    const minPage = isEditMode() ? -2 : 0;
    if (currentPage > minPage) {
        const bookPage = document.getElementById('bookPage');
        bookPage.classList.add('slide-right');
        setTimeout(() => {
            setCurrentPage(currentPage - 1);
            renderPage();
            updateUrl();
            bookPage.classList.remove('slide-right');
            bookPage.classList.add('fade-in');
            setTimeout(() => bookPage.classList.remove('fade-in'), 300);
        }, 150);
    }
}

export function nextPage(renderPage, showBookComplete) {
    if (currentBook && currentPage < currentBook.pages.length - 1) {
        const bookPage = document.getElementById('bookPage');
        bookPage.classList.add('slide-left');
        setTimeout(() => {
            setCurrentPage(currentPage + 1);
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

// Setup keyboard navigation
export function setupKeyboardNavigation(prevPageFn, nextPageFn) {
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

        if (e.key === 'ArrowLeft') prevPageFn();
        if (e.key === 'ArrowRight') nextPageFn();
        if (e.key === 'Escape') window.location.href = '/books/';
    });
}

// Setup touch swipe navigation
export function setupTouchNavigation(prevPageFn, nextPageFn) {
    let touchStartX = 0;

    document.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
    });

    document.addEventListener('touchend', (e) => {
        const touchEndX = e.changedTouches[0].clientX;
        const diff = touchStartX - touchEndX;

        if (Math.abs(diff) > 50) {
            if (diff > 0) nextPageFn();
            else prevPageFn();
        }
    });
}
