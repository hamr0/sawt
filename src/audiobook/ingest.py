"""
POC-1: Book Ingestion

EPUB/DOCX/TXT → clean text with paragraph boundaries.

Input:  data/books/{epub,docx,txt}/book.*
Output: output/{epub,docx,txt}/{book}/ingestion/clean_text.txt
        output/{epub,docx,txt}/{book}/ingestion/paragraphs.csv
"""
import csv
import re
import unicodedata
from pathlib import Path


# ---------------------------------------------------------------------------
# Arabic text normalization
# ---------------------------------------------------------------------------

def normalize_arabic(text: str) -> tuple[str, dict]:
    """Normalize Arabic text: NFKC, strip tatweel, collapse whitespace.

    Returns (cleaned_text, stats_dict).
    """
    stats = {"presentation_forms_converted": 0, "tatweel_stripped": 0}

    # Count presentation forms before normalization
    for c in text:
        if "\uFE70" <= c <= "\uFEFF" or "\uFB50" <= c <= "\uFE6F":
            stats["presentation_forms_converted"] += 1

    # NFKC normalization — converts all Presentation Forms to standard Arabic
    text = unicodedata.normalize("NFKC", text)

    # Replace ornate parentheses (U+FD3E/FD3F) — NFKC doesn't decompose these
    text = text.replace("\uFD3E", "(").replace("\uFD3F", ")")

    # Strip tatweel/kashida (U+0640) — typographic stretching, not semantic
    tatweel_count = text.count("\u0640")
    stats["tatweel_stripped"] = tatweel_count
    text = text.replace("\u0640", "")

    # Strip decorative separator lines that stand alone (no words attached)
    # Matches: ====, ____, ****, •••, ---  (full line, 3+ chars)
    # NOT dots/periods — "..." could be speech ellipsis even standalone
    separator_count = 0
    cleaned_lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped and len(stripped) >= 3 and re.match(r"^[=_*•·\-]+$", stripped):
            separator_count += 1
        else:
            cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)
    stats["separators_stripped"] = separator_count

    # Collapse runs of spaces (but preserve newlines for paragraph detection)
    text = re.sub(r"[^\S\n]+", " ", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    return text, stats


# ---------------------------------------------------------------------------
# Format extractors
# ---------------------------------------------------------------------------

def extract_txt(path: str) -> str:
    """Read a plain text file with encoding detection."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Try UTF-8 first, fall back to CP-1256 (Windows Arabic)
    for encoding in ("utf-8", "cp1256"):
        try:
            return p.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode {path} as UTF-8 or CP-1256")


def extract_docx(path: str) -> str:
    """Extract text from a DOCX file using python-docx.

    Preserves paragraph structure. Skips empty paragraphs.
    """
    from docx import Document

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    doc = Document(str(p))
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


def extract_epub(path: str) -> str:
    """Extract text from an EPUB file using ebooklib + BeautifulSoup."""
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    book = epub.read_epub(str(p), options={"ignore_ncx": True})
    paragraphs = []

    # Get all HTML content items (some EPUBs use type 0, others ITEM_DOCUMENT)
    html_items = sorted(
        [item for item in book.get_items()
         if item.get_name().endswith((".html", ".xhtml"))
         and not item.get_name().startswith("nav")],
        key=lambda x: x.get_name(),
    )

    for item in html_items:
        html = item.get_content().decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")

        # Collect text from this page
        page_texts = []

        # Prefer <p> and heading tags (leaf-level content)
        leaf_tags = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])
        if leaf_tags:
            for tag in leaf_tags:
                text = tag.get_text(strip=True)
                if text:
                    page_texts.append(text)
        else:
            # Fallback: try <div> elements that don't contain nested blocks
            block_names = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6"}
            for div in soup.find_all("div"):
                if div.find(block_names):
                    continue  # skip container divs
                text = div.get_text(strip=True)
                if text:
                    page_texts.append(text)

        if not page_texts:
            # Last resort: grab body text directly
            body = soup.find("body")
            if body:
                text = body.get_text(strip=True)
                if text:
                    page_texts.append(text)

        # Skip pages with no Arabic content (e.g. archive.org notices)
        page_combined = " ".join(page_texts)
        arabic_chars = sum(1 for c in page_combined if "\u0600" <= c <= "\u06FF")
        if arabic_chars < 10:
            continue

        paragraphs.extend(page_texts)

    return "\n\n".join(paragraphs)


# ---------------------------------------------------------------------------
# Back-matter stripping
# ---------------------------------------------------------------------------

_BACK_MATTER_MARKERS = [
    "الناشر",           # "The publisher"
    "الترقيم الدولى",    # ISBN (Eastern spelling)
    "الترقيم الدولي",    # ISBN (Western spelling)
    "حقوق النشر",        # "Copyright"
    "حقوق الطبع",        # "Print rights"
]


def strip_back_matter(paragraphs: list[str]) -> tuple[list[str], list[str]]:
    """Remove publisher boilerplate from the end of a book.

    Scans the last 15 paragraphs for publisher markers (الناشر, ISBN, etc.).
    When found, removes from that point onward, plus any short preceding
    paragraphs (repeated book title, author name).

    Returns (cleaned_paragraphs, removed_paragraphs).
    """
    if len(paragraphs) < 5:
        return paragraphs, []

    search_start = max(0, len(paragraphs) - 15)

    # Find earliest paragraph containing a back-matter marker
    cut_idx = None
    for i in range(search_start, len(paragraphs)):
        for marker in _BACK_MATTER_MARKERS:
            if marker in paragraphs[i]:
                cut_idx = i
                break
        if cut_idx is not None:
            break

    if cut_idx is None:
        return paragraphs, []

    # Walk back over short preceding paragraphs (book title, author name)
    # Max 3 steps, only over lines < 50 chars (title/author are very short)
    walked = 0
    while cut_idx > 0 and walked < 3 and len(paragraphs[cut_idx - 1]) < 50:
        cut_idx -= 1
        walked += 1

    removed = paragraphs[cut_idx:]
    return paragraphs[:cut_idx], removed


# ---------------------------------------------------------------------------
# Paragraph splitting
# ---------------------------------------------------------------------------

def _split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs. Uses blank lines if present, else single newlines."""
    # Try blank-line splitting first
    raw_paragraphs = re.split(r"\n\s*\n", text)
    # If we got very few chunks but the text has many lines, it's hard-wrapped text
    # Fall back to single-newline splitting
    line_count = text.count("\n")
    if len(raw_paragraphs) <= 3 and line_count > 20:
        raw_paragraphs = text.split("\n")

    paragraphs = []
    for p in raw_paragraphs:
        cleaned = p.strip()
        if cleaned:
            # Collapse internal newlines within a paragraph to spaces
            cleaned = re.sub(r"\n", " ", cleaned)
            cleaned = re.sub(r" {2,}", " ", cleaned)
            paragraphs.append(cleaned)
    return paragraphs


# ---------------------------------------------------------------------------
# Ingest orchestrator
# ---------------------------------------------------------------------------

EXTRACTORS = {
    ".txt": extract_txt,
    ".epub": extract_epub,
    ".docx": extract_docx,
}


def ingest(book_path: str, output_dir: str = "output") -> dict:
    """Ingest a book file: extract → normalize → paragraph split → write output.

    Returns a summary dict.
    """
    bp = Path(book_path)
    suffix = bp.suffix.lower()

    if suffix not in EXTRACTORS:
        raise ValueError(f"Unsupported format: {suffix}")

    # Derive book slug from filename (no extension)
    book_slug = bp.stem

    # Extract raw text
    raw_text = EXTRACTORS[suffix](str(bp))

    # Normalize Arabic encoding
    clean_text, norm_stats = normalize_arabic(raw_text)

    # Split into paragraphs
    paragraphs = _split_paragraphs(clean_text)

    # Strip publisher boilerplate from end
    paragraphs, back_matter = strip_back_matter(paragraphs)

    # Prepare output directory: output/{format}/{book_slug}/ingestion/
    format_subdir = suffix.lstrip(".")
    out_dir = Path(output_dir) / format_subdir / book_slug / "ingestion"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write clean text (paragraphs separated by blank lines)
    clean_text_out = "\n\n".join(paragraphs)
    (out_dir / "clean_text.txt").write_text(clean_text_out, encoding="utf-8")

    # Write paragraphs CSV
    csv_path = out_dir / "paragraphs.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "paragraph_number", "char_count", "word_count", "first_50_chars"
        ])
        writer.writeheader()
        for i, para in enumerate(paragraphs, 1):
            writer.writerow({
                "paragraph_number": i,
                "char_count": len(para),
                "word_count": len(para.split()),
                "first_50_chars": para[:50],
            })

    # Build summary
    summary = {
        "book_slug": book_slug,
        "format": suffix,
        "total_chars": len(clean_text_out),
        "paragraph_count": len(paragraphs),
        "back_matter_removed": len(back_matter),
        "output_dir": str(out_dir),
        **norm_stats,
    }

    # Print encoding report
    print(f"\n--- Ingestion Report: {bp.name} ---")
    print(f"  Format: {suffix}")
    print(f"  Paragraphs: {len(paragraphs)}")
    print(f"  Total chars: {len(clean_text_out)}")
    print(f"  Presentation forms converted: {norm_stats['presentation_forms_converted']}")
    print(f"  Tatweel stripped: {norm_stats['tatweel_stripped']}")
    if back_matter:
        print(f"  Back-matter stripped: {len(back_matter)} paragraphs")
        print(f"    First removed: {back_matter[0][:60]}...")
    print(f"  Output: {out_dir}")

    return summary
