#!/usr/bin/env python3
"""Generate 8 two-voice samples: 4 gender combos × 2 providers (Google + ElevenLabs).

Book: tharthara-fawq-al-nil (Chitchat on the Nile), Chapter 1
All voices are V Liked from listening tests.
"""
from __future__ import annotations

import base64
import csv
import io
import logging
import os
import subprocess
import sys
import time
import wave
from dataclasses import dataclass
from pathlib import Path

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEGMENTS_CSV = (
    PROJECT_ROOT
    / "output/epub/tharthara-fawq-al-nil-hindawi/03_segments/ssml/chapter_01.csv"
)
OUTPUT_DIR = PROJECT_ROOT / "output/epub/tharthara-fawq-al-nil-hindawi/05_audio/voice_pairings"

# ---------------------------------------------------------------------------
# Voice pairings — ALL V Liked
# ---------------------------------------------------------------------------

GOOGLE_PAIRINGS = {
    "google_MM": ("Enceladus", "Sadaltager"),
    "google_FF": ("Sulafat", "Leda"),
    "google_MF": ("Orus", "Leda"),
    "google_FM": ("Sulafat", "Rasalgethi"),
}

ELEVENLABS_PAIRINGS = {
    "elevenlabs_MM": {
        "narrator": ("QRq5hPRAKf5ZhSlTBH6r", "Yahya"),
        "dialogue": ("oUCSlKjkoFDoKamPHpAV", "Karim"),
    },
    "elevenlabs_FF": {
        "narrator": ("RzNYiYBiH7YrpC9QKXyc", "Sakina"),
        "dialogue": ("XTa3iQyMA6f1qrI4F6kZ", "Sara"),
    },
    "elevenlabs_MF": {
        "narrator": ("Jez3JdhBInQTvlAvDOWR", "Moncellence"),
        "dialogue": ("LjKPkQHpXCsWoy7Pjq4U", "Alice"),
    },
    "elevenlabs_FM": {
        "narrator": ("XTa3iQyMA6f1qrI4F6kZ", "Sara"),
        "dialogue": ("ZCXYdzd5Evtsll2EdoCi", "Yousef"),
    },
}


# ---------------------------------------------------------------------------
# Segment loading
# ---------------------------------------------------------------------------

@dataclass
class Segment:
    number: int
    type: str
    text: str
    char_count: int


def load_segments() -> list[Segment]:
    with open(SEGMENTS_CSV, encoding="utf-8") as f:
        return [
            Segment(
                number=int(row["segment_number"]),
                type=row["type"],
                text=row["text"],
                char_count=int(row["char_count"]),
            )
            for row in csv.DictReader(f)
        ]


# ---------------------------------------------------------------------------
# Coalescing (for ElevenLabs — needs longer chunks for Arabic detection)
# ---------------------------------------------------------------------------

@dataclass
class CoalescedGroup:
    voice_role: str
    text: str
    char_count: int
    segment_count: int
    break_before_ms: int | None


def _break_duration(prev_type: str, cur_type: str) -> int:
    if prev_type != cur_type:
        return 300
    if cur_type == "dialogue":
        return 200
    return 500


def coalesce_segments(segments: list[Segment]) -> list[CoalescedGroup]:
    if not segments:
        return []
    groups: list[CoalescedGroup] = []
    prev_type: str | None = None
    for seg in segments:
        if groups and seg.type == groups[-1].voice_role:
            g = groups[-1]
            g.text += "\n" + seg.text
            g.char_count += seg.char_count
            g.segment_count += 1
        else:
            break_ms = _break_duration(prev_type, seg.type) if prev_type else None
            groups.append(
                CoalescedGroup(
                    voice_role=seg.type, text=seg.text,
                    char_count=seg.char_count, segment_count=1,
                    break_before_ms=break_ms,
                )
            )
        prev_type = seg.type
    return groups


# ---------------------------------------------------------------------------
# Audio utils
# ---------------------------------------------------------------------------

def make_silence_wav(duration_ms: int, sample_rate: int = 24000) -> bytes:
    num_samples = int(sample_rate * duration_ms / 1000)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(b"\x00\x00" * num_samples)
    return buf.getvalue()


def concat_audio_files(file_list: list[Path], output_path: Path) -> None:
    list_file = output_path.parent / "_concat_list.txt"
    with open(list_file, "w") as f:
        for fp in file_list:
            f.write(f"file '{fp.resolve()}'\n")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", str(list_file), "-c:a", "libmp3lame", "-q:a", "2",
             str(output_path)],
            capture_output=True, check=True,
        )
    finally:
        list_file.unlink(missing_ok=True)


def get_credential(env_var: str, pass_path: str | None = None) -> str | None:
    val = os.environ.get(env_var)
    if val:
        return val.strip()
    if pass_path:
        try:
            result = subprocess.run(
                ["pass", pass_path], capture_output=True, text=True, check=True,
            )
            return result.stdout.strip().split("\n")[0]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    return None


def http_post_with_retry(client: httpx.Client, url: str, max_retries: int = 5, **kwargs) -> httpx.Response:
    for attempt in range(max_retries + 1):
        try:
            resp = client.post(url, **kwargs)
        except (httpx.ConnectError, httpx.RemoteProtocolError, ConnectionError) as e:
            if attempt == max_retries:
                raise
            wait = min(2 ** attempt, 16)
            log.warning("Connection error (%s), waiting %.0fs...", e, wait)
            time.sleep(wait)
            continue
        if resp.status_code not in (429, 401):
            resp.raise_for_status()
            return resp
        if attempt == max_retries:
            break
        wait = float(resp.headers.get("retry-after", min(2 ** attempt, 16)))
        log.warning("%d response, waiting %.0fs...", resp.status_code, wait)
        time.sleep(wait)
    resp.raise_for_status()
    return resp


# ---------------------------------------------------------------------------
# Google Chirp3-HD generation
# ---------------------------------------------------------------------------

def generate_google_pairing(
    label: str, narrator_voice: str, dialogue_voice: str,
    segments: list[Segment], output_dir: Path, api_key: str,
) -> Path:
    out_file = output_dir / f"{label}.mp3"
    if out_file.exists():
        log.info("SKIP %s (exists)", label)
        return out_file

    tmp_dir = output_dir / f"_tmp_{label}"
    tmp_dir.mkdir(exist_ok=True)
    client = httpx.Client(timeout=60)
    parts: list[Path] = []
    prev_type = None

    for i, seg in enumerate(segments):
        voice_name = (
            f"ar-XA-Chirp3-HD-{narrator_voice}"
            if seg.type == "narrator"
            else f"ar-XA-Chirp3-HD-{dialogue_voice}"
        )

        if prev_type is not None:
            sil_ms = _break_duration(prev_type, seg.type)
            sil_file = tmp_dir / f"sil_{i:03d}.wav"
            sil_file.write_bytes(make_silence_wav(sil_ms))
            parts.append(sil_file)

        seg_file = tmp_dir / f"seg_{i:03d}.mp3"
        log.info("  %s seg %d/%d (%s → %s)", label, i + 1, len(segments), seg.type, voice_name.split("-")[-1])

        resp = client.post(
            f"https://texttospeech.googleapis.com/v1beta1/text:synthesize?key={api_key}",
            json={
                "input": {"text": seg.text},
                "voice": {"languageCode": "ar-XA", "name": voice_name},
                "audioConfig": {"audioEncoding": "MP3", "sampleRateHertz": 24000},
            },
        )
        resp.raise_for_status()
        audio_b64 = resp.json()["audioContent"]
        seg_file.write_bytes(base64.b64decode(audio_b64))
        parts.append(seg_file)
        prev_type = seg.type
        time.sleep(0.2)

    client.close()
    log.info("  Concatenating %d parts → %s", len(parts), out_file.name)
    concat_audio_files(parts, out_file)

    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()
    return out_file


# ---------------------------------------------------------------------------
# ElevenLabs generation
# ---------------------------------------------------------------------------

def generate_elevenlabs_pairing(
    label: str, narrator_id: str, narrator_name: str,
    dialogue_id: str, dialogue_name: str,
    segments: list[Segment], output_dir: Path, api_key: str,
) -> Path:
    out_file = output_dir / f"{label}.mp3"
    if out_file.exists():
        log.info("SKIP %s (exists)", label)
        return out_file

    groups = coalesce_segments(segments)
    tmp_dir = output_dir / f"_tmp_{label}"
    tmp_dir.mkdir(exist_ok=True)
    client = httpx.Client(timeout=120)
    parts: list[Path] = []

    for i, grp in enumerate(groups):
        voice_id = narrator_id if grp.voice_role == "narrator" else dialogue_id
        voice_name = narrator_name if grp.voice_role == "narrator" else dialogue_name

        if grp.break_before_ms:
            sil_file = tmp_dir / f"sil_{i:03d}.wav"
            sil_file.write_bytes(make_silence_wav(grp.break_before_ms))
            parts.append(sil_file)

        seg_file = tmp_dir / f"grp_{i:03d}.mp3"
        log.info("  %s grp %d/%d (%s → %s, %d chars)", label, i + 1, len(groups), grp.voice_role, voice_name, grp.char_count)

        resp = http_post_with_retry(
            client,
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
            json={
                "text": grp.text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.4},
            },
        )
        seg_file.write_bytes(resp.content)
        parts.append(seg_file)
        time.sleep(1.5)

    client.close()
    log.info("  Concatenating %d parts → %s", len(parts), out_file.name)
    concat_audio_files(parts, out_file)

    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()
    return out_file


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    segments = load_segments()
    total = sum(s.char_count for s in segments)
    log.info("Loaded %d segments, %d chars from chapter_01", len(segments), total)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Google ---
    google_key = get_credential("GOOGLE_TTS_API_KEY", "amr/google_api")
    if google_key:
        log.info("\n=== Google Chirp3-HD (4 pairings) ===")
        for label, (narrator, dialogue) in GOOGLE_PAIRINGS.items():
            log.info("Generating %s: narrator=%s, dialogue=%s", label, narrator, dialogue)
            generate_google_pairing(label, narrator, dialogue, segments, OUTPUT_DIR, google_key)
    else:
        log.warning("Skipping Google — no API key")

    # --- ElevenLabs ---
    el_key = get_credential("ELEVENLABS_API_KEY", "amr/elevenlabs_api")
    if el_key:
        log.info("\n=== ElevenLabs (4 pairings) ===")
        for label, voices in ELEVENLABS_PAIRINGS.items():
            n_id, n_name = voices["narrator"]
            d_id, d_name = voices["dialogue"]
            log.info("Generating %s: narrator=%s, dialogue=%s", label, n_name, d_name)
            generate_elevenlabs_pairing(label, n_id, n_name, d_id, d_name, segments, OUTPUT_DIR, el_key)
    else:
        log.warning("Skipping ElevenLabs — no API key")

    # --- Summary ---
    log.info("\n=== Done ===")
    log.info("Output: %s", OUTPUT_DIR)
    for f in sorted(OUTPUT_DIR.glob("*.mp3")):
        size_kb = f.stat().st_size / 1024
        log.info("  %s (%.0f KB)", f.name, size_kb)


if __name__ == "__main__":
    main()
