// API endpoint to log image generation metadata
// Logs to Vercel Blob Storage for persistence across serverless invocations

import { put, list } from '@vercel/blob';

const LOG_PREFIX = 'logs/image-gen';

export default async function handler(req, res) {
    // Allow both GET (view logs) and POST (add log)
    if (req.method === 'GET') {
        return await getLogs(req, res);
    } else if (req.method === 'POST') {
        return await addLog(req, res);
    } else {
        return res.status(405).json({ error: 'Method not allowed' });
    }
}

async function addLog(req, res) {
    try {
        const entry = req.body;

        // Validate required fields
        if (!entry.model || !entry.prompt) {
            return res.status(400).json({ error: 'Missing required fields: model, prompt' });
        }

        // Build log entry with defaults
        const logEntry = {
            timestamp: entry.timestamp || new Date().toISOString(),
            model: entry.model,
            prompt: entry.prompt,
            parameters: entry.parameters || {},
            source: entry.source || 'unknown',
            book_slug: entry.book_slug || null,
            page: entry.page || null,
            cost: entry.cost || null,
            status: entry.status || 'completed',
            result_url: entry.result_url || null,
            error: entry.error || null,
            duration_ms: entry.duration_ms || null,
            reference_images: entry.reference_images || [],
        };

        // Generate unique filename with timestamp
        const date = new Date();
        const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD
        const timeStr = date.toISOString().replace(/[:.]/g, '-');
        const filename = `${LOG_PREFIX}/${dateStr}/${timeStr}-${Math.random().toString(36).slice(2, 8)}.json`;

        // Store to Vercel Blob
        const blob = await put(filename, JSON.stringify(logEntry, null, 2), {
            access: 'public',
            contentType: 'application/json',
        });

        return res.status(200).json({
            success: true,
            logged: true,
            url: blob.url
        });
    } catch (error) {
        console.error('Error logging image generation:', error);
        return res.status(500).json({ error: error.message });
    }
}

async function getLogs(req, res) {
    try {
        const { date, limit = 100 } = req.query;

        // List logs, optionally filtered by date
        const prefix = date ? `${LOG_PREFIX}/${date}/` : `${LOG_PREFIX}/`;
        const { blobs } = await list({ prefix, limit: parseInt(limit) });

        // Fetch and parse each log entry
        const logs = await Promise.all(
            blobs.map(async (blob) => {
                try {
                    const response = await fetch(blob.url);
                    const data = await response.json();
                    return { ...data, _log_url: blob.url };
                } catch (e) {
                    return { error: 'Failed to parse', url: blob.url };
                }
            })
        );

        // Sort by timestamp descending
        logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        return res.status(200).json({
            count: logs.length,
            logs
        });
    } catch (error) {
        console.error('Error fetching logs:', error);
        return res.status(500).json({ error: error.message });
    }
}
