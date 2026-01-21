-- Book Quality Ratings Table
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/YOUR_PROJECT/sql

CREATE TABLE IF NOT EXISTS book_ratings (
    id TEXT PRIMARY KEY,
    ratings JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (optional, depends on your needs)
-- ALTER TABLE book_ratings ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (for service key)
-- CREATE POLICY "Allow all for service key" ON book_ratings FOR ALL USING (true);

-- Insert initial empty row (optional)
INSERT INTO book_ratings (id, ratings)
VALUES ('quality-assessment', '{}')
ON CONFLICT (id) DO NOTHING;
