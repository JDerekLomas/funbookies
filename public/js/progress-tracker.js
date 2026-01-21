/**
 * Progress Tracker - Tracks activity mastery and band progression
 * Uses localStorage for persistence (will sync to Supabase later)
 */

const ProgressTracker = (function() {
    const STORAGE_KEY = 'funbookies_progress';

    // Mastery requirements per band
    const BAND_MASTERY = {
        A: {
            activities: ['letter-match', 'first-sounds', 'letter-sounds', 'rhyme-time'],
            requiredAccuracy: 0.85,
            requiredSessions: 3,
            unlocks: 'B'
        },
        B: {
            activities: ['sound-boxes', 'blend-it', 'word-builder', 'word-chains', 'monster-munch'],
            requiredAccuracy: 0.85,
            requiredSessions: 3,
            unlocks: 'C'
        },
        C: {
            activities: ['chop-it-up', 'word-chains-c', 'sentence-scramble', 'read-aloud'],
            requiredAccuracy: 0.80,
            requiredSessions: 3,
            unlocks: 'D'
        },
        D: {
            activities: ['read-aloud-d', 'sentence-scramble-d', 'word-chains-d'],
            requiredAccuracy: 0.75,
            requiredSessions: 3,
            unlocks: null // Final band
        }
    };

    /**
     * Get stored progress data
     */
    function getProgress() {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                console.error('Failed to parse progress data:', e);
            }
        }
        return {
            currentBand: 'A',
            bandsUnlocked: ['A'],
            activities: {},
            lastUpdated: Date.now()
        };
    }

    /**
     * Save progress data
     */
    function saveProgress(progress) {
        progress.lastUpdated = Date.now();
        localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
    }

    /**
     * Record an activity session result
     * @param {string} activityId - Activity identifier
     * @param {string} band - Band the activity belongs to (A, B, C, D)
     * @param {number} accuracy - Score 0-1
     * @param {object} metadata - Additional session data
     */
    function recordSession(activityId, band, accuracy, metadata = {}) {
        const progress = getProgress();

        if (!progress.activities[activityId]) {
            progress.activities[activityId] = {
                band: band,
                sessions: [],
                totalAttempts: 0,
                bestAccuracy: 0,
                recentAccuracy: 0,
                successfulSessions: 0,
                mastered: false
            };
        }

        const activity = progress.activities[activityId];

        // Add session
        activity.sessions.push({
            accuracy: accuracy,
            timestamp: Date.now(),
            ...metadata
        });

        // Keep only last 10 sessions
        if (activity.sessions.length > 10) {
            activity.sessions = activity.sessions.slice(-10);
        }

        activity.totalAttempts++;
        activity.bestAccuracy = Math.max(activity.bestAccuracy, accuracy);

        // Calculate recent accuracy (last 3 sessions)
        const recentSessions = activity.sessions.slice(-3);
        activity.recentAccuracy = recentSessions.reduce((sum, s) => sum + s.accuracy, 0) / recentSessions.length;

        // Count successful sessions (meeting threshold)
        const bandConfig = BAND_MASTERY[band];
        if (bandConfig) {
            const threshold = bandConfig.requiredAccuracy;
            activity.successfulSessions = activity.sessions.filter(s => s.accuracy >= threshold).length;

            // Check mastery
            if (activity.successfulSessions >= bandConfig.requiredSessions && activity.recentAccuracy >= threshold) {
                activity.mastered = true;
            }
        }

        saveProgress(progress);

        // Check for band promotion
        checkBandPromotion(band);

        return activity;
    }

    /**
     * Check if user qualifies for next band
     */
    function checkBandPromotion(currentBand) {
        const progress = getProgress();
        const bandConfig = BAND_MASTERY[currentBand];

        if (!bandConfig || !bandConfig.unlocks) return { ready: false };

        // Check if all required activities are mastered
        const masteredCount = bandConfig.activities.filter(actId => {
            const activity = progress.activities[actId];
            return activity && activity.mastered;
        }).length;

        const totalRequired = bandConfig.activities.length;
        const allMastered = masteredCount === totalRequired;

        if (allMastered && !progress.bandsUnlocked.includes(bandConfig.unlocks)) {
            // Unlock next band
            progress.bandsUnlocked.push(bandConfig.unlocks);
            saveProgress(progress);

            return {
                ready: true,
                nextBand: bandConfig.unlocks,
                justUnlocked: true
            };
        }

        return {
            ready: allMastered,
            nextBand: bandConfig.unlocks,
            progress: masteredCount / totalRequired
        };
    }

    /**
     * Get band progress percentage
     */
    function getBandProgress(band) {
        const progress = getProgress();
        const bandConfig = BAND_MASTERY[band];

        if (!bandConfig) return { percent: 0, mastered: [], total: 0 };

        const mastered = [];
        const inProgress = [];

        bandConfig.activities.forEach(actId => {
            const activity = progress.activities[actId];
            if (activity) {
                if (activity.mastered) {
                    mastered.push(actId);
                } else if (activity.sessions.length > 0) {
                    inProgress.push({
                        id: actId,
                        progress: activity.successfulSessions / bandConfig.requiredSessions
                    });
                }
            }
        });

        // Calculate overall progress
        // Mastered activities = 100%, in-progress weighted by sessions
        let totalProgress = mastered.length;
        inProgress.forEach(ip => {
            totalProgress += ip.progress * 0.5; // Partial credit for in-progress
        });

        const percent = Math.round((totalProgress / bandConfig.activities.length) * 100);

        return {
            percent: percent,
            mastered: mastered,
            inProgress: inProgress,
            total: bandConfig.activities.length,
            readyForNext: mastered.length === bandConfig.activities.length
        };
    }

    /**
     * Check if a band is unlocked
     */
    function isBandUnlocked(band) {
        const progress = getProgress();
        return progress.bandsUnlocked.includes(band);
    }

    /**
     * Get current recommended band
     */
    function getCurrentBand() {
        const progress = getProgress();
        return progress.currentBand;
    }

    /**
     * Set current band (user choice)
     */
    function setCurrentBand(band) {
        const progress = getProgress();
        if (progress.bandsUnlocked.includes(band)) {
            progress.currentBand = band;
            saveProgress(progress);
            return true;
        }
        return false;
    }

    /**
     * Get activity stats
     */
    function getActivityStats(activityId) {
        const progress = getProgress();
        return progress.activities[activityId] || null;
    }

    /**
     * Update band UI elements on band pages
     */
    function updateBandUI(band) {
        const bandProgress = getBandProgress(band);

        // Update mastery bar
        const masteryFill = document.getElementById('mastery-fill');
        const masteryPercent = document.getElementById('mastery-percent');

        if (masteryFill) {
            masteryFill.style.width = `${bandProgress.percent}%`;
        }
        if (masteryPercent) {
            masteryPercent.textContent = `${bandProgress.percent}%`;
        }

        // Update activity mastery indicators
        const masteryActivities = document.querySelectorAll('.mastery-activity');
        masteryActivities.forEach(el => {
            const actId = el.dataset.activity;
            if (bandProgress.mastered.includes(actId)) {
                el.classList.add('complete');
            }
        });

        // Show promotion banner if ready
        const promotionBanner = document.getElementById('promotion-banner');
        const celebrationBanner = document.getElementById('celebration-banner');

        if (bandProgress.readyForNext) {
            if (band === 'D' && celebrationBanner) {
                celebrationBanner.classList.add('visible');
            } else if (promotionBanner) {
                promotionBanner.classList.add('visible');
            }
        }
    }

    /**
     * Reset all progress (for testing)
     */
    function resetProgress() {
        localStorage.removeItem(STORAGE_KEY);
        return getProgress();
    }

    /**
     * Export progress for backup/sync
     */
    function exportProgress() {
        return getProgress();
    }

    /**
     * Import progress from backup/sync
     */
    function importProgress(data) {
        if (data && data.activities && data.bandsUnlocked) {
            saveProgress(data);
            return true;
        }
        return false;
    }

    // Public API
    return {
        recordSession,
        checkBandPromotion,
        getBandProgress,
        isBandUnlocked,
        getCurrentBand,
        setCurrentBand,
        getActivityStats,
        updateBandUI,
        resetProgress,
        exportProgress,
        importProgress,
        BAND_MASTERY
    };
})();

// Make available globally
if (typeof window !== 'undefined') {
    window.ProgressTracker = ProgressTracker;
}
