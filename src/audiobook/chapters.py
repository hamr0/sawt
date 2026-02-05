"""
POC-2: Chapter Detection & Splitting

Clean text → chapter files, split at paragraph boundaries when exceeding char limits.

Input:  output/{format}/{book}/ingestion/clean_text.txt
Output: output/{format}/{book}/chapters/chapter_01.txt, ...
        output/{format}/{book}/chapters/chapters.csv

Hard rules:
  1. Never cut mid-paragraph. Paragraphs are atomic.
  2. Delimiter OR size limit (~25K chars) — whichever comes first.
  3. All detection runs on clean_text.txt (format-agnostic).
"""
import csv
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_UNIT_CHARS = 25_000  # Azure SSML usable limit (~64KB / 2 for Arabic UTF-8, minus markup)
MIN_UNIT_CHARS = 200     # Below this, merge into neighbor (too short for standalone TTS)


# ---------------------------------------------------------------------------
# Delimiter detection patterns
# ---------------------------------------------------------------------------

# Shamela page markers — FILTER OUT, not delimiters
PAGE_MARKER_RE = re.compile(r"^\(\d+/\d+\)$")

# Lone Eastern Arabic numerals: ١, ٢, ١٠, etc. (standalone paragraph = chapter marker)
EASTERN_NUMERAL_RE = re.compile(r"^[٠-٩]+$")

# Lone Western numerals: 1, 2, 10, etc. (standalone paragraph = chapter marker)
WESTERN_NUMERAL_RE = re.compile(r"^[0-9]+$")

# Arabic structural heading terms (match at start of paragraph)
# Keyword must be followed by whitespace or end-of-string.
# Exclude conjunction patterns like "القسم والشرط" where the keyword is part of a compound
# phrase (و = "and" immediately after suggests grammatical usage, not a heading).
HEADING_RE = re.compile(
    r"^("
    r"الباب|باب"        # Part/Book (highest level in religious/academic texts)
    r"|الجزء|جزء"       # Volume/Part
    r"|القسم|قسم"       # Division
    r"|الفصل|فصل"       # Chapter
    r"|المبحث|مبحث"     # Topic/Section (academic)
    r"|المطلب|مطلب"     # Subtopic
    r"|الفرع|فرع"       # Branch/Subsection
    r"|مقدمة|تمهيد"     # Introduction/Preamble
    r"|خاتمة|إهداء"     # Conclusion/Dedication
    r")"
    r"(?:\s(?!و\s|و[^\s])|$)"  # Followed by space (but NOT و+space/word) or end of string
)

# Hierarchy levels (higher number = higher level in the book structure)
LEVEL_PRIORITY = {
    "الباب": 5, "باب": 5,
    "الجزء": 5, "جزء": 5,
    "القسم": 4, "قسم": 4,
    "الفصل": 3, "فصل": 3,
    "المبحث": 2, "مبحث": 2,
    "المطلب": 1, "مطلب": 1,
    "الفرع": 1, "فرع": 1,
    "مقدمة": 0, "تمهيد": 0,
    "خاتمة": 0, "إهداء": 0,
}


# ---------------------------------------------------------------------------
# Paragraph classification
# ---------------------------------------------------------------------------

def classify_paragraph(text: str) -> tuple[str, str | None]:
    """Classify a paragraph as a delimiter or content.

    Returns (kind, detail) where:
      - ("page_marker", None) — Shamela noise, filter out
      - ("eastern_numeral", "١٢") — chapter number
      - ("western_numeral", "12") — chapter number
      - ("heading", "الفصل") — Arabic heading term (the matched keyword)
      - ("content", None) — regular text paragraph
    """
    stripped = text.strip()

    if PAGE_MARKER_RE.match(stripped):
        return ("page_marker", None)

    if EASTERN_NUMERAL_RE.match(stripped):
        return ("eastern_numeral", stripped)

    if WESTERN_NUMERAL_RE.match(stripped):
        return ("western_numeral", stripped)

    m = HEADING_RE.match(stripped)
    if m:
        return ("heading", m.group(1))

    return ("content", None)


def detect_delimiters(paragraphs: list[str]) -> list[tuple[int, str, str | None]]:
    """Scan paragraphs and return all detected delimiters.

    Returns list of (paragraph_index, kind, detail) for non-content paragraphs.
    Page markers are included so callers can filter them.
    """
    results = []
    for i, para in enumerate(paragraphs):
        kind, detail = classify_paragraph(para)
        if kind != "content":
            results.append((i, kind, detail))
    return results


# ---------------------------------------------------------------------------
# Splitting logic
# ---------------------------------------------------------------------------

def _find_dominant_delimiter(detections: list[tuple[int, str, str | None]]) -> str | None:
    """Determine the book's dominant delimiter pattern from detections.

    Returns the most common non-page-marker kind, or None if no delimiters found.
    A single stray detection (e.g. lone "8" in a heading-dominated book) is ignored
    if it's < 5% of the dominant pattern's count.
    """
    counts: dict[str, int] = {}
    for _, kind, _ in detections:
        if kind == "page_marker":
            continue
        counts[kind] = counts.get(kind, 0) + 1

    if not counts:
        return None

    # Sort by count descending
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    dominant = ranked[0][0]
    dominant_count = ranked[0][1]

    # If there's a secondary pattern with < 5% of dominant, it's noise
    # (e.g. lone "8" when 47 headings exist)
    # We still return the dominant — the splitter will only use that kind
    return dominant


def _delimiter_indices(
    paragraphs: list[str],
    detections: list[tuple[int, str, str | None]],
    dominant: str,
) -> set[int]:
    """Return paragraph indices that are delimiters of the dominant kind."""
    return {i for i, kind, _ in detections if kind == dominant}


def _page_marker_indices(
    detections: list[tuple[int, str, str | None]],
) -> set[int]:
    """Return paragraph indices that are page markers (noise to skip)."""
    return {i for i, kind, _ in detections if kind == "page_marker"}


MAX_TITLE_LEN = 60  # Truncate long titles (DOCX merges heading + body into one paragraph)


def _truncate_title(title: str) -> str:
    """Truncate a title to MAX_TITLE_LEN chars, cutting at a word boundary."""
    if len(title) <= MAX_TITLE_LEN:
        return title
    truncated = title[:MAX_TITLE_LEN].rsplit(" ", 1)[0]
    return truncated + "…"


def _make_unit_name(
    unit_index: int,
    delimiter_title: str | None,
    dominant: str | None,
    is_pre_content: bool = False,
) -> str:
    """Generate a unit name based on the delimiter and index.

    For delimiter-based splits: the title text (truncated) or CH1, CH2.
    For size-based splits: 001, 002, 003.
    For pre-first-delimiter content: 000.
    """
    if dominant is None:
        return f"{unit_index:03d}"

    if is_pre_content:
        return "000"

    if delimiter_title:
        return _truncate_title(delimiter_title)
    return f"CH{unit_index}"


def split_into_units(
    paragraphs: list[str],
    max_chars: int = MAX_UNIT_CHARS,
) -> list[dict]:
    """Split paragraphs into units by delimiter or size limit, whichever comes first.

    Returns list of unit dicts:
      {
        "unit_number": int,
        "unit_name": str,
        "level": str,           # heading/eastern_numeral/western_numeral/size
        "title": str,           # delimiter paragraph text or ""
        "paragraphs": [str],    # content paragraphs (excludes delimiter + page markers)
        "char_count": int,
        "paragraph_count": int,
        "split_part": int,      # 0 if not sub-split, else 1-based part number
        "total_splits": int,    # 0 if not sub-split, else total parts
      }
    """
    detections = detect_delimiters(paragraphs)
    dominant = _find_dominant_delimiter(detections)
    delim_set = _delimiter_indices(paragraphs, detections, dominant) if dominant else set()
    page_set = _page_marker_indices(detections)

    raw_units: list[dict] = []
    current_paras: list[str] = []
    current_title = ""
    current_level = dominant or "size"
    seen_first_delimiter = False
    unit_counter = 0
    active_delimiter_idx = -1  # Paragraph index of current delimiter (persists across overflow flushes)

    def _flush(force_title: str = ""):
        """Flush current accumulator into a unit.

        If current_paras is empty AND there's no force_title, skip (nothing to flush).
        If current_paras is empty BUT force_title is set, create a title-only unit
        (e.g. trailing خاتمة or standalone مقدمة with no content after it).
        """
        nonlocal unit_counter, current_paras, current_title
        title = current_title or force_title
        if not current_paras and not title:
            return
        unit_counter += 1
        text = "\n\n".join(current_paras)
        raw_units.append({
            "unit_number": unit_counter,
            "unit_name": "",  # filled after sub-splitting
            "level": current_level,
            "title": title,
            "paragraphs": current_paras,
            "char_count": len(text),
            "paragraph_count": len(current_paras),
            "split_part": 0,
            "total_splits": 0,
            "_is_pre_content": dominant is not None and not seen_first_delimiter,
            "_delimiter_idx": active_delimiter_idx,
        })
        current_paras = []
        current_title = ""

    for i, para in enumerate(paragraphs):
        # Skip page markers entirely
        if i in page_set:
            continue

        # Hit a delimiter — close current unit, store title for next
        if i in delim_set:
            _flush()
            seen_first_delimiter = True
            current_title = para.strip()
            active_delimiter_idx = i  # Track for overflow grouping
            current_level = dominant or "size"
            continue

        # Would adding this paragraph exceed the limit?
        running_text = "\n\n".join(current_paras + [para])
        if len(running_text) > max_chars and current_paras:
            # Close at current paragraph boundary (before this paragraph)
            _flush()
            current_level = dominant or "size"

        current_paras.append(para)

    # Flush remaining
    _flush()

    # --- Sub-splitting: break oversized units at paragraph boundaries ---
    final_units: list[dict] = []
    global_counter = 0

    for unit in raw_units:
        is_pre = unit.pop("_is_pre_content", False)
        if unit["char_count"] <= max_chars:
            # Fits — no sub-splitting needed
            global_counter += 1
            unit["unit_number"] = global_counter
            unit["unit_name"] = _make_unit_name(global_counter, unit["title"], dominant, is_pre_content=is_pre)
            final_units.append(unit)
        else:
            # Sub-split this unit at paragraph boundaries
            sub_parts: list[list[str]] = []
            current_sub: list[str] = []
            for para in unit["paragraphs"]:
                candidate = "\n\n".join(current_sub + [para])
                if len(candidate) > max_chars and current_sub:
                    sub_parts.append(current_sub)
                    current_sub = []
                current_sub.append(para)
            if current_sub:
                sub_parts.append(current_sub)

            total = len(sub_parts)
            base_name = _make_unit_name(
                0, unit["title"], dominant, is_pre_content=is_pre,
            )
            for part_num, sub_paras in enumerate(sub_parts, 1):
                global_counter += 1
                text = "\n\n".join(sub_paras)

                if is_pre or not unit["title"]:
                    sub_name = f"{global_counter:03d}"
                elif total > 1:
                    sub_name = f"{base_name} - {part_num}/{total}"
                else:
                    sub_name = base_name

                final_units.append({
                    "unit_number": global_counter,
                    "unit_name": sub_name,
                    "level": unit["level"],
                    "title": unit["title"] if part_num == 1 else f"{unit['title']} ({part_num}/{total})",
                    "paragraphs": sub_paras,
                    "char_count": len(text),
                    "paragraph_count": len(sub_paras),
                    "split_part": 0,
                    "total_splits": 0,
                    "_delimiter_idx": unit.get("_delimiter_idx", -1),
                })

    # --- Post-process: fold title-only units into the next unit ---
    # A 0-paragraph unit (e.g. باب before فصل) is a parent container, not content.
    # Merge its title as a prefix into the next unit. Chains accumulate naturally:
    # باب (0p) → قسم (0p) → فصل (content) becomes "باب / قسم / فصل".
    # A trailing title-only unit (e.g. خاتمة at end) is kept as-is.
    merged: list[dict] = []
    i = 0
    while i < len(final_units):
        unit = final_units[i]
        if unit["paragraph_count"] == 0 and i + 1 < len(final_units):
            # Fold this title into the next unit
            next_unit = final_units[i + 1]
            parent = unit["title"]
            if next_unit["title"]:
                next_unit["title"] = f"{parent} / {next_unit['title']}"
            else:
                next_unit["title"] = parent
            next_unit["unit_name"] = _truncate_title(next_unit["title"])
            i += 1
            continue
        merged.append(unit)
        i += 1

    # --- Post-process: merge tiny units into neighbors ---
    # Units below MIN_UNIT_CHARS are too short for standalone TTS.
    # Prepend to the next unit; if last, append to previous.
    compact: list[dict] = []
    pending_tiny: list[dict] = []

    for unit in merged:
        if unit["char_count"] < MIN_UNIT_CHARS:
            pending_tiny.append(unit)
        else:
            if pending_tiny:
                for tiny in pending_tiny:
                    unit["paragraphs"] = tiny["paragraphs"] + unit["paragraphs"]
                    if tiny["title"] and unit["title"]:
                        unit["title"] = f"{tiny['title']} / {unit['title']}"
                    elif tiny["title"]:
                        unit["title"] = tiny["title"]
                text = "\n\n".join(unit["paragraphs"])
                unit["char_count"] = len(text)
                unit["paragraph_count"] = len(unit["paragraphs"])
                unit["unit_name"] = _truncate_title(unit["title"]) if unit["title"] else unit["unit_name"]
                pending_tiny = []
            compact.append(unit)

    # Trailing tiny units — append to last normal unit
    if pending_tiny and compact:
        last = compact[-1]
        for tiny in pending_tiny:
            last["paragraphs"] = last["paragraphs"] + tiny["paragraphs"]
        text = "\n\n".join(last["paragraphs"])
        last["char_count"] = len(text)
        last["paragraph_count"] = len(last["paragraphs"])
    elif pending_tiny:
        # All units are tiny — keep them as-is
        compact.extend(pending_tiny)

    # Renumber after merges
    for idx, unit in enumerate(compact, 1):
        unit["unit_number"] = idx

    # --- Assign split_part/total_splits for overflow groups ---
    # When a chapter exceeds max_chars, the main loop creates multiple units
    # sharing the same _delimiter_idx. Group consecutive units and number them.
    if dominant is not None:
        i = 0
        while i < len(compact):
            didx = compact[i].get("_delimiter_idx", -1)
            if didx < 0:
                i += 1
                continue
            # Start a group at this delimiter
            group_start = i
            i += 1
            while i < len(compact) and compact[i].get("_delimiter_idx", -1) == didx:
                i += 1
            group_size = i - group_start
            if group_size > 1:
                group_title = compact[group_start].get("title", "") or compact[group_start]["unit_name"]
                for part_num, idx in enumerate(range(group_start, i), 1):
                    compact[idx]["split_part"] = part_num
                    compact[idx]["total_splits"] = group_size
                    if part_num > 1:
                        label = _truncate_title(group_title)
                        compact[idx]["unit_name"] = f"{label} ({part_num}/{group_size})"

    # Strip internal tracking fields
    for unit in compact:
        unit.pop("_delimiter_idx", None)

    return compact


# ---------------------------------------------------------------------------
# File I/O orchestrator
# ---------------------------------------------------------------------------

CSV_COLUMNS = [
    "unit_number", "unit_name", "level", "title",
    "char_count", "paragraph_count", "split_part", "total_splits",
]


def _sanitize_filename(name: str) -> str:
    """Turn a unit_name into a safe filename component."""
    # Replace path-unsafe chars
    safe = re.sub(r'[\\/:*?"<>|]', "_", name)
    # Collapse whitespace
    safe = re.sub(r"\s+", "_", safe.strip())
    return safe or "unit"


def split_book(ingestion_dir: str, output_dir: str | None = None) -> dict:
    """Read clean_text.txt from POC-1 output, split into units, write files + CSV.

    Args:
        ingestion_dir: Path to output/{format}/{book}/ingestion/ (must contain clean_text.txt)
        output_dir: Override for chapters output dir. Defaults to sibling of ingestion_dir.

    Returns summary dict.
    """
    ing_path = Path(ingestion_dir)
    clean_text_path = ing_path / "clean_text.txt"
    if not clean_text_path.exists():
        raise FileNotFoundError(f"clean_text.txt not found in {ingestion_dir}")

    text = clean_text_path.read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    units = split_into_units(paragraphs)

    # Output directory: sibling "chapters" folder
    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = ing_path.parent / "chapters"
    out_path.mkdir(parents=True, exist_ok=True)

    # Clear stale chapter files from previous runs
    for old_file in out_path.glob("chapter_*.txt"):
        old_file.unlink()

    # Write individual unit text files (title prepended for TTS)
    for unit in units:
        fname = f"chapter_{unit['unit_number']:02d}.txt"
        parts = []
        if unit["title"]:
            parts.append(unit["title"])
        parts.extend(unit["paragraphs"])
        unit_text = "\n\n".join(parts)
        (out_path / fname).write_text(unit_text, encoding="utf-8")

    # Write chapters.csv
    csv_path = out_path / "chapters.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for unit in units:
            writer.writerow({col: unit[col] for col in CSV_COLUMNS})

    # Detect dominant delimiter for summary
    detections = detect_delimiters(paragraphs)
    dominant = _find_dominant_delimiter(detections)
    page_markers = sum(1 for _, k, _ in detections if k == "page_marker")

    total_chars = sum(u["char_count"] for u in units)
    splits_needed = sum(1 for u in units if u["split_part"] > 0)

    summary = {
        "ingestion_dir": str(ing_path),
        "output_dir": str(out_path),
        "delimiter_type": dominant or "none (size-based)",
        "total_units": len(units),
        "total_chars": total_chars,
        "total_paragraphs": len(paragraphs),
        "page_markers_filtered": page_markers,
        "sub_splits": splits_needed,
    }

    print(f"\n--- Chapter Split Report ---")
    print(f"  Delimiter: {summary['delimiter_type']}")
    print(f"  Units: {summary['total_units']}")
    print(f"  Total chars: {summary['total_chars']}")
    print(f"  Page markers filtered: {summary['page_markers_filtered']}")
    print(f"  Sub-splits needed: {summary['sub_splits']}")
    print(f"  Output: {out_path}")

    return summary
