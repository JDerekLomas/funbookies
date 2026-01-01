"""
Print-ready PDF generator for Funbookies Pixi-style books.
Creates 10x10cm books ready for professional printing.
"""

import json
from pathlib import Path
from fpdf import FPDF
from PIL import Image
from config import PRINT_SPECS, BOOK_SPECS, BRAND


class PixiPDF(FPDF):
    """Custom PDF class for Pixi-style children's books."""

    def __init__(self):
        # 10x10cm with 3mm bleed = 106x106mm
        super().__init__(unit='mm', format=(106, 106))
        self.set_auto_page_break(False)
        self.bleed = 3  # mm
        self.trim_size = 100  # mm

    def add_fonts(self):
        """Add child-friendly fonts."""
        # Use built-in Helvetica (bold for readability)
        pass


def create_print_pdf(book_json_path: str, images_dir: str, output_path: str = None) -> str:
    """
    Create a print-ready PDF from a book JSON file.

    Args:
        book_json_path: Path to the book JSON file (e.g., volcano_curated.json)
        images_dir: Path to directory containing page images
        output_path: Optional output path for PDF

    Returns:
        Path to generated PDF
    """
    # Load book data
    with open(book_json_path) as f:
        book = json.load(f)

    title = book.get('title', 'Untitled')
    word_list = book.get('word_list', {})
    pages = book.get('pages', [])

    # Create PDF
    pdf = PixiPDF()
    pdf.add_fonts()

    images_path = Path(images_dir)

    for page_data in pages:
        pdf.add_page()
        page_type = page_data.get('type', 'story')
        text = page_data.get('text', '')
        image_file = page_data.get('image')

        if page_type == 'wordlist':
            # Word list page - no image, just styled text
            render_wordlist_page(pdf, word_list)
        elif image_file:
            # Page with image
            image_path = images_path / image_file
            if image_path.exists():
                render_image_page(pdf, str(image_path), text, page_type)
            else:
                render_text_only_page(pdf, text, page_type)
        else:
            render_text_only_page(pdf, text, page_type)

    # Determine output path
    if output_path is None:
        safe_title = "".join(c for c in title if c.isalnum() or c in ' -_').strip().replace(' ', '_').lower()
        output_path = f"output/{safe_title}_print.pdf"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(output_path)

    return output_path


def render_image_page(pdf: PixiPDF, image_path: str, text: str, page_type: str):
    """Render a page with image (70%) and text box (30%)."""
    bleed = pdf.bleed
    page_size = 106  # mm with bleed
    trim_size = 100  # mm

    # Image area: full bleed width, top 70% of page
    image_height = page_size * 0.75  # 75% for image including bleed overlap

    # Place image to fill top portion (with bleed)
    try:
        pdf.image(image_path, x=0, y=0, w=page_size, h=image_height)
    except Exception as e:
        print(f"Warning: Could not load image {image_path}: {e}")

    # Text box: bottom 30% with opaque background
    text_box_height = page_size * 0.28
    text_box_y = page_size - text_box_height

    # Draw opaque white background for text
    pdf.set_fill_color(255, 255, 255)  # White
    pdf.rect(bleed, text_box_y, trim_size, text_box_height - bleed, 'F')

    # Add colored accent line at top of text box
    if page_type == 'cover':
        pdf.set_fill_color(255, 107, 53)  # Orange for cover
        line_height = 1.5
    else:
        pdf.set_fill_color(255, 179, 71)  # Light orange for story
        line_height = 1

    pdf.rect(bleed, text_box_y, trim_size, line_height, 'F')

    # Render text
    render_text(pdf, text, text_box_y + line_height + 2, page_type)


def render_text(pdf: PixiPDF, text: str, y_start: float, page_type: str):
    """Render text in the text box area."""
    bleed = pdf.bleed
    trim_size = 100

    # Set font based on page type
    if page_type == 'cover':
        pdf.set_font('Helvetica', 'B', 18)
        pdf.set_text_color(255, 107, 53)  # Orange
    elif page_type == 'end':
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(100, 100, 100)  # Gray
    else:
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(51, 51, 51)  # Dark gray

    # Center text in the text box
    text_width = trim_size - 10  # 5mm padding on each side
    pdf.set_xy(bleed + 5, y_start + 3)

    # Handle multi-line text
    lines = text.split('\n')
    for line in lines:
        pdf.set_x(bleed + 5)
        pdf.multi_cell(text_width, 6, line, align='C')


def render_wordlist_page(pdf: PixiPDF, word_list: dict):
    """Render the word list page with categorized words."""
    bleed = pdf.bleed
    trim_size = 100

    # Cream background
    pdf.set_fill_color(255, 254, 245)
    pdf.rect(bleed, bleed, trim_size, trim_size, 'F')

    # Title
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(51, 51, 51)
    pdf.set_xy(bleed, bleed + 8)
    pdf.cell(trim_size, 8, 'Words to Know', align='C')

    y = bleed + 22

    # Sound-out words (blue)
    if word_list.get('sound_out'):
        y = render_word_category(pdf, 'SOUND OUT', word_list['sound_out'],
                                  y, (21, 101, 192), (227, 242, 253))

    # Sight words (purple)
    if word_list.get('sight'):
        y = render_word_category(pdf, 'SIGHT WORDS', word_list['sight'],
                                  y, (123, 31, 162), (243, 229, 245))

    # New words (orange)
    if word_list.get('new'):
        y = render_word_category(pdf, 'NEW WORDS', word_list['new'],
                                  y, (230, 81, 0), (255, 243, 224))


def render_word_category(pdf: PixiPDF, label: str, words: list, y: float,
                         label_color: tuple, box_color: tuple) -> float:
    """Render a category of words with colored boxes."""
    bleed = pdf.bleed
    trim_size = 100

    # Category label
    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_text_color(*label_color)
    pdf.set_xy(bleed + 5, y)
    pdf.cell(trim_size - 10, 4, label, align='L')
    y += 5

    # Words in boxes
    pdf.set_font('Helvetica', 'B', 10)
    x = bleed + 5
    max_x = bleed + trim_size - 5

    for word in words:
        word_width = pdf.get_string_width(word) + 6

        # Wrap to next line if needed
        if x + word_width > max_x:
            x = bleed + 5
            y += 8

        # Draw box
        pdf.set_fill_color(*box_color)
        pdf.set_draw_color(*label_color)
        pdf.rect(x, y, word_width, 6, 'DF')

        # Draw text
        pdf.set_text_color(*label_color)
        pdf.set_xy(x + 3, y + 0.5)
        pdf.cell(word_width - 6, 5, word)

        x += word_width + 2

    return y + 12


def render_text_only_page(pdf: PixiPDF, text: str, page_type: str):
    """Render a page with only text (no image)."""
    bleed = pdf.bleed
    trim_size = 100

    # Light background
    pdf.set_fill_color(255, 254, 245)
    pdf.rect(bleed, bleed, trim_size, trim_size, 'F')

    # Center text on page
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(51, 51, 51)
    pdf.set_xy(bleed + 5, 45)
    pdf.multi_cell(trim_size - 10, 8, text, align='C')


def generate_all_books():
    """Generate print PDFs for all curated books."""
    books_dir = Path(__file__).parent.parent / 'web' / 'books'
    images_dir = books_dir / 'images'
    output_dir = Path(__file__).parent.parent / 'output' / 'print'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Curated books ready for print
    curated_books = [
        'volcano_curated.json',
        'castle_rats.json',
        'jungle_zee.json',
    ]

    results = []
    for book_file in curated_books:
        book_path = books_dir / book_file
        if book_path.exists():
            try:
                safe_name = book_file.replace('.json', '')
                output_path = output_dir / f"{safe_name}_print.pdf"
                result = create_print_pdf(str(book_path), str(images_dir), str(output_path))
                results.append(result)
                print(f"Created: {result}")
            except Exception as e:
                print(f"Failed {book_file}: {e}")
        else:
            print(f"Not found: {book_path}")

    return results


if __name__ == "__main__":
    pdfs = generate_all_books()
    print(f"\nGenerated {len(pdfs)} print-ready PDFs")
    for pdf in pdfs:
        print(f"  {pdf}")
