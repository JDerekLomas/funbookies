/**
 * ReadingPlanet Standards Service
 *
 * Utility for loading and querying CCSS ELA standards data.
 * Works with the standards database at /data/standards-ccss-ela.json
 */

class StandardsService {
    constructor() {
        this.standards = null;
        this.standardsById = {};
        this.ready = this.init();
    }

    /**
     * Initialize by loading standards data
     */
    async init() {
        try {
            const response = await fetch('/readingplanet/data/standards-ccss-ela.json');
            if (!response.ok) {
                throw new Error('Failed to load standards data');
            }
            const data = await response.json();
            this.standards = data;

            // Build lookup index
            data.standards.forEach(standard => {
                this.standardsById[standard.id] = standard;
            });

            return this;
        } catch (error) {
            console.error('Error loading standards:', error);
            this.standards = { domains: [], standards: [] };
            return this;
        }
    }

    /**
     * Get standard by ID
     */
    async getStandard(id) {
        await this.ready;
        return this.standardsById[id] || null;
    }

    /**
     * Get multiple standards by IDs
     */
    async getStandards(ids) {
        await this.ready;
        return ids.map(id => this.standardsById[id]).filter(Boolean);
    }

    /**
     * Get all standards for a specific domain
     */
    async getStandardsByDomain(domain) {
        await this.ready;
        return this.standards.standards.filter(s => s.domain === domain);
    }

    /**
     * Get all standards for a specific grade
     */
    async getStandardsByGrade(grade) {
        await this.ready;
        return this.standards.standards.filter(s => s.grade === grade.toString());
    }

    /**
     * Get standards by domain and grade
     */
    async getStandardsByDomainAndGrade(domain, grade) {
        await this.ready;
        return this.standards.standards.filter(
            s => s.domain === domain && s.grade === grade.toString()
        );
    }

    /**
     * Get all standards that include a specific skill
     */
    async getStandardsBySkill(skill) {
        await this.ready;
        return this.standards.standards.filter(s => s.skills.includes(skill));
    }

    /**
     * Get all available domains
     */
    async getDomains() {
        await this.ready;
        return this.standards.domains;
    }

    /**
     * Get all available grades
     */
    async getGrades() {
        await this.ready;
        return this.standards.grades;
    }

    /**
     * Get all unique skills across all standards
     */
    async getAllSkills() {
        await this.ready;
        const skills = new Set();
        this.standards.standards.forEach(s => {
            s.skills.forEach(skill => skills.add(skill));
        });
        return Array.from(skills).sort();
    }

    /**
     * Format standard ID for display
     * e.g., "CCSS.ELA-LITERACY.RL.6.1" -> "RL.6.1"
     */
    formatShortId(id) {
        const parts = id.split('.');
        if (parts.length >= 5) {
            return `${parts[3]}.${parts[4]}.${parts[5] || ''}`.replace(/\.$/, '');
        }
        return id;
    }

    /**
     * Get a human-readable label for a standard
     */
    async getStandardLabel(id) {
        const standard = await this.getStandard(id);
        if (!standard) return id;
        return `${this.formatShortId(id)}: ${standard.shortName}`;
    }

    /**
     * Get standards appropriate for a student's grade level
     * Returns standards from the student's grade and one below
     */
    async getStandardsForStudent(grade) {
        await this.ready;
        const gradeNum = parseInt(grade);
        const targetGrades = [gradeNum.toString()];

        // Include previous grade for scaffolding
        if (gradeNum > 4) {
            targetGrades.push((gradeNum - 1).toString());
        }

        return this.standards.standards.filter(s => targetGrades.includes(s.grade));
    }

    /**
     * Get mastery status text
     */
    getMasteryStatus(mastery) {
        if (mastery === null || mastery === undefined) return 'Not Started';
        if (mastery >= 90) return 'Excellent';
        if (mastery >= 80) return 'Mastered';
        if (mastery >= 70) return 'Proficient';
        if (mastery >= 60) return 'Approaching';
        if (mastery >= 40) return 'Developing';
        return 'Beginning';
    }

    /**
     * Get mastery color class
     */
    getMasteryColor(mastery) {
        if (mastery === null || mastery === undefined) return 'gray';
        if (mastery >= 90) return 'emerald';
        if (mastery >= 80) return 'green';
        if (mastery >= 70) return 'lime';
        if (mastery >= 60) return 'yellow';
        if (mastery >= 40) return 'orange';
        return 'red';
    }

    /**
     * Get skill display name
     */
    getSkillDisplayName(skill) {
        const skillNames = {
            'main-idea': 'Main Idea',
            'inference': 'Making Inferences',
            'literal': 'Literal Comprehension',
            'vocabulary': 'Vocabulary',
            'text-structure': 'Text Structure',
            'author-purpose': 'Author\'s Purpose',
            'citing-evidence': 'Citing Evidence',
            'summarizing': 'Summarizing',
            'compare-contrast': 'Compare & Contrast',
            'cause-effect': 'Cause & Effect',
            'theme': 'Theme',
            'character-analysis': 'Character Analysis',
            'point-of-view': 'Point of View',
            'figurative-language': 'Figurative Language',
            'tone': 'Tone',
            'context-clues': 'Context Clues',
            'word-parts': 'Word Parts',
            'fluency': 'Fluency',
            'analysis': 'Analysis',
            'evaluation': 'Evaluation',
            'argument': 'Argument',
            'evidence': 'Evidence',
        };
        return skillNames[skill] || skill.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    }

    /**
     * Get domain display info
     */
    getDomainInfo(domain) {
        const domainInfo = {
            RL: {
                name: 'Reading: Literature',
                shortName: 'Literature',
                icon: '📖',
                color: 'purple'
            },
            RI: {
                name: 'Reading: Informational Text',
                shortName: 'Informational',
                icon: '📰',
                color: 'blue'
            },
            RF: {
                name: 'Reading: Foundational Skills',
                shortName: 'Foundational',
                icon: '🔤',
                color: 'green'
            },
            L: {
                name: 'Language',
                shortName: 'Language',
                icon: '💬',
                color: 'amber'
            },
            W: {
                name: 'Writing',
                shortName: 'Writing',
                icon: '✏️',
                color: 'pink'
            },
            SL: {
                name: 'Speaking & Listening',
                shortName: 'Speaking',
                icon: '🎤',
                color: 'teal'
            },
        };
        return domainInfo[domain] || { name: domain, shortName: domain, icon: '📚', color: 'gray' };
    }

    /**
     * Build a standards report for a student
     */
    async buildReport(studentId, masteryData) {
        await this.ready;

        const report = {
            student: studentId,
            generatedAt: new Date().toISOString(),
            domains: {},
            grades: {},
            summary: {
                totalStandards: this.standards.standards.length,
                attempted: 0,
                mastered: 0,
                approaching: 0,
                needsPractice: 0,
            }
        };

        // Group mastery data by domain and grade
        Object.entries(masteryData).forEach(([standardId, data]) => {
            const standard = this.standardsById[standardId];
            if (!standard) return;

            report.summary.attempted++;
            if (data.mastery >= 80) report.summary.mastered++;
            else if (data.mastery >= 60) report.summary.approaching++;
            else report.summary.needsPractice++;

            // By domain
            if (!report.domains[standard.domain]) {
                report.domains[standard.domain] = {
                    ...this.getDomainInfo(standard.domain),
                    standards: [],
                    avgMastery: null,
                };
            }
            report.domains[standard.domain].standards.push({
                ...standard,
                ...data,
                shortId: this.formatShortId(standardId),
                statusText: this.getMasteryStatus(data.mastery),
                statusColor: this.getMasteryColor(data.mastery),
            });

            // By grade
            if (!report.grades[standard.grade]) {
                report.grades[standard.grade] = {
                    standards: [],
                    avgMastery: null,
                };
            }
            report.grades[standard.grade].standards.push({
                ...standard,
                ...data,
            });
        });

        // Calculate averages
        Object.values(report.domains).forEach(domain => {
            if (domain.standards.length > 0) {
                domain.avgMastery = Math.round(
                    domain.standards.reduce((sum, s) => sum + s.mastery, 0) / domain.standards.length
                );
            }
        });

        Object.values(report.grades).forEach(grade => {
            if (grade.standards.length > 0) {
                grade.avgMastery = Math.round(
                    grade.standards.reduce((sum, s) => sum + s.mastery, 0) / grade.standards.length
                );
            }
        });

        return report;
    }
}

// Singleton instance
const standardsService = new StandardsService();

// Export for use
window.StandardsService = standardsService;
