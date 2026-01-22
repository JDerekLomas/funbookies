// ===================
// STATE MANAGEMENT
// ===================

const STATE_KEY_PREFIX = 'wizard_state_';

// Story ideas loaded from JSON
let storyIdeasData = null;
let storyIdeasVisible = true;
let selectedIdeaIndex = null;

// Story types and art styles loaded from JSON
let storyTypesData = null;
let artStylesData = null;

let state = {
    slug: null,
    currentPhase: 1,
    phaseStatus: { 1: 'in_progress', 2: 'pending', 3: 'pending', 4: 'pending', 5: 'pending', 6: 'pending' },
    outline: null,  // Beat-by-beat story outline from Phase 1
    book: null,
    referenceImage: null,
    // Prompt tracking - stores custom/edited prompts
    prompts: {
        story: null,           // Custom story prompt (null = use default)
        styleGuide: null,      // Custom style guide prompt
        openingScenes: null,   // Custom opening scenes prompt
        closingScenes: null    // Custom closing scenes prompt
    },
    // Metaprompts - templates with placeholders that generate final prompts
    // Placeholders: {title}, {name}, {description}, {traits}, {setting}
    metaprompts: {
        reference: null,       // Reference sheet metaprompt (null = use default)
        openingScenes: null,   // Opening scenes metaprompt
        closingScenes: null    // Closing scenes metaprompt
    },
    // Multi-ref support (3-ref cascade)
    refStrategy: 'single', // 'single' or 'multi'
    multiRefs: {
        styleGuide: null,    // 9-panel (nano-banana T2I)
        openingScenes: null, // First half pages (wan 2.6 I2I)
        closingScenes: null  // Second half pages (wan 2.6 I2I)
    },
    pendingTasks: [],
    checkpointApprovals: {},
    formData: {
        level: 'B1',
        concept: '',
        setting: '',
        words: [],
        storyType: 'problem-solution',
        artStyle: 'warm-watercolor'
    }
};

// ===================
// INITIALIZATION
// ===================

async function init() {
    // Load story ideas, story types, and art styles
    await Promise.all([
        loadStoryIdeas(),
        loadStoryTypes(),
        loadArtStyles()
    ]);

    // Check URL params for existing book
    const params = new URLSearchParams(window.location.search);
    const slug = params.get('slug');
    const phase = parseInt(params.get('phase')) || null;
    const refresh = params.get('refresh') === 'true';

    if (slug) {
        // Always try Supabase first (source of truth for cross-device sync)
        // Use localStorage only as fallback if Supabase fails
        if (!refresh) {
            loadState(slug); // Load localStorage as initial state
        }

        // Always fetch from Supabase to get latest state
        await loadFromSupabase(slug);

        if (state.book) {
            // Use URL phase param if provided, otherwise use saved phase
            const targetPhase = phase || state.currentPhase;
            goToPhase(targetPhase);
        }
    }

    setupEventListeners();
    updateUI();

    // Render initial story ideas for default level
    renderStoryIdeas();
}

function setupEventListeners() {
    // Word input
    document.getElementById('wordInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const word = e.target.value.trim().toLowerCase();
            if (word && !state.formData.words.includes(word)) {
                state.formData.words.push(word);
                renderWordTags();
            }
            e.target.value = '';
        }
    });

    // Level select
    document.getElementById('levelSelect').addEventListener('change', (e) => {
        state.formData.level = e.target.value;
        selectedIdeaIndex = null; // Clear selection when level changes
        renderStoryIdeas();
    });

    // Story type and art style cards are handled via onclick in the rendered HTML

    // Stepper navigation - click on completed/active steps to navigate
    document.getElementById('stepper').addEventListener('click', (e) => {
        const step = e.target.closest('.step');
        if (step && step.classList.contains('clickable')) {
            const phase = parseInt(step.dataset.phase);
            if (phase && phase !== state.currentPhase) {
                goToPhase(phase);
            }
        }
    });
}

// ===================
// STATE PERSISTENCE
// ===================

function saveState() {
    if (state.slug) {
        try {
            localStorage.setItem(STATE_KEY_PREFIX + state.slug, JSON.stringify(state));
        } catch (e) {
            // localStorage quota exceeded - clear old wizard states and try again
            console.warn('localStorage quota exceeded, clearing old wizard states');
            clearOldWizardStates();
            try {
                localStorage.setItem(STATE_KEY_PREFIX + state.slug, JSON.stringify(state));
            } catch (e2) {
                console.error('Still cannot save to localStorage, relying on Supabase');
            }
        }
        updateURL();
    }
}

function clearOldWizardStates() {
    // Remove all wizard states except current one
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(STATE_KEY_PREFIX) && key !== STATE_KEY_PREFIX + state.slug) {
            keysToRemove.push(key);
        }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key));
}

// Save book to Supabase (called after each phase)
async function saveToSupabase() {
    if (!state.slug || !state.book) return;

    try {
        // Save full wizard state alongside book data
        const bookData = {
            ...state.book,
            slug: state.slug,
            referenceImage: state.referenceImage,
            wizardPhase: state.currentPhase,
            updatedAt: new Date().toISOString(),
            // Wizard state - stored with book for cross-device sync
            wizardState: {
                phaseStatus: state.phaseStatus,
                checkpointApprovals: state.checkpointApprovals,
                prompts: state.prompts,
                metaprompts: state.metaprompts,
                refStrategy: state.refStrategy,
                multiRefs: state.multiRefs,
                outline: state.outline,
                formData: state.formData
            }
        };

        const response = await fetch('/api/save-book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                slug: state.slug,
                fullBook: bookData
            })
        });

        if (!response.ok) {
            console.warn('Failed to save to Supabase:', await response.text());
        } else {
            console.log('Book + wizard state saved to Supabase (phase ' + state.currentPhase + ')');
        }
    } catch (error) {
        console.warn('Supabase save error:', error);
    }
}

// Load book from Supabase (fallback when localStorage is empty)
async function loadFromSupabase(slug) {
    try {
        const response = await fetch(`/api/get-book?slug=${slug}`);
        if (!response.ok) {
            console.log('Book not found in Supabase:', slug);
            return;
        }

        const result = await response.json();
        if (result.book) {
            state.slug = slug;
            state.book = result.book;
            state.referenceImage = result.book.referenceImage;
            state.currentPhase = result.book.wizardPhase || 1;

            // Load multiRefs from book JSON if present (CLI-generated)
            if (result.book.multiRefs) {
                state.multiRefs = result.book.multiRefs;
                state.refStrategy = 'multi';
                console.log('Loaded multiRefs from book JSON:', state.multiRefs);
            }

            // Restore full wizard state if available
            if (result.book.wizardState) {
                const ws = result.book.wizardState;
                state.phaseStatus = ws.phaseStatus || state.phaseStatus;
                state.checkpointApprovals = ws.checkpointApprovals || {};
                state.prompts = ws.prompts || state.prompts;
                state.metaprompts = ws.metaprompts || state.metaprompts;
                state.refStrategy = ws.refStrategy || 'single';
                state.multiRefs = ws.multiRefs || state.multiRefs;
                state.outline = ws.outline || null;
                state.formData = ws.formData || state.formData;
                console.log('Restored full wizard state from Supabase');
            } else {
                // Fallback: Mark completed phases based on wizardPhase
                for (let i = 1; i < state.currentPhase; i++) {
                    state.phaseStatus[i] = 'complete';
                }
            }
            state.phaseStatus[state.currentPhase] = 'in_progress';

            // Also save to localStorage for future loads
            saveState();
            console.log('Loaded book from Supabase:', slug);
        }
    } catch (error) {
        console.warn('Failed to load from Supabase:', error);
    }
}

function loadState(slug) {
    const saved = localStorage.getItem(STATE_KEY_PREFIX + slug);
    if (saved) {
        state = JSON.parse(saved);
    }
}

function updateURL() {
    const url = new URL(window.location);
    if (state.slug) {
        url.searchParams.set('slug', state.slug);
    }
    url.searchParams.set('phase', state.currentPhase);
    window.history.replaceState({}, '', url);
}

function generateSlug(title) {
    return title.toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/(^-|-$)/g, '');
}

// ===================
// UI UPDATES
// ===================

function updateUI() {
    updateStepper();
    renderWordTags();

    // Show book info if we have a slug
    if (state.slug) {
        document.getElementById('bookInfo').classList.remove('hidden');
        document.getElementById('bookSlug').textContent = state.slug;
    } else {
        document.getElementById('bookInfo').classList.add('hidden');
    }
}

function updateStepper() {
    document.querySelectorAll('.step').forEach(step => {
        const phase = parseInt(step.dataset.phase);
        step.classList.remove('active', 'completed', 'clickable');

        if (phase === state.currentPhase) {
            step.classList.add('active', 'clickable');
        } else if (state.phaseStatus[phase] === 'complete') {
            step.classList.add('completed', 'clickable');
            step.querySelector('.step-indicator').innerHTML = '&#10003;';
        } else if (state.phaseStatus[phase] === 'in_progress') {
            // Allow clicking on phases that have been started (even if not complete)
            step.classList.add('clickable');
            step.querySelector('.step-indicator').textContent = phase;
        } else {
            // Reset indicator number if not started
            step.querySelector('.step-indicator').textContent = phase;
        }
    });
}

async function goToPhase(phase) {
    // Hide all phases
    document.querySelectorAll('.phase-content').forEach(el => el.classList.remove('active'));

    // Show target phase
    document.getElementById(`phase${phase}`).classList.add('active');
    state.currentPhase = phase;
    state.phaseStatus[phase] = 'in_progress';

    updateStepper();
    updateURL();

    // Render phase-specific content
    if (phase === 2 && state.outline) {
        renderOutlinePhase();
    } else if (phase === 3 && state.book) {
        renderPhase2Content();
    } else if (phase === 4 && state.book) {
        await renderReferencePhase();
    } else if (phase === 5 && state.book) {
        renderPageImagesGrid();
    } else if (phase === 6 && state.book) {
        renderReviewPhase();
    }
}

function renderWordTags() {
    const container = document.getElementById('wordTags');
    container.innerHTML = state.formData.words.map(w =>
        `<span class="word-tag">${w}<button onclick="removeWord('${w}')">&times;</button></span>`
    ).join('');
}

function removeWord(word) {
    state.formData.words = state.formData.words.filter(w => w !== word);
    renderWordTags();
}

// ===================
// STORY IDEAS
// ===================

async function loadStoryIdeas() {
    try {
        const response = await fetch('/data/story-ideas.json');
        if (response.ok) {
            storyIdeasData = await response.json();
            console.log('Loaded story ideas:', Object.keys(storyIdeasData.ideas).length, 'levels');
        }
    } catch (error) {
        console.warn('Could not load story ideas:', error);
    }
}

async function loadStoryTypes() {
    try {
        const response = await fetch('/data/story-types.json');
        if (response.ok) {
            storyTypesData = await response.json();
            console.log('Loaded story types:', storyTypesData.storyTypes.length);
            renderStoryTypeCards();
            updateStoryTypeInfo();
        }
    } catch (error) {
        console.warn('Could not load story types:', error);
    }
}

async function loadArtStyles() {
    try {
        const response = await fetch('/data/art-styles.json');
        if (response.ok) {
            artStylesData = await response.json();
            console.log('Loaded art styles:', artStylesData.artStyles.length);
            renderArtStyleCards();
        }
    } catch (error) {
        console.warn('Could not load art styles:', error);
    }
}

// Story type icons (emoji fallbacks)
const storyTypeIcons = {
    'problem-solution': '🎯',
    'fantasy-dream': '✨',
    'journey': '🚶',
    'slice-of-life': '🌸',
    'cumulative': '📚',
    'friendship': '🤝',
    'overcoming-fear': '💪',
    'helping': '❤️',
    'discovery': '🔍',
    'silly-chain': '🎪',
    'bedtime': '🌙',
    'lost-found': '🔎'
};

function renderStoryTypeCards() {
    const container = document.getElementById('storyTypeCards');
    if (!container || !storyTypesData) return;

    container.innerHTML = storyTypesData.storyTypes.map(type => {
        const isSelected = state.formData.storyType === type.id;
        const icon = storyTypeIcons[type.id] || '📖';
        return `
            <div class="style-card ${isSelected ? 'selected' : ''}"
                 data-type="${type.id}"
                 onclick="selectStoryType('${type.id}')">
                <div class="style-card-icon">${icon}</div>
                <div class="style-card-name">${type.name}</div>
            </div>
        `;
    }).join('');
}

function selectStoryType(typeId) {
    state.formData.storyType = typeId;
    document.getElementById('storyTypeSelect').value = typeId;

    // Update card selection visuals
    document.querySelectorAll('#storyTypeCards .style-card').forEach(card => {
        card.classList.toggle('selected', card.dataset.type === typeId);
    });

    updateStoryTypeInfo();
}

function renderArtStyleCards() {
    const container = document.getElementById('artStyleCards');
    if (!container || !artStylesData) return;

    container.innerHTML = artStylesData.artStyles.map(style => {
        const isSelected = state.formData.artStyle === style.id;
        const imagePath = `/images/art-styles/${style.id}.png`;
        return `
            <div class="style-card ${isSelected ? 'selected' : ''}"
                 data-style="${style.id}"
                 onclick="selectArtStyle('${style.id}')">
                <img class="style-card-image"
                     src="${imagePath}"
                     alt="${style.name}"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div class="style-card-icon" style="display:none;">🎨</div>
                <div class="style-card-name">${style.name}</div>
            </div>
        `;
    }).join('');
}

function selectArtStyle(styleId) {
    state.formData.artStyle = styleId;
    document.getElementById('artStyleSelect').value = styleId;

    // Update card selection visuals
    document.querySelectorAll('#artStyleCards .style-card').forEach(card => {
        card.classList.toggle('selected', card.dataset.style === styleId);
    });
}

function updateStoryTypeInfo() {
    const infoBox = document.getElementById('storyTypeInfo');
    if (!infoBox || !storyTypesData) return;

    const selectedType = state.formData.storyType;
    const typeData = storyTypesData.storyTypes.find(t => t.id === selectedType);

    if (typeData) {
        const beats = typeData.beats.join(' → ');
        infoBox.innerHTML = `
            <strong>${typeData.name}:</strong> ${typeData.description}
            <br><span style="color: var(--color-text-muted);">Beats: ${beats}</span>
        `;
    }
}

function getSelectedStoryType() {
    if (!storyTypesData) return null;
    const selectedType = state.formData.storyType;
    return storyTypesData.storyTypes.find(t => t.id === selectedType);
}

function getSelectedArtStyle() {
    if (!artStylesData) return null;
    const selectedStyle = state.formData.artStyle;
    return artStylesData.artStyles.find(s => s.id === selectedStyle);
}

function renderStoryIdeas() {
    const grid = document.getElementById('storyIdeasGrid');
    const countEl = document.getElementById('storyIdeasCount');
    const level = document.getElementById('levelSelect').value;

    if (!storyIdeasData || !storyIdeasData.ideas) {
        grid.innerHTML = '<div class="no-ideas-message">Could not load story ideas</div>';
        countEl.textContent = '';
        return;
    }

    const ideas = storyIdeasData.ideas[level] || [];

    // Update count display
    countEl.textContent = ideas.length > 0 ? `(${ideas.length} ideas)` : '';

    if (ideas.length === 0) {
        grid.innerHTML = '<div class="no-ideas-message">No pre-made ideas for this level yet. Write your own below!</div>';
        return;
    }

    grid.innerHTML = ideas.map((idea, index) => `
        <div class="story-idea-card ${selectedIdeaIndex === index ? 'selected' : ''}"
             onclick="selectStoryIdea(${index})">
            <div class="story-idea-title">${idea.title}</div>
            <div class="story-idea-concept">${idea.concept}</div>
            <div class="story-idea-meta">
                <span class="story-idea-tag">${idea.character}</span>
                ${idea.theme ? `<span class="story-idea-tag theme">${idea.theme}</span>` : ''}
            </div>
        </div>
    `).join('');

    // Update visibility
    grid.style.display = storyIdeasVisible ? 'grid' : 'none';
    document.getElementById('toggleIdeas').textContent = storyIdeasVisible ? 'Hide' : 'Show';
}

function selectStoryIdea(index) {
    const level = document.getElementById('levelSelect').value;
    const ideas = storyIdeasData?.ideas[level] || [];
    const idea = ideas[index];

    if (!idea) return;

    // Toggle selection
    if (selectedIdeaIndex === index) {
        // Deselect
        selectedIdeaIndex = null;
        document.getElementById('conceptInput').value = '';
        document.getElementById('settingInput').value = '';
        state.formData.words = [];
    } else {
        // Select this idea
        selectedIdeaIndex = index;

        // Populate form fields
        document.getElementById('conceptInput').value = idea.concept;
        document.getElementById('settingInput').value = idea.setting || '';

        // Add sample words if available
        if (idea.sample_words && idea.sample_words.length > 0) {
            state.formData.words = [...idea.sample_words];
        }
    }

    renderStoryIdeas();
    renderWordTags();
}

function toggleStoryIdeas() {
    storyIdeasVisible = !storyIdeasVisible;
    const grid = document.getElementById('storyIdeasGrid');
    grid.style.display = storyIdeasVisible ? 'grid' : 'none';
    document.getElementById('toggleIdeas').textContent = storyIdeasVisible ? 'Hide' : 'Show';
}

// ===================
// PHASE 1: OUTLINE GENERATION
// ===================

function generateOutline() {
    state.formData.concept = document.getElementById('conceptInput').value.trim();
    state.formData.setting = document.getElementById('settingInput').value.trim();
    state.formData.level = document.getElementById('levelSelect').value;
    state.formData.storyType = document.getElementById('storyTypeSelect').value;
    state.formData.artStyle = document.getElementById('artStyleSelect').value;

    if (!state.formData.concept) {
        alert('Please enter a story concept.');
        return;
    }

    if (state.outline) {
        showConfirmModal(
            'Generate New Outline?',
            'This will replace your current outline and all progress. Continue?',
            doGenerateOutline
        );
    } else {
        doGenerateOutline();
    }
}

async function doGenerateOutline() {
    document.getElementById('phase1Form').classList.add('hidden');
    document.getElementById('phase1Loading').classList.remove('hidden');
    document.getElementById('phase1LoadingText').textContent = 'Generating story outline...';

    try {
        const response = await fetch('/api/generate-story', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: buildOutlinePrompt(),
                mode: 'outline'
            })
        });

        if (!response.ok) throw new Error('Failed to generate outline');

        const outline = await response.json();
        state.slug = generateSlug(outline.title);
        state.outline = outline;
        state.outline.level = state.formData.level;
        saveState();

        state.phaseStatus[1] = 'complete';
        state.checkpointApprovals[1] = { approved: true, timestamp: new Date().toISOString() };
        saveState();

        document.getElementById('phase1Loading').classList.add('hidden');
        goToPhase(2);
        renderOutlinePhase();

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate outline. Please try again.');
        document.getElementById('phase1Form').classList.remove('hidden');
        document.getElementById('phase1Loading').classList.add('hidden');
    }
}

function buildOutlinePrompt() {
    const customPrompt = document.getElementById('storyPromptTextarea').value.trim();
    if (customPrompt) {
        state.prompts.story = customPrompt;
        return customPrompt;
    }
    return buildDefaultOutlinePrompt();
}

function buildDefaultOutlinePrompt() {
    const level = state.formData.level;
    const band = level.charAt(0); // A, B, C, or D

    const levelDescriptions = {
        'A0': 'Concept of Print. 0-2 words per page. UPPERCASE only.',
        'A1': 'Letter Recognition. 1 word per page. Labels only.',
        'A2': 'CV/VC Words. 2-3 words per page. Max 3 words per sentence.',
        'A3': 'CVC Words. 3-4 words per page. Max 4 words per sentence.',
        'A4': 'CVC Fluency. 4-5 words per page. Max 5 words per sentence.',
        'B1': 'Beginning blends (st, sp, cr, fl). Max 5-6 words per sentence.',
        'B2': 'Ending blends (mp, nd, st). Max 6 words per sentence.',
        'B3': 'Digraphs (sh, ch, th, wh). Max 6 words per sentence.',
        'B4': 'Short vowel mastery. Max 7 words per sentence.',
        'B5': 'Silent e (CVCe). Max 7 words per sentence.',
        'B6': 'Soft c and g. Max 8 words per sentence.',
        'B7': 'R-controlled vowels. Max 8 words per sentence.',
        'B8': 'Vowel teams (ai, ea, oa). Max 9 words per sentence.',
        'B9': 'Diphthongs (oi, ou, ow). Max 9 words per sentence.',
        'C1': 'Two-syllable compound words. Max 10 words per sentence.',
        'C2': 'Open syllables. Max 10 words per sentence.',
        'C3': 'Two-syllable closed (kitten, rabbit). Max 12 words per sentence.',
        'C4': 'Consonant -le (table, little). Max 12 words per sentence.',
        'C5': 'Prefixes (un-, re-, pre-). Natural sentence length.',
        'C6': 'Suffixes (-ful, -less, -ness). Natural sentence length.',
        'C7': 'Latin roots. Natural sentence length.',
        'C8': 'Greek combining forms. Natural sentence length.',
        'D1': 'Chapter books intro. Natural sentence length.',
        'D2': 'Complex narratives. Natural sentence length.',
        'D3': 'Multiple viewpoints. Natural sentence length.',
        'D4': 'Abstract themes. Natural sentence length.',
        'D5': 'Literary devices. Natural sentence length.',
        'D6': 'Independent reading. Natural sentence length.'
    };

    // Get selected story type and art style
    const storyType = getSelectedStoryType();
    const artStyle = getSelectedArtStyle();

    // Build story type section
    const storyTypeName = storyType?.name || 'Problem-Solution';
    const storyTypeDesc = storyType?.description || 'Character wants something, faces obstacle, tries and fails, finally succeeds';
    const storyTypeBeats = storyType?.beats || ['INTRODUCE', 'WANT', 'OBSTACLE', 'TRY', 'FAIL', 'RESOLVE', 'CELEBRATE'];
    const storyTypeGoodFor = storyType?.goodFor || 'Action verbs, cause/effect';

    // Build art style section
    const artStyleName = artStyle?.name || 'Warm Watercolor';
    const artStylePrompt = artStyle?.prompt || 'Warm watercolor illustration, soft edges, gentle color washes, luminous quality, traditional children\'s book art';
    const artStyleMood = artStyle?.mood || 'Gentle, cozy, nostalgic';

    // Generate beats template based on story type
    const beatsTemplate = storyTypeBeats.map((beat, i) => {
        return `    { "page": ${i + 1}, "beat": "${beat}: [describe what happens]" }`;
    }).join(',\n');

    return `You are a master children's book author. Generate a story OUTLINE for a decodable book.

READING LEVEL: ${level} - ${levelDescriptions[level] || 'Age-appropriate vocabulary'}
CONCEPT: ${state.formData.concept}
SETTING: ${state.formData.setting || 'appropriate for the story'}
${state.formData.words.length > 0 ? `WORDS TO INCLUDE: ${state.formData.words.join(', ')}` : ''}

## STORY TYPE: ${storyTypeName}

${storyTypeDesc}

This type is good for: ${storyTypeGoodFor}

Follow this beat structure:
${storyTypeBeats.map((beat, i) => `${i + 1}. ${beat}`).join('\n')}

## ART STYLE: ${artStyleName}

${artStylePrompt}

Mood: ${artStyleMood}

## OUTPUT FORMAT (JSON only, no other text)

{
  "title": "Story Title (2-4 catchy words)",
  "character": {
    "name": "Character Name",
    "type": "animal/child/creature",
    "visual_shorthand": "small orange tabby kitten with white paws",
    "distinctive_features": ["bright green eyes", "fluffy striped tail", "white mittens on paws"]
  },
  "setting": "Detailed setting description with visual elements",
  "visual_style": "${artStylePrompt}",
  "story_type": "${storyType?.id || 'problem-solution'}",
  "beats": [
${beatsTemplate}
  ],
  "arc": "Brief description: [Character] wants [goal] but [obstacle]. They try [attempts] and finally [resolution]."
}

Create ${storyTypeBeats.length}-${storyTypeBeats.length + 4} beats following the ${storyTypeName} structure. Each beat should clearly connect to the next.`;
}

// ===================
// PHASE 2: OUTLINE REVIEW
// ===================

function renderOutlinePhase() {
    if (!state.outline) return;
    document.getElementById('outlineTitle').value = state.outline.title || '';

    // Editable character fields
    const char = state.outline.character || {};
    document.getElementById('charName').value = char.name || '';
    document.getElementById('charVisual').value = char.visual_shorthand || '';
    document.getElementById('charFeatures').value = (char.distinctive_features || []).join(', ');

    // Editable setting, style, and arc
    document.getElementById('outlineSetting').value = state.outline.setting || '';
    document.getElementById('outlineStyle').value = state.outline.visual_style || '';
    document.getElementById('outlineArc').value = state.outline.arc || '';

    renderBeats();
}

function renderBeats() {
    const container = document.getElementById('beatsList');
    if (!state.outline || !state.outline.beats) {
        container.innerHTML = '<p class="hint">No beats yet. Generate an outline first.</p>';
        return;
    }
    container.innerHTML = state.outline.beats.map((beat, index) => `
        <div class="beat-item" data-index="${index}">
            <div class="beat-number">${beat.page}</div>
            <div class="beat-content">
                <textarea class="beat-input" onchange="updateBeat(${index}, this.value)">${beat.beat}</textarea>
            </div>
            <div class="beat-actions">
                <button onclick="moveBeatUp(${index})" ${index === 0 ? 'disabled' : ''}>↑</button>
                <button onclick="moveBeatDown(${index})" ${index === state.outline.beats.length - 1 ? 'disabled' : ''}>↓</button>
                <button onclick="deleteBeat(${index})">×</button>
            </div>
        </div>
    `).join('');
}

function updateOutlineTitle(value) {
    if (state.outline) {
        state.outline.title = value;
        state.slug = generateSlug(value);
        saveState();
    }
}

function updateCharacter(field, value) {
    if (!state.outline) return;
    if (!state.outline.character) state.outline.character = {};

    if (field === 'distinctive_features') {
        state.outline.character[field] = value.split(',').map(f => f.trim()).filter(f => f);
    } else {
        state.outline.character[field] = value;
    }
    saveState();
}

function updateOutlineSetting(value) {
    if (!state.outline) return;
    state.outline.setting = value;
    saveState();
}

function updateOutlineStyle(value) {
    if (!state.outline) return;
    state.outline.visual_style = value;
    saveState();
}

function updateOutlineArc(value) {
    if (!state.outline) return;
    state.outline.arc = value;
    saveState();
}

function updateBeat(index, value) {
    if (state.outline && state.outline.beats[index]) {
        state.outline.beats[index].beat = value;
        saveState();
    }
}

function addBeat() {
    if (!state.outline) return;
    state.outline.beats.push({ page: state.outline.beats.length + 1, beat: '' });
    renderBeats();
    saveState();
}

function deleteBeat(index) {
    if (!state.outline || state.outline.beats.length <= 1) return;
    state.outline.beats.splice(index, 1);
    state.outline.beats.forEach((b, i) => b.page = i + 1);
    renderBeats();
    saveState();
}

function moveBeatUp(index) {
    if (!state.outline || index <= 0) return;
    [state.outline.beats[index - 1], state.outline.beats[index]] = [state.outline.beats[index], state.outline.beats[index - 1]];
    state.outline.beats.forEach((b, i) => b.page = i + 1);
    renderBeats();
    saveState();
}

function moveBeatDown(index) {
    if (!state.outline || index >= state.outline.beats.length - 1) return;
    [state.outline.beats[index], state.outline.beats[index + 1]] = [state.outline.beats[index + 1], state.outline.beats[index]];
    state.outline.beats.forEach((b, i) => b.page = i + 1);
    renderBeats();
    saveState();
}

function regenerateOutline() {
    showConfirmModal('Regenerate Outline?', 'This will replace your current outline.', doGenerateOutline);
}

// ===================
// PHASE 2→3: EXPAND TO FULL STORY
// ===================

async function expandToFullStory() {
    if (!state.outline) {
        alert('No outline to expand.');
        return;
    }

    document.getElementById('phase2Content').classList.add('hidden');
    document.getElementById('phase2Loading').classList.remove('hidden');
    document.getElementById('phase2LoadingText').textContent = 'Expanding to full story...';

    try {
        const response = await fetch('/api/generate-story', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: buildFullStoryPrompt(),
                mode: 'full',
                outline: state.outline
            })
        });

        if (!response.ok) throw new Error('Failed to expand story');

        const book = await response.json();
        state.book = book;
        state.book.slug = state.slug;
        state.book.level = state.formData.level;
        state.book.setting = state.formData.setting;
        state.book.storyType = state.formData.storyType;
        state.book.artStyle = state.formData.artStyle;

        // Ensure story_bible is preserved (generated by LLM in full story expansion)
        if (book.story_bible) {
            state.book.story_bible = book.story_bible;
            console.log('Story bible generated:', state.book.story_bible);
        }

        state.phaseStatus[2] = 'complete';
        state.checkpointApprovals[2] = { approved: true, timestamp: new Date().toISOString() };
        saveState();
        saveToSupabase();

        document.getElementById('phase2Loading').classList.add('hidden');
        goToPhase(3);
        renderPhase2Content();

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to expand story.');
        document.getElementById('phase2Content').classList.remove('hidden');
        document.getElementById('phase2Loading').classList.add('hidden');
    }
}

function buildFullStoryPrompt() {
    const level = state.formData.level;
    const band = level.charAt(0);
    const outline = state.outline;

    const levelConstraints = {
        'A0': { maxWords: 2, pages: '8-12', guidance: 'Wordless or 1-2 word labels. Pictures carry all meaning.' },
        'A1': { maxWords: 2, pages: '10-12', guidance: 'Labels only: "A [noun]" or "I [verb]". One word per page.' },
        'A2': { maxWords: 3, pages: '10-12', guidance: 'Simple patterns: "I see a [noun]." Repetitive structure.' },
        'A3': { maxWords: 4, pages: '12-14', guidance: 'CVC words in simple sentences. "The cat sat."' },
        'A4': { maxWords: 5, pages: '12-14', guidance: 'CVC fluency. Short predictable sentences.' },
        'B1': { maxWords: 6, pages: '12-16', guidance: 'Beginning blends. "The frog stops."' },
        'B2': { maxWords: 6, pages: '12-16', guidance: 'Ending blends. "The ant went fast."' },
        'B3': { maxWords: 6, pages: '12-16', guidance: 'Digraphs. "The ship is big."' },
        'B4': { maxWords: 7, pages: '14-16', guidance: 'Short vowel mastery. Varied sentence patterns.' },
        'B5': { maxWords: 7, pages: '14-16', guidance: 'Silent e. "The cake is on the plate."' },
        'B6': { maxWords: 8, pages: '14-16', guidance: 'Soft c/g. "The mice race to the fence."' },
        'B7': { maxWords: 8, pages: '14-16', guidance: 'R-controlled. "The bird sat on her perch."' },
        'B8': { maxWords: 9, pages: '14-16', guidance: 'Vowel teams. "The boat floats on the sea."' },
        'B9': { maxWords: 9, pages: '14-16', guidance: 'Diphthongs. "The cow found a coin."' },
        'C1': { maxWords: 10, pages: '16-20', guidance: 'Compound words. "The sunflower grew tall."' },
        'C2': { maxWords: 10, pages: '16-20', guidance: 'Open syllables. "The tiny baby spider..."' },
        'C3': { maxWords: 12, pages: '16-20', guidance: 'Chapter-style. "The kitten was hidden in the basket."' },
        'C4': { maxWords: 12, pages: '16-20', guidance: 'Consonant-le. "The little turtle..."' },
        'D1': { maxWords: 15, pages: '20-24', guidance: 'Chapter book style. Complex narratives.' },
        'D2': { maxWords: 15, pages: '20-24', guidance: 'Rich vocabulary. Nuanced storytelling.' }
    };

    const constraints = levelConstraints[level] || { maxWords: 10, pages: '12', guidance: 'Age-appropriate.' };

    const bandStyles = {
        'A': 'Simple bold shapes, soft watercolor, minimal detail, warm pastels.',
        'B': 'Playful watercolor, expressive characters, vibrant colors.',
        'C': 'Rich watercolor, detailed characters/settings, dynamic compositions.',
        'D': 'Sophisticated watercolor, detailed environments, nuanced lighting.'
    };

    const charDesc = outline.character ?
        `${outline.character.name}: ${outline.character.visual_shorthand || outline.character.type}` +
        (outline.character.distinctive_features ? ` (${outline.character.distinctive_features.join(', ')})` : '') :
        'Main character';

    return `You are a master children's book author. Expand this outline into a complete decodable book.

## STORY OUTLINE
Title: ${outline.title}
Character: ${charDesc}
Setting: ${outline.setting}
Visual Style: ${outline.visual_style || bandStyles[band]}
Arc: ${outline.arc}

Beats:
${outline.beats.map(b => `Page ${b.page}: ${b.beat}`).join('\n')}

## LEVEL CONSTRAINTS: ${level}
- Maximum ${constraints.maxWords} words per sentence (STRICT - count every word!)
- 2-3 sentences per page
- Level guidance: ${constraints.guidance}

## CRITICAL: NATURAL LANGUAGE

**Every sentence must sound like something a real person would say.**

READ EACH SENTENCE ALOUD before writing it. If it sounds awkward, rewrite it.

BAD (phonics-forced, unnatural):
- "He feels so free up." ← grammatically wrong
- "Stan stops at his bed." ← stilted, robotic
- "Is it wet?" (to a well) ← nobody says this

GOOD (natural speech that uses target sounds):
- "He felt free as a bird!"
- "Stan sat on his bed."
- "Hello? Is anyone there?"

RULE: Prioritize natural-sounding sentences OVER hitting phonics targets.
A clear story with fewer target words beats awkward text that hits every pattern.

## CRITICAL: LOGIC AND CONTINUITY

Every sentence MUST make logical sense. Check cause and effect.

LOGIC ERRORS TO AVOID:
- "He got wet in the sun." (sun doesn't make you wet)
- "Now Max is not wet." (after a bath? he'd be soaking wet!)
- "The cat ran to sit." (awkward phrasing)

GOOD LOGIC:
- "Max jumped in the mud. Mud splashed on his nose!" (cause → effect)
- "Mom dried Max with a towel. Now his fur was fluffy." (action → result)

CONTINUITY: Track character state across pages:
- If muddy on page 4, still muddy on page 5 (unless cleaned)
- If in bath, they're WET when they get out
- Each scene visually connects to the previous one

## SCENE DESCRIPTION FORMAT

Each scene must include WHO/WHERE/WHAT/STATE:
- WHO: Character with EXACT visual details (use character description above)
- WHERE: Specific setting with lighting/atmosphere
- WHAT: Active verb describing current action
- STATE: Character's current physical state (wet? muddy? tired? happy expression?)
- Shot type: Wide/Medium/Close-up

SCENE RULES:
- PHYSICAL descriptions only (not emotional - "eyes wide" not "scared")
- NEVER use negations ("no ball" makes a ball appear!)
- End every scene with: NO TEXT, NO WORDS, NO LETTERS

## OUTPUT FORMAT (JSON only)

{
  "title": "${outline.title}",
  "summary": "One sentence story description",
  "characters": {
    "main": {
      "name": "${outline.character?.name || 'Character'}",
      "visual_shorthand": "${outline.character?.visual_shorthand || 'description'}",
      "distinctive_features": ${JSON.stringify(outline.character?.distinctive_features || [])}
    }
  },
  "setting_context": "${outline.setting}",
  "visual_style": "${outline.visual_style || bandStyles[band]}",
  "story_bible": {
    "premise": "2-3 sentence summary of the story's core concept and emotional journey",
    "setting": "Detailed description of where/when the story takes place",
    "characters": [
      {
        "name": "${outline.character?.name || 'Character'}",
        "role": "main",
        "description": "Full visual description: physical appearance, clothing, distinctive features, personality"
      }
    ],
    "themes": ["Primary theme", "Secondary theme"],
    "character_arcs": {
      "${outline.character?.name || 'Character'}": "Character's emotional/growth journey from start to end"
    },
    "emotional_arc": "Overall story emotional journey",
    "emotional_beats": [
      { "page": 1, "beat": "emotion or story beat for this page" }
    ],
    "level_adaptation": "Notes on how the story was adapted for reading level ${level}"
  },
  "pages": [
    {
      "story_page": 1,
      "text": "<line>First sentence here.</line><line>Second sentence.</line>",
      "scene": "Wide shot: ${outline.character?.name || 'Character'}, ${outline.character?.visual_shorthand || 'with visual details'}, [ACTION verb-ing] in [WHERE with specifics]. [Mood/lighting]. NO TEXT, NO WORDS, NO LETTERS."
    }
  ],
  "word_list": {
    "sound_out": ["decodable", "phonics", "words"],
    "sight": ["the", "is", "a"],
    "heart": ["emotional", "vocabulary", "words"]
  },
  "reference_prompt": "9-panel children's book reference sheet, grid layout (3x3), consistent ${bandStyles[band]} throughout all panels:\\n\\nRow 1 - ${outline.character?.name || 'MAIN CHARACTER'}:\\n[1] ${outline.character?.name || 'Character'}, ${outline.character?.visual_shorthand || 'full visual description'}, front view, friendly expression, cream background\\n[2] Same character [action from story], side view\\n[3] Same character [different expression/action]\\n\\nRow 2 - Supporting Elements:\\n[4] [Key object or secondary character from story]\\n[5] **KEY MOMENT** - [Hero shot: main character in central story moment]\\n[6] [Another key prop from story]\\n\\nRow 3 - Settings:\\n[7] [First setting], [lighting/mood]\\n[8] [Second setting or different time]\\n[9] [Final heartwarming scene]\\n\\nSTYLE: ${bandStyles[band]} Soft edges, muted earthy palette.\\nFORMAT: Square 1:1, 3x3 grid, thin white borders.\\nCRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere."
}

Write the COMPLETE story with ALL pages. Use level-appropriate vocabulary only.`;
}

// Legacy compatibility
function generateStory() { generateOutline(); }

// Internal scene generation
async function generateScenesInternal() {
    const response = await fetch('/api/generate-scenes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ book: state.book })
    });
    if (!response.ok) throw new Error('Failed to generate scenes');
    const result = await response.json();
    result.pages.forEach((newPage, i) => {
        if (state.book.pages[i]) state.book.pages[i].scene = newPage.scene;
    });
    saveState();
}

function buildStoryPrompt() {
    const customPrompt = document.getElementById('storyPromptTextarea').value.trim();
    if (customPrompt) {
        state.prompts.story = customPrompt;
        return customPrompt;
    }
    return buildDefaultOutlinePrompt();
}

function resetPhase1() {
    state.book = null;
    state.slug = null;
    document.getElementById('phase1Form').classList.remove('hidden');
    updateUI();
}

// ===================
// PROMPT EDITOR FUNCTIONS
// ===================

// Build the default story prompt (without using custom)
function buildDefaultStoryPrompt() {
    const levelDescriptions = {
        'A1': 'Simple CVC words only (cat, dog, sun). 3-4 words per sentence.',
        'A2': 'CVC words with basic sight words (the, a, is). 4-5 words per sentence.',
        'B1': 'Beginning consonant blends (st-, fl-, cr-, etc.). 5-6 words per sentence.',
        'B2': 'Ending blends (-mp, -lp, -st). 6-7 words per sentence.',
        'C1': 'Digraphs (sh, ch, th). 7-8 words per sentence.',
        'C2': 'Silent e words (cake, bike, home). Longer sentences OK.',
        'D1': 'Vowel teams (rain, boat, see). Complex sentences OK.',
        'D2': 'R-controlled vowels (car, bird, corn). Natural sentence length.'
    };

    // Get story type info
    const storyType = storyTypesData?.storyTypes?.find(t => t.id === state.formData.storyType);
    const storyTypeSection = storyType ? `
STORY TYPE: ${storyType.name}
Structure: ${storyType.description}
Beats to follow: ${storyType.beats.join(' → ')}
` : '';

    return `You are writing a decodable book for beginning readers. Your goal is to create a story that is BOTH phonetically appropriate AND narratively compelling.

READING LEVEL: ${state.formData.level} - ${levelDescriptions[state.formData.level] || 'Age-appropriate vocabulary'}
CONCEPT: ${state.formData.concept}
SETTING: ${state.formData.setting || 'appropriate for the story'}
${state.formData.words.length > 0 ? `WORDS TO INCLUDE: ${state.formData.words.join(', ')}` : ''}
${storyTypeSection}
== NARRATIVE REQUIREMENTS (CRITICAL) ==

1. **CHARACTER WANT**: The main character must want something specific and clear
   - Good: "Pip wants a friend"
   - Bad: "Pip is sad" (vague mood, not a want)

2. **OBSTACLE**: There must be a real problem preventing the want
   - Good: "The ball rolled into a dark cave"
   - Bad: Random events that don't block the goal

3. **CAUSATION**: Each page must cause the next. If any page could be removed without breaking the story, it doesn't belong.

4. **RESOLUTION**: The ending must directly solve the problem from page 1
   - Setup: "Fox had no pals" → Ending: "Fox had a pal at last!"
   - NOT: Random happy ending unrelated to the problem

== LANGUAGE QUALITY (CRITICAL) ==

**Every sentence must sound like something a real person would say.**

BAD (phonics-forced, unnatural):
- "He feels so free up."
- "Stan stops at his bed."
- "Is it wet?" (to a well)

GOOD (natural speech that happens to use target sounds):
- "He felt free as a bird!"
- "Stan sat on his bed."
- "Hello? Is anyone there?"

Rules:
- Read each sentence aloud. If it sounds awkward, rewrite it.
- Prioritize natural language OVER hitting every phonics target.
- A clear story with slightly fewer target words beats a confusing story that hits every pattern.
- One idea per sentence. Short and punchy.

== EMOTIONAL CLARITY ==

You should be able to name the emotion on each page:
- Page 1: SAD (lonely)
- Page 2: CURIOUS (what's that?)
- Page 3: HOPEFUL (maybe this will work)
- etc.

If you can't name the emotion, the page isn't working.

== PHONICS CONSTRAINTS ==

Level ${state.formData.level}: ${levelDescriptions[state.formData.level] || 'Age-appropriate'}

- Use decodable words appropriate for this level
- Sight words allowed: the, a, is, was, to, I, he, she, we, they, said, have, do, what
- 1-2 "reach words" OK if picturable (like "helicopter" with clear illustration)
- If a phonics word doesn't fit naturally, DON'T USE IT

== OUTPUT FORMAT ==

Generate 8 pages. Return ONLY valid JSON:

{
  "title": "2-4 word title",
  "level": "${state.formData.level}",
  "character": {
    "name": "Character name",
    "type": "child/animal/creature",
    "visual_shorthand": "brief visual description for illustrations"
  },
  "pages": [
    {"page": 1, "text": "Natural sentence here.", "emotion": "SAD"},
    {"page": 2, "text": "Next sentence.", "emotion": "CURIOUS"},
    ...
  ],
  "word_list": {
    "sound_out": ["decodable", "words", "used"],
    "sight": ["sight", "words", "used"],
    "heart": ["emotional", "theme", "words"]
  }
}

Return ONLY the JSON, no explanation.`;
}

// Preview the story prompt in the editor
function previewStoryPrompt() {
    // First update form data from inputs
    state.formData.concept = document.getElementById('conceptInput').value.trim();
    state.formData.setting = document.getElementById('settingInput').value.trim();
    state.formData.level = document.getElementById('levelSelect').value;
    state.formData.storyType = document.getElementById('storyTypeSelect').value;
    state.formData.artStyle = document.getElementById('artStyleSelect').value;

    const prompt = buildDefaultStoryPrompt();
    document.getElementById('storyPromptTextarea').value = prompt;
}

// Reset story prompt to default
function resetStoryPrompt() {
    state.prompts.story = null;
    previewStoryPrompt();
}

// Preview style guide prompt
function previewStyleGuidePrompt() {
    const prompt = buildDefaultReferencePrompt();
    document.getElementById('styleGuidePromptTextarea').value = prompt;
}

// Reset style guide prompt
function resetStyleGuidePrompt() {
    state.prompts.styleGuide = null;
    previewStyleGuidePrompt();
}

// Preview opening scenes prompt
function previewOpeningScenesPrompt() {
    const prompt = buildDefaultOpeningScenesPrompt();
    document.getElementById('openingScenesPromptTextarea').value = prompt;
}

// Reset opening scenes prompt
function resetOpeningScenesPrompt() {
    state.prompts.openingScenes = null;
    previewOpeningScenesPrompt();
}

// Preview closing scenes prompt
function previewClosingScenesPrompt() {
    const prompt = buildDefaultClosingScenesPrompt();
    document.getElementById('closingScenesPromptTextarea').value = prompt;
}

// Reset closing scenes prompt
function resetClosingScenesPrompt() {
    state.prompts.closingScenes = null;
    previewClosingScenesPrompt();
}

// Build default reference prompt
function buildDefaultReferencePrompt() {
    const character = state.book?.characterName || 'the character';
    const characterType = state.book?.character || 'animal';
    const setting = state.book?.setting || 'the scene';

    return `Create a 3x3 grid style reference sheet for a children's book character:

GRID LAYOUT (9 panels total):
Row 1: [1] ${character} front view, [2] ${character} expressions (happy, surprised, worried), [3] ${character} in action pose
Row 2: [4] Secondary elements/props from story, [5] KEY SCENE: ${character} in main story moment, [6] Important objects/items
Row 3: [7] ${setting} background element, [8] Another setting element, [9] ${character} resolution pose

CHARACTER DESIGN for ${character} the ${characterType}:
- Soft, friendly, rounded shapes
- Clear, simple features easy to recognize
- Consistent color palette throughout all panels
- Expressive but simple face

STYLE: Soft watercolor children's book illustration, warm colors, gentle lighting, Eric Carle inspired textures.

IMPORTANT: This is a reference sheet with 9 distinct panels arranged in a 3x3 grid. Each panel should be clearly separated.
NO TEXT, NO WORDS, NO LETTERS anywhere in the image.`;
}

// Build default opening scenes prompt
function buildDefaultOpeningScenesPrompt() {
    if (!state.book) return '';
    const pages = state.book.pages || [];
    // Filter for pages with scenes (type may be 'story' or undefined for older books)
    const storyPages = pages.filter(p => p.scene && p.scene.length > 20);
    const midPoint = Math.ceil(storyPages.length / 2);
    const openingPages = storyPages.slice(0, midPoint);

    const scenes = openingPages
        .filter(p => !p.scene.includes('Illustration for:'))
        .slice(0, 6)
        .map((p, i) => `[${i + 1}] ${p.scene.substring(0, 150)}`);

    while (scenes.length < 6) {
        scenes.push(`[${scenes.length + 1}] Key moment from opening`);
    }

    return `9-PANEL OPENING SCENES REFERENCE for '${state.book.title}'

Using the style from the reference image, create a 3x3 grid showing scenes from the FIRST HALF of the story.

Row 1:
${scenes[0]}
${scenes[1]}
${scenes[2]}

Row 2:
${scenes[3]}
${scenes[4]}
${scenes[5]}

Row 3 - Key moments from first half:
[7] Establishing shot of main setting
[8] Character interaction moment
[9] Transition scene leading to second half

STYLE: Match the watercolor style from the reference image exactly.
Consistent characters across all panels.
NO TEXT, NO WORDS, NO LETTERS anywhere in the image.`;
}

// Build default closing scenes prompt
function buildDefaultClosingScenesPrompt() {
    if (!state.book) return '';
    const pages = state.book.pages || [];
    // Filter for pages with scenes (type may be 'story' or undefined for older books)
    const storyPages = pages.filter(p => p.scene && p.scene.length > 20);
    const midPoint = Math.ceil(storyPages.length / 2);
    const closingPages = storyPages.slice(midPoint);

    const scenes = closingPages
        .filter(p => !p.scene.includes('Illustration for:'))
        .slice(0, 6)
        .map((p, i) => `[${i + 1}] ${p.scene.substring(0, 150)}`);

    while (scenes.length < 6) {
        scenes.push(`[${scenes.length + 1}] Key moment from closing`);
    }

    return `9-PANEL CLOSING SCENES REFERENCE for '${state.book.title}'

Using the style from the reference image, create a 3x3 grid showing scenes from the SECOND HALF of the story.

Row 1:
${scenes[0]}
${scenes[1]}
${scenes[2]}

Row 2:
${scenes[3]}
${scenes[4]}
${scenes[5]}

Row 3 - Key moments from second half:
[7] Climax scene
[8] Resolution moment
[9] Final happy ending

STYLE: Match the watercolor style from the reference image exactly.
Consistent characters across all panels.
NO TEXT, NO WORDS, NO LETTERS anywhere in the image.`;
}

// ===================
// CONFIRMATION MODAL
// ===================

let pendingConfirmAction = null;

function showConfirmModal(title, message, actionCallback) {
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMessage').textContent = message;
    pendingConfirmAction = actionCallback;
    document.getElementById('confirmModal').classList.add('visible');
}

function closeConfirmModal() {
    document.getElementById('confirmModal').classList.remove('visible');
    pendingConfirmAction = null;
}

function executeConfirmedAction() {
    if (pendingConfirmAction) {
        pendingConfirmAction();
    }
    closeConfirmModal();
}

// ===================
// PHASE 2: STORY REVIEW (Split View)
// ===================

function renderPhase2Content() {
    if (!state.book) return;

    // Show content, hide loading (Phase 3 elements)
    document.getElementById('phase3Loading').classList.add('hidden');
    document.getElementById('phase3Content').classList.remove('hidden');
    document.getElementById('phase3Actions').classList.remove('hidden');

    // Render editable story (left panel)
    renderEditableStory();

    // Render scene list (right panel)
    renderSceneList();

    // Render metadata panels (word_list and story_bible)
    renderMetadataPanels();
}

function renderEditableStory() {
    // Set title
    document.getElementById('editableTitle').value = state.book.title || '';

    // Render pages
    const container = document.getElementById('editablePages');
    container.innerHTML = state.book.pages.map((page, i) => {
        const pageNum = page.page || page.story_page || (i + 1);
        return `
            <div class="editable-page">
                <label>Page ${pageNum}</label>
                <textarea onchange="updatePageText(${i}, this.value)">${page.text || ''}</textarea>
            </div>
        `;
    }).join('');
}

function updatePageText(index, newText) {
    if (state.book.pages[index]) {
        state.book.pages[index].text = newText;
        saveState();
    }
}

function updateTitle(newTitle) {
    state.book.title = newTitle;
    state.slug = generateSlug(newTitle);
    state.book.slug = state.slug;
    saveState();
}

// Wrapper that shows confirmation before regenerating
function regenerateStoryAndScenes() {
    showConfirmModal(
        'Regenerate Story?',
        'This will replace your current story and all scene descriptions. Any edits you\'ve made will be lost.',
        doRegenerateStoryAndScenes
    );
}

async function doRegenerateStoryAndScenes() {
    // Show loading (Phase 3 elements)
    document.getElementById('phase3Content').classList.add('hidden');
    document.getElementById('phase3Actions').classList.add('hidden');
    document.getElementById('phase3Loading').classList.remove('hidden');
    document.getElementById('phase3LoadingText').textContent = 'Regenerating story...';

    try {
        // Regenerate story
        const response = await fetch('/api/generate-story', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: buildStoryPrompt()
            })
        });

        if (!response.ok) {
            throw new Error('Failed to generate story');
        }

        const book = await response.json();
        state.slug = generateSlug(book.title);
        state.book = book;
        state.book.slug = state.slug;
        state.book.level = state.formData.level;
        state.book.setting = state.formData.setting;
        state.book.storyType = state.formData.storyType;
        state.book.artStyle = state.formData.artStyle;
        saveState();

        // Regenerate scenes
        document.getElementById('phase3LoadingText').textContent = 'Regenerating scene descriptions...';
        await generateScenesInternal();

        renderPhase2Content();

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to regenerate. Please try again.');
        renderPhase2Content();
    }
}

async function generateScenes() {
    document.getElementById('phase3Content').classList.add('hidden');
    document.getElementById('phase3Actions').classList.add('hidden');
    document.getElementById('phase3Loading').classList.remove('hidden');
    document.getElementById('phase3LoadingText').textContent = 'Generating scene descriptions...';

    try {
        await generateScenesInternal();
        renderPhase2Content();
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate scenes. Please try again.');
        renderPhase2Content();
    }
}

function renderSceneList() {
    const container = document.getElementById('sceneList');

    container.innerHTML = state.book.pages.map((page, i) => {
        const validation = validateScene(page.scene);
        const statusClass = validation.valid ? 'valid' : 'invalid';
        const pageNum = page.page || page.story_page || (i + 1);
        // Clean text - remove XML tags for display
        const displayText = (page.text || '').replace(/<\/?line>/g, ' ').replace(/\s+/g, ' ').trim();

        return `
            <div class="scene-item ${statusClass}" data-page="${i}">
                <div class="scene-header">
                    <strong>Page ${pageNum}</strong>
                    <div style="display: flex; gap: var(--space-xs); align-items: center;">
                        <span class="scene-status ${statusClass}">${validation.valid ? 'Valid' : validation.issues[0]}</span>
                        <button class="btn btn-sm btn-ghost" onclick="regenerateSingleScene(${i})" title="Regenerate this scene">&#x21bb;</button>
                    </div>
                </div>
                <div class="scene-page-text">"${displayText}"</div>
                <textarea class="scene-textarea" onchange="updateScene(${i}, this.value)"
                    placeholder="Describe what we see in this illustration...">${page.scene || ''}</textarea>
            </div>
        `;
    }).join('');
}

function renderMetadataPanels() {
    // Render word list
    const wordList = state.book.word_list || {};
    const soundOut = wordList.sound_out || [];
    const sight = wordList.sight || [];
    const heart = wordList.heart || [];
    const totalWords = soundOut.length + sight.length + heart.length;

    document.getElementById('wordListCount').textContent = `${totalWords} words`;
    document.getElementById('wordListSoundOut').innerHTML = soundOut.length
        ? soundOut.map(w => `<span class="word-chip">${w}</span>`).join('')
        : '<span class="hint">None</span>';
    document.getElementById('wordListSight').innerHTML = sight.length
        ? sight.map(w => `<span class="word-chip">${w}</span>`).join('')
        : '<span class="hint">None</span>';
    document.getElementById('wordListHeart').innerHTML = heart.length
        ? heart.map(w => `<span class="word-chip">${w}</span>`).join('')
        : '<span class="hint">None</span>';

    // Render story bible
    const bible = state.book.story_bible || {};

    document.getElementById('biblePremise').textContent = bible.premise || 'Not generated';

    const characters = bible.characters || [];
    document.getElementById('bibleCharacters').innerHTML = characters.length
        ? characters.map(c => `
            <div class="bible-character">
                <div class="bible-character-name">${c.name} (${c.role || 'character'})</div>
                <div class="bible-character-desc">${c.description || ''}</div>
            </div>
        `).join('')
        : '<span class="hint">No characters defined</span>';

    const themes = bible.themes || [];
    document.getElementById('bibleThemes').innerHTML = themes.length
        ? themes.map(t => `<span class="bible-chip">${t}</span>`).join('')
        : '<span class="hint">No themes defined</span>';

    document.getElementById('bibleEmotionalArc').textContent = bible.emotional_arc || 'Not defined';
}

async function regenerateSingleScene(index) {
    const page = state.book.pages[index];
    const item = document.querySelector(`.scene-item[data-page="${index}"]`);
    const textarea = item.querySelector('.scene-textarea');

    textarea.disabled = true;
    textarea.placeholder = 'Regenerating...';

    try {
        // Create a mini-book with just this page for the API
        const miniBook = {
            ...state.book,
            pages: [page]
        };

        const response = await fetch('/api/generate-scenes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ book: miniBook })
        });

        if (!response.ok) throw new Error('Failed to regenerate scene');

        const result = await response.json();
        if (result.pages && result.pages[0]) {
            state.book.pages[index].scene = result.pages[0].scene;
            saveState();
            renderSceneList();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to regenerate scene');
        textarea.disabled = false;
        textarea.placeholder = 'Describe what we see in this illustration...';
    }
}

function updateScene(index, value) {
    state.book.pages[index].scene = value;
    saveState();

    // Update validation status
    const item = document.querySelector(`.scene-item[data-page="${index}"]`);
    const validation = validateScene(value);
    const statusClass = validation.valid ? 'valid' : 'invalid';
    item.className = `scene-item ${statusClass}`;
    item.querySelector('.scene-status').className = `scene-status ${statusClass}`;
    item.querySelector('.scene-status').textContent = validation.valid ? 'Valid' : validation.issues[0];
}

function validateScene(scene) {
    const issues = [];

    if (!scene || scene.length < 50) {
        issues.push('Too short');
    }

    if (scene && scene.toLowerCase().includes('illustration for:')) {
        issues.push('Placeholder text');
    }

    // Check for negations (excluding the required "NO TEXT, NO WORDS, NO LETTERS" suffix)
    if (scene) {
        // Remove the required suffix before checking for negations
        const sceneWithoutSuffix = scene.replace(/NO TEXT,?\s*NO WORDS,?\s*NO LETTERS\.?/gi, '');
        const negationPattern = /\b(no|not|without|never)\b/gi;
        if (negationPattern.test(sceneWithoutSuffix)) {
            issues.push('Contains negation');
        }
    }

    return {
        valid: issues.length === 0,
        issues
    };
}

function validateAndApprovePhase2() {
    const issues = [];

    state.book.pages.forEach((page, i) => {
        const validation = validateScene(page.scene);
        if (!validation.valid) {
            issues.push(`Page ${page.page}: ${validation.issues.join(', ')}`);
        }
    });

    if (issues.length > 0) {
        document.getElementById('validationMessages').classList.remove('hidden');
        document.getElementById('validationList').innerHTML = issues.map(i => `<li>${i}</li>`).join('');
        return;
    }

    document.getElementById('validationMessages').classList.add('hidden');
    state.phaseStatus[2] = 'complete';
    state.checkpointApprovals[2] = { approved: true, timestamp: new Date().toISOString() };
    saveState();
    saveToSupabase(); // Persist to database
    goToPhase(3);
}

// Alias for Phase 3 button (Story Review -> Reference)
async function validateAndApprovePhase3() {
    // Phase 3 is Story Review, validates scenes and proceeds to Phase 4 (Reference)
    const loadingEl = document.getElementById('phase3Loading');
    const loadingText = document.getElementById('phase3LoadingText');

    // Show loading
    loadingEl.classList.remove('hidden');
    loadingText.textContent = 'Validating book with AI...';

    try {
        // Use LLM-based validation
        const response = await fetch('/api/validate-book-v2', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ book: state.book })
        });

        const result = await response.json();
        loadingEl.classList.add('hidden');

        if (!result.valid) {
            const allIssues = [...result.errors, ...result.warnings];
            document.getElementById('validationMessages').classList.remove('hidden');
            document.getElementById('validationList').innerHTML = allIssues.map(i => `<li>${i}</li>`).join('');
            if (result.assessment) {
                const assessmentEl = document.createElement('p');
                assessmentEl.style.marginTop = '0.5rem';
                assessmentEl.style.fontStyle = 'italic';
                assessmentEl.textContent = result.assessment;
                document.getElementById('validationList').appendChild(assessmentEl);
            }
            return;
        }

        document.getElementById('validationMessages').classList.add('hidden');
        state.phaseStatus[3] = 'complete';
        state.checkpointApprovals[3] = { approved: true, timestamp: new Date().toISOString() };
        saveState();
        saveToSupabase();
        goToPhase(4);

    } catch (error) {
        console.error('Validation error:', error);
        loadingEl.classList.add('hidden');
        // Fall back to local validation on error
        const issues = [];
        state.book.pages.forEach((page, i) => {
            const validation = validateScene(page.scene);
            if (!validation.valid) {
                issues.push(`Page ${page.page}: ${validation.issues.join(', ')}`);
            }
        });

        if (issues.length > 0) {
            document.getElementById('validationMessages').classList.remove('hidden');
            document.getElementById('validationList').innerHTML = issues.map(i => `<li>${i}</li>`).join('');
            return;
        }

        document.getElementById('validationMessages').classList.add('hidden');
        state.phaseStatus[3] = 'complete';
        state.checkpointApprovals[3] = { approved: true, timestamp: new Date().toISOString() };
        saveState();
        saveToSupabase();
        goToPhase(4);
    }
}

// Generate/enhance all scenes using LLM
async function regenerateAllScenes() {
    const loadingEl = document.getElementById('phase3Loading');
    const loadingText = document.getElementById('phase3LoadingText');

    loadingEl.classList.remove('hidden');
    loadingText.textContent = 'Generating scenes with AI...';

    try {
        const response = await fetch('/api/enhance-scenes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ book: state.book, mode: 'generate' })
        });

        const result = await response.json();

        if (result.scenes) {
            // Update book with new scenes
            result.scenes.forEach(s => {
                const page = state.book.pages.find(p => p.page === s.page);
                if (page) {
                    page.scene = s.scene;
                }
            });

            // Update character description if provided
            if (result.characterDescription) {
                state.book.characterDescription = result.characterDescription;
            }

            saveState();
            renderPhase2Content(); // Re-render to show new scenes
        }

    } catch (error) {
        console.error('Scene generation error:', error);
        alert('Failed to generate scenes: ' + error.message);
    }

    loadingEl.classList.add('hidden');
}

// ===================
// PHASE 3: REFERENCE
// ===================

async function renderReferencePhase() {
    const promptEl = document.getElementById('referencePrompt');
    const loadingEl = document.getElementById('phase4Loading');
    const loadingTextEl = document.getElementById('phase4LoadingText');

    // Generate prompt using LLM if we don't have one yet (or if it looks like the old generic template)
    const needsNewPrompt = !state.book.referencePrompt ||
        state.book.referencePrompt.includes('{title}') ||
        state.book.referencePrompt.includes('the character') ||
        state.book.referencePrompt.includes('{name}');

    if (needsNewPrompt) {
        // Show loading state
        loadingEl.classList.remove('hidden');
        loadingTextEl.textContent = 'Generating reference prompt with AI...';
        promptEl.value = 'Generating prompt...';

        try {
            const response = await fetch('/api/generate-ref-prompt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ book: state.book })
            });

            const result = await response.json();

            if (result.success && result.prompt) {
                state.book.referencePrompt = result.prompt;
                saveState();
            } else {
                // Fall back to old method if API fails
                console.warn('API failed, falling back to template:', result.error);
                state.book.referencePrompt = buildReferencePrompt();
            }
        } catch (error) {
            console.error('Error generating prompt:', error);
            // Fall back to old method
            state.book.referencePrompt = buildReferencePrompt();
        }

        loadingEl.classList.add('hidden');
    }

    // Populate generated prompt
    promptEl.value = state.book.referencePrompt;

    // Populate story data preview (for debugging/transparency)
    const storyDataEl = document.getElementById('storyDataPreview');
    if (storyDataEl) {
        // Show book summary instead of extracted data
        const summary = {
            title: state.book.title,
            setting: state.book.setting,
            characterName: state.book.characterName,
            pageCount: state.book.pages?.length || 0,
            firstScene: state.book.pages?.[0]?.scene?.substring(0, 100) + '...'
        };
        storyDataEl.textContent = JSON.stringify(summary, null, 2);
    }

    // Populate multi-ref prompt editors
    const styleGuideEl = document.getElementById('styleGuidePromptTextarea');
    const openingEl = document.getElementById('openingScenesPromptTextarea');
    const closingEl = document.getElementById('closingScenesPromptTextarea');

    if (styleGuideEl) {
        // Use the same LLM-generated prompt for style guide
        styleGuideEl.value = state.prompts.styleGuide || state.book.referencePrompt;
    }
    if (openingEl) {
        openingEl.value = state.prompts.openingScenes || buildDefaultOpeningScenesPrompt();
    }
    if (closingEl) {
        closingEl.value = state.prompts.closingScenes || buildDefaultClosingScenesPrompt();
    }

    // Restore strategy toggle state
    setRefStrategy(state.refStrategy || 'single', false);

    // Show existing reference image if we have one (single strategy)
    if (state.referenceImage && state.refStrategy === 'single') {
        showReferenceImage(state.referenceImage);
        document.getElementById('approveRefBtn').disabled = false;
    }

    // Show existing multi-ref images
    if (state.refStrategy === 'multi') {
        renderMultiRefState();
    }
}

function setRefStrategy(strategy, save = true) {
    state.refStrategy = strategy;

    // Update toggle buttons
    document.querySelectorAll('.strategy-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.strategy === strategy);
    });

    // Show/hide views
    document.getElementById('singleRefView').classList.toggle('hidden', strategy !== 'single');
    document.getElementById('multiRefView').classList.toggle('hidden', strategy !== 'multi');

    // Update approve button state
    updateApproveButtonState();

    if (save) saveState();
}

function updateApproveButtonState() {
    const btn = document.getElementById('approveRefBtn');
    if (state.refStrategy === 'single') {
        btn.disabled = !state.referenceImage;
    } else {
        // Multi: need all 3 sheets
        const hasAll = state.multiRefs.styleGuide && state.multiRefs.openingScenes && state.multiRefs.closingScenes;
        btn.disabled = !hasAll;
    }
}

function renderMultiRefState() {
    ['styleGuide', 'openingScenes', 'closingScenes'].forEach(sheet => {
        const url = state.multiRefs[sheet];
        const capitalizedSheet = sheet.charAt(0).toUpperCase() + sheet.slice(1);
        const imgContainer = document.getElementById(`img${capitalizedSheet}`);
        const statusEl = document.getElementById(`status${capitalizedSheet}`);

        if (url) {
            imgContainer.innerHTML = `<img src="${url}" alt="${sheet}">`;
            statusEl.textContent = 'Complete';
            statusEl.className = 'card-status complete';
        }
    });

    // Enable cascade buttons based on what's generated
    if (state.multiRefs.styleGuide) {
        document.getElementById('btnOpeningScenes').disabled = false;
        document.getElementById('btnClosingScenes').disabled = false;
    }

    updateApproveButtonState();
}

// Extract character details from scene descriptions
function extractCharacterFromScenes() {
    if (!state.book?.pages?.length) {
        return { name: 'the character', description: '', traits: [] };
    }

    // Scene descriptions typically start with "Shot type: CharacterName, description, action..."
    // e.g. "Wide shot: Spot, fluffy gray and white cat with distinctive black spots, stretching..."
    const firstScene = state.book.pages[0]?.scene || '';

    // Try to extract character name and description from first scene
    // Pattern: "Shot type: Name, description (species/animal type with features), action..."
    // e.g. "Wide shot: Spot, fluffy gray and white cat with distinctive black spots, stretching..."
    // e.g. "Medium shot: Little Bear, a small brown bear with round ears, walking..."

    // First prefer explicit characterName from book data if set
    let name = state.book.characterName || '';
    let description = '';

    // Regex handles multi-word names: "Shot: Name Name, description,"
    // Captures: group 1 = character name (words before first comma after colon)
    //           group 2 = description (text after first comma until next comma or -ing verb)
    const sceneMatch = firstScene.match(/(?:shot:\s*)([^,]+),\s*([^,]+)/i);

    if (sceneMatch) {
        // Only use extracted name if we don't have one from book data
        if (!name) {
            name = sceneMatch[1].trim();
        }
        // Clean up description - stop at action verbs (-ing words that start actions)
        let desc = sceneMatch[2].trim();
        desc = desc.replace(/\s+\b\w+ing\b.*$/, '');
        description = desc;
    }

    // Final fallback
    if (!name) name = 'the character';

    // Collect unique physical traits from all scenes (eyes, nose, fur, etc.)
    const traits = new Set();
    const traitPatterns = [
        /\b(amber|blue|green|brown|golden)\s+eyes\b/gi,
        /\b(pink|black|brown)\s+nose\b/gi,
        /\b(fluffy|soft|sleek|furry)\s+(belly|tail|fur|coat)\b/gi,
        /\b(spotted|striped|tabby|calico)\b/gi,
        /\b(extra fluffy|bushy|long|short)\s+\w+/gi
    ];

    for (const page of state.book.pages) {
        const scene = page.scene || '';
        for (const pattern of traitPatterns) {
            const matches = scene.match(pattern);
            if (matches) {
                matches.forEach(m => traits.add(m.toLowerCase()));
            }
        }
    }

    return { name, description, traits: Array.from(traits) };
}

// ===================
// METAPROMPT SYSTEM
// ===================

// Default metaprompt template for reference sheets
// Placeholders: {title}, {name}, {NAME}, {description}, {traits}, {setting}
const DEFAULT_REFERENCE_METAPROMPT = `Create a 3x3 grid style reference sheet for "{title}":

GRID LAYOUT (9 panels total):
Row 1: [1] {name} front view, [2] {name} expressions (happy, surprised, worried), [3] {name} in action pose
Row 2: [4] Secondary elements/props from story, [5] KEY SCENE: {name} in main story moment, [6] Important objects/items
Row 3: [7] {setting} background element, [8] Another setting element, [9] {name} resolution pose

CHARACTER DESIGN - {NAME}:
- {description}
- Physical details: {traits}
- Soft, friendly, rounded shapes
- Clear, simple features easy to recognize
- Consistent color palette throughout all panels
- Expressive but simple face

STYLE: Soft watercolor children's book illustration, warm colors, gentle lighting, Eric Carle inspired textures.

IMPORTANT: This is a reference sheet with 9 distinct panels arranged in a 3x3 grid. Each panel should be clearly separated.
NO TEXT, NO WORDS, NO LETTERS anywhere in the image.`;

// Get story data for filling metaprompts
function getStoryData() {
    const { name, description, traits } = extractCharacterFromScenes();
    return {
        title: state.book?.title || "children's book",
        name: name,
        NAME: name.toUpperCase(),
        description: description || 'friendly character with expressive features',
        traits: traits.length > 0 ? traits.join(', ') : 'expressive eyes, distinctive features',
        setting: state.book?.setting || 'the scene'
    };
}

// Fill a metaprompt template with story data
function fillMetaprompt(template, data) {
    let result = template;
    for (const [key, value] of Object.entries(data)) {
        result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), value);
    }
    return result;
}

// Get the current reference metaprompt (custom or default)
function getReferenceMetaprompt() {
    return state.metaprompts?.reference || DEFAULT_REFERENCE_METAPROMPT;
}

// Build the final reference prompt from metaprompt + story data
function buildReferencePrompt() {
    const metaprompt = getReferenceMetaprompt();
    const data = getStoryData();
    return fillMetaprompt(metaprompt, data);
}

// UI: Apply edited metaprompt template and regenerate prompt
function regenerateFromMetaprompt() {
    const metapromptEl = document.getElementById('metapromptTemplate');
    if (metapromptEl) {
        // Save custom metaprompt
        state.metaprompts = state.metaprompts || {};
        state.metaprompts.reference = metapromptEl.value;
        saveState();

        // Regenerate and update the generated prompt
        const newPrompt = buildReferencePrompt();
        state.book.referencePrompt = newPrompt;
        document.getElementById('referencePrompt').value = newPrompt;
    }
}

// UI: Reset metaprompt to default template
function resetMetaprompt() {
    // Clear custom metaprompt
    if (state.metaprompts) {
        state.metaprompts.reference = null;
    }
    saveState();

    // Update UI
    const metapromptEl = document.getElementById('metapromptTemplate');
    if (metapromptEl) {
        metapromptEl.value = DEFAULT_REFERENCE_METAPROMPT;
    }

    // Regenerate prompt with default template
    const newPrompt = buildReferencePrompt();
    state.book.referencePrompt = newPrompt;
    document.getElementById('referencePrompt').value = newPrompt;
}

// Multi-ref prompt builders (3-ref cascade)
// These check for edited values in textareas first, then fall back to defaults

// 1. Style Guide - 9-panel reference using same prompt as single ref
function buildStyleGuidePrompt() {
    // Check multi-ref textarea first
    const customPrompt = document.getElementById('styleGuidePromptTextarea')?.value.trim();
    if (customPrompt) {
        state.prompts.styleGuide = customPrompt;
        return customPrompt;
    }
    // Fall back to single ref textarea or default
    return document.getElementById('referencePrompt').value || buildReferencePrompt();
}

// 2. Opening Scenes - first half of the book (9-panel grid)
function buildOpeningScenesPrompt() {
    // Check textarea for custom prompt
    const customPrompt = document.getElementById('openingScenesPromptTextarea')?.value.trim();
    if (customPrompt) {
        state.prompts.openingScenes = customPrompt;
        return customPrompt;
    }
    // Otherwise use default
    return buildDefaultOpeningScenesPrompt();
}

// 3. Closing Scenes - second half of the book (9-panel grid)
function buildClosingScenesPrompt() {
    // Check textarea for custom prompt
    const customPrompt = document.getElementById('closingScenesPromptTextarea')?.value.trim();
    if (customPrompt) {
        state.prompts.closingScenes = customPrompt;
        return customPrompt;
    }
    // Otherwise use default
    return buildDefaultClosingScenesPrompt();
}

async function generateMultiRefSheet(sheetType) {
    // Map sheetType to proper capitalization for element IDs
    const capitalizedType = sheetType.charAt(0).toUpperCase() + sheetType.slice(1);
    const statusEl = document.getElementById(`status${capitalizedType}`);
    const imgContainer = document.getElementById(`img${capitalizedType}`);

    statusEl.textContent = 'Generating...';
    statusEl.className = 'card-status generating';

    // Build prompt and determine model based on sheet type
    let prompt;
    let model;
    let reference = null;

    if (sheetType === 'styleGuide') {
        // Style Guide uses model from dropdown (default nano-banana-pro)
        prompt = buildStyleGuidePrompt();
        const modelSelect = document.getElementById('multiRefModelSelect');
        model = modelSelect ? modelSelect.value : 'nano-banana-pro';
    } else {
        // Opening/Closing Scenes use wan 2.6 I2I with styleGuide as reference
        if (!state.multiRefs.styleGuide) {
            alert('Generate Style Guide first (cascade dependency)');
            statusEl.textContent = 'Pending';
            statusEl.className = 'card-status';
            return;
        }
        prompt = sheetType === 'openingScenes' ? buildOpeningScenesPrompt() : buildClosingScenesPrompt();
        model = 'wan2.6-image';
        reference = state.multiRefs.styleGuide;
    }

    try {
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                model: model,
                reference: reference,
                referenceIsUrl: reference && reference.startsWith('http'),
                slug: state.slug,
                page: `ref-${sheetType}`
            })
        });

        const result = await response.json();

        if (result.pending && result.taskId) {
            await pollForImage(result.taskId, result.statusEndpoint, (url) => {
                state.multiRefs[sheetType] = url;
                saveState();
                imgContainer.innerHTML = `<img src="${url}" alt="${sheetType}">`;
                statusEl.textContent = 'Complete';
                statusEl.className = 'card-status complete';

                // Enable cascade buttons if styleGuide done
                if (sheetType === 'styleGuide') {
                    document.getElementById('btnOpeningScenes').disabled = false;
                    document.getElementById('btnClosingScenes').disabled = false;
                }
                updateApproveButtonState();
            });
        } else if (result.url) {
            state.multiRefs[sheetType] = result.url;
            saveState();
            imgContainer.innerHTML = `<img src="${result.url}" alt="${sheetType}">`;
            statusEl.textContent = 'Complete';
            statusEl.className = 'card-status complete';

            if (sheetType === 'styleGuide') {
                document.getElementById('btnOpeningScenes').disabled = false;
                document.getElementById('btnClosingScenes').disabled = false;
            }
            updateApproveButtonState();
        } else {
            const errMsg = typeof result.error === 'object'
                ? JSON.stringify(result.error)
                : (result.error || 'Failed to generate');
            throw new Error(errMsg);
        }
    } catch (error) {
        console.error('Error:', error);
        statusEl.textContent = 'Error';
        statusEl.className = 'card-status';
        const msg = error.message || (typeof error === 'object' ? JSON.stringify(error) : String(error));
        alert(`Failed to generate ${sheetType}: ${msg}`);
        throw error; // Re-throw to stop cascade
    }
}

async function generateAllMultiRefs() {
    document.getElementById('genAllRefsBtn').disabled = true;
    document.getElementById('phase4LoadingText').textContent = 'Generating style guide (1/3)...';
    document.getElementById('phase4Loading').classList.remove('hidden');
    document.getElementById('phase4Actions').classList.add('hidden');

    try {
        // Step 1: Style Guide (T2I)
        await generateMultiRefSheet('styleGuide');

        // Step 2: Opening Scenes (I2I from style guide)
        document.getElementById('phase4LoadingText').textContent = 'Generating opening scenes (2/3)...';
        await generateMultiRefSheet('openingScenes');

        // Step 3: Closing Scenes (I2I from style guide)
        document.getElementById('phase4LoadingText').textContent = 'Generating closing scenes (3/3)...';
        await generateMultiRefSheet('closingScenes');

    } catch (error) {
        console.error('Error in cascade generation:', error);
        // Cascade stopped - error already shown by generateMultiRefSheet
    }

    document.getElementById('phase4Loading').classList.add('hidden');
    document.getElementById('phase4Actions').classList.remove('hidden');
    document.getElementById('genAllRefsBtn').disabled = false;
}

function generateReference() {
    // Show confirmation if there's already a reference image
    if (state.referenceImage) {
        showConfirmModal(
            'Regenerate Reference Image?',
            'This will replace your existing reference image. Continue?',
            doGenerateReference
        );
    } else {
        doGenerateReference();
    }
}

async function doGenerateReference() {
    const prompt = document.getElementById('referencePrompt').value;
    state.book.referencePrompt = prompt;
    saveState();

    document.getElementById('phase3Actions').classList.add('hidden');
    document.getElementById('phase3Loading').classList.remove('hidden');
    document.getElementById('genRefBtn').disabled = true;

    try {
        // Get selected model from dropdown (default to nano-banana-pro)
        const modelSelect = document.getElementById('refModelSelect');
        const model = modelSelect ? modelSelect.value : 'nano-banana-pro';

        const response = await fetch('/api/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                model: model,
                slug: state.slug,
                page: 'reference'
            })
        });

        const result = await response.json();

        if (result.pending && result.taskId) {
            // Poll for result
            await pollForImage(result.taskId, result.statusEndpoint, (url) => {
                state.referenceImage = url;
                saveState();
                showReferenceImage(url);
            });
        } else if (result.url) {
            state.referenceImage = result.url;
            saveState();
            showReferenceImage(result.url);
        } else {
            const errorMsg = typeof result.error === 'object'
                ? JSON.stringify(result.error)
                : (result.error || 'Failed to generate reference');
            throw new Error(errorMsg);
        }

    } catch (error) {
        console.error('Error:', error);
        const msg = error.message || (typeof error === 'object' ? JSON.stringify(error) : String(error));
        alert('Failed to generate reference image: ' + msg);
    }

    document.getElementById('phase3Loading').classList.add('hidden');
    document.getElementById('phase3Actions').classList.remove('hidden');
    document.getElementById('genRefBtn').disabled = false;
}

function showReferenceImage(url) {
    document.getElementById('referenceImageContainer').innerHTML = `<img src="${url}" alt="Reference image">`;
    document.getElementById('approveRefBtn').disabled = false;
}

function approvePhase3() {
    if (state.refStrategy === 'single') {
        if (!state.referenceImage) {
            alert('Please generate a reference image first.');
            return;
        }
    } else {
        // Multi-ref: need all 3 sheets
        if (!state.multiRefs.closingScenesGuide || !state.multiRefs.openingScenes || !state.multiRefs.closingScenes) {
            alert('Please generate all 3 reference sheets (Characters, Settings, Style).');
            return;
        }
    }

    state.phaseStatus[3] = 'complete';
    state.checkpointApprovals[3] = { approved: true, timestamp: new Date().toISOString() };
    saveState();
    saveToSupabase(); // Persist to database
    goToPhase(4);
}

// ===================
// PHASE 4: PAGE IMAGES
// ===================

function hasValidImage(page) {
    // Check for base64 data URL or file path
    if (!page.image) return false;
    if (page.image.startsWith('data:')) return true;
    if (page.image.startsWith('images/')) return true;
    if (page.image.startsWith('/books/')) return true;
    if (page.image.startsWith('http')) return true;
    return false;
}

function getImageSrc(page) {
    if (!page.image) return null;
    if (page.image.startsWith('data:') || page.image.startsWith('http')) {
        return page.image;
    }
    // Convert relative path to absolute
    if (page.image.startsWith('images/')) {
        return `/books/${page.image}`;
    }
    return page.image;
}

function renderPageImagesGrid() {
    const grid = document.getElementById('pageImagesGrid');
    const lastPageIdx = state.book.pages.length - 1;

    // Cover image card
    const hasCover = state.book.cover_image;
    const coverCard = `
        <div class="page-image-card cover-card" data-type="cover">
            <div class="page-image-container">
                ${hasCover ?
                    `<img src="${state.book.cover_image}" alt="Cover">` :
                    `<div class="page-image-placeholder">Cover</div>`
                }
            </div>
            <div class="page-image-info">
                <span>Cover</span>
                <span class="page-image-status ${hasCover ? 'complete' : 'pending'}">${hasCover ? 'Complete' : 'Pending'}</span>
            </div>
            <div style="padding: 0 var(--space-xs) var(--space-xs);">
                <button class="btn btn-sm btn-ghost" onclick="generateCoverImage()" style="width: 100%;">
                    ${hasCover ? 'Regenerate' : 'Generate'}
                </button>
            </div>
        </div>
    `;

    // Page image cards
    const pageCards = state.book.pages.map((page, i) => {
        const pageNum = page.page || page.story_page || (i + 1);
        const hasImage = hasValidImage(page);
        const imageSrc = getImageSrc(page);
        const status = hasImage ? 'complete' : 'pending';
        const statusLabel = hasImage ? 'Complete' : 'Pending';
        const isEndPage = i === lastPageIdx;

        return `
            <div class="page-image-card ${isEndPage ? 'end-page' : ''}" data-page="${i}">
                <div class="page-image-container">
                    ${hasImage ?
                        `<img src="${imageSrc}" alt="Page ${pageNum}">` :
                        `<div class="page-image-placeholder">Page ${pageNum}</div>`
                    }
                </div>
                <div class="page-image-info">
                    <span>Page ${pageNum}${isEndPage ? ' (End)' : ''}</span>
                    <span class="page-image-status ${status}">${statusLabel}</span>
                </div>
                <div style="padding: 0 var(--space-xs) var(--space-xs);">
                    <button class="btn btn-sm btn-ghost" onclick="generatePageImage(${i})" style="width: 100%;">
                        ${hasImage ? 'Regenerate' : 'Generate'}
                    </button>
                </div>
            </div>
        `;
    }).join('');

    grid.innerHTML = coverCard + pageCards;

    updatePageProgress();
}

function updatePageProgress() {
    const total = state.book.pages.length;
    const complete = state.book.pages.filter(p => hasValidImage(p)).length;

    const progressEl = document.getElementById('pageProgress');
    const finishBtn = document.getElementById('finishBtn');

    if (progressEl) progressEl.textContent = `${complete} / ${total} complete`;
    if (finishBtn) finishBtn.disabled = complete < total;
}

async function generatePageImage(index) {
    const page = state.book.pages[index];
    const card = document.querySelector(`.page-image-card[data-page="${index}"]`);
    const statusEl = card.querySelector('.page-image-status');

    statusEl.className = 'page-image-status generating';
    statusEl.textContent = 'Generating...';

    const prompt = buildPageImagePrompt(page);

    // Build reference payload based on strategy
    let requestBody;
    if (state.refStrategy === 'multi' && state.multiRefs.styleGuide) {
        // Multi-ref: pass array of references (up to 3)
        const refArray = [
            state.multiRefs.styleGuide,
            state.multiRefs.openingScenes,
            state.multiRefs.closingScenes
        ].filter(Boolean);

        requestBody = {
            prompt: prompt,
            model: 'wan2.6-image',
            reference: refArray, // API accepts array for wan2.6-image
            referenceIsUrl: true,
            slug: state.slug,
            page: page.page
        };
    } else {
        // Single ref: use original format
        requestBody = {
            prompt: prompt,
            model: 'wan2.6-image',
            reference: state.referenceImage,
            referenceIsUrl: state.referenceImage && state.referenceImage.startsWith('http'),
            slug: state.slug,
            page: page.page
        };
    }

    try {
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        const result = await response.json();

        if (result.pending && result.taskId) {
            await pollForImage(result.taskId, result.statusEndpoint, (url) => {
                page.image = url;
                saveState();
                updatePageImageCard(index, url);
            });
        } else if (result.url) {
            page.image = result.url;
            saveState();
            updatePageImageCard(index, result.url);
        } else {
            throw new Error(result.error || 'Failed to generate image');
        }

    } catch (error) {
        console.error('Error:', error);
        statusEl.className = 'page-image-status error';
        statusEl.textContent = 'Error';
    }
}

function buildPageImagePrompt(page) {
    return `Single scene illustration: ${page.scene}

CHARACTERS (draw EXACTLY as described):
${state.book.characterName} the ${state.book.character} - soft, rounded, friendly appearance with expressive face

COMPOSITION: One cohesive illustration filling the entire canvas.
Full-bleed image with the scene filling edge to edge.

STYLE: Soft watercolor children's book illustration, warm colors, gentle lighting, matching the reference style.

CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere. Pure illustration only.`;
}

function updatePageImageCard(index, url) {
    const card = document.querySelector(`.page-image-card[data-page="${index}"]`);
    const container = card.querySelector('.page-image-container');
    const statusEl = card.querySelector('.page-image-status');
    const btn = card.querySelector('button');

    container.innerHTML = `<img src="${url}" alt="Page ${state.book.pages[index].page}">`;
    statusEl.className = 'page-image-status complete';
    statusEl.textContent = 'Complete';
    btn.textContent = 'Regenerate';

    updatePageProgress();
}

async function generateCoverImage() {
    const card = document.querySelector('.page-image-card.cover-card');
    const statusEl = card.querySelector('.page-image-status');

    statusEl.className = 'page-image-status generating';
    statusEl.textContent = 'Generating...';

    const coverPrompt = buildCoverImagePrompt();

    // Use reference for consistent style
    let requestBody;
    if (state.refStrategy === 'multi' && state.multiRefs.styleGuide) {
        requestBody = {
            prompt: coverPrompt,
            model: 'wan2.6-image',
            reference: [state.multiRefs.styleGuide].filter(Boolean),
            referenceIsUrl: true,
            slug: state.slug,
            page: 'cover'
        };
    } else {
        requestBody = {
            prompt: coverPrompt,
            model: 'wan2.6-image',
            reference: state.referenceImage,
            referenceIsUrl: state.referenceImage && state.referenceImage.startsWith('http'),
            slug: state.slug,
            page: 'cover'
        };
    }

    try {
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        const result = await response.json();

        if (result.pending && result.taskId) {
            await pollForImage(result.taskId, result.statusEndpoint, (url) => {
                state.book.cover_image = url;
                saveState();
                updateCoverImageCard(url);
            });
        } else if (result.url) {
            state.book.cover_image = result.url;
            saveState();
            updateCoverImageCard(result.url);
        } else {
            throw new Error(result.error || 'Failed to generate cover image');
        }

    } catch (error) {
        console.error('Error:', error);
        statusEl.className = 'page-image-status error';
        statusEl.textContent = 'Error';
    }
}

function buildCoverImagePrompt() {
    const char = state.outline?.character || {};
    const charDesc = char.visual_shorthand || `${char.type || 'character'}`;
    const setting = state.outline?.setting || state.book?.setting || '';

    return `Book cover illustration for "${state.book.title}":

SCENE: ${char.name || 'Main character'} (${charDesc}) prominently featured, looking directly at viewer with warm, inviting expression. Setting: ${setting}

COMPOSITION: Dynamic, eye-catching cover design. Character fills most of the frame, slightly off-center. Vibrant background suggesting the story's world.

STYLE: Soft watercolor children's book illustration, warm inviting colors, friendly and appealing for young readers, matching the reference style.

CRITICAL: NO TEXT, NO WORDS, NO LETTERS, NO TITLE anywhere. Pure illustration only - text will be added separately.`;
}

function updateCoverImageCard(url) {
    const card = document.querySelector('.page-image-card.cover-card');
    const container = card.querySelector('.page-image-container');
    const statusEl = card.querySelector('.page-image-status');
    const btn = card.querySelector('button');

    container.innerHTML = `<img src="${url}" alt="Cover">`;
    statusEl.className = 'page-image-status complete';
    statusEl.textContent = 'Complete';
    btn.textContent = 'Regenerate';

    updatePageProgress();
}

async function generateAllPageImages() {
    document.getElementById('genAllPagesBtn').disabled = true;

    for (let i = 0; i < state.book.pages.length; i++) {
        const page = state.book.pages[i];
        if (!hasValidImage(page)) {
            await generatePageImage(i);
            // Small delay between requests
            await new Promise(r => setTimeout(r, 1000));
        }
    }

    document.getElementById('genAllPagesBtn').disabled = false;
}

// ===================
// POLLING
// ===================

async function pollForImage(taskId, endpoint, onComplete, maxAttempts = 60) {
    for (let i = 0; i < maxAttempts; i++) {
        await new Promise(r => setTimeout(r, 3000));

        try {
            const response = await fetch(`/api/check-status?taskId=${taskId}&endpoint=${encodeURIComponent(endpoint)}`);
            const result = await response.json();

            if (result.completed && result.url) {
                onComplete(result.url);
                return;
            }

            if (!result.success && !result.pending) {
                const errMsg = typeof result.error === 'object'
                    ? JSON.stringify(result.error)
                    : (result.error || 'Task failed');
                throw new Error(errMsg);
            }
        } catch (error) {
            console.error('Poll error:', error);
            throw error;
        }
    }

    throw new Error('Timeout waiting for image');
}

// ===================
// DOWNLOAD
// ===================

function openImagePromptsReview() {
    if (!state.slug) {
        alert('No book loaded.');
        return;
    }
    window.open(`/review/image-prompts.html?book=${state.slug}`, '_blank');
}

function downloadBookJSON() {
    if (!state.book) {
        alert('No book data to download.');
        return;
    }

    const bookData = {
        ...state.book,
        slug: state.slug,
        referenceImage: state.referenceImage,
        refStrategy: state.refStrategy,
        multiRefs: state.refStrategy === 'multi' ? state.multiRefs : undefined,
        exportedAt: new Date().toISOString()
    };

    const dataStr = JSON.stringify(bookData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `${state.slug || 'book'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ===================
// PHASE 5: REVIEW & PUBLISH
// ===================

function approvePhase4() {
    // Phase 4 is Reference - check that reference images are generated
    if (state.refStrategy === 'single') {
        if (!state.referenceImage) {
            alert('Please generate a reference image first.');
            return;
        }
    } else {
        // Multi-ref: need at least the style guide
        if (!state.multiRefs?.styleGuide) {
            alert('Please generate at least the style guide reference sheet.');
            return;
        }
    }

    state.phaseStatus[4] = 'complete';
    state.checkpointApprovals[4] = { approved: true, timestamp: new Date().toISOString() };
    saveState();
    saveToSupabase();
    goToPhase(5);
}

function approvePhase5() {
    // Phase 5 is Page Images - check that at least some images are generated
    const pagesWithImages = state.book.pages.filter(p => hasValidImage(p)).length;
    if (pagesWithImages === 0) {
        alert('Please generate at least some page images before continuing.');
        return;
    }

    state.phaseStatus[5] = 'complete';
    state.checkpointApprovals[5] = { approved: true, timestamp: new Date().toISOString() };
    saveState();
    saveToSupabase();
    goToPhase(6);
}

function renderReviewPhase() {
    // Update summary
    const summary = document.getElementById('reviewSummary');
    const pagesWithImages = state.book.pages.filter(p => hasValidImage(p)).length;
    const totalPages = state.book.pages.length;
    const hasCover = state.book.cover_image ? 'Yes' : 'No';

    summary.innerHTML = `
        <p><strong>Title:</strong> ${state.book.title || 'Untitled'}</p>
        <p><strong>Level:</strong> ${state.book.level || 'Unknown'}</p>
        <p><strong>Pages:</strong> ${totalPages} (${pagesWithImages} with images)</p>
        <p><strong>Cover:</strong> ${hasCover}</p>
        <p><strong>Slug:</strong> ${state.slug}</p>
    `;

    // Update word list
    const wordList = state.book.word_list || {};
    const soundOut = wordList.sound_out || [];
    const sight = wordList.sight || [];
    const heart = wordList.heart || [];

    document.getElementById('reviewSoundOut').innerHTML = soundOut.length
        ? soundOut.map(w => `<span class="word-chip">${w}</span>`).join('')
        : '<span class="hint">None</span>';
    document.getElementById('reviewSight').innerHTML = sight.length
        ? sight.map(w => `<span class="word-chip">${w}</span>`).join('')
        : '<span class="hint">None</span>';
    document.getElementById('reviewHeart').innerHTML = heart.length
        ? heart.map(w => `<span class="word-chip">${w}</span>`).join('')
        : '<span class="hint">None</span>';

    // Update story bible
    const bible = state.book.story_bible || {};

    document.getElementById('reviewPremise').textContent = bible.premise || 'Not generated';

    const themes = bible.themes || [];
    document.getElementById('reviewThemes').innerHTML = themes.length
        ? themes.map(t => `<span class="bible-chip">${t}</span>`).join('')
        : '<span class="hint">None</span>';

    document.getElementById('reviewEmotionalArc').textContent = bible.emotional_arc || 'Not defined';

    const characters = bible.characters || [];
    document.getElementById('reviewCharacters').innerHTML = characters.length
        ? characters.map(c => `<div class="bible-character-item"><strong>${c.name}</strong> (${c.role || 'character'}): ${c.description || '-'}</div>`).join('')
        : '<span class="hint">No characters defined</span>';

    // Update links
    document.getElementById('readerLink').href = `/reader.html?book=${state.slug}`;
    document.getElementById('editLink').href = `/reader.html?book=${state.slug}&mode=edit`;

    // Reset checklist
    document.querySelectorAll('.checklist input[type="checkbox"]').forEach(cb => cb.checked = false);
}

async function saveAndPublish() {
    // Prepare book with reference image(s)
    const finalBook = {
        ...state.book,
        referenceImage: state.referenceImage,
        refStrategy: state.refStrategy,
        multiRefs: state.refStrategy === 'multi' ? state.multiRefs : undefined,
        publishedAt: new Date().toISOString(),
        createdWith: 'wizard'
    };

    try {
        const response = await fetch('/api/save-book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                slug: state.slug,
                fullBook: finalBook
            })
        });

        if (!response.ok) {
            const result = await response.json();
            alert('Could not save book: ' + (result.error || 'Unknown error'));
            return;
        }

        alert('Book saved to library successfully!');
        state.book = finalBook;
        saveState();

    } catch (error) {
        console.error('Save error:', error);
        alert('Error saving book: ' + error.message);
    }
}

// ===================
// FINISH
// ===================

async function finishWizard() {
    // Prepare book with reference image(s)
    const finalBook = {
        ...state.book,
        referenceImage: state.referenceImage,
        refStrategy: state.refStrategy,
        multiRefs: state.refStrategy === 'multi' ? state.multiRefs : undefined,
        createdAt: new Date().toISOString(),
        createdWith: 'wizard'
    };

    // Save the book JSON to Supabase
    try {
        const response = await fetch('/api/save-book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                slug: state.slug,
                fullBook: finalBook
            })
        });

        if (!response.ok) {
            const result = await response.json();
            console.warn('Could not save book to server:', result.error || 'Unknown error');
            // Still continue - book is in localStorage
        } else {
            console.log('Book saved to Supabase successfully');
        }
    } catch (error) {
        console.warn('Could not save book:', error);
    }

    // Update local state
    state.book = finalBook;
    state.phaseStatus[5] = 'complete';
    state.checkpointApprovals[5] = { approved: true, timestamp: new Date().toISOString() };
    saveState();

    // Redirect to reader
    window.location.href = `/reader.html?book=${state.slug}`;
}

// ===================
// CHECKPOINT MODAL
// ===================

let checkpointCallback = null;

function showCheckpoint(title, message, callback) {
    document.getElementById('checkpointTitle').textContent = title;
    document.getElementById('checkpointMessage').textContent = message;
    document.getElementById('checkpointModal').classList.add('visible');
    checkpointCallback = callback;
}

function closeCheckpoint() {
    document.getElementById('checkpointModal').classList.remove('visible');
    checkpointCallback = null;
}

function confirmCheckpoint() {
    closeCheckpoint();
    if (checkpointCallback) {
        checkpointCallback();
    }
}

// ===================
// INIT
// ===================

init();
