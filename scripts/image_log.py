"""
Image Generation Logging Utility

Logs all image generation events to a local JSON Lines file for tracking
costs, prompts, models, and results.

Usage:
    from image_log import log_image_generation

    log_image_generation(
        model='wan2.6-image',
        prompt='A friendly dog...',
        parameters={'size': '1024x1024'},
        source='generate_page_images.py',
        book_slug='the-big-dog',
        page=3,
        cost=0.03,
        status='completed',
        result_url='https://...',
        reference_images=['path/to/ref.png']
    )
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Log file location
LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_FILE = LOG_DIR / 'image-gen.jsonl'

# Model cost estimates (per image)
MODEL_COSTS = {
    'wan2.6-image': 0.03,      # I2I
    'wan2.6-t2i': 0.03,        # T2I
    'wan2.5-i2i': 0.03,        # I2I preview
    'nano-banana-pro': 0.15,   # T2I
    'gemini-3-pro': 0.13,      # T2I/I2I
    'gemini-flash': 0.04,      # T2I/I2I (2.5 Flash)
    'flux-dev-i2i': 0.05,      # I2I
    'flux-kontext-pro': 0.04,  # I2I
}


def log_image_generation(
    model: str,
    prompt: str,
    parameters: dict = None,
    source: str = None,
    book_slug: str = None,
    page: int = None,
    cost: float = None,
    status: str = 'completed',
    result_url: str = None,
    error: str = None,
    duration_ms: int = None,
    reference_images: list = None,
):
    """
    Log an image generation event to the local log file.

    Args:
        model: Model used (e.g., 'wan2.6-image', 'gemini-3-pro')
        prompt: The prompt used for generation
        parameters: Dict of generation parameters (size, etc.)
        source: Source script or endpoint
        book_slug: Book slug if applicable
        page: Page number if applicable
        cost: Cost in dollars (will estimate from MODEL_COSTS if not provided)
        status: 'completed', 'failed', 'pending'
        result_url: URL or path of generated image
        error: Error message if failed
        duration_ms: Time taken in milliseconds
        reference_images: List of reference image paths/URLs used
    """
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Build log entry
    entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'model': model,
        'prompt': prompt,
        'parameters': parameters or {},
        'source': source,
        'book_slug': book_slug,
        'page': page,
        'cost': cost if cost is not None else MODEL_COSTS.get(model),
        'status': status,
        'result_url': result_url,
        'error': error,
        'duration_ms': duration_ms,
        'reference_images': reference_images or [],
    }

    # Append to log file
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(entry) + '\n')

        # Print summary
        status_emoji = '✓' if status == 'completed' else '✗' if status == 'failed' else '⏳'
        cost_str = f"${cost:.3f}" if cost else f"${MODEL_COSTS.get(model, 0):.3f}"
        print(f"[LOG] {status_emoji} {model} - {source} - {book_slug or 'N/A'} p{page or 'N/A'} - {cost_str}")

    except Exception as e:
        print(f"[LOG] Warning: Failed to log: {e}")


def get_recent_logs(limit: int = 50, book_slug: str = None, status: str = None):
    """
    Read recent log entries.

    Args:
        limit: Maximum number of entries to return
        book_slug: Filter by book slug
        status: Filter by status ('completed', 'failed', 'pending')

    Returns:
        List of log entry dicts
    """
    if not LOG_FILE.exists():
        return []

    logs = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())

                # Apply filters
                if book_slug and entry.get('book_slug') != book_slug:
                    continue
                if status and entry.get('status') != status:
                    continue

                logs.append(entry)
            except json.JSONDecodeError:
                continue

    # Return most recent
    return logs[-limit:] if limit else logs


def get_cost_summary(book_slug: str = None, since: str = None):
    """
    Get cost summary from logs.

    Args:
        book_slug: Filter by book slug
        since: ISO date string to filter from (e.g., '2024-01-01')

    Returns:
        Dict with total cost, count, and breakdown by model
    """
    logs = get_recent_logs(limit=None, book_slug=book_slug)

    if since:
        logs = [l for l in logs if l.get('timestamp', '') >= since]

    # Only count completed
    completed = [l for l in logs if l.get('status') == 'completed']

    total_cost = sum(l.get('cost', 0) or 0 for l in completed)

    by_model = {}
    for log in completed:
        model = log.get('model', 'unknown')
        by_model[model] = by_model.get(model, {'count': 0, 'cost': 0})
        by_model[model]['count'] += 1
        by_model[model]['cost'] += log.get('cost', 0) or 0

    return {
        'total_cost': round(total_cost, 2),
        'total_images': len(completed),
        'failed_count': len([l for l in logs if l.get('status') == 'failed']),
        'by_model': by_model,
    }


if __name__ == '__main__':
    # CLI to view logs
    import argparse

    parser = argparse.ArgumentParser(description='View image generation logs')
    parser.add_argument('--book', help='Filter by book slug')
    parser.add_argument('--limit', type=int, default=20, help='Number of logs to show')
    parser.add_argument('--summary', action='store_true', help='Show cost summary')
    parser.add_argument('--since', help='Show logs since date (YYYY-MM-DD)')

    args = parser.parse_args()

    if args.summary:
        summary = get_cost_summary(book_slug=args.book, since=args.since)
        print(f"\nImage Generation Summary")
        print(f"{'=' * 40}")
        print(f"Total images: {summary['total_images']}")
        print(f"Failed: {summary['failed_count']}")
        print(f"Total cost: ${summary['total_cost']:.2f}")
        print(f"\nBy model:")
        for model, data in summary['by_model'].items():
            print(f"  {model}: {data['count']} images, ${data['cost']:.2f}")
    else:
        logs = get_recent_logs(limit=args.limit, book_slug=args.book)
        print(f"\nRecent logs ({len(logs)} entries)")
        print(f"{'=' * 60}")
        for log in logs:
            ts = log.get('timestamp', '')[:19]
            status = log.get('status', 'unknown')
            model = log.get('model', 'unknown')
            book = log.get('book_slug', 'N/A')
            page = log.get('page', 'N/A')
            cost = log.get('cost', 0) or 0
            print(f"{ts} | {status:9} | {model:15} | {book:20} | p{page} | ${cost:.3f}")
