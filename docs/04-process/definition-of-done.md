# Definition of Done

## Per-POC Completion

A POC is done when:

- [ ] Module implemented in `src/audiobook/`
- [ ] Tests pass: `pytest tests/audiobook/test_{module}.py -v`
- [ ] Run on at least 1 real book
- [ ] CSV output reviewed chapter by chapter
- [ ] No text loss (character count verification where applicable)
- [ ] Edge cases handled or documented as known limitations

## POC-Specific Criteria

### POC-1: Book Ingestion
- Clean text extraction from both PDF and TXT
- Zero text loss (verified by char count comparison)
- Correct paragraph boundary detection
- Arabic encoding normalized (Presentation Forms → Standard)

### POC-2: Chapter Splitting
- Correct chapter boundary detection on 3+ books
- No mid-sentence splits
- Chapter files concatenate back to original text
- Chapters exceeding Azure limits are split at paragraph boundaries

### POC-3a: Two-Voice
- All narration/dialogue boundaries verified via CSV review
- Complete two-voice audiobook from at least 1 real book
- Voice switching sounds natural on listen-through
- Repeatable on a second book with different formatting

### POC-3b: Multi-Voice (stretch)
- Character attribution completed for at least 1 book
- CSV review completed for all "Unknown" segments
- Multi-voice audiobook with distinct character voices
- Honest assessment: is quality improvement worth the review effort?
