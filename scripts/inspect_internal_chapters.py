"""Check if single-file EPUBs contain internal chapter headings."""
import ebooklib
from ebooklib import epub
from pathlib import Path
from bs4 import BeautifulSoup
import re

EPUB_DIR = Path("/home/hamr/PycharmProjects/Sawt/data/books/epub")

# Books that had only 1 content spine item
SINGLE_FILE_BOOKS = [
    "bidaya-wa-nihaya.epub",
    "tharthara-fawq-al-nil-hindawi.epub",
    "zuqaq-al-midaqq.epub",
]

for name in SINGLE_FILE_BOOKS:
    book = epub.read_epub(str(EPUB_DIR / name), options={"ignore_ncx": False})
    print(f"\n{'='*80}")
    print(f"BOOK: {name}")

    # Get the single content item (the last spine item, which is the chapter)
    for item_id, linear in book.spine:
        item = book.get_item_with_id(item_id)
        if item and "chapter" in item.get_name():
            content = item.get_content().decode('utf-8', errors='replace')
            soup = BeautifulSoup(content, 'html.parser')

            # Find all heading tags
            headings = soup.find_all(re.compile(r'^h[1-6]$'))
            print(f"  Heading tags found: {len(headings)}")
            for i, h in enumerate(headings[:30]):
                text = h.get_text(strip=True)[:80]
                classes = h.get('class', [])
                print(f"    {i+1:>3}. <{h.name} class={classes}> {text}")
            if len(headings) > 30:
                print(f"    ... and {len(headings)-30} more headings")

            # Also check for <div> or <section> with class containing "chapter"
            chapter_divs = soup.find_all(['div', 'section'], class_=re.compile(r'chapter|section|part', re.I))
            if chapter_divs:
                print(f"\n  Chapter-like divs/sections: {len(chapter_divs)}")
                for d in chapter_divs[:10]:
                    text = d.get_text(strip=True)[:60]
                    print(f"    <{d.name} class={d.get('class', [])}> {text}...")

            # Check total text length
            text = soup.get_text()
            print(f"\n  Total text length: {len(text):,} chars")
            print(f"  Total paragraphs (<p> tags): {len(soup.find_all('p'))}")

# Also check awlad-haretna -- it has 5 content items but the book has 114 chapters
print(f"\n{'='*80}")
print(f"BOOK: awlad-haretna.epub (5 spine content items for a 114-chapter book)")
book = epub.read_epub(str(EPUB_DIR / "awlad-haretna.epub"), options={"ignore_ncx": False})
for item_id, linear in book.spine:
    item = book.get_item_with_id(item_id)
    if item and "chapter" in item.get_name():
        content = item.get_content().decode('utf-8', errors='replace')
        soup = BeautifulSoup(content, 'html.parser')
        headings = soup.find_all(re.compile(r'^h[1-6]$'))
        text = soup.get_text()
        print(f"\n  {item.get_name()}: {len(text):,} chars, {len(headings)} headings, {len(soup.find_all('p'))} paragraphs")
        for i, h in enumerate(headings[:5]):
            ht = h.get_text(strip=True)[:80]
            print(f"    {i+1}. <{h.name}> {ht}")
        if len(headings) > 5:
            print(f"    ... and {len(headings)-5} more headings")
