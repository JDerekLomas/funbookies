/**
 * Celebration utilities for FunBookies games.
 * Provides confetti, sound effects, and emoji popups.
 *
 * Usage:
 *   Celebration.confetti()        // falling confetti particles
 *   Celebration.sound('correct')  // single correct tone
 *   Celebration.sound('success')  // arpeggio
 *   Celebration.emoji(['⭐','🌟']) // scale-up emoji popup
 *   Celebration.celebrate()       // combo: all three
 */
const Celebration = (() => {
    let _audioCtx = null;

    function getAudioCtx() {
        if (!_audioCtx) {
            _audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        return _audioCtx;
    }

    function playTone(freq, duration, startDelay = 0) {
        try {
            const ctx = getAudioCtx();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.value = freq;
            osc.type = 'sine';
            const t = ctx.currentTime + startDelay;
            gain.gain.setValueAtTime(0.3, t);
            gain.gain.exponentialRampToValueAtTime(0.01, t + duration);
            osc.start(t);
            osc.stop(t + duration);
        } catch (e) { /* silent fail */ }
    }

    /**
     * Play a named sound effect.
     * @param {'correct'|'success'|'wrong'} name
     */
    function sound(name = 'correct') {
        switch (name) {
            case 'correct':
                playTone(523, 0.3); // C5
                break;
            case 'success':
                // Arpeggio C5 → E5 → G5 → C6
                playTone(523, 0.25, 0);
                playTone(659, 0.25, 0.1);
                playTone(784, 0.25, 0.2);
                playTone(1047, 0.35, 0.3);
                break;
            case 'wrong':
                playTone(220, 0.3); // A3
                break;
            default:
                playTone(523, 0.3);
        }
    }

    /**
     * Spawn falling confetti particles.
     * @param {number} count Number of particles (default 30)
     */
    function confetti(count = 30) {
        const colors = ['#9FC7AA', '#EFA487', '#A8C4D4', '#E8D4A8', '#D4736B', '#667eea'];
        for (let i = 0; i < count; i++) {
            setTimeout(() => {
                const el = document.createElement('div');
                el.className = 'confetti';
                el.style.left = Math.random() * 100 + '%';
                el.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                el.style.animationDuration = (Math.random() * 2 + 2) + 's';
                el.style.width = (Math.random() * 8 + 6) + 'px';
                el.style.height = (Math.random() * 8 + 6) + 'px';
                el.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
                document.body.appendChild(el);
                setTimeout(() => el.remove(), 4500);
            }, i * 30);
        }
    }

    /**
     * Show a scale-up emoji popup at center screen.
     * @param {string[]} emojis Array of emoji to cycle through (default ['⭐','🌟'])
     */
    function emoji(emojis = ['⭐', '🌟']) {
        const pick = emojis[Math.floor(Math.random() * emojis.length)];
        const el = document.createElement('div');
        el.className = 'celebration-emoji';
        el.textContent = pick;
        el.style.position = 'fixed';
        el.style.top = '50%';
        el.style.left = '50%';
        el.style.transform = 'translate(-50%, -50%) scale(0)';
        el.style.fontSize = '4rem';
        el.style.zIndex = '10001';
        el.style.pointerEvents = 'none';
        el.style.animation = 'pop-scale 0.6s ease forwards';
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 800);
    }

    /**
     * Full celebration combo: confetti + success sound + emoji.
     */
    function celebrate() {
        confetti();
        sound('success');
        emoji();
    }

    return { confetti, sound, emoji, celebrate };
})();
