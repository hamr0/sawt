# Stash: POC-4 SSML Generation + Voice Testing
**Date:** 2026-02-10
**Branch:** main (commits: 373559f, 3b292bf, 488914e, 901f571)

## Completed Work

### POC-4 SSML Generation — DONE
- `src/audiobook/ssml/core.py` — 280 lines, full implementation
- `tests/audiobook/ssml/test_core.py` — 30 tests, all passing
- 12 books fully converted to SSML in `output/**/04_ssml/`
- Voice config: 7 Arabic dialects, M/F per dialect, `make_voice_config()`
- Context-aware breaks: 500ms paragraph, 300ms voice transition, 200ms dialogue exchange
- Coalesces consecutive same-voice segments under one `<voice>` tag

### Key Findings
1. **Azure 50 voice tag limit is 50 DISTINCT names**, not 50 total elements — no chapter splitting needed
2. **Mishkal diacritization makes pronunciation WORSE** — Azure's internal model (Dec 2024, 78% error reduction) conflicts with pre-diacritized text. Plain text stays.
3. **Azure "dialect" voices are MSA readers** — ar-EG, ar-SY, ar-SA etc are different speakers, not different pronunciation models. Exception: Syrian voices capture Levantine feel better.
4. **Egyptian voices most robotic**, Syrian most natural for literary Arabic

### Azure Voice Testing Results (Chapter 15, al-liss-wal-kilab)
Samples in `output/epub/al-liss-wal-kilab/05_audio/`:

| File | Config | User Verdict |
|------|--------|-------------|
| ch15_mf_egyptian.mp3 | Shakir(M,EG) + Salma(F,EG) | Most robotic |
| ch15_fm_syrian.mp3 | Amany(F,SY) + Laith(M,SY) | Most accurate Levant dialect |
| ch15_ff_saudi_lebanese.mp3 | Zariyah(F,SA) + Layla(F,LB) | Nice, could distinguish |
| ch15_mm_jordanian_iraqi.mp3 | Taim(M,JO) + Bassel(M,IQ) | Nice male voices, hard to distinguish |

### Azure Validation
- Small test: 200 OK, 23KB audio (2-voice SSML accepted)
- Full chapter 16: 200 OK, 5.8MB audio
- Full chapter 15 (dialogue-heavy, 86 segments): 200 OK, ~6-7MB per combo
- Credentials via `pass amr/azure_tts`, parsed on the fly, never stored

---

## POC-4a: TTS Provider Comparison — DONE

### Script: `scripts/poc4a_tts_comparison.py`
- Compares Azure, Google, OpenAI, ElevenLabs on same chapter (ch15)
- Segment coalescing for single-voice APIs (86 segments → 49 groups)
- Fixes short-segment language detection issues for non-SSML providers
- Retry logic for rate limits and connection resets
- Output: `output/epub/al-liss-wal-kilab/05_audio/poc4a/`

### Provider Comparison (Chapter 15, 4026 chars, 86 segments)

| Provider | Size | Time | Ch15 Cost | Book Cost | Verdict |
|----------|------|------|-----------|-----------|---------|
| Azure (Syrian Neural) | 6.0MB | 3.4s | $0.06 | $1.16 | Baseline, native SSML, correct Arabic |
| Google (WaveNet) | 3.3MB | 34.7s | $0.06 | $1.16 | Correct pronunciation, flat/robotic |
| Google (Chirp3-HD) | — | — | ~$0.06 | ~$1.16 | **New gen, much better than WaveNet** |
| OpenAI (tts-1-hd) | 3.2MB | 170s | $0.12 | $2.17 | Lively but mispronounces Arabic, no Arabic voices |
| ElevenLabs (multilingual_v2) | 5.3MB | 156s | $1.21 | $21.74 | Best quality with Arabic voices, expensive |

### Key POC-4a Findings
1. **OpenAI has NO Arabic-specific voices** — all 9 voices are English-primary multilingual. Produces English/gibberish on short Arabic segments. Not viable.
2. **ElevenLabs needs Arabic voices from shared library** — default English voices (Adam/Sarah) produce gibberish. Arabic community voices are excellent.
3. **Google Chirp3-HD is a major upgrade** — 30 Arabic voices (vs 4 WaveNet), much more natural, same low cost.
4. **Segment coalescing essential** for non-SSML providers — merging consecutive same-type segments prevents language detection failures on short fragments.

### Credentials
```
pass amr/azure_tts          → AZURE_SPEECH_KEY (works)
pass amr/openai_api         → OPENAI_API_KEY (works, not viable for Arabic)
pass amr/google_api         → GOOGLE_TTS_API_KEY (works)
pass amr/elevenlabs_api     → ELEVENLABS_API_KEY (works, Creator plan)
```

---

## Voice Sampling Results

### ElevenLabs — Preferred Voices
Samples in `output/epub/al-liss-wal-kilab/05_audio/poc4a/elevenlabs/`
31 Arabic voices tested on same narrator paragraph.

**User-approved voices (10):**

| Voice | ID | Accent | Gender | Style | Notes |
|-------|-----|--------|--------|-------|-------|
| Sara | XTa3iQyMA6f1qrI4F6kZ | MSA | F | Soft, expressive, warm | Top pick |
| Alice | LjKPkQHpXCsWoy7Pjq4U | Egyptian | F | Smooth, charming, soft | Only Egyptian female |
| Razan | EUojVLG1QfxaqqH4ce6s | MSA | F | Academic, formal | Formal but good |
| Mona | tavIIPLplRB883FzWU0V | MSA | F | Attractive, expressive | Formal |
| Ghizlane | u0TsaWvt0v8migutHM3M | MSA | F | Smooth, distinctive, calm | Narrative |
| Salma | B5xxC4eQoOFJnY4R5XkI | Levantine | F | Friendly, clear | Narrative |
| Suhair | ML7jGRDg4E9hIl5qEm1Z | MSA | F | Warm, honest, clear | Narrative |
| Hanafi | DWMVT5WflKt0P8OPpIrY | Egyptian | M | — | Good |
| Moncellence | Jez3JdhBInQTvlAvDOWR | Egyptian | M | Clear, masculine | Good |
| Yahya | QRq5hPRAKf5ZhSlTBH6r | MSA | M | Deep, warm, expressive | Good |

**User preference pattern:**
- Tone: warm, soft, narrative — rejects loud/dramatic/energetic
- Accent: Egyptian + MSA preferred, Levantine OK, no Gulf
- Gender: strong female lean (7/10 picks female)
- Style: distinguishes "formal/narrative" (narrator) vs "soft/warm" (dialogue)

**Best pairings for the book:**

| Combo | Narrator | Dialogue | Rationale |
|-------|----------|----------|-----------|
| F/F #1 | Razan (MSA formal) | Sara (MSA soft) | Formal narrator vs soft dialogue |
| F/F #2 | Ghizlane (MSA narrative) | Alice (Egyptian) | Narrative tone vs Egyptian warmth |
| F/F #3 | Mona (MSA formal) | Salma (Levantine) | Formal vs intimate |
| M/F | Hanafi (Egyptian) | Sara (MSA soft) | Classic M narrator / F dialogue |

### Google — Preferred Voices
Samples in `output/epub/al-liss-wal-kilab/05_audio/poc4a/google/`
12 voices tested (5 Chirp3-HD female, 5 male, 2 WaveNet baseline).

**Chirp3-HD is a big improvement over WaveNet** — more natural, same cost.

**User-approved voices:**

| Voice | Gender | Notes |
|-------|--------|-------|
| ar-XA-Chirp3-HD-Sadachbia | M | Good choice |
| ar-XA-Chirp3-HD-Puck | M | Good choice |
| ar-XA-Chirp3-HD-Fenrir | M | Good choice |
| ar-XA-Chirp3-HD-Laomedeia | F | Good choice |
| ar-XA-Chirp3-HD-Achernar | F | Good choice |

**Google = cheaper option** — same quality tier as Azure, much cheaper than ElevenLabs, Chirp3-HD voices are good.

---

## Cost Comparison (Full Book, ~72K chars)

| Provider | Cost/1M chars | Book Cost | Quality Tier |
|----------|--------------|-----------|-------------|
| Google (Chirp3-HD) | ~$16 | ~$1.16 | Good, natural HD voices |
| Azure (Neural) | $16 | $1.16 | Good, native SSML multi-voice |
| OpenAI (tts-1-hd) | $30 | $2.17 | NOT VIABLE (no Arabic voices) |
| ElevenLabs (Creator) | ~$300 | ~$21.74 | Best quality, Arabic community voices |
| ElevenLabs (Scale) | ~$100 | ~$7.25 | Same quality, volume discount |

---

## Open Decisions
1. **Which provider for production?** Google Chirp3-HD (cheap + good) vs ElevenLabs (best quality, 20x cost)
2. **Which voice pair?** F/F or M/F — user leans F/F
3. **Full chapter test** with chosen pair before committing
4. When to close POC-4a and move to POC-5 (full audio generation)

## PLAN.md Updates Made
- Corrected 50 voice tag limit (distinct names, not total)
- Added context-aware break durations
- `.aurora/friction/` added to .gitignore (was 29K lines of noise)
