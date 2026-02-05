# Research: Arabic PDF Text Extraction & PDF-to-EPUB Conversion

**Date:** February 2026
**Context:** Audiobook pipeline ingestion — POC-1 (book ingestion) works for TXT and EPUB but fails on Arabic PDFs
**Author:** Research conducted by Claude Opus 4.5

---

## The Problem

Arabic PDFs from publishers like Hindawi Foundation encode word spacing as **positional coordinates** rather than explicit space characters. When PyMuPDF or pdfplumber extracts text, they fail to infer word boundaries, producing fused output:

- **Expected:** `أقطعُ هذا`
- **Actual:** `أﻗﻄﻊُﻫﺬا`

Additionally:
- PyMuPDF has [closed the Arabic ligature issue as "wontfix"](https://github.com/pymupdf/PyMuPDF/issues/2199), stating proper Arabic support would require integrating HarfBuzz (a text-shaping engine)
- pdfplumber produces worse reading order than PyMuPDF for Arabic
- This is a **source data problem** in how Arabic publishers encode PDFs, not a bug in our code

---

## 1. Direct Text-Layer Extraction (No OCR)

These tools extract text from the PDF's embedded text layer. They all share the same fundamental limitation: Arabic PDFs store character positions instead of spaces.

### PyMuPDF (fitz)

- **URL:** https://github.com/pymupdf/PyMuPDF
- **Arabic word spacing:** Fails on position-based spacing. [Issue #2755](https://github.com/pymupdf/PyMuPDF/issues/2755) documents fused words.
- **Arabic ligatures:** [Issue #2199](https://github.com/pymupdf/PyMuPDF/issues/2199) — closed as "wontfix." Ligature characters composed of two Unicode characters are not reversed correctly in RTL extraction. Maintainers say proper support requires HarfBuzz integration, which is not planned.
- **RTL order:** Mostly correct (better than alternatives).
- **Maintained:** Yes, actively maintained.
- **`rawdict` workaround:** `page.get_text("rawdict")` returns per-character bounding boxes. A custom gap-detection algorithm could insert spaces when the gap between character bboxes exceeds a threshold (~25% of character width, per maintainer suggestion in issue #2755). This is the most promising non-OCR approach but requires custom code.
- **`space-guess` parameter:** An experimental MuPDF Extract facility with a `space-guess` parameter can adjust space detection thresholds. Testing showed improvement from 172 to 197 detected spaces on a problem document.
- **Verdict:** Best available text-layer extractor for Arabic, but fundamentally broken for position-based spacing. The `rawdict` approach is worth prototyping.

### pypdf

- **URL:** https://github.com/py-pdf/pypdf
- **Arabic word spacing:** Same core problem as PyMuPDF but with different thresholds. [Issue #1296](https://github.com/py-pdf/pypdf/issues/1296) documents Arabic text extraction order problems.
- **RTL order:** Worse than PyMuPDF. Text sometimes returned in reversed order.
- **Maintained:** Yes.
- **Verdict:** Not better than PyMuPDF for Arabic. Sometimes complementary (different files fail differently), but not a solution.

### pdfplumber

- **URL:** https://github.com/jsvine/pdfplumber
- **Arabic word spacing:** Same core issue.
- **RTL order:** Poor for Arabic — worse than PyMuPDF.
- **Maintained:** Yes.
- **Verdict:** Worse than PyMuPDF for Arabic. Already tested and rejected in POC-1.

### Apache PDFBox / Tika (Java)

- **URL:** https://pdfbox.apache.org/
- **Arabic:** [PDFBOX-5029](https://issues.apache.org/jira/browse/PDFBOX-5029) documents Arabic extraction issues.
- **Maintained:** Yes.
- **Verdict:** Java-based, same class of problems. Not worth the language switch.

### multilingual-pdf2text

- **URL:** https://github.com/shahrukhx01/multilingual-pdf2text
- **Arabic:** Claims multilingual support, preserves formatting. Built on top of pdfplumber.
- **Maintained:** Low activity.
- **Verdict:** Wrapper around pdfplumber — inherits all its Arabic problems.

---

## 2. OCR-Based Approaches

These tools treat PDF pages as images and perform optical character recognition. For born-digital PDFs (like Hindawi books with clean fonts), OCR accuracy should be high because the images are crisp.

### Tesseract 5.x

- **URL:** https://github.com/tesseract-ocr/tesseract
- **Arabic quality:** Moderate baseline. [Fine-tuning research (IEEE 2024)](https://github.com/OmarSamirz/Fine-Tuning-an-Arabic-OCR-Model-using-Tesseract-5.0) shows significant WER improvements with fine-tuned models, but default Arabic performance is weak compared to commercial solutions.
- **Speed:** Fast (local).
- **Cost:** Free, open source.
- **Maintained:** Yes, actively maintained.
- **Used by:** archive.org uses Tesseract for Arabic book digitization with [two-pass OCR](https://archive.org/developers/ocr.html) (script detection then language-specific pass). Results are functional for search indexing but not production-quality.
- **Verdict:** Acceptable if fine-tuned. Not recommended as-is for audiobook-quality text.

### PaddleOCR

- **URL:** https://github.com/PaddlePaddle/PaddleOCR (47k+ stars)
- **Arabic quality:** Better than Tesseract for Arabic. ppocr-v5 models (2025) improved Arabic accuracy by **40%+** compared to previous versions. Supports 109 languages.
- **Speed:** Fast (local, GPU-accelerated).
- **Cost:** Free, open source.
- **Maintained:** Yes, very actively maintained. Largest open-source OCR project.
- **Known limitation:** [Issue #10358](https://github.com/PaddlePaddle/PaddleOCR/issues/10358) — achieving 95%+ accuracy on Arabic requires fine-tuning.
- **Verdict:** Best open-source OCR option for Arabic. The v5 Arabic models are a significant improvement. Worth testing on Hindawi PDFs.

### EasyOCR

- **URL:** https://github.com/JaidedAI/EasyOCR
- **Arabic quality:** Decent. [KITAB-Bench (ACL 2025)](https://arxiv.org/abs/2502.14949) reports WER 0.53, CER 0.20 for Arabic — superior recognition to Surya despite lower detection scores.
- **Speed:** Moderate (local, GPU-accelerated).
- **Cost:** Free, open source.
- **Maintained:** Yes.
- **Verdict:** Simpler API than PaddleOCR. Good fallback option. Arabic performance is moderate — not best-in-class.

### Surya

- **URL:** https://github.com/datalab-to/surya
- **Arabic quality:** Strong detection (mAP@0.50 of 79.67% per KITAB-Bench) but weaker recognition. Lacks Arabic-specific optimizations for segmentation and diacritic handling.
- **Speed:** Moderate (local, GPU).
- **Cost:** Free, open source.
- **Maintained:** Yes, actively maintained by Datalab.
- **Verdict:** Better for layout analysis and reading order detection than for text recognition. Could complement another OCR tool.

### Mistral OCR (API)

- **URL:** https://mistral.ai/news/mistral-ocr
- **Arabic quality:** Claims 94.9% overall accuracy, outperforming Google Document AI (83.4%) and Azure OCR (89.5%) per [independent benchmarks](https://parsio.io/blog/mistral-ocr-test-review/). [Dedicated Arabic toolkit exists](https://github.com/Pythonation/Mistral-Arabic-OCR-test) with batch processing support.
- **Speed:** Fast (API-based), up to 2,000 pages/minute.
- **Cost:** Paid API. Pricing varies.
- **Maintained:** Yes. Mistral OCR 3 released in late 2025.
- **Output format:** Markdown with preserved document structure.
- **Verdict:** Most promising commercial-grade option. Highest reported accuracy. The Arabic-specific toolkit demonstrates production readiness. Cost is the main concern.

### Google Document AI (API)

- **URL:** https://cloud.google.com/document-ai
- **Arabic quality:** Strong. Backed by 25 years of Google OCR research. Supports 200+ languages including Arabic.
- **Speed:** Fast (API-based).
- **Cost:** First 1,000 pages/month free. Then usage-based pricing.
- **Maintained:** Yes, Google Cloud product.
- **Features:** ENABLE_NATIVE_PDF_PARSING can extract embedded text from PDFs. Enterprise Document OCR detects blocks, paragraphs, lines, words, and symbols.
- **Verdict:** Proven cloud solution. Free tier may cover testing needs. Good accuracy but benchmark data shows Mistral OCR outperforms it.

### ABBYY FineReader

- **URL:** https://pdf.abbyy.com/
- **Arabic quality:** [~98% accuracy on Arabic](https://www.cisdem.com/resource/arabic-ocr.html). Industry leader for complex scripts. End-to-end Arabic recognition available as add-on module.
- **Speed:** Fast.
- **Cost:** Expensive. Arabic module requires separate licensing.
- **Maintained:** Yes, commercial product.
- **Verdict:** Gold standard for Arabic OCR accuracy. Not practical for an open-source pipeline — expensive and not scriptable in Python.

---

## 3. PDF-to-Markdown/EPUB Conversion Tools

### Calibre (ebook-convert)

- **URL:** https://calibre-ebook.com/
- **Arabic PDF support:** Broken. [Bug #2032531](https://bugs.launchpad.net/calibre/+bug/2032531): text spelling reversed, RTL direction flipped to LTR. Calibre's own documentation calls PDF "the worst format to convert from."
- **Workaround:** CSS `*{ direction: rtl; }` partially helps, but text reversal remains.
- **Verdict:** Not viable for Arabic PDFs. Do not use.

### MinerU

- **URL:** https://github.com/opendatalab/MinerU
- **Arabic support:** Uses PaddleOCR backend for scanned PDFs. ppocr-v5 models improved Arabic by 40%+. Known limitation: "easily confused characters in Arabic script."
- **Output:** Markdown and JSON.
- **Maintained:** Yes, actively maintained. MinerU 2.5 released 2025.
- **Verdict:** Promising for PDF-to-Markdown. Does not output EPUB directly. Arabic accuracy improving but not yet production-grade.

### Marker (Datalab)

- **URL:** https://github.com/datalab-to/marker
- **Arabic support:** Uses Surya OCR (90+ languages). Arabic included but no Arabic-specific optimizations.
- **Output:** Markdown and JSON.
- **Maintained:** Yes, actively maintained.
- **Verdict:** Good general tool. Arabic support is present but not tuned.

### k2pdfopt

- **URL:** https://www.willus.com/k2pdfopt/
- **Arabic support:** No documented RTL support. Bitmap-based page reflow for e-readers.
- **Verdict:** Unlikely to help with Arabic text extraction. Designed for reflowing page layout, not text extraction.

### Adobe Acrobat

- **Arabic support:** Good Arabic support in PDF-to-Word/EPUB export.
- **Cost:** Expensive commercial product.
- **Scriptable:** Limited. Not practical for automated pipeline.
- **Verdict:** Manual option for occasional one-off conversions.

---

## 4. Arabic NLP Post-Processing Tools

These tools could fix extracted text (even fused) by applying morphological analysis to re-segment words.

### CAMeL Tools

- **URL:** https://github.com/CAMeL-Lab/camel_tools (~900 stars)
- **Developer:** CAMeL Lab at NYU Abu Dhabi.
- **Capabilities:** Morphological analysis, word segmentation, diacritization, POS tagging, dialect identification. 98% tokenization accuracy on MSA (Modern Standard Arabic).
- **Maintained:** Yes, actively maintained.
- **Relevance:** Could potentially re-segment fused words from PyMuPDF output without OCR. Morphological analysis knows where Arabic word boundaries should be.
- **Verdict:** High potential for post-processing. Worth experimenting with on fused text.

### Farasa

- **URL:** https://farasa.qcri.org/
- **Developer:** Qatar Computing Research Institute.
- **Capabilities:** Fast Arabic segmentation ("Fast and Furious Segmenter for Arabic"), POS tagging, lemmatization. 98% segmentation accuracy on Arabic Treebank.
- **Maintained:** Yes.
- **Relevance:** Similar to CAMeL Tools — could detect word boundaries in fused text.
- **Verdict:** Alternative to CAMeL Tools for word boundary detection. Slightly different tokenization conventions.

### arafix_ocr

- **URL:** https://github.com/CAMeL-Lab/arafix_ocr (~30 stars)
- **Developer:** CAMeL Lab at NYU Abu Dhabi.
- **Capabilities:** N-gram-based post-correction of Arabic OCR output. Operates purely on text (no image knowledge).
- **Status:** Last updated 2021. The prediction module is "not ready for use" per documentation. No quantitative accuracy results published.
- **Verdict:** Interesting concept but inactive and incomplete. Not production-ready.

### SinaTools

- **URL:** https://arxiv.org/html/2411.01523v1
- **Capabilities:** Alternative Arabic NLP toolkit.
- **Verdict:** Lower profile, less tested. Not recommended over CAMeL Tools.

---

## 5. Relevant GitHub Repositories

### Arabic PDF Extraction

| Repository | URL | Purpose | Stars | Status |
|-----------|-----|---------|-------|--------|
| Arabic-PDF-OCR-Text-Extraction | https://github.com/AliAlWahayb/Arabic-PDF-OCR-Text-Extraction | Google Document AI + Farasa diacritization | Low | Active |
| Arabic_OCR_From_PDF | https://github.com/zaakki-ahamed/Arabic_OCR_From_PDF | Tesseract OCR for Arabic PDFs | Low | Small project |
| arabic-ocr | https://github.com/Kareem-Emad/arabic-ocr | General Arabic OCR from images with word segmentation | ~200 | Older |
| Mistral-Arabic-OCR-test | https://github.com/Pythonation/Mistral-Arabic-OCR-test | Mistral OCR for Arabic PDFs, batch processing | Low | Recent (2025) |
| arabic-pdf-chat | https://github.com/MohammedNasserAhmed/arabic-pdf-chat | Arabic PDF Q&A using pytesseract + PyPDF2 | Low | Niche |
| Clean-and-Segmentation-of-Arabic-Text | https://github.com/Nagoudi/Clean-and-Segmentation-of-Arabic-Text | Text segmentation, cleaning (remove diacritics, non-Arabic, etc.) | Low | Utility |

### Arabic NLP & OCR Post-Processing

| Repository | URL | Purpose | Stars | Status |
|-----------|-----|---------|-------|--------|
| camel_tools | https://github.com/CAMeL-Lab/camel_tools | Full Arabic NLP toolkit | ~900 | Active |
| arafix_ocr | https://github.com/CAMeL-Lab/arafix_ocr | N-gram OCR post-correction | ~30 | Inactive (2021) |
| Fine-Tuning-Arabic-OCR-Tesseract-5.0 | https://github.com/OmarSamirz/Fine-Tuning-an-Arabic-OCR-Model-using-Tesseract-5.0 | Fine-tuning Tesseract for Arabic | Low | Research (2024) |

### Hindawi-Specific

| Repository | URL | Purpose | Stars | Status |
|-----------|-----|---------|-------|--------|
| hindawi-dl | https://github.com/shahwan42/hindawi-dl | Bulk PDF downloader for Hindawi Foundation books | Low | Useful for sourcing |

### Key Gap

**No repository was found that specifically addresses the word-spacing/gap-detection problem in Arabic PDF text-layer extraction.** This is a genuine gap in the open-source ecosystem. The closest approach is PyMuPDF's `rawdict` character-level extraction combined with custom gap detection.

---

## 6. The Kindle / Amazon Analogy

- Amazon KDP [supports Arabic](https://kdp.amazon.com/en_US/help/topic/GUQT4C8J6RR6V8TY) but **does not accept PDF uploads for Arabic** — only EPUB, DOCX, HTML, or MOBI.
- RTL support is limited: no X-Ray, no WordWise, no page numbers for RTL languages.
- [Creating RTL Kindle books](https://abiusx.com/how-to-create-rtl-books-for-kindle/) requires EPUB with explicit `direction: rtl` CSS.
- Amazon added Arabic Kindle support in [2018](https://arablit.org/2018/06/28/amazons-kindle-now-supports-arabic/).
- **Takeaway:** Even Amazon does not attempt to convert Arabic PDFs. They require structured input formats (EPUB/DOCX). This validates the "avoid PDF" strategy.

---

## 7. State of the Art: How Arabic Digital Libraries Work

### Al-Maktaba al-Shamela (The Comprehensive Library)

- **Method:** Primarily [manual double-keying](https://kitab-project.org/Al-Maktaba-al-Sh%C4%81mila-a-short-history/) (human transcription), not OCR.
- **Scale:** At one point had 30 data entry employees.
- **Format:** Custom markup format, later converted to EPUB.
- **Quality:** High — human transcription from specific print editions allows accurate scholarly citation.
- **Takeaway:** The largest Arabic digital library chose human transcription over OCR. This speaks to the difficulty of automated Arabic text extraction.

### Archive.org

- **Method:** [Tesseract with Arabic language detection](https://archive.org/developers/ocr.html). Two-pass OCR: first script detection, then language-specific OCR.
- **Software:** Tesseract 5.3.0 with language "ar" and script "Arabic."
- **Quality:** Mixed. Functional for search indexing but not production-quality for audiobooks. Some books use ABBYY XML if provided by the uploader.
- **Takeaway:** Archive.org's OCR is "good enough for search" but not "good enough for audiobooks."

### Hindawi Foundation (our source publisher)

- **Method:** Born-digital content. Books are produced from their typesetting system, available in both PDF and EPUB.
- **Collection:** [1,745 books (81.5 million words)](https://researchdata.se/en/catalogue/dataset/2024-145) published 2008-2024. Genres: non-fiction, novels, children's literature, poetry, plays.
- **Formats:** PDF and EPUB both available. [Hindawi embraced EPUB standard](https://teleread.com/hindawi-stm-publisher-embraces-epub-standard-for-technical-materials/index.html).
- **Key insight:** The PDFs have a text layer but it encodes spacing as coordinates. The EPUBs have proper text. **EPUB is the correct format to source from Hindawi.**

### Academic State of the Art (2025)

- **[KITAB-Bench (ACL 2025)](https://github.com/mbzuai-oryx/KITAB-Bench):** First comprehensive Arabic OCR benchmark. 8,809 samples across 9 domains and 36 sub-domains. Key finding: **Vision-language models (GPT-4o, Gemini) outperform traditional OCR by ~60% in Character Error Rate.** Best PDF-to-Markdown: Gemini-2.0-Flash at 65% accuracy.
- **[QARI-OCR](https://arxiv.org/html/2506.02295v1):** Multimodal LLM adaptation for high-fidelity Arabic text recognition. Represents the cutting edge.
- **Trend:** The field is moving from traditional OCR pipelines to vision-language models for Arabic document understanding.

---

## 8. Recommendations

### Decision Framework

The choice depends on two questions:
1. **Can we get EPUBs instead of PDFs?** (Eliminates the problem entirely)
2. **If PDFs are unavoidable, what quality bar do we need?** (Audiobook production requires near-perfect text)

### Option A: Avoid the Problem — Source EPUBs (RECOMMENDED FIRST)

**Approach:** Get EPUBs from Hindawi instead of PDFs.

Hindawi Foundation publishes in both PDF and EPUB. Our EPUB extraction already works perfectly in POC-1.

**Steps:**
1. Check if Hindawi's website offers EPUB downloads for target books
2. Source EPUBs from archive.org (already confirmed working)
3. Only fall back to PDF for books where no EPUB exists

**Effort:** Minimal.
**Quality:** Perfect (proven in POC-1).
**Risk:** Some books may only be available as PDF.

### Option B: PyMuPDF `rawdict` Gap Detection (Custom Code, No OCR)

**Approach:** Build a character-position gap detector using PyMuPDF's rawdict output.

**Steps:**
1. Extract per-character bounding boxes with `page.get_text("rawdict")`
2. For each pair of adjacent characters, compute the gap between bbox edges
3. If gap exceeds threshold (start with 25% of average character width), insert space
4. Handle RTL direction (gaps go right-to-left)

**Effort:** 1-2 days of development + testing.
**Quality:** Unknown but promising. PyMuPDF's character extraction is trusted; only space insertion is missing.
**Risk:** Threshold tuning may be book-specific. Arabic cursive connections complicate gap measurement.

### Option C: PaddleOCR on Rendered PDF Pages

**Approach:** Render PDF pages to images, run PaddleOCR with Arabic v5 models.

**Steps:**
1. Render PDF pages to high-res images with PyMuPDF (`page.get_pixmap()`)
2. Run PaddleOCR with Arabic model (ppocr-v5) on each page image
3. Reconstruct full text from OCR output

**Effort:** 1 day setup + accuracy testing.
**Quality:** PaddleOCR v5 models show 40%+ improvement on Arabic. Born-digital PDFs (clean fonts) should produce near-perfect results since the images are crisp.
**Risk:** OCR may introduce errors that text-layer extraction would not (diacritic confusion, similar character shapes).
**Cost:** Free.

### Option D: Mistral OCR API

**Approach:** Use Mistral OCR API to process Arabic PDFs with best-in-class accuracy.

**Steps:**
1. Send PDFs to [Mistral OCR API](https://mistral.ai/news/mistral-ocr)
2. Receive Markdown output with preserved document structure
3. [Arabic-specific toolkit](https://github.com/Pythonation/Mistral-Arabic-OCR-test) provides batch processing

**Effort:** Half a day.
**Quality:** Best-in-class per benchmarks (94.9% overall accuracy, outperforms Google and Azure).
**Risk:** API dependency, potential cost at scale.
**Cost:** Paid API (pricing varies).

### Option E: CAMeL Tools / Farasa Post-Processing (Experimental)

**Approach:** Use PyMuPDF's fused output and re-segment with Arabic morphological analysis.

**Steps:**
1. Extract text with PyMuPDF (accepting fused words)
2. Run through [CAMeL Tools](https://github.com/CAMeL-Lab/camel_tools) word segmenter or Farasa
3. Reconstruct text with proper spacing

**Effort:** 1 day.
**Quality:** Unknown. Morphological segmenters are designed for tokenization (splitting clitics from stems), not for fixing fused PDF extraction. The input (fused multi-word strings) may be outside their training distribution.
**Risk:** Morphological tools may not recognize fused words as valid input.

### Recommended Path

```
1. FIRST: Check if Hindawi EPUBs are available (Option A)
   - This eliminates the problem entirely
   - Our EPUB extraction is proven

2. IF PDFs are unavoidable: Try Option B (rawdict gap detection)
   - Most targeted fix for the exact problem
   - No external APIs or OCR required
   - Can prototype quickly on one Hindawi PDF

3. IF Option B doesn't produce clean text: Fall back to Option C (PaddleOCR)
   - Born-digital PDFs are OCR's best-case scenario
   - Free, open source, actively maintained
   - 40%+ Arabic improvement in v5 models

4. Option D (Mistral OCR) is the "throw money at it" option
   - Highest accuracy, minimal code
   - Best for books where accuracy is paramount and volume is low
```

---

## Key Takeaways

1. **No open-source tool correctly extracts word-spaced Arabic text from PDFs.** This is a genuine gap in the ecosystem. Even the largest Arabic digital library (Shamela) uses human transcription.

2. **EPUB is the correct format for Arabic books.** Amazon does not accept Arabic PDFs. Hindawi publishes EPUBs. Avoid the problem.

3. **If OCR is needed, PaddleOCR v5 is the best free option.** For commercial accuracy, Mistral OCR leads.

4. **The field is moving to vision-language models.** KITAB-Bench (2025) shows GPT-4o and Gemini outperform all traditional OCR by 60% CER on Arabic.

5. **The rawdict gap-detection approach has never been publicly implemented for Arabic.** It is the most promising low-cost path for fixing text-layer extraction, but requires custom development.

---

## Sources

### GitHub Issues & Bug Reports
- [PyMuPDF Issue #2199 — Arabic Ligatures (wontfix)](https://github.com/pymupdf/PyMuPDF/issues/2199)
- [PyMuPDF Issue #2755 — Words Lumped Together](https://github.com/pymupdf/PyMuPDF/issues/2755)
- [pypdf Issue #1296 — Arabic Text Order](https://github.com/py-pdf/pypdf/issues/1296)
- [Apache PDFBOX-5029 — Arabic Extraction](https://issues.apache.org/jira/browse/PDFBOX-5029)
- [Calibre Bug #2032531 — Arabic PDF Conversion](https://bugs.launchpad.net/calibre/+bug/2032531)
- [PaddleOCR Issue #10358 — Arabic Fine-Tuning](https://github.com/PaddlePaddle/PaddleOCR/issues/10358)

### Academic Papers & Benchmarks
- [KITAB-Bench (ACL 2025)](https://arxiv.org/abs/2502.14949)
- [QARI-OCR — Arabic Multimodal LLM OCR](https://arxiv.org/html/2506.02295v1)
- [Fine-Tuning Arabic OCR with Tesseract 5.0 (IEEE 2024)](https://ieeexplore.ieee.org/document/10928060/)
- [A Survey of OCR in Arabic Language (MDPI)](https://www.mdpi.com/2076-3417/13/7/4584)
- [Arabic E-Book Corpus (Hindawi, 81.5M words)](https://researchdata.se/en/catalogue/dataset/2024-145)

### Tools & Libraries
- [PyMuPDF Text Extraction Docs](https://pymupdf.readthedocs.io/en/latest/app1.html)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [Surya OCR](https://github.com/datalab-to/surya)
- [Marker](https://github.com/datalab-to/marker)
- [MinerU](https://github.com/opendatalab/MinerU)
- [CAMeL Tools](https://github.com/CAMeL-Lab/camel_tools)
- [Farasa](https://farasa.qcri.org/)
- [arafix_ocr](https://github.com/CAMeL-Lab/arafix_ocr)
- [Mistral OCR](https://mistral.ai/news/mistral-ocr)
- [Mistral Arabic OCR Toolkit](https://github.com/Pythonation/Mistral-Arabic-OCR-test)
- [Google Document AI](https://cloud.google.com/document-ai)
- [ABBYY Arabic OCR](https://support.abbyy.com/hc/en-us/articles/360016365800-OCR-for-Arabic-and-Farsi)
- [Calibre](https://calibre-ebook.com/)

### Industry & Libraries
- [Amazon KDP Arabic Support](https://kdp.amazon.com/en_US/help/topic/GUQT4C8J6RR6V8TY)
- [Creating RTL Books for Kindle](https://abiusx.com/how-to-create-rtl-books-for-kindle/)
- [Al-Maktaba al-Shamela History](https://kitab-project.org/Al-Maktaba-al-Sh%C4%81mila-a-short-history/)
- [Archive.org OCR with Tesseract](https://archive.org/developers/ocr.html)
- [hindawi-dl Bulk Downloader](https://github.com/shahwan42/hindawi-dl)
- [Hindawi Embraces EPUB](https://teleread.com/hindawi-stm-publisher-embraces-epub-standard-for-technical-materials/index.html)
- [KITAB-Bench GitHub](https://github.com/mbzuai-oryx/KITAB-Bench)
- [Mistral OCR Benchmark Review](https://parsio.io/blog/mistral-ocr-test-review/)
