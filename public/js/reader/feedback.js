import { currentBook, bookSlug, currentPage, isEditMode } from './state.js';

// Feedback state
let currentRating = null;

function getFeedbackKey(bookSlug, pageNum) {
    return `feedback_${bookSlug}_page${pageNum}`;
}

function getAllFeedbackKey() {
    return 'funbookies_all_feedback';
}

export function setRating(rating) {
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

export function saveFeedback() {
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

export function loadFeedback() {
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

export function submitToGitHub() {
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

export function clearAllFeedback() {
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

export function updateFeedbackCount() {
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

export function showAllFeedback() {
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

export function closeFeedbackModal() {
    document.getElementById('feedbackModal').style.display = 'none';
}

export function copyFeedback() {
    const textarea = document.getElementById('feedbackModalText');
    textarea.select();
    document.execCommand('copy');

    // Show feedback
    const status = document.getElementById('feedbackStatus');
    status.textContent = 'Copied to clipboard!';
    setTimeout(() => { status.textContent = ''; }, 3000);

    closeFeedbackModal();
}
