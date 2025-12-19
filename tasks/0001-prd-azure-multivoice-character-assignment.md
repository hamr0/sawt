# Product Requirements Document (PRD)
## Azure TTS SSML Multi-Voice Character Assignment System

**Project:** ArabicTTS - Multi-dialect Arabic Text-to-Speech System
**Document Version:** 3.1 (FINAL + Prototype Validated)
**Date:** 2025-12-18
**Author:** Product Manager (AI-assisted)
**Status:** Final - Azure Voice Verified (32 voices, NO style support), JSON Simplified, CSV Pattern Learned, Prototypes Validated

---

## CRITICAL: Azure Voice Reality Check (Dec 18, 2025)

**API Query Results** (`tools/azure_tts/arabic_voices_capabilities.json`):
- ✅ **32 Arabic voices available** (16 dialects × 2 voices per dialect: 1 male, 1 female)
- ❌ **NO emotional style support** for ANY Arabic voice (`style_list: [""]` for all)
- ❌ `<mstts:express-as>` tags will NOT work with Arabic
- ✅ **Prosody tags WILL work** (rate, pitch, volume)
- ✅ All voices are **OnlineNeural** type (high quality)

**Strategic Decision: MVP Character Differentiation Strategy**
1. ✅ **Voice Selection** (32 different voices across 16 dialects)
2. ✅ **Dialect Mixing** (e.g., ar-EG character + ar-SA narrator)
3. ✅ **Gender Variation** (male vs female voices)
4. ✅ **Prosody Adjustment** (rate, pitch, volume - per character or per segment)
5. ❌ **NO Emotion/Style Fields** in MVP JSON (not supported by Azure for Arabic)

**Post-MVP:** Emotion detection via stage directions `(بغضب)` → prosody mapping (Phase 5)

---

## 1. Introduction/Overview

### 1.1 Feature Description
A production-ready system that automatically detects characters in Arabic audiobook text, assigns different Azure Neural TTS voices (across multiple dialects) to each character, and generates high-quality multi-voice audiobooks using Azure SSML. The system provides a web-based interface for efficient character detection review and voice assignment, minimizing manual effort while maintaining quality control.

### 1.2 Problem Statement
Current ArabicTTS system produces single-voice audiobooks, which lack the natural character differentiation needed for engaging Arabic literature. Manual voice assignment is time-consuming and error-prone. Users need an efficient way to:
- Automatically detect characters in Arabic text (handling various quotation styles)
- Assign different Azure voices (potentially from different dialects) to characters
- Review and correct detection results without overwhelming manual work
- Generate production-quality multi-voice audiobooks at scale

### 1.3 High-Level Goal
Enable users to transform Arabic books (TXT or PDF files) into engaging multi-voice audiobooks through a three-step semi-automated workflow: detect characters, review/edit JSON checkpoint, and generate audio. The system processes 100k-word books in under 1 hour while staying within Azure free tier limits (~5M characters/month, $11/book target).

---

## 2. Goals

### Primary Goals
- **Automate character detection** from Arabic text with 80%+ accuracy (quotation-based detection)
- **Support multi-dialect voice assignment** (mix ar-EG, ar-SA, ar-AE, etc. in same book)
- **Provide efficient review interface** that surfaces only uncertain detections (reduce manual review time by 70%)
- **Generate valid Azure SSML** with seamless voice switching between characters
- **Process chapter-by-chapter** with visual progress tracking
- **Achieve production quality** suitable for commercial audiobook distribution

### Secondary Goals
- **Cost transparency:** Display per-book and cumulative monthly Azure usage
- **Prosody-based character differentiation:** Support rate, pitch, volume adjustment per character and per segment
- **Voice reference generation:** Auto-generate available_voices.json from live Azure API query
- **Reusable character configs** across book series (save JSON templates)
- **Comprehensive testing** (unit + integration tests for all components)

### Explicit Non-Goals (MVP)
- ❌ **Emotional style detection** (Azure doesn't support for Arabic)
- ❌ **Stage direction parsing** (e.g., `(بغضب)` → emotion) - Post-MVP Phase 5
- ❌ **`<mstts:express-as>` SSML tags** (not supported for Arabic voices)
- ❌ **Emotion-to-prosody automatic mapping** - Post-MVP Phase 5

---

## 3. User Stories

### 3.1 File Upload & Text Extraction
**As an audiobook producer**, I want to upload my Arabic book as either a TXT or PDF file, so that I can process books in multiple formats without manual conversion.

**Acceptance Criteria:**
- System accepts TXT files (UTF-8 encoding)
- System accepts PDF files and extracts Arabic text
- System preserves original text structure (paragraphs, chapters)
- System displays extraction progress for large PDFs
- System validates file format before processing

### 3.2 Character Detection
**As an audiobook producer**, I want to automatically detect all speaking characters from uploaded text, so that I don't have to manually identify each dialogue segment.

**Acceptance Criteria:**
- System detects characters based on Arabic quotation patterns: « », " ", ' ', — (em dash)
- System provides character occurrence count and number of speeches per character
- System processes text chapter-by-chapter
- System outputs structured JSON with detected characters and segments
- System defaults to "Narrator" voice for non-dialogue text
- System generates detection summary analytics (total speeches, character frequency)

### 3.3 JSON Review Checkpoint (Mandatory)
**As an audiobook producer**, I want to review and edit the character detection JSON before audio generation, so that I can correct errors and ensure accurate voice assignments without wasting Azure credits.

**Acceptance Criteria:**
- System displays detection results in web UI (JSON viewer with syntax highlighting)
- User can download JSON, edit locally, and re-upload
- User can edit JSON directly in web interface (textarea editor)
- System validates JSON schema before accepting changes
- User must click "Approve & Continue" to proceed to audio generation
- System prevents audio generation without JSON approval (mandatory checkpoint)

### 3.4 Visual Review & Correction
**As an audiobook producer**, I want to visually review detected characters with color-coding and confidence indicators, so that I can quickly correct errors without reading the entire book.

**Acceptance Criteria:**
- Web interface displays text with color-coded character assignments
- Low-confidence segments are highlighted for review
- Chapter summary shows character frequency table
- User can click to reassign character/voice for any segment
- Changes persist to character config JSON
- Interface shows only flagged segments by default (expandable to full text)

### 3.5 Azure Voice Reference Guide
**As an audiobook producer**, I want to see all available Azure voices with their dialects and attributes during voice assignment, so that I can make informed choices without searching Azure documentation.

**Acceptance Criteria:**
- System generates `available_voices_<timestamp>.json` on every detection run
- File contains: all Azure Arabic voices, dialects, genders, style availability
- File saved to `outputs/<book_name>/available_voices.json`
- Web UI displays voice reference during character assignment
- System validates selected voices against current Azure availability

### 3.6 Multi-Dialect Voice Assignment
**As an audiobook producer**, I want to assign different Azure voices from different Arabic dialects to different characters, so that I can create diverse, authentic character voices.

**Acceptance Criteria:**
- System supports assigning voices from any Azure Arabic dialect (ar-EG, ar-SA, ar-AE, ar-LB, ar-DZ, etc.)
- User can select dialect and voice independently for each character
- Character config JSON stores: name, dialect, gender, voice ID
- Generated SSML correctly switches between multi-dialect voices
- Audio output is seamless (no gaps or artifacts at voice boundaries)

### 3.7 Configurable Diacritization
**As an audiobook producer**, I want to optionally enable diacritization for my text before sending to Azure, so that I can test whether it improves pronunciation quality for my specific content.

**Acceptance Criteria:**
- Web interface provides checkbox: "Apply diacritization (mishkal)" - default: OFF
- When enabled, system diacritizes text before Azure TTS processing
- User can A/B test: generate samples with/without diacritization
- System logs whether diacritization was used (for quality tracking)

### 3.8 Prosody-Based Character Differentiation
**As an audiobook producer**, I want to adjust rate, pitch, and volume for each character and individual speeches, so that I can differentiate characters beyond just voice selection (since emotional styles are not supported by Azure for Arabic).

**Acceptance Criteria:**
- JSON schema includes prosody at character level (defaults for all speeches)
- JSON schema includes prosody_override at segment level (per-speech customization)
- Prosody fields: rate (0.5-2.0), pitch (±50%), volume (±50%)
- UI allows manual prosody adjustment during review
- System validates prosody values before SSML generation
- SSML generator includes `<prosody>` tags with validated values
- Users can create prosody "presets" for common character types (angry, calm, excited)

### 3.9 Cost Monitoring
**As an audiobook producer**, I want to see estimated costs before processing and track cumulative monthly Azure usage, so that I can stay within budget and avoid unexpected charges.

**Acceptance Criteria:**
- Detection results page displays: "Estimated cost: ~$8.50 (85,000 characters)"
- Dashboard shows: "Monthly usage: 1.2M / 5M characters (24% of free tier)"
- System warns if book would exceed free tier limit
- Cost calculations use Azure pricing: $16/million characters

### 3.10 Chapter-Level Processing with Progress
**As an audiobook producer**, I want to process my book chapter-by-chapter with visual progress indication, so that I can monitor long-running jobs and identify issues early.

**Acceptance Criteria:**
- User can specify chapter boundaries (auto-detect or manual markers)
- Web interface shows progress bar: "Processing Chapter 3/12 (25%)"
- Each chapter generates separate audio file (for easier editing)
- User can pause/resume processing (chapters are independent units)
- Failed chapters are flagged without blocking others

### 3.11 Smart SSML Chunking
**As an audiobook producer**, I want SSML chunks to break at natural boundaries (paragraphs, not mid-sentence), so that audio quality is maintained across chunk boundaries.

**Acceptance Criteria:**
- System breaks SSML at paragraph boundaries when exceeding 10k character limit
- System never breaks mid-sentence
- System detects paragraphs via double newline (\n\n) or newline + indent (\n + spaces/tabs)
- Each chunk maintains character voice consistency
- Chunks processed sequentially, audio concatenated seamlessly

### 3.12 Efficient Testing & Debugging
**As a developer**, I want comprehensive tests and a multi-layer processing view, so that I can quickly identify where character detection or SSML generation fails.

**Acceptance Criteria:**
- Unit tests for: quotation pattern detection, character segmentation, SSML generation, PDF extraction
- Integration tests: 5+ end-to-end test cases (short Arabic texts with known characters)
- Web interface shows processing layers: [Raw Text] → [Detected Characters] → [SSML] → [Audio]
- Each layer is expandable/inspectable for debugging
- Test suite runs in < 30 seconds (fast feedback loop)

---

## 4. Functional Requirements

### 4.0 File Input & Text Extraction
0. The system MUST accept TXT files (UTF-8 encoding) as input
1. The system MUST accept PDF files and extract Arabic text using PyPDF2 or pdfplumber
2. The system MUST preserve paragraph structure during PDF extraction
3. The system MUST validate file format before processing (reject unsupported formats)
4. The system MUST display extraction progress for large files (>100 pages)
5. The system MUST handle RTL (right-to-left) text correctly from PDFs

### 4.1 Character Detection Engine
6. The system MUST detect dialogue segments using Arabic quotation patterns: « », " ", ' ', — (em dash)
7. The system MUST support mixed quotation styles within the same text
8. The system MUST count total occurrences and number of speeches per detected character
9. The system MUST default unquoted text to "Narrator" character
10. The system MUST assign confidence scores to each detected segment (high/medium/low)
11. The system MUST handle nested quotations (dialogue within dialogue)
12. The system MUST detect character names from attribution phrases (e.g., "قال أحمد" → character: أحمد)
13. The system MUST output detection results as structured JSON per chapter
14. The system MUST generate detection summary analytics (total speeches, character frequency, chapter breakdown)

### 4.2 Character Configuration Management
15. The system MUST generate JSON config files with schema:
   ```json
   {
     "book_title": "string",
     "chapters": [
       {
         "chapter_num": "integer",
         "characters": [
           {
             "name": "string",
             "dialect": "string (ar-EG, ar-SA, etc.)",
             "gender": "string (male/female/neutral)",
             "voice_id": "string (Azure voice name)",
             "occurrence_count": "integer",
             "speech_count": "integer",
             "prosody": {
               "rate": "float (0.5-2.0, default: 1.0)",
               "pitch": "string (±50%, default: 0%)",
               "volume": "string (±50%, default: 0%)"
             }
           }
         ],
         "segments": [
           {
             "text": "string",
             "character": "string",
             "confidence": "string (high/medium/low)"
           }
         ]
       }
     ]
   }
   ```
16. The system MUST allow manual editing of character config JSON (download/upload or in-browser editor)
17. The system MUST validate JSON schema before audio generation
18. The system MUST support saving character configs as reusable templates
19. The system MUST provide JSON review checkpoint interface (mandatory approval before generation)
20. The system MUST prevent audio generation without explicit user approval of detection JSON

### 4.3 Azure Voice Reference Generation
21. The system MUST query Azure Speech API for available Arabic voices on every detection run
22. The system MUST generate `available_voices_<timestamp>.json` with:
    - All 32 Arabic voices (or current count from API)
    - Dialect code (ar-EG, ar-SA, ar-AE, etc.)
    - Local name in Arabic (e.g., "حامد" for Hamed)
    - Gender (male/female)
    - Voice type (OnlineNeural)
    - Style support status (currently: none for all Arabic voices)
23. The system MUST save voice reference to `outputs/<book_name>/available_voices_<timestamp>.json`
24. The system MUST display voice reference in web UI during character assignment
25. The system MUST validate selected voices against current Azure availability

### 4.4 Multi-Dialect Voice Assignment
26. The system MUST support all available Azure Arabic neural voices across dialects
27. The system MUST allow mixing voices from different dialects in the same book
28. The system MUST provide voice selection UI with dialect filtering (e.g., show only ar-EG voices)
29. The system MUST display voice previews (short sample audio) for selection
30. The system MUST validate voice availability before processing

### 4.5 Visual Review Interface
31. The system MUST display detected text with color-coding per character
32. The system MUST highlight low-confidence segments for review
33. The system MUST provide chapter summary view: character frequency table
34. The system MUST allow click-to-reassign character/voice for any segment
35. The system MUST default to showing only flagged segments (expandable to full text)
36. The system MUST persist user corrections to character config JSON
37. The system MUST provide "Accept All" and "Review Flagged" workflow modes

### 4.5a CSV Export & Review Pattern (Prototype-Validated)
**Rationale:** Visual review of 350+ segments on web UI is too heavy. CSV export enables efficient filtering/sorting in Excel/Google Sheets.

**Pattern Learned from Existing System** (`tts_matrix_20251216_122325.csv` with 2,012 rows):
- Hierarchical structure: Data rows (Type=SEGMENT) + Stats rows (Processing Stats, Character Stats, etc.)
- Stats rows use compact format: comma-separated values in single cells (e.g., "Total: 353, Success: 342")
- Status + Needs_Review columns enable filtering to review only flagged segments
- Final rows document detection method codes (legend)

**Requirements:**
37a. The system MUST export character detection results as CSV with the following structure:
   ```csv
   Type,Segment_ID,Chapter,Text,Speaker,Detection_Method,Confidence,Quote_Pattern,Speech_Count,Prosody_Rate,Prosody_Pitch,Prosody_Volume,Status,Needs_Review
   SEGMENT,1,1,"Text...",Narrator,default,high,-,-,1.0,0%,0%,success,-
   SEGMENT,2,1,"Quote...",أحمد,quote_guillemet+speaker_attr_before,high,« »,-,1.0,0%,0%,success,-
   ...
   Processing Stats,Total Segments: 350,Success: 320,Warning: 25,Error: 5,Success Rate: 91.4%,Flagged for Review: 30 (8.6%),...
   Character Stats,Detected Characters: 5,Narrator: 200 segs,أحمد: 65 segs (28 speeches),فاطمة: 45 segs (17 speeches),...
   Detection Methods,quote_guillemet: 85,quote_double: 42,quote_single: 18,speaker_attr: 65,default: 140,...
   Confidence Breakdown,High: 320 (91.4%),Medium: 25 (7.1%),Low: 5 (1.4%),...
   Review Flags,Confirm_Speaker: 18,Ambiguous_Quote: 8,Multiple_Speakers: 4,...
   Notes,Detection Method Codes:,quote_guillemet=« »,quote_double=" ",quote_single=' ',speaker_attr=قال patterns,...
   ```

37b. The system MUST display stats summary on web UI (NOT full segment list)
37c. The system MUST provide "Download Full CSV" and "Download Flagged Only CSV" buttons
37d. The system MUST allow CSV upload for corrections (user edits in Excel, re-uploads)
37e. The system MUST validate CSV structure on re-upload (column count, required fields)
37f. The system MUST parse stats rows separately from data rows (Type != "SEGMENT")
37g. The system MUST use compact stats format matching existing pattern (e.g., "Total: 353, Success: 342" in single cell)

**Prototype Validation:**
- ✓ Prototype 1 (Character Detection): 85% high confidence, 5% flagged (targets met)
- ✓ Prototype 2 (CSV Stats): Successfully generated CSV matching learned pattern
- ✓ Prototype 3 (Multi-Voice SSML): Generated 233.7 KB audio with voice switching

### 4.6 SSML Generation with Smart Chunking
38. The system MUST generate valid Azure SSML with `<voice>` tags for character switching
39. The system MUST include prosody settings in SSML (rate, pitch, volume) from JSON config
40. The system MUST handle multi-dialect voice switching without audio artifacts
41. The system MUST escape special XML characters in Arabic text
42. The system MUST split SSML into chunks if exceeding Azure limits (10,000 characters per request)
43. The system MUST break SSML chunks at paragraph boundaries (not mid-paragraph)
44. The system MUST never break SSML chunks mid-sentence
45. The system MUST detect paragraphs via double newline (\n\n) or newline + indent (\n + spaces/tabs)
46. The system MUST preserve character voice consistency within each chunk
47. The system MUST preserve diacritics (if enabled) through SSML encoding

### 4.7 Audio Generation Pipeline
48. The system MUST process books chapter-by-chapter (independent audio files)
49. The system MUST display real-time progress: "Processing Chapter X/Y (Z%)"
50. The system MUST generate 16-bit PCM WAV or MP3 output (user selectable)
51. The system MUST handle Azure API errors gracefully (retry logic, error messages)
52. The system MUST allow pause/resume of multi-chapter processing
53. The system MUST concatenate chapter audio files into full book (optional)

### 4.8 Diacritization (Optional)
54. The system MUST provide optional diacritization using mishkal library
55. The system MUST default diacritization to OFF
56. The system MUST allow per-book diacritization configuration
57. The system MUST log diacritization status for quality tracking

### 4.9 Cost Monitoring
58. The system MUST calculate estimated cost based on character count before processing
59. The system MUST display cumulative monthly Azure usage (characters processed)
60. The system MUST warn if processing would exceed Azure free tier (5M chars/month)
61. The system MUST provide cost breakdown: per-chapter and total book

### 4.10 Prosody Control (Character Differentiation)
62. The system MUST support prosody settings at character level (defaults for all speeches):
    - rate: float 0.5 to 2.0 (default: 1.0)
    - pitch: string "-50%" to "+50%" (default: "0%")
    - volume: string "-50%" to "+50%" (default: "0%")
63. The system MUST support prosody_override at segment level (optional per-speech customization)
64. The system MUST validate prosody values before SSML generation (reject out-of-range values)
65. The system MUST generate SSML `<prosody>` tags with validated rate, pitch, volume
66. The system MUST allow manual prosody adjustment in review UI
67. The system MUST NOT include `<mstts:express-as>` tags (not supported for Arabic voices)
68. The system MUST NOT include emotion/style fields in JSON (Azure doesn't support for Arabic)

### 4.11 Web Interface (Flask App with New Routes)
69. The system MUST add new routes to existing Flask app (`app.py`) without modifying existing routes
70. The system MUST preserve existing demo.html and all current functionality (NO changes to demo page)
71. The system MUST create new template directory: `templates/multivoice/` for all new pages
72. The system MUST implement the following new routes:
    - `GET /multivoice` - New multi-voice landing page
    - `POST /multivoice/upload` - Upload TXT/PDF file
    - `POST /multivoice/detect` - Run character detection
    - `GET /multivoice/review/<book_id>` - Display JSON review checkpoint
    - `POST /multivoice/update_config` - Save edited character config
    - `POST /multivoice/generate` - Generate audio from approved config
    - `GET /multivoice/progress/<job_id>` - Poll processing progress
73. The system MUST enforce desktop-only UI (minimum screen width: 1024px, no mobile optimization)
74. The system MUST maintain lightweight, functional design (similar to demo aesthetic)
75. The system MUST support concurrent jobs (multiple users/books)

---

## 5. Non-Goals (Out of Scope)

### Post-MVP Features (Phase 5 or Later)
- **Emotional style detection:** Azure doesn't support `<mstts:express-as>` for Arabic voices
- **Stage direction parsing:** Detecting `(بغضب)`, `(بهدوء)` → prosody mapping (not in MVP)
- **Emotion-to-prosody automatic mapping:** Manual prosody adjustment only in MVP
- **Punctuation-based emotion hints:** `!!!` → louder/faster (not in MVP)
- **Prosody presets UI:** Dropdown with "angry", "sad", "excited" templates (Phase 5)
- **Advanced prosody tuning UI:** Slider controls for real-time prosody testing (Phase 5)
- **Multi-book character templates:** Character registry database across books
- **ML-based character detection:** Current approach uses rule-based quotation parsing
- **Real-time audio streaming:** Focus on batch processing for MVP
- **Automated voice selection:** User must select voices (no AI-based matching)
- **Speaker diarization:** Assumes clear quotation marks for dialogue
- **Cloud storage integration:** Local file storage only (no S3/Azure Blob)

### Explicitly NOT Included
- eSpeak NG integration (deprecated in favor of Azure)
- XTTS integration (too slow on CPU)
- X-SAMPA conversion (not needed for Azure plain text)
- Custom phonological processing (Azure handles internally)
- Mobile app interface (web UI only)
- Mobile/tablet responsive design (desktop-only, 1024px+ screens)
- Modifications to existing demo.html page (preserved as-is)
- DOCX/EPUB file formats (TXT and PDF only for MVP)

---

## 6. Design Considerations

### 6.1 UI/UX Requirements
- **Separation of Concerns:** Create completely new multi-voice interface (templates/multivoice/) separate from demo.html
- **Preserve Existing Demo:** Do NOT modify templates/demo.html or existing routes (/, /synthesize)
- **Desktop-Only:** Minimum screen width 1024px, enforce via CSS, no mobile optimization
- **Lightweight Design:** Maintain functional aesthetic similar to existing demo page
- **Efficiency:** Default to "flagged segments only" view (reduce review overhead by 70%)
- **Visual Hierarchy:** Color-code characters clearly (max 8-10 distinct colors for readability)
- **Three-Step Workflow:** Upload → Detect → Review JSON Checkpoint → Generate (mandatory approval)

### 6.2 Existing Components to Leverage
- Flask app structure (`app.py`) - add new routes, do NOT modify existing routes
- Existing demo.html aesthetic and design patterns (replicate in multivoice templates)
- Character voice assignment logic (`tools/azure_tts/character_voice_assignment.py` - 463 LOC)

### 6.3 Design Patterns
- **Three-pass processing:** Upload/Extract → Detect → Review/Approve → Generate
- **Mandatory Checkpoint:** JSON review and approval required before audio generation
- **Stateless REST API:** Each endpoint is independent (use job IDs for long-running tasks)
- **JSON-driven configuration:** All settings externalized (no hardcoded character mappings)
- **Smart Chunking:** Break SSML at paragraph boundaries, never mid-sentence
- **Progressive enhancement:** Core functionality works, visual polish added incrementally

---

## 7. Technical Considerations

### 7.1 Architecture
- **Language:** Python 3.10+
- **Web Framework:** Flask 3.0+
- **TTS Service:** Azure Cognitive Services Speech SDK
- **Diacritization:** mishkal v0.4.1 (optional)
- **Data Storage:** JSON files (character configs), local file system (audio outputs)

### 7.2 Azure Integration
- **API:** Azure Speech SDK (`azure-cognitiveservices-speech`)
- **Authentication:** Azure subscription key + region
- **Rate Limits:** 20 concurrent requests (plan for throttling)
- **Character Limit:** 10,000 chars per SSML request (chunking required)

### 7.3 Dependencies
- Existing: Flask, mishkal, pytest
- New (Azure): `azure-cognitiveservices-speech` (pip install)
- New (PDF): `PyPDF2` or `pdfplumber` for PDF text extraction
- New (PDF, optional): `Pillow` for handling PDF images (skip image pages)
- Dev: `pytest-flask` for web endpoint testing

### 7.4 Integration Points
- **Extend:** `app.py` (add new routes, preserve existing routes)
- **Reuse:** `tools/azure_tts/character_voice_assignment.py` (refactor into module)
- **New Modules:**
  - `src/integrations/azure_multivoice.py` - SSML generation, voice management, voice reference generation
  - `src/core/character_detector.py` - Quotation parsing, character extraction, confidence scoring
  - `src/utils/ssml_builder.py` - XML generation helpers, smart chunking logic
  - `src/utils/pdf_extractor.py` - PDF text extraction, paragraph preservation
  - `src/utils/paragraph_detector.py` - Paragraph boundary detection for smart chunking

### 7.5 Performance Constraints
- **Processing Speed:** 100k-word book in < 1 hour (target: 2-3k words/minute)
- **Detection Accuracy:** 80%+ for quotation-based character detection
- **Review Efficiency:** Flag < 20% of segments for manual review
- **API Latency:** Azure TTS ~500ms per request (chunk optimization needed)

### 7.6 Cost Constraints
- **Azure Free Tier:** 5M characters/month (first 12 months)
- **Target Cost:** ~$11 per 100k-word book (~100k characters)
- **Overage Pricing:** $16/million characters (neural voices)

---

## 8. Success Metrics

### 8.1 Functional Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Character detection accuracy | 80%+ | Manual validation on 10 test books |
| False positive rate (incorrect dialogue detection) | < 15% | Test suite validation |
| Multi-dialect voice switching (no audio gaps) | 100% | Automated SSML validation + audio QA |
| Prosody adjustment working correctly | 100% | SSML validation (rate/pitch/volume tags) |
| Voice reference generation success | 100% | All 32 voices detected from Azure API |
| Smart chunking (no mid-sentence breaks) | 100% | Automated chunking tests |
| SSML generation success rate | 99%+ | Integration tests |
| Processing speed | 2-3k words/min | Benchmark on 100k-word book |

### 8.2 User Experience Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Manual review time reduction | 70% vs full manual | User testing (time to review 50k-word book) |
| Flagged segments requiring review | < 20% of total | System logs |
| User satisfaction (review interface) | 4/5+ | User survey (post-MVP) |
| Time to first audio output | < 5 min | From upload to first chapter audio |

### 8.3 Quality Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Test coverage (character detection) | 90%+ | pytest coverage report |
| Test coverage (SSML generation) | 95%+ | pytest coverage report |
| Integration test pass rate | 100% | CI/CD pipeline |
| Production audiobook quality | 4/5+ | Expert review (Arabic speakers) |

### 8.4 Cost Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Cost per 100k-word book | ~$11 | Azure usage logs |
| Books processed per free tier month | 8-10 | Character count tracking |
| Cost estimation accuracy | ±10% | Compare estimate to actual Azure bill |

### 8.5 Prototype Validation Results (Dec 18, 2025)
**Status:** ✅ All 3 prototypes successfully validated core functionality

**Prototype 1: Character Detection Algorithm**
- **Goal:** Validate >80% high confidence, <20% flagged for review
- **Results:**
  - ✅ High confidence: 85.0% (target: >80%)
  - ✅ Flagged for review: 5.0% (target: <20%)
  - ✅ Success rate: 95.0%
  - ✅ Detected 5 characters from test sample (20 segments)
  - ✅ Detection methods: 8 patterns (guillemet, double, single, em_dash + speaker attribution)
- **Files:** `tools/azure_tts/prototypes/01_character_detection.py`
- **Output:** `outputs/character_detection_20251218_223809.csv` (27 rows)

**Prototype 2: CSV Stats Generation**
- **Goal:** Validate stats row calculation matches existing pattern
- **Results:**
  - ✅ Generated CSV with hierarchical structure (SEGMENT rows + Stats rows)
  - ✅ Processing Stats row: Total, Success, Warning, Error, Success Rate
  - ✅ Character Stats row: Detected characters with speech counts
  - ✅ Detection Methods row: Breakdown by algorithm
  - ✅ Confidence Breakdown row: High/Medium/Low percentages
  - ✅ Review Flags row: Flagged segment counts
  - ✅ Notes row: Detection method legend
- **Pattern Match:** 100% match to learned pattern from `tts_matrix_20251216_122325.csv`

**Prototype 3: Multi-Voice SSML Generation**
- **Goal:** Validate Azure accepts voice switching and generates quality audio
- **Results:**
  - ✅ SSML generation: SUCCESS (valid multi-voice SSML)
  - ✅ Azure synthesis: SUCCESS (233.7 KB audio, ~7.5s duration)
  - ✅ Voice switching: 5 characters mapped to Azure voices
  - ✅ Prosody support: rate, pitch, volume tags validated
  - ✅ Voice assignments:
    - Narrator: ar-EG-SalmaNeural (female, Egyptian)
    - أحمد: ar-EG-ShakirNeural (male, Egyptian)
    - فاطمة: ar-SA-ZariyahNeural (female, Saudi)
    - محمود: ar-SA-HamedNeural (male, Saudi)
    - Unknown: ar-EG-ShakirNeural (male, Egyptian)
- **Files:**
  - SSML: `outputs/multivoice_ssml_20251218_223910.xml`
  - Audio: `outputs/multivoice_audio_20251218_223910.mp3`

**Key Learnings:**
1. **CSV Review Pattern Works:** Hierarchical structure with stats rows enables efficient review in Excel
2. **Detection Accuracy Exceeded Target:** 85% high confidence vs 80% target
3. **Low Flag Rate:** Only 5% flagged vs 20% target (algorithm very effective)
4. **Azure Multi-Voice Validated:** Voice switching works seamlessly with prosody control
5. **Dialect Mixing Confirmed:** Can mix ar-EG (Egyptian) and ar-SA (Saudi) in same audiobook

---

## 9. Testing Strategy

### 9.1 Unit Tests (New)
**Scope:** Individual components in isolation
- `test_pdf_extractor.py`:
  - Test TXT file loading (UTF-8 encoding)
  - Test PDF text extraction (sample Arabic PDF)
  - Test paragraph preservation during extraction
  - Test RTL text handling
  - Test file format validation (reject invalid formats)
- `test_character_detector.py`:
  - Test quotation pattern detection (« », " ", ' ', —)
  - Test character name extraction from attribution phrases
  - Test confidence scoring logic
  - Test edge cases (nested quotes, mixed quotations)
  - Test detection summary analytics generation
- `test_ssml_builder.py`:
  - Test SSML generation with single voice
  - Test SSML with multi-dialect voice switching
  - Test XML escaping (special characters)
  - Test prosody tag generation (rate, pitch, volume)
  - Test smart chunking at paragraph boundaries
  - Test chunking never breaks mid-sentence
  - Test paragraph detection (double newline, newline + indent)
- `test_character_config.py`:
  - Test JSON schema validation
  - Test character config loading/saving
  - Test template management
  - Test detection summary analytics in JSON
- `test_voice_reference.py`:
  - Test available_voices.json generation
  - Test Azure voice API querying
  - Test voice validation against reference

**Target:** 60+ unit tests, 90%+ coverage

### 9.2 Integration Tests (New)
**Scope:** End-to-end workflows with real Azure API (use test account)
- `test_file_upload_pipeline.py`:
  - Test TXT file upload → extraction → detection
  - Test PDF file upload → extraction → detection
  - Test large PDF (100+ pages) with progress tracking
- `test_detection_pipeline.py`:
  - Test full detection workflow (text → JSON output)
  - Test chapter splitting
  - Test occurrence counting
  - Test detection summary analytics generation
- `test_json_checkpoint.py`:
  - Test JSON review checkpoint (approval required)
  - Test JSON download/upload workflow
  - Test in-browser JSON editing
  - Test validation (reject malformed JSON)
- `test_chunking_strategy.py`:
  - Test smart chunking with 15k+ character text
  - Test paragraph boundary detection
  - Test no mid-sentence breaks
  - Test audio concatenation across chunks
- `test_audio_generation.py`:
  - Test single-chapter SSML → audio generation
  - Test multi-chapter book processing
  - Test multi-dialect voice switching (3+ voices)
  - Test with/without diacritization
- `test_voice_reference_generation.py`:
  - Test available_voices.json creation on detection
  - Test voice validation against reference
- `test_web_endpoints.py`:
  - Test all `/multivoice/*` endpoints
  - Test existing demo routes unchanged (/, /synthesize)
  - Test progress polling (`/multivoice/progress/<job_id>`)
  - Test error handling (malformed inputs)

**Test Data:** 7 curated test cases:
- 5 Arabic texts (50-500 words each) with known character counts
- 1 sample Arabic PDF (3 pages)
- 1 long text (15k+ characters) for chunking tests
- Reference SSML outputs
- Reference audio files (for quality regression)

**Target:** 20+ integration tests, all passing

### 9.3 Manual QA Testing
**Scope:** Human validation of quality and usability
- **Sample Audiobooks:** Process 3 test books (10k-50k words each):
  1. Simple dialogue (2-3 characters)
  2. Complex dialogue (5+ characters, nested quotes)
  3. Mixed dialects (narrator MSA, characters EG/Gulf)
- **Review Interface Testing:**
  - Validate color-coding clarity
  - Test click-to-reassign workflow
  - Test flagged segments filtering
- **Audio Quality Assessment:**
  - Native Arabic speaker review (pronunciation, naturalness)
  - Verify seamless voice transitions
  - Check for audio artifacts/gaps

**Target:** 3 complete test books processed, 4/5+ quality rating

### 9.4 Debugging & Observability
**Multi-Layer Processing View:**
- Web interface displays 4 processing layers (expandable):
  1. **Raw Text:** Original input with chapter markers
  2. **Detected Characters:** Color-coded segments with confidence
  3. **SSML Output:** Generated XML (formatted, syntax-highlighted)
  4. **Audio Metadata:** Duration, file size, Azure response codes
- Each layer is inspectable (click to expand full details)
- Failed layers are highlighted in red with error messages

**Logging:**
- All detection decisions logged (character assignments, confidence scores)
- Azure API calls logged (request/response, latency, errors)
- Cost tracking logged per book/chapter

---

## 10. Open Questions

### 10.1 Technical Decisions Needed
1. **Chapter Boundary Detection:**
   - Auto-detect via common patterns (e.g., "الفصل الأول", "Chapter 1")?
   - Require user to manually mark chapter breaks?
   - Support both (auto-detect with manual override)?

2. **Confidence Scoring Algorithm:**
   - What factors determine low/medium/high confidence?
   - Suggested: High = direct quote with attribution, Medium = quote without attribution, Low = ambiguous (no quotes, indirect speech)

3. **Character Name Normalization:**
   - How to handle variations: "أحمد", "احمد", "Ahmed"?
   - Should system auto-merge similar names (fuzzy matching)?

4. **Azure Voice Fallback:**
   - If selected voice is unavailable (Azure API error), default to which voice?
   - Should system auto-select closest alternative (same dialect/gender)?

5. **Job Queue Management:**
   - For multi-user web interface, use background job queue (Celery/RQ)?
   - Or simple in-memory job tracking (MVP)?

### 10.2 Product Decisions Needed
6. **Default Voice Assignments:**
   - Should system pre-assign voices based on gender detection (male → HamedNeural, female → SalmaNeural)?
   - Or leave all voices unassigned, forcing user to choose?

7. **Character Limit per Book:**
   - Should system warn/block books exceeding X characters (to prevent runaway costs)?
   - Suggested limit: 500k characters (~5 books per month on free tier)

8. **Prosody Defaults:**
   - Should narrator voice have different prosody than dialogue (e.g., slower rate)?
   - Or keep all defaults at 1.0/0%/0% for MVP?

9. **Diacritization Testing:**
   - Should we conduct formal A/B test (plain vs diacritized) before MVP launch?
   - Or leave as user-configurable option without official guidance?

10. **Reusable Templates:**
    - Should system include pre-built character configs for common book types?
    - (e.g., "2-character dialogue", "narrator + 3 characters", etc.)

---

## 11. Implementation Phases (Suggested)

### Phase 1: Core Detection & SSML (Weeks 1-2)
**Goal:** Basic file handling, character detection, and smart SSML generation working
- Implement `src/utils/pdf_extractor.py` (TXT and PDF text extraction)
- Implement `src/core/character_detector.py` (quotation parsing, confidence scoring)
- Implement `src/utils/paragraph_detector.py` (paragraph boundary detection)
- Implement `src/utils/ssml_builder.py` (SSML generation with smart chunking)
- Unit tests for PDF extraction, detection, chunking, and SSML
- CLI tool: `python extract_text.py book.pdf --output book.txt`
- CLI tool: `python detect_characters.py book.txt --output chars.json`
- CLI tool: `python generate_ssml.py book.txt chars.json --output book.ssml`

**Deliverable:** Command-line tools producing valid SSML with smart chunking

### Phase 2: Azure Integration & Audio (Weeks 2-3)
**Goal:** Generate actual audio files via Azure with voice reference
- Implement `src/integrations/azure_multivoice.py` (Azure SDK wrapper, voice reference generation)
- Multi-dialect voice switching logic
- Chapter-by-chapter processing
- Voice reference guide generation (available_voices.json)
- Integration tests with real Azure API
- Cost calculation logic

**Deliverable:** CLI tool producing MP3/WAV audio files + voice reference JSON

### Phase 3: Web Interface (Weeks 3-5)
**Goal:** User-friendly web UI with three-step workflow and JSON checkpoint
- Create new template directory: `templates/multivoice/`
- Implement new Flask routes (do NOT modify existing demo routes):
  - `/multivoice` - Landing page
  - `/multivoice/upload` - TXT/PDF upload
  - `/multivoice/detect` - Character detection
  - `/multivoice/review/<book_id>` - JSON review checkpoint (mandatory)
  - `/multivoice/update_config` - Save edited config
  - `/multivoice/generate` - Audio generation
  - `/multivoice/progress/<job_id>` - Progress polling
- Character detection results page (color-coded)
- JSON review/edit interface (download/upload + in-browser editor)
- Voice selection UI with dialect filtering and voice reference display
- Progress tracking UI (chapter-level)
- Cost monitoring dashboard
- Desktop-only CSS (min-width: 1024px)

**Deliverable:** Functional web interface with three-step workflow, existing demo preserved

### Phase 4: Testing & Polish (Weeks 5-6)
**Goal:** Production-ready quality
- Complete test suite (60+ unit, 20+ integration)
- Test PDF extraction with sample Arabic PDFs
- Test smart chunking with 15k+ character texts
- Test JSON checkpoint workflow (approval required)
- Process 3 test audiobooks (manual QA)
- Verify existing demo.html untouched (regression testing)
- Debug multi-layer view implementation
- Performance optimization (chunking, caching)
- Documentation (user guide, API docs)

**Deliverable:** Production-ready MVP with comprehensive tests

### Phase 5: Post-MVP Enhancements (Future)

**Emotion Detection & Prosody Mapping** (when Azure adds style support OR manual implementation):
- Stage direction detection: `(بغضب)` → prosody adjustment
- Punctuation-based hints: `!!!` → louder/faster, `...` → slower
- Prosody presets UI: dropdown with "angry", "sad", "excited" templates
- Emotion-to-prosody mapping rules engine
- IF Azure adds Arabic style support: integrate `<mstts:express-as>` tags

**Prosody Tuning UI:**
- Interactive slider controls for real-time prosody testing
- Character-level prosody presets (save/load templates)
- Per-speech prosody quick-apply buttons
- Visual waveform preview with prosody adjustments

**Other Enhancements:**
- Character templates library (save voice/prosody combos)
- Multi-book character registry (database)
- Advanced confidence scoring (ML-based)
- Real-time audio preview (stream first chapter)
- Cloud storage integration (S3/Azure Blob)

---

## 12. Dependencies & Prerequisites

### 12.1 External Dependencies
- **Azure Cognitive Services account** with Speech API enabled
- **Azure subscription key** and region configured
- **14+ Arabic neural voices** available (verify during implementation)

### 12.2 Internal Dependencies
- Existing Flask app structure (`app.py`)
- Existing character assignment module (`tools/azure_tts/character_voice_assignment.py`)
- Optional: mishkal integration (if diacritization enabled)

### 12.3 Team Dependencies
- **Developer:** Implement core logic, web endpoints, tests
- **QA/Tester:** Manual audiobook quality assessment (native Arabic speaker)
- **User/Stakeholder:** Provide test books, validate review workflow UX

---

## 13. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Azure API rate limiting blocks processing | High | Medium | Implement exponential backoff, queue management |
| Character detection accuracy < 80% | High | Low | Comprehensive test suite, user review workflow |
| Multi-dialect voice switching causes audio artifacts | Medium | Low | Azure SSML validation, integration tests |
| Cost overruns (exceed free tier) | Medium | Medium | Cost warnings, usage tracking dashboard |
| Quotation style variations not detected | Medium | Medium | Support 4+ quotation patterns, extensible regex |
| Review interface too complex (users overwhelmed) | High | Low | Default to flagged segments only, user testing |
| Performance bottleneck (Azure API latency) | Medium | Medium | Optimize chunking, parallel chapter processing |
| Diacritization degrades quality | Low | Low | Default OFF, make opt-in, A/B testing |

---

## 14. Acceptance Criteria (MVP Completion)

### 14.1 Functional Completeness
- [ ] User can upload TXT or PDF files via web interface
- [ ] System extracts Arabic text from PDF with paragraph preservation
- [ ] System detects characters with 80%+ accuracy on test books
- [ ] User must review and approve JSON checkpoint before audio generation
- [ ] User can edit JSON in-browser or download/upload
- [ ] System generates available_voices.json on every detection run
- [ ] User can review detected characters with color-coded UI
- [ ] User can assign Azure voices from multiple dialects
- [ ] System generates valid SSML with smart chunking (paragraph boundaries)
- [ ] System never breaks SSML mid-sentence
- [ ] System produces high-quality MP3/WAV audio files
- [ ] System processes 100k-word book in < 1 hour
- [ ] System displays cost estimate and cumulative usage
- [ ] Existing demo.html functionality preserved (no modifications)

### 14.2 Quality Gates
- [ ] 60+ unit tests passing (90%+ coverage)
- [ ] 20+ integration tests passing (100%)
- [ ] PDF extraction tests pass (sample 3-page Arabic PDF)
- [ ] Smart chunking tests pass (15k+ character text, no mid-sentence breaks)
- [ ] JSON checkpoint tests pass (approval required before generation)
- [ ] 3 test audiobooks processed successfully (manual QA: 4/5+ rating)
- [ ] No audio artifacts at voice boundaries (integration test validation)
- [ ] No audio artifacts at chunk boundaries (integration test validation)
- [ ] Review interface reduces manual work by 70% (user testing)
- [ ] Existing demo routes pass regression tests (unchanged)

### 14.3 Documentation
- [ ] User guide: How to process a book (step-by-step)
- [ ] Developer guide: Architecture, module structure
- [ ] API documentation: Flask endpoints, request/response schemas
- [ ] Testing guide: How to run tests, add new test cases

### 14.4 Production Readiness
- [ ] Error handling for Azure API failures (retry logic, user-friendly messages)
- [ ] Logging for all processing steps (debugging, auditing)
- [ ] Cost monitoring working (estimate vs actual validation)
- [ ] Web interface deployed and accessible (localhost or server)

---

## 15. Appendices

### Appendix A: Azure Arabic Neural Voices (VERIFIED Dec 18, 2025)

**Source:** Live Azure API query (`tools/azure_tts/arabic_voices_capabilities.json`)
**Total:** 32 voices across 16 dialects (2 per dialect: 1 male, 1 female)
**Style Support:** NONE (all voices have `style_list: [""]`)
**Voice Type:** All OnlineNeural

| Dialect Code | Country/Region | Male Voice | Local Name (M) | Female Voice | Local Name (F) |
|--------------|----------------|------------|----------------|--------------|----------------|
| ar-AE | UAE (Gulf) | ar-AE-HamdanNeural | حمدان | ar-AE-FatimaNeural | فاطمة |
| ar-BH | Bahrain (Gulf) | ar-BH-AliNeural | علي | ar-BH-LailaNeural | ليلى |
| ar-DZ | Algeria (Maghreb) | ar-DZ-IsmaelNeural | إسماعيل | ar-DZ-AminaNeural | أمينة |
| ar-EG | Egypt | ar-EG-ShakirNeural | شاكر | ar-EG-SalmaNeural | سلمى |
| ar-IQ | Iraq | ar-IQ-BasselNeural | باسل | ar-IQ-RanaNeural | رنا |
| ar-JO | Jordan (Levantine) | ar-JO-TaimNeural | تيم | ar-JO-SanaNeural | سناء |
| ar-KW | Kuwait (Gulf) | ar-KW-FahedNeural | فهد | ar-KW-NouraNeural | نورا |
| ar-LB | Lebanon (Levantine) | ar-LB-RamiNeural | رامي | ar-LB-LaylaNeural | ليلى |
| ar-LY | Libya (Maghreb) | ar-LY-OmarNeural | أحمد | ar-LY-ImanNeural | إيمان |
| ar-MA | Morocco (Maghreb) | ar-MA-JamalNeural | جمال | ar-MA-MounaNeural | منى |
| ar-OM | Oman (Gulf) | ar-OM-AbdullahNeural | عبدالله | ar-OM-AyshaNeural | عائشة |
| ar-QA | Qatar (Gulf) | ar-QA-MoazNeural | معاذ | ar-QA-AmalNeural | أمل |
| ar-SA | Saudi Arabia (MSA) | ar-SA-HamedNeural | حامد | ar-SA-ZariyahNeural | زارية |
| ar-SY | Syria (Levantine) | ar-SY-LaithNeural | ليث | ar-SY-AmanyNeural | أماني |
| ar-TN | Tunisia (Maghreb) | ar-TN-HediNeural | هادي | ar-TN-ReemNeural | ريم |
| ar-YE | Yemen | ar-YE-SalehNeural | صالح | ar-YE-MaryamNeural | مريم |

**NOTE:** No emotional styles (`<mstts:express-as>`) supported for ANY Arabic voice. Character differentiation achieved through: voice selection, dialect mixing, gender, and prosody (rate/pitch/volume).

### Appendix B: JSON Schema (SIMPLIFIED - NO Emotion/Style Fields)

**Design Decision:** Keep JSON light. No emotion/style fields since Azure doesn't support `<mstts:express-as>` for Arabic voices. Character differentiation via prosody adjustment only.

```json
{
  "book_title": "رواية تجريبية",
  "total_characters": 150000,
  "estimated_cost_usd": 2.40,
  "diacritization_enabled": false,
  "chapters": [
    {
      "chapter_num": 1,
      "chapter_title": "الفصل الأول",
      "character_count": 12500,
      "characters": [
        {
          "name": "Narrator",
          "dialect": "ar-SA",
          "gender": "male",
          "voice_id": "ar-SA-HamedNeural",
          "local_name": "حامد",
          "occurrence_count": 45,
          "speech_count": 45,
          "prosody": {
            "rate": 1.0,
            "pitch": "0%",
            "volume": "0%"
          }
        },
        {
          "name": "أحمد",
          "dialect": "ar-EG",
          "gender": "male",
          "voice_id": "ar-EG-ShakirNeural",
          "local_name": "شاكر",
          "occurrence_count": 28,
          "speech_count": 18,
          "prosody": {
            "rate": 1.1,
            "pitch": "+5%",
            "volume": "0%"
          }
        }
      ],
      "segments": [
        {
          "segment_id": 1,
          "text": "كان يوما جميلا في القاهرة",
          "character": "Narrator",
          "confidence": "high"
        },
        {
          "segment_id": 2,
          "text": "«مرحبا يا فاطمة»",
          "character": "أحمد",
          "confidence": "high",
          "prosody_override": {
            "rate": 1.2,
            "pitch": "+10%",
            "volume": "+5%"
          }
        }
      ]
    }
  ],
  "detection_summary": {
    "total_speeches": 195,
    "characters_by_frequency": [
      {"name": "Narrator", "speeches": 150},
      {"name": "أحمد", "speeches": 28}
    ],
    "chapter_breakdown": [
      {
        "chapter": 1,
        "character_speeches": {
          "Narrator": 45,
          "أحمد": 8
        }
      }
    ]
  }
}
```

**Key Fields:**
- `local_name`: Arabic voice name from Azure (e.g., "حامد" for Hamed)
- `prosody`: Character-level defaults (applied to all speeches)
- `prosody_override`: Optional segment-level override (for specific speeches)
- `detection_summary`: Analytics (total speeches, frequency, chapter breakdown)
- ❌ NO `style`, `emotion`, `stage_direction` fields (not supported by Azure)

### Appendix C: SSML Output Example (with Smart Chunking)
```xml
<!-- Chunk 1 (9,800 characters, ends at paragraph boundary) -->
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-SA">
  <!-- Narrator segment -->
  <voice name="ar-SA-HamedNeural">
    <prosody rate="1.0" pitch="0%" volume="0%">
      كان يوما جميلا في القاهرة
    </prosody>
  </voice>

  <!-- Character: أحمد (Egyptian dialect) -->
  <voice name="ar-EG-ShakirNeural">
    <prosody rate="1.1" pitch="+5%" volume="0%">
      مرحبا يا فاطمة
    </prosody>
  </voice>

  <!-- Narrator segment -->
  <voice name="ar-SA-HamedNeural">
    <prosody rate="1.0" pitch="0%" volume="0%">
      قال أحمد بحماس
    </prosody>
  </voice>

  <!-- Character: فاطمة (MSA dialect) -->
  <voice name="ar-SA-ZariyahNeural">
    <prosody rate="0.95" pitch="-3%" volume="+5%">
      أهلا أحمد، كيف حالك؟
    </prosody>
  </voice>

  <!-- ... more content ... -->
  <!-- Chunk ends at complete paragraph, NOT mid-sentence -->
</speak>

<!-- Chunk 2 (9,500 characters, starts at next paragraph) -->
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-SA">
  <!-- Next paragraph continues here -->
  <voice name="ar-SA-HamedNeural">
    <prosody rate="1.0" pitch="0%" volume="0%">
      في اليوم التالي...
    </prosody>
  </voice>
  <!-- ... -->
</speak>
```

### Appendix D: Available Voices Reference JSON (Actual Format)

**Source:** `tools/azure_tts/arabic_voices_capabilities.json` (live Azure API query)
**Purpose:** Generated on every detection run for user reference during voice assignment

```json
{
  "query_timestamp": "2025-12-18T20:34:57.665873",
  "azure_region": "eastus",
  "total_voices_available": 617,
  "arabic_voices_count": 32,
  "dialects": {
    "ar-SA": {
      "locale": "ar-SA",
      "voices": [
        {
          "short_name": "ar-SA-HamedNeural",
          "local_name": "حامد",
          "gender": "male",
          "voice_type": "OnlineNeural",
          "style_list": [""],
          "role_play_list": []
        },
        {
          "short_name": "ar-SA-ZariyahNeural",
          "local_name": "زارية",
          "gender": "female",
          "voice_type": "OnlineNeural",
          "style_list": [""],
          "role_play_list": []
        }
      ]
    },
    "ar-EG": {
      "locale": "ar-EG",
      "voices": [
        {
          "short_name": "ar-EG-ShakirNeural",
          "local_name": "شاكر",
          "gender": "male",
          "voice_type": "OnlineNeural",
          "style_list": [""],
          "role_play_list": []
        },
        {
          "short_name": "ar-EG-SalmaNeural",
          "local_name": "سلمى",
          "gender": "female",
          "voice_type": "OnlineNeural",
          "style_list": [""],
          "role_play_list": []
        }
      ]
    }
    // ... 14 more dialects (ar-AE, ar-BH, ar-DZ, ar-IQ, ar-JO, ar-KW, ar-LB,
    //     ar-LY, ar-MA, ar-OM, ar-QA, ar-SY, ar-TN, ar-YE)
  }
}
```

**Key Observations:**
- `style_list: [""]` for ALL Arabic voices → NO emotional style support
- `role_play_list: []` for all → NO role-play support
- All voices are `OnlineNeural` type (high quality)
- Each dialect has exactly 2 voices (1 male, 1 female)
- `local_name` provides Arabic name for UI display

**Storage:** `outputs/<book_name>/available_voices_<timestamp>.json`

---

**End of PRD**

---

## Next Steps

1. **Review & Approve PRD:** Stakeholder validation (user confirms scope, priorities)
2. **Technical Spike:** Prototype character detection algorithm (1-2 days)
3. **Invoke `2-generate-tasks` Agent:** Generate granular task list from this PRD
4. **Begin Phase 1 Implementation:** Core detection & SSML module development

---

**Document Storage:** `/home/hamr/PycharmProjects/ArabicTTS/tasks/0001-prd-azure-multivoice-character-assignment.md`
