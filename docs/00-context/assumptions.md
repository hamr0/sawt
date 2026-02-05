# Assumptions & Constraints

## Technical Assumptions

- **Azure Neural TTS** produces acceptable Arabic audio quality with plain text input (no phoneme control needed)
- **Colon `:` is the primary dialogue marker** in Arabic literature, not quotation marks (validated across 7 prototype iterations)
- **Arabic Presentation Forms** (U+FE70-FEFF) vs Standard Arabic encoding is a real issue that must be normalized during ingestion
- **PDF text extraction** with pdfplumber/PyPDF2 preserves paragraph structure for Arabic
- **Azure free tier** (5M chars/month, 12 months) is sufficient for development and testing

## Product Assumptions

- Two-voice (narrator + dialogue) is sufficient for 70-80% of fiction books
- Binary narration/dialogue classification is tractable with pattern matching (no ML required)
- CSV review workflow (chapter-by-chapter) is the right review interface for now
- Manual review of 5-15 minutes per book is acceptable for two-voice production

## Constraints

| Constraint | Detail |
|-----------|--------|
| Language | Python (PDF libs, Azure SDK, existing prototype knowledge) |
| TTS provider | Azure Speech Service (14+ Arabic neural voices, 7 dialects) |
| Cost | ~$8-12 per 150-page book at standard pricing |
| SSML char limit | Azure has per-request character limits; chapters may need splitting |
| No dialect switching | One voice profile per book — dialect changes expressions, not just accent |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PDF extraction loses formatting | High | High | Test multiple PDF libraries, compare output |
| Chapter detection fails on unusual structures | Medium | Medium | Fallback: size-based splitting at paragraph boundaries |
| Quotation conventions vary between books | High | Medium | Build normalizer, test on 3+ books |
| Multi-voice review too painful to scale | High | Medium | Accept cost; improve tooling incrementally |

## Known Unknowns

- How many different chapter heading patterns exist across Arabic publishers?
- What percentage of Arabic fiction uses non-colon dialogue markers?
- How well does Azure handle mixed Arabic/English text in audiobooks?
