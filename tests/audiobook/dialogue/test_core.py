"""Tests for POC-3 Phase A: Two-Voice Dialogue Detection"""
import csv
from pathlib import Path

import pytest

from src.audiobook.dialogue import (
    CSV_COLUMNS,
    EM_DASH_CHARS,
    REVIEW_OPEN,
    REVIEW_CLOSE,
    detect_markers,
    segment_paragraphs,
    segment_chapter,
    segment_book,
    parse_review_text,
    sync_review,
    _find_dialogue_colon,
    _split_at_colon,
    _split_at_review_markers,
    _segments_to_review_text,
    _has_speech_attribution,
    _has_trailing_speech,
)


# ---------------------------------------------------------------------------
# _find_dialogue_colon
# ---------------------------------------------------------------------------

class TestFindDialogueColon:
    def test_simple_colon(self):
        assert _find_dialogue_colon("فقال: هذا كلام") is not None

    def test_no_colon(self):
        assert _find_dialogue_colon("لا يوجد نقطتان هنا") is None

    def test_time_colon_skipped(self):
        assert _find_dialogue_colon("الساعة ١٢:٣٠ مساء") is None

    def test_time_colon_western_skipped(self):
        assert _find_dialogue_colon("at 12:30 pm") is None

    def test_url_colon_skipped(self):
        assert _find_dialogue_colon("الموقع http://example.com جيد") is None

    def test_colon_at_end_skipped(self):
        """Colon with nothing after it is heading-style, not dialogue."""
        assert _find_dialogue_colon("عنوان:") is None

    def test_colon_with_only_whitespace_after(self):
        assert _find_dialogue_colon("عنوان:   ") is None

    def test_colon_at_start_skipped(self):
        """Colon with nothing before it."""
        assert _find_dialogue_colon(": بعد") is None

    def test_returns_first_valid_colon_index(self):
        text = "قال في كآبة: هذا في الحلم"
        idx = _find_dialogue_colon(text)
        assert text[idx] == ":"
        assert "كآبة" in text[:idx]

    def test_time_then_dialogue_colon(self):
        """Time colon skipped, dialogue colon found."""
        text = "في ١٢:٣٠ قال: مرحبا"
        idx = _find_dialogue_colon(text)
        assert idx is not None
        assert text[idx + 1:].strip() == "مرحبا"


# ---------------------------------------------------------------------------
# detect_markers
# ---------------------------------------------------------------------------

class TestDetectMarkers:
    def test_empty(self):
        assert detect_markers("") == "plain"
        assert detect_markers("   ") == "plain"

    def test_em_dash_en(self):
        assert detect_markers("– صدِّقيني أنا سعيد بكِ") == "em_dash"

    def test_em_dash_long(self):
        assert detect_markers("— قال لي") == "em_dash"

    def test_em_dash_hyphen(self):
        assert detect_markers("- لزوم العمل") == "em_dash"

    def test_em_dash_needs_space(self):
        """Dash without space after is not em-dash marker."""
        assert detect_markers("–مرحبا") == "plain"

    def test_colon(self):
        assert detect_markers("فقال في كآبة: هذا في الحلم") == "colon"

    def test_colon_with_attribution(self):
        assert detect_markers("وهي تقول: حلمتُ أنك بعيد") == "colon"

    def test_guillemet_is_plain(self):
        """Guillemets are typographic quotation marks, not dialogue markers."""
        assert detect_markers("نظرت إلى المرآة «لا بأس، جميل»") == "plain"

    def test_guillemet_only_open_is_plain(self):
        assert detect_markers("قال «مرحبا ولكن") == "plain"

    def test_plain(self):
        assert detect_markers("ذهبت إلى البيت وجلست على الكنبة") == "plain"

    def test_colon_with_guillemet_still_colon(self):
        """Colon with guillemets — colon detected, guillemets are just text."""
        text = "قالت: «لا بأس»"
        assert detect_markers(text) == "colon"

    def test_em_dash_takes_priority_over_colon(self):
        """Em dash at start takes priority over colon in body."""
        text = "– قال: نعم"
        assert detect_markers(text) == "em_dash"

    def test_time_colon_not_dialogue(self):
        assert detect_markers("وصلت الساعة ١٢:٣٠") == "plain"

    def test_heading_colon_not_dialogue(self):
        assert detect_markers("الفصل الأول:") == "plain"

    def test_trailing_colon_with_speech_verb(self):
        assert detect_markers("فهتف وهو يرفع رأسه إلى سقف القهوة:") == "trailing_colon"

    def test_trailing_colon_with_qala(self):
        assert detect_markers("وقال وعيناه لا تزالان شاخِصتَين إلى السقف:") == "trailing_colon"

    def test_trailing_colon_without_speech_verb(self):
        """Trailing colon without speech verb is plain (label/heading)."""
        assert detect_markers("عنوان:") == "plain"

    def test_trailing_colon_heading_style(self):
        assert detect_markers("الفصل الأول:") == "plain"


# ---------------------------------------------------------------------------
# _has_speech_attribution
# ---------------------------------------------------------------------------

class TestHasSpeechAttribution:
    def test_short_text_always_true(self):
        """Short text before colon is assumed to be dialogue attribution."""
        assert _has_speech_attribution("فقال")
        assert _has_speech_attribution("في كآبة")

    def test_long_text_with_speech_verb(self):
        text = "أ" * 200 + " قال حسين كرشة عنها"
        assert _has_speech_attribution(text)

    def test_long_text_without_speech_verb(self):
        text = "أ" * 200 + " وقيل في تفسير هذا"
        assert not _has_speech_attribution(text)

    def test_passive_qila_not_matched(self):
        """قيل (passive 'was said') should NOT match — it's indirect speech."""
        text = "أ" * 200 + " وقيل في تفسير هذا"
        assert not _has_speech_attribution(text)

    def test_present_tense_matched(self):
        text = "أ" * 200 + " وهي تقول"
        assert _has_speech_attribution(text)

    def test_participle_matched(self):
        text = "أ" * 200 + " واستدرك قائلا"
        assert _has_speech_attribution(text)


# ---------------------------------------------------------------------------
# _split_at_colon
# ---------------------------------------------------------------------------

class TestSplitAtColon:
    def test_simple_split(self):
        before, after = _split_at_colon("قال: مرحبا")
        assert before == "قال"
        assert after == "مرحبا"

    def test_no_colon(self):
        before, after = _split_at_colon("لا يوجد نقطتان")
        assert before == "لا يوجد نقطتان"
        assert after == ""

    def test_preserves_full_text(self):
        text = "فقال في كآبة: هذا في الحلم أما في الحقيقة فأنتِ"
        before, after = _split_at_colon(text)
        assert before == "فقال في كآبة"
        assert after == "هذا في الحلم أما في الحقيقة فأنتِ"


# ---------------------------------------------------------------------------
# segment_paragraphs — state machine
# ---------------------------------------------------------------------------

class TestSegmentParagraphs:
    def test_pure_narrator(self):
        """No dialogue markers → all narrator."""
        paragraphs = [
            "ذهب إلى البيت",
            "جلس على الكنبة",
            "نظر من النافذة",
        ]
        segments = segment_paragraphs(paragraphs)
        assert all(s["type"] == "narrator" for s in segments)
        assert len(segments) == 3

    def test_single_colon(self):
        """Colon paragraph → narrator + dialogue segments."""
        paragraphs = ["فقال: مرحبا يا صديقي"]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 2
        assert segments[0]["type"] == "narrator"
        assert segments[0]["text"] == "فقال"
        assert segments[1]["type"] == "dialogue"
        assert segments[1]["text"] == "مرحبا يا صديقي"

    def test_em_dash_line(self):
        """Em-dash paragraph → dialogue."""
        paragraphs = ["– صدِّقيني أنا سعيد"]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 1
        assert segments[0]["type"] == "dialogue"
        assert segments[0]["text"] == "صدِّقيني أنا سعيد"

    def test_em_dash_strips_dash(self):
        """Verify em-dash characters are stripped from output."""
        paragraphs = ["— نعم بالطبع"]
        segments = segment_paragraphs(paragraphs)
        assert segments[0]["text"] == "نعم بالطبع"
        assert "—" not in segments[0]["text"]

    def test_colon_then_plain_resets_to_narrator(self):
        """Colon → new paragraph resets to narrator (no continuation)."""
        paragraphs = [
            "فقال: مرحبا",
            "كيف حالك؟",
        ]
        segments = segment_paragraphs(paragraphs)
        assert segments[0]["type"] == "narrator"   # "فقال"
        assert segments[1]["type"] == "dialogue"    # "مرحبا"
        assert segments[2]["type"] == "narrator"    # "كيف حالك؟" (new paragraph = narrator)

    def test_colon_then_long_paragraph_is_narrator(self):
        """Any plain paragraph after dialogue → narrator (regardless of length)."""
        long_narration = "أ" * 250
        paragraphs = [
            "فقال: مرحبا",
            long_narration,
        ]
        segments = segment_paragraphs(paragraphs)
        assert segments[0]["type"] == "narrator"   # "فقال"
        assert segments[1]["type"] == "dialogue"    # "مرحبا"
        assert segments[2]["type"] == "narrator"    # long narration

    def test_em_dash_sequence(self):
        """Multiple em-dash lines → all dialogue."""
        paragraphs = [
            "– حقًّا؟",
            "– نعم بالطبع",
            "– لا أصدق",
        ]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 3
        assert all(s["type"] == "dialogue" for s in segments)

    def test_colon_then_new_colon(self):
        """New colon paragraph starts new narrator+dialogue pair."""
        paragraphs = [
            "قال: مرحبا",
            "أجابت: أهلا",
        ]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 4
        assert segments[0]["type"] == "narrator"   # "قال"
        assert segments[1]["type"] == "dialogue"    # "مرحبا"
        assert segments[2]["type"] == "narrator"    # "أجابت"
        assert segments[3]["type"] == "dialogue"    # "أهلا"

    def test_narrator_then_em_dash_then_narrator(self):
        """Narrator → em-dash dialogue → narrator."""
        long_narration = "أ" * 250
        paragraphs = [
            "جلس في المقعد",
            "– كيف الحال؟",
            long_narration,
        ]
        segments = segment_paragraphs(paragraphs)
        assert segments[0]["type"] == "narrator"
        assert segments[1]["type"] == "dialogue"
        assert segments[2]["type"] == "narrator"

    def test_empty_paragraphs_skipped(self):
        paragraphs = ["", "   ", "نص عادي", ""]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 1
        assert segments[0]["text"] == "نص عادي"

    def test_segment_numbering(self):
        paragraphs = ["نص أول", "قال: مرحبا", "– نعم"]
        segments = segment_paragraphs(paragraphs)
        numbers = [s["segment_number"] for s in segments]
        assert numbers == list(range(1, len(segments) + 1))

    def test_char_count_accurate(self):
        paragraphs = ["فقال: مرحبا يا صديقي"]
        segments = segment_paragraphs(paragraphs)
        for seg in segments:
            assert seg["char_count"] == len(seg["text"])

    def test_colon_heading_style_stays_narrator(self):
        """Colon at end with nothing after → narrator (heading-style)."""
        paragraphs = ["الفصل الأول:"]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 1
        assert segments[0]["type"] == "narrator"

    def test_time_colon_stays_narrator(self):
        """Time-format colon is not dialogue."""
        paragraphs = ["وصل الساعة ١٢:٣٠ مساء"]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 1
        assert segments[0]["type"] == "narrator"

    def test_speech_verb_no_longer_continues_dialogue(self):
        """Plain paragraph with speech verb is narrator (no continuation)."""
        long_with_verb = "أ" * 100 + " قال " + "أ" * 120
        paragraphs = [
            "قال: مرحبا",
            long_with_verb,
        ]
        segments = segment_paragraphs(paragraphs)
        assert segments[-1]["type"] == "narrator"

    def test_guillemet_paragraph_is_narrator(self):
        """Guillemet paragraph is plain narrator — no voice splitting."""
        text = "«لا بأس، جميل، وأيم الله جميل»"
        paragraphs = [text]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 1
        assert segments[0]["type"] == "narrator"
        assert "«" in segments[0]["text"]  # guillemets preserved as text

    def test_guillemet_in_narration_stays_narrator(self):
        """Guillemets embedded in narration — whole paragraph is narrator."""
        text = "أ" * 200 + " «نعم» " + "أ" * 200
        paragraphs = [text]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 1
        assert segments[0]["type"] == "narrator"
        assert "«نعم»" in segments[0]["text"]

    def test_colon_with_guillemet_after(self):
        """Colon before guillemet — colon splits, guillemets stay in dialogue text."""
        text = "قالت: «لا بأس، جميل»"
        paragraphs = [text]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 2
        assert segments[0]["type"] == "narrator"
        assert segments[0]["text"] == "قالت"
        assert segments[1]["type"] == "dialogue"
        assert segments[1]["text"] == "«لا بأس، جميل»"

    def test_colon_with_multiple_guillemets(self):
        """Colon wins over guillemets — entire post-colon text is dialogue."""
        text = "وتساءل: «لماذا؟» وأغمض عينيه ثم قال لنفسه: «قُضي عليَّ.»"
        paragraphs = [text]
        segments = segment_paragraphs(paragraphs)
        types = [s["type"] for s in segments]
        # Colon splits: narrator + dialogue (paragraph = unit)
        assert types == ["narrator", "dialogue"]
        assert segments[0]["text"] == "وتساءل"
        assert "«لماذا؟»" in segments[1]["text"]
        assert "«قُضي عليَّ.»" in segments[1]["text"]

    def test_guillemet_stream_of_consciousness_is_narrator(self):
        """Inner thoughts in «» are narrator — no voice switching for inner monologue."""
        text = (
            "وعاود الشابَّ إحساسُه بالغرابة، "
            + "أ" * 200
            + " «لماذا أضطربُ هكذا؟ ألم أقتنع؟» "
            + "وذكَر بغتةً أمَّه "
            + "أ" * 100
            + " «لماذا هذا كلُّه؟!»"
        )
        paragraphs = [text]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 1
        assert segments[0]["type"] == "narrator"
        assert "«لماذا أضطربُ" in segments[0]["text"]
        assert "«لماذا هذا كلُّه" in segments[0]["text"]

    def test_text_preservation(self):
        """All input chars appear in output (minus colon from splits, dashes stripped)."""
        paragraphs = [
            "نص أول",
            "فقال: مرحبا",
            "– نعم",
            "نص أخير طويل جدا " + "أ" * 250,
        ]
        segments = segment_paragraphs(paragraphs)
        output_text = "".join(s["text"] for s in segments)
        # Build expected: all paragraphs with colons removed at split point,
        # dashes stripped from em-dash lines
        for para in paragraphs:
            stripped = para.strip()
            if not stripped:
                continue
            # For colon paragraphs: both sides present
            if ":" in stripped:
                before_colon = stripped.split(":")[0].strip()
                after_colon = ":".join(stripped.split(":")[1:]).strip()
                assert before_colon in output_text or before_colon == ""
                assert after_colon in output_text or after_colon == ""
            elif stripped[0] in EM_DASH_CHARS:
                # Dash stripped, rest present
                content = stripped.lstrip(EM_DASH_CHARS).strip()
                assert content in output_text
            else:
                assert stripped in output_text

    def test_mixed_real_dialogue(self):
        """Real-world pattern: narration → colon dialogue → em-dash exchanges → narration."""
        long_narration = "وكان يقف عند الباب ينظر " + "أ" * 200
        paragraphs = [
            long_narration,
            "وهي تقول: حلمتُ أنك بعيد",
            "فقال في كآبة: هذا في الحلم",
            "– لزوم العمل",
            "– حقًّا؟",
            "– نعم",
            "وكانت ثمة فراشة تعانق المصباح " + "أ" * 200,
        ]
        segments = segment_paragraphs(paragraphs)

        types = [s["type"] for s in segments]
        # First is narrator (long)
        assert types[0] == "narrator"
        # Colon splits produce narrator + dialogue pairs
        assert types[1] == "narrator"   # "وهي تقول"
        assert types[2] == "dialogue"   # "حلمتُ أنك بعيد"
        assert types[3] == "narrator"   # "فقال في كآبة"
        assert types[4] == "dialogue"   # "هذا في الحلم"
        # Em-dashes are dialogue
        assert types[5] == "dialogue"   # "لزوم العمل"
        assert types[6] == "dialogue"   # "حقًّا؟"
        assert types[7] == "dialogue"   # "نعم"
        # Final long paragraph back to narrator
        assert types[8] == "narrator"

    def test_trailing_colon_triggers_dialogue(self):
        """Trailing colon → narrator, next paragraph → dialogue."""
        paragraphs = [
            "فهتف وهو يرفع رأسه إلى سقف القهوة:",
            "أين أنت يا صديقي؟",
        ]
        segments = segment_paragraphs(paragraphs)
        assert segments[0]["type"] == "narrator"
        assert ":" not in segments[0]["text"]  # colon stripped
        assert segments[1]["type"] == "dialogue"

    def test_trailing_colon_strips_colon(self):
        paragraphs = ["وقال وعيناه شاخصتان إلى السقف:"]
        segments = segment_paragraphs(paragraphs)
        assert segments[0]["type"] == "narrator"
        assert not segments[0]["text"].endswith(":")

    def test_trailing_colon_then_narrator_resumes(self):
        """Trailing colon → dialogue (one-shot) → narrator."""
        long_narration = "أ" * 250
        paragraphs = [
            "فهتف قائلا:",
            "أين الحقيقة؟",
            long_narration,
        ]
        segments = segment_paragraphs(paragraphs)
        assert segments[0]["type"] == "narrator"
        assert segments[1]["type"] == "dialogue"
        assert segments[2]["type"] == "narrator"

    def test_explanatory_colon_stays_narrator(self):
        """Long paragraph with passive قيل before colon → not dialogue."""
        text = "أ" * 200 + " وقيل في تفسير هذا: إن الرجل آثر العمل على الراحة"
        paragraphs = [text]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 1
        assert segments[0]["type"] == "narrator"

    def test_long_monologue_stays_dialogue(self):
        """Entire text after attribution colon is dialogue — paragraph = unit."""
        long_speech = "لا أنكر أن الحج أمنية. " + "أ" * 300 + " وقلت لنفسي: ماذا فعلت؟"
        text = "ثم قال يجيب نظرات الاستطلاع: " + long_speech
        paragraphs = [text]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 2
        assert segments[0]["type"] == "narrator"
        assert segments[1]["type"] == "dialogue"
        # Entire post-colon text is one dialogue segment (no sentence split)
        assert "لا أنكر" in segments[1]["text"]
        assert "ماذا فعلت" in segments[1]["text"]

    def test_nested_colons_within_monologue(self):
        """Nested colons (quotes/self-talk within speech) stay as dialogue."""
        text = "وراح يقول: أحب الحياة، ولذلك أقول لكم: إن حب الحياة نصف العبادة"
        paragraphs = [text]
        segments = segment_paragraphs(paragraphs)
        # First colon splits: narrator + dialogue (entire rest including nested colon)
        assert segments[0]["type"] == "narrator"
        assert segments[1]["type"] == "dialogue"
        assert "أقول لكم" in segments[1]["text"]

    def test_first_person_verb_no_longer_continues_dialogue(self):
        """First-person قلت in a plain paragraph is narrator (no continuation)."""
        long_with_qultu = "أ" * 100 + " وقلت لنفسي " + "أ" * 120
        paragraphs = [
            "قال: مرحبا",
            long_with_qultu,
        ]
        segments = segment_paragraphs(paragraphs)
        assert segments[-1]["type"] == "narrator"

    def test_colon_whole_paragraph_is_dialogue(self):
        """After colon with speech attribution, everything to end of paragraph is dialogue."""
        paragraphs = ["قال حسين عنها: إنها كفلقة القمر. " + "أ" * 200]
        segments = segment_paragraphs(paragraphs)
        assert len(segments) == 2
        assert segments[0]["type"] == "narrator"
        assert segments[1]["type"] == "dialogue"
        # All post-colon text in one segment
        assert "إنها كفلقة القمر" in segments[1]["text"]
        assert len(segments[1]["text"]) > 200

    def test_zuqaq_passage(self):
        """Zuqaq passage: explanatory colon, dialogue colon, trailing colons."""
        paragraphs = [
            "أ" * 200 + " وقيل في تفسير هذا: إن عم كامل آثر إشراك الدكتور في مسكنه",
            "قال حسين كرشة عنها: إنها كفلقة القمر. " + "أ" * 200,
            "فهتف وهو يرفع رأسه إلى سقف القهوة:",
            "فتجهَّم وجه عم كامل وقال وعيناه شاخصتان إلى السقف:",
            "ثمَّ واستدرك قائلا: يا ست الستات يا قاضية الحاجات",
        ]
        segments = segment_paragraphs(paragraphs)
        types = [s["type"] for s in segments]

        # P1: explanatory colon (قيل passive) → all narrator
        assert types[0] == "narrator"
        # P2: dialogue colon → N + D (entire post-colon is dialogue)
        assert types[1] == "narrator"
        assert types[2] == "dialogue"
        # P3: trailing colon with هتف → narrator, sets IN_DIALOGUE
        assert types[3] == "narrator"
        # P4: trailing colon with قال → narrator, stays IN_DIALOGUE
        assert types[4] == "narrator"
        # P5: colon with قائلا → N + D
        assert types[5] == "narrator"
        assert types[6] == "dialogue"


# ---------------------------------------------------------------------------
# _segments_to_review_text
# ---------------------------------------------------------------------------

class TestSegmentsToReviewText:
    def test_dialogue_wrapped(self):
        segments = [
            {"type": "narrator", "text": "نص عادي"},
            {"type": "dialogue", "text": "مرحبا"},
        ]
        result = _segments_to_review_text(segments)
        assert result == "نص عادي\n\n// مرحبا \\\\"

    def test_narrator_not_wrapped(self):
        segments = [{"type": "narrator", "text": "نص عادي"}]
        result = _segments_to_review_text(segments)
        assert "//" not in result
        assert result == "نص عادي"

    def test_alternating(self):
        segments = [
            {"type": "narrator", "text": "قال"},
            {"type": "dialogue", "text": "مرحبا"},
            {"type": "narrator", "text": "ثم أضاف"},
            {"type": "dialogue", "text": "وداعا"},
        ]
        result = _segments_to_review_text(segments)
        parts = result.split("\n\n")
        assert parts == ["قال", "// مرحبا \\\\", "ثم أضاف", "// وداعا \\\\"]

    def test_empty_segments(self):
        assert _segments_to_review_text([]) == ""

    def test_guillemets_in_text_preserved(self):
        """Original «» from source text pass through without collision."""
        segments = [
            {"type": "dialogue", "text": "«لا بأس، جميل»"},
        ]
        result = _segments_to_review_text(segments)
        assert result == "// «لا بأس، جميل» \\\\"


# ---------------------------------------------------------------------------
# parse_review_text
# ---------------------------------------------------------------------------

class TestParseReviewText:
    def test_dialogue_unwrapped(self):
        text = "نص عادي\n\n// مرحبا \\\\"
        segments = parse_review_text(text)
        assert len(segments) == 2
        assert segments[0] == {"segment_number": 1, "type": "narrator", "char_count": 7, "text": "نص عادي"}
        assert segments[1] == {"segment_number": 2, "type": "dialogue", "char_count": 5, "text": "مرحبا"}

    def test_pure_narrator(self):
        text = "فقرة أولى\n\nفقرة ثانية"
        segments = parse_review_text(text)
        assert all(s["type"] == "narrator" for s in segments)
        assert len(segments) == 2

    def test_inline_markers_in_paragraph(self):
        """Inline // \\\\ within a paragraph produce multiple segments."""
        text = "قالت: // لا بأس \\\\ وابتسمت"
        segments = parse_review_text(text)
        assert len(segments) == 3
        assert segments[0]["type"] == "narrator"
        assert segments[1]["type"] == "dialogue"
        assert segments[1]["text"] == "لا بأس"
        assert segments[2]["type"] == "narrator"

    def test_roundtrip(self):
        """segments → review text → parse back → same types and texts."""
        original = [
            {"segment_number": 1, "type": "narrator", "char_count": 3, "text": "قال"},
            {"segment_number": 2, "type": "dialogue", "char_count": 5, "text": "مرحبا"},
            {"segment_number": 3, "type": "narrator", "char_count": 7, "text": "ثم أضاف"},
            {"segment_number": 4, "type": "dialogue", "char_count": 5, "text": "وداعا"},
        ]
        review = _segments_to_review_text(original)
        parsed = parse_review_text(review)
        assert len(parsed) == len(original)
        for orig, back in zip(original, parsed):
            assert orig["type"] == back["type"]
            assert orig["text"] == back["text"]

    def test_guillemets_in_text_survive_roundtrip(self):
        """Original «» from source text survive the roundtrip unchanged."""
        original = [
            {"segment_number": 1, "type": "dialogue", "char_count": 14, "text": "«لا بأس، جميل»"},
        ]
        review = _segments_to_review_text(original)
        parsed = parse_review_text(review)
        assert parsed[0]["text"] == "«لا بأس، جميل»"

    def test_empty_text(self):
        assert parse_review_text("") == []
        assert parse_review_text("   \n\n   ") == []


# ---------------------------------------------------------------------------
# sync_review
# ---------------------------------------------------------------------------

class TestSyncReview:
    def test_sync_generates_csvs(self, tmp_path):
        """Sync reads review texts and writes matching CSVs."""
        segments_dir = tmp_path / "segments"
        review_dir = segments_dir / "review"
        review_dir.mkdir(parents=True)

        review_dir.joinpath("chapter_01.txt").write_text(
            "نص عادي\n\n// مرحبا \\\\", encoding="utf-8"
        )
        review_dir.joinpath("chapter_02.txt").write_text(
            "// وداعا \\\\\n\nنص آخر", encoding="utf-8"
        )

        count = sync_review(str(segments_dir))
        assert count == 2

        ssml_dir = segments_dir / "ssml"
        assert (ssml_dir / "chapter_01.csv").exists()
        assert (ssml_dir / "chapter_02.csv").exists()

        # Verify CSV content
        with open(ssml_dir / "chapter_01.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2
        assert rows[0]["type"] == "narrator"
        assert rows[1]["type"] == "dialogue"
        assert rows[1]["text"] == "مرحبا"

    def test_sync_overwrites_stale_csv(self, tmp_path):
        """Sync overwrites existing CSV with corrected content."""
        segments_dir = tmp_path / "segments"
        review_dir = segments_dir / "review"
        ssml_dir = segments_dir / "ssml"
        review_dir.mkdir(parents=True)
        ssml_dir.mkdir(parents=True)

        # Old CSV has wrong classification
        ssml_dir.joinpath("chapter_01.csv").write_text("old,stale,data", encoding="utf-8")

        # Corrected review text
        review_dir.joinpath("chapter_01.txt").write_text(
            "// هذا حوار الآن \\\\", encoding="utf-8"
        )

        sync_review(str(segments_dir))

        with open(ssml_dir / "chapter_01.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        assert rows[0]["type"] == "dialogue"

    def test_sync_no_review_dir(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            sync_review(str(tmp_path / "nonexistent"))


# ---------------------------------------------------------------------------
# segment_chapter — file I/O
# ---------------------------------------------------------------------------

class TestSegmentChapter:
    def test_roundtrip(self, tmp_path):
        """Write a chapter file, segment it, verify CSV and review output."""
        chapters_dir = tmp_path / "book" / "chapters"
        chapters_dir.mkdir(parents=True)
        ch_file = chapters_dir / "chapter_01.txt"
        ch_file.write_text(
            "نص عادي طويل\n\nقال: مرحبا\n\n– نعم\n\nنص أخير طويل " + "أ" * 250,
            encoding="utf-8",
        )

        segments_dir = tmp_path / "book" / "segments"
        summary = segment_chapter(str(ch_file), str(segments_dir))

        assert summary["total_segments"] > 0
        assert summary["narrator_segments"] > 0
        assert summary["dialogue_segments"] > 0
        assert 0.0 < summary["dialogue_ratio"] < 1.0

        # Verify CSV was written to ssml/
        csv_path = segments_dir / "ssml" / "chapter_01.csv"
        assert csv_path.exists()

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == summary["total_segments"]
        assert set(reader.fieldnames) == set(CSV_COLUMNS)

        # Verify review text was written to review/
        review_path = segments_dir / "review" / "chapter_01.txt"
        assert review_path.exists()
        review_text = review_path.read_text(encoding="utf-8")
        assert "// مرحبا \\\\" in review_text
        assert "// نعم \\\\" in review_text

    def test_default_output_dir(self, tmp_path):
        """Without output_dir, segments go to sibling segments/ dir."""
        chapters_dir = tmp_path / "book" / "chapters"
        chapters_dir.mkdir(parents=True)
        ch_file = chapters_dir / "chapter_01.txt"
        ch_file.write_text("نص عادي\n\nقال: مرحبا", encoding="utf-8")

        summary = segment_chapter(str(ch_file))

        expected_dir = tmp_path / "book" / "03_segments"
        assert expected_dir.exists()
        assert (expected_dir / "ssml" / "chapter_01.csv").exists()
        assert (expected_dir / "review" / "chapter_01.txt").exists()

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            segment_chapter("/nonexistent/chapter_01.txt")

    def test_empty_chapter(self, tmp_path):
        """Empty chapter file → no segments."""
        chapters_dir = tmp_path / "book" / "chapters"
        chapters_dir.mkdir(parents=True)
        ch_file = chapters_dir / "chapter_01.txt"
        ch_file.write_text("", encoding="utf-8")

        segments_dir = tmp_path / "book" / "segments"
        summary = segment_chapter(str(ch_file), str(segments_dir))

        assert summary["total_segments"] == 0
        assert summary["total_chars"] == 0
        assert summary["dialogue_ratio"] == 0.0


# ---------------------------------------------------------------------------
# segment_book — multi-chapter orchestration
# ---------------------------------------------------------------------------

class TestSegmentBook:
    def test_multi_chapter(self, tmp_path):
        """Process multiple chapters, verify per-chapter stats."""
        chapters_dir = tmp_path / "book" / "chapters"
        chapters_dir.mkdir(parents=True)

        for i in range(1, 4):
            ch_file = chapters_dir / f"chapter_{i:02d}.txt"
            ch_file.write_text(
                f"الفصل {i}\n\nنص عادي طويل " + "أ" * 100 + f"\n\nقال: مرحبا {i}\n\n– نعم {i}",
                encoding="utf-8",
            )

        segments_dir = tmp_path / "book" / "segments"
        summary = segment_book(str(chapters_dir), str(segments_dir))

        assert summary["total_chapters"] == 3
        assert summary["total_segments"] > 0
        assert len(summary["chapters"]) == 3
        assert 0.0 < summary["dialogue_ratio"] < 1.0

        # Verify CSV and review files exist
        for i in range(1, 4):
            assert (segments_dir / "ssml" / f"chapter_{i:02d}.csv").exists()
            assert (segments_dir / "review" / f"chapter_{i:02d}.txt").exists()

    def test_default_output_dir(self, tmp_path):
        chapters_dir = tmp_path / "book" / "chapters"
        chapters_dir.mkdir(parents=True)
        (chapters_dir / "chapter_01.txt").write_text(
            "نص عادي\n\nقال: مرحبا", encoding="utf-8"
        )

        summary = segment_book(str(chapters_dir))

        expected_dir = tmp_path / "book" / "03_segments"
        assert expected_dir.exists()

    def test_clears_stale_files(self, tmp_path):
        """Previous CSVs and review files are cleared before writing new ones."""
        chapters_dir = tmp_path / "book" / "chapters"
        chapters_dir.mkdir(parents=True)
        (chapters_dir / "chapter_01.txt").write_text("نص عادي", encoding="utf-8")

        segments_dir = tmp_path / "book" / "segments"
        ssml_dir = segments_dir / "ssml"
        review_dir = segments_dir / "review"
        ssml_dir.mkdir(parents=True)
        review_dir.mkdir(parents=True)
        stale_csv = ssml_dir / "chapter_99.csv"
        stale_csv.write_text("old data", encoding="utf-8")
        stale_txt = review_dir / "chapter_99.txt"
        stale_txt.write_text("old data", encoding="utf-8")

        segment_book(str(chapters_dir), str(segments_dir))

        assert not stale_csv.exists()
        assert not stale_txt.exists()

    def test_dir_not_found(self):
        with pytest.raises(FileNotFoundError):
            segment_book("/nonexistent/chapters/")

    def test_no_chapter_files(self, tmp_path):
        empty_dir = tmp_path / "book" / "chapters"
        empty_dir.mkdir(parents=True)
        with pytest.raises(FileNotFoundError):
            segment_book(str(empty_dir))


# ---------------------------------------------------------------------------
# Integration tests — real EPUB data
# ---------------------------------------------------------------------------

# Paths to real chapter files from POC-2 output
AL_LISS_CH02 = Path("output/epub/al-liss-wal-kilab/02_chapters/chapter_02.txt")
ZUQAQ_CH02 = Path("output/epub/zuqaq-al-midaqq/02_chapters/chapter_02.txt")
THARTHARA_CH02 = Path("output/epub/tharthara-fawq-al-nil-hindawi/02_chapters/chapter_02.txt")


@pytest.mark.corpus
@pytest.mark.skipif(not AL_LISS_CH02.exists(), reason="Real EPUB data not available")
class TestIntegrationAlLiss:
    def test_segments_produced(self, tmp_path):
        summary = segment_chapter(str(AL_LISS_CH02), str(tmp_path))
        assert summary["total_segments"] > 5
        assert summary["narrator_segments"] > 0
        assert summary["dialogue_segments"] > 0

    def test_dialogue_ratio_reasonable(self, tmp_path):
        """Mahfouz novels are ~30-50% dialogue."""
        summary = segment_chapter(str(AL_LISS_CH02), str(tmp_path))
        assert 0.10 < summary["dialogue_ratio"] < 0.80

    def test_text_preservation(self, tmp_path):
        """Total chars in segments ≈ input chars (minus colons/dashes at splits)."""
        text = AL_LISS_CH02.read_text(encoding="utf-8")
        input_chars = sum(len(p.strip()) for p in text.split("\n\n") if p.strip())

        summary = segment_chapter(str(AL_LISS_CH02), str(tmp_path))
        output_chars = summary["total_chars"]

        # Output should be close to input — we strip colons and dashes,
        # but those are few chars relative to total
        ratio = output_chars / input_chars if input_chars > 0 else 0
        assert 0.95 < ratio < 1.05

    def test_csv_readable(self, tmp_path):
        segment_chapter(str(AL_LISS_CH02), str(tmp_path))
        csv_path = tmp_path / "ssml" / "chapter_02.csv"
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) > 0
        assert all(row["type"] in ("narrator", "dialogue") for row in rows)

    def test_review_text_readable(self, tmp_path):
        segment_chapter(str(AL_LISS_CH02), str(tmp_path))
        review_path = tmp_path / "review" / "chapter_02.txt"
        assert review_path.exists()
        text = review_path.read_text(encoding="utf-8")
        # Dialogue should be wrapped in // \\
        assert "//" in text
        assert "\\\\" in text


@pytest.mark.corpus
@pytest.mark.skipif(not ZUQAQ_CH02.exists(), reason="Real EPUB data not available")
class TestIntegrationZuqaq:
    def test_segments_produced(self, tmp_path):
        summary = segment_chapter(str(ZUQAQ_CH02), str(tmp_path))
        assert summary["total_segments"] > 5

    def test_dialogue_ratio_reasonable(self, tmp_path):
        summary = segment_chapter(str(ZUQAQ_CH02), str(tmp_path))
        assert 0.10 < summary["dialogue_ratio"] < 0.80

    def test_guillemets_preserved_in_text(self, tmp_path):
        """Guillemets pass through as text — not used for voice splitting."""
        text = ZUQAQ_CH02.read_text(encoding="utf-8")
        if "«" not in text:
            pytest.skip("No guillemets in this chapter")

        segment_chapter(str(ZUQAQ_CH02), str(tmp_path))
        csv_path = tmp_path / "ssml" / "chapter_02.csv"
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        # Guillemets should appear in segment text (preserved, not stripped)
        all_text = " ".join(r["text"] for r in rows)
        assert "«" in all_text


@pytest.mark.corpus
@pytest.mark.skipif(not THARTHARA_CH02.exists(), reason="Real EPUB data not available")
class TestIntegrationTharthara:
    def test_segments_produced(self, tmp_path):
        summary = segment_chapter(str(THARTHARA_CH02), str(tmp_path))
        assert summary["total_segments"] > 3

    def test_em_dash_dialogue(self, tmp_path):
        """Tharthara has short em-dash exchanges."""
        text = THARTHARA_CH02.read_text(encoding="utf-8")
        has_dashes = any(
            line.strip().startswith(("–", "—", "-"))
            for line in text.split("\n")
            if line.strip()
        )
        if not has_dashes:
            pytest.skip("No em-dash dialogue in this chapter")

        summary = segment_chapter(str(THARTHARA_CH02), str(tmp_path))
        assert summary["dialogue_segments"] > 0

    def test_dialogue_ratio_reasonable(self, tmp_path):
        summary = segment_chapter(str(THARTHARA_CH02), str(tmp_path))
        assert 0.10 < summary["dialogue_ratio"] < 0.80


# ---------------------------------------------------------------------------
# Integration: full book segmentation
# ---------------------------------------------------------------------------

AL_LISS_CHAPTERS = Path("output/epub/al-liss-wal-kilab/02_chapters")


@pytest.mark.corpus
@pytest.mark.skipif(not AL_LISS_CHAPTERS.exists(), reason="Real EPUB data not available")
class TestIntegrationFullBook:
    def test_segment_full_book(self, tmp_path):
        summary = segment_book(str(AL_LISS_CHAPTERS), str(tmp_path))
        assert summary["total_chapters"] > 5
        assert summary["total_segments"] > 20
        assert 0.10 < summary["dialogue_ratio"] < 0.80

        # Every chapter should have a CSV and review file
        for ch in summary["chapters"]:
            assert Path(ch["csv_path"]).exists()
            assert Path(ch["review_path"]).exists()
