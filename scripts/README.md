# Scripts

Utility scripts for data preparation and exploration.

## Files

| Script | Purpose |
|--------|---------|
| `create_docx.py` | Convert TXT books to DOCX format for testing |
| `inspect_internal_chapters.py` | Inspect EPUB internal chapter structure |
| `inspect_spines.py` | Inspect EPUB spine/TOC structure |

## Usage

These are one-off utilities for data preparation and investigation, not part of the main pipeline.

```bash
# Create DOCX test files
python scripts/create_docx.py

# Inspect EPUB structure
python scripts/inspect_spines.py
python scripts/inspect_internal_chapters.py
```

## Note

For the main audiobook pipeline, see `src/audiobook/` and `tests/audiobook/`.
