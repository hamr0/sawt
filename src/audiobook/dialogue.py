"""
POC-3 Phase A: Two-Voice Dialogue Detection

Binary classification of paragraphs into narrator vs dialogue segments.

Input:  output/{format}/{book}/02_chapters/chapter_*.txt
Output: output/{format}/{book}/03_segments/chapter_*.csv

CSV columns: segment_number, type, char_count, text
  type = "narrator" or "dialogue"

Dialogue markers:
  - Colon `:` — split: before = narrator (attribution), after = dialogue
  - Em dash `–/—` at paragraph start — whole paragraph = dialogue
  - Trailing colon — narrator sets up dialogue for next paragraph (one-shot)
  - Plain paragraphs are always narrator (no continuation across paragraphs)
  - Guillemets `«»` are NOT dialogue markers — they are typographic quotation marks
    (short quotes, inner thoughts, scare quotes). Kept as text, no voice switch.
"""
import csv
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEECH_ATTRIBUTION_LEN = 150  # Before-colon text shorter than this → assume dialogue
EM_DASH_CHARS = "–—-"  # En dash, em dash, hyphen-minus (used as dialogue dash)

# Arabic diacritics (harakat) — stripped before speech verb matching
DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670]")

# Speech attribution pattern for colon checks (includes present tense + participle)
# Used with diacritics stripped from text
COLON_ATTRIBUTION_RE = re.compile(
    r"(?:قال|قالت|قلت|قلنا|يقول|تقول"
    r"|أجاب|أجابت|سأل|سألت"
    r"|صاح|صاحت|همس|همست"
    r"|تساءل|تساءلت|صرخ|صرخت"
    r"|هتف|هتفت|تمتم|تمتمت|غمغم|غمغمت"
    r"|أضاف|أضافت|تابع|أردف"
    r"|قائلا|قائلة)"
)

# URL-like colons
URL_COLON_RE = re.compile(r"https?:|ftp:|mailto:")

CSV_COLUMNS = ["segment_number", "type", "char_count", "text"]


REVIEW_OPEN = "//"
REVIEW_CLOSE = "\\\\"


def _segments_to_review_text(segments: list[dict]) -> str:
    """Convert segments to annotated review text with // \\\\ around dialogue.

    Each segment becomes a paragraph (double-newline separated).
    Dialogue: // text \\\\
    Narrator: plain text
    """
    lines = []
    for seg in segments:
        if seg["type"] == "dialogue":
            lines.append(f"{REVIEW_OPEN} {seg['text']} {REVIEW_CLOSE}")
        else:
            lines.append(seg["text"])
    return "\n\n".join(lines)


def _split_at_review_markers(paragraph: str) -> list[tuple[str, str]]:
    """Split paragraph into segments at // \\\\ dialogue marker boundaries.

    Returns list of (type, text) tuples:
      - Text outside // \\\\ = "narrator"
      - Text inside // \\\\ = "dialogue"
    """
    segments: list[tuple[str, str]] = []
    pos = 0
    while pos < len(paragraph):
        open_pos = paragraph.find(REVIEW_OPEN, pos)
        if open_pos == -1:
            text = paragraph[pos:].strip()
            if text:
                segments.append(("narrator", text))
            break

        before = paragraph[pos:open_pos].strip()
        if before:
            segments.append(("narrator", before))

        close_pos = paragraph.find(REVIEW_CLOSE, open_pos + len(REVIEW_OPEN))
        if close_pos == -1:
            # Unclosed marker — treat rest as dialogue
            text = paragraph[open_pos + len(REVIEW_OPEN):].strip()
            if text:
                segments.append(("dialogue", text))
            break

        inner = paragraph[open_pos + len(REVIEW_OPEN):close_pos].strip()
        if inner:
            segments.append(("dialogue", inner))

        pos = close_pos + len(REVIEW_CLOSE)

    return segments


def parse_review_text(review_text: str) -> list[dict]:
    """Parse annotated review text (with // \\\\ dialogue markers) into segments.

    Inverse of _segments_to_review_text(). Used to read human-edited review
    files back into structured segments for SSML generation.

    Each paragraph separated by blank lines becomes one or more segments.
    Text inside // \\\\ = dialogue, everything else = narrator.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", review_text) if p.strip()]
    segments: list[dict] = []
    counter = 0

    for para in paragraphs:
        if REVIEW_OPEN in para and REVIEW_CLOSE in para:
            parts = _split_at_review_markers(para)
            for part_type, part_text in parts:
                text = part_text.strip()
                if text:
                    counter += 1
                    segments.append({
                        "segment_number": counter,
                        "type": part_type,
                        "char_count": len(text),
                        "text": text,
                    })
        else:
            counter += 1
            segments.append({
                "segment_number": counter,
                "type": "narrator",
                "char_count": len(para),
                "text": para,
            })

    return segments


def sync_review(segments_dir: str) -> int:
    """Re-generate ssml/ CSVs from edited review/ text files.

    Reads each review/*.txt, parses «» markers, writes matching ssml/*.csv.
    Returns the number of chapters synced.
    """
    seg_path = Path(segments_dir)
    review_dir = seg_path / "review"
    ssml_dir = seg_path / "ssml"

    if not review_dir.exists():
        raise FileNotFoundError(f"Review directory not found: {review_dir}")

    ssml_dir.mkdir(parents=True, exist_ok=True)

    review_files = sorted(review_dir.glob("chapter_*.txt"))
    for review_file in review_files:
        text = review_file.read_text(encoding="utf-8")
        segments = parse_review_text(text)

        csv_name = review_file.stem + ".csv"
        csv_path = ssml_dir / csv_name
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for seg in segments:
                writer.writerow(seg)

    return len(review_files)


# ---------------------------------------------------------------------------
# Marker detection
# ---------------------------------------------------------------------------

def _find_dialogue_colon(paragraph: str) -> int | None:
    """Find the index of the first valid dialogue colon in a paragraph.

    Returns the index of the colon, or None if no valid dialogue colon found.

    Filters out:
    - Time colons (digit:digit)
    - URL colons (http:)
    - Colon at end of paragraph (heading-style)
    - Colon with no Arabic text before or after
    """
    if ":" not in paragraph:
        return None

    for i, ch in enumerate(paragraph):
        if ch != ":":
            continue

        # Skip time-format colons: digit before AND after
        if i > 0 and i < len(paragraph) - 1:
            before_char = paragraph[i - 1]
            after_char = paragraph[i + 1]
            is_digit_before = before_char.isdigit() or "٠" <= before_char <= "٩"
            is_digit_after = after_char.isdigit() or "٠" <= after_char <= "٩"
            if is_digit_before and is_digit_after:
                continue

        # Skip URL-like colons
        start = max(0, i - 6)
        context = paragraph[start:i + 1]
        if URL_COLON_RE.search(context):
            continue

        # Must have text after the colon (not just whitespace/end)
        after = paragraph[i + 1:].strip()
        if not after:
            continue

        # Must have text before the colon
        before = paragraph[:i].strip()
        if not before:
            continue

        return i

    return None


def _strip_diacritics(text: str) -> str:
    """Strip Arabic diacritics (harakat) for speech verb matching."""
    return DIACRITICS_RE.sub("", text)


def _has_speech_attribution(text: str) -> bool:
    """Check if text contains a direct speech verb suitable for dialogue attribution.

    Short attributions (< SPEECH_ATTRIBUTION_LEN chars) are assumed to be dialogue
    — a short phrase before a colon is almost always speech attribution.
    Longer text requires an explicit speech verb in the last 100 chars.
    """
    if len(text) < SPEECH_ATTRIBUTION_LEN:
        return True
    clean = _strip_diacritics(text)
    context = clean[-100:]
    return bool(COLON_ATTRIBUTION_RE.search(context))


def _has_trailing_speech(text: str) -> bool:
    """Check if text (before a trailing colon) has a speech verb.

    Unlike _has_speech_attribution, always requires an explicit verb —
    trailing colons without speech verbs are headings/labels, not dialogue triggers.
    """
    clean = _strip_diacritics(text)
    context = clean[-100:] if len(clean) > 100 else clean
    return bool(COLON_ATTRIBUTION_RE.search(context))


def detect_markers(paragraph: str) -> str:
    """Classify a paragraph by its primary dialogue marker.

    Returns: "em_dash", "colon", "trailing_colon", or "plain"
    """
    stripped = paragraph.strip()
    if not stripped:
        return "plain"

    # Em dash at paragraph start (most specific)
    if stripped[0] in EM_DASH_CHARS and len(stripped) > 1 and stripped[1] in (" ", "\u00A0"):
        return "em_dash"

    # Colon check (dialogue attribution)
    if _find_dialogue_colon(stripped) is not None:
        return "colon"

    # Trailing colon: paragraph ends with colon, speech verb present → dialogue trigger
    if stripped.endswith(":") and len(stripped) > 1:
        before = stripped[:-1].strip()
        if before and _has_trailing_speech(before):
            return "trailing_colon"

    return "plain"


# ---------------------------------------------------------------------------
# Paragraph segmentation (state machine)
# ---------------------------------------------------------------------------

def _split_at_colon(paragraph: str) -> tuple[str, str]:
    """Split a paragraph at the first valid dialogue colon.

    Returns (before_colon, after_colon) with whitespace stripped.
    """
    idx = _find_dialogue_colon(paragraph)
    if idx is None:
        return paragraph, ""
    before = paragraph[:idx].strip()
    after = paragraph[idx + 1:].strip()
    return before, after


def segment_paragraphs(paragraphs: list[str]) -> list[dict]:
    """Segment paragraphs into narrator/dialogue using a state machine.

    State: NARRATOR or IN_DIALOGUE
    Returns list of segment dicts:
      {"segment_number": int, "type": str, "char_count": int, "text": str}
    """
    segments: list[dict] = []
    state = "NARRATOR"
    counter = 0

    def _emit(seg_type: str, text: str):
        nonlocal counter
        text = text.strip()
        if not text:
            return
        counter += 1
        segments.append({
            "segment_number": counter,
            "type": seg_type,
            "char_count": len(text),
            "text": text,
        })

    for para in paragraphs:
        stripped = para.strip()
        if not stripped:
            continue

        marker = detect_markers(stripped)

        if marker == "em_dash":
            dialogue_text = stripped.lstrip(EM_DASH_CHARS).strip()
            _emit("dialogue", dialogue_text)
            state = "NARRATOR"

        elif marker == "colon":
            before, after = _split_at_colon(stripped)
            if _has_speech_attribution(before):
                _emit("narrator", before)
                _emit("dialogue", after)
            else:
                # Explanatory colon (no speech verb) — not dialogue
                _emit("narrator", stripped)
            state = "NARRATOR"

        elif marker == "trailing_colon":
            # Attribution ending with colon — narrator, next paragraph is dialogue
            _emit("narrator", stripped.rstrip(":").strip())
            state = "IN_DIALOGUE"

        elif marker == "plain":
            if state == "IN_DIALOGUE":
                _emit("dialogue", stripped)
            else:
                _emit("narrator", stripped)
            state = "NARRATOR"

    return segments


# ---------------------------------------------------------------------------
# File I/O orchestrator
# ---------------------------------------------------------------------------

def segment_chapter(chapter_path: str, output_dir: str | None = None) -> dict:
    """Read a chapter file, segment into narrator/dialogue, write CSV.

    Args:
        chapter_path: Path to a chapter_*.txt file from POC-2.
        output_dir: Override output directory. Defaults to sibling segments/ dir.

    Returns summary dict with chapter stats.
    """
    ch_path = Path(chapter_path)
    if not ch_path.exists():
        raise FileNotFoundError(f"Chapter file not found: {chapter_path}")

    text = ch_path.read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    segments = segment_paragraphs(paragraphs)

    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = ch_path.parent.parent / "03_segments"

    ssml_dir = out_path / "ssml"
    review_dir = out_path / "review"
    ssml_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)

    # Machine-readable CSV for SSML generator
    csv_name = ch_path.stem + ".csv"
    csv_path = ssml_dir / csv_name
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for seg in segments:
            writer.writerow(seg)

    # Human-readable annotated text for review/editing
    review_name = ch_path.stem + ".txt"
    review_path = review_dir / review_name
    review_path.write_text(_segments_to_review_text(segments), encoding="utf-8")

    narrator_count = sum(1 for s in segments if s["type"] == "narrator")
    dialogue_count = sum(1 for s in segments if s["type"] == "dialogue")
    narrator_chars = sum(s["char_count"] for s in segments if s["type"] == "narrator")
    dialogue_chars = sum(s["char_count"] for s in segments if s["type"] == "dialogue")
    total_chars = narrator_chars + dialogue_chars

    summary = {
        "chapter": ch_path.stem,
        "total_segments": len(segments),
        "narrator_segments": narrator_count,
        "dialogue_segments": dialogue_count,
        "total_chars": total_chars,
        "narrator_chars": narrator_chars,
        "dialogue_chars": dialogue_chars,
        "dialogue_ratio": dialogue_chars / total_chars if total_chars > 0 else 0.0,
        "csv_path": str(csv_path),
        "review_path": str(review_path),
    }

    logger.debug("  %s: %d segments (N:%d D:%d) ratio=%.1f%%",
                 ch_path.stem, len(segments), narrator_count, dialogue_count,
                 summary["dialogue_ratio"] * 100)

    return summary


def segment_book(chapters_dir: str, output_dir: str | None = None) -> dict:
    """Segment all chapters in a book directory.

    Args:
        chapters_dir: Path to output/{format}/{book}/02_chapters/
        output_dir: Override for segments output dir. Defaults to sibling 03_segments/.

    Returns summary dict with per-chapter and aggregate stats.
    """
    ch_dir = Path(chapters_dir)
    if not ch_dir.exists():
        raise FileNotFoundError(f"Chapters directory not found: {chapters_dir}")

    chapter_files = sorted(ch_dir.glob("chapter_*.txt"))
    if not chapter_files:
        raise FileNotFoundError(f"No chapter_*.txt files in {chapters_dir}")

    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = ch_dir.parent / "03_segments"

    # Clear stale files from previous runs
    if out_path.exists():
        for subdir_name in ("ssml", "review"):
            subdir = out_path / subdir_name
            if subdir.exists():
                for old_file in subdir.glob("chapter_*"):
                    old_file.unlink()

    chapter_summaries = []
    for ch_file in chapter_files:
        ch_summary = segment_chapter(str(ch_file), str(out_path))
        chapter_summaries.append(ch_summary)

    total_chars = sum(s["total_chars"] for s in chapter_summaries)
    total_dialogue = sum(s["dialogue_chars"] for s in chapter_summaries)
    total_narrator = sum(s["narrator_chars"] for s in chapter_summaries)
    total_segments = sum(s["total_segments"] for s in chapter_summaries)

    # Write segments.csv — per-chapter breakdown for quality review
    summary_csv_columns = [
        "chapter", "total_segments", "narrator_segments", "dialogue_segments",
        "total_chars", "narrator_chars", "dialogue_chars", "dialogue_ratio",
    ]
    csv_path = out_path / "segments.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary_csv_columns)
        writer.writeheader()
        for ch in chapter_summaries:
            writer.writerow({
                "chapter": ch["chapter"],
                "total_segments": ch["total_segments"],
                "narrator_segments": ch["narrator_segments"],
                "dialogue_segments": ch["dialogue_segments"],
                "total_chars": ch["total_chars"],
                "narrator_chars": ch["narrator_chars"],
                "dialogue_chars": ch["dialogue_chars"],
                "dialogue_ratio": f"{ch['dialogue_ratio']:.3f}",
            })

    summary = {
        "chapters_dir": str(ch_dir),
        "output_dir": str(out_path),
        "total_chapters": len(chapter_summaries),
        "total_segments": total_segments,
        "total_chars": total_chars,
        "narrator_chars": total_narrator,
        "dialogue_chars": total_dialogue,
        "dialogue_ratio": total_dialogue / total_chars if total_chars > 0 else 0.0,
        "csv_path": str(csv_path),
        "chapters": chapter_summaries,
    }

    logger.info("Dialogue segmentation complete: %d chapters", len(chapter_summaries))
    logger.info("  Segments: %d | Chars: %d | Dialogue ratio: %.1f%%",
                total_segments, total_chars, summary["dialogue_ratio"] * 100)
    logger.debug("  Output: %s", out_path)

    return summary
