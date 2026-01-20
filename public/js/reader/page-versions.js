import { currentBook, currentPage } from './state.js';

export function loadPageVersions(setImageAsCurrent) {
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
        div.onclick = () => selectPageVersion(currentImage, div, setImageAsCurrent);
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
        div.onclick = () => selectPageVersion(v.url, div, setImageAsCurrent);
        container.appendChild(div);
    });
}

async function selectPageVersion(url, element, setImageAsCurrent) {
    if (!currentBook || currentPage < 0) return;

    // Update UI immediately
    document.querySelectorAll('.page-version').forEach(el => el.classList.remove('active'));
    element.classList.add('active');

    // Use shared function to set as current
    await setImageAsCurrent(url);
}

export function getNextVersionNumber() {
    if (!currentBook || currentPage < 0) return 1;
    const page = currentBook.pages[currentPage];
    if (!page) return 1;

    const versions = page.image_versions || [];
    return versions.length + 1;
}
