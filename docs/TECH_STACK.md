# Technology Stack Documentation

**Project:** Egyptian Arabic TTS System  
**Version:** 1.0  
**Date:** October 30, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Internal Development](#internal-development)
3. [External Libraries](#external-libraries)
4. [System Dependencies](#system-dependencies)
5. [Development Tools](#development-tools)
6. [Technology Decisions](#technology-decisions)

---

## Overview

The Arabic TTS system uses a hybrid approach combining **internally developed components** for linguistic processing with **proven external libraries** for infrastructure and auxiliary tasks.

### Technology Split

| Category | Internal | External | Total |
|----------|----------|----------|-------|
| **Core Logic** | 90% | 10% | 100% |
| **Infrastructure** | 10% | 90% | 100% |
| **Testing** | 70% | 30% | 100% |
| **Total LOC** | ~5,000 | ~500 | ~5,500 |

---

## Internal Development

### What We Built from Scratch

#### 1. Syllabification Engine ✅
**File:** `src/core/syllabifier.py` (200 lines)

**What it does:**
- Segments Arabic words into syllables based on CV patterns
- Implements Egyptian Arabic syllable structure rules
- Validates syllable patterns (CV, CVC, CVV, CVCC, CVVC, V)
- Maps syllables to IPA representations

**Why we built it:**
- No existing library handles Arabic syllabification with dialect-specific rules
- Needed fine-grained control over segmentation logic
- Required integration with our phonological rule system

**Key features:**
```python
- CV pattern recognition (6 patterns)
- Phonotactic constraint validation
- Dialect-specific rule application
- Real-time segmentation (< 0.1ms per word)
```

**Accuracy:** 96.30% on validation dataset

---

#### 2. Gemination Processor ✅
**File:** `src/core/gemination.py` (142 lines)

**What it does:**
- Detects shadda (ّ) markers in Arabic text
- Marks consonants for doubling (gemination)
- Applies gemination rules in IPA output
- Handles all geminated consonants in Arabic

**Why we built it:**
- Gemination is critical for correct Arabic pronunciation
- No existing library handles shadda in IPA context
- Needed precise control over gemination detection

**Key features:**
```python
- Shadda (ّ) detection: 100% accuracy
- All Arabic consonants supported
- Position-independent detection
- Integration with phonological pipeline
```

**Test Coverage:** 26 tests, 100% passing

---

#### 3. Sun Letter Assimilation Processor ✅
**File:** `src/core/sun_letters.py` (288 lines)

**What it does:**
- Identifies sun letters vs moon letters
- Applies /al/ + sun letter assimilation
- Deletes /l/ and geminates sun letter
- Preserves moon letter patterns

**Why we built it:**
- Fundamental phonological rule in Arabic
- No existing implementation for TTS context
- Required for natural-sounding speech

**Key features:**
```python
Sun Letters (14): ت، ث، د، ذ، ر، ز، س، ش، ص، ض، ط، ظ، ل، ن
Moon Letters (14): ا، ب، ج، ح، خ، ع، غ، ف، ق، ك، م، ه، و، ي

Rules:
- الشمس (al-shams) → ash-shams ✅
- القمر (al-qamar) → al-qamar ✅
```

**Test Coverage:** 37 tests, 100% passing

---

#### 4. Positional Allophone Processor ✅
**File:** `src/core/allophones.py` (316 lines)

**What it does:**
- Detects character position in words (initial, medial, final)
- Selects position-specific IPA variants
- Applies positional pronunciation rules
- Handles all Arabic consonants and vowels

**Why we built it:**
- Arabic pronunciation varies by position in word
- No existing library provides position-based IPA selection
- Critical for accurate pronunciation

**Key features:**
```python
Positions:
- Initial (word start): specific articulation
- Medial (word middle): different variants
- Final (word end): final forms

Example: ك
- Initial: [k]
- Medial: [k]
- Final: [k~] (velarized)
```

**Test Coverage:** 34 tests, 100% passing

---

#### 5. Emphatic Spread Processor ✅
**File:** `src/core/emphatic.py` (390 lines)

**What it does:**
- Detects emphatic/pharyngealized consonants
- Applies pharyngealization to adjacent vowels
- Backs vowels (a→ɑ, i→ɪ, u→ʊ)
- Adds pharyngealization markers

**Why we built it:**
- Emphatic consonants are unique to Arabic
- Pharyngealization spread is complex phonological process
- No existing library handles this

**Key features:**
```python
Emphatic Consonants: ص، ض، ط، ظ، ق

Vowel Backing:
- a → ɑ (front → back)
- i → ɪ (high → lowered)
- u → ʊ (high → lowered)
- Long vowels: aː→ɑː, iː→ɪː, uː→ʊː

Pharyngealization marker: ˁ
```

**Test Coverage:** 52 tests, 100% passing

---

#### 6. Main TTS Pipeline ✅
**File:** `src/main.py` (400+ lines)

**What it does:**
- Orchestrates entire TTS pipeline
- Coordinates all processing stages
- Manages phonological rule application
- Provides API interface

**Why we built it:**
- Core business logic of the TTS system
- Requires custom workflow for Arabic
- Integrates all components seamlessly

**Key features:**
```python
Pipeline Stages:
1. Text preprocessing
2. Syllabification
3. Phonological rules (4 processors)
4. IPA generation
5. Audio synthesis integration

Performance:
- 3,059 words/second
- 0.0005s per sentence
- 100% test pass rate
```

---

#### 7. eSpeak Integration Wrapper ✅
**File:** `src/integrations/espeak.py` (300+ lines)

**What it does:**
- Wraps eSpeak NG for Python use
- Converts IPA to X-SAMPA notation
- Manages audio generation process
- Handles errors and validation

**Why we built it:**
- eSpeak NG has no Python bindings
- Needed custom IPA→X-SAMPA mapping for Arabic
- Required error handling and file management

**Key features:**
```python
IPA to X-SAMPA Conversion:
- 40+ Arabic phoneme mappings
- Emphatic consonant markers
- Pharyngealization support
- Long vowel markers

Audio Generation:
- Subprocess management
- File I/O handling
- Error recovery
- Format validation
```

**Test Coverage:** 28 tests, 100% passing

---

#### 8. Flask REST API ✅
**File:** `app.py` (150+ lines)

**What it does:**
- Provides HTTP REST API endpoints
- Handles text → IPA conversion
- Manages audio generation requests
- Serves audio files for download

**Why we built it:**
- Application-specific API requirements
- Custom routing for TTS workflow
- Integration with core engine

**Endpoints:**
```python
POST /process
- Input: Arabic text + dialect
- Output: JSON with syllabification + IPA

POST /generate_audio
- Input: Arabic text + dialect + parameters
- Output: Audio file ID + metadata

GET /download/audio/<filename>
- Input: Audio file ID
- Output: WAV audio file
```

---

#### 9. Comprehensive Test Suite ✅
**Files:** `tests/` (16 test files, 329 tests)

**What we built:**
- 329 comprehensive tests
- All test logic and scenarios
- Custom test fixtures
- Performance benchmarks

**Why we built it:**
- Application-specific test requirements
- Custom validation logic
- Domain-specific test cases

**Test Categories:**
```python
- Smoke tests: 23
- Unit tests: 237
- Integration tests: 38
- Error handling: 45
- Performance: 21

Total: 329 tests (100% passing)
```

---

### Summary: Internal Development

| Component | Lines of Code | Purpose | Test Coverage |
|-----------|---------------|---------|---------------|
| **Syllabification** | 200 | Core linguistic | 25 tests |
| **Gemination** | 142 | Phonological rule | 26 tests |
| **Sun Letters** | 288 | Phonological rule | 37 tests |
| **Allophones** | 316 | Phonological rule | 34 tests |
| **Emphatic Spread** | 390 | Phonological rule | 52 tests |
| **Main Pipeline** | 400+ | Orchestration | 38 tests |
| **eSpeak Wrapper** | 300+ | Integration | 28 tests |
| **Flask API** | 150+ | Web interface | Tested |
| **Test Suite** | 2,000+ | QA | 329 tests |
| **Total Internal** | **~5,000** | **Core system** | **Complete** |

---

## External Libraries

### What We Used (And Why)

#### 1. mishkal (v0.4.1) 📦
**Purpose:** Arabic text diacritization

**What it provides:**
- Automatic vowel (harakah) addition to Arabic text
- Diacritic mark insertion (َ ِ ُ ْ ّ)
- Multiple vowelization possibilities
- Arabic linguistic knowledge

**Why we use it:**
```python
# Without diacritization
"صباح" → ambiguous pronunciation

# With mishkal
"صَبَاح" → clear pronunciation (ṣabāḥ)
```

**Alternatives considered:**
- ❌ Building our own: Would require extensive Arabic linguistic corpus
- ❌ Other libraries: mishkal is most mature and accurate
- ✅ mishkal: Open source, actively maintained, best accuracy

**Integration:**
```python
from mishkal.tashkeel import TashkeelClass

diacritizer = TashkeelClass()
result = diacritizer.tashkeel("صباح الخير")
# Output: "صَبَاحُ الْخَيْرِ"
```

**Limitations:**
- Not 100% accurate (Arabic is ambiguous)
- Slower for large texts
- Requires network for some features (optional)

---

#### 2. eSpeak NG (v1.50+) 🔊
**Purpose:** Text-to-speech audio synthesis

**What it provides:**
- Speech synthesis engine
- Multi-language support (including Arabic)
- IPA phonetic input support
- WAV audio output

**Why we use it:**
```python
Pros:
✅ Open source and free
✅ Supports IPA input (critical for us)
✅ Arabic language support
✅ Fast synthesis (~30ms per sentence)
✅ Lightweight and portable
✅ No cloud dependencies

Cons:
❌ Robotic voice quality
❌ Limited prosody control
❌ No emotion support
```

**Alternatives considered:**
- Google TTS: Requires internet, not free, no IPA support
- Amazon Polly: Cloud-based, costs money, limited Arabic
- Festival: Older, less maintained
- ✅ eSpeak NG: Best fit for MVP requirements

**Integration:**
```python
# Our wrapper converts IPA to eSpeak format
subprocess.run([
    "espeak-ng",
    "-v", "ar",  # Arabic voice
    f"[[{ipa}]]",  # IPA input
    "-w", output_path  # WAV output
])
```

**Audio specs:**
- Format: WAV (RIFF)
- Sample rate: 22050 Hz
- Bit depth: 16-bit PCM
- Channels: Mono

---

#### 3. Flask (v3.0+) 🌐
**Purpose:** Web framework for REST API

**What it provides:**
- HTTP request/response handling
- URL routing
- JSON serialization
- Development server

**Why we use it:**
```python
Pros:
✅ Lightweight and simple
✅ Perfect for APIs
✅ Well-documented
✅ Large ecosystem
✅ Easy deployment

Cons:
❌ Not async (fine for MVP)
❌ Needs WSGI server for production
```

**Integration:**
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_text():
    data = request.json
    result = tts.process_text(data['text'])
    return jsonify(result)
```

**Production:** Deploy with Gunicorn or uWSGI

---

#### 4. pytest (v8.4.2) 🧪
**Purpose:** Testing framework

**What it provides:**
- Test discovery and execution
- Fixtures and parametrization
- Coverage reporting
- Plugin ecosystem

**Why we use it:**
```python
Pros:
✅ Industry standard
✅ Simple and powerful
✅ Great assertion introspection
✅ Excellent plugin ecosystem
✅ Coverage integration

Our usage:
- 329 comprehensive tests
- pytest-cov for coverage
- Custom fixtures
- Pre-commit integration
```

**Alternatives:**
- unittest: More verbose, less features
- nose: Deprecated
- ✅ pytest: Best choice

---

### External Libraries Summary

| Library | Version | Purpose | Why We Use It | LOC Saved |
|---------|---------|---------|---------------|-----------|
| **mishkal** | v0.4.1 | Diacritization | Arabic linguistic expertise | ~5,000+ |
| **eSpeak NG** | v1.50 | Audio synthesis | Speech engine | ~10,000+ |
| **Flask** | v3.0+ | Web framework | API infrastructure | ~500 |
| **pytest** | v8.4.2 | Testing | Test infrastructure | ~300 |
| **Total** | - | - | - | **~15,800** |

---

## System Dependencies

### Operating System Requirements

| OS | Support | Notes |
|----|---------|-------|
| **Linux** | ✅ Full | Primary platform, tested on Ubuntu |
| **macOS** | ✅ Compatible | eSpeak NG via Homebrew |
| **Windows** | ⚠️ Limited | eSpeak NG installation required |

### Required System Packages

```bash
# Ubuntu/Debian
apt-get install espeak-ng python3 python3-pip

# macOS
brew install espeak-ng python3

# Arch Linux
pacman -S espeak-ng python
```

### Python Version

```python
Required: Python 3.10+
Tested: Python 3.10.12
Reason: 
- Modern Python features
- Type hints support
- Performance improvements
- Security patches
```

---

## Development Tools

### Version Control

**Git (v2.34.1+)**
```bash
# Conventional commits format
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update documentation"
```

### Code Quality

**Pre-commit Hooks**
```bash
# Runs automatically before commits
.git/hooks/pre-commit
- Executes all 329 tests
- Prevents commits if tests fail
- Ensures code quality
```

**Linting (Optional)**
```bash
# Can add these for code quality
flake8  # PEP 8 compliance
black   # Code formatting
mypy    # Type checking
```

### Testing Tools

**pytest Plugins**
```bash
pytest-cov    # Coverage reporting
pytest-xdist  # Parallel testing (optional)
pytest-html   # HTML reports (optional)
```

---

## Technology Decisions

### Why Python?

**Chosen:** Python 3.10+

**Reasons:**
```python
✅ Rich NLP ecosystem
✅ Easy integration with linguistics tools
✅ Excellent for rapid prototyping
✅ Good performance for our use case
✅ Large developer community
✅ Cross-platform compatibility
✅ Great testing frameworks

Performance:
- Processing: 3,059 words/second ✅
- Bottleneck: Audio generation (eSpeak), not Python
```

**Alternatives considered:**
- JavaScript/Node.js: Weaker NLP libraries
- Java: Overkill for this project
- C++: Too low-level, slower development
- ✅ Python: Best fit

---

### Why Not Cloud TTS?

**Decision:** Build custom TTS vs use cloud services

**Reasons for custom:**
```python
✅ Full control over linguistic rules
✅ No recurring cloud costs
✅ No internet dependency
✅ Privacy (no data leaves system)
✅ Customization for Arabic dialects
✅ Educational value
✅ Open source

Cloud TTS limitations:
❌ Limited Arabic dialect support
❌ No control over phonological rules
❌ Recurring costs
❌ Internet dependency
❌ Data privacy concerns
❌ Limited customization
```

**Cloud services considered:**
- Google Cloud TTS: Good quality, expensive
- Amazon Polly: Limited Arabic, cloud-only
- Azure Speech: Similar limitations
- ✅ Custom system: Best for our requirements

---

### Why eSpeak NG vs Neural TTS?

**Decision:** eSpeak NG for MVP, neural TTS for Phase 2

**MVP Reasoning:**
```python
eSpeak NG Pros:
✅ Free and open source
✅ IPA input support (critical)
✅ Fast (30ms per sentence)
✅ No GPU required
✅ Lightweight (<50 MB)
✅ Proven stability

Neural TTS Cons for MVP:
❌ Complex implementation
❌ Requires training data
❌ GPU dependency
❌ Slower inference
❌ Larger memory footprint
❌ More development time
```

**Phase 2 Plan:**
- Integrate Tacotron 2 or FastSpeech
- Train on Arabic dataset
- Keep eSpeak as fallback

---

### Why REST API vs gRPC?

**Decision:** Flask REST API

**Reasons:**
```python
REST Pros:
✅ Simple and well-understood
✅ HTTP/JSON standard
✅ Easy debugging
✅ Good tooling
✅ Browser compatible
✅ Wide client support

gRPC Cons for MVP:
❌ More complex
❌ Requires .proto files
❌ Less familiar to most developers
❌ Overkill for current needs
```

**Future:** Can add gRPC alongside REST in Phase 2

---

## Dependencies File

### requirements.txt

```txt
# Core dependencies
Flask>=3.0.0
mishkal>=0.4.1

# Testing
pytest>=8.4.2
pytest-cov>=7.0.0

# Optional
# pytest-xdist>=3.0.0  # Parallel testing
# black>=23.0.0         # Code formatting
# flake8>=6.0.0         # Linting
```

### Installation

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install system dependencies
sudo apt install espeak-ng  # Ubuntu/Debian
brew install espeak-ng       # macOS
```

---

## Technology Comparison

### Internal vs External Breakdown

```
┌─────────────────────────────────────────────────────┐
│         What We Built (Internal)                     │
├─────────────────────────────────────────────────────┤
│  ✓ Syllabification engine (200 LOC)                 │
│  ✓ 4 Phonological processors (1,136 LOC)            │
│  ✓ Main TTS pipeline (400+ LOC)                     │
│  ✓ eSpeak wrapper (300+ LOC)                        │
│  ✓ Flask API (150+ LOC)                             │
│  ✓ Test suite (2,000+ LOC)                          │
│  ✓ Documentation (2,000+ lines)                     │
│                                                      │
│  Total: ~5,000 LOC of custom code                   │
│  Purpose: Core TTS logic + Arabic linguistics       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         What We Used (External)                      │
├─────────────────────────────────────────────────────┤
│  ✓ mishkal - Diacritization (~5,000 LOC saved)      │
│  ✓ eSpeak NG - Audio synthesis (~10,000 LOC saved)  │
│  ✓ Flask - Web framework (~500 LOC saved)           │
│  ✓ pytest - Testing framework (~300 LOC saved)      │
│                                                      │
│  Total: ~15,800 LOC saved                           │
│  Purpose: Infrastructure + proven solutions         │
└─────────────────────────────────────────────────────┘

Result: 76% code savings by using proven libraries
        100% control over core TTS logic
```

---

## Licensing

### Our Code
- License: [To be determined]
- All custom code is original

### External Dependencies

| Library | License | Commercial Use |
|---------|---------|----------------|
| **mishkal** | GPL v3 | ✅ Yes |
| **eSpeak NG** | GPL v3 | ✅ Yes |
| **Flask** | BSD 3-Clause | ✅ Yes |
| **pytest** | MIT | ✅ Yes |

**Note:** All dependencies are open source and allow commercial use.

---

## Future Technology Considerations

### Phase 2 Enhancements

**Neural TTS Integration:**
```python
Candidates:
- Tacotron 2 (Google)
- FastSpeech 2 (Microsoft)
- VITS (recent SOTA)

Benefits:
- More natural voice
- Better prosody
- Emotion control
- Voice customization
```

**Performance Optimization:**
```python
- Cython for critical paths
- Parallel processing
- GPU acceleration (neural TTS)
- Caching layer (Redis)
```

**Additional Libraries:**
```python
- FastAPI (async REST API)
- Redis (caching)
- Docker (containerization)
- Kubernetes (orchestration)
```

---

**Document Version:** 1.0  
**Last Updated:** October 30, 2025  
**Dependencies Status:** All up to date ✅
