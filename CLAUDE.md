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

# Sawt - Arabic Audiobook Production

Produce Arabic audiobooks from raw book files (PDF/TXT/EPUB) using Azure Neural TTS.
Two-voice (narrator + dialogue) as primary goal. Multi-voice closed (Azure Arabic lacks voices/emotions).

## Architecture

Pipeline: Raw Book (EPUB/DOCX/TXT) → Ingestion → Chapter Splitting → Dialogue Detection → SSML + Voice Selection → Azure TTS → Audio

Text processing IS the product. SSML is just markup. Let Azure handle pronunciation.

## Pipeline Status

| Module | Status | Purpose |
|--------|--------|---------|
| src/audiobook/ingest/ | PRODUCTION READY | File ingestion (EPUB/DOCX/TXT → text) |
| src/audiobook/chapters/ | PRODUCTION READY | Chapter splitting (25K char units) |
| src/audiobook/dialogue/ | PRODUCTION READY | Dialogue detection (~95% accuracy) |
| src/audiobook/ssml/ | NEXT (POC 4) | SSML generation + voice selection + sampling |
| src/audiobook/shared/ | Active | Shared utilities (review, azure_client) |
| tests/audiobook/ | 126 tests | Tests per module (mirrored structure) |
| data/books/ | 12 books | Input books (epub/, docx/, txt/) |
| output/ | gitignored | Per-book working output |

## Archive

`archive/` -- previous IPA phonological pipeline (code + old docs). Reference only, not active.
Prototype history (7 iterations) -- `docs/02-features/azure-audiobooks/reference/prototypes/`

## Key Patterns

- POCs isolated by data boundaries (file output), not code imports
- CSV review at every pipeline stage, chapter-by-chapter cadence
- Two-voice (narrator + dialogue) for fiction, single voice for non-fiction
- Multi-voice closed (only 2 Arabic voices per dialect, attribution overhead not justified)
- Dialect-matched voices per book (Egyptian author → ar-EG, Levantine → ar-SY/JO/LB, etc.)
- Code-first for text processing, LLM only where it demonstrably helps
- No dialect switching -- a book is a book

## Commands

```bash
pytest tests/audiobook/ -v                    # Run all audiobook tests
pytest tests/audiobook/ingest/ -v             # Run ingestion tests
pytest tests/audiobook/chapters/ -v           # Run chapter splitting tests
pytest tests/audiobook/dialogue/ -v           # Run dialogue detection tests
pip install -r requirements.txt               # Install dependencies
```

## Docs

| Topic | Location |
|-------|----------|
| Documentation hub | docs/README.md |
| Execution plan (source of truth) | docs/02-features/azure-audiobooks/PLAN.md |
| Knowledge base (topic index) | docs/KNOWLEDGE_BASE.md |
