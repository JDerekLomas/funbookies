#!/usr/bin/env node
/**
 * Migrate all local book JSON files to Supabase
 *
 * Usage:
 *   SUPABASE_URL=xxx SUPABASE_SERVICE_KEY=xxx node scripts/migrate_books_to_supabase.mjs
 *
 * Or with .env:
 *   node --env-file=.env scripts/migrate_books_to_supabase.mjs
 */

import { readdir, readFile } from 'fs/promises';
import { join } from 'path';

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error('Missing SUPABASE_URL or SUPABASE_SERVICE_KEY');
  console.error('Usage: SUPABASE_URL=xxx SUPABASE_SERVICE_KEY=xxx node scripts/migrate_books_to_supabase.mjs');
  process.exit(1);
}

const BOOKS_DIR = join(process.cwd(), 'public', 'books');
const SKIP_FILES = ['manifest.json', 'index.json'];

async function getExistingBooks() {
  const response = await fetch(
    `${SUPABASE_URL}/rest/v1/books?select=slug`,
    {
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`
      }
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch existing books: ${await response.text()}`);
  }

  const rows = await response.json();
  return new Set(rows.map(r => r.slug));
}

async function upsertBook(slug, data) {
  const response = await fetch(
    `${SUPABASE_URL}/rest/v1/books`,
    {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
      },
      body: JSON.stringify({
        slug,
        data,
        updated_at: new Date().toISOString()
      })
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to upsert ${slug}: ${await response.text()}`);
  }
}

async function migrate() {
  console.log('Fetching existing books from Supabase...');
  const existing = await getExistingBooks();
  console.log(`Found ${existing.size} books already in Supabase\n`);

  const files = await readdir(BOOKS_DIR);
  const bookFiles = files.filter(f =>
    f.endsWith('.json') && !SKIP_FILES.includes(f)
  );

  console.log(`Found ${bookFiles.length} local book files\n`);

  let migrated = 0;
  let skipped = 0;
  let errors = 0;

  for (const file of bookFiles) {
    const slug = file.replace('.json', '');

    if (existing.has(slug)) {
      console.log(`  SKIP ${slug} (already in Supabase)`);
      skipped++;
      continue;
    }

    try {
      const content = await readFile(join(BOOKS_DIR, file), 'utf-8');
      const data = JSON.parse(content);

      await upsertBook(slug, data);
      console.log(`  OK   ${slug} - ${data.title || 'Untitled'}`);
      migrated++;
    } catch (err) {
      console.error(`  ERR  ${slug}: ${err.message}`);
      errors++;
    }
  }

  console.log('\n--- Summary ---');
  console.log(`Migrated: ${migrated}`);
  console.log(`Skipped:  ${skipped}`);
  console.log(`Errors:   ${errors}`);
  console.log(`Total:    ${migrated + skipped + errors}`);
}

migrate().catch(err => {
  console.error('Migration failed:', err);
  process.exit(1);
});
