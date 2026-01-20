import { currentBook, bookSlug, currentPage } from './state.js';

export async function saveTextToBook(renderPage) {
    const text = document.getElementById('textEditor').value;
    const status = document.getElementById('textStatus');

    if (currentPage < 0) {
        status.className = 'text-status error';
        status.textContent = 'Cannot edit text on this page type';
        return;
    }

    const slug = currentBook?._slug || bookSlug;
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

export async function savePromptToBook() {
    const prompt = document.getElementById('promptEditor').value;
    const status = document.getElementById('promptStatus');

    if (!prompt) {
        status.className = 'prompt-status error';
        status.textContent = 'No prompt to save';
        return;
    }

    const slug = currentBook?._slug || bookSlug;
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
