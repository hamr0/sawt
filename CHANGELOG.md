# Changelog

All notable changes to sawt are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

Versions are **retro-fitted**: the codebase is a continuation of an
older Arabic TTS project (rebranded to Sawt at commit `472c3ce` on
2026-02-06). The version numbers absorb that history rather than
restarting from zero. Two eras:

- **0.0.x – 0.10.x — ArabicTTS / IPA pipeline era** (2025-08 → 2025-12).
  Multi-dialect Arabic TTS via syllabifier + IPA pronunciation
  dictionary + AWS Polly + early Azure character-detection pipeline.
  Archived to `archive/` at the rebrand.
- **0.11.x onward — Sawt audiobook production era** (2026-02 → ).
  Two-voice Arabic audiobooks from raw book files via the four-POC
  pipeline (ingestion → chapter split → segmentation → SSML/TTS).

## [Unreleased]

### Added
- GitHub Actions CI (`.github/workflows/ci.yml`): pytest on push/PR to `main` (Python 3.14, node 22) plus a gitleaks scan of the new commits.
- `corpus` pytest marker for tests that need the git-ignored `data/books` corpus; `tests/fixtures/sample.txt` (CC BY 4.0 excerpt) so the TXT ingest tests run without it.
- `SAWT_CI=1` skip ceiling: CI fails if any non-`corpus` test skips.
- `.python-version`, `pyproject.toml` (`[project]`, pytest markers), `.gitleaksignore` (historical dead AWS key).

## [0.16.0] — 2026-10-06

### Added

- **Local UI shell (PRD module 2).** `python -m src.audiobook.ui` serves a stdlib-only page on 127.0.0.1 (Host-header checked): job cards, new-job panel with inline overwrite warning, live run log with retry, history, rename, light/dark theme. Runs execute one at a time on a worker thread.

- **Artifacts tab, file viewer and open-folder (PRD module 3).** Each job's Artifacts tab lists its numbered step folders as collapsible blocks (all start collapsed; expansion is remembered across tab and job switches). Headers show the newest file's local date and a display name; steps not yet produced appear as greyed, non-expandable rows. Subfolders get a "dir/ · N files" subheader and files render as a responsive "name (size)" grid. A built-in viewer shows text and CSV files (short CSV columns do not wrap; lines with no strong direction default to RTL), and an open-folder button launches the system file manager (child processes are reaped).

- **Folder pick list.** Pointing the new-job panel at a folder scans it (`GET /api/scan`) into a row list with tick box, editable job name, status and skipped files; `[ start N books ]` runs only the ticked rows. `POST /api/runs` accepts `{"books": [...]}` and re-validates every path and name. Default job names avoid taken names (`<stem>`, `<stem>-2`, ...), also used as the single-file placeholder.

- **Job search and two-line status cards**, and a job heading that uses the card status.

- **Stop, delete and queue view.** The Run tab has an action row: stop a run between steps (the run ends "stopped" and stays retryable), delete a job, and see waiting jobs as queued placeholder cards (`POST /api/stop`, `POST /api/jobs/<name>/delete`).

- **Re-attach an orphaned job folder.** A `_sawt` output folder whose history entry is gone can be attached back to the job list from the UI.

- **Orphan-folder overwrite confirm.** A new job whose output folder already holds step output (for example a job deleted from history) now gets the same overwrite warning and confirm as an existing job, in the CLI and in both UI run forms, instead of being cleared silently.

- **Safe shared job history.** `jobs.json` is written as a locked read-merge-write matched by a stable job id (runs carry ids too), so a rename made mid-run survives, a delete mid-run is not resurrected, and one writer no longer overwrites another's runs. Delete is no longer refused while another job runs. Book sources are stored and matched by resolved path, and job names must be printable and at most 100 characters.

- **Bundled offline font and layout polish.** Courier Prime (SIL OFL) is bundled in `ui/static/` and served from an allow-listed `GET /static/<name>`; the Google Fonts link and CSP hosts are gone (`font-src 'self'`), so the UI works offline. The job pane is wider (300px to 360px), the header has a tagline, Start enables as the path is typed, path segments and names are bidi-isolated, and error messages are worded for the UI.

- **Runner CLI (PRD module 0).** `python -m src.audiobook.runner <book-or-folder>` chains ingest → chapters → dialogue (→ SSML with `--ssml`) into `<book dir>/<job name>_sawt/`, stops only on an error or at the pre-audio gate, retries from the failed step using only files on disk (`--retry`), and records every run in `~/.config/sawt/jobs.json` (`SAWT_HOME` overrides; `--list`, `--rename`, `--import-existing`). `ingest()` gained an optional `ingestion_dir` argument so the runner can choose the output folder.

- **POC-4c: Gemini TTS evaluated and chosen as the production provider.**
  `scripts/generate_gemini_sample.py` renders tharthara-fawq-al-nil
  chapter 1 with `gemini-3.8-flash-tts` in native two-speaker mode
  (Sulafat narrator + Leda dialogue, the same voices as the Google
  Chirp3-HD FF pair). It writes two variants: plain, and styled via
  `speech_metadata.style` ("warm, calm, measured" narration; "soft, not
  dramatic" dialogue). In listening tests the styled variant beat
  ElevenLabs, with pronunciation judged ~90%+. Measured cost is ~3.6 output
  tokens per character: ~$54 for the 5 Mahfouz novels at standard or 2027
  batch pricing, against ~$167 for ElevenLabs. Gemini's content filter
  deterministically blocks some violent literary passages in context
  (each sentence passes alone), so the script halves on `content_blocked`
  and retries. Findings, costs and the decision are in POC-4 results;
  POC-5's open provider and voice questions are now closed.

### Changed

- **Docs consolidated into one PRD and one learnings doc.**
  `docs/product/prd.md` (now including the local UI + runner spec) and
  `docs/product/learnings.md` replace the old PLAN, PRD, vision,
  assumptions, knowledge base and six split wiki pages, which are
  archived; logs flattened into `docs/logs/`.
- **Docs reorganized into product / wiki / logs / archive** via
  docs-builder. 24 files moved and 59 inbound links repaired; the stale
  `system-state.md` was archived. `docs/index.md` is now the generated map
  of every doc. The 1,019-line `PLAN.md` was split into seven themed
  pages: the core execution plan stays at `docs/product/PLAN.md`, the
  themes are in `docs/wiki/`, and the original is archived byte-identical
  at `docs/archive/PLAN.md`.

- **`CLAUDE.md` rewritten against the built codebase.** The old file had
  drifted from reality: it claimed 126 tests (the suite has 259), pointed
  at `docs/02-features/azure-audiobooks/PLAN.md` and
  `.claude/memory/AGENT_RULES.md` (both moved), described the project as
  Azure-only (it is multi-provider — Google Chirp3-HD primary, ElevenLabs
  premium, Azure baseline), omitted POC-5 audio generation as the next
  stage, and listed `shared/` as active when it and `voice_pool/` are
  docstring-only stubs. Now also records the numbered output contract
  (`01_ingestion` → `05_audio`), the `from .core import *` plus
  explicit private-helper export convention, and a domain-knowledge
  section covering the decisions that read as bugs but are deliberate
  (guillemets are not dialogue, no continuation heuristic, non-fiction
  false positives by design, PDF permanently out of scope, 25K chars
  derived from the 64KB Azure SSML ceiling). Memory and agent-rules
  pointers appended as `@` imports; these resolve from local, gitignored
  `.claude/` state and are intentionally not shipped with the repo.

- **Agent/IDE scratch gitignored and de-tracked.** `.gitignore` now default-denies every dot-directory (`.*/`), re-admitting only what ships (`.github/`). Per-machine agent/IDE state (`.claude/`, `.litectx/`, `.idea/`, …) regenerates locally and only added noise and churn; any already-committed copies are removed from tracking (local files kept on disk). Repo hygiene only.

- **Test isolation guard.** `tests/conftest.py` pins `SAWT_HOME` for the whole session and asserts at the end that the real `~/.config/sawt/jobs.json` is unchanged; the UI test client waits for the worker to go idle before teardown.
- **AWS keys removed from the archive docs.** The Polly guides in `docs/archive` now carry placeholders instead of real keys (the account behind the leaked key is deactivated; git history is left as is), and AWS's documentation example key is replaced so secret scans stay quiet.

### Infrastructure
- Apache-2.0 LICENSE file added.
- Root `package.json` added (private; for tooling/metadata, not npm
  publish — this is a Python project).
- README badges (version + license, plato-style; version hardcoded
  because the repo is private and shields.io's auto-version endpoint
  can't read private repos).

## [0.15.0] — 2026-02-11

Multi-provider voice testing across Azure Neural TTS / AWS Polly /
others to validate the audiobook-best-practices research baseline.
ArabicTTS reference code archived under `archive/` so the audiobook
codebase reads cleanly without the IPA-era apparatus. Docs
reorganized to match the post-rebrand pipeline structure.

### Added
- `scripts/poc4a_tts_comparison.py` — multi-provider voice
  comparison harness covering chapter-15 dialogue/narration cuts.
- `sampling/` — A/B reference cuts (diacritized vs plain;
  Saudi/Lebanese, Syrian, Egyptian, Jordanian/Iraqi voice
  pairings).
- Audiobook best-practices research notes (provider trade-offs,
  per-dialect voice availability).

### Changed
- Repo structure consolidated under `src/`, `scripts/`, `tests/`,
  `data/`, `docs/`. Old `app.py`, Flask templates, and IPA
  per-dialect dictionaries moved to `archive/`.
- `docs/` reorganized into the 5-tier hierarchy
  (`00-context`, `01-product`, `02-features`, `03-tasks`,
  `04-process`).

## [0.14.0] — 2026-02-09

POC-4 SSML generation lands: two-voice output with dialect-matched
Azure Neural voices wired into the chapter pipeline. POC-1, POC-2,
and POC-3a (binary narration/dialogue classification) are formally
marked production ready. The multi-voice stretch goal (POC-3b /
Phase B) is **closed** — Azure Arabic ships only 2 voices per
dialect, not enough to credibly distinguish characters without
crossing dialects mid-book.

### Added
- POC-4 SSML two-voice generator: per-segment voice tag selection,
  dialect-matched narrator + dialogue voice pairs, prosody
  adjustments per segment type.
- Context-aware SSML breaks between segment types (narration ↔
  dialogue ↔ chapter boundary).
- Voice-pairing generator (`scripts/generate_voice_pairings.py`)
  and sample-generation script
  (`scripts/generate_voice_samples.py`).

### Changed
- POC-1, POC-2, POC-3a marked production ready in pipeline status
  table; POC labels removed from completed modules.
- Numbered output folders; guillemet-splitting and continuation
  logic removed in favor of simpler segment-boundary rules; per-run
  summary CSV emitted.

### Closed
- POC-3b (multi-voice character attribution) — Phase B closed.
  Azure Arabic has only 2 voices per dialect. Documented in PRD
  non-goals.

### Notes
- Azure 50-voice-tag-per-document limit clarified as **distinct
  names**, not total elements — relevant for long chapters that
  re-cite the same two voices many times.

## [0.13.0] — 2026-02-06

**Rebrand: ArabicTTS → Sawt (صوت).** Tagline: *كل كتاب له صوت* —
"every book has a voice." Fiction-only scope locked in: non-fiction
(textbooks, essays, technical) is out of v1 because their structure
(footnotes, tables, equations, citations) breaks the
chapter/dialogue model the pipeline is built around.

### Changed
- Project identity: ArabicTTS → Sawt. README, package metadata, and
  PyCharm workspace renamed.
- Product scope narrowed to fiction. PRD updated with explicit
  non-fiction exclusion + reasoning.

## [0.12.0] — 2026-02-05

POC-1 (book ingestion) and POC-2 (chapter detection + splitting)
both complete. Ingestion handles EPUB / DOCX / TXT, normalizes
Arabic Presentation Forms to standard Arabic, strips publisher
noise, and emits clean text + paragraph-inventory CSV. Chapter
splitting handles numbered, named, and structural patterns, plus
the no-explicit-chapters fallback (split by size at paragraph
boundaries) and the Azure character-limit splitter.

### Added
- POC-1: EPUB / DOCX / TXT ingestion → normalized text +
  paragraph-inventory CSV.
- POC-2: chapter detection (numbered, named, structural) + size-
  based splitter at paragraph boundaries + Azure-limit chunker.
- Review-text outputs and review→CSV sync for dialogue segments.
- Dialogue-segment review markers (`«»`, later switched to
  `//` `\\` for reviewer ergonomics).

### Changed
- POC-1 / POC-2 modules polished: logging, type hints, named
  constants, isolated package boundaries.
- Marker priority: colons take precedence over guillemets when
  both could trigger a dialogue segment.

## [0.11.0] — 2026-02-05

**Pivot.** The IPA / phonetic-pipeline approach is archived. The
project re-focuses on *audiobook production from raw book files* —
the original syllabifier work was solving a problem one layer
deeper than the audiobook user actually needs. Azure Neural TTS
handles pronunciation natively for the dialects in scope; what's
missing is the **book-shape** layer (ingestion, chapter split,
two-voice segmentation, SSML).

### Added
- Audiobook production scaffold: `src/`, `scripts/`, `data/`,
  `tests/`, `docs/01-product/prd.md` defining the four-POC pipeline
  (POC-1 ingestion, POC-2 chapter split, POC-3 two-voice
  segmentation, POC-4 SSML/audio).
- `KNOWLEDGE_BASE.md` topic index + updated `CLAUDE.md` for the
  new shape.
- Pipeline guide covering all three POC stages
  (`docs/02-features/azure-audiobooks/`).

### Changed
- IPA pipeline (syllabifier, phonological processors, dialect
  dictionaries, Polly wrapper, Flask UI) archived to `archive/`.
  Behavior preserved for reference; not part of the active
  codebase.

## [0.10.0] — 2025-12-19

Production-ready multi-voice character detection pipeline for
Azure TTS. Detects character names per chapter, builds a per-book
character inventory, and assigns voices from the Azure pool with
gender matching. (Closed at the 0.11 pivot — the four-POC
audiobook reframing absorbed the segmentation work but moved
character attribution to a stretch goal that was later closed in
0.14.)

### Added
- Azure TTS multi-voice character detection pipeline.
- Character breakdown utility for the `azure-tts` path.
- Documentation reorganized into a 5-tier hierarchy under `docs/`.

## [0.9.0] — 2025-12-16

**Phase 3 syllabifier alternative** completes pattern coverage:
CVVV (gemination), CVCCVV (cluster splitting), CVVVV (long-vowel
sequences), CVCCVVC / CCVC / edge cases. Phase 6 Final Validation
& Documentation closes out the IPA-era pipeline as feature-complete.

### Added
- Syllabifier patterns: CVVV (Phase 3A), CVCCVV (3B), CVVVV (3C),
  CVCCVVC / CCVC and edge cases (3D).
- Pattern-analysis tools and baseline checkpoint for the Phase 3
  Alternative implementation.

### Changed
- Phase 6.0 Final Validation & Documentation completed.

## [0.8.0] — 2025-12-16

Multi-dialect IPA coverage rounds out: MSA, Gulf, Levantine, and
Maghreb dictionaries each get their missing entries. ~50+ entries
added across dialects to close pronunciation gaps.

### Added
- MSA: ta marbuta + hamza-on-ya/waw entries; default-position
  entries for 6 missing consonants.
- Gulf: 22 missing IPA-coverage entries.
- Levantine: 15 missing IPA-coverage entries.
- Maghreb: 13 missing entries + 3 hamza-variant entries.

### Fixed
- UI typo: "Maghrebi" → "Maghreb" to match dictionary key.

## [0.7.0] — 2025-11-03

AWS Polly integration ships. `PollyTTS` wrapper class with
comprehensive tests; POC test script extended with comparison mode
and reporting. Graceful fallback for diacritization improves
Polly resilience on edge inputs.

### Added
- `PollyTTS` wrapper class with tests.
- POC comparison harness (eSpeak vs Polly) with reporting.
- Status / Failed_Layers columns in CSV export.
- Graceful fallback on diacritization failure.

### Changed
- AWS dependencies + configuration set up for Polly.
- Default Flask port: 5000 → 5050.

## [0.6.0] — 2025-10-30

Comprehensive TTS technology evaluation (2024-2025 landscape) and
Polly integration plan. Decision: add Polly **alongside** eSpeak
rather than replace, so the comparison harness can drive future
provider-selection calls with data, not vendor preference.

### Added
- Comprehensive TTS technology research (eSpeak, Polly, Azure,
  Coqui, others) with cost / quality / dialect-coverage matrix.
- Polly integration research + implementation plan.
- Polly planning docs reorganized under `docs/planning/polly/`.

## [0.5.0] — 2025-10-30

**MVP Phase 1 complete.** Egyptian Arabic test dataset built and
validated. Tasks 6.x (dataset) and 7.0 (MVP closeout) shipped.
Documentation pass: architecture, testing, tech-stack, and README
brought up to date.

### Added
- Egyptian Arabic test dataset with validation pass (Tasks 6.1-6.5).
- Task 6.6 + Task 7.0 closeout: MVP Phase 1 100% complete.
- Comprehensive architecture / testing / tech-stack docs +
  README rewrite.

### Changed
- Branding: "Egyptian Arabic TTS" → "Arabic TTS" (multi-dialect)
  to match what shipped.

## [0.4.0] — 2025-10-30

Comprehensive testing + error-handling. **329 total tests** across
unit / integration / error / performance benchmarks. Pre-commit
hook enforces the test gate.

### Added
- Integration tests (Tasks 5.1, 5.3): 38 tests, 263 total at the
  time.
- Error-handling test suite (Task 5.4): 45 tests.
- Performance benchmarks (Tasks 5.5, 5.6): 21 tests, 329 total.
- Comprehensive test documentation (Task 5.7).
- Pre-commit hook + Task 5.0 closeout.

## [0.3.0] — 2025-10-30

eSpeak / X-SAMPA integration + Flask API. Audio generation works
end-to-end through the IPA pipeline; **MVP Audio is functional.**

### Added
- eSpeak integration with X-SAMPA mapping (Tasks 4.1-4.3).
- Flask API for audio generation (Tasks 4.4-4.5).
- eSpeak integration unit tests (Task 4.6, 100% pass).
- Manual audio testing closeout (Task 4.7) — MVP Audio complete.
- JSON / CSV download endpoints in the Flask UI.
- Responsive UI for all screen sizes.

## [0.2.0] — 2025-10-30

Phonological pipeline: gemination, sun-letter assimilation,
positional allophones, emphatic spread. Each processor lands at
**100% accuracy** on the test corpus. The pipeline composes into a
single `phonological_pipeline` integration point.

### Added
- Gemination Processor (Task 3.1, 100% accuracy).
- Sun Letter Assimilation (Task 3.2, 100% accuracy).
- Positional Allophone Processor (Task 3.3, 100% accuracy).
- Emphatic Spread Processor (Task 3.4, 100% accuracy).
- Phonological pipeline integration (Task 3.5).

## [0.1.0] — 2025-10-30

Foundation: project setup + dependencies (Task 1.0); syllabifier
algorithm fixed at 100% test pass (Task 2.0) after the 85%
checkpoint at Task 2.2. The `masterTTS.json` dictionary becomes
the canonical pronunciation source.

### Added
- Foundation setup + Python dependencies (Task 1.0).
- Syllabifier algorithm: 85% (Tasks 2.1-2.2) → 100% (Task 2.0
  closeout) on the corpus.
- `masterTTS.json` file-path resolution.
- Test infrastructure (`test_system.py`).
- Initial demo + summary doc.

## [0.0.x] — 2025-08-15

First upload of the refactored Arabic TTS project on top of an
earlier Replit-assistant scaffold (~15 assistant-checkpoint commits
seeding the Flask UI, dependencies, JSON/CSV download, and
responsive layout).

### Added
- Flask web UI for Arabic TTS parsing.
- pytest + flask dependencies; initial test execution.
- JSON / CSV download functionality.
- Responsive UI for all screen sizes.
