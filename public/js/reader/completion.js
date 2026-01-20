import { currentBook, bookSlug, isEditMode } from './state.js';
import { getCoverImagePath } from './image-paths.js';

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

export function getActivitiesForLevel(level) {
    if (!level) return levelActivities['A'];

    // Check exact match first
    if (levelActivities[level]) return levelActivities[level];

    // Fall back to band (first character)
    const band = level.charAt(0);
    if (levelActivities[band]) return levelActivities[band];

    return levelActivities['A'];
}

export function showBookComplete(renderPage) {
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

export function closeCompleteOverlay(setCurrentPage, renderPage) {
    document.getElementById('bookCompleteOverlay').classList.add('hidden');
    // Reset to first page
    setCurrentPage(0);
    renderPage();
}

export async function saveReadingHistory() {
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

export function saveSessionState() {
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
