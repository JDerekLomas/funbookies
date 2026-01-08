/**
 * FunBookies Data Service
 *
 * IndexedDB-based data layer for student management, assessments, and activity tracking.
 * Designed for teacher/parent devices - all student data lives on the adult's device.
 */

const DB_NAME = 'funbookies';
const DB_VERSION = 1;

// Level mapping from old numeric system to new A0-D6 system
const LEVEL_MAP = {
    1: 'A4',   // Simple CVC → Emergent Bridge
    2: 'B1',   // CVC short u → CVC Short a, i
    3: 'B2',   // CVC b/d → CVC Short o, u, e
    4: 'B3',   // Beginning blends → Consonant Blends
    5: 'B5',   // Digraphs → Digraphs
    6: 'B6',   // Magic e → Silent E (CVCe)
    7: 'B8',   // Vowel teams → Vowel Teams
    8: 'B7',   // R-controlled → R-Controlled Vowels
    9: 'C3',   // 2-syllable → Two-Syllable Closed
};

// Reverse mapping for display
const LEVEL_DISPLAY = {
    'A0': { name: 'Concept of Print', band: 'A', order: 0 },
    'A1': { name: 'Letter Recognition', band: 'A', order: 1 },
    'A2': { name: 'CV/VC Words', band: 'A', order: 2 },
    'A3': { name: 'Mixed Case Sentences', band: 'A', order: 3 },
    'A4': { name: 'Emergent Bridge', band: 'A', order: 4 },
    'B1': { name: 'CVC Short a, i', band: 'B', order: 5 },
    'B2': { name: 'CVC Short o, u, e', band: 'B', order: 6 },
    'B3': { name: 'Consonant Blends', band: 'B', order: 7 },
    'B4': { name: 'FLOSS + Word Endings', band: 'B', order: 8 },
    'B5': { name: 'Digraphs', band: 'B', order: 9 },
    'B6': { name: 'Silent E (CVCe)', band: 'B', order: 10 },
    'B7': { name: 'R-Controlled Vowels', band: 'B', order: 11 },
    'B8': { name: 'Vowel Teams', band: 'B', order: 12 },
    'B9': { name: 'Diphthongs + Complex', band: 'B', order: 13 },
    'C1': { name: 'Silent Letters', band: 'C', order: 14 },
    'C2': { name: 'Soft C and G', band: 'C', order: 15 },
    'C3': { name: 'Two-Syllable Closed', band: 'C', order: 16 },
    'C4': { name: 'Open + Consonant-le', band: 'C', order: 17 },
    'C5': { name: 'Contractions', band: 'C', order: 18 },
    'C6': { name: 'Inflectional Endings', band: 'C', order: 19 },
    'C7': { name: 'Derivational Suffixes', band: 'C', order: 20 },
    'C8': { name: 'Prefixes', band: 'C', order: 21 },
    'D1': { name: 'Complex Multisyllable', band: 'D', order: 22 },
    'D2': { name: 'Greek/Latin Roots', band: 'D', order: 23 },
    'D3': { name: 'Advanced Morphology', band: 'D', order: 24 },
    'D4': { name: 'Complex Text', band: 'D', order: 25 },
    'D5': { name: 'Literary Analysis', band: 'D', order: 26 },
    'D6': { name: 'Independent Reading', band: 'D', order: 27 },
};

class FunBookiesDB {
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
                this.migrateFromLocalStorage();
                resolve(this);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Students store
                if (!db.objectStoreNames.contains('students')) {
                    const studentStore = db.createObjectStore('students', { keyPath: 'id' });
                    studentStore.createIndex('name', 'name', { unique: false });
                    studentStore.createIndex('createdAt', 'createdAt', { unique: false });
                }

                // Assessments store (linked to students)
                if (!db.objectStoreNames.contains('assessments')) {
                    const assessmentStore = db.createObjectStore('assessments', { keyPath: 'id' });
                    assessmentStore.createIndex('studentId', 'studentId', { unique: false });
                    assessmentStore.createIndex('date', 'date', { unique: false });
                }

                // Activities store (linked to students)
                if (!db.objectStoreNames.contains('activities')) {
                    const activityStore = db.createObjectStore('activities', { keyPath: 'id' });
                    activityStore.createIndex('studentId', 'studentId', { unique: false });
                    activityStore.createIndex('type', 'type', { unique: false });
                    activityStore.createIndex('date', 'date', { unique: false });
                }

                // Settings store
                if (!db.objectStoreNames.contains('settings')) {
                    db.createObjectStore('settings', { keyPath: 'key' });
                }
            };
        });
    }

    /**
     * Migrate data from old localStorage format
     */
    async migrateFromLocalStorage() {
        const migrated = localStorage.getItem('funbookies-migrated');
        if (migrated) return;

        const oldAssessment = localStorage.getItem('funbookies-assessment');
        const oldLevel = localStorage.getItem('funbookies-reading-level');

        if (oldAssessment || oldLevel) {
            // Create a "Default Student" for legacy data
            const defaultStudent = await this.createStudent('My Child');

            if (oldAssessment) {
                try {
                    const data = JSON.parse(oldAssessment);
                    const newLevel = LEVEL_MAP[data.estimatedLevel] || 'B1';

                    await this.saveAssessment({
                        studentId: defaultStudent.id,
                        date: data.date || new Date().toISOString(),
                        level: newLevel,
                        legacyLevel: data.estimatedLevel,
                        stats: data.stats,
                        history: data.history?.map(h => ({
                            ...h,
                            level: LEVEL_MAP[h.level] || 'B1'
                        })) || []
                    });
                } catch (e) {
                    console.error('Migration error:', e);
                }
            }

            localStorage.setItem('funbookies-migrated', 'true');
        }
    }

    // ============================================
    // STUDENT OPERATIONS
    // ============================================

    /**
     * Create a new student
     */
    async createStudent(name, options = {}) {
        await this.ready;

        const student = {
            id: crypto.randomUUID(),
            name: name.trim(),
            avatar: options.avatar || this.getRandomAvatar(),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            notes: options.notes || '',
            grade: options.grade || null,
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
            id, // Ensure ID doesn't change
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
     * Delete a student and all their data
     */
    async deleteStudent(id) {
        await this.ready;

        // Delete student
        const tx1 = this.db.transaction('students', 'readwrite');
        await new Promise((resolve, reject) => {
            const request = tx1.objectStore('students').delete(id);
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });

        // Delete their assessments
        const assessments = await this.getAssessments(id);
        const tx2 = this.db.transaction('assessments', 'readwrite');
        for (const a of assessments) {
            tx2.objectStore('assessments').delete(a.id);
        }

        // Delete their activities
        const activities = await this.getActivities(id);
        const tx3 = this.db.transaction('activities', 'readwrite');
        for (const a of activities) {
            tx3.objectStore('activities').delete(a.id);
        }

        return true;
    }

    /**
     * Get random avatar for new students
     */
    getRandomAvatar() {
        const avatars = ['🦊', '🐰', '🐻', '🦁', '🐼', '🐨', '🐯', '🦄', '🐸', '🐙', '🦋', '🐝'];
        return avatars[Math.floor(Math.random() * avatars.length)];
    }

    // ============================================
    // ASSESSMENT OPERATIONS
    // ============================================

    /**
     * Save an assessment result
     */
    async saveAssessment(data) {
        await this.ready;

        const assessment = {
            id: crypto.randomUUID(),
            studentId: data.studentId,
            date: data.date || new Date().toISOString(),
            level: data.level,
            stats: data.stats,
            history: data.history,
            duration: data.duration || null,
            notes: data.notes || '',
        };

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('assessments', 'readwrite');
            const store = tx.objectStore('assessments');
            const request = store.add(assessment);

            request.onsuccess = () => resolve(assessment);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get all assessments for a student
     */
    async getAssessments(studentId) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('assessments', 'readonly');
            const store = tx.objectStore('assessments');
            const index = store.index('studentId');
            const request = index.getAll(studentId);

            request.onsuccess = () => {
                const assessments = request.result.sort((a, b) =>
                    new Date(b.date) - new Date(a.date)
                );
                resolve(assessments);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get the latest assessment for a student
     */
    async getLatestAssessment(studentId) {
        const assessments = await this.getAssessments(studentId);
        return assessments[0] || null;
    }

    /**
     * Get current reading level for a student
     */
    async getCurrentLevel(studentId) {
        const latest = await this.getLatestAssessment(studentId);
        return latest?.level || null;
    }

    // ============================================
    // ACTIVITY TRACKING
    // ============================================

    /**
     * Save an activity result
     */
    async saveActivity(data) {
        await this.ready;

        const activity = {
            id: crypto.randomUUID(),
            studentId: data.studentId,
            type: data.type, // 'sight-words', 'word-builder', 'blend-it', etc.
            date: data.date || new Date().toISOString(),
            score: data.score,
            total: data.total,
            level: data.level || null,
            duration: data.duration || null,
            details: data.details || {}, // Activity-specific data
        };

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('activities', 'readwrite');
            const store = tx.objectStore('activities');
            const request = store.add(activity);

            request.onsuccess = () => resolve(activity);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get all activities for a student
     */
    async getActivities(studentId, options = {}) {
        await this.ready;

        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('activities', 'readonly');
            const store = tx.objectStore('activities');
            const index = store.index('studentId');
            const request = index.getAll(studentId);

            request.onsuccess = () => {
                let activities = request.result;

                // Filter by type if specified
                if (options.type) {
                    activities = activities.filter(a => a.type === options.type);
                }

                // Filter by date range if specified
                if (options.since) {
                    const since = new Date(options.since);
                    activities = activities.filter(a => new Date(a.date) >= since);
                }

                // Sort by date descending
                activities.sort((a, b) => new Date(b.date) - new Date(a.date));

                // Limit if specified
                if (options.limit) {
                    activities = activities.slice(0, options.limit);
                }

                resolve(activities);
            };
            request.onerror = () => reject(request.error);
        });
    }

    // ============================================
    // DASHBOARD / REPORTING
    // ============================================

    /**
     * Get summary stats for a student
     */
    async getStudentSummary(studentId) {
        const [student, assessments, activities] = await Promise.all([
            this.getStudent(studentId),
            this.getAssessments(studentId),
            this.getActivities(studentId)
        ]);

        if (!student) return null;

        const latestAssessment = assessments[0];
        const currentLevel = latestAssessment?.level || null;
        const levelInfo = currentLevel ? LEVEL_DISPLAY[currentLevel] : null;

        // Calculate progress (level changes over time)
        const levelProgress = assessments.map(a => ({
            date: a.date,
            level: a.level,
            order: LEVEL_DISPLAY[a.level]?.order || 0
        })).reverse();

        // Activity stats (last 7 days)
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        const recentActivities = activities.filter(a => new Date(a.date) >= weekAgo);

        const activityStats = {
            totalSessions: recentActivities.length,
            totalCorrect: recentActivities.reduce((sum, a) => sum + (a.score || 0), 0),
            totalQuestions: recentActivities.reduce((sum, a) => sum + (a.total || 0), 0),
            byType: {}
        };

        recentActivities.forEach(a => {
            if (!activityStats.byType[a.type]) {
                activityStats.byType[a.type] = { sessions: 0, score: 0, total: 0 };
            }
            activityStats.byType[a.type].sessions++;
            activityStats.byType[a.type].score += a.score || 0;
            activityStats.byType[a.type].total += a.total || 0;
        });

        // Skills from latest assessment
        const skills = latestAssessment?.history ? this.analyzeSkills(latestAssessment.history) : [];

        return {
            student,
            currentLevel,
            levelInfo,
            levelProgress,
            assessmentCount: assessments.length,
            lastAssessmentDate: latestAssessment?.date,
            activityStats,
            skills,
            streak: this.calculateStreak(activities),
        };
    }

    /**
     * Get class overview (all students)
     */
    async getClassOverview() {
        const students = await this.getStudents();
        const summaries = await Promise.all(
            students.map(s => this.getStudentSummary(s.id))
        );

        // Group by level
        const byLevel = {};
        summaries.forEach(s => {
            if (!s) return;
            const level = s.currentLevel || 'Not Assessed';
            if (!byLevel[level]) byLevel[level] = [];
            byLevel[level].push(s);
        });

        // Calculate class stats
        const assessed = summaries.filter(s => s?.currentLevel);
        const levels = assessed.map(s => LEVEL_DISPLAY[s.currentLevel]?.order || 0);
        const avgLevel = levels.length > 0
            ? levels.reduce((a, b) => a + b, 0) / levels.length
            : null;

        return {
            totalStudents: students.length,
            assessedStudents: assessed.length,
            averageLevelOrder: avgLevel,
            byLevel,
            students: summaries,
        };
    }

    /**
     * Analyze skills from assessment history
     */
    analyzeSkills(history) {
        const skillMap = {
            'A': { name: 'Pre-Reading', levels: ['A0', 'A1', 'A2', 'A3', 'A4'] },
            'B1-B2': { name: 'CVC Words', levels: ['B1', 'B2'] },
            'B3': { name: 'Blends', levels: ['B3'] },
            'B4': { name: 'FLOSS', levels: ['B4'] },
            'B5': { name: 'Digraphs', levels: ['B5'] },
            'B6': { name: 'Silent E', levels: ['B6'] },
            'B7': { name: 'R-Controlled', levels: ['B7'] },
            'B8': { name: 'Vowel Teams', levels: ['B8'] },
            'B9': { name: 'Diphthongs', levels: ['B9'] },
            'C': { name: 'Word Study', levels: ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8'] },
        };

        const results = [];

        Object.entries(skillMap).forEach(([key, skill]) => {
            const relevant = history.filter(h => skill.levels.includes(h.level));
            if (relevant.length === 0) {
                results.push({ ...skill, key, status: 'not-tested', correct: 0, total: 0 });
            } else {
                const correct = relevant.filter(h => h.result === 'correct').length;
                const total = relevant.length;
                const pct = correct / total;
                const status = pct >= 0.8 ? 'mastered' : pct >= 0.5 ? 'learning' : 'needs-work';
                results.push({ ...skill, key, status, correct, total, percentage: Math.round(pct * 100) });
            }
        });

        return results;
    }

    /**
     * Calculate activity streak (consecutive days)
     */
    calculateStreak(activities) {
        if (activities.length === 0) return 0;

        const dates = [...new Set(activities.map(a =>
            new Date(a.date).toDateString()
        ))].sort((a, b) => new Date(b) - new Date(a));

        let streak = 0;
        const today = new Date().toDateString();
        const yesterday = new Date(Date.now() - 86400000).toDateString();

        // Must have activity today or yesterday to have a streak
        if (dates[0] !== today && dates[0] !== yesterday) return 0;

        for (let i = 0; i < dates.length; i++) {
            const expected = new Date(Date.now() - i * 86400000).toDateString();
            if (dates[i] === expected) {
                streak++;
            } else {
                break;
            }
        }

        return streak;
    }

    // ============================================
    // SETTINGS
    // ============================================

    /**
     * Get a setting
     */
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

    /**
     * Set a setting
     */
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

    // ============================================
    // EXPORT / IMPORT
    // ============================================

    /**
     * Export all data as JSON
     */
    async exportData() {
        await this.ready;

        const [students, assessments, activities] = await Promise.all([
            new Promise((resolve, reject) => {
                const tx = this.db.transaction('students', 'readonly');
                const request = tx.objectStore('students').getAll();
                request.onsuccess = () => resolve(request.result);
                request.onerror = () => reject(request.error);
            }),
            new Promise((resolve, reject) => {
                const tx = this.db.transaction('assessments', 'readonly');
                const request = tx.objectStore('assessments').getAll();
                request.onsuccess = () => resolve(request.result);
                request.onerror = () => reject(request.error);
            }),
            new Promise((resolve, reject) => {
                const tx = this.db.transaction('activities', 'readonly');
                const request = tx.objectStore('activities').getAll();
                request.onsuccess = () => resolve(request.result);
                request.onerror = () => reject(request.error);
            }),
        ]);

        return {
            version: DB_VERSION,
            exportedAt: new Date().toISOString(),
            students,
            assessments,
            activities,
        };
    }

    /**
     * Import data from JSON
     */
    async importData(data) {
        await this.ready;

        if (!data.students || !data.assessments || !data.activities) {
            throw new Error('Invalid import data format');
        }

        // Import students
        const tx1 = this.db.transaction('students', 'readwrite');
        for (const student of data.students) {
            tx1.objectStore('students').put(student);
        }

        // Import assessments
        const tx2 = this.db.transaction('assessments', 'readwrite');
        for (const assessment of data.assessments) {
            tx2.objectStore('assessments').put(assessment);
        }

        // Import activities
        const tx3 = this.db.transaction('activities', 'readwrite');
        for (const activity of data.activities) {
            tx3.objectStore('activities').put(activity);
        }

        return true;
    }

    /**
     * Clear all data (dangerous!)
     */
    async clearAllData() {
        await this.ready;

        const stores = ['students', 'assessments', 'activities', 'settings'];

        for (const storeName of stores) {
            await new Promise((resolve, reject) => {
                const tx = this.db.transaction(storeName, 'readwrite');
                const request = tx.objectStore(storeName).clear();
                request.onsuccess = () => resolve();
                request.onerror = () => reject(request.error);
            });
        }

        return true;
    }
}

// Singleton instance
const db = new FunBookiesDB();

// Export for use in other scripts
window.FunBookiesDB = db;

// Also export level constants
window.FUNBOOKIES_LEVELS = LEVEL_DISPLAY;
window.FUNBOOKIES_LEVEL_MAP = LEVEL_MAP;
