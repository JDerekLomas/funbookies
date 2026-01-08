/**
 * Student Picker Component
 *
 * A reusable modal for selecting or creating students before activities/assessments.
 * Usage:
 *   const picker = new StudentPicker();
 *   const student = await picker.show(); // Returns selected student or null if cancelled
 */

class StudentPicker {
    constructor(options = {}) {
        this.options = {
            title: options.title || 'Who is practicing today?',
            allowCreate: options.allowCreate !== false,
            allowSkip: options.allowSkip || false,
            ...options
        };
        this.modal = null;
        this.resolvePromise = null;
    }

    /**
     * Show the picker modal
     * @returns {Promise<object|null>} Selected student or null
     */
    async show() {
        // Wait for DB to be ready
        await window.FunBookiesDB.ready;

        return new Promise((resolve) => {
            this.resolvePromise = resolve;
            this.render();
        });
    }

    /**
     * Render the modal
     */
    async render() {
        // Remove existing modal if any
        this.close();

        const students = await window.FunBookiesDB.getStudents();

        // Create modal HTML
        const modal = document.createElement('div');
        modal.className = 'student-picker-overlay';
        modal.innerHTML = `
            <div class="student-picker-modal">
                <div class="student-picker-header">
                    <h2>${this.options.title}</h2>
                    ${this.options.allowSkip ? '<button class="btn-close" aria-label="Close">&times;</button>' : ''}
                </div>

                <div class="student-picker-content">
                    ${students.length > 0 ? `
                        <div class="student-list">
                            ${students.map(s => `
                                <button class="student-card" data-student-id="${s.id}">
                                    <span class="student-avatar">${s.avatar}</span>
                                    <span class="student-name">${this.escapeHtml(s.name)}</span>
                                    ${this.getStudentBadge(s)}
                                </button>
                            `).join('')}
                        </div>
                    ` : `
                        <div class="empty-state">
                            <span class="empty-icon">👋</span>
                            <p>No students yet. Add your first student to get started!</p>
                        </div>
                    `}

                    ${this.options.allowCreate ? `
                        <div class="add-student-section">
                            <button class="btn-add-student" id="showAddForm">
                                <span>+</span> Add Student
                            </button>

                            <form class="add-student-form hidden" id="addStudentForm">
                                <input type="text"
                                       id="newStudentName"
                                       placeholder="Student name"
                                       maxlength="50"
                                       autocomplete="off"
                                       required>
                                <div class="form-buttons">
                                    <button type="button" class="btn-cancel" id="cancelAdd">Cancel</button>
                                    <button type="submit" class="btn-primary">Add</button>
                                </div>
                            </form>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        // Add styles if not already added
        this.addStyles();

        // Add to DOM
        document.body.appendChild(modal);
        this.modal = modal;

        // Bind events
        this.bindEvents();
    }

    /**
     * Get badge HTML for student (shows level if assessed)
     */
    getStudentBadge(student) {
        // We'll load this async, but for now show placeholder
        return `<span class="student-level" data-student-level="${student.id}">...</span>`;
    }

    /**
     * Load student levels asynchronously
     */
    async loadStudentLevels() {
        const levelSpans = this.modal.querySelectorAll('[data-student-level]');

        for (const span of levelSpans) {
            const studentId = span.dataset.studentLevel;
            const level = await window.FunBookiesDB.getCurrentLevel(studentId);

            if (level) {
                const levelInfo = window.FUNBOOKIES_LEVELS[level];
                span.textContent = level;
                span.classList.add('has-level');
                span.title = levelInfo?.name || '';
            } else {
                span.textContent = 'New';
                span.classList.add('no-level');
            }
        }
    }

    /**
     * Bind event handlers
     */
    bindEvents() {
        // Close button
        const closeBtn = this.modal.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.cancel());
        }

        // Click outside to close (if allowed)
        if (this.options.allowSkip) {
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) this.cancel();
            });
        }

        // Student selection
        const studentCards = this.modal.querySelectorAll('.student-card');
        studentCards.forEach(card => {
            card.addEventListener('click', async () => {
                const studentId = card.dataset.studentId;
                const student = await window.FunBookiesDB.getStudent(studentId);
                this.select(student);
            });
        });

        // Show add form
        const showAddBtn = this.modal.querySelector('#showAddForm');
        if (showAddBtn) {
            showAddBtn.addEventListener('click', () => {
                showAddBtn.classList.add('hidden');
                this.modal.querySelector('#addStudentForm').classList.remove('hidden');
                this.modal.querySelector('#newStudentName').focus();
            });
        }

        // Cancel add
        const cancelBtn = this.modal.querySelector('#cancelAdd');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.modal.querySelector('#addStudentForm').classList.add('hidden');
                this.modal.querySelector('#showAddForm').classList.remove('hidden');
                this.modal.querySelector('#newStudentName').value = '';
            });
        }

        // Add student form
        const addForm = this.modal.querySelector('#addStudentForm');
        if (addForm) {
            addForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const name = this.modal.querySelector('#newStudentName').value.trim();
                if (name) {
                    const student = await window.FunBookiesDB.createStudent(name);
                    this.select(student);
                }
            });
        }

        // Escape key to close
        this.escapeHandler = (e) => {
            if (e.key === 'Escape' && this.options.allowSkip) {
                this.cancel();
            }
        };
        document.addEventListener('keydown', this.escapeHandler);

        // Load levels async
        this.loadStudentLevels();
    }

    /**
     * Select a student and close
     */
    select(student) {
        this.close();
        if (this.resolvePromise) {
            this.resolvePromise(student);
        }
    }

    /**
     * Cancel selection
     */
    cancel() {
        this.close();
        if (this.resolvePromise) {
            this.resolvePromise(null);
        }
    }

    /**
     * Close the modal
     */
    close() {
        if (this.modal) {
            this.modal.remove();
            this.modal = null;
        }
        if (this.escapeHandler) {
            document.removeEventListener('keydown', this.escapeHandler);
        }
    }

    /**
     * Escape HTML
     */
    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    /**
     * Add component styles
     */
    addStyles() {
        if (document.getElementById('student-picker-styles')) return;

        const style = document.createElement('style');
        style.id = 'student-picker-styles';
        style.textContent = `
            .student-picker-overlay {
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                padding: 16px;
                animation: fadeIn 0.2s ease;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            .student-picker-modal {
                background: white;
                border-radius: 16px;
                width: 100%;
                max-width: 400px;
                max-height: 80vh;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                animation: slideUp 0.3s ease;
            }

            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }

            .student-picker-header {
                padding: 20px 24px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .student-picker-header h2 {
                margin: 0;
                font-size: 1.25rem;
                font-weight: 600;
            }

            .student-picker-header .btn-close {
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: #999;
                padding: 0;
                line-height: 1;
            }

            .student-picker-content {
                padding: 16px;
                overflow-y: auto;
                flex: 1;
            }

            .student-list {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .student-card {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                background: #f8f8f8;
                border: 2px solid transparent;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.2s;
                width: 100%;
                text-align: left;
            }

            .student-card:hover {
                background: #f0f0f0;
                border-color: #9FC7AA;
            }

            .student-card:active {
                transform: scale(0.98);
            }

            .student-avatar {
                font-size: 2rem;
                line-height: 1;
            }

            .student-name {
                flex: 1;
                font-size: 1.1rem;
                font-weight: 500;
            }

            .student-level {
                font-size: 0.75rem;
                padding: 4px 8px;
                border-radius: 6px;
                font-weight: 600;
            }

            .student-level.has-level {
                background: #E8F5E9;
                color: #2E7D32;
            }

            .student-level.no-level {
                background: #FFF3E0;
                color: #E65100;
            }

            .empty-state {
                text-align: center;
                padding: 32px 16px;
                color: #666;
            }

            .empty-icon {
                font-size: 3rem;
                display: block;
                margin-bottom: 12px;
            }

            .add-student-section {
                margin-top: 16px;
                padding-top: 16px;
                border-top: 1px solid #eee;
            }

            .btn-add-student {
                width: 100%;
                padding: 12px;
                background: white;
                border: 2px dashed #ccc;
                border-radius: 12px;
                font-size: 1rem;
                color: #666;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }

            .btn-add-student:hover {
                border-color: #9FC7AA;
                color: #2E7D32;
            }

            .btn-add-student span {
                font-size: 1.25rem;
                font-weight: 300;
            }

            .add-student-form {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .add-student-form input {
                padding: 12px 16px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 1rem;
                outline: none;
                transition: border-color 0.2s;
            }

            .add-student-form input:focus {
                border-color: #9FC7AA;
            }

            .form-buttons {
                display: flex;
                gap: 8px;
            }

            .form-buttons button {
                flex: 1;
                padding: 10px;
                border-radius: 8px;
                font-size: 0.95rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
            }

            .btn-cancel {
                background: #f0f0f0;
                border: none;
                color: #666;
            }

            .btn-cancel:hover {
                background: #e0e0e0;
            }

            .btn-primary {
                background: #9FC7AA;
                border: none;
                color: white;
            }

            .btn-primary:hover {
                background: #8AB898;
            }

            .hidden {
                display: none !important;
            }
        `;
        document.head.appendChild(style);
    }
}

// Export
window.StudentPicker = StudentPicker;
