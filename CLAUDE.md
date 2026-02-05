<!-- AURORA:START -->
# Aurora Instructions

These instructions are for AI assistants working in this project.

Always open `@/.aurora/AGENTS.md` when the request:
- Mentions planning or proposals (words like plan, create, implement)
- Introduces new capabilities, breaking changes, or architecture shifts
- Sounds ambiguous and you need authoritative guidance before coding

Use `@/.aurora/AGENTS.md` to learn:
- How to create and work with plans
- Aurora workflow and conventions
- Project structure and guidelines

## MCP Tools Available

Aurora provides MCP tools for code intelligence (automatically available in Claude):

**`lsp`** - LSP code intelligence with 3 actions:
- `deadcode` - Find unused symbols, generates CODE_QUALITY_REPORT.md
- `impact` - Analyze symbol usage, show callers and risk level
- `check` - Quick usage check before editing

**`mem_search`** - Search indexed code with LSP enrichment:
- Returns code snippets with metadata (type, symbol, lines)
- Enriched with LSP context (used_by, called_by, calling)
- Includes git info (last_modified, last_author)

**When to use:**
- Before edits: Use `lsp check` to see usage impact
- Before refactoring: Use `lsp deadcode` or `lsp impact` to find all references
- Code search: Use `mem_search` instead of grep for semantic results
- After large changes: Use `lsp deadcode` to find orphaned code

Keep this managed block so 'aur init --config' can refresh the instructions.

<!-- AURORA:END -->

# ArabicTTS - Arabic Audiobook Production

Produce Arabic audiobooks from raw book files (PDF/TXT/EPUB) using Azure Neural TTS.
Two-voice (narrator + dialogue) as primary goal. Multi-voice (per-character) as stretch.

## Architecture

Pipeline: Raw Book (PDF/TXT/EPUB) → Ingestion → Chapter Splitting → Dialogue Detection → SSML → Azure TTS → Audio

Text processing IS the product. SSML is just markup. Let Azure handle pronunciation.

## Active Code

| Path | Purpose |
|------|---------|
| src/audiobook/ | Pipeline modules (one file per POC) |
| tests/audiobook/ | Tests per POC |
| data/books/ | Input books (txt/, pdf/, epub/) |
| output/ | Per-book working output (gitignored) |

## Archive

`archive/` -- previous IPA phonological pipeline (code + old docs). Reference only, not active.
Prototype history (7 iterations) -- `docs/02-features/azure-audiobooks/reference/prototypes/`

## Key Patterns

- POCs isolated by data boundaries (file output), not code imports
- CSV review at every pipeline stage, chapter-by-chapter cadence
- Two-voice first (narrator + dialogue), multi-voice is stretch
- Code-first for text processing, LLM only where it demonstrably helps
- No dialect switching -- a book is a book

## Commands

```bash
pytest tests/audiobook/ -v        # Run audiobook tests
pytest tests/audiobook/test_ingest.py -v  # Run single POC tests
pip install -r requirements.txt   # Install dependencies
```

## Docs

| Topic | Location |
|-------|----------|
| Documentation hub | docs/README.md |
| Execution plan (source of truth) | docs/02-features/azure-audiobooks/PLAN.md |
| Knowledge base (topic index) | docs/KNOWLEDGE_BASE.md |
