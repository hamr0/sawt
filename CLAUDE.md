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

Produce Arabic audiobooks from raw book files (PDF/TXT) using Azure Neural TTS.
Two-voice (narrator + dialogue) as primary goal. Multi-voice (per-character) as stretch.

## Architecture

Pipeline: Raw Book (PDF/TXT) → Ingestion → Chapter Splitting → Dialogue Detection → SSML → Azure TTS → Audio

Text processing IS the product. SSML is just markup. Let Azure handle pronunciation.

## Active Code

```
src/audiobook/          # Pipeline modules (one per POC)
tests/audiobook/        # Tests per POC
data/books/             # Input books
output/                 # Per-book working output (gitignored)
docs/02-features/azure-audiobooks/  # Plan, repo structure
```

## Archive

`archive/` contains a previous IPA phonological pipeline. Reference only, not active.
POC reference (7 iterations of dialogue detection R&D): `docs/02-features/azure-audiobooks/reference/prototypes/`

## Key Decisions

- No dialect switching for audiobooks — a book is a book
- POCs isolated by data boundaries (file output), not code imports
- CSV review at every pipeline stage, chapter-by-chapter review cadence
- Two-voice first (narrator + dialogue), multi-voice is stretch goal
- Code-first for text processing, LLM only where it demonstrably helps

## Essential Commands

```bash
pytest tests/audiobook/ -v    # Run audiobook tests
pip install -r requirements.txt
```

## Docs

| Topic | Location |
|-------|----------|
| Documentation hub | docs/README.md |
| Execution plan | docs/02-features/azure-audiobooks/PLAN.md |
| Repo structure | docs/02-features/azure-audiobooks/REPO_STRUCTURE.md |
| Product requirements | docs/01-product/prd.md |
| System state | docs/00-context/system-state.md |
