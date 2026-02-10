# POC-4 Results: SSML Generation + Voice Selection

**Date completed:** February 2026
**Code:** `src/audiobook/ssml/core.py` (280 lines)
**Tests:** `tests/audiobook/ssml/test_core.py` — 30 tests, all passing
**Script:** `scripts/poc4a_tts_comparison.py` — multi-provider TTS comparison

---

## Summary

POC-4 converts verified segment CSVs from POC-3 into Azure-ready SSML files with two-voice dialect-matched output. All 12 books fully converted.

POC-4a extends with a multi-provider TTS comparison (Azure, Google, OpenAI, ElevenLabs) to find the best cost/quality balance for Arabic audiobook production.

---

## POC-4: SSML Generation — DONE

### What was built

- `build_ssml()` — pure function, segments → valid Azure SSML string
- `VoiceConfig` — typed dict: `book_dialect`, `narrator_voice`, `dialogue_voice`
- `make_voice_config(dialect, narrator_gender)` — config factory, 7 Arabic dialects
- Coalesces consecutive same-voice segments under one `<voice>` tag (reduces voice tag count)
- Context-aware breaks between segments:
  - `500ms` — narrator→narrator (paragraph boundary)
  - `300ms` — narrator↔dialogue (voice transition)
  - `200ms` — dialogue→dialogue (rapid exchange)

### Output

- 12 books fully converted: `output/**/04_ssml/chapter_*.ssml`
- Per-book summary CSV: `04_ssml/ssml_summary.csv`

### Key finding: Azure 50 voice tag limit

The Azure SSML limit of 50 voice tags refers to 50 **distinct voice names**, not 50 total `<voice>` elements. Two-voice output uses only 2 distinct names — no chapter splitting needed regardless of segment count.

---

## POC-4a: TTS Provider Comparison — DONE

### Test setup

- **Test chapter:** Chapter 15, al-liss-wal-kilab (Naguib Mahfouz)
- **Segments:** 86 segments, 4,026 chars, dialogue-heavy
- **Providers tested:** Azure, Google, OpenAI, ElevenLabs
- **Output:** `output/epub/al-liss-wal-kilab/05_audio/poc4a/`

### Provider results

| Provider | Voice | Size | Time | Ch15 Cost | Book Cost (121K) | Verdict |
|----------|-------|------|------|-----------|-----------------|---------|
| Azure (Syrian Neural) | Laith + Amany | 6.0MB | 3.4s | $0.06 | $1.93 | Baseline, native SSML, correct Arabic |
| Google (WaveNet) | ar-XA-Wavenet-B + A | 3.3MB | 34.7s | $0.06 | $1.93 | Correct pronunciation, flat/robotic |
| Google (Chirp3-HD) | Various | — | — | $0.12 | $3.63 | Much better than WaveNet, 2x cost |
| OpenAI (tts-1-hd) | onyx + nova | 3.2MB | 170s | $0.12 | — | NOT VIABLE — no Arabic voices |
| ElevenLabs (multilingual_v2) | Arabic voices | 5.3MB | 156s | $0.40 | $11.98 | Best quality, ~3x Google Chirp3-HD |

### Key findings

**1. OpenAI has no Arabic voices — not viable.**
All 9 OpenAI voices (alloy, echo, fable, onyx, nova, shimmer, ash, ballad, coral) are English-primary multilingual. Short Arabic segments produce English or gibberish. Not suitable for Arabic audiobooks.

**2. Segment coalescing is essential for non-SSML providers.**
86 segments → 49 coalesced groups. Short Arabic fragments (31 of 86 under 20 chars) cause language detection failures in providers without SSML language hints. Merging consecutive same-type segments prevents this.

**3. Azure "dialect" voices are MSA readers, not dialect speakers.**
ar-EG, ar-SY, ar-SA etc. are different speakers reading MSA, not different pronunciation models. Exception: Syrian voices capture Levantine literary feel better than Egyptian voices.

**4. Egyptian Azure voices are most robotic, Syrian most natural.**
For literary Arabic (Mahfouz), Syrian voices (Laith/Amany) sound better despite being off-dialect.

**5. Google Chirp3-HD is a major upgrade.**
30 Arabic voices (vs 4 WaveNet). Much more natural. Same low cost ($16/1M chars). Good cheaper alternative to ElevenLabs.

**6. Mishkal diacritization makes pronunciation worse.**
Azure's internal Arabic model (Dec 2024, 78% error reduction) conflicts with pre-diacritized text. Plain text produces better results.

---

## Voice Sampling

### Azure voice combos tested (Chapter 15)

| Config | Voices | User verdict |
|--------|--------|-------------|
| M/F Egyptian | Shakir + Salma (ar-EG) | Most robotic |
| F/M Syrian | Amany + Laith (ar-SY) | Most natural, best Levantine feel |
| F/F Saudi+Lebanese | Zariyah (ar-SA) + Layla (ar-LB) | Nice, distinguishable |
| M/M Jordanian+Iraqi | Taim (ar-JO) + Bassel (ar-IQ) | Nice male voices, hard to distinguish |

### ElevenLabs — preferred voices (31 tested)

Samples in `output/epub/al-liss-wal-kilab/05_audio/poc4a/elevenlabs/`

**User-approved (10 voices):**

| Voice | ID | Accent | Gender | Style |
|-------|----|--------|--------|-------|
| Sara | XTa3iQyMA6f1qrI4F6kZ | MSA | F | Soft, expressive, warm — top pick |
| Alice | LjKPkQHpXCsWoy7Pjq4U | Egyptian | F | Smooth, charming, soft |
| Razan | EUojVLG1QfxaqqH4ce6s | MSA | F | Academic, formal |
| Mona | tavIIPLplRB883FzWU0V | MSA | F | Attractive, expressive |
| Ghizlane | u0TsaWvt0v8migutHM3M | MSA | F | Smooth, distinctive, calm |
| Salma | B5xxC4eQoOFJnY4R5XkI | Levantine | F | Friendly, clear |
| Suhair | ML7jGRDg4E9hIl5qEm1Z | MSA | F | Warm, honest, clear |
| Hanafi | DWMVT5WflKt0P8OPpIrY | Egyptian | M | Good narrator voice |
| Moncellence | Jez3JdhBInQTvlAvDOWR | Egyptian | M | Clear, masculine |
| Yahya | QRq5hPRAKf5ZhSlTBH6r | MSA | M | Deep, warm, expressive |

**User preference pattern:**
- **Tone:** Warm, soft, narrative — rejects loud/dramatic/energetic
- **Accent:** Egyptian + MSA preferred, Levantine OK, no Gulf
- **Gender:** Strong female lean (7/10 picks female)
- **Style:** Distinguishes "formal/narrative" (narrator) vs "soft/warm" (dialogue)

**Recommended pairings:**

| Combo | Narrator | Dialogue | Rationale |
|-------|----------|----------|-----------|
| F/F #1 | Razan (MSA formal) | Sara (MSA soft) | Formal narrator vs soft dialogue |
| F/F #2 | Ghizlane (MSA narrative) | Alice (Egyptian) | Narrative tone vs Egyptian warmth |
| F/F #3 | Mona (MSA formal) | Salma (Levantine) | Formal vs intimate |
| M/F | Hanafi (Egyptian) | Sara (MSA soft) | Classic M narrator / F dialogue |

### Google — preferred voices (12 tested)

Samples in `output/epub/al-liss-wal-kilab/05_audio/poc4a/google/`

Chirp3-HD is a significant upgrade over WaveNet — more natural, same cost.

**User-approved:**

| Voice | Gender | Notes |
|-------|--------|-------|
| ar-XA-Chirp3-HD-Sadachbia | M | Good choice |
| ar-XA-Chirp3-HD-Puck | M | Good choice |
| ar-XA-Chirp3-HD-Fenrir | M | Good choice |
| ar-XA-Chirp3-HD-Laomedeia | F | Good choice |
| ar-XA-Chirp3-HD-Achernar | F | Good choice |

---

## Cost Comparison

### Actual pricing (per 1M characters)

| Provider | Voice tier | Cost/1M chars | Source |
|----------|-----------|---------------|--------|
| Google Cloud | Standard | $4 | cloud.google.com/text-to-speech/pricing |
| Google Cloud | WaveNet / Neural2 | $16 | cloud.google.com/text-to-speech/pricing |
| Google Cloud | **Chirp3-HD** | **$30** | cloud.google.com/text-to-speech/pricing |
| Azure | Neural | $16 | azure.microsoft.com/pricing/details/cognitive-services/speech-services |
| ElevenLabs | Multilingual v2 (API) | $99 | elevenlabs.io/pricing/api |
| ElevenLabs | Creator overage | $300 ($0.30/1K) | elevenlabs.io/pricing |
| ElevenLabs | Pro overage | $240 ($0.24/1K) | elevenlabs.io/pricing |
| ElevenLabs | Scale overage | $180 ($0.18/1K) | elevenlabs.io/pricing |
| OpenAI | tts-1-hd | $30 | **Not viable** (no Arabic voices) |

### Per-book cost: al-liss-wal-kilab (121K chars actual)

| Provider | Calculation | Book cost |
|----------|-------------|-----------|
| Azure Neural | 121K × $16/1M | $1.93 |
| Google WaveNet | 121K × $16/1M | $1.93 |
| **Google Chirp3-HD** | 121K × $30/1M | **$3.63** |
| **ElevenLabs** (Creator, marginal) | 21K overage × $0.30/1K | **$6.30** (+ $22/mo base) |
| ElevenLabs (API rate) | 121K × $99/1M | $11.98 |

### ElevenLabs plan comparison

ElevenLabs uses credits: 1 credit = 1 character for Multilingual v2.

| Plan | Monthly cost | Chars/mo | Best for |
|------|-------------|----------|----------|
| Creator | $22/mo (annual) | 100K | 1 small book/mo, overage on larger books |
| Pro | $99/mo (annual) | 500K | 1-4 books/mo depending on size |
| Scale | $330/mo (annual) | 2M | Batch production, 5-16 books/mo |

### Catalog projection: 5 Mahfouz novels (1.69M chars total)

| Book | Chars | Google Chirp3-HD | ElevenLabs ($99/1M) |
|------|-------|-----------------|---------------------|
| al-liss-wal-kilab | 121K | $3.63 | $11.98 |
| tharthara-fawq-al-nil | 146K | $4.38 | $14.45 |
| zuqaq-al-midaqq | 383K | $11.49 | $37.92 |
| bidaya-wa-nihaya | 474K | $14.22 | $46.93 |
| awlad-haretna | 563K | $16.89 | $55.74 |
| **Total** | **1.69M** | **$50.61** | **$167.02** |

ElevenLabs plan cost for 5 books (1.69M chars):
- Creator ($22/mo): 17 months + heavy overage = **~$730**
- Pro ($99/mo): 4 months = **$396**
- Scale ($330/mo): 1 month = **$330** (best if batched)

**Google Chirp3-HD vs ElevenLabs gap: ~3x** (not 20x as originally estimated).

---

## Multi-voice approach per provider

| Provider | Multi-voice method |
|----------|--------------------|
| Azure | Native SSML `<voice>` tags — narrator and dialogue voices in single request |
| Google | Per-group generation + silence insertion + ffmpeg concatenation |
| ElevenLabs | Per-group generation + silence insertion + ffmpeg concatenation |
| OpenAI | Not applicable (not viable for Arabic) |

Non-SSML providers require segment coalescing (merge consecutive same-type segments) before per-group generation. Context-aware silence between groups matches SSML break durations: 500ms paragraph, 300ms transition, 200ms dialogue.

---

## Credentials

All API keys managed via `pass` (password manager), parsed on the fly, never stored in code or env files.

```
pass amr/azure_tts      → AZURE_SPEECH_KEY
pass amr/google_api     → GOOGLE_TTS_API_KEY
pass amr/elevenlabs_api → ELEVENLABS_API_KEY
pass amr/openai_api     → OPENAI_API_KEY (not viable)
```

---

## Open decisions for POC-5

1. **Which provider for production?** Google Chirp3-HD ($3.63/book, good) vs ElevenLabs ($12/book API, best quality, ~3x cost)
2. **Which ElevenLabs plan?** Pro ($99/mo, 500K chars) for steady production, Scale ($330/mo, 2M chars) for batch runs
3. **Which voice pair?** F/F preferred — full chapter test with chosen pair before committing
4. **Audio generation pipeline** — chapter-by-chapter, per-book output to `05_audio/`
