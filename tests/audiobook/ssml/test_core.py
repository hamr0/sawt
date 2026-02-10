"""Tests for POC-4: SSML Generation + Voice Selection."""
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from src.audiobook.ssml import (
    VOICE_INVENTORY,
    build_ssml,
    generate_book_ssml,
    generate_chapter_ssml,
    make_voice_config,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seg(num: int, seg_type: str, text: str) -> dict:
    """Shorthand for building a segment dict."""
    return {
        "segment_number": str(num),
        "type": seg_type,
        "char_count": str(len(text)),
        "text": text,
    }


def _parse_ssml(ssml: str) -> ET.Element:
    """Parse SSML string and return root element."""
    return ET.fromstring(ssml)


def _write_segment_csv(path: Path, segments: list[dict]) -> None:
    """Write a segment CSV file for testing."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["segment_number", "type", "char_count", "text"]
        )
        writer.writeheader()
        for seg in segments:
            writer.writerow(seg)


# ---------------------------------------------------------------------------
# TestVoiceConfig
# ---------------------------------------------------------------------------


class TestMakeVoiceConfig:
    def test_default_egyptian_male_narrator(self):
        cfg = make_voice_config()
        assert cfg["book_dialect"] == "ar-EG"
        assert cfg["narrator_voice"] == "ar-EG-ShakirNeural"
        assert cfg["dialogue_voice"] == "ar-EG-SalmaNeural"

    def test_egyptian_female_narrator(self):
        cfg = make_voice_config("ar-EG", "female")
        assert cfg["narrator_voice"] == "ar-EG-SalmaNeural"
        assert cfg["dialogue_voice"] == "ar-EG-ShakirNeural"

    def test_all_dialects(self):
        for dialect in VOICE_INVENTORY:
            cfg = make_voice_config(dialect)
            assert cfg["book_dialect"] == dialect
            assert cfg["narrator_voice"] != cfg["dialogue_voice"]

    def test_unknown_dialect_raises(self):
        with pytest.raises(ValueError, match="Unknown dialect"):
            make_voice_config("ar-XX")

    def test_male_female_swap(self):
        for dialect in VOICE_INVENTORY:
            male_cfg = make_voice_config(dialect, "male")
            female_cfg = make_voice_config(dialect, "female")
            assert male_cfg["narrator_voice"] == female_cfg["dialogue_voice"]
            assert male_cfg["dialogue_voice"] == female_cfg["narrator_voice"]


# ---------------------------------------------------------------------------
# TestBuildSSML
# ---------------------------------------------------------------------------


class TestBuildSSML:
    def setup_method(self):
        self.config = make_voice_config("ar-EG", "male")

    def test_pure_narrator(self):
        segments = [
            _seg(1, "narrator", "نص عادي"),
            _seg(2, "narrator", "نص آخر"),
        ]
        ssml = build_ssml(segments, self.config)
        root = _parse_ssml(ssml)
        assert root.tag == "{http://www.w3.org/2001/10/synthesis}speak"
        voices = root.findall("{http://www.w3.org/2001/10/synthesis}voice")
        assert len(voices) == 1
        assert voices[0].attrib["name"] == "ar-EG-ShakirNeural"

    def test_pure_dialogue(self):
        segments = [
            _seg(1, "dialogue", "مرحبا"),
            _seg(2, "dialogue", "أهلا"),
        ]
        ssml = build_ssml(segments, self.config)
        root = _parse_ssml(ssml)
        voices = root.findall("{http://www.w3.org/2001/10/synthesis}voice")
        assert len(voices) == 1
        assert voices[0].attrib["name"] == "ar-EG-SalmaNeural"

    def test_mixed_narrator_dialogue(self):
        segments = [
            _seg(1, "narrator", "ذهب إلى البيت"),
            _seg(2, "dialogue", "مرحبا"),
            _seg(3, "narrator", "قال وهو يبتسم"),
        ]
        ssml = build_ssml(segments, self.config)
        root = _parse_ssml(ssml)
        voices = root.findall("{http://www.w3.org/2001/10/synthesis}voice")
        assert len(voices) == 3
        assert voices[0].attrib["name"] == "ar-EG-ShakirNeural"
        assert voices[1].attrib["name"] == "ar-EG-SalmaNeural"
        assert voices[2].attrib["name"] == "ar-EG-ShakirNeural"

    def test_coalesces_consecutive_same_voice(self):
        segments = [
            _seg(1, "narrator", "نص أول"),
            _seg(2, "narrator", "نص ثاني"),
            _seg(3, "narrator", "نص ثالث"),
        ]
        ssml = build_ssml(segments, self.config)
        assert ssml.count("<voice ") == 1

    def test_break_at_voice_transition(self):
        segments = [
            _seg(1, "narrator", "قال"),
            _seg(2, "dialogue", "مرحبا"),
        ]
        ssml = build_ssml(segments, self.config)
        assert '<break time="300ms"/>' in ssml

    def test_paragraph_break_between_narrator(self):
        segments = [
            _seg(1, "narrator", "نص أول"),
            _seg(2, "narrator", "نص ثاني"),
        ]
        ssml = build_ssml(segments, self.config)
        assert '<break time="500ms"/>' in ssml

    def test_dialogue_break_between_dialogue(self):
        segments = [
            _seg(1, "dialogue", "مرحبا"),
            _seg(2, "dialogue", "أهلا"),
        ]
        ssml = build_ssml(segments, self.config)
        assert '<break time="200ms"/>' in ssml

    def test_no_break_before_first_segment(self):
        segments = [_seg(1, "narrator", "نص")]
        ssml = build_ssml(segments, self.config)
        assert "<break" not in ssml

    def test_valid_xml(self):
        segments = [
            _seg(1, "narrator", "نص"),
            _seg(2, "dialogue", "حوار"),
            _seg(3, "narrator", "نص"),
            _seg(4, "dialogue", "حوار"),
        ]
        ssml = build_ssml(segments, self.config)
        _parse_ssml(ssml)

    def test_xml_lang_matches_dialect(self):
        cfg = make_voice_config("ar-SY")
        segments = [_seg(1, "narrator", "نص")]
        ssml = build_ssml(segments, cfg)
        root = _parse_ssml(ssml)
        assert root.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "ar-SY"

    def test_empty_segments_raises(self):
        with pytest.raises(ValueError, match="No segments"):
            build_ssml([], self.config)

    def test_text_preserved(self):
        text = "هذا نص عربي طويل مع تفاصيل كثيرة"
        segments = [_seg(1, "narrator", text)]
        ssml = build_ssml(segments, self.config)
        assert text in ssml


# ---------------------------------------------------------------------------
# TestGenerateChapterSSML
# ---------------------------------------------------------------------------


class TestGenerateChapterSSML:
    def test_roundtrip(self, tmp_path):
        csv_dir = tmp_path / "ssml"
        csv_dir.mkdir()
        csv_path = csv_dir / "chapter_01.csv"
        _write_segment_csv(
            csv_path,
            [
                _seg(1, "narrator", "ذهب إلى البيت"),
                _seg(2, "dialogue", "مرحبا"),
                _seg(3, "narrator", "رد عليه"),
            ],
        )

        out_dir = tmp_path / "04_ssml"
        cfg = make_voice_config()
        summary = generate_chapter_ssml(str(csv_path), str(out_dir), cfg)

        assert summary["chapter"] == "chapter_01"
        assert summary["total_segments"] == 3
        assert summary["narrator_segments"] == 2
        assert summary["dialogue_segments"] == 1

        ssml_path = Path(summary["ssml_path"])
        assert ssml_path.exists()
        assert ssml_path.suffix == ".ssml"

        _parse_ssml(ssml_path.read_text(encoding="utf-8"))

    def test_voice_tags_counted(self, tmp_path):
        csv_dir = tmp_path / "ssml"
        csv_dir.mkdir()
        csv_path = csv_dir / "chapter_01.csv"
        _write_segment_csv(
            csv_path,
            [
                _seg(1, "narrator", "نص"),
                _seg(2, "dialogue", "حوار"),
                _seg(3, "narrator", "نص"),
            ],
        )

        out_dir = tmp_path / "04_ssml"
        summary = generate_chapter_ssml(str(csv_path), str(out_dir), make_voice_config())
        assert summary["voice_tags"] == 3


# ---------------------------------------------------------------------------
# TestGenerateBookSSML
# ---------------------------------------------------------------------------


class TestGenerateBookSSML:
    def _setup_book(self, tmp_path, num_chapters=3):
        """Create a fake 03_segments/ssml/ structure."""
        seg_dir = tmp_path / "03_segments" / "ssml"
        seg_dir.mkdir(parents=True)
        for i in range(1, num_chapters + 1):
            _write_segment_csv(
                seg_dir / f"chapter_{i:02d}.csv",
                [
                    _seg(1, "narrator", f"نص الفصل {i}"),
                    _seg(2, "dialogue", f"حوار الفصل {i}"),
                ],
            )
        return tmp_path / "03_segments"

    def test_generates_all_chapters(self, tmp_path):
        seg_dir = self._setup_book(tmp_path, 3)
        result = generate_book_ssml(str(seg_dir))

        assert result["total_chapters"] == 3
        assert result["total_segments"] == 6
        assert len(result["chapters"]) == 3

        out_dir = Path(result["output_dir"])
        assert len(list(out_dir.glob("chapter_*.ssml"))) == 3

    def test_default_output_dir(self, tmp_path):
        seg_dir = self._setup_book(tmp_path)
        result = generate_book_ssml(str(seg_dir))
        assert result["output_dir"] == str(tmp_path / "04_ssml")

    def test_custom_output_dir(self, tmp_path):
        seg_dir = self._setup_book(tmp_path)
        custom = tmp_path / "custom_out"
        result = generate_book_ssml(str(seg_dir), output_dir=str(custom))
        assert result["output_dir"] == str(custom)

    def test_default_voice_config_egyptian(self, tmp_path):
        seg_dir = self._setup_book(tmp_path)
        result = generate_book_ssml(str(seg_dir))
        assert result["voice_config"]["book_dialect"] == "ar-EG"

    def test_custom_voice_config(self, tmp_path):
        seg_dir = self._setup_book(tmp_path)
        cfg = make_voice_config("ar-SY", "female")
        result = generate_book_ssml(str(seg_dir), voice_config=cfg)
        assert result["voice_config"]["book_dialect"] == "ar-SY"

    def test_clears_stale_files(self, tmp_path):
        seg_dir = self._setup_book(tmp_path, 2)
        out_dir = tmp_path / "04_ssml"
        out_dir.mkdir(parents=True)
        stale = out_dir / "chapter_99.ssml"
        stale.write_text("stale", encoding="utf-8")

        generate_book_ssml(str(seg_dir), output_dir=str(out_dir))
        assert not stale.exists()

    def test_summary_csv_written(self, tmp_path):
        seg_dir = self._setup_book(tmp_path)
        result = generate_book_ssml(str(seg_dir))

        summary_csv = Path(result["summary_csv"])
        assert summary_csv.exists()

        with open(summary_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 3
        assert "chapter" in reader.fieldnames
        assert "voice_tags" in reader.fieldnames

    def test_no_csv_files_raises(self, tmp_path):
        empty = tmp_path / "03_segments" / "ssml"
        empty.mkdir(parents=True)
        with pytest.raises(FileNotFoundError):
            generate_book_ssml(str(tmp_path / "03_segments"))

    def test_all_ssml_files_valid_xml(self, tmp_path):
        seg_dir = self._setup_book(tmp_path, 3)
        result = generate_book_ssml(str(seg_dir))
        for ch in result["chapters"]:
            ssml_text = Path(ch["ssml_path"]).read_text(encoding="utf-8")
            _parse_ssml(ssml_text)


# ---------------------------------------------------------------------------
# Integration tests (real book data)
# ---------------------------------------------------------------------------

AL_LISS_SEGMENTS = Path(
    "output/epub/al-liss-wal-kilab/03_segments"
)


@pytest.mark.skipif(
    not (AL_LISS_SEGMENTS / "ssml" / "chapter_01.csv").exists(),
    reason="Real EPUB data not available",
)
class TestIntegrationAlLiss:
    def test_generates_ssml(self, tmp_path):
        result = generate_book_ssml(str(AL_LISS_SEGMENTS), output_dir=str(tmp_path))
        assert result["total_chapters"] > 0
        assert result["total_segments"] > 10
        for ch in result["chapters"]:
            ssml_text = Path(ch["ssml_path"]).read_text(encoding="utf-8")
            _parse_ssml(ssml_text)

    def test_two_distinct_voices_only(self, tmp_path):
        """Azure limit is 50 distinct voice tags — two-voice uses only 2."""
        result = generate_book_ssml(str(AL_LISS_SEGMENTS), output_dir=str(tmp_path))
        cfg = result["voice_config"]
        for ch in result["chapters"]:
            ssml_text = Path(ch["ssml_path"]).read_text(encoding="utf-8")
            root = _parse_ssml(ssml_text)
            ns = "{http://www.w3.org/2001/10/synthesis}"
            voice_names = {v.attrib["name"] for v in root.findall(f"{ns}voice")}
            assert voice_names <= {cfg["narrator_voice"], cfg["dialogue_voice"]}
