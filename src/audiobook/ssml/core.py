"""
SSML generation from verified segments.

Two voice: narrator/dialogue → two voice tags (M/F switch per dialect).

Input:  output/{format}/{book}/03_segments/ssml/chapter_*.csv
Output: output/{format}/{book}/04_ssml/chapter_*.ssml
"""
import csv
import logging
from pathlib import Path
from typing import TypedDict

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SEGMENT_COLUMNS = ["segment_number", "type", "char_count", "text"]

# Azure Arabic voice inventory — one male + one female per dialect.
VOICE_INVENTORY: dict[str, dict[str, str]] = {
    "ar-EG": {"male": "ar-EG-ShakirNeural", "female": "ar-EG-SalmaNeural"},
    "ar-SA": {"male": "ar-SA-HamedNeural", "female": "ar-SA-ZariyahNeural"},
    "ar-SY": {"male": "ar-SY-LaithNeural", "female": "ar-SY-AmanyNeural"},
    "ar-JO": {"male": "ar-JO-TaimNeural", "female": "ar-JO-SanaNeural"},
    "ar-LB": {"male": "ar-LB-RamiNeural", "female": "ar-LB-LaylaNeural"},
    "ar-IQ": {"male": "ar-IQ-BasselNeural", "female": "ar-IQ-RanaNeural"},
    "ar-MA": {"male": "ar-MA-JamalNeural", "female": "ar-MA-MounaNeural"},
}

SSML_HEADER = (
    '<speak version="1.0"'
    ' xmlns="http://www.w3.org/2001/10/synthesis"'
    ' xmlns:mstts="https://www.w3.org/2001/mstts"'
    ' xml:lang="{lang}">'
)
SSML_FOOTER = "</speak>"

TRANSITION_BREAK = '<break time="300ms"/>'

CSV_SUMMARY_COLUMNS = [
    "chapter",
    "total_segments",
    "narrator_segments",
    "dialogue_segments",
    "voice_tags",
    "ssml_path",
]


# ---------------------------------------------------------------------------
# Voice config
# ---------------------------------------------------------------------------


class VoiceConfig(TypedDict):
    book_dialect: str
    narrator_voice: str
    dialogue_voice: str


def make_voice_config(
    dialect: str = "ar-EG", narrator_gender: str = "male"
) -> VoiceConfig:
    """Build a two-voice config from dialect and narrator gender.

    The other voice gets the opposite gender.

    Args:
        dialect: Azure locale code (e.g. "ar-EG").
        narrator_gender: "male" or "female" for the narrator voice.

    Returns:
        VoiceConfig with dialect, narrator, and dialogue voices.
    """
    if dialect not in VOICE_INVENTORY:
        raise ValueError(
            f"Unknown dialect {dialect!r}. "
            f"Available: {', '.join(sorted(VOICE_INVENTORY))}"
        )
    voices = VOICE_INVENTORY[dialect]
    other = "female" if narrator_gender == "male" else "male"
    return VoiceConfig(
        book_dialect=dialect,
        narrator_voice=voices[narrator_gender],
        dialogue_voice=voices[other],
    )


# ---------------------------------------------------------------------------
# SSML builder (pure function, no I/O)
# ---------------------------------------------------------------------------


def build_ssml(segments: list[dict], voice_config: VoiceConfig) -> str:
    """Convert segment dicts into a valid Azure SSML string.

    Coalesces consecutive same-voice segments under one <voice> tag.
    Inserts a <break> at narrator↔dialogue transitions.

    Args:
        segments: List of dicts with keys: segment_number, type, char_count, text.
        voice_config: Two-voice config (dialect, narrator, dialogue).

    Returns:
        Complete SSML string ready for Azure TTS API.
    """
    if not segments:
        raise ValueError("No segments to convert")

    lang = voice_config["book_dialect"]
    parts: list[str] = [SSML_HEADER.format(lang=lang)]

    current_voice: str | None = None
    prev_type: str | None = None

    for seg in segments:
        seg_type = seg["type"]
        voice = (
            voice_config["narrator_voice"]
            if seg_type == "narrator"
            else voice_config["dialogue_voice"]
        )

        if voice != current_voice:
            # Close previous voice tag
            if current_voice is not None:
                parts.append("</voice>")
            # Insert break at narrator↔dialogue transition
            if prev_type is not None and prev_type != seg_type:
                parts.append(TRANSITION_BREAK)
            parts.append(f'<voice name="{voice}">')
            current_voice = voice
        else:
            # Same voice block — still insert break if type changed
            if prev_type is not None and prev_type != seg_type:
                parts.append(TRANSITION_BREAK)

        parts.append(seg["text"])
        prev_type = seg_type

    # Close last voice tag
    if current_voice is not None:
        parts.append("</voice>")

    parts.append(SSML_FOOTER)
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Chapter-level: CSV → SSML file
# ---------------------------------------------------------------------------


def generate_chapter_ssml(
    csv_path: str, output_dir: str, voice_config: VoiceConfig
) -> dict:
    """Read a segment CSV and write an SSML file.

    Args:
        csv_path: Path to 03_segments/ssml/chapter_*.csv
        output_dir: Directory for .ssml output files.
        voice_config: Two-voice config.

    Returns:
        Summary dict with chapter stats.
    """
    cp = Path(csv_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    with open(cp, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        segments = list(reader)

    ssml = build_ssml(segments, voice_config)
    ssml_path = out / (cp.stem + ".ssml")
    ssml_path.write_text(ssml, encoding="utf-8")

    narrator_count = sum(1 for s in segments if s["type"] == "narrator")
    dialogue_count = sum(1 for s in segments if s["type"] == "dialogue")
    voice_tags = ssml.count("<voice ")

    logger.info(
        "%s: %d segments (%d narrator, %d dialogue) → %s",
        cp.stem,
        len(segments),
        narrator_count,
        dialogue_count,
        ssml_path,
    )

    return {
        "chapter": cp.stem,
        "total_segments": len(segments),
        "narrator_segments": narrator_count,
        "dialogue_segments": dialogue_count,
        "voice_tags": voice_tags,
        "ssml_path": str(ssml_path),
    }


# ---------------------------------------------------------------------------
# Book-level orchestrator
# ---------------------------------------------------------------------------


def generate_book_ssml(
    segments_dir: str,
    output_dir: str | None = None,
    voice_config: VoiceConfig | None = None,
) -> dict:
    """Generate SSML files for all chapters in a book.

    Args:
        segments_dir: Path to 03_segments/ (must contain ssml/ subdirectory).
        output_dir: Override output dir. Defaults to sibling 04_ssml/.
        voice_config: Two-voice config. Defaults to Egyptian M-narrator/F-dialogue.

    Returns:
        Aggregate summary dict with per-chapter and totals.
    """
    seg_dir = Path(segments_dir)
    ssml_subdir = seg_dir / "ssml" if (seg_dir / "ssml").exists() else seg_dir

    csv_files = sorted(ssml_subdir.glob("chapter_*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No chapter_*.csv files in {ssml_subdir}")

    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = seg_dir.parent / "04_ssml"

    # Clear stale files
    if out_path.exists():
        for old in out_path.glob("chapter_*.ssml"):
            old.unlink()

    if voice_config is None:
        voice_config = make_voice_config("ar-EG", "male")

    chapter_summaries = []
    for csv_file in csv_files:
        summary = generate_chapter_ssml(str(csv_file), str(out_path), voice_config)
        chapter_summaries.append(summary)

    # Write summary CSV
    summary_csv = out_path / "ssml_summary.csv"
    with open(summary_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_SUMMARY_COLUMNS)
        writer.writeheader()
        for ch in chapter_summaries:
            writer.writerow({col: ch[col] for col in CSV_SUMMARY_COLUMNS})

    total_segments = sum(ch["total_segments"] for ch in chapter_summaries)
    total_narrator = sum(ch["narrator_segments"] for ch in chapter_summaries)
    total_dialogue = sum(ch["dialogue_segments"] for ch in chapter_summaries)

    logger.info(
        "Book SSML: %d chapters, %d segments → %s",
        len(chapter_summaries),
        total_segments,
        out_path,
    )

    return {
        "total_chapters": len(chapter_summaries),
        "total_segments": total_segments,
        "narrator_segments": total_narrator,
        "dialogue_segments": total_dialogue,
        "voice_config": dict(voice_config),
        "output_dir": str(out_path),
        "summary_csv": str(summary_csv),
        "chapters": chapter_summaries,
    }
