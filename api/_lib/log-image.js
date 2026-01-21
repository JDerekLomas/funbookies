// Shared helper to log image generation from any API endpoint
// Use: import { logImageGeneration } from './_lib/log-image.js';

import { put } from '@vercel/blob';

const LOG_PREFIX = 'logs/image-gen';

/**
 * Log an image generation event
 * @param {Object} entry - Log entry data
 * @param {string} entry.model - Model used (e.g., 'wan2.6-image', 'gemini-3-pro')
 * @param {string} entry.prompt - The prompt used
 * @param {Object} entry.parameters - Generation parameters (size, etc.)
 * @param {string} entry.source - Source endpoint or script
 * @param {string} entry.book_slug - Book slug if applicable
 * @param {number} entry.page - Page number if applicable
 * @param {number} entry.cost - Cost in dollars if known
 * @param {string} entry.status - 'completed', 'failed', 'pending'
 * @param {string} entry.result_url - URL of generated image
 * @param {string} entry.error - Error message if failed
 * @param {number} entry.duration_ms - Time taken in milliseconds
 * @param {Array} entry.reference_images - Reference image URLs/paths used
 */
export async function logImageGeneration(entry) {
    try {
        const logEntry = {
            timestamp: new Date().toISOString(),
            model: entry.model || 'unknown',
            prompt: entry.prompt || '',
            parameters: entry.parameters || {},
            source: entry.source || 'api',
            book_slug: entry.book_slug || null,
            page: entry.page || null,
            cost: entry.cost || null,
            status: entry.status || 'completed',
            result_url: entry.result_url || null,
            error: entry.error || null,
            duration_ms: entry.duration_ms || null,
            reference_images: entry.reference_images || [],
        };

        // Generate unique filename
        const date = new Date();
        const dateStr = date.toISOString().split('T')[0];
        const timeStr = date.toISOString().replace(/[:.]/g, '-');
        const filename = `${LOG_PREFIX}/${dateStr}/${timeStr}-${Math.random().toString(36).slice(2, 8)}.json`;

        // Store to Vercel Blob (fire and forget - don't block on logging)
        await put(filename, JSON.stringify(logEntry, null, 2), {
            access: 'public',
            contentType: 'application/json',
        });

        console.log(`[IMAGE-LOG] ${entry.model} - ${entry.source} - ${entry.status}`);
        return true;
    } catch (error) {
        // Don't fail the main operation if logging fails
        console.error('[IMAGE-LOG] Failed to log:', error.message);
        return false;
    }
}

// Model cost estimates (per image)
export const MODEL_COSTS = {
    'wan2.6-image': 0.03,      // I2I
    'wan2.6-t2i': 0.03,        // T2I
    'wan2.5-i2i': 0.03,        // I2I preview
    'nano-banana-pro': 0.15,   // T2I
    'gemini-3-pro': 0.13,      // T2I/I2I
    'gemini-flash': 0.04,      // T2I/I2I (2.5 Flash)
    'flux-dev-i2i': 0.05,      // I2I
    'flux-kontext-pro': 0.04,  // I2I
};
