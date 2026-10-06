# Development Workflow

## POC-Based Development

Each POC follows the same cycle:

1. **Implement** the module in `src/audiobook/`
2. **Write tests** in `tests/audiobook/`
3. **Run on a real book** — produce CSV output
4. **Review CSV** chapter by chapter
5. **Fix issues**, re-run, review again
6. **Move on** only when output is correct

## Commands

```bash
# Run audiobook tests
pytest tests/audiobook/ -v

# Run a specific POC's tests
pytest tests/audiobook/test_ingest.py -v
pytest tests/audiobook/test_chapters.py -v
pytest tests/audiobook/test_dialogue.py -v

# Install dependencies
pip install -r requirements.txt
```

## Branch Strategy

- `main` — stable, working code
- Feature branches for each POC

## Review Gates

Every POC produces CSV output. Review before moving on:

| POC | Review File | What to Check |
|-----|-------------|---------------|
| POC-1 | `output/{book}/ingestion/paragraphs.csv` | No text lost, paragraphs correct |
| POC-2 | `output/{book}/chapters/chapters.csv` | Boundaries correct, no mid-sentence splits |
| POC-3a | `output/{book}/segments/chapter_*.csv` | Narration/dialogue tags correct |
| POC-3b | `output/{book}/segments/chapter_*.csv` | Character attribution correct |

## File Conventions

- One module per POC in `src/audiobook/`
- One test file per module in `tests/audiobook/`
- Output goes to `output/{book_name}/{stage}/` (gitignored)
- Input books in `data/books/`
