"""
Funbookies Print Specifications
Based on Pixi book format (10x10cm, 24 pages, saddle-stitch)
"""

# Print dimensions in mm
PRINT_SPECS = {
    "trim_width_mm": 100,
    "trim_height_mm": 100,
    "bleed_mm": 3,
    "safe_margin_mm": 3,

    # Calculated values
    "document_width_mm": 106,  # trim + 2*bleed
    "document_height_mm": 106,
    "safe_width_mm": 94,       # trim - 2*safe_margin
    "safe_height_mm": 94,

    # In pixels at 300 DPI
    "dpi": 300,
    "document_width_px": 1252,  # 106mm at 300dpi
    "document_height_px": 1252,
    "trim_width_px": 1181,      # 100mm at 300dpi
    "trim_height_px": 1181,
    "safe_width_px": 1110,      # 94mm at 300dpi
    "safe_height_px": 1110,
}

# Book structure
BOOK_SPECS = {
    "total_pages": 24,
    "cover_pages": 4,          # front, inside front, inside back, back
    "story_pages": 20,         # 10 spreads
    "binding": "saddle-stitch",
    "cover_stock_gsm": 300,
    "interior_stock_gsm": 130,
    "cover_finish": "gloss_lamination",
    "interior_finish": "gloss",
}

# Page layout
PAGE_LAYOUT = {
    1: "front_cover",
    2: "inside_front",        # title page or story start
    # 3-22: story pages
    23: "inside_back",        # story end or activity
    24: "back_cover",         # branding, craft tip
}

# Brand
BRAND = {
    "name": "Funbookies",
    "domain": "funbookies.com",
    "tagline": "Little books, big adventures",
}

# Image generation defaults
IMAGE_DEFAULTS = {
    "style": "children's book illustration, colorful, friendly, soft edges",
    "negative_prompt": "scary, dark, violent, realistic photo, text, watermark",
    "aspect_ratio": "1:1",
    "width": 1252,
    "height": 1252,
}
