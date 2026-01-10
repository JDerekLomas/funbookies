/**
 * ReadingPlanet Student Picker
 *
 * A mature, clean modal for selecting or creating student profiles.
 * Designed for older students - no childish elements.
 */

const AVATAR_OPTIONS = [
    { id: 'astronaut', emoji: '🧑‍🚀', label: 'Astronaut' },
    { id: 'scientist', emoji: '🧑‍🔬', label: 'Scientist' },
    { id: 'artist', emoji: '🧑‍🎨', label: 'Artist' },
    { id: 'athlete', emoji: '🏃', label: 'Athlete' },
    { id: 'musician', emoji: '🎸', label: 'Musician' },
    { id: 'gamer', emoji: '🎮', label: 'Gamer' },
    { id: 'reader', emoji: '📚', label: 'Reader' },
    { id: 'explorer', emoji: '🧭', label: 'Explorer' },
];

const GENRE_OPTIONS = [
    { id: 'sports', label: 'Sports', emoji: '🏀' },
    { id: 'science', label: 'Science', emoji: '🔬' },
    { id: 'technology', label: 'Technology', emoji: '💻' },
    { id: 'music', label: 'Music', emoji: '🎵' },
    { id: 'gaming', label: 'Gaming', emoji: '🎮' },
    { id: 'history', label: 'History', emoji: '📜' },
    { id: 'nature', label: 'Nature', emoji: '🌿' },
    { id: 'mystery', label: 'Mystery', emoji: '🔍' },
];

const AVATAR_COLORS = [
    '#3b82f6', // blue
    '#8b5cf6', // purple
    '#ec4899', // pink
    '#ef4444', // red
    '#f59e0b', // amber
    '#22c55e', // green
    '#14b8a6', // teal
    '#06b6d4', // cyan
];

class StudentPicker {
    constructor(options = {}) {
        this.options = {
            title: options.title || 'Select Profile',
            allowCreate: options.allowCreate !== false,
            allowSkip: options.allowSkip || false,
            onSelect: options.onSelect || null,
        };
        this.modal = null;
        this.resolve = null;
        this.selectedAvatar = AVATAR_OPTIONS[0];
        this.selectedColor = AVATAR_COLORS[0];
        this.selectedGenres = [];
        this.createStep = 1; // 1: name/grade, 2: avatar, 3: preferences
    }

    /**
     * Show the picker modal
     * @returns {Promise<object|null>} Selected student or null if skipped
     */
    async show() {
        // Wait for DB to be ready
        if (window.ReadingPlanetDB) {
            await window.ReadingPlanetDB.ready;
        }

        return new Promise(async (resolve) => {
            this.resolve = resolve;

            // Check for existing session
            const session = this.getSession();
            if (session?.currentStudentId) {
                const student = await window.ReadingPlanetDB?.getStudent(session.currentStudentId);
                if (student) {
                    resolve(student);
                    return;
                }
            }

            // Get students
            const students = await window.ReadingPlanetDB?.getStudents() || [];

            // If only one student, auto-select
            if (students.length === 1 && !this.options.allowCreate) {
                this.saveSession(students[0].id);
                resolve(students[0]);
                return;
            }

            // Show modal
            this.render(students);
        });
    }

    render(students) {
        // Create modal overlay
        this.modal = document.createElement('div');
        this.modal.className = 'sp-overlay';
        this.modal.innerHTML = `
            <div class="sp-modal">
                <div class="sp-header">
                    <h2 class="sp-title">${this.options.title}</h2>
                    ${this.options.allowSkip ? `
                        <button class="sp-skip" aria-label="Skip">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 6L6 18M6 6l12 12"/>
                            </svg>
                        </button>
                    ` : ''}
                </div>

                <div class="sp-content">
                    ${students.length > 0 ? `
                        <div class="sp-students">
                            ${students.map(s => this.renderStudent(s)).join('')}
                        </div>
                    ` : `
                        <div class="sp-empty">
                            <p>No profiles yet. Create one to get started.</p>
                        </div>
                    `}

                    ${this.options.allowCreate ? `
                        <div class="sp-create">
                            <button class="sp-create-btn" id="spCreateBtn">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="10"/>
                                    <path d="M12 8v8M8 12h8"/>
                                </svg>
                                <span>Create New Profile</span>
                            </button>
                        </div>

                        <div class="sp-create-form hidden" id="spCreateForm">
                            <!-- Step 1: Name and Grade -->
                            <div class="sp-step" id="spStep1">
                                <div class="sp-step-header">
                                    <span class="sp-step-num">1 of 3</span>
                                    <span class="sp-step-title">Basic Info</span>
                                </div>
                                <div class="sp-form-group">
                                    <label class="sp-label">Name</label>
                                    <input type="text" class="sp-input" id="spNameInput" placeholder="Enter your name" maxlength="30">
                                </div>
                                <div class="sp-form-group">
                                    <label class="sp-label">Grade Level</label>
                                    <select class="sp-select" id="spGradeInput">
                                        <option value="4">4th Grade</option>
                                        <option value="5">5th Grade</option>
                                        <option value="6" selected>6th Grade</option>
                                        <option value="7">7th Grade</option>
                                        <option value="8">8th Grade</option>
                                        <option value="9">9th Grade</option>
                                        <option value="10">10th Grade</option>
                                    </select>
                                </div>
                                <div class="sp-form-actions">
                                    <button class="sp-btn sp-btn-ghost" id="spCancelCreate">Cancel</button>
                                    <button class="sp-btn sp-btn-primary" id="spNextStep1">Next</button>
                                </div>
                            </div>

                            <!-- Step 2: Avatar -->
                            <div class="sp-step hidden" id="spStep2">
                                <div class="sp-step-header">
                                    <span class="sp-step-num">2 of 3</span>
                                    <span class="sp-step-title">Choose Your Avatar</span>
                                </div>
                                <div class="sp-avatar-preview" id="spAvatarPreview">
                                    <div class="sp-avatar-large" id="spAvatarLarge">🧑‍🚀</div>
                                </div>
                                <div class="sp-avatar-grid" id="spAvatarGrid">
                                    ${AVATAR_OPTIONS.map((a, i) => `
                                        <button class="sp-avatar-option ${i === 0 ? 'selected' : ''}" data-avatar="${a.id}" data-emoji="${a.emoji}">
                                            ${a.emoji}
                                        </button>
                                    `).join('')}
                                </div>
                                <div class="sp-form-group">
                                    <label class="sp-label">Color</label>
                                    <div class="sp-color-grid" id="spColorGrid">
                                        ${AVATAR_COLORS.map((c, i) => `
                                            <button class="sp-color-option ${i === 0 ? 'selected' : ''}" data-color="${c}" style="background-color: ${c}"></button>
                                        `).join('')}
                                    </div>
                                </div>
                                <div class="sp-form-actions">
                                    <button class="sp-btn sp-btn-ghost" id="spBackStep2">Back</button>
                                    <button class="sp-btn sp-btn-primary" id="spNextStep2">Next</button>
                                </div>
                            </div>

                            <!-- Step 3: Interests -->
                            <div class="sp-step hidden" id="spStep3">
                                <div class="sp-step-header">
                                    <span class="sp-step-num">3 of 3</span>
                                    <span class="sp-step-title">What do you like to read about?</span>
                                </div>
                                <p class="sp-hint">Select 2-4 topics that interest you</p>
                                <div class="sp-genre-grid" id="spGenreGrid">
                                    ${GENRE_OPTIONS.map(g => `
                                        <button class="sp-genre-option" data-genre="${g.id}">
                                            <span class="sp-genre-emoji">${g.emoji}</span>
                                            <span class="sp-genre-label">${g.label}</span>
                                        </button>
                                    `).join('')}
                                </div>
                                <div class="sp-form-actions">
                                    <button class="sp-btn sp-btn-ghost" id="spBackStep3">Back</button>
                                    <button class="sp-btn sp-btn-primary" id="spConfirmCreate">Create Profile</button>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        // Add styles
        this.addStyles();

        // Add to DOM
        document.body.appendChild(this.modal);

        // Animate in
        requestAnimationFrame(() => {
            this.modal.classList.add('active');
        });

        // Bind events
        this.bindEvents(students);
    }

    renderStudent(student) {
        // Check if avatar is an emoji or initials
        const isEmoji = student.avatar && /\p{Emoji}/u.test(student.avatar);
        const displayAvatar = isEmoji ? student.avatar : (student.avatar || student.name.slice(0, 2).toUpperCase());
        const color = student.avatarColor || '#3b82f6';
        const fontSize = isEmoji ? '1.5rem' : '1rem';

        return `
            <button class="sp-student" data-id="${student.id}">
                <div class="sp-avatar" style="background-color: ${color}; font-size: ${fontSize}">
                    ${displayAvatar}
                </div>
                <div class="sp-student-info">
                    <span class="sp-student-name">${student.name}</span>
                    <span class="sp-student-meta">Grade ${student.grade} • Level ${student.stats?.level || 1}</span>
                </div>
                <svg class="sp-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 18l6-6-6-6"/>
                </svg>
            </button>
        `;
    }

    bindEvents(students) {
        // Student selection
        this.modal.querySelectorAll('.sp-student').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const student = students.find(s => s.id === id);
                if (student) {
                    this.selectStudent(student);
                }
            });
        });

        // Skip button
        const skipBtn = this.modal.querySelector('.sp-skip');
        if (skipBtn) {
            skipBtn.addEventListener('click', () => this.close(null));
        }

        // Create button
        const createBtn = this.modal.querySelector('#spCreateBtn');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.showCreateForm());
        }

        // Cancel create
        const cancelBtn = this.modal.querySelector('#spCancelCreate');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.hideCreateForm());
        }

        // Step navigation
        const nextStep1 = this.modal.querySelector('#spNextStep1');
        if (nextStep1) {
            nextStep1.addEventListener('click', () => this.goToStep(2));
        }

        const backStep2 = this.modal.querySelector('#spBackStep2');
        if (backStep2) {
            backStep2.addEventListener('click', () => this.goToStep(1));
        }

        const nextStep2 = this.modal.querySelector('#spNextStep2');
        if (nextStep2) {
            nextStep2.addEventListener('click', () => this.goToStep(3));
        }

        const backStep3 = this.modal.querySelector('#spBackStep3');
        if (backStep3) {
            backStep3.addEventListener('click', () => this.goToStep(2));
        }

        // Confirm create
        const confirmBtn = this.modal.querySelector('#spConfirmCreate');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => this.createStudent());
        }

        // Avatar selection
        this.modal.querySelectorAll('.sp-avatar-option').forEach(btn => {
            btn.addEventListener('click', () => {
                this.modal.querySelectorAll('.sp-avatar-option').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                this.selectedAvatar = AVATAR_OPTIONS.find(a => a.id === btn.dataset.avatar);
                const preview = this.modal.querySelector('#spAvatarLarge');
                if (preview) preview.textContent = btn.dataset.emoji;
            });
        });

        // Color selection
        this.modal.querySelectorAll('.sp-color-option').forEach(btn => {
            btn.addEventListener('click', () => {
                this.modal.querySelectorAll('.sp-color-option').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                this.selectedColor = btn.dataset.color;
                const preview = this.modal.querySelector('#spAvatarLarge');
                if (preview) preview.style.backgroundColor = this.selectedColor;
            });
        });

        // Genre selection
        this.modal.querySelectorAll('.sp-genre-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const genre = btn.dataset.genre;
                if (btn.classList.contains('selected')) {
                    btn.classList.remove('selected');
                    this.selectedGenres = this.selectedGenres.filter(g => g !== genre);
                } else {
                    if (this.selectedGenres.length < 4) {
                        btn.classList.add('selected');
                        this.selectedGenres.push(genre);
                    }
                }
            });
        });

        // Enter key in name input
        const nameInput = this.modal.querySelector('#spNameInput');
        if (nameInput) {
            nameInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') this.goToStep(2);
            });
        }

        // Close on overlay click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal && this.options.allowSkip) {
                this.close(null);
            }
        });

        // Close on Escape
        document.addEventListener('keydown', this.handleEscape = (e) => {
            if (e.key === 'Escape' && this.options.allowSkip) {
                this.close(null);
            }
        });
    }

    goToStep(step) {
        // Validate current step
        if (step === 2) {
            const nameInput = this.modal.querySelector('#spNameInput');
            if (!nameInput?.value.trim()) {
                nameInput?.focus();
                return;
            }
        }

        // Hide all steps
        this.modal.querySelectorAll('.sp-step').forEach(s => s.classList.add('hidden'));

        // Show target step
        const targetStep = this.modal.querySelector(`#spStep${step}`);
        if (targetStep) {
            targetStep.classList.remove('hidden');
        }

        this.createStep = step;
    }

    showCreateForm() {
        const btn = this.modal.querySelector('#spCreateBtn');
        const form = this.modal.querySelector('#spCreateForm');
        const students = this.modal.querySelector('.sp-students');

        if (btn) btn.classList.add('hidden');
        if (form) form.classList.remove('hidden');
        if (students) students.classList.add('hidden');

        // Focus name input
        const input = this.modal.querySelector('#spNameInput');
        if (input) {
            setTimeout(() => input.focus(), 100);
        }
    }

    hideCreateForm() {
        const btn = this.modal.querySelector('#spCreateBtn');
        const form = this.modal.querySelector('#spCreateForm');
        const students = this.modal.querySelector('.sp-students');

        if (btn) btn.classList.remove('hidden');
        if (form) form.classList.add('hidden');
        if (students) students.classList.remove('hidden');

        // Reset to step 1
        this.createStep = 1;
        this.goToStep(1);

        // Reset selections
        this.selectedAvatar = AVATAR_OPTIONS[0];
        this.selectedColor = AVATAR_COLORS[0];
        this.selectedGenres = [];

        // Reset form
        const nameInput = this.modal.querySelector('#spNameInput');
        if (nameInput) nameInput.value = '';
    }

    async createStudent() {
        const nameInput = this.modal.querySelector('#spNameInput');
        const gradeInput = this.modal.querySelector('#spGradeInput');

        const name = nameInput?.value.trim();
        const grade = parseInt(gradeInput?.value || '6');

        if (!name) {
            this.goToStep(1);
            nameInput?.focus();
            return;
        }

        if (!window.ReadingPlanetDB) {
            console.error('ReadingPlanetDB not available');
            return;
        }

        try {
            const student = await window.ReadingPlanetDB.createStudent(name, {
                grade,
                avatar: this.selectedAvatar.emoji,
                avatarColor: this.selectedColor,
                favoriteGenres: this.selectedGenres,
            });
            this.selectStudent(student);
        } catch (e) {
            console.error('Failed to create student:', e);
        }
    }

    selectStudent(student) {
        this.saveSession(student.id);
        if (this.options.onSelect) {
            this.options.onSelect(student);
        }
        this.close(student);
    }

    saveSession(studentId) {
        try {
            const session = this.getSession();
            session.currentStudentId = studentId;
            session.lastLogin = new Date().toISOString();
            localStorage.setItem('readingplanet_session', JSON.stringify(session));
        } catch (e) {
            console.error('Failed to save session:', e);
        }
    }

    getSession() {
        try {
            return JSON.parse(localStorage.getItem('readingplanet_session') || '{}');
        } catch {
            return {};
        }
    }

    close(result) {
        // Remove escape handler
        document.removeEventListener('keydown', this.handleEscape);

        // Animate out
        this.modal.classList.remove('active');

        setTimeout(() => {
            this.modal.remove();
            if (this.resolve) {
                this.resolve(result);
            }
        }, 200);
    }

    addStyles() {
        if (document.getElementById('sp-styles')) return;

        const style = document.createElement('style');
        style.id = 'sp-styles';
        style.textContent = `
            .sp-overlay {
                position: fixed;
                inset: 0;
                background: rgba(15, 23, 42, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1rem;
                z-index: 10000;
                opacity: 0;
                transition: opacity 200ms ease;
            }

            .sp-overlay.active {
                opacity: 1;
            }

            .sp-modal {
                background: #fff;
                border-radius: 16px;
                width: 100%;
                max-width: 400px;
                max-height: 90vh;
                overflow: hidden;
                transform: translateY(16px);
                transition: transform 200ms ease;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            }

            .sp-overlay.active .sp-modal {
                transform: translateY(0);
            }

            .sp-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 1.25rem 1.5rem;
                border-bottom: 1px solid #e2e8f0;
            }

            .sp-title {
                font-size: 1.125rem;
                font-weight: 600;
                color: #1e293b;
                margin: 0;
            }

            .sp-skip {
                padding: 0.5rem;
                background: none;
                border: none;
                cursor: pointer;
                color: #94a3b8;
                border-radius: 8px;
                transition: all 150ms;
            }

            .sp-skip:hover {
                background: #f1f5f9;
                color: #64748b;
            }

            .sp-content {
                padding: 1rem;
            }

            .sp-students {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                margin-bottom: 1rem;
            }

            .sp-student {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 0.875rem 1rem;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                cursor: pointer;
                transition: all 150ms;
                text-align: left;
                width: 100%;
            }

            .sp-student:hover {
                background: #f1f5f9;
                border-color: #3b82f6;
            }

            .sp-avatar {
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 1rem;
                color: white;
                flex-shrink: 0;
            }

            .sp-student-info {
                flex: 1;
                min-width: 0;
            }

            .sp-student-name {
                display: block;
                font-weight: 600;
                color: #1e293b;
                font-size: 0.9375rem;
            }

            .sp-student-meta {
                display: block;
                font-size: 0.8125rem;
                color: #64748b;
                margin-top: 2px;
            }

            .sp-arrow {
                color: #94a3b8;
                flex-shrink: 0;
            }

            .sp-empty {
                text-align: center;
                padding: 2rem 1rem;
                color: #64748b;
            }

            .sp-create {
                padding-top: 0.5rem;
            }

            .sp-create-btn {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                width: 100%;
                padding: 0.875rem;
                background: #f1f5f9;
                border: 2px dashed #cbd5e1;
                border-radius: 12px;
                color: #64748b;
                font-weight: 500;
                font-size: 0.9375rem;
                cursor: pointer;
                transition: all 150ms;
            }

            .sp-create-btn:hover {
                background: #e2e8f0;
                border-color: #94a3b8;
                color: #475569;
            }

            .sp-create-form {
                padding: 0.5rem 0;
            }

            .sp-form-group {
                margin-bottom: 1rem;
            }

            .sp-label {
                display: block;
                font-size: 0.8125rem;
                font-weight: 500;
                color: #475569;
                margin-bottom: 0.375rem;
            }

            .sp-input,
            .sp-select {
                width: 100%;
                padding: 0.75rem 1rem;
                font-size: 0.9375rem;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: #fff;
                color: #1e293b;
                transition: all 150ms;
            }

            .sp-input:focus,
            .sp-select:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }

            .sp-form-actions {
                display: flex;
                gap: 0.75rem;
                margin-top: 1.25rem;
            }

            .sp-btn {
                flex: 1;
                padding: 0.75rem 1rem;
                font-size: 0.9375rem;
                font-weight: 500;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: all 150ms;
            }

            .sp-btn-ghost {
                background: #f1f5f9;
                color: #475569;
            }

            .sp-btn-ghost:hover {
                background: #e2e8f0;
            }

            .sp-btn-primary {
                background: #3b82f6;
                color: white;
            }

            .sp-btn-primary:hover {
                background: #2563eb;
            }

            .hidden {
                display: none !important;
            }

            /* Step header */
            .sp-step-header {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 1.25rem;
            }

            .sp-step-num {
                font-size: 0.75rem;
                font-weight: 500;
                color: #64748b;
                background: #f1f5f9;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
            }

            .sp-step-title {
                font-size: 1rem;
                font-weight: 600;
                color: #1e293b;
            }

            .sp-hint {
                font-size: 0.8125rem;
                color: #64748b;
                margin-bottom: 1rem;
            }

            /* Avatar preview */
            .sp-avatar-preview {
                display: flex;
                justify-content: center;
                margin-bottom: 1.25rem;
            }

            .sp-avatar-large {
                width: 80px;
                height: 80px;
                border-radius: 20px;
                background: #3b82f6;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.5rem;
                transition: background-color 200ms ease;
            }

            /* Avatar grid */
            .sp-avatar-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 0.5rem;
                margin-bottom: 1rem;
            }

            .sp-avatar-option {
                aspect-ratio: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                background: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                cursor: pointer;
                transition: all 150ms;
            }

            .sp-avatar-option:hover {
                background: #f1f5f9;
                border-color: #94a3b8;
            }

            .sp-avatar-option.selected {
                border-color: #3b82f6;
                background: #eff6ff;
            }

            /* Color grid */
            .sp-color-grid {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
            }

            .sp-color-option {
                width: 36px;
                height: 36px;
                border-radius: 50%;
                border: 3px solid transparent;
                cursor: pointer;
                transition: all 150ms;
            }

            .sp-color-option:hover {
                transform: scale(1.1);
            }

            .sp-color-option.selected {
                border-color: #1e293b;
                box-shadow: 0 0 0 2px white inset;
            }

            /* Genre grid */
            .sp-genre-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 0.5rem;
            }

            .sp-genre-option {
                display: flex;
                align-items: center;
                gap: 0.625rem;
                padding: 0.75rem;
                background: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                cursor: pointer;
                transition: all 150ms;
                text-align: left;
            }

            .sp-genre-option:hover {
                background: #f1f5f9;
                border-color: #94a3b8;
            }

            .sp-genre-option.selected {
                border-color: #3b82f6;
                background: #eff6ff;
            }

            .sp-genre-emoji {
                font-size: 1.25rem;
            }

            .sp-genre-label {
                font-size: 0.875rem;
                font-weight: 500;
                color: #1e293b;
            }

            @media (prefers-color-scheme: dark) {
                .sp-modal {
                    background: #1e293b;
                }

                .sp-header {
                    border-color: #334155;
                }

                .sp-title {
                    color: #f1f5f9;
                }

                .sp-student {
                    background: #0f172a;
                    border-color: #334155;
                }

                .sp-student:hover {
                    background: #1e293b;
                }

                .sp-student-name {
                    color: #f1f5f9;
                }

                .sp-create-btn {
                    background: #0f172a;
                    border-color: #475569;
                    color: #94a3b8;
                }

                .sp-input,
                .sp-select {
                    background: #0f172a;
                    border-color: #334155;
                    color: #f1f5f9;
                }
            }
        `;

        document.head.appendChild(style);
    }
}

// Export
window.StudentPicker = StudentPicker;
