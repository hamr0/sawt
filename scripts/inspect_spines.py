"""Inspect EPUB spine structure for all test books."""
import os
import re
import ebooklib
from ebooklib import epub
from pathlib import Path

EPUB_DIR = Path("/home/hamr/PycharmProjects/Sawt/data/books/epub")

# Patterns that suggest chapter-like content vs. front/back matter
CHAPTER_PATTERNS = re.compile(
    r'(chapter|chap|ch[\-_]?\d|section|part[\-_]?\d|content[\-_]?\d|text[\-_]?\d)',
    re.IGNORECASE
)
FRONTMATTER_PATTERNS = re.compile(
    r'(cover|toc|title|nav|copyright|dedication|preface|foreword|intro|colophon|about|index|appendix|bibliography|glossary)',
    re.IGNORECASE
)


def classify_item(item_id, href):
    """Classify a spine item based on its ID and href."""
    combined = f"{item_id} {href}"
    if FRONTMATTER_PATTERNS.search(combined):
        return "frontmatter/backmatter"
    if CHAPTER_PATTERNS.search(combined):
        return "chapter-like"
    return "content (unclassified)"


def inspect_epub(epub_path):
    """Inspect spine structure of a single EPUB."""
    book = epub.read_epub(str(epub_path), options={"ignore_ncx": False})

    print(f"\n{'='*80}")
    print(f"BOOK: {epub_path.name}")
    print(f"{'='*80}")

    # --- Metadata ---
    title = book.get_metadata('DC', 'title')
    if title:
        print(f"Title: {title[0][0]}")

    # --- Spine ---
    spine = book.spine
    print(f"\nSpine items: {len(spine)}")
    print(f"{'─'*80}")
    print(f"{'#':>3}  {'ID':<30}  {'Linear':>6}  {'Href':<40}  Classification")
    print(f"{'─'*80}")

    chapter_count = 0
    front_count = 0
    content_count = 0

    for i, (item_id, linear) in enumerate(spine):
        # Look up the actual item to get href
        item = book.get_item_with_id(item_id)
        href = item.get_name() if item else "???"
        classification = classify_item(item_id, href)

        if "chapter" in classification:
            chapter_count += 1
        elif "front" in classification:
            front_count += 1
        else:
            content_count += 1

        # Truncate long hrefs
        href_display = href if len(href) <= 40 else "..." + href[-37:]
        print(f"{i+1:>3}  {item_id:<30}  {str(linear):>6}  {href_display:<40}  {classification}")

    print(f"\nSummary: {chapter_count} chapter-like, {front_count} front/backmatter, {content_count} unclassified content")

    # --- Check content size of each spine item ---
    print(f"\n{'─'*80}")
    print(f"Content size per spine item (top 10 largest):")
    print(f"{'─'*80}")

    sizes = []
    for item_id, linear in spine:
        item = book.get_item_with_id(item_id)
        if item:
            content = item.get_content()
            sizes.append((item_id, item.get_name(), len(content)))

    sizes.sort(key=lambda x: x[2], reverse=True)
    for item_id, href, size in sizes[:10]:
        print(f"  {item_id:<30}  {size:>8,} bytes  {href}")

    # --- Check NCX / Table of Contents ---
    toc = book.toc
    print(f"\n{'─'*80}")
    print(f"Table of Contents entries: {len(toc)}")
    print(f"{'─'*80}")
    for i, entry in enumerate(toc[:20]):
        if isinstance(entry, tuple):
            # It's a section with sub-items
            section, children = entry
            print(f"  {i+1:>3}. [Section] {section.title}  -> {section.href}")
            for j, child in enumerate(children[:5]):
                print(f"       {j+1}. {child.title}  -> {child.href}")
            if len(children) > 5:
                print(f"       ... and {len(children)-5} more sub-items")
        else:
            print(f"  {i+1:>3}. {entry.title}  -> {entry.href}")
    if len(toc) > 20:
        print(f"  ... and {len(toc)-20} more entries")

    # --- Key question: do spine items map 1:1 to TOC entries? ---
    spine_hrefs = set()
    for item_id, linear in spine:
        item = book.get_item_with_id(item_id)
        if item:
            spine_hrefs.add(item.get_name().split('#')[0])

    toc_hrefs = set()
    def collect_toc_hrefs(entries):
        for entry in entries:
            if isinstance(entry, tuple):
                section, children = entry
                toc_hrefs.add(section.href.split('#')[0])
                collect_toc_hrefs(children)
            else:
                toc_hrefs.add(entry.href.split('#')[0])
    collect_toc_hrefs(toc)

    in_spine_not_toc = spine_hrefs - toc_hrefs
    in_toc_not_spine = toc_hrefs - spine_hrefs

    print(f"\n{'─'*80}")
    print(f"Spine vs TOC alignment:")
    print(f"  Spine hrefs: {len(spine_hrefs)}")
    print(f"  TOC hrefs:   {len(toc_hrefs)}")
    print(f"  In spine but not TOC: {len(in_spine_not_toc)} {list(in_spine_not_toc)[:5] if in_spine_not_toc else ''}")
    print(f"  In TOC but not spine: {len(in_toc_not_spine)} {list(in_toc_not_spine)[:5] if in_toc_not_spine else ''}")

    return {
        "name": epub_path.name,
        "spine_count": len(spine),
        "toc_count": len(toc),
        "chapter_count": chapter_count,
    }


if __name__ == "__main__":
    results = []
    for epub_file in sorted(EPUB_DIR.glob("*.epub")):
        try:
            result = inspect_epub(epub_file)
            results.append(result)
        except Exception as e:
            print(f"\nERROR processing {epub_file.name}: {e}")

    # Final comparison table
    print(f"\n\n{'='*80}")
    print(f"COMPARISON TABLE")
    print(f"{'='*80}")
    print(f"{'Book':<45}  {'Spine':>5}  {'TOC':>5}  {'Ch-like':>7}")
    print(f"{'─'*80}")
    for r in results:
        print(f"{r['name']:<45}  {r['spine_count']:>5}  {r['toc_count']:>5}  {r['chapter_count']:>7}")
