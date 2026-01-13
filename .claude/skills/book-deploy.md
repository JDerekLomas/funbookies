# Book Deploy Skill

Commit and push a FunBookies book to production.

## When to Use

Use this skill when:
- A book is complete and ready for review on funbookies.com
- Updates have been made to an existing book
- Deploying after regenerating images

## Usage

```
/book-deploy <slug> [--message "<custom message>"]
```

Examples:
- `/book-deploy b2-if-i-could-only-be-a-red-tractor`
- `/book-deploy c1-the-knights-quest --message "Regenerated pages 3,5 with fixed prompts"`

## How It Works

### 1. Check Git Status

Verify what files have changed:

```bash
git status
```

Expected files for a new book:
```
public/books/{slug}.json
public/books/references/{slug}_reference.png
public/images/covers/{slug}.png
public/books/images/{slug}_page01.png
public/books/images/{slug}_page02.png
...
```

### 2. Stage Files

Add all book-related files:

```bash
git add public/books/{slug}.json
git add public/books/references/{slug}_reference*.png
git add public/images/covers/{slug}.png
git add public/books/images/{slug}_page*.png
```

Also add any updated documentation:
```bash
git add BOOK_TEMPLATE.md IMAGE_GENERATION_WORKFLOW.md
```

### 3. Create Commit Message

**For new books:**
```
Add new {level} book: {title}

{summary}

- {story_pages} story pages
- Heart words: {heart_words}
- Setting: {setting_context}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**For updates:**
```
Update {slug}: {description}

{details of what changed}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### 4. Commit and Push

```bash
git commit -m "$(cat <<'EOF'
{commit message}
EOF
)"

git push
```

### 5. Provide Review Links

After push, output:

```
Deployed: {title}

Vercel will auto-deploy in ~1 minute.

Review links:
- Read mode: https://funbookies.com/reader.html?book={slug}
- Edit mode: https://funbookies.com/reader.html?book={slug}&mode=edit

Check for:
- [ ] Images match text on each page
- [ ] No content contamination
- [ ] Style is consistent throughout
- [ ] Character looks the same across pages
```

## Deployment Checklist

Before deploying, verify:

- [ ] Book JSON is valid (no syntax errors)
- [ ] All referenced images exist
- [ ] Scene descriptions are concrete (not abstract)
- [ ] story_elements field is populated
- [ ] parent_tips and comprehension_questions exist
- [ ] wordsearch_words are appropriate

## Rollback

If something is wrong after deployment:

```bash
# View recent commits
git log --oneline -5

# Revert last commit
git revert HEAD

# Push the revert
git push
```

## File Checklist

A complete book deployment includes:

| File | Required |
|------|----------|
| `/public/books/{slug}.json` | Yes |
| `/public/books/references/{slug}_reference.png` | Yes |
| `/public/images/covers/{slug}.png` | Yes |
| `/public/books/images/{slug}_page01.png` | Yes |
| `/public/books/images/{slug}_page{NN}.png` | Yes (all pages) |

## Post-Deploy Actions

After user reviews, common follow-ups:

1. **Regenerate specific pages:**
   ```
   /book-images {slug} --pages 3,5
   /book-deploy {slug} --message "Regenerated pages 3,5"
   ```

2. **Update scene descriptions:**
   ```
   /book-scenes {slug}
   /book-images {slug} --all
   /book-deploy {slug} --message "Rewrote scenes and regenerated images"
   ```

3. **Fix text/phonics issues:**
   - Edit JSON manually
   - Run `/book-deploy {slug}`
