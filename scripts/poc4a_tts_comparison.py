#!/usr/bin/env python3
"""
POC-4a: TTS Provider Comparison for Arabic Audiobooks

Compare Arabic TTS quality across providers using the same chapter (ch15).
Prioritized by cost/quality ratio.

Providers (cost order):
  1. OpenAI     $15-30/1M chars   Generic voices, good prosody
  2. Google     $16/1M chars      ar-XA WaveNet voices, free 1M/month
  3. Azure      $16/1M chars      Baseline (already tested)
  4. ElevenLabs ~$300/1M chars    Highest quality, Arabic voice library

Usage:
    python scripts/poc4a_tts_comparison.py --provider openai
    python scripts/poc4a_tts_comparison.py --provider google
    python scripts/poc4a_tts_comparison.py --provider elevenlabs
    python scripts/poc4a_tts_comparison.py --provider azure
    python scripts/poc4a_tts_comparison.py --all
    python scripts/poc4a_tts_comparison.py --all --dry-run
    python scripts/poc4a_tts_comparison.py --provider elevenlabs --list-voices

Credentials (via `pass` or env vars):
    AZURE_SPEECH_KEY     or  pass amr/azure_tts
    ELEVENLABS_API_KEY   or  pass amr/elevenlabs_api
    OPENAI_API_KEY       (env var only — no pass entry)
    GOOGLE_TTS_API_KEY   (env var only — no pass entry)
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import os
import struct
import subprocess
import sys
import time
import wave
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

# httpx for REST APIs (stdlib fallback: urllib if not available)
try:
    import httpx

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)

# Ensure src/ is importable when running as script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEGMENTS_CSV = (
    PROJECT_ROOT
    / "output/epub/al-liss-wal-kilab/03_segments/ssml/chapter_15.csv"
)
OUTPUT_DIR = PROJECT_ROOT / "output/epub/al-liss-wal-kilab/05_audio/poc4a"

# ---------------------------------------------------------------------------
# Segment loading
# ---------------------------------------------------------------------------


@dataclass
class Segment:
    number: int
    type: str  # "narrator" or "dialogue"
    text: str
    char_count: int


def load_segments(csv_path: Path = SEGMENTS_CSV) -> list[Segment]:
    """Load segments from the dialogue detection CSV."""
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            Segment(
                number=int(row["segment_number"]),
                type=row["type"],
                text=row["text"],
                char_count=int(row["char_count"]),
            )
            for row in reader
        ]


def total_chars(segments: list[Segment]) -> int:
    return sum(s.char_count for s in segments)


# ---------------------------------------------------------------------------
# Segment coalescing for single-voice APIs
# ---------------------------------------------------------------------------


@dataclass
class CoalescedGroup:
    """Consecutive segments of the same type, merged for single-voice APIs."""

    voice_role: str  # "narrator" or "dialogue"
    text: str  # joined text with newline separators
    char_count: int
    segment_count: int
    break_before_ms: int | None  # silence to insert before this group


def coalesce_segments(segments: list[Segment]) -> list[CoalescedGroup]:
    """Merge consecutive same-type segments into groups.

    This gives single-voice APIs (OpenAI, ElevenLabs) enough Arabic context
    to avoid language detection failures on short segments.
    """
    if not segments:
        return []

    groups: list[CoalescedGroup] = []
    prev_type: str | None = None

    for seg in segments:
        if groups and seg.type == groups[-1].voice_role:
            # Same type — merge into current group
            g = groups[-1]
            g.text += "\n" + seg.text
            g.char_count += seg.char_count
            g.segment_count += 1
        else:
            # New type — start new group
            break_ms = _break_duration(prev_type, seg.type) if prev_type else None
            groups.append(
                CoalescedGroup(
                    voice_role=seg.type,
                    text=seg.text,
                    char_count=seg.char_count,
                    segment_count=1,
                    break_before_ms=break_ms,
                )
            )
        prev_type = seg.type

    return groups


# ---------------------------------------------------------------------------
# Silence generation (WAV, no dependencies)
# ---------------------------------------------------------------------------


def make_silence_wav(duration_ms: int, sample_rate: int = 24000) -> bytes:
    """Generate silence as raw WAV bytes."""
    num_samples = int(sample_rate * duration_ms / 1000)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(b"\x00\x00" * num_samples)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Audio concatenation via ffmpeg
# ---------------------------------------------------------------------------


def concat_audio_files(
    file_list: list[Path], output_path: Path, format: str = "mp3"
) -> None:
    """Concatenate audio files using ffmpeg."""
    list_file = output_path.parent / "_concat_list.txt"
    with open(list_file, "w") as f:
        for fp in file_list:
            f.write(f"file '{fp.resolve()}'\n")
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file),
                "-c:a",
                "libmp3lame",
                "-q:a",
                "2",
                str(output_path),
            ],
            capture_output=True,
            check=True,
        )
    finally:
        list_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Credential loading
# ---------------------------------------------------------------------------


def get_credential(env_var: str, pass_path: str | None = None) -> str | None:
    """Get credential from env var, or fallback to `pass`."""
    val = os.environ.get(env_var)
    if val:
        return val.strip()
    if pass_path:
        try:
            result = subprocess.run(
                ["pass", pass_path],
                capture_output=True,
                text=True,
                check=True,
            )
            # First line of pass output is the secret
            return result.stdout.strip().split("\n")[0]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    return None


def http_client() -> httpx.Client:
    if not HAS_HTTPX:
        print("ERROR: httpx required. Install: pip install httpx")
        sys.exit(1)
    return httpx.Client(timeout=120.0)


def http_post_with_retry(client: httpx.Client, url: str, max_retries: int = 5, **kwargs) -> httpx.Response:
    """POST with retry on rate limit (429), transient auth (401), or connection errors."""
    for attempt in range(max_retries + 1):
        try:
            resp = client.post(url, **kwargs)
        except (httpx.ConnectError, httpx.RemoteProtocolError, ConnectionError) as e:
            if attempt == max_retries:
                raise
            wait = min(2 ** attempt, 16)
            log.warning("  Connection error (%s), waiting %.0fs (attempt %d/%d)...", e, wait, attempt + 1, max_retries)
            time.sleep(wait)
            continue
        if resp.status_code not in (429, 401):
            resp.raise_for_status()
            return resp
        if attempt == max_retries:
            break
        wait = float(resp.headers.get("retry-after", min(2 ** attempt, 16)))
        log.warning(
            "  %d response, waiting %.0fs (attempt %d/%d)...",
            resp.status_code, wait, attempt + 1, max_retries,
        )
        time.sleep(wait)
    resp.raise_for_status()
    return resp


# ---------------------------------------------------------------------------
# Provider base
# ---------------------------------------------------------------------------


@dataclass
class ProviderResult:
    provider: str
    output_file: Path
    total_chars: int
    duration_sec: float
    cost_estimate_usd: float
    file_size_kb: float
    voice_config: str
    notes: str = ""


class TTSProvider(ABC):
    name: str
    cost_per_1m_chars: float  # USD

    @abstractmethod
    def check_credentials(self) -> bool: ...

    @abstractmethod
    def list_voices(self) -> None: ...

    @abstractmethod
    def synthesize(
        self, segments: list[Segment], output_path: Path
    ) -> ProviderResult: ...

    def estimate_cost(self, chars: int) -> float:
        return chars * self.cost_per_1m_chars / 1_000_000


# ---------------------------------------------------------------------------
# OpenAI TTS
# ---------------------------------------------------------------------------


class OpenAIProvider(TTSProvider):
    name = "openai"
    cost_per_1m_chars = 30.0  # tts-1-hd

    # Best generic voices for Arabic narration
    NARRATOR_VOICE = "onyx"  # deep male
    DIALOGUE_VOICE = "nova"  # expressive female
    MODEL = "tts-1-hd"

    def __init__(self):
        self.api_key = get_credential("OPENAI_API_KEY", "amr/openai_api")

    def check_credentials(self) -> bool:
        return self.api_key is not None

    def list_voices(self) -> None:
        print("OpenAI TTS voices (all multilingual):")
        for v in ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]:
            marker = " ← narrator" if v == self.NARRATOR_VOICE else ""
            marker = " ← dialogue" if v == self.DIALOGUE_VOICE else marker
            print(f"  {v}{marker}")

    def _synthesize_segment(
        self, text: str, voice: str, output_path: Path
    ) -> None:
        client = http_client()
        resp = http_post_with_retry(
            client,
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.MODEL,
                "voice": voice,
                "input": text,
                "response_format": "mp3",
            },
        )
        output_path.write_bytes(resp.content)

    def synthesize(
        self, segments: list[Segment], output_path: Path
    ) -> ProviderResult:
        t0 = time.time()
        chars = total_chars(segments)
        groups = coalesce_segments(segments)
        tmp_dir = output_path.parent / "_tmp_openai"
        tmp_dir.mkdir(exist_ok=True)

        parts: list[Path] = []

        for i, grp in enumerate(groups):
            voice = (
                self.NARRATOR_VOICE
                if grp.voice_role == "narrator"
                else self.DIALOGUE_VOICE
            )
            seg_file = tmp_dir / f"grp_{i:03d}.mp3"

            if grp.break_before_ms:
                sil_file = tmp_dir / f"sil_{i:03d}.wav"
                sil_file.write_bytes(make_silence_wav(grp.break_before_ms))
                parts.append(sil_file)

            log.info(
                "  OpenAI grp %d/%d (%s, %s, %d chars, %d segs)",
                i + 1,
                len(groups),
                grp.voice_role,
                voice,
                grp.char_count,
                grp.segment_count,
            )
            self._synthesize_segment(grp.text, voice, seg_file)
            parts.append(seg_file)

        log.info("  Concatenating %d parts...", len(parts))
        concat_audio_files(parts, output_path)

        # Cleanup
        for f in tmp_dir.iterdir():
            f.unlink()
        tmp_dir.rmdir()

        elapsed = time.time() - t0
        return ProviderResult(
            provider=self.name,
            output_file=output_path,
            total_chars=chars,
            duration_sec=elapsed,
            cost_estimate_usd=self.estimate_cost(chars),
            file_size_kb=output_path.stat().st_size / 1024,
            voice_config=f"{self.MODEL}: narrator={self.NARRATOR_VOICE}, dialogue={self.DIALOGUE_VOICE}",
            notes=f"Coalesced {len(segments)} segments → {len(groups)} groups",
        )


# ---------------------------------------------------------------------------
# Google Cloud TTS
# ---------------------------------------------------------------------------


class GoogleProvider(TTSProvider):
    name = "google"
    cost_per_1m_chars = 16.0  # WaveNet

    # ar-XA WaveNet voices
    NARRATOR_VOICE = "ar-XA-Wavenet-B"  # male
    DIALOGUE_VOICE = "ar-XA-Wavenet-A"  # female

    def __init__(self):
        self.api_key = get_credential("GOOGLE_TTS_API_KEY", "amr/google_api")

    def check_credentials(self) -> bool:
        return self.api_key is not None

    def list_voices(self) -> None:
        print("Google Cloud TTS Arabic voices (ar-XA):")
        voices = {
            "ar-XA-Wavenet-A": "Female (WaveNet)",
            "ar-XA-Wavenet-B": "Male (WaveNet)",
            "ar-XA-Wavenet-C": "Male (WaveNet)",
            "ar-XA-Wavenet-D": "Female (WaveNet)",
            "ar-XA-Standard-A": "Female (Standard)",
            "ar-XA-Standard-B": "Male (Standard)",
            "ar-XA-Standard-C": "Male (Standard)",
            "ar-XA-Standard-D": "Female (Standard)",
        }
        for v, desc in voices.items():
            marker = " ← narrator" if v == self.NARRATOR_VOICE else ""
            marker = " ← dialogue" if v == self.DIALOGUE_VOICE else marker
            print(f"  {v}: {desc}{marker}")

    def _synthesize_segment(
        self, text: str, voice_name: str, output_path: Path
    ) -> None:
        import base64

        client = http_client()
        resp = client.post(
            f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.api_key}",
            json={
                "input": {"text": text},
                "voice": {
                    "languageCode": "ar-XA",
                    "name": voice_name,
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "sampleRateHertz": 24000,
                },
            },
        )
        resp.raise_for_status()
        audio_b64 = resp.json()["audioContent"]
        output_path.write_bytes(base64.b64decode(audio_b64))

    def synthesize(
        self, segments: list[Segment], output_path: Path
    ) -> ProviderResult:
        t0 = time.time()
        chars = total_chars(segments)
        tmp_dir = output_path.parent / "_tmp_google"
        tmp_dir.mkdir(exist_ok=True)

        parts: list[Path] = []
        prev_type = None

        for i, seg in enumerate(segments):
            voice = (
                self.NARRATOR_VOICE
                if seg.type == "narrator"
                else self.DIALOGUE_VOICE
            )
            seg_file = tmp_dir / f"seg_{i:03d}.mp3"

            if prev_type is not None:
                silence_ms = _break_duration(prev_type, seg.type)
                sil_file = tmp_dir / f"sil_{i:03d}.wav"
                sil_file.write_bytes(make_silence_wav(silence_ms))
                parts.append(sil_file)

            log.info(
                "  Google seg %d/%d (%s, %s, %d chars)",
                i + 1,
                len(segments),
                seg.type,
                voice,
                seg.char_count,
            )
            self._synthesize_segment(seg.text, voice, seg_file)
            parts.append(seg_file)
            prev_type = seg.type

        log.info("  Concatenating %d parts...", len(parts))
        concat_audio_files(parts, output_path)

        for f in tmp_dir.iterdir():
            f.unlink()
        tmp_dir.rmdir()

        elapsed = time.time() - t0
        return ProviderResult(
            provider=self.name,
            output_file=output_path,
            total_chars=chars,
            duration_sec=elapsed,
            cost_estimate_usd=self.estimate_cost(chars),
            file_size_kb=output_path.stat().st_size / 1024,
            voice_config=f"WaveNet: narrator={self.NARRATOR_VOICE}, dialogue={self.DIALOGUE_VOICE}",
        )


# ---------------------------------------------------------------------------
# Azure TTS (baseline)
# ---------------------------------------------------------------------------


class AzureProvider(TTSProvider):
    name = "azure"
    cost_per_1m_chars = 16.0

    # Syrian voices — best natural quality from POC-4 testing
    NARRATOR_VOICE = "ar-SY-LaithNeural"
    DIALOGUE_VOICE = "ar-SY-AmanyNeural"

    def __init__(self):
        self.api_key = get_credential("AZURE_SPEECH_KEY", "amr/azure_tts")
        self.region = os.environ.get("AZURE_SPEECH_REGION", "eastus")

    def check_credentials(self) -> bool:
        return self.api_key is not None

    def list_voices(self) -> None:
        print("Azure Arabic Neural voices (tested in POC-4):")
        from src.audiobook.ssml.core import VOICE_INVENTORY

        for dialect, voices in sorted(VOICE_INVENTORY.items()):
            for gender, name in sorted(voices.items()):
                marker = " ← narrator" if name == self.NARRATOR_VOICE else ""
                marker = " ← dialogue" if name == self.DIALOGUE_VOICE else marker
                print(f"  {name} ({gender}){marker}")

    def synthesize(
        self, segments: list[Segment], output_path: Path
    ) -> ProviderResult:
        """Azure supports multi-voice SSML natively — use it."""
        from src.audiobook.ssml.core import VoiceConfig, build_ssml

        t0 = time.time()
        chars = total_chars(segments)

        voice_config = VoiceConfig(
            book_dialect="ar-SY",
            narrator_voice=self.NARRATOR_VOICE,
            dialogue_voice=self.DIALOGUE_VOICE,
        )
        seg_dicts = [
            {
                "segment_number": s.number,
                "type": s.type,
                "char_count": s.char_count,
                "text": s.text,
            }
            for s in segments
        ]
        ssml = build_ssml(seg_dicts, voice_config)

        # Use REST API directly (no SDK dependency for comparison fairness)
        client = http_client()
        token_resp = client.post(
            f"https://{self.region}.api.cognitive.microsoft.com/sts/v1.0/issueToken",
            headers={
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Length": "0",
            },
            content=b"",
        )
        token_resp.raise_for_status()
        token = token_resp.text

        log.info("  Azure: synthesizing full chapter via SSML (%d chars)...", chars)
        resp = client.post(
            f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
            },
            content=ssml.encode("utf-8"),
        )
        resp.raise_for_status()
        output_path.write_bytes(resp.content)

        elapsed = time.time() - t0
        return ProviderResult(
            provider=self.name,
            output_file=output_path,
            total_chars=chars,
            duration_sec=elapsed,
            cost_estimate_usd=self.estimate_cost(chars),
            file_size_kb=output_path.stat().st_size / 1024,
            voice_config=f"Neural SSML: narrator={self.NARRATOR_VOICE}, dialogue={self.DIALOGUE_VOICE}",
            notes="Multi-voice SSML (native, no concatenation)",
        )


# ---------------------------------------------------------------------------
# ElevenLabs TTS
# ---------------------------------------------------------------------------


class ElevenLabsProvider(TTSProvider):
    name = "elevenlabs"
    cost_per_1m_chars = 300.0  # approximate, varies by plan

    MODEL = "eleven_multilingual_v2"

    # Arabic voices from shared library
    NARRATOR_VOICE_ID = "HJ8unGw6UFYkApOU"  # "Omars" — MSA storytelling male
    NARRATOR_VOICE_NAME = "Omars (MSA)"
    DIALOGUE_VOICE_ID = "EUojVLG1QfxaqqH4"  # "Razan" — MSA academic female
    DIALOGUE_VOICE_NAME = "Razan (MSA)"

    def __init__(self):
        self.api_key = get_credential("ELEVENLABS_API_KEY", "amr/elevenlabs_api")

    def check_credentials(self) -> bool:
        return self.api_key is not None

    def list_voices(self) -> None:
        """Query ElevenLabs voice library for Arabic voices."""
        if not self.check_credentials():
            print("ElevenLabs: no API key available")
            return

        client = http_client()
        # Search shared voice library for Arabic
        print("ElevenLabs — searching for Arabic voices...\n")

        # User's own voices
        resp = client.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": self.api_key},
        )
        resp.raise_for_status()
        voices = resp.json()["voices"]
        print(f"Your library ({len(voices)} voices):")
        for v in voices:
            labels = v.get("labels", {})
            lang = labels.get("language", "?")
            accent = labels.get("accent", "")
            print(
                f"  {v['voice_id'][:12]}... {v['name']:20s} lang={lang} accent={accent}"
            )

        # Search shared library for Arabic
        print("\nShared library — Arabic voices:")
        resp = client.get(
            "https://api.elevenlabs.io/v1/shared-voices",
            headers={"xi-api-key": self.api_key},
            params={
                "language": "ar",
                "page_size": 20,
                "sort": "usage_character_count_7d",
            },
        )
        resp.raise_for_status()
        shared = resp.json().get("voices", [])
        for v in shared:
            print(
                f"  {v['voice_id'][:12]}... {v['name']:20s} "
                f"accent={v.get('accent', '?')} "
                f"gender={v.get('gender', '?')} "
                f"use_count={v.get('usage_character_count_7d', 0)}"
            )

    def _synthesize_segment(
        self, text: str, voice_id: str, output_path: Path
    ) -> None:
        client = http_client()
        resp = http_post_with_retry(
            client,
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": self.MODEL,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.4,
                },
            },
        )
        output_path.write_bytes(resp.content)
        # Free tier rate limit — delay between requests
        time.sleep(1.5)

    def synthesize(
        self, segments: list[Segment], output_path: Path
    ) -> ProviderResult:
        t0 = time.time()
        chars = total_chars(segments)
        groups = coalesce_segments(segments)
        tmp_dir = output_path.parent / "_tmp_elevenlabs"
        tmp_dir.mkdir(exist_ok=True)

        parts: list[Path] = []

        for i, grp in enumerate(groups):
            voice_id = (
                self.NARRATOR_VOICE_ID
                if grp.voice_role == "narrator"
                else self.DIALOGUE_VOICE_ID
            )
            voice_name = (
                self.NARRATOR_VOICE_NAME
                if grp.voice_role == "narrator"
                else self.DIALOGUE_VOICE_NAME
            )
            seg_file = tmp_dir / f"grp_{i:03d}.mp3"

            if grp.break_before_ms:
                sil_file = tmp_dir / f"sil_{i:03d}.wav"
                sil_file.write_bytes(make_silence_wav(grp.break_before_ms))
                parts.append(sil_file)

            log.info(
                "  ElevenLabs grp %d/%d (%s, %s, %d chars, %d segs)",
                i + 1,
                len(groups),
                grp.voice_role,
                voice_name,
                grp.char_count,
                grp.segment_count,
            )
            self._synthesize_segment(grp.text, voice_id, seg_file)
            parts.append(seg_file)

        log.info("  Concatenating %d parts...", len(parts))
        concat_audio_files(parts, output_path)

        for f in tmp_dir.iterdir():
            f.unlink()
        tmp_dir.rmdir()

        elapsed = time.time() - t0
        return ProviderResult(
            provider=self.name,
            output_file=output_path,
            total_chars=chars,
            duration_sec=elapsed,
            cost_estimate_usd=self.estimate_cost(chars),
            file_size_kb=output_path.stat().st_size / 1024,
            voice_config=(
                f"{self.MODEL}: narrator={self.NARRATOR_VOICE_NAME}, "
                f"dialogue={self.DIALOGUE_VOICE_NAME}"
            ),
            notes=f"Coalesced {len(segments)} segments → {len(groups)} groups",
        )


# ---------------------------------------------------------------------------
# Break duration (matching POC-4 SSML breaks)
# ---------------------------------------------------------------------------


def _break_duration(prev_type: str, cur_type: str) -> int:
    """Return silence duration in ms between segment types."""
    if prev_type != cur_type:
        return 300  # narrator↔dialogue transition
    if cur_type == "dialogue":
        return 200  # dialogue→dialogue (rapid exchange)
    return 500  # narrator→narrator (paragraph boundary)


# ---------------------------------------------------------------------------
# Comparison report
# ---------------------------------------------------------------------------


def print_report(results: list[ProviderResult], segments: list[Segment]) -> None:
    chars = total_chars(segments)
    full_book_chars = chars * 18  # ~18 chapters

    print("\n" + "=" * 70)
    print("POC-4a: TTS Provider Comparison — Chapter 15 (al-liss-wal-kilab)")
    print(f"Segments: {len(segments)} | Characters: {chars:,}")
    print("=" * 70)

    for r in sorted(results, key=lambda x: x.cost_estimate_usd):
        print(f"\n--- {r.provider.upper()} ---")
        print(f"  File:       {r.output_file.name} ({r.file_size_kb:.0f} KB)")
        print(f"  Voices:     {r.voice_config}")
        print(f"  Time:       {r.duration_sec:.1f}s")
        print(f"  Ch15 cost:  ${r.cost_estimate_usd:.4f}")
        print(
            f"  Full book:  ${r.cost_estimate_usd * 18:.2f} (est. {full_book_chars:,} chars)"
        )
        if r.notes:
            print(f"  Notes:      {r.notes}")

    print("\n" + "-" * 70)
    print("COST COMPARISON (full book estimate):")
    for r in sorted(results, key=lambda x: x.cost_estimate_usd):
        book_cost = r.cost_estimate_usd * 18
        print(f"  {r.provider:12s}  ${book_cost:.2f}")
    print("-" * 70)
    print("Listen to files in:", OUTPUT_DIR)
    print()


def print_dry_run(segments: list[Segment]) -> None:
    chars = total_chars(segments)
    full_book_chars = chars * 18

    print("\n" + "=" * 70)
    print("POC-4a DRY RUN — Cost Estimates")
    print(f"Chapter 15: {chars:,} chars | Full book est: {full_book_chars:,} chars")
    print("=" * 70)

    providers = [
        ("OpenAI (tts-1-hd)", 30.0),
        ("Google (WaveNet)", 16.0),
        ("Azure (Neural)", 16.0),
        ("ElevenLabs (v2)", 300.0),
    ]
    for name, cost_per_1m in providers:
        ch_cost = chars * cost_per_1m / 1_000_000
        book_cost = full_book_chars * cost_per_1m / 1_000_000
        print(f"  {name:25s}  ch15: ${ch_cost:.4f}  book: ${book_cost:.2f}")

    print("=" * 70)
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

PROVIDERS: dict[str, type[TTSProvider]] = {
    "openai": OpenAIProvider,
    "google": GoogleProvider,
    "azure": AzureProvider,
    "elevenlabs": ElevenLabsProvider,
}

# Cost-priority order
PROVIDER_ORDER = ["openai", "google", "azure", "elevenlabs"]


def main():
    parser = argparse.ArgumentParser(
        description="POC-4a: Compare Arabic TTS providers"
    )
    parser.add_argument(
        "--provider",
        choices=list(PROVIDERS.keys()),
        help="Run a specific provider",
    )
    parser.add_argument(
        "--all", action="store_true", help="Run all providers with credentials"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Cost estimate only, no API calls"
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List available voices for provider",
    )
    args = parser.parse_args()

    if not args.provider and not args.all and not args.dry_run:
        parser.print_help()
        return

    segments = load_segments()
    chars = total_chars(segments)
    log.info(
        "Loaded %d segments, %d chars from %s",
        len(segments),
        chars,
        SEGMENTS_CSV.name,
    )

    if args.dry_run:
        print_dry_run(segments)
        return

    if args.list_voices:
        if not args.provider:
            print("--list-voices requires --provider")
            return
        provider = PROVIDERS[args.provider]()
        provider.list_voices()
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    providers_to_run = (
        PROVIDER_ORDER if args.all else [args.provider] if args.provider else []
    )

    results: list[ProviderResult] = []
    for name in providers_to_run:
        provider = PROVIDERS[name]()
        if not provider.check_credentials():
            log.warning(
                "Skipping %s — no credentials (set %s or configure pass)",
                name,
                {
                    "openai": "OPENAI_API_KEY",
                    "google": "GOOGLE_TTS_API_KEY",
                    "azure": "AZURE_SPEECH_KEY",
                    "elevenlabs": "ELEVENLABS_API_KEY",
                }[name],
            )
            continue

        output_file = OUTPUT_DIR / f"ch15_{name}.mp3"
        log.info("Running %s → %s", name, output_file.name)
        try:
            result = provider.synthesize(segments, output_file)
            results.append(result)
            log.info(
                "  ✓ %s done: %.0f KB in %.1fs ($%.4f)",
                name,
                result.file_size_kb,
                result.duration_sec,
                result.cost_estimate_usd,
            )
        except Exception as e:
            log.error("  ✗ %s failed: %s", name, e)

    if results:
        print_report(results, segments)

        # Save results as JSON for reference
        report_path = OUTPUT_DIR / "comparison.json"
        report_data = [
            {
                "provider": r.provider,
                "output_file": r.output_file.name,
                "total_chars": r.total_chars,
                "duration_sec": round(r.duration_sec, 1),
                "cost_estimate_usd": round(r.cost_estimate_usd, 4),
                "file_size_kb": round(r.file_size_kb, 0),
                "voice_config": r.voice_config,
                "notes": r.notes,
            }
            for r in results
        ]
        report_path.write_text(
            json.dumps(report_data, indent=2, ensure_ascii=False)
        )
        log.info("Report saved: %s", report_path)


if __name__ == "__main__":
    main()
