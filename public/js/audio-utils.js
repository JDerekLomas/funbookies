/**
 * Shared Audio Utilities for FunBookies Activities
 *
 * Provides:
 * - Preloading of letter sounds (a-z)
 * - Cached audio playback
 * - Audio instructions via TTS
 * - Consistent audio handling across activities
 */

const AudioUtils = (function() {
  'use strict';

  // Audio cache
  const cache = new Map();
  const preloadedLetters = new Set();

  // Currently playing audio (for stopping overlaps)
  let currentlyPlaying = null;

  // Paths
  const SOUNDS_PATH = '/audio/sounds';
  const LETTER_SOUNDS_PATH = '/activities/letter-sounds/openai-us/sounds';
  const LETTER_NAMES_PATH = '/activities/letter-sounds/openai-us/names';

  // All letters
  const LETTERS = 'abcdefghijklmnopqrstuvwxyz'.split('');

  // Phonetic representations for TTS fallback
  const PHONETICS = {
    a: 'ah', b: 'buh', c: 'kuh', d: 'duh', e: 'eh', f: 'fff',
    g: 'guh', h: 'huh', i: 'ih', j: 'juh', k: 'kuh', l: 'lll',
    m: 'mmm', n: 'nnn', o: 'ah', p: 'puh', q: 'kwuh', r: 'rrr',
    s: 'sss', t: 'tuh', u: 'uh', v: 'vvv', w: 'wuh', x: 'ks',
    y: 'yuh', z: 'zzz'
  };

  /**
   * Preload letter sounds into cache
   * @param {string} type - 'sounds' or 'names'
   * @returns {Promise} Resolves when all letters are loaded
   */
  async function preloadLetters(type = 'sounds') {
    const basePath = type === 'names' ? LETTER_NAMES_PATH : LETTER_SOUNDS_PATH;
    const promises = LETTERS.map(letter => {
      const path = `${basePath}/${letter}.mp3`;
      return preloadAudio(path).catch(() => {
        // Try alternate path
        return preloadAudio(`${SOUNDS_PATH}/${letter}.mp3`).catch(() => null);
      });
    });

    await Promise.all(promises);
    preloadedLetters.add(type);
    console.log(`[AudioUtils] Preloaded ${type} for all letters`);
  }

  /**
   * Preload a single audio file
   * @param {string} path - Path to audio file
   * @returns {Promise<HTMLAudioElement>}
   */
  function preloadAudio(path) {
    return new Promise((resolve, reject) => {
      if (cache.has(path)) {
        resolve(cache.get(path));
        return;
      }

      const audio = new Audio();
      audio.preload = 'auto';

      audio.oncanplaythrough = () => {
        cache.set(path, audio);
        resolve(audio);
      };

      audio.onerror = () => {
        reject(new Error(`Failed to load: ${path}`));
      };

      audio.src = path;
    });
  }

  /**
   * Stop any currently playing audio
   */
  function stopCurrentAudio() {
    if (currentlyPlaying) {
      currentlyPlaying.pause();
      currentlyPlaying.currentTime = 0;
      currentlyPlaying = null;
    }
    // Also cancel any TTS
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }

  /**
   * Play audio from cache or load on-demand
   * @param {string} path - Path to audio file
   * @param {boolean} allowOverlap - If false (default), stops previous audio
   * @returns {Promise} Resolves when audio finishes playing
   */
  async function playAudio(path, allowOverlap = false) {
    let audio = cache.get(path);

    if (!audio) {
      try {
        audio = await preloadAudio(path);
      } catch (e) {
        throw new Error(`Audio not available: ${path}`);
      }
    }

    // Stop previous audio unless overlap is allowed
    if (!allowOverlap) {
      stopCurrentAudio();
    }

    // Clone for clean playback
    const clone = audio.cloneNode();
    clone.currentTime = 0;
    currentlyPlaying = clone;

    return new Promise((resolve, reject) => {
      clone.onended = () => {
        if (currentlyPlaying === clone) {
          currentlyPlaying = null;
        }
        resolve();
      };
      clone.onerror = reject;
      clone.play().catch(reject);
    });
  }

  /**
   * Play a letter sound
   * @param {string} letter - Single letter (a-z)
   * @param {string} type - 'sound' or 'name'
   * @returns {Promise}
   */
  async function playLetterSound(letter, type = 'sound') {
    const l = letter.toLowerCase();
    const basePath = type === 'name' ? LETTER_NAMES_PATH : LETTER_SOUNDS_PATH;
    const primaryPath = `${basePath}/${l}.mp3`;
    const fallbackPath = `${SOUNDS_PATH}/${l}.mp3`;

    try {
      await playAudio(primaryPath);
    } catch (e) {
      try {
        await playAudio(fallbackPath);
      } catch (e2) {
        // Final fallback: TTS
        await speakTTS(PHONETICS[l] || l, { rate: 0.8 });
      }
    }
  }

  /**
   * Speak text using Web Speech API
   * @param {string} text - Text to speak
   * @param {object} options - { rate, pitch, volume }
   * @returns {Promise}
   */
  function speakTTS(text, options = {}) {
    return new Promise((resolve, reject) => {
      if (!('speechSynthesis' in window)) {
        reject(new Error('Speech synthesis not supported'));
        return;
      }

      // Stop any currently playing audio AND cancel ongoing speech
      stopCurrentAudio();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = options.rate ?? 0.9;
      utterance.pitch = options.pitch ?? 1;
      utterance.volume = options.volume ?? 1;

      utterance.onend = resolve;
      utterance.onerror = (e) => reject(e);

      window.speechSynthesis.speak(utterance);
    });
  }

  /**
   * Play audio instruction (tries pre-recorded first, falls back to TTS)
   * @param {string} key - Instruction key (e.g., 'word-builder-intro')
   * @param {string} fallbackText - Text to speak if audio not found
   * @returns {Promise}
   */
  async function playInstruction(key, fallbackText) {
    const path = `/audio/instructions/${key}.mp3`;

    try {
      await playAudio(path);
    } catch (e) {
      // Fallback to TTS
      await speakTTS(fallbackText, { rate: 0.85 });
    }
  }

  /**
   * Play a word using TTS
   * @param {string} word - Word to speak
   * @returns {Promise}
   */
  async function playWord(word) {
    // Try pre-recorded word first
    const path = `/audio/words/${word.toLowerCase()}.mp3`;

    try {
      await playAudio(path);
    } catch (e) {
      // Fallback to TTS
      await speakTTS(word, { rate: 0.85 });
    }
  }

  /**
   * Play a sequence of sounds with delays
   * @param {string[]} sounds - Array of sounds/letters to play
   * @param {number} delay - Delay between sounds in ms
   * @returns {Promise}
   */
  async function playSoundSequence(sounds, delay = 400) {
    for (let i = 0; i < sounds.length; i++) {
      await playLetterSound(sounds[i]);
      if (i < sounds.length - 1) {
        await sleep(delay);
      }
    }
  }

  /**
   * Sleep utility
   * @param {number} ms - Milliseconds to sleep
   * @returns {Promise}
   */
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Check if audio is preloaded
   * @param {string} type - 'sounds' or 'names'
   * @returns {boolean}
   */
  function isPreloaded(type = 'sounds') {
    return preloadedLetters.has(type);
  }

  /**
   * Get cache stats
   * @returns {object}
   */
  function getCacheStats() {
    return {
      cachedFiles: cache.size,
      preloadedSounds: preloadedLetters.has('sounds'),
      preloadedNames: preloadedLetters.has('names')
    };
  }

  // Public API
  return {
    preloadLetters,
    preloadAudio,
    playAudio,
    playLetterSound,
    playWord,
    playInstruction,
    playSoundSequence,
    speakTTS,
    stopCurrentAudio,
    isPreloaded,
    getCacheStats,
    sleep,
    PHONETICS
  };
})();

// Auto-export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AudioUtils;
}
