# Insights

Learnings from development, testing, and review that inform future work.

---

### Prototype phase insights (from 7 iterations)

- **Colon `:` is the primary Arabic dialogue marker**, not quotation marks. Quotation marks (`«»`) caught only 5 dialogues vs 59 with colons.
- **External character name lists** (from Wikipedia) beat heuristic name extraction. Heuristic approach had 19% false positive rate.
- **Arabic Presentation Forms encoding** (U+FE70-FEFF) silently breaks string matching. Must normalize to Standard Arabic early in pipeline.
- **State machine approach** handles multiline dialogue continuation better than regex-only.
- **CSV review workflow** is essential — without structured output, review is unbearable.
- **Voice switching creates attention resets** that mask TTS pronunciation artifacts. Two-voice sounds significantly better than single-voice, independent of detection accuracy.
- **63.5% automated character attribution** is competitive with English SOTA (53-69% for similar tasks).
