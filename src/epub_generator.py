"""
Fixed-layout EPUB generator for Funbookies minibooks.
Creates print-ready EPUBs that maintain exact positioning.
"""

import os
import zipfile
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field
from config import PRINT_SPECS, BOOK_SPECS, BRAND


@dataclass
class Page:
    number: int
    image_path: str = ""
    text: str = ""
    text_position: str = "bottom"  # top, bottom, center
    page_type: str = "story"  # cover, wordlist, story, back
    bg_color: str = "#FFF8E7"  # Warm cream default


@dataclass
class Book:
    title: str
    author: str = "Funbookies"
    pages: List[Page] = field(default_factory=list)
    word_list: List[str] = field(default_factory=list)


class FixedLayoutEPUB:
    """Generate fixed-layout EPUB 3.0 for print-ready minibooks."""

    def __init__(self, book: Book, output_dir: str = "output"):
        self.book = book
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.width = PRINT_SPECS["trim_width_px"]
        self.height = PRINT_SPECS["trim_height_px"]

    def generate(self) -> str:
        """Generate the EPUB file and return its path."""
        epub_path = self.output_dir / f"{self._safe_filename(self.book.title)}.epub"

        with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as epub:
            epub.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
            epub.writestr('META-INF/container.xml', self._container_xml())
            epub.writestr('OEBPS/content.opf', self._content_opf())
            epub.writestr('OEBPS/toc.ncx', self._toc_ncx())
            epub.writestr('OEBPS/nav.xhtml', self._nav_xhtml())
            epub.writestr('OEBPS/styles.css', self._styles_css())

            for page in self.book.pages:
                epub.writestr(f'OEBPS/page{page.number:02d}.xhtml', self._page_xhtml(page))

                if page.image_path and os.path.exists(page.image_path):
                    ext = Path(page.image_path).suffix.lower()
                    with open(page.image_path, 'rb') as img:
                        epub.writestr(f'OEBPS/images/page{page.number:02d}{ext}', img.read())

        return str(epub_path)

    def _safe_filename(self, name: str) -> str:
        return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')

    def _get_image_ext(self, page: Page) -> str:
        if page.image_path and os.path.exists(page.image_path):
            return Path(page.image_path).suffix.lower()
        return ".png"

    def _get_mime_type(self, ext: str) -> str:
        return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext.lstrip('.'), "image/png")

    def _container_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''

    def _content_opf(self) -> str:
        book_id = self._safe_filename(self.book.title)
        manifest_items = [
            '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
            '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
            '<item id="css" href="styles.css" media-type="text/css"/>',
        ]
        spine_items = []

        for page in self.book.pages:
            page_id = f"page{page.number:02d}"
            manifest_items.append(
                f'<item id="{page_id}" href="{page_id}.xhtml" media-type="application/xhtml+xml" properties="rendition:layout-pre-paginated"/>'
            )
            if page.image_path and os.path.exists(page.image_path):
                ext = self._get_image_ext(page)
                mime = self._get_mime_type(ext)
                manifest_items.append(f'<item id="img{page.number:02d}" href="images/{page_id}{ext}" media-type="{mime}"/>')
            spine_items.append(f'<itemref idref="{page_id}"/>')

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">urn:uuid:{book_id}</dc:identifier>
    <dc:title>{self.book.title}</dc:title>
    <dc:creator>{self.book.author}</dc:creator>
    <dc:publisher>{BRAND["name"]}</dc:publisher>
    <dc:language>en</dc:language>
    <meta property="rendition:layout">pre-paginated</meta>
    <meta property="rendition:orientation">portrait</meta>
    <meta property="rendition:spread">none</meta>
  </metadata>
  <manifest>
    {chr(10).join(manifest_items)}
  </manifest>
  <spine toc="ncx">
    {chr(10).join(spine_items)}
  </spine>
</package>'''

    def _toc_ncx(self) -> str:
        book_id = self._safe_filename(self.book.title)
        nav_points = "\n".join([
            f'    <navPoint id="navpoint{i}" playOrder="{i}"><navLabel><text>Page {p.number}</text></navLabel><content src="page{p.number:02d}.xhtml"/></navPoint>'
            for i, p in enumerate(self.book.pages, 1)
        ])
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="urn:uuid:{book_id}"/></head>
  <docTitle><text>{self.book.title}</text></docTitle>
  <navMap>
{nav_points}
  </navMap>
</ncx>'''

    def _nav_xhtml(self) -> str:
        nav_items = "\n".join([f'      <li><a href="page{p.number:02d}.xhtml">Page {p.number}</a></li>' for p in self.book.pages])
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>{self.book.title}</title></head>
<body>
  <nav epub:type="toc"><h1>Contents</h1><ol>
{nav_items}
  </ol></nav>
</body>
</html>'''

    def _styles_css(self) -> str:
        return f'''@page {{ width: {self.width}px; height: {self.height}px; margin: 0; }}
html, body {{ margin: 0; padding: 0; width: {self.width}px; height: {self.height}px; overflow: hidden; }}
.page {{ position: relative; width: {self.width}px; height: {self.height}px; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
.page-image {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }}
.text-overlay {{ position: absolute; left: 5%; right: 5%; padding: 12px 16px; background: rgba(255,255,255,0.92); border-radius: 12px; font-family: "Nunito", "Comic Sans MS", sans-serif; font-size: 28px; line-height: 1.4; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
.text-top {{ top: 5%; }}
.text-bottom {{ bottom: 5%; }}
.text-center {{ top: 50%; transform: translateY(-50%); }}
.no-image {{ font-size: 32px; font-weight: bold; color: #333; }}
.cover-text {{ font-size: 48px; font-weight: bold; color: #FF6B35; text-shadow: 2px 2px 0 #fff; }}
.wordlist {{ font-size: 24px; line-height: 2; }}
'''

    def _page_xhtml(self, page: Page) -> str:
        has_image = page.image_path and os.path.exists(page.image_path)
        ext = self._get_image_ext(page) if has_image else ""

        # Background color based on page type
        bg_colors = {
            "cover": "#FFE4B5",
            "wordlist": "#E8F5E9",
            "wordlist_title": "#E8F5E9",
            "story": "#FFF8E7",
            "fun_fact": "#E3F2FD",
            "back_cover": "#FFF3E0",
        }
        bg = bg_colors.get(page.page_type, page.bg_color)

        img_tag = f'<img class="page-image" src="images/page{page.number:02d}{ext}" alt=""/>' if has_image else ""

        # Text styling based on page type
        if page.page_type == "cover":
            text_class = "text-overlay text-center cover-text"
        elif page.page_type in ["wordlist", "wordlist_title"]:
            text_class = "text-overlay text-center wordlist"
        else:
            text_class = f"text-overlay text-{page.text_position}"

        text_div = f'<div class="{text_class}">{page.text}</div>' if page.text else ""

        if not has_image and not page.text:
            text_div = f'<div class="no-image">Page {page.number}</div>'

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Page {page.number}</title>
  <link rel="stylesheet" href="styles.css"/>
  <meta name="viewport" content="width={self.width}, height={self.height}"/>
</head>
<body>
  <div class="page" style="background: {bg};">
    {img_tag}
    {text_div}
  </div>
</body>
</html>'''


def create_book_from_story(story_path: str, images_dir: str = "output/images") -> Book:
    """Create a Book from a story JSON file."""
    import json

    with open(story_path) as f:
        story = json.load(f)

    book_name = Path(story_path).stem.replace("_story", "")
    pages = []

    for p in story["pages"]:
        # Try to find image
        img_path = ""
        for ext in [".png", ".jpg", ".jpeg"]:
            candidate = Path(images_dir) / f"{book_name}_page{p['page']:02d}{ext}"
            if candidate.exists():
                img_path = str(candidate)
                break

        pages.append(Page(
            number=p["page"],
            image_path=img_path,
            text=p.get("text", ""),
            page_type=p.get("type", "story"),
            text_position="center" if p.get("type") in ["cover", "wordlist", "wordlist_title"] else "bottom",
        ))

    return Book(
        title=story["title"],
        author=BRAND["name"],
        pages=pages,
        word_list=story.get("word_list", []),
    )


if __name__ == "__main__":
    book = create_book_from_story("output/volcano_story.json")
    generator = FixedLayoutEPUB(book)
    path = generator.generate()
    print(f"Generated: {path}")
