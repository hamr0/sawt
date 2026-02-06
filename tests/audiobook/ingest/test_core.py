"""Tests for POC-1: Book Ingestion"""
import os
import csv
from pathlib import Path

import pytest

from src.audiobook.ingest import (
    normalize_arabic, extract_txt, extract_epub, extract_docx, ingest,
    strip_back_matter,
)

BOOKS_DIR = Path("data/books")
TXT_BOOK = BOOKS_DIR / "txt" / "رحلة-ابن-فطومة.txt"
EPUB_BOOK = BOOKS_DIR / "epub" / "tharthara-fawq-al-nil-hindawi.epub"
DOCX_DIR = BOOKS_DIR / "docx"


def _has_presentation_forms(text):
    """Check if text contains any Arabic Presentation Forms characters."""
    for c in text:
        if "\uFE70" <= c <= "\uFEFF" or "\uFB50" <= c <= "\uFE6F":
            return True
    return False


# --- normalize_arabic tests ---

class TestNormalizeArabic:
    # Real Presentation Forms sample from awalad-7aretna.txt
    SAMPLE_PRES_FORMS = (
        "\u0627\uFED3\uFE98\uFE98\uFE8E\uFEA3\uFEF4\uFE94"  # افتتاحية in presentation forms
    )

    def test_removes_all_presentation_forms(self):
        text = self.SAMPLE_PRES_FORMS * 10  # synthetic text with presentation forms
        assert _has_presentation_forms(text)
        cleaned, stats = normalize_arabic(text)
        assert not _has_presentation_forms(cleaned)
        assert stats["presentation_forms_converted"] > 0

    def test_strips_tatweel(self):
        text = "كتـــاب"  # tatweel (U+0640) stretching
        cleaned, stats = normalize_arabic(text)
        assert "\u0640" not in cleaned
        assert stats["tatweel_stripped"] > 0

    def test_collapses_whitespace(self):
        text = "كلمة   كلمة   كلمة"
        cleaned, _ = normalize_arabic(text)
        assert "   " not in cleaned

    def test_preserves_diacritics(self):
        text = "كِتَابٌ"  # kasra, fatha, tanwin
        cleaned, _ = normalize_arabic(text)
        assert cleaned == "كِتَابٌ"

    def test_returns_stats_dict(self):
        _, stats = normalize_arabic("test")
        assert "presentation_forms_converted" in stats
        assert "tatweel_stripped" in stats
        assert "separators_stripped" in stats

    def test_empty_input(self):
        cleaned, stats = normalize_arabic("")
        assert cleaned == ""
        assert stats["presentation_forms_converted"] == 0

    def test_strips_separator_lines(self):
        text = "كلمة\n============\nكلمة أخرى\n•••\n---\nنهاية"
        cleaned, stats = normalize_arabic(text)
        assert "====" not in cleaned
        assert "•••" not in cleaned
        assert "---" not in cleaned
        assert stats["separators_stripped"] == 3
        assert "كلمة" in cleaned
        assert "نهاية" in cleaned

    def test_keeps_dots_ellipsis(self):
        """Dots/periods are never stripped — could be speech ellipsis."""
        text = "وقال... ثم سكت"
        cleaned, _ = normalize_arabic(text)
        assert "..." in cleaned

    def test_keeps_inline_separators(self):
        """Separators mixed with words on the same line stay."""
        text = "– حوار عادي"
        cleaned, _ = normalize_arabic(text)
        assert "–" in cleaned


# --- extract_txt tests ---

class TestExtractTxt:
    def test_reads_utf8_file(self):
        text = extract_txt(str(TXT_BOOK))
        assert len(text) > 1000
        arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
        assert arabic_chars > 500

    def test_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            extract_txt("nonexistent.txt")


# --- extract_epub tests ---

class TestExtractEpub:
    @pytest.mark.skipif(not EPUB_BOOK.exists(), reason="EPUB test book not available")
    def test_extracts_arabic_text(self):
        text = extract_epub(str(EPUB_BOOK))
        assert len(text) > 1000
        arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
        assert arabic_chars > 1000

    @pytest.mark.skipif(not EPUB_BOOK.exists(), reason="EPUB test book not available")
    def test_paragraphs_are_reasonable_size(self):
        text = extract_epub(str(EPUB_BOOK))
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        # No single paragraph should be excessively large (container div bug)
        max_len = max(len(p) for p in paragraphs)
        assert max_len < 10000


# --- extract_docx tests ---

def _first_docx():
    """Return a .docx file in DOCX_DIR that has extractable text, or None."""
    if not DOCX_DIR.exists():
        return None
    from docx import Document
    for f in sorted(DOCX_DIR.glob("*.docx")):
        try:
            doc = Document(str(f))
            if any(p.text.strip() for p in doc.paragraphs):
                return f
        except Exception:
            continue
    return None


class TestExtractDocx:
    @pytest.mark.skipif(_first_docx() is None, reason="No DOCX test files available")
    def test_extracts_text(self):
        docx_file = _first_docx()
        text = extract_docx(str(docx_file))
        assert len(text) > 100

    @pytest.mark.skipif(_first_docx() is None, reason="No DOCX test files available")
    def test_has_arabic_content(self):
        docx_file = _first_docx()
        text = extract_docx(str(docx_file))
        arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
        assert arabic_chars > 50

    def test_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            extract_docx("nonexistent.docx")


# --- ingest orchestrator tests ---

class TestIngest:
    def test_ingest_txt_produces_output_files(self, tmp_path):
        result = ingest(str(TXT_BOOK), output_dir=str(tmp_path))
        book_dir = tmp_path / "txt" / "رحلة-ابن-فطومة" / "01_ingestion"
        assert (book_dir / "clean_text.txt").exists()
        assert (book_dir / "paragraphs.csv").exists()

    def test_ingest_txt_clean_text_has_no_pres_forms(self, tmp_path):
        ingest(str(TXT_BOOK), output_dir=str(tmp_path))
        clean_text = (tmp_path / "txt" / "رحلة-ابن-فطومة" / "01_ingestion" / "clean_text.txt").read_text()
        assert not _has_presentation_forms(clean_text)

    def test_ingest_txt_csv_has_correct_columns(self, tmp_path):
        ingest(str(TXT_BOOK), output_dir=str(tmp_path))
        csv_path = tmp_path / "txt" / "رحلة-ابن-فطومة" / "01_ingestion" / "paragraphs.csv"
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            assert set(reader.fieldnames) == {
                "paragraph_number", "char_count", "word_count", "first_50_chars"
            }
            rows = list(reader)
            assert len(rows) > 0

    def test_ingest_returns_summary_dict(self, tmp_path):
        result = ingest(str(TXT_BOOK), output_dir=str(tmp_path))
        assert "book_slug" in result
        assert "format" in result
        assert "paragraph_count" in result
        assert "total_chars" in result

    def test_ingest_idempotent(self, tmp_path):
        ingest(str(TXT_BOOK), output_dir=str(tmp_path))
        text1 = (tmp_path / "txt" / "رحلة-ابن-فطومة" / "01_ingestion" / "clean_text.txt").read_text()
        ingest(str(TXT_BOOK), output_dir=str(tmp_path))
        text2 = (tmp_path / "txt" / "رحلة-ابن-فطومة" / "01_ingestion" / "clean_text.txt").read_text()
        assert text1 == text2

    @pytest.mark.skipif(not EPUB_BOOK.exists(), reason="EPUB test book not available")
    def test_ingest_epub_produces_output(self, tmp_path):
        result = ingest(str(EPUB_BOOK), output_dir=str(tmp_path))
        book_dir = tmp_path / "epub" / "tharthara-fawq-al-nil-hindawi" / "01_ingestion"
        assert (book_dir / "clean_text.txt").exists()
        assert (book_dir / "paragraphs.csv").exists()
        clean_text = (book_dir / "clean_text.txt").read_text()
        assert not _has_presentation_forms(clean_text)
        assert result["paragraph_count"] > 10
        # Should have substantial Arabic content
        arabic_chars = sum(1 for c in clean_text if "\u0600" <= c <= "\u06FF")
        assert arabic_chars > 1000

    @pytest.mark.skipif(_first_docx() is None, reason="No DOCX test files available")
    def test_ingest_docx_produces_output(self, tmp_path):
        docx_file = _first_docx()
        result = ingest(str(docx_file), output_dir=str(tmp_path))
        book_dir = tmp_path / "docx" / docx_file.stem / "01_ingestion"
        assert (book_dir / "clean_text.txt").exists()
        assert (book_dir / "paragraphs.csv").exists()
        clean_text = (book_dir / "clean_text.txt").read_text()
        assert not _has_presentation_forms(clean_text)
        assert result["paragraph_count"] > 5

    def test_ingest_unsupported_format_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Unsupported"):
            ingest("book.xyz", output_dir=str(tmp_path))

    def test_ingest_summary_includes_back_matter_count(self, tmp_path):
        result = ingest(str(TXT_BOOK), output_dir=str(tmp_path))
        assert "back_matter_removed" in result

    @pytest.mark.skipif(not EPUB_BOOK.exists(), reason="EPUB test book not available")
    def test_ingest_epub_strips_back_matter(self, tmp_path):
        result = ingest(str(EPUB_BOOK), output_dir=str(tmp_path))
        assert result["back_matter_removed"] > 0
        clean_text = (
            tmp_path / "epub" / "tharthara-fawq-al-nil-hindawi" / "01_ingestion" / "clean_text.txt"
        ).read_text()
        assert "الناشر" not in clean_text


# --- strip_back_matter tests ---

class TestStripBackMatter:
    # Realistic Hindawi-style ending
    HINDAWI_BOILERPLATE = [
        "زقاق المدق",
        "نجيب محفوظ",
        "الناشر مؤسسة هنداويالمشهرة برقم ١٠٥٨٥٩٧٠ بتاريخ ٢٦ / ١ / ٢٠١٧",
        "يورك هاوس، شييت ستريت، وندسور، SL4 1DD، المملكة المتحدة",
        "رسم الغلاف: سامح عرفةالترقيم الدولى:٩٧٨ ١ ٥٢٧٣ ٢٧٢٢ ١",
        "زقاق المدق",
        "تأليفنجيب محفوظ",
        "زقاق المدق زقاق المدق",
    ]

    def _make_book(self, extra_tail=None):
        """Build a fake book: 20 content paragraphs + optional tail."""
        content = [f"هذا نص الفقرة رقم {i} من الكتاب وهو طويل بما يكفي لتجاوز حد المائة حرف." * 3 for i in range(20)]
        if extra_tail:
            content.extend(extra_tail)
        return content

    def test_strips_hindawi_boilerplate(self):
        paras = self._make_book(self.HINDAWI_BOILERPLATE)
        cleaned, removed = strip_back_matter(paras)
        assert len(cleaned) == 20
        assert len(removed) == len(self.HINDAWI_BOILERPLATE)

    def test_walks_back_over_short_title_author(self):
        """Title + author lines before الناشر are also stripped."""
        paras = self._make_book(self.HINDAWI_BOILERPLATE)
        cleaned, removed = strip_back_matter(paras)
        # "زقاق المدق" and "نجيب محفوظ" should be in removed
        removed_text = " ".join(removed)
        assert "نجيب محفوظ" in removed_text
        assert "الناشر" in removed_text

    def test_no_markers_returns_unchanged(self):
        paras = self._make_book()
        cleaned, removed = strip_back_matter(paras)
        assert cleaned == paras
        assert removed == []

    def test_short_book_returns_unchanged(self):
        paras = ["فقرة أولى", "فقرة ثانية", "فقرة ثالثة"]
        cleaned, removed = strip_back_matter(paras)
        assert cleaned == paras
        assert removed == []

    def test_walkback_stops_at_long_paragraph(self):
        """Don't walk back into actual content even if near the marker."""
        long_para = "ك" * 200  # 200-char paragraph = real content
        tail = [long_para, "الناشر دار الكتاب العربي", "حقوق النشر محفوظة"]
        paras = self._make_book(tail)
        cleaned, removed = strip_back_matter(paras)
        # Long paragraph should NOT be removed
        assert long_para in cleaned
        assert len(removed) == 2

    def test_walkback_limited_to_three(self):
        """Walk back at most 3 short paragraphs."""
        tail = ["قصيرة ١", "قصيرة ٢", "قصيرة ٣", "قصيرة ٤", "الناشر مؤسسة هنداوي"]
        paras = self._make_book(tail)
        cleaned, removed = strip_back_matter(paras)
        # Should walk back 3 from الناشر, keeping "قصيرة ١"
        assert removed[0] == "قصيرة ٢"
        assert len(removed) == 4

    def test_isbn_marker_triggers_strip(self):
        tail = ["الترقيم الدولى: ٩٧٨ ١ ٥٢٧٣", "حقوق الطبع محفوظة"]
        paras = self._make_book(tail)
        cleaned, removed = strip_back_matter(paras)
        assert len(removed) == 2

    def test_copyright_marker_triggers_strip(self):
        tail = ["حقوق الطبع والنشر محفوظة", "جميع الحقوق محفوظة"]
        paras = self._make_book(tail)
        cleaned, removed = strip_back_matter(paras)
        assert len(removed) == 2
