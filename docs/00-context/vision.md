# Vision

## What We're Building

An Arabic audiobook production pipeline that converts raw books (PDF/TXT) into two-voice audiobooks using Azure Neural TTS.

## Why

- Arabic audiobook market is severely underserved despite massive growth ($237.6M in 2024 → $1.24B by 2030, 31.5% CAGR)
- No accessible tooling exists for Arabic audiobook production with voice differentiation
- Two-voice narration (narrator + dialogue) dramatically improves listening experience over single-voice

## Core Insight

Text processing IS the product. Once text is correctly broken into narration and dialogue segments, SSML generation and TTS are commodity operations. The hard problems are:

1. **Extracting clean text** from PDF/TXT with correct encoding and paragraph structure
2. **Detecting chapter boundaries** with safe splitting at paragraph breaks
3. **Classifying narration vs dialogue** — the primary differentiator

Azure's neural voices handle pronunciation better than any phoneme-level control. Our job is text structure, not pronunciation.

## What We're NOT Building

- An IPA phonological pipeline (tried it — 329 tests, unusable audio output, archived)
- A dialect-switching system (a book is a book — one voice profile per book)
- A real-time TTS service or API
- An LLM-heavy pipeline (code-first, LLM only where it demonstrably helps)

## Product Tiers

| Tier | Description | Status |
|------|-------------|--------|
| Two-voice | Narrator + dialogue voices | Primary goal |
| Multi-voice | Per-character voice assignment | Stretch goal |
| Emotion/prosody | SSML prosody tags for emphasis | Future layer |

## Success Looks Like

A complete two-voice audiobook from a real Arabic book where:
- Narration and dialogue are clearly distinguished
- Voice switches feel natural
- No text is missing
- Repeatable on a second book with different formatting
