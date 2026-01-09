# Claude Code Instructions for LilBookies

## Links and File Access

When providing links to the user:

1. **Web URLs** - Put on their own line so they're clickable:
   ```
   https://funbookies.com/reader.html?book=d1-the-lighthouse-keeper
   ```

2. **Local files** - Use `file://` URLs (right-click → Open URL):
   ```
   file:///Users/dereklomas/lilbookies/public/books/references/example.png
   ```

3. **Or offer to open directly** - Use `open` command:
   ```bash
   open /path/to/file.png           # Opens in default app
   open https://funbookies.com      # Opens in browser
   ```

Always prefer giving the user clickable links rather than just file paths.

## Project Structure

- `/public/books/` - Book JSON files and assets
- `/public/books/references/` - 9-panel style reference images
- `/public/books/images/` - Generated page images
- `/public/images/covers/` - Cover images
- `/scripts/` - Python generation scripts

## Image Generation Workflow

See `IMAGE_GENERATION_WORKFLOW.md` for the full pipeline:
1. Reference sheets (nano-banana-pro) → style guide
2. Covers/pages (wan2.6-image) → style transfer from reference

## Key URLs

- Production: https://funbookies.com
- Reader: https://funbookies.com/reader.html?book={slug}
- Edit mode: https://funbookies.com/reader.html?book={slug}&mode=edit
