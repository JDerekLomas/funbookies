#!/usr/bin/env node
/**
 * One-time script to create the book_ratings table in Supabase
 * Requires: SUPABASE_URL and SUPABASE_SERVICE_KEY env vars
 *
 * Run with: node scripts/setup_supabase_table.mjs
 */

const SUPABASE_URL = process.env.SUPABASE_URL || "https://cxzwclvkkjvkromubzmp.supabase.co";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.argv[2];

if (!SUPABASE_KEY) {
  console.error('Missing SUPABASE_SERVICE_KEY');
  console.error('Usage: SUPABASE_SERVICE_KEY=xxx node scripts/setup_supabase_table.mjs');
  process.exit(1);
}

// Try to create a function first that can execute SQL, then call it
async function setupTable() {
  const baseUrl = SUPABASE_URL.replace(/\\n$/, '').trim();

  console.log('Attempting to create book_ratings table...');
  console.log('Supabase URL:', baseUrl);

  // First, let's try to see if we can create via RPC by first creating a function
  // This is a workaround - we'll try direct insert and see the error

  // Try inserting to see if table exists
  const testRes = await fetch(`${baseUrl}/rest/v1/book_ratings`, {
    method: 'POST',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=minimal'
    },
    body: JSON.stringify({ id: 'quality-assessment', ratings: {} })
  });

  if (testRes.ok) {
    console.log('✓ Table exists and initial row created!');
    return;
  }

  const error = await testRes.json();

  if (error.code === 'PGRST205') {
    console.log('✗ Table does not exist. Please create it manually in Supabase SQL Editor:');
    console.log('\n--- SQL to run ---\n');
    console.log(`CREATE TABLE IF NOT EXISTS book_ratings (
    id TEXT PRIMARY KEY,
    ratings JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO book_ratings (id, ratings)
VALUES ('quality-assessment', '{}')
ON CONFLICT (id) DO NOTHING;`);
    console.log('\n--- End SQL ---\n');
    console.log('Dashboard URL: https://supabase.com/dashboard/project/cxzwclvkkjvkromubzmp/sql');
    process.exit(1);
  } else if (error.code === '23505') {
    // Unique violation - row already exists, table is fine
    console.log('✓ Table exists (row already present)');
  } else {
    console.log('Error:', error);
  }
}

setupTable().catch(console.error);
