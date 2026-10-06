#!/usr/bin/env python3
"""Generate two-voice Gemini TTS samples for comparison with the POC-4b pairings.

Book: tharthara-fawq-al-nil (Chitchat on the Nile), Chapter 1 — same chapter and
same FF voices (Sulafat narrator, Leda dialogue) as google_FF.mp3, so the only
variable is the model. A second "styled" variant adds per-speaker delivery
direction via speech_metadata.style.

Gemini TTS is natively two-speaker: narrator and dialogue go in one request,
like Azure SSML, instead of per-segment calls stitched with silence.
"""
from __future__ import annotations

import base64
import io
import logging
import re
import subprocess
import wave

import httpx

from generate_voice_pairings import (
    OUTPUT_DIR,
    CoalescedGroup,
    coalesce_segments,
    get_credential,
    http_post_with_retry,
    load_segments,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

MODEL = "gemini-3.8-flash-tts"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
MAX_REQUEST_CHARS = 1500  # ~2.5 min audio, well under the 16K output-token cap
CHUNK_GAP_MS = 500        # silence between requests (paragraph-boundary break)
SPLIT_GAP_MS = 200        # silence at seams introduced by content-block splitting
SENTENCE_END_RE = re.compile(r"(?<=[.!؟?])\s+")


class ContentBlocked(Exception):
    """Gemini refused the input (code=content_blocked)."""

VOICES = {"narrator": "Sulafat", "dialogue": "Leda"}
SPEAKER_LABEL = {"narrator": "Narrator", "dialogue": "Dialogue"}

STYLES = {
    "narrator": "warm, calm, measured audiobook narration; soft and unhurried",
    "dialogue": "natural, soft conversational delivery; gentle, not dramatic",
}

VARIANTS = {
    "gemini_FF": None,
    "gemini_FF_styled": STYLES,
}


def chunk_groups(groups: list[CoalescedGroup]) -> list[list[CoalescedGroup]]:
    """Pack whole groups into requests up to MAX_REQUEST_CHARS; never split a group."""
    chunks: list[list[CoalescedGroup]] = []
    size = 0
    for g in groups:
        if chunks and size + g.char_count <= MAX_REQUEST_CHARS:
            chunks[-1].append(g)
            size += g.char_count
        else:
            chunks.append([g])
            size = g.char_count
    return chunks


def build_request(chunk: list[CoalescedGroup], styles: dict[str, str] | None) -> dict:
    content = []
    for g in chunk:
        meta = {"type": "speech_metadata", "speaker": SPEAKER_LABEL[g.voice_role]}
        if styles:
            meta["style"] = styles[g.voice_role]
        content.append({"type": "text", "text": g.text, "annotations": [meta]})
    return {
        "model": MODEL,
        "input": [{"type": "user_input", "content": content}],
        "response_format": {"type": "audio"},
        "generation_config": {
            "speech_config": {
                "mode": "conversational",
                "speakers": [
                    {"speaker": SPEAKER_LABEL[role], "voice": voice}
                    for role, voice in VOICES.items()
                ],
            }
        },
    }


def extract_pcm(response: dict) -> bytes:
    audio = [
        c for step in response.get("steps", []) if step.get("type") == "model_output"
        for c in step.get("content", []) if c.get("type") == "audio"
    ]
    if not audio:
        raise RuntimeError(f"No audio in response (status={response.get('status')})")
    with wave.open(io.BytesIO(base64.b64decode(audio[-1]["data"]))) as w:
        if (w.getframerate(), w.getnchannels(), w.getsampwidth()) != (24000, 1, 2):
            raise RuntimeError("Unexpected audio format — expected 24kHz mono 16-bit")
        return w.readframes(w.getnframes())


def synthesize(client: httpx.Client, chunk: list[CoalescedGroup],
               styles: dict[str, str] | None, api_key: str) -> tuple[bytes, int]:
    try:
        resp = http_post_with_retry(
            client, ENDPOINT, headers={"x-goog-api-key": api_key},
            json=build_request(chunk, styles),
        ).json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400 and "content_blocked" in e.response.text:
            raise ContentBlocked from e
        raise
    return extract_pcm(resp), resp.get("usage", {}).get("total_output_tokens", 0)


def split_in_half(chunk: list[CoalescedGroup]) -> list[list[CoalescedGroup]] | None:
    """Halve a chunk at a group boundary, or a lone group at a sentence boundary."""
    if len(chunk) > 1:
        mid = len(chunk) // 2
        return [chunk[:mid], chunk[mid:]]
    g = chunk[0]
    sentences = SENTENCE_END_RE.split(g.text)
    if len(sentences) < 2:
        return None
    mid = len(sentences) // 2
    halves = [" ".join(sentences[:mid]), " ".join(sentences[mid:])]
    return [[CoalescedGroup(g.voice_role, h, len(h), 1, None)] for h in halves]


def synthesize_with_fallback(client, chunk, styles, api_key, stats, depth=0) -> tuple[bytes, int]:
    """On a content block, split and retry each half; seams get a short gap."""
    try:
        return synthesize(client, chunk, styles, api_key)
    except ContentBlocked:
        parts = split_in_half(chunk)
        if parts is None:
            raise RuntimeError(f"Single sentence blocked: {chunk[0].text[:80]!r}")
        stats["splits"] += 1
        log.warning("  %scontent_blocked on %d chars — splitting", "  " * depth,
                    sum(g.char_count for g in chunk))
        gap = b"\x00\x00" * int(24000 * SPLIT_GAP_MS / 1000)
        pcm, tokens = bytearray(), 0
        for part in parts:
            audio, t = synthesize_with_fallback(client, part, styles, api_key, stats, depth + 1)
            if pcm:
                pcm += gap
            pcm += audio
            tokens += t
        return bytes(pcm), tokens


def generate_variant(
    label: str, styles: dict[str, str] | None,
    chunks: list[list[CoalescedGroup]], api_key: str,
) -> None:
    gap = b"\x00\x00" * int(24000 * CHUNK_GAP_MS / 1000)
    pcm = bytearray()
    output_tokens = 0
    stats = {"splits": 0}
    with httpx.Client(timeout=300) as client:
        for i, chunk in enumerate(chunks, 1):
            chars = sum(g.char_count for g in chunk)
            audio, tokens = synthesize_with_fallback(client, chunk, styles, api_key, stats)
            secs = len(audio) / 48000
            output_tokens += tokens
            log.info("  [%s] chunk %d/%d: %d chars → %.1fs (%.1f chars/s)",
                     label, i, len(chunks), chars, secs, chars / secs)
            if pcm:
                pcm += gap
            pcm += audio
    if stats["splits"]:
        log.warning("  [%s] %d content-block split(s) needed", label, stats["splits"])

    wav_path = OUTPUT_DIR / f"{label}.wav"
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(bytes(pcm))
    mp3_path = OUTPUT_DIR / f"{label}.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav_path), "-c:a", "libmp3lame", "-q:a", "2", str(mp3_path)],
        capture_output=True, check=True,
    )
    wav_path.unlink()
    log.info("  [%s] → %s (%.1fs, %d output tokens)",
             label, mp3_path.name, len(pcm) / 48000, output_tokens)


def main():
    api_key = get_credential("GEMINI_API_KEY", "amr/gemini_api")
    if not api_key:
        raise SystemExit("No Gemini API key (GEMINI_API_KEY or pass amr/gemini_api)")

    segments = load_segments()
    groups = coalesce_segments(segments)
    chunks = chunk_groups(groups)
    log.info("%d segments → %d groups → %d requests (model %s)",
             len(segments), len(groups), len(chunks), MODEL)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for label, styles in VARIANTS.items():
        log.info("Generating %s (narrator=%s, dialogue=%s, styled=%s)",
                 label, VOICES["narrator"], VOICES["dialogue"], bool(styles))
        generate_variant(label, styles, chunks, api_key)


if __name__ == "__main__":
    main()
