/**
 * Reusable results card component for FunBookies games.
 *
 * Usage:
 *   const card = new ResultsCard({
 *     title: 'Round Complete!',
 *     message: 'Great work!',
 *     stats: [{ label: 'Score', value: '85' }, { label: 'Accuracy', value: '92%' }],
 *     buttons: [{ label: 'Next Round', onclick: () => startRound() }],
 *     style: 'overlay'  // or 'inline'
 *   });
 *   card.show();
 *   card.hide();
 */
class ResultsCard {
    /**
     * @param {Object} options
     * @param {string} [options.title='Results']
     * @param {string} [options.message]
     * @param {Array<{label: string, value: string}>} [options.stats=[]]
     * @param {Array<{label: string, onclick?: Function, href?: string, className?: string}>} [options.buttons=[]]
     * @param {'overlay'|'inline'} [options.style='overlay']
     * @param {HTMLElement} [options.container] - Parent element for inline style
     */
    constructor(options = {}) {
        this.options = {
            title: 'Results',
            message: '',
            stats: [],
            buttons: [],
            style: 'overlay',
            container: null,
            ...options
        };
        this._el = null;
    }

    _buildCard() {
        const { title, message, stats, buttons } = this.options;

        const card = document.createElement('div');
        card.className = 'results-card';

        // Title
        const h2 = document.createElement('h2');
        h2.textContent = title;
        card.appendChild(h2);

        // Message
        if (message) {
            const p = document.createElement('p');
            p.className = 'results-message';
            p.textContent = message;
            card.appendChild(p);
        }

        // Stats
        if (stats.length > 0) {
            const grid = document.createElement('div');
            grid.className = 'results-stats';
            stats.forEach(stat => {
                const item = document.createElement('div');
                item.className = 'results-stat';
                item.innerHTML = `
                    <div class="results-stat-value">${stat.value}</div>
                    <div class="results-stat-label">${stat.label}</div>
                `;
                grid.appendChild(item);
            });
            card.appendChild(grid);
        }

        // Buttons
        if (buttons.length > 0) {
            const row = document.createElement('div');
            row.className = 'results-buttons';
            buttons.forEach((btn, i) => {
                if (btn.href) {
                    const a = document.createElement('a');
                    a.href = btn.href;
                    a.className = btn.className || (i === 0 ? 'btn btn-primary' : 'btn btn-secondary');
                    a.textContent = btn.label;
                    row.appendChild(a);
                } else {
                    const b = document.createElement('button');
                    b.className = btn.className || (i === 0 ? 'btn btn-primary' : 'btn btn-secondary');
                    b.textContent = btn.label;
                    if (btn.onclick) b.addEventListener('click', btn.onclick);
                    row.appendChild(b);
                }
            });
            card.appendChild(row);
        }

        return card;
    }

    show() {
        this.hide(); // remove any existing

        if (this.options.style === 'inline') {
            this._el = this._buildCard();
            const container = this.options.container || document.body;
            container.appendChild(this._el);
        } else {
            // Overlay mode
            const overlay = document.createElement('div');
            overlay.className = 'results-overlay';
            overlay.appendChild(this._buildCard());
            document.body.appendChild(overlay);
            // Trigger reflow for animation
            requestAnimationFrame(() => overlay.classList.add('visible'));
            this._el = overlay;
        }
        return this;
    }

    hide() {
        if (this._el) {
            this._el.remove();
            this._el = null;
        }
        return this;
    }

    /**
     * Update stats after showing.
     * @param {Array<{label: string, value: string}>} stats
     */
    updateStats(stats) {
        if (!this._el) return;
        const grid = this._el.querySelector('.results-stats');
        if (!grid) return;
        grid.innerHTML = '';
        stats.forEach(stat => {
            const item = document.createElement('div');
            item.className = 'results-stat';
            item.innerHTML = `
                <div class="results-stat-value">${stat.value}</div>
                <div class="results-stat-label">${stat.label}</div>
            `;
            grid.appendChild(item);
        });
    }
}
