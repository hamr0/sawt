# ArabicTTS - Multi-Dialect Arabic Text-to-Speech

Production-ready IPA-first Arabic TTS. We own linguistic intelligence; voice is commodity.
5 dialects (MSA, Egyptian, Gulf, Levantine, Maghrebi). 329 tests passing. 96.30% syllabification accuracy.

## Current Status

| Metric | Value |
|--------|-------|
| Phase | MVP Complete, Polly Integration Active |
| Tests | 329/329 passing (100%) |
| Accuracy | 96.30% syllabification, 94.44% IPA |
| Speed | 3,059 words/second |

**Active:** Amazon Polly integration for production-quality audiobooks.

## Architecture

Processing Pipeline: Arabic Text -> Diacritization (mishkal) -> Syllabification (6 patterns) -> Phonological Processing (4 processors in order: Gemination -> Sun Letters -> Allophones -> Emphatic Spread) -> IPA -> X-SAMPA -> Audio (eSpeak dev / Polly prod)

**Critical:** masterTTS.json lookup happens AFTER phonological processing.

## Tech Stack

- Python 3.10+, mishkal 0.4.1 (diacritization)
- eSpeak NG (dev), Amazon Polly Zeina voice (prod, standard engine)
- Flask 3.0+ (REST API), pytest (329 tests)
- masterTTS.json: 1,030 phonetic entries, 5 dialects

## Essential Commands

```bash
pytest tests/ -v                                    # Run all tests
PYTHONPATH=. python3 scripts/demo_full_tts.py       # eSpeak demo
PYTHONPATH=. python3 scripts/test_polly_integration.py  # Polly test
python3 app.py                                      # Flask API (localhost:5000)
```

## Key Rules

DO: Run tests before commit, use masterTTS.json for lookups, follow processor order, use X-SAMPA for Polly
DONT: Skip phonological processing, modify processor order, commit without tests passing

## Known Issues

- Empty X-SAMPA: Falls back to plain Arabic (handled in polly.py)
- Zeina voice: Standard engine only, not neural
- AWS Free Tier: 5M chars/month for 12 months

## Documentation

Detailed docs in docs/KNOWLEDGE_BASE.md

| Topic | Location |
|-------|----------|
| Vision and business analysis | docs/00-context/vision.md |
| System architecture | docs/00-context/system-state.md |
| Tech stack decisions | docs/00-context/tech-stack.md |
| Product requirements | docs/01-product/prd.md |
| Polly integration | docs/02-features/polly/ |
| Testing guide | docs/04-process/testing.md |
| Quick start | docs/04-process/setup/QUICK_START.md |
| Decision history | docs/03-logs/decisions-log.md |
