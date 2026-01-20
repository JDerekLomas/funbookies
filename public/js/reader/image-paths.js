import { currentBook, bookSlug, currentPage } from './state.js';

// Legacy book registry for old books with custom image paths
export const legacyImagePaths = {
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

export function getCoverImagePath() {
    const slug = currentBook?._slug || bookSlug;
    return `/images/covers/${slug}.png`;
}

export function getReferenceImagePath() {
    const slug = currentBook?._slug || bookSlug;
    return `/books/references/${slug}_reference.png`;
}

export function getImagePath(page) {
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
    const slug = currentBook?._slug || bookSlug;

    // Check if this is a legacy book with custom image paths
    if (legacyImagePaths[slug]) {
        const info = legacyImagePaths[slug];
        return `/books/${info.imageFolder}/${info.imagePrefix}${pageNum}.png`;
    }

    // Default path for new curriculum books: /books/images/{slug}_page{nn}.png
    return `/books/images/${slug}_page${pageNum}.png`;
}

export function getImagePathForPage(page, pageIdx) {
    const slug = currentBook?._slug || bookSlug;

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
    if (legacyImagePaths[slug]) {
        const info = legacyImagePaths[slug];
        return `/books/${info.imageFolder}/${info.imagePrefix}${pageNum}.png`;
    }
    return `/books/images/${slug}_page${pageNum}.png`;
}
