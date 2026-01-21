import { currentBook, bookSlug, currentPage, setCurrentPage, isEditMode, isGalleryMode, updateUrl, setMode, updateModeButtons, currentMode } from './state.js';
import { getImagePath, getCoverImagePath, getReferenceImagePath } from './image-paths.js';
import { updateNavigationState, preloadAdjacentPages } from './navigation.js';
import { loadReferenceVersions } from './references.js';
import { loadPageVersions } from './page-versions.js';
import { loadFeedback, updateFeedbackCount } from './feedback.js';

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

// Generate rich gold renaissance tapestry pattern
function generateCoverPattern(seed = 0) {
    // Rich gold/burgundy renaissance palette
    const baseGold = '#8B6914';
    const lightGold = '#C9A227';
    const darkGold = '#5C4510';

    // Damask/floral motif variations
    const motifs = [
        `<g id="motif">
            <path d="M20 5 Q25 10 20 15 Q15 10 20 5" fill="${lightGold}" opacity="0.6"/>
            <path d="M20 5 Q25 10 20 15 Q15 10 20 5" fill="none" stroke="${darkGold}" stroke-width="0.5"/>
            <circle cx="20" cy="10" r="2" fill="${lightGold}" opacity="0.8"/>
            <path d="M15 10 Q20 5 25 10" fill="none" stroke="${lightGold}" stroke-width="1" opacity="0.5"/>
            <path d="M15 10 Q20 15 25 10" fill="none" stroke="${lightGold}" stroke-width="1" opacity="0.5"/>
        </g>`,
        `<g id="motif">
            <path d="M12 10 Q20 2 28 10 Q20 18 12 10" fill="${lightGold}" opacity="0.4"/>
            <circle cx="20" cy="10" r="3" fill="${lightGold}" opacity="0.6"/>
            <path d="M17 10 Q20 7 23 10 Q20 13 17 10" fill="${darkGold}" opacity="0.5"/>
            <path d="M10 10 L14 10 M26 10 L30 10" stroke="${lightGold}" stroke-width="1" opacity="0.4"/>
        </g>`,
        `<g id="motif">
            <circle cx="20" cy="10" r="6" fill="none" stroke="${lightGold}" stroke-width="1" opacity="0.5"/>
            <circle cx="20" cy="10" r="3" fill="${lightGold}" opacity="0.5"/>
            <path d="M20 4 L20 6 M20 14 L20 16 M14 10 L16 10 M24 10 L26 10" stroke="${lightGold}" stroke-width="1.5" opacity="0.6"/>
            <path d="M15 5 L17 7 M23 7 L25 5 M15 15 L17 13 M23 13 L25 15" stroke="${lightGold}" stroke-width="1" opacity="0.4"/>
        </g>`,
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
                    <rect width="40" height="20" fill="url(#noise)" opacity="0.1"/>
                    ${motif}
                </pattern>
                <filter id="noise">
                    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" result="noise"/>
                    <feColorMatrix type="saturate" values="0"/>
                </filter>
                <linearGradient id="goldSheen" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:${lightGold};stop-opacity:0.2"/>
                    <stop offset="50%" style="stop-color:${darkGold};stop-opacity:0.1"/>
                    <stop offset="100%" style="stop-color:${lightGold};stop-opacity:0.2"/>
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#tapestryPattern)"/>
            <rect width="100%" height="100%" fill="url(#goldSheen)"/>
            <line x1="0" y1="2" x2="100%" y2="2" stroke="${lightGold}" stroke-width="1" opacity="0.6"/>
            <line x1="0" y1="98%" x2="100%" y2="98%" stroke="${lightGold}" stroke-width="1" opacity="0.6"/>
        </svg>
    `;
}

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

export function initEditMode() {
    const slug = currentBook?._slug || bookSlug;

    // Set initial edit info
    if (isEditMode() && currentBook) {
        document.getElementById('infoSlug').textContent = slug;
        document.getElementById('infoLevel').textContent = currentBook.level || 'N/A';
    }
}

export function updateEditInfo(setImageAsCurrent) {
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
    loadPageVersions(setImageAsCurrent);

    // Load feedback for current page
    loadFeedback();
    updateFeedbackCount();
}

export function renderPage(setImageAsCurrent) {
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
        updateEditInfo(setImageAsCurrent);
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
        updateEditInfo(setImageAsCurrent);
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
            renderSyntheticCover(bookPage, page, colorDisplay);
            break;
        case 'copyright':
            renderCopyright(bookPage);
            break;
        case 'parent_guide':
            renderParentGuide(bookPage);
            break;
        case 'level_info':
            renderLevelInfo(bookPage, color, colorDisplay);
            break;
        case 'wordlist':
            renderWordlist(bookPage);
            break;
        case 'wordsearch':
            renderWordsearch(bookPage, page);
            break;
        case 'end':
            renderEndPage(bookPage, page);
            break;
        case 'series_info':
            renderSeriesInfo(bookPage, color);
            break;
        case 'back_cover':
            renderBackCover(bookPage, page, color, colorDisplay);
            break;
        case 'cover':
            renderCover(bookPage, page, colorDisplay);
            break;
        default:
            renderStoryPage(bookPage, page);
    }

    // Update navigation state
    updateNavigationState();

    // Update edit mode info
    updateEditInfo(setImageAsCurrent);

    // Preload adjacent pages for faster navigation
    preloadAdjacentPages();
}

function renderSyntheticCover(bookPage, page, colorDisplay) {
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
}

function renderCopyright(bookPage) {
    const copyrightYear = currentBook.created ? currentBook.created.split('-')[0] : new Date().getFullYear();
    const slug = currentBook.slug || currentBook.id || '';
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
            ${slug ? `<div class="book-id">${slug}</div>` : ''}
        </div>
    `;
}

function renderParentGuide(bookPage) {
    const tips = currentBook.parent_tips;
    if (tips && (tips.before_reading || tips.during_reading || tips.after_reading)) {
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
}

function renderLevelInfo(bookPage, color, colorDisplay) {
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
}

function renderWordlist(bookPage) {
    const wl = currentBook.word_list || {};
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
}

function renderWordsearch(bookPage, page) {
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
}

function renderEndPage(bookPage, page) {
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
                <button class="end-btn" onclick="window._goToPage(0)">Read Again</button>
                <button class="end-btn primary" onclick="window.location.href='/books/'">More Books</button>
            </div>
        </div>
    `;
}

function renderSeriesInfo(bookPage, color) {
    const levels = ['pink', 'yellow', 'orange', 'red', 'purple', 'blue', 'green', 'gold'];
    const levelNames = ['Pink', 'Yellow', 'Orange', 'Red', 'Purple', 'Blue', 'Green', 'Gold'];
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
}

function renderBackCover(bookPage, page, color, colorDisplay) {
    const backImgPath = page.image ? getImagePath(page) : getCoverImagePath();
    const backBlurb = page.text || currentBook.summary ||
        (currentBook.story_bible?.premise ? currentBook.story_bible.premise.split('.')[0] + '.' : 'A fun story for beginning readers!');
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
}

function renderCover(bookPage, page, colorDisplay) {
    const coverImgPath = getImagePath(page);
    const coverScene = page.scene || currentBook.summary || '';
    const coverPlaceholderId = `cover-placeholder`;
    const coverTitle = page.text || currentBook.title || 'Untitled';
    const authorName = currentBook.author || '';
    bookPage.innerHTML = `
        <div class="page-cover">
            <div class="cover-corner-tab">
                <div class="corner-ribbon">
                    <span class="brand-name">FunBookies</span>
                    <span class="level-text">${colorDisplay} Level</span>
                </div>
            </div>
            <div class="cover-logo">
                <img src="/images/funbookies_icon.png" alt="FunBookies">
            </div>
            <div class="cover-image">
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
}

function renderStoryPage(bookPage, page) {
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

// Gallery functions
export function goToPage(pageIndex, renderPageFn) {
    // From gallery, go to read mode; otherwise stay in current mode
    if (isGalleryMode()) {
        // Direct mode change without triggering setMode's full logic
        document.body.classList.remove('mode-gallery', 'gallery-mode');
        document.body.classList.add('mode-read');
        updateModeButtons();
    }

    setCurrentPage(pageIndex);
    renderPageFn();
    updateUrl();
}

export function goToPageEdit(pageIndex, setModeFn) {
    // Switch to edit mode and go to page
    setCurrentPage(pageIndex);
    setModeFn('edit');
}

export function renderGallery(regenerateImageFn, goToPageFn, goToPageEditFn, generatePageFromGalleryFn) {
    if (!currentBook) return;

    const grid = document.getElementById('galleryGrid');
    const generateAllBtn = document.getElementById('generateAllBtn');
    const slug = currentBook._slug || bookSlug;

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
            <div class="gallery-card" id="${cardId}" data-page="${index}" onclick="window._goToPage(${index})">
                <div class="gallery-card-image">
                    <img src="${imagePath}"
                         alt="Page ${pageNum}"
                         onload="window._markCardHasImage('${cardId}')"
                         onerror="window._markCardNoImage('${cardId}')">
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
                    <button class="edit-btn" onclick="event.stopPropagation(); window._goToPageEdit(${index})">Edit</button>
                    <button class="generate-btn" onclick="event.stopPropagation(); window._generatePageFromGallery(${index})">Generate</button>
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

export function markCardHasImage(cardId) {
    const card = document.getElementById(cardId);
    if (card) {
        card.classList.add('has-image');
        card.classList.remove('no-image');
    }
    updateGalleryStats();
}

export function markCardNoImage(cardId) {
    const card = document.getElementById(cardId);
    if (card) {
        card.classList.add('no-image');
        card.classList.remove('has-image');
    }
    updateGalleryStats();
}

export function updateGalleryStats() {
    const hasImage = document.querySelectorAll('.gallery-card.has-image').length;
    const noImage = document.querySelectorAll('.gallery-card.no-image').length;
    const stats = document.getElementById('galleryStats');
    if (stats) {
        stats.innerHTML = `
            <span class="has-image">${hasImage} with images</span>
            <span class="no-image">${noImage} need images</span>
        `;
    }
}
