/**
 * ReadingPlanet Data Service
 *
 * IndexedDB-based data layer for student management, reading progress, and activity tracking.
 * Designed for older students (grades 4-10) with Lexile-based leveling.
 */

const DB_NAME = 'readingplanet';
const DB_VERSION = 2; // Bumped for standards mastery tracking

// Lexile bands by grade level (approximate)
const LEXILE_BANDS = {
    3: { min: 330, max: 700, target: 520 },
    4: { min: 445, max: 810, target: 640 },
    5: { min: 565, max: 910, target: 770 },
    6: { min: 665, max: 1000, target: 855 },
    7: { min: 735, max: 1065, target: 925 },
    8: { min: 805, max: 1100, target: 985 },
    9: { min: 855, max: 1165, target: 1030 },
    10: { min: 905, max: 1195, target: 1080 },
    11: { min: 940, max: 1210, target: 1100 },
    12: { min: 970, max: 1235, target: 1120 },
};

// WCPM (Words Correct Per Minute) targets by grade
const WCPM_TARGETS = {
    3: { fall: 71, winter: 92, spring: 107 },
    4: { fall: 94, winter: 112, spring: 123 },
    5: { fall: 110, winter: 127, spring: 139 },
    6: { fall: 127, winter: 140, spring: 150 },
    7: { fall: 128, winter: 136, spring: 150 },
    8: { fall: 133, winter: 146, spring: 151 },
};

// Skill categories for older readers
const SKILL_CATEGORIES = {
    decoding: {
        name: 'Decoding',
        skills: ['multisyllable', 'morphology', 'irregular-words']
    },
    fluency: {
        name: 'Fluency',
        skills: ['wcpm', 'prosody', 'phrasing']
    },
    vocabulary: {
        name: 'Vocabulary',
        skills: ['academic-words', 'context-clues', 'word-parts']
    },
    comprehension: {
        name: 'Comprehension',
        skills: ['main-idea', 'inference', 'text-structure', 'author-purpose']
    }
};

class ReadingPlanetDB {
    constructor() {
        this.db = null;
        this.ready = this.init();
    }

    /**
     * Initialize the database
     */
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onerror = () => reject(request.error);

            request.onsuccess = () => {
                this.db = request.result;
                resolve(this);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Students store
                if (!db.objectStoreNames.contains('students')) {
                    const studentStore = db.createObjectStore('students', { keyPath: 'id' });
                    studentStore.createIndex('name', 'name', { unique: false });
                    studentStore.createIndex('grade', 'grade', { unique: false });
                    studentStore.createIndex('createdAt', 'createdAt', { unique: false });
                }

                // Reading sessions store
                if (!db.objectStoreNames.contains('reading_sessions')) {
                    const sessionStore = db.createObjectStore('reading_sessions', { keyPath: 'id' });
                    sessionStore.createIndex('studentId', 'studentId', { unique: false });
                    sessionStore.createIndex('textId', 'textId', { unique: false });
                    sessionStore.createIndex('date', 'date', { unique: false });
                }

                // Fluency assessments store
                if (!db.objectStoreNames.contains('fluency')) {
                    const fluencyStore = db.createObjectStore('fluency', { keyPath: 'id' });
                    fluencyStore.createIndex('studentId', 'studentId', { unique: false });
                    fluencyStore.createIndex('date', 'date', { unique: false });
                }

                // Vocabulary store
                if (!db.objectStoreNames.contains('vocabulary')) {
                    const vocabStore = db.createObjectStore('vocabulary', { keyPath: 'id' });
                    vocabStore.createIndex('studentId', 'studentId', { unique: false });
                    vocabStore.createIndex('word', 'word', { unique: false });
                    vocabStore.createIndex('mastery', 'mastery', { unique: false });
                }

                // Writing submissions store
                if (!db.objectStoreNames.contains('writing')) {
                    const writingStore = db.createObjectStore('writing', { keyPath: 'id' });
                    writingStore.createIndex('studentId', 'studentId', { unique: false });
                    writingStore.createIndex('textId', 'textId', { unique: false });
                    writingStore.createIndex('date', 'date', { unique: false });
                }

                // Comprehension checks store
                if (!db.objectStoreNames.contains('comprehension')) {
                    const compStore = db.createObjectStore('comprehension', { keyPath: 'id' });
                    compStore.createIndex('studentId', 'studentId', { unique: false });
                    compStore.createIndex('textId', 'textId', { unique: false });
                }

                // Achievements store
                if (!db.objectStoreNames.contains('achievements')) {
                    const achieveStore = db.createObjectStore('achievements', { keyPath: 'id' });
                    achieveStore.createIndex('studentId', 'studentId', { unique: false });
                }

                // Settings store
                if (!db.objectStoreNames.contains('settings')) {
                    db.createObjectStore('settings', { keyPath: 'key' });
                }

                // Standards mastery store - tracks attempts per standard
                if (!db.objectStoreNames.contains('standards_mastery')) {
                    const standardsStore = db.createObjectStore('standards_mastery', { keyPath: 'id' });
                    standardsStore.createIndex('studentId', 'studentId', { unique: false });
                    standardsStore.createIndex('standardId', 'standardId', { unique: false });
                    standardsStore.createIndex('studentStandard', ['studentId', 'standardId'], { unique: false });
                    standardsStore.createIndex('date', 'date', { unique: false });
                }
            };
        });
    }

    // ============================================
    // STUDENT OPERATIONS
    // ============================================

    /**
     * Create a new student
     */
    async createStudent(name, options = {}) {
        await this.ready;

        const grade = options.grade || 6;
        const lexileBand = LEXILE_BANDS[grade] || LEXILE_BANDS[6];

        const student = {
            id: crypto.randomUUID(),
            name: name.trim(),
            avatar: options.avatar || this.generateInitials(name),
            avatarColor: options.avatarColor || this.getRandomColor(),
            grade: grade,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),

            // Reading levels
            currentLexile: options.initialLexile || null,
            targetLexile: lexileBand.target,
            initialLexile: options.initialLexile || null,

            // Fluency
            currentWcpm: options.initialWcpm || null,
            targetWcpm: WCPM_TARGETS[grade]?.spring || 150,

            // Preferences
            preferences: {
                favoriteGenres: options.favoriteGenres || [],
                fontSize: 'medium',
                theme: 'light',
                audioSpeed: 1.0,
                ...options.preferences
            },

            // Progress tracking
            stats: {
                textsCompleted: 0,
                wordsRead: 0,
                timeSpentMinutes: 0,
                writingSubmissions: 0,
                vocabularyLearned: 0,
                currentStreak: 0,
                longestStreak: 0,
                totalXp: 0,
                level: 1,
            },

            notes: options.notes || '',
        };

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('students', 'readwrite');
            const store = tx.objectStore('students');
            const request = store.add(student);

            request.onsuccess = () => resolve(student);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get all students
     */
    async getStudents() {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('students', 'readonly');
            const store = tx.objectStore('students');
            const request = store.getAll();

            request.onsuccess = () => {
                const students = request.result.sort((a, b) =>
                    a.name.localeCompare(b.name)
                );
                resolve(students);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get a single student by ID
     */
    async getStudent(id) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('students', 'readonly');
            const store = tx.objectStore('students');
            const request = store.get(id);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Update a student
     */
    async updateStudent(id, updates) {
        await this.ready;

        const student = await this.getStudent(id);
        if (!student) throw new Error('Student not found');

        const updated = {
            ...student,
            ...updates,
            id,
            updatedAt: new Date().toISOString()
        };

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('students', 'readwrite');
            const store = tx.objectStore('students');
            const request = store.put(updated);

            request.onsuccess = () => resolve(updated);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Update student stats
     */
    async updateStudentStats(studentId, statUpdates) {
        const student = await this.getStudent(studentId);
        if (!student) return null;

        const newStats = { ...student.stats };

        Object.entries(statUpdates).forEach(([key, value]) => {
            if (typeof value === 'number' && typeof newStats[key] === 'number') {
                newStats[key] += value;
            } else {
                newStats[key] = value;
            }
        });

        // Calculate level from XP
        newStats.level = this.calculateLevel(newStats.totalXp);

        return this.updateStudent(studentId, { stats: newStats });
    }

    /**
     * Delete a student and all their data
     */
    async deleteStudent(id) {
        await this.ready;

        const stores = ['students', 'reading_sessions', 'fluency', 'vocabulary', 'writing', 'comprehension', 'achievements', 'standards_mastery'];

        for (const storeName of stores) {
            const tx = this.db.transaction(storeName, 'readwrite');
            const store = tx.objectStore(storeName);

            if (storeName === 'students') {
                store.delete(id);
            } else {
                const index = store.index('studentId');
                const request = index.getAllKeys(id);
                request.onsuccess = () => {
                    request.result.forEach(key => store.delete(key));
                };
            }
        }

        return true;
    }

    /**
     * Generate initials from name
     */
    generateInitials(name) {
        return name.split(' ')
            .map(part => part[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    }

    /**
     * Get random avatar color
     */
    getRandomColor() {
        const colors = [
            '#3b82f6', '#8b5cf6', '#ec4899', '#ef4444',
            '#f59e0b', '#22c55e', '#14b8a6', '#06b6d4'
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    /**
     * Calculate level from XP
     */
    calculateLevel(xp) {
        const levels = [0, 500, 1500, 3500, 7000, 12000, 20000, 35000];
        for (let i = levels.length - 1; i >= 0; i--) {
            if (xp >= levels[i]) return i + 1;
        }
        return 1;
    }

    // ============================================
    // READING SESSION OPERATIONS
    // ============================================

    /**
     * Start a reading session
     */
    async startReadingSession(studentId, textId, textMetadata = {}) {
        await this.ready;

        const session = {
            id: crypto.randomUUID(),
            studentId,
            textId,
            textTitle: textMetadata.title || '',
            textLexile: textMetadata.lexile || null,
            startedAt: new Date().toISOString(),
            endedAt: null,
            date: new Date().toISOString().split('T')[0],
            progress: 0,
            wordsRead: 0,
            timeSpentSeconds: 0,
            comprehensionScore: null,
            completed: false,
        };

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('reading_sessions', 'readwrite');
            const store = tx.objectStore('reading_sessions');
            const request = store.add(session);

            request.onsuccess = () => resolve(session);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Update a reading session
     */
    async updateReadingSession(sessionId, updates) {
        await this.ready;

        return new Promise(async (resolve, reject) => {
            const tx = this.db.transaction('reading_sessions', 'readwrite');
            const store = tx.objectStore('reading_sessions');
            const getRequest = store.get(sessionId);

            getRequest.onsuccess = () => {
                const session = getRequest.result;
                if (!session) {
                    reject(new Error('Session not found'));
                    return;
                }

                const updated = { ...session, ...updates };
                const putRequest = store.put(updated);
                putRequest.onsuccess = () => resolve(updated);
                putRequest.onerror = () => reject(putRequest.error);
            };
            getRequest.onerror = () => reject(getRequest.error);
        });
    }

    /**
     * Complete a reading session
     */
    async completeReadingSession(sessionId, finalData = {}) {
        const session = await this.updateReadingSession(sessionId, {
            ...finalData,
            endedAt: new Date().toISOString(),
            completed: true,
        });

        // Update student stats
        if (session.studentId) {
            await this.updateStudentStats(session.studentId, {
                textsCompleted: 1,
                wordsRead: session.wordsRead || 0,
                timeSpentMinutes: Math.round((session.timeSpentSeconds || 0) / 60),
                totalXp: this.calculateReadingXp(session),
            });

            // Update streak
            await this.updateStreak(session.studentId);
        }

        return session;
    }

    /**
     * Get reading sessions for a student
     */
    async getReadingSessions(studentId, options = {}) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('reading_sessions', 'readonly');
            const store = tx.objectStore('reading_sessions');
            const index = store.index('studentId');
            const request = index.getAll(studentId);

            request.onsuccess = () => {
                let sessions = request.result;

                if (options.completed !== undefined) {
                    sessions = sessions.filter(s => s.completed === options.completed);
                }

                if (options.since) {
                    const since = new Date(options.since);
                    sessions = sessions.filter(s => new Date(s.date) >= since);
                }

                sessions.sort((a, b) => new Date(b.startedAt) - new Date(a.startedAt));

                if (options.limit) {
                    sessions = sessions.slice(0, options.limit);
                }

                resolve(sessions);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Calculate XP from reading session
     */
    calculateReadingXp(session) {
        let xp = 0;
        xp += Math.floor((session.timeSpentSeconds || 0) / 60) * 2; // 2 XP per minute
        xp += session.completed ? 25 : 0; // Completion bonus
        if (session.comprehensionScore >= 80) xp += 20; // Comprehension bonus
        return xp;
    }

    // ============================================
    // FLUENCY OPERATIONS
    // ============================================

    /**
     * Save a fluency assessment
     */
    async saveFluencyAssessment(data) {
        await this.ready;

        const assessment = {
            id: crypto.randomUUID(),
            studentId: data.studentId,
            date: new Date().toISOString(),
            passageId: data.passageId || null,
            passageTitle: data.passageTitle || '',
            passageLexile: data.passageLexile || null,
            wordsRead: data.wordsRead,
            errors: data.errors || 0,
            wcpm: data.wcpm,
            accuracy: data.accuracy || Math.round(((data.wordsRead - (data.errors || 0)) / data.wordsRead) * 100),
            prosodyScore: data.prosodyScore || null,
            recordingUrl: data.recordingUrl || null,
            duration: data.duration || 60,
            notes: data.notes || '',
        };

        // Update student's current WCPM
        await this.updateStudent(data.studentId, { currentWcpm: data.wcpm });

        // Add XP
        await this.updateStudentStats(data.studentId, { totalXp: 25 });

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('fluency', 'readwrite');
            const store = tx.objectStore('fluency');
            const request = store.add(assessment);

            request.onsuccess = () => resolve(assessment);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get fluency history for a student
     */
    async getFluencyHistory(studentId, options = {}) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('fluency', 'readonly');
            const store = tx.objectStore('fluency');
            const index = store.index('studentId');
            const request = index.getAll(studentId);

            request.onsuccess = () => {
                let assessments = request.result;
                assessments.sort((a, b) => new Date(b.date) - new Date(a.date));

                if (options.limit) {
                    assessments = assessments.slice(0, options.limit);
                }

                resolve(assessments);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Record a fluency practice session (alias for saveFluencyAssessment)
     */
    async recordFluency(studentId, data) {
        return this.saveFluencyAssessment({
            studentId,
            passageId: data.passageId,
            passageTitle: data.passageTitle,
            wordsRead: data.wordsRead,
            errors: data.errors,
            wcpm: data.wcpm,
            duration: data.timeSeconds,
        });
    }

    /**
     * Get fluency records for a student (alias for getFluencyHistory)
     */
    async getFluencyRecords(studentId) {
        return this.getFluencyHistory(studentId);
    }

    // ============================================
    // VOCABULARY OPERATIONS
    // ============================================

    /**
     * Add word to student's vocabulary
     */
    async addVocabularyWord(studentId, wordData) {
        await this.ready;

        const word = {
            id: crypto.randomUUID(),
            studentId,
            word: wordData.word.toLowerCase(),
            definition: wordData.definition,
            exampleSentence: wordData.exampleSentence || '',
            sourceTextId: wordData.sourceTextId || null,
            addedAt: new Date().toISOString(),
            lastReviewed: null,
            nextReview: new Date().toISOString(),
            mastery: 0, // 0-100
            reviewCount: 0,
            correctCount: 0,
        };

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('vocabulary', 'readwrite');
            const store = tx.objectStore('vocabulary');
            const request = store.add(word);

            request.onsuccess = () => resolve(word);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Update vocabulary word after review
     */
    async updateVocabularyWord(wordId, correct) {
        await this.ready;

        return new Promise(async (resolve, reject) => {
            const tx = this.db.transaction('vocabulary', 'readwrite');
            const store = tx.objectStore('vocabulary');
            const getRequest = store.get(wordId);

            getRequest.onsuccess = () => {
                const word = getRequest.result;
                if (!word) {
                    reject(new Error('Word not found'));
                    return;
                }

                word.reviewCount++;
                if (correct) word.correctCount++;

                // Update mastery (simple algorithm)
                word.mastery = Math.min(100, Math.round((word.correctCount / word.reviewCount) * 100));

                // Schedule next review (spaced repetition)
                const daysUntilReview = correct
                    ? Math.min(30, Math.pow(2, Math.floor(word.mastery / 20)))
                    : 1;
                word.nextReview = new Date(Date.now() + daysUntilReview * 86400000).toISOString();
                word.lastReviewed = new Date().toISOString();

                const putRequest = store.put(word);
                putRequest.onsuccess = () => resolve(word);
                putRequest.onerror = () => reject(putRequest.error);
            };
            getRequest.onerror = () => reject(getRequest.error);
        });
    }

    /**
     * Get vocabulary words for a student
     */
    async getVocabulary(studentId, options = {}) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('vocabulary', 'readonly');
            const store = tx.objectStore('vocabulary');
            const index = store.index('studentId');
            const request = index.getAll(studentId);

            request.onsuccess = () => {
                let words = request.result;

                if (options.dueForReview) {
                    const now = new Date().toISOString();
                    words = words.filter(w => w.nextReview <= now);
                }

                if (options.mastery) {
                    if (options.mastery === 'learning') {
                        words = words.filter(w => w.mastery < 80);
                    } else if (options.mastery === 'mastered') {
                        words = words.filter(w => w.mastery >= 80);
                    }
                }

                resolve(words);
            };
            request.onerror = () => reject(request.error);
        });
    }

    // ============================================
    // COMPREHENSION OPERATIONS
    // ============================================

    /**
     * Save comprehension check results
     */
    async saveComprehensionCheck(data) {
        await this.ready;

        const check = {
            id: crypto.randomUUID(),
            studentId: data.studentId,
            textId: data.textId,
            date: new Date().toISOString(),
            questionType: data.questionType, // literal, inferential, vocabulary, main-idea
            correct: data.correct,
            questionId: data.questionId || null,
            response: data.response || null,
        };

        // Add XP for correct answers
        if (data.correct) {
            await this.updateStudentStats(data.studentId, { totalXp: 10 });
        }

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('comprehension', 'readwrite');
            const store = tx.objectStore('comprehension');
            const request = store.add(check);

            request.onsuccess = () => resolve(check);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get comprehension stats for a student
     */
    async getComprehensionStats(studentId) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('comprehension', 'readonly');
            const store = tx.objectStore('comprehension');
            const index = store.index('studentId');
            const request = index.getAll(studentId);

            request.onsuccess = () => {
                const checks = request.result;

                const stats = {
                    total: checks.length,
                    correct: checks.filter(c => c.correct).length,
                    byType: {}
                };

                stats.accuracy = stats.total > 0
                    ? Math.round((stats.correct / stats.total) * 100)
                    : 0;

                // Group by question type
                checks.forEach(c => {
                    if (!stats.byType[c.questionType]) {
                        stats.byType[c.questionType] = { total: 0, correct: 0 };
                    }
                    stats.byType[c.questionType].total++;
                    if (c.correct) stats.byType[c.questionType].correct++;
                });

                // Calculate accuracy per type
                Object.keys(stats.byType).forEach(type => {
                    const t = stats.byType[type];
                    t.accuracy = Math.round((t.correct / t.total) * 100);
                });

                resolve(stats);
            };
            request.onerror = () => reject(request.error);
        });
    }

    // ============================================
    // STANDARDS MASTERY OPERATIONS
    // ============================================

    /**
     * Record a standards-based question attempt
     * Uses Max Value Grading - only the highest score matters
     */
    async recordStandardAttempt(data) {
        await this.ready;

        const attempt = {
            id: crypto.randomUUID(),
            studentId: data.studentId,
            standardId: data.standardId, // e.g., "CCSS.ELA-LITERACY.RI.6.1"
            textId: data.textId || null,
            questionId: data.questionId || null,
            skill: data.skill || null, // e.g., "inference", "main-idea"
            correct: data.correct,
            score: data.score || (data.correct ? 100 : 0), // 0-100 score
            date: new Date().toISOString(),
            responseTime: data.responseTime || null, // ms
        };

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('standards_mastery', 'readwrite');
            const store = tx.objectStore('standards_mastery');
            const request = store.add(attempt);

            request.onsuccess = () => resolve(attempt);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get all attempts for a student on a specific standard
     */
    async getStandardAttempts(studentId, standardId) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('standards_mastery', 'readonly');
            const store = tx.objectStore('standards_mastery');
            const index = store.index('studentStandard');
            const request = index.getAll([studentId, standardId]);

            request.onsuccess = () => {
                const attempts = request.result;
                attempts.sort((a, b) => new Date(b.date) - new Date(a.date));
                resolve(attempts);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Calculate mastery for a single standard using Max Value Grading
     * Returns the highest score ever achieved (not average)
     */
    async getStandardMastery(studentId, standardId) {
        const attempts = await this.getStandardAttempts(studentId, standardId);

        if (attempts.length === 0) {
            return {
                standardId,
                mastery: null, // Not yet attempted
                attempts: 0,
                lastAttempt: null,
                highestScore: null,
                trend: null,
            };
        }

        // Max Value Grading: highest score = mastery level
        const highestScore = Math.max(...attempts.map(a => a.score));

        // Calculate trend (last 5 vs previous 5)
        let trend = null;
        if (attempts.length >= 3) {
            const recent = attempts.slice(0, Math.min(5, attempts.length));
            const older = attempts.slice(5, 10);
            if (older.length > 0) {
                const recentAvg = recent.reduce((sum, a) => sum + a.score, 0) / recent.length;
                const olderAvg = older.reduce((sum, a) => sum + a.score, 0) / older.length;
                trend = recentAvg - olderAvg; // Positive = improving
            }
        }

        return {
            standardId,
            mastery: highestScore,
            attempts: attempts.length,
            lastAttempt: attempts[0].date,
            highestScore,
            correctCount: attempts.filter(a => a.correct).length,
            accuracy: Math.round((attempts.filter(a => a.correct).length / attempts.length) * 100),
            trend,
        };
    }

    /**
     * Get mastery for all standards a student has attempted
     */
    async getAllStandardsMastery(studentId) {
        await this.ready;

        return new Promise(async (resolve, reject) => {
            const tx = this.db.transaction('standards_mastery', 'readonly');
            const store = tx.objectStore('standards_mastery');
            const index = store.index('studentId');
            const request = index.getAll(studentId);

            request.onsuccess = async () => {
                const attempts = request.result;

                // Group by standard
                const byStandard = {};
                attempts.forEach(attempt => {
                    if (!byStandard[attempt.standardId]) {
                        byStandard[attempt.standardId] = [];
                    }
                    byStandard[attempt.standardId].push(attempt);
                });

                // Calculate mastery for each standard
                const masteryData = {};
                for (const [standardId, standardAttempts] of Object.entries(byStandard)) {
                    const highestScore = Math.max(...standardAttempts.map(a => a.score));
                    const correctCount = standardAttempts.filter(a => a.correct).length;

                    masteryData[standardId] = {
                        standardId,
                        mastery: highestScore,
                        attempts: standardAttempts.length,
                        correctCount,
                        accuracy: Math.round((correctCount / standardAttempts.length) * 100),
                        lastAttempt: standardAttempts.sort((a, b) =>
                            new Date(b.date) - new Date(a.date))[0].date,
                    };
                }

                resolve(masteryData);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get mastery grouped by domain (RL, RI, RF, L, W)
     */
    async getMasteryByDomain(studentId) {
        const allMastery = await this.getAllStandardsMastery(studentId);

        const byDomain = {
            RL: { name: 'Reading: Literature', standards: [], avgMastery: null },
            RI: { name: 'Reading: Informational Text', standards: [], avgMastery: null },
            RF: { name: 'Reading: Foundational Skills', standards: [], avgMastery: null },
            L: { name: 'Language', standards: [], avgMastery: null },
            W: { name: 'Writing', standards: [], avgMastery: null },
        };

        // Group standards by domain
        Object.entries(allMastery).forEach(([standardId, data]) => {
            const domain = standardId.split('.')[3]; // e.g., "RL" from "CCSS.ELA-LITERACY.RL.6.1"
            if (byDomain[domain]) {
                byDomain[domain].standards.push(data);
            }
        });

        // Calculate average mastery per domain
        Object.values(byDomain).forEach(domain => {
            if (domain.standards.length > 0) {
                domain.avgMastery = Math.round(
                    domain.standards.reduce((sum, s) => sum + s.mastery, 0) / domain.standards.length
                );
            }
        });

        return byDomain;
    }

    /**
     * Get mastery grouped by grade level
     */
    async getMasteryByGrade(studentId) {
        const allMastery = await this.getAllStandardsMastery(studentId);

        const byGrade = {};

        Object.entries(allMastery).forEach(([standardId, data]) => {
            // Extract grade from standard ID: "CCSS.ELA-LITERACY.RL.6.1" -> "6"
            const parts = standardId.split('.');
            const grade = parts[4]; // The grade level

            if (!byGrade[grade]) {
                byGrade[grade] = { standards: [], avgMastery: null };
            }
            byGrade[grade].standards.push(data);
        });

        // Calculate average mastery per grade
        Object.values(byGrade).forEach(gradeData => {
            if (gradeData.standards.length > 0) {
                gradeData.avgMastery = Math.round(
                    gradeData.standards.reduce((sum, s) => sum + s.mastery, 0) / gradeData.standards.length
                );
            }
        });

        return byGrade;
    }

    /**
     * Get standards that need practice (mastery below threshold)
     */
    async getStandardsNeedingPractice(studentId, threshold = 70) {
        const allMastery = await this.getAllStandardsMastery(studentId);

        return Object.values(allMastery)
            .filter(s => s.mastery < threshold)
            .sort((a, b) => a.mastery - b.mastery); // Lowest mastery first
    }

    /**
     * Get standards at mastery (above threshold)
     */
    async getMasteredStandards(studentId, threshold = 80) {
        const allMastery = await this.getAllStandardsMastery(studentId);

        return Object.values(allMastery)
            .filter(s => s.mastery >= threshold)
            .sort((a, b) => b.mastery - a.mastery); // Highest mastery first
    }

    /**
     * Get skill gaps - skills with low accuracy
     */
    async getSkillGaps(studentId) {
        await this.ready;

        return new Promise(async (resolve, reject) => {
            const tx = this.db.transaction('standards_mastery', 'readonly');
            const store = tx.objectStore('standards_mastery');
            const index = store.index('studentId');
            const request = index.getAll(studentId);

            request.onsuccess = () => {
                const attempts = request.result;

                // Group by skill
                const bySkill = {};
                attempts.forEach(attempt => {
                    if (!attempt.skill) return;
                    if (!bySkill[attempt.skill]) {
                        bySkill[attempt.skill] = { correct: 0, total: 0 };
                    }
                    bySkill[attempt.skill].total++;
                    if (attempt.correct) bySkill[attempt.skill].correct++;
                });

                // Calculate accuracy and find gaps
                const skillData = Object.entries(bySkill).map(([skill, data]) => ({
                    skill,
                    accuracy: Math.round((data.correct / data.total) * 100),
                    attempts: data.total,
                    correct: data.correct,
                }));

                // Sort by accuracy (lowest first) to show gaps
                skillData.sort((a, b) => a.accuracy - b.accuracy);

                resolve(skillData);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get standards mastery summary for dashboard
     */
    async getStandardsSummary(studentId) {
        const [allMastery, byDomain, skillGaps] = await Promise.all([
            this.getAllStandardsMastery(studentId),
            this.getMasteryByDomain(studentId),
            this.getSkillGaps(studentId),
        ]);

        const standards = Object.values(allMastery);
        const totalStandards = standards.length;

        if (totalStandards === 0) {
            return {
                totalAttempted: 0,
                mastered: 0,
                approaching: 0,
                needsPractice: 0,
                overallMastery: null,
                byDomain,
                topSkillGaps: [],
                recentProgress: [],
            };
        }

        // Categorize standards
        const mastered = standards.filter(s => s.mastery >= 80).length;
        const approaching = standards.filter(s => s.mastery >= 60 && s.mastery < 80).length;
        const needsPractice = standards.filter(s => s.mastery < 60).length;

        // Overall mastery (average of all standards' max scores)
        const overallMastery = Math.round(
            standards.reduce((sum, s) => sum + s.mastery, 0) / totalStandards
        );

        return {
            totalAttempted: totalStandards,
            mastered,
            approaching,
            needsPractice,
            overallMastery,
            byDomain,
            topSkillGaps: skillGaps.slice(0, 5), // Top 5 skill gaps
            masteryDistribution: {
                excellent: standards.filter(s => s.mastery >= 90).length,
                good: standards.filter(s => s.mastery >= 70 && s.mastery < 90).length,
                fair: standards.filter(s => s.mastery >= 50 && s.mastery < 70).length,
                needsWork: standards.filter(s => s.mastery < 50).length,
            },
        };
    }

    /**
     * Enhanced comprehension check that records standards data
     */
    async saveComprehensionCheckWithStandards(data) {
        // Save the regular comprehension check
        const check = await this.saveComprehensionCheck(data);

        // If standards are provided, record standards attempts
        if (data.standards && data.standards.length > 0) {
            for (const standardId of data.standards) {
                await this.recordStandardAttempt({
                    studentId: data.studentId,
                    standardId,
                    textId: data.textId,
                    questionId: data.questionId,
                    skill: data.skill || data.questionType,
                    correct: data.correct,
                    score: data.correct ? 100 : 0,
                });
            }
        }

        return check;
    }

    // ============================================
    // WRITING OPERATIONS
    // ============================================

    /**
     * Save a writing submission
     */
    async saveWriting(data) {
        await this.ready;

        const writing = {
            id: crypto.randomUUID(),
            studentId: data.studentId,
            textId: data.textId || null,
            promptId: data.promptId || null,
            promptType: data.promptType, // summary, response, creative
            date: new Date().toISOString(),
            content: data.content,
            wordCount: data.content.split(/\s+/).filter(w => w).length,
            score: data.score || null, // AI-generated score
            feedback: data.feedback || null, // AI-generated feedback
            rubricScores: data.rubricScores || null, // { mainIdea: 3, evidence: 2, ... }
            isDraft: data.isDraft || false,
            version: 1,
        };

        // Update stats
        if (!data.isDraft) {
            await this.updateStudentStats(data.studentId, {
                writingSubmissions: 1,
                totalXp: 50,
            });
        }

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('writing', 'readwrite');
            const store = tx.objectStore('writing');
            const request = store.add(writing);

            request.onsuccess = () => resolve(writing);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get writing submissions for a student
     */
    async getWriting(studentId, options = {}) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('writing', 'readonly');
            const store = tx.objectStore('writing');
            const index = store.index('studentId');
            const request = index.getAll(studentId);

            request.onsuccess = () => {
                let submissions = request.result;

                if (options.excludeDrafts) {
                    submissions = submissions.filter(s => !s.isDraft);
                }

                submissions.sort((a, b) => new Date(b.date) - new Date(a.date));

                if (options.limit) {
                    submissions = submissions.slice(0, options.limit);
                }

                resolve(submissions);
            };
            request.onerror = () => reject(request.error);
        });
    }

    // ============================================
    // STREAK & ACHIEVEMENTS
    // ============================================

    /**
     * Update student streak
     */
    async updateStreak(studentId) {
        const student = await this.getStudent(studentId);
        if (!student) return null;

        const sessions = await this.getReadingSessions(studentId, { limit: 30 });
        const dates = [...new Set(sessions.map(s => s.date))].sort().reverse();

        let streak = student.stats?.currentStreak || 0;
        const today = new Date().toISOString().split('T')[0];
        const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

        // Check if we need to use a streak freeze
        if (dates[0] !== today && dates[0] !== yesterday) {
            // Check for streak freeze
            const freezeKey = `rp_freezes_${studentId}`;
            const freezes = parseInt(localStorage.getItem(freezeKey) || '2');

            if (freezes > 0 && streak > 0) {
                // Use a freeze to protect the streak
                localStorage.setItem(freezeKey, (freezes - 1).toString());
                localStorage.setItem(`rp_freeze_used_${studentId}`, new Date().toISOString());
            } else {
                streak = 0;
            }
        } else {
            // Recalculate streak from activity
            streak = 0;
            for (let i = 0; i < 365; i++) {
                const expected = new Date(Date.now() - i * 86400000).toISOString().split('T')[0];
                if (dates.includes(expected)) {
                    streak++;
                } else if (i === 0 && dates[0] === yesterday) {
                    // Allow gap for today if yesterday was active
                    continue;
                } else {
                    break;
                }
            }
        }

        const updates = {
            stats: {
                ...student.stats,
                currentStreak: streak,
                longestStreak: Math.max(student.stats.longestStreak || 0, streak),
            }
        };

        return this.updateStudent(studentId, updates);
    }

    /**
     * Use a streak freeze
     */
    async useStreakFreeze(studentId) {
        const freezeKey = `rp_freezes_${studentId}`;
        const freezes = parseInt(localStorage.getItem(freezeKey) || '2');

        if (freezes <= 0) {
            return { success: false, remaining: 0, error: 'No freezes available' };
        }

        localStorage.setItem(freezeKey, (freezes - 1).toString());
        return { success: true, remaining: freezes - 1 };
    }

    /**
     * Get streak freeze count
     */
    getStreakFreezes(studentId) {
        return parseInt(localStorage.getItem(`rp_freezes_${studentId}`) || '2');
    }

    /**
     * Add streak freeze (earned through achievements or purchase)
     */
    addStreakFreeze(studentId, count = 1) {
        const freezeKey = `rp_freezes_${studentId}`;
        const current = parseInt(localStorage.getItem(freezeKey) || '2');
        localStorage.setItem(freezeKey, (current + count).toString());
        return current + count;
    }

    /**
     * Check and award achievements
     */
    async checkAchievements(studentId) {
        await this.ready;

        const student = await this.getStudent(studentId);
        if (!student) return [];

        const sessions = await this.getReadingSessions(studentId);
        const vocabulary = await this.getVocabulary(studentId);
        const writing = await this.getWriting(studentId, { excludeDrafts: true });
        const fluency = await this.getFluencyHistory(studentId);

        const achievements = [
            { id: 'first-text', name: 'First Read', check: () => sessions.filter(s => s.completed).length >= 1 },
            { id: 'bookworm', name: 'Bookworm', check: () => sessions.filter(s => s.completed).length >= 10 },
            { id: 'word-collector', name: 'Word Collector', check: () => vocabulary.length >= 50 },
            { id: 'linguist', name: 'Linguist', check: () => vocabulary.filter(v => v.mastery >= 80).length >= 100 },
            { id: 'writer', name: 'First Draft', check: () => writing.length >= 1 },
            { id: 'prolific', name: 'Prolific Writer', check: () => writing.length >= 25 },
            { id: 'fluent', name: 'Fluent Reader', check: () => fluency.some(f => f.wcpm >= 150) },
            { id: 'streak-7', name: 'Week Warrior', check: () => student.stats.longestStreak >= 7 },
            { id: 'streak-30', name: 'Monthly Master', check: () => student.stats.longestStreak >= 30 },
            { id: 'level-5', name: 'Rising Scholar', check: () => student.stats.level >= 5 },
        ];

        const earned = [];

        for (const achievement of achievements) {
            if (achievement.check()) {
                // Check if already earned
                const existing = await this.getAchievement(studentId, achievement.id);
                if (!existing) {
                    await this.awardAchievement(studentId, achievement.id, achievement.name);
                    earned.push(achievement);
                }
            }
        }

        return earned;
    }

    /**
     * Get achievement
     */
    async getAchievement(studentId, achievementId) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('achievements', 'readonly');
            const store = tx.objectStore('achievements');
            const request = store.get(`${studentId}_${achievementId}`);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Award achievement
     */
    async awardAchievement(studentId, achievementId, name) {
        await this.ready;

        const achievement = {
            id: `${studentId}_${achievementId}`,
            studentId,
            achievementId,
            name,
            earnedAt: new Date().toISOString(),
        };

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('achievements', 'readwrite');
            const store = tx.objectStore('achievements');
            const request = store.add(achievement);

            request.onsuccess = () => resolve(achievement);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get all achievements for a student
     */
    async getAchievements(studentId) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('achievements', 'readonly');
            const store = tx.objectStore('achievements');
            const index = store.index('studentId');
            const request = index.getAll(studentId);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // ============================================
    // DASHBOARD / REPORTING
    // ============================================

    /**
     * Get comprehensive student dashboard data
     */
    async getStudentDashboard(studentId) {
        const [
            student,
            sessions,
            fluency,
            vocabulary,
            comprehension,
            writing,
            achievements,
            standardsSummary
        ] = await Promise.all([
            this.getStudent(studentId),
            this.getReadingSessions(studentId, { limit: 50 }),
            this.getFluencyHistory(studentId, { limit: 10 }),
            this.getVocabulary(studentId),
            this.getComprehensionStats(studentId),
            this.getWriting(studentId, { limit: 10, excludeDrafts: true }),
            this.getAchievements(studentId),
            this.getStandardsSummary(studentId),
        ]);

        if (!student) return null;

        // Calculate weekly activity
        const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString();
        const thisWeekSessions = sessions.filter(s => s.startedAt >= weekAgo);
        const thisWeekMinutes = thisWeekSessions.reduce((sum, s) => sum + Math.round((s.timeSpentSeconds || 0) / 60), 0);

        // Lexile progress
        const lexileGrowth = student.initialLexile && student.currentLexile
            ? student.currentLexile - student.initialLexile
            : null;

        // WCPM trend
        const wcpmTrend = fluency.length >= 2
            ? fluency[0].wcpm - fluency[fluency.length - 1].wcpm
            : null;

        return {
            student,
            stats: student.stats,

            // Progress metrics
            currentLexile: student.currentLexile,
            targetLexile: student.targetLexile,
            lexileGrowth,
            currentWcpm: student.currentWcpm,
            targetWcpm: student.targetWcpm,
            wcpmTrend,

            // Activity
            thisWeekMinutes,
            thisWeekTexts: thisWeekSessions.filter(s => s.completed).length,
            recentSessions: sessions.slice(0, 5),

            // Skills
            fluencyHistory: fluency,
            comprehensionStats: comprehension,
            vocabularyCount: vocabulary.length,
            vocabularyMastered: vocabulary.filter(v => v.mastery >= 80).length,
            vocabularyDueForReview: vocabulary.filter(v => v.nextReview <= new Date().toISOString()).length,

            // Writing
            recentWriting: writing.slice(0, 3),

            // Achievements
            achievements,

            // Standards Mastery
            standardsSummary,

            // Recommendations
            recommendations: this.generateRecommendations(student, comprehension, fluency, standardsSummary),
        };
    }

    /**
     * Generate recommendations based on student data
     */
    generateRecommendations(student, comprehension, fluency, standardsSummary) {
        const recommendations = [];

        // Check fluency
        if (student.currentWcpm && student.currentWcpm < student.targetWcpm * 0.8) {
            recommendations.push({
                type: 'fluency',
                priority: 'high',
                message: 'Practice fluency with repeated reading',
                action: '/fluency',
            });
        }

        // Check comprehension by type
        if (comprehension.byType) {
            Object.entries(comprehension.byType).forEach(([type, data]) => {
                if (data.accuracy < 60) {
                    recommendations.push({
                        type: 'comprehension',
                        priority: 'medium',
                        message: `Work on ${type.replace('-', ' ')} questions`,
                        action: `/skills/${type}`,
                    });
                }
            });
        }

        // Check standards-based skill gaps
        if (standardsSummary?.topSkillGaps) {
            standardsSummary.topSkillGaps.slice(0, 3).forEach(gap => {
                if (gap.accuracy < 60) {
                    recommendations.push({
                        type: 'standards',
                        priority: 'medium',
                        message: `Practice ${gap.skill.replace('-', ' ')} skills`,
                        action: `/skills/${gap.skill}`,
                        skill: gap.skill,
                        currentAccuracy: gap.accuracy,
                    });
                }
            });
        }

        // Check for standards needing practice
        if (standardsSummary?.needsPractice > 0) {
            recommendations.push({
                type: 'standards',
                priority: 'medium',
                message: `${standardsSummary.needsPractice} standards need more practice`,
                action: '/standards',
            });
        }

        // Check engagement
        if (student.stats.currentStreak === 0) {
            recommendations.push({
                type: 'engagement',
                priority: 'medium',
                message: 'Start a reading streak today!',
                action: '/library',
            });
        }

        return recommendations;
    }

    // ============================================
    // ADAPTIVE LEARNING
    // ============================================

    /**
     * Check if student needs reassessment
     */
    async needsReassessment(studentId) {
        const student = await this.getStudent(studentId);
        if (!student) return false;

        const lastAssessment = student.lastAssessment?.date;
        if (!lastAssessment) return true; // Never assessed

        // Recommend reassessment every 30 days
        const daysSince = (Date.now() - new Date(lastAssessment).getTime()) / 86400000;
        return daysSince >= 30;
    }

    /**
     * Get recommended texts based on student level
     */
    async getRecommendedTexts(studentId, count = 5) {
        const student = await this.getStudent(studentId);
        if (!student) return [];

        const lexile = student.currentLexile || LEXILE_BANDS[student.grade]?.target || 700;
        const range = 100; // Lexile range for recommendations

        // This would fetch from texts manifest in real app
        // For now, return structure for what should be fetched
        return {
            targetLexile: lexile,
            minLexile: lexile - range,
            maxLexile: lexile + range,
            favoriteGenres: student.preferences?.favoriteGenres || []
        };
    }

    /**
     * Detect if student has phonics gaps (for FunBookies bridge)
     */
    async detectPhonicsGaps(studentId) {
        const student = await this.getStudent(studentId);
        if (!student) return null;

        const gaps = [];

        // Check if Lexile is very low for grade (suggests decoding issues)
        const gradeTarget = LEXILE_BANDS[student.grade]?.target || 700;
        if (student.currentLexile && student.currentLexile < gradeTarget * 0.6) {
            gaps.push({
                type: 'decoding',
                severity: 'high',
                message: 'May benefit from phonics practice',
                action: '/public/activities/early-reader/'
            });
        }

        // Check WCPM vs target
        const wcpmTarget = WCPM_TARGETS[student.grade]?.spring || 150;
        if (student.currentWcpm && student.currentWcpm < wcpmTarget * 0.6) {
            gaps.push({
                type: 'fluency',
                severity: 'high',
                message: 'Reading fluency needs attention',
                action: '/readingplanet/fluency/'
            });
        }

        // Check comprehension accuracy from assessment
        const assessment = student.lastAssessment;
        if (assessment?.byType) {
            Object.entries(assessment.byType).forEach(([type, data]) => {
                if (data.accuracy < 50) {
                    gaps.push({
                        type,
                        severity: 'high',
                        message: `Needs practice with ${type} skills`,
                        action: `/readingplanet/skills/?focus=${type}`
                    });
                } else if (data.accuracy < 70) {
                    gaps.push({
                        type,
                        severity: 'medium',
                        message: `Could improve ${type} skills`,
                        action: `/readingplanet/skills/?focus=${type}`
                    });
                }
            });
        }

        return {
            hasGaps: gaps.length > 0,
            gaps: gaps.sort((a, b) => {
                const order = { high: 0, medium: 1, low: 2 };
                return order[a.severity] - order[b.severity];
            }),
            needsPhonicsIntervention: gaps.some(g => g.type === 'decoding' && g.severity === 'high'),
            funBookiesLink: gaps.some(g => g.type === 'decoding') ? '/public/activities/early-reader/' : null
        };
    }

    /**
     * Get adaptive learning path for student
     */
    async getAdaptivePath(studentId) {
        const student = await this.getStudent(studentId);
        if (!student) return null;

        const gaps = await this.detectPhonicsGaps(studentId);
        const path = [];

        // If severe phonics gaps, start with FunBookies
        if (gaps?.needsPhonicsIntervention) {
            path.push({
                step: 1,
                type: 'phonics',
                title: 'Build Foundation Skills',
                description: 'Practice phonics with FunBookies activities',
                action: '/public/activities/early-reader/',
                priority: 'high'
            });
        }

        // Add skill gaps
        gaps?.gaps?.slice(0, 3).forEach((gap, idx) => {
            path.push({
                step: path.length + 1,
                type: gap.type,
                title: `Practice ${gap.type.replace('-', ' ')}`,
                description: gap.message,
                action: gap.action,
                priority: gap.severity
            });
        });

        // Add reading at level
        path.push({
            step: path.length + 1,
            type: 'reading',
            title: 'Read at Your Level',
            description: 'Practice with texts matched to your ability',
            action: '/readingplanet/library/',
            priority: 'medium'
        });

        // Add fluency practice
        if (!gaps?.gaps?.some(g => g.type === 'fluency')) {
            path.push({
                step: path.length + 1,
                type: 'fluency',
                title: 'Build Fluency',
                description: 'Practice reading aloud smoothly',
                action: '/readingplanet/fluency/',
                priority: 'low'
            });
        }

        return {
            studentId,
            path: path.slice(0, 5),
            needsReassessment: await this.needsReassessment(studentId),
            lastAssessment: student.lastAssessment?.date
        };
    }

    /**
     * Update student after assessment
     */
    async saveAssessmentResults(studentId, results) {
        const student = await this.getStudent(studentId);
        if (!student) return null;

        const updates = {
            currentLexile: results.estimatedLexile,
            lastAssessment: {
                date: new Date().toISOString(),
                score: results.score,
                lexile: results.estimatedLexile,
                byType: results.byType,
                gradeLevel: results.gradeLevel
            }
        };

        // Set initial Lexile if not set
        if (!student.initialLexile) {
            updates.initialLexile = results.estimatedLexile;
        }

        return this.updateStudent(studentId, updates);
    }

    // ============================================
    // SETTINGS
    // ============================================

    async getSetting(key) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('settings', 'readonly');
            const store = tx.objectStore('settings');
            const request = store.get(key);

            request.onsuccess = () => resolve(request.result?.value);
            request.onerror = () => reject(request.error);
        });
    }

    async setSetting(key, value) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('settings', 'readwrite');
            const store = tx.objectStore('settings');
            const request = store.put({ key, value });

            request.onsuccess = () => resolve(value);
            request.onerror = () => reject(request.error);
        });
    }
}

// Singleton instance
const db = new ReadingPlanetDB();

// Export for use
window.ReadingPlanetDB = db;
window.LEXILE_BANDS = LEXILE_BANDS;
window.WCPM_TARGETS = WCPM_TARGETS;
window.SKILL_CATEGORIES = SKILL_CATEGORIES;
