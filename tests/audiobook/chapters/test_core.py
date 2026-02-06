"""Tests for POC-2: Chapter Detection & Splitting"""
import csv
from pathlib import Path

import pytest

from src.audiobook.chapters import (
    MAX_UNIT_CHARS,
    MIN_UNIT_CHARS,
    classify_paragraph,
    detect_delimiters,
    split_book,
    split_into_units,
    _find_dominant_delimiter,
    _truncate_title,
)


# ---------------------------------------------------------------------------
# classify_paragraph
# ---------------------------------------------------------------------------

class TestClassifyParagraph:
    def test_page_marker(self):
        assert classify_paragraph("(1/406)") == ("page_marker", None)
        assert classify_paragraph("(23/100)") == ("page_marker", None)

    def test_not_page_marker(self):
        assert classify_paragraph("(text)")[0] == "content"
        assert classify_paragraph("(1/2/3)")[0] == "content"

    def test_eastern_numeral(self):
        assert classify_paragraph("١") == ("eastern_numeral", "١")
        assert classify_paragraph("١٠") == ("eastern_numeral", "١٠")
        assert classify_paragraph("١١٤") == ("eastern_numeral", "١١٤")

    def test_western_numeral(self):
        assert classify_paragraph("1") == ("western_numeral", "1")
        assert classify_paragraph("42") == ("western_numeral", "42")

    def test_numeral_with_text_is_content(self):
        assert classify_paragraph("١ مقدمة")[0] == "content"
        assert classify_paragraph("Chapter 1")[0] == "content"

    def test_heading_keywords(self):
        assert classify_paragraph("الفصل الأول") == ("heading", "الفصل")
        assert classify_paragraph("فصل في التجويد") == ("heading", "فصل")
        assert classify_paragraph("الباب الثاني") == ("heading", "الباب")
        assert classify_paragraph("باب المد والقصر") == ("heading", "باب")
        assert classify_paragraph("مقدمة") == ("heading", "مقدمة")
        assert classify_paragraph("خاتمة") == ("heading", "خاتمة")
        assert classify_paragraph("تمهيد") == ("heading", "تمهيد")
        assert classify_paragraph("إهداء") == ("heading", "إهداء")
        assert classify_paragraph("المبحث الأول") == ("heading", "المبحث")
        assert classify_paragraph("القسم الرابع") == ("heading", "القسم")

    def test_heading_standalone(self):
        """Keyword alone (end-of-string) should match."""
        assert classify_paragraph("مقدمة") == ("heading", "مقدمة")
        assert classify_paragraph("خاتمة") == ("heading", "خاتمة")

    def test_conjunction_exclusion(self):
        """Keywords followed by و (conjunction) are grammatical, not structural."""
        assert classify_paragraph("القسم والشرط")[0] == "content"
        assert classify_paragraph("فصل ومعنى")[0] == "content"

    def test_content(self):
        assert classify_paragraph("هذا نص عادي")[0] == "content"
        assert classify_paragraph("محتوى الكتاب الأول")[0] == "content"

    def test_whitespace_stripped(self):
        assert classify_paragraph("  ١  ") == ("eastern_numeral", "١")
        assert classify_paragraph("  (1/406)  ") == ("page_marker", None)


# ---------------------------------------------------------------------------
# detect_delimiters
# ---------------------------------------------------------------------------

class TestDetectDelimiters:
    def test_mixed_paragraphs(self):
        paras = ["مقدمة", "نص عادي", "١", "نص آخر", "(1/406)"]
        dets = detect_delimiters(paras)
        assert len(dets) == 3
        assert dets[0] == (0, "heading", "مقدمة")
        assert dets[1] == (2, "eastern_numeral", "١")
        assert dets[2] == (4, "page_marker", None)

    def test_no_delimiters(self):
        paras = ["نص عادي", "نص آخر", "المزيد من النص"]
        assert detect_delimiters(paras) == []


# ---------------------------------------------------------------------------
# _find_dominant_delimiter
# ---------------------------------------------------------------------------

class TestFindDominant:
    def test_heading_dominant(self):
        dets = [(0, "heading", "الفصل"), (5, "heading", "الباب"), (10, "heading", "فصل")]
        assert _find_dominant_delimiter(dets) == "heading"

    def test_eastern_dominant(self):
        dets = [(0, "eastern_numeral", "١"), (5, "eastern_numeral", "٢")]
        assert _find_dominant_delimiter(dets) == "eastern_numeral"

    def test_page_markers_ignored(self):
        dets = [
            (0, "page_marker", None), (1, "page_marker", None),
            (5, "heading", "الفصل"),
        ]
        assert _find_dominant_delimiter(dets) == "heading"

    def test_no_delimiters(self):
        assert _find_dominant_delimiter([]) is None
        dets = [(0, "page_marker", None)]
        assert _find_dominant_delimiter(dets) is None


# ---------------------------------------------------------------------------
# split_into_units — core logic
# ---------------------------------------------------------------------------

class TestSplitIntoUnits:
    def test_size_fallback_no_delimiters(self):
        """Books with no delimiters split by size at paragraph boundaries."""
        paras = [f"محتوى الفقرة {i}" * 100 for i in range(10)]
        units = split_into_units(paras, max_chars=5000)
        assert all(u["char_count"] <= 5000 for u in units)
        assert all(u["level"] == "size" for u in units)
        # All content preserved
        all_paras = [p for u in units for p in u["paragraphs"]]
        assert all_paras == paras

    def test_delimiter_split(self):
        """Eastern numeral delimiters split correctly."""
        paras = ["١", "محتوى الفصل الأول", "٢", "محتوى الفصل الثاني"]
        units = split_into_units(paras)
        assert len(units) == 2
        assert units[0]["title"] == "١"
        assert units[0]["paragraphs"] == ["محتوى الفصل الأول"]
        assert units[1]["title"] == "٢"
        assert units[1]["paragraphs"] == ["محتوى الفصل الثاني"]

    def test_pre_delimiter_content(self):
        """Content before the first delimiter becomes unit 000."""
        paras = ["بداية النص قبل أي فصل", "١", "محتوى"]
        units = split_into_units(paras)
        assert units[0]["unit_name"] == "000"
        assert units[0]["paragraphs"] == ["بداية النص قبل أي فصل"]

    def test_page_markers_filtered(self):
        """Page markers are excluded from content and don't act as delimiters."""
        paras = ["الفصل الأول", "محتوى", "(1/406)", "المزيد", "(2/406)"]
        units = split_into_units(paras)
        assert len(units) == 1
        assert units[0]["paragraphs"] == ["محتوى", "المزيد"]

    def test_paragraph_never_split(self):
        """A single paragraph larger than max_chars stays intact (atomic rule)."""
        big_para = "كلمة " * 10_000  # ~50K chars
        paras = [big_para]
        units = split_into_units(paras, max_chars=5000)
        assert len(units) == 1
        assert units[0]["paragraphs"] == [big_para]

    def test_sub_splitting(self):
        """Oversized chapter gets sub-split at paragraph boundaries."""
        paras = ["١"] + [f"فقرة {i} " * 200 for i in range(10)]  # ~14K per para
        units = split_into_units(paras, max_chars=5000)
        assert all(u["level"] == "eastern_numeral" for u in units)
        # All content preserved
        all_paras = [p for u in units for p in u["paragraphs"]]
        assert all_paras == paras[1:]  # exclude delimiter

    def test_numbering_sequential(self):
        units = split_into_units(["١", "أ", "٢", "ب", "٣", "ج"])
        numbers = [u["unit_number"] for u in units]
        assert numbers == [1, 2, 3]


# ---------------------------------------------------------------------------
# Parent folding (nesting)
# ---------------------------------------------------------------------------

class TestParentFolding:
    def test_parent_child_folded(self):
        """Empty parent (باب) folds title into next child (فصل)."""
        paras = ["الباب الأول", "فصل في التجويد", "محتوى"]
        units = split_into_units(paras)
        assert len(units) == 1
        assert "الباب الأول / فصل" in units[0]["title"]

    def test_triple_chain(self):
        """Three-level chain folds into single unit."""
        paras = ["الباب الأول", "القسم الثاني", "فصل في النحو", "محتوى"]
        units = split_into_units(paras)
        assert len(units) == 1
        assert "الباب الأول / القسم الثاني / فصل" in units[0]["title"]

    def test_trailing_delimiter_kept(self):
        """Trailing delimiter with no successor is kept as title-only."""
        paras = ["محتوى الكتاب", "خاتمة"]
        units = split_into_units(paras)
        assert len(units) == 2
        assert units[1]["title"] == "خاتمة"
        assert units[1]["paragraph_count"] == 0

    def test_parent_with_own_content_not_folded(self):
        """A parent with content between it and the child is NOT folded."""
        paras = ["الباب الأول", "محتوى الباب", "فصل في التجويد", "محتوى الفصل"]
        units = split_into_units(paras)
        assert len(units) == 2
        assert units[0]["title"] == "الباب الأول"
        assert units[0]["paragraph_count"] == 1

    def test_two_parent_child_pairs(self):
        paras = [
            "الباب الأول", "فصل في النحو", "محتوى أول",
            "الباب الثاني", "فصل في الصرف", "محتوى ثان",
        ]
        units = split_into_units(paras)
        assert len(units) == 2
        assert "الباب الأول / فصل" in units[0]["title"]
        assert "الباب الثاني / فصل" in units[1]["title"]


# ---------------------------------------------------------------------------
# _truncate_title
# ---------------------------------------------------------------------------

class TestTruncateTitle:
    def test_short_title_unchanged(self):
        assert _truncate_title("فصل") == "فصل"

    def test_long_title_truncated(self):
        long = "الفصل الأول في معنى التجويد وفيه فصول كثيرة جداً تتناول موضوعات عديدة ومتنوعة"
        result = _truncate_title(long)
        assert len(result) <= 61  # 60 + ellipsis char
        assert result.endswith("…")


# ---------------------------------------------------------------------------
# split_book (file I/O orchestrator)
# ---------------------------------------------------------------------------

class TestSplitBook:
    def test_split_book_writes_files(self, tmp_path):
        """split_book reads clean_text.txt and writes chapter files + CSV."""
        # Setup: fake ingestion output
        ing_dir = tmp_path / "epub" / "test-book" / "ingestion"
        ing_dir.mkdir(parents=True)
        paras = ["١", "محتوى الفصل الأول الطويل", "٢", "محتوى الفصل الثاني"]
        (ing_dir / "clean_text.txt").write_text(
            "\n\n".join(paras), encoding="utf-8"
        )

        summary = split_book(str(ing_dir))

        chap_dir = ing_dir.parent / "02_chapters"
        assert chap_dir.exists()

        # Check chapter text files
        chapter_files = sorted(chap_dir.glob("chapter_*.txt"))
        assert len(chapter_files) == 2
        # Title is prepended to chapter content for TTS
        assert chapter_files[0].read_text(encoding="utf-8") == "١\n\nمحتوى الفصل الأول الطويل"
        assert chapter_files[1].read_text(encoding="utf-8") == "٢\n\nمحتوى الفصل الثاني"

        # Check CSV
        csv_path = chap_dir / "chapters.csv"
        assert csv_path.exists()
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2
        assert rows[0]["unit_name"] == "١"
        assert rows[1]["unit_name"] == "٢"

        # Check summary
        assert summary["delimiter_type"] == "eastern_numeral"
        assert summary["total_units"] == 2

    def test_split_book_size_fallback(self, tmp_path):
        """Books with no delimiters get size-based splitting."""
        ing_dir = tmp_path / "txt" / "plain-book" / "ingestion"
        ing_dir.mkdir(parents=True)
        paras = [f"فقرة طويلة جداً رقم {i} " * 500 for i in range(5)]
        (ing_dir / "clean_text.txt").write_text(
            "\n\n".join(paras), encoding="utf-8"
        )

        summary = split_book(str(ing_dir))
        assert summary["delimiter_type"] == "none (size-based)"
        assert summary["total_units"] >= 2

        chap_dir = ing_dir.parent / "02_chapters"
        chapter_files = sorted(chap_dir.glob("chapter_*.txt"))
        assert len(chapter_files) == summary["total_units"]

    def test_split_book_missing_clean_text(self, tmp_path):
        ing_dir = tmp_path / "missing"
        ing_dir.mkdir(parents=True)
        with pytest.raises(FileNotFoundError):
            split_book(str(ing_dir))

    def test_split_book_clears_stale_files(self, tmp_path):
        """Re-running split_book removes orphaned chapter files from previous runs."""
        ing_dir = tmp_path / "epub" / "stale-test" / "ingestion"
        ing_dir.mkdir(parents=True)
        chap_dir = ing_dir.parent / "02_chapters"
        chap_dir.mkdir(parents=True)

        # Simulate a previous run that produced 5 chapter files
        for i in range(1, 6):
            (chap_dir / f"chapter_{i:02d}.txt").write_text(f"old {i}", encoding="utf-8")

        # New run produces only 2 chapters
        paras = ["١", "محتوى أول", "٢", "محتوى ثان"]
        (ing_dir / "clean_text.txt").write_text("\n\n".join(paras), encoding="utf-8")
        split_book(str(ing_dir))

        chapter_files = sorted(chap_dir.glob("chapter_*.txt"))
        assert len(chapter_files) == 2
        # Old files are gone, not just overwritten
        assert not (chap_dir / "chapter_03.txt").exists()

    def test_split_book_custom_output_dir(self, tmp_path):
        ing_dir = tmp_path / "ingestion"
        ing_dir.mkdir(parents=True)
        (ing_dir / "clean_text.txt").write_text("نص بسيط", encoding="utf-8")

        custom_out = tmp_path / "custom_chapters"
        split_book(str(ing_dir), output_dir=str(custom_out))
        assert (custom_out / "chapters.csv").exists()
        assert (custom_out / "chapter_01.txt").exists()


# ---------------------------------------------------------------------------
# Integration: real books (data-driven)
# ---------------------------------------------------------------------------

BOOK_DIR = Path("data/books")

EPUB_BOOKS = [
    "al-liss-wal-kilab",
    "awlad-haretna",
    "bidaya-wa-nihaya",
    "tharthara-fawq-al-nil-hindawi",
    "zuqaq-al-midaqq",
]

DOCX_BOOKS = [
    "al-tamheed-fi-tajweed",
    "jawahir-al-adab",
    "mabahith-ulum-alquran",
    "mawsuat-al-ijaz-al-ilmi",
]

TXT_BOOKS = [
    "رحلة-ابن-فطومة",
    "صدى-النسيان",
    "يوميات-نائب-في-الأرياف",
]


def _load_paragraphs(book_name: str) -> list[str]:
    """Find and load a book, return paragraphs."""
    import re as _re
    from src.audiobook.ingest import EXTRACTORS, normalize_arabic

    for ext in (".epub", ".docx", ".txt"):
        path = BOOK_DIR / ext.lstrip(".") / (book_name + ext)
        if path.exists():
            raw = EXTRACTORS[ext](str(path))
            clean, _ = normalize_arabic(raw)
            return [p.strip() for p in _re.split(r"\n\s*\n", clean) if p.strip()]
    pytest.skip(f"Book not found: {book_name}")


def _all_book_names():
    return EPUB_BOOKS + DOCX_BOOKS + TXT_BOOKS


@pytest.mark.parametrize("book_name", _all_book_names())
class TestRealBooks:
    def test_no_oversized_units(self, book_name):
        paras = _load_paragraphs(book_name)
        units = split_into_units(paras)
        oversized = [u for u in units if u["char_count"] > MAX_UNIT_CHARS]
        assert oversized == [], (
            f"{book_name}: {len(oversized)} units exceed {MAX_UNIT_CHARS} chars"
        )

    def test_text_integrity(self, book_name):
        """All content paragraphs are preserved in order."""
        paras = _load_paragraphs(book_name)
        detections = detect_delimiters(paras)
        dominant = _find_dominant_delimiter(detections)

        skip = set()
        for idx, kind, _ in detections:
            if kind == "page_marker":
                skip.add(idx)
            elif dominant and kind == dominant:
                skip.add(idx)

        expected = [p for i, p in enumerate(paras) if i not in skip]
        units = split_into_units(paras)
        actual = [p for u in units for p in u["paragraphs"]]
        assert actual == expected, f"{book_name}: text integrity mismatch"

    def test_no_paragraph_split(self, book_name):
        """Every paragraph in every unit exists as a complete original paragraph."""
        paras = _load_paragraphs(book_name)
        para_set = set(paras)
        units = split_into_units(paras)
        for u in units:
            for p in u["paragraphs"]:
                assert p in para_set, (
                    f"{book_name}: unit {u['unit_number']} has paragraph not in original"
                )

    def test_sequential_numbering(self, book_name):
        paras = _load_paragraphs(book_name)
        units = split_into_units(paras)
        numbers = [u["unit_number"] for u in units]
        assert numbers == list(range(1, len(units) + 1))


# --- Tiny unit merge tests ---

class TestTinyUnitMerge:
    """Units below MIN_UNIT_CHARS are merged into neighbors."""

    def _content_para(self, n=1):
        """A content paragraph well above MIN_UNIT_CHARS."""
        return "هذا نص طويل بما يكفي. " * 30  # ~600 chars

    def test_tiny_preamble_merged_into_next(self):
        """A tiny preamble (book title) is prepended to the first real chapter."""
        paras = ["زقاق المدق", "١"] + [self._content_para() for _ in range(5)]
        units = split_into_units(paras)
        # The preamble should be merged — first unit should contain it
        assert units[0]["paragraphs"][0] == "زقاق المدق"
        assert units[0]["char_count"] >= MIN_UNIT_CHARS

    def test_tiny_trailing_merged_into_previous(self):
        """A tiny trailing unit is appended to the last real chapter."""
        paras = (
            ["١"] + [self._content_para()] +
            ["٢"] + [self._content_para()] +
            ["٣", "خاتمة قصيرة"]
        )
        units = split_into_units(paras)
        last = units[-1]
        assert "خاتمة قصيرة" in last["paragraphs"]

    def test_normal_units_unchanged(self):
        """Units above MIN_UNIT_CHARS are not merged."""
        paras = ["١"] + [self._content_para()] + ["٢"] + [self._content_para()]
        units = split_into_units(paras)
        # Should have at least 2 real units (no merging)
        content_units = [u for u in units if u["char_count"] >= MIN_UNIT_CHARS]
        assert len(content_units) >= 2

    def test_all_tiny_kept(self):
        """If every unit is tiny, keep them all (don't crash)."""
        paras = ["سطر قصير", "سطر آخر", "سطر ثالث"]
        units = split_into_units(paras)
        assert len(units) >= 1
        # All text preserved
        all_text = " ".join(p for u in units for p in u["paragraphs"])
        assert "سطر قصير" in all_text

    def test_renumbered_after_merge(self):
        """Unit numbers are sequential after merging."""
        paras = ["عنوان", "١"] + [self._content_para() for _ in range(4)]
        units = split_into_units(paras)
        numbers = [u["unit_number"] for u in units]
        assert numbers == list(range(1, len(units) + 1))


# ---------------------------------------------------------------------------
# Split part tracking (overflow grouping)
# ---------------------------------------------------------------------------

class TestSplitPartTracking:
    """When a chapter exceeds max_chars, overflow units track split_part/total_splits."""

    def test_overflow_units_get_split_tracking(self):
        """Multiple units from the same delimiter get split_part=1..N, total_splits=N."""
        # Build: delimiter + enough content to create 3 overflow units at 500-char limit
        big_para = "كلمة عربية طويلة. " * 30  # ~570 chars each
        paras = ["الفصل الأول"] + [big_para for _ in range(5)]
        units = split_into_units(paras, max_chars=500)
        assert len(units) >= 2
        # All units should have split tracking
        for u in units:
            assert u["total_splits"] == len(units)
            assert 1 <= u["split_part"] <= len(units)
        # First unit has the title
        assert units[0]["title"] == "الفصل الأول"
        assert units[0]["split_part"] == 1
        # Overflow units get named with part number
        if len(units) > 1:
            assert f"(2/{len(units)})" in units[1]["unit_name"]

    def test_no_split_tracking_when_fits(self):
        """Chapters that fit in one unit have split_part=0, total_splits=0."""
        paras = ["١", "محتوى قصير", "٢", "محتوى آخر"]
        units = split_into_units(paras)
        for u in units:
            assert u["split_part"] == 0
            assert u["total_splits"] == 0

    def test_mixed_split_and_non_split(self):
        """One oversized chapter + one normal chapter."""
        big_para = "كلمة عربية طويلة. " * 30  # ~570 chars
        normal_para = "محتوى الفصل الثاني كامل. " * 20  # ~500 chars, above MIN_UNIT_CHARS
        paras = (
            ["١"] + [big_para for _ in range(5)] +
            ["٢", normal_para]
        )
        units = split_into_units(paras, max_chars=500)
        # Find the ٢ chapter (last unit)
        last = units[-1]
        assert last["title"] == "٢"
        assert last["split_part"] == 0
        assert last["total_splits"] == 0
        # First chapter's units have split tracking
        split_units = [u for u in units if u["total_splits"] > 0]
        assert len(split_units) >= 2

    def test_size_only_books_no_split_tracking(self):
        """Size-based books (no delimiters) don't get split tracking."""
        paras = [f"فقرة رقم {i} " * 100 for i in range(10)]
        units = split_into_units(paras, max_chars=5000)
        for u in units:
            assert u["split_part"] == 0
            assert u["total_splits"] == 0
