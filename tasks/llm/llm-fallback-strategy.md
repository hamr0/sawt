# Plan: Syllables & Diacritization Documentation + Intelligent Fallback Strategy

## User's Vision & Constraints

**Key Principles:**
1. **IPA is the foundation** - masterTTS.json is source of truth for pronunciation
2. **Keep costs low** - LLM sparingly, build local knowledge over time
3. **Balance accuracy with simplicity** - Practical solutions, not over-engineered
4. **MSA focus now** - Dialectal content comes later
5. **LLM for prosody later** - Post-MVP: emotions, pauses, personalities for audiobooks
6. **Pronunciation first, expressiveness second** - Get the core right before adding flair

## Deliverable 1: Comprehensive Documentation

### File: `docs/SYLLABLES_AND_DIACRITIZATION.md`

**Structure:**

#### 1. The Foundation: Why Diacritization Matters (Introduction)
- Written Arabic ambiguity problem (كتب = 5 different words)
- How diacritics reveal vowels hidden in Arabic script
- Diacritization as prerequisite for all downstream processing

#### 2. Understanding Arabic Syllables
- **What are C and V?**
  - C = Consonant (الحروف الصحيحة)
  - V = Vowel (الحركات والمد)
  - Short vowels: فتحة (َ), ضمة (ُ), كسرة (ِ)
  - Long vowels: ا، و، ي

- **Valid Arabic Syllable Patterns:**
  - CV (open): مَ, لِ
  - CVC (closed): كَتْ, مِنْ
  - CVV (long vowel): كا, لِي
  - CVVC: كتاب → كِتَاب
  - CVCC (complex): كتب → كُتْب

- **Syllable Roles (Onset-Nucleus-Coda):**
  - Onset: Initial consonant(s) starting the syllable
  - Nucleus: The vowel core (V or VV)
  - Coda: Final consonant(s) closing the syllable (optional)

- **Example Breakdown:**
  ```
  Word: كِتَابٌ (kitaabun - "book")

  Step 1: Identify diacritics
  كِ تَ ا ب ٌ

  Step 2: Mark C and V
  C V C V V C V

  Step 3: Apply syllable rules
  CV-CVV-CVC
  ki-taa-bun

  Step 4: Assign syllable roles
  Syllable 1 (ki):   k=onset, i=nucleus
  Syllable 2 (taa):  t=onset, aa=nucleus
  Syllable 3 (bun):  b=onset, u=nucleus, n=coda
  ```

#### 3. The Architecture Pipeline
- **Step 1: Diacritization (Mishkal - MSA-based)**
  - Input: Undiacritized text
  - Output: Text with diacritics
  - Universal for all dialects (same diacritization)

- **Step 2: Syllabification (CV Pattern Detection)**
  - Input: Diacritized text
  - Output: Word broken into syllables with CV patterns
  - Depends entirely on Step 1 (cannot work without vowels!)

- **Step 3: Position Detection**
  - Syllable boundaries define initial/medial/final positions
  - Position affects IPA (e.g., ر in onset vs coda)

- **Step 4: IPA Mapping (Dialect-Specific)**
  - Uses masterTTS.json
  - Same diacritization → Different IPA per dialect
  - Example: قَلْب → [ʔælb] (EG) vs [qalb] (MSA) vs [galb] (Gulf)

#### 4. Why CV Patterns = Syllables = IPA Accuracy
- **Same letters, different syllables = different pronunciation**
- Examples showing how syllable boundaries change meaning
- How syllable role (onset vs coda) affects articulation

#### 5. The UNKNOWN Pattern Problem
- **What UNKNOWN means**: Syllabification failure (not a syllable type!)
- **When it occurs:**
  - Diacritization failed (Mishkal returned undiacritized text)
  - Word doesn't match Arabic syllable rules
  - Proper nouns, foreign words, colloquialisms
- **System behavior**: Graceful fallback to character-level IPA lookup

#### 6. How Position Affects IPA
- Character-in-word position vs syllable role
- Examples of same consonant in different positions
- Why masterTTS.json has initial/medial/final entries

#### 7. Mishkal Strengths & Limitations
- **Strengths:** MSA vocabulary, standard grammar, verb conjugations
- **Weaknesses:** Proper nouns (الإسكندرية), dialectal words, place names
- **Architecture decision:** MSA-based diacritization is acceptable because:
  - IPA mapping (Step 4) is where dialect-specific pronunciation happens
  - Even "wrong" MSA diacritics provide syllable structure
  - Character fallback catches edge cases

## PRE-IMPLEMENTATION: Testing Strategy (DO THIS FIRST!)

### Goal: Evaluate CAMeL Tools Before Building Full System

**Critical Decision:** Test CAMeL Tools on known failures to determine if LLM is even needed.

### Test Setup

#### Test Corpus (Known Failures from Dataset)
```python
TEST_WORDS = [
    # Proper nouns (known Mishkal failures)
    "الإسكندرية",  # Alexandria - place name
    "القاهرة",      # Cairo - capital city
    "مصر",          # Egypt
    "محمد",         # Mohammed - person name
    "أحمد",         # Ahmed - person name

    # Common MSA words (should work with both)
    "كتاب",         # Book
    "مدرسة",        # School
    "الطبيعي",      # Natural (known to work)

    # Dialectal/colloquial (might fail both)
    # Add specific examples from your 39.4% failure dataset
]
```

### Test Script 1: Mishkal Only (Baseline)

```python
#!/usr/bin/env python3
"""Test Mishkal diacritization on known failures"""

from mishkal.tashkeel import TashkeelClass
import json

diacritizer = TashkeelClass()

results = {
    "tested": 0,
    "succeeded": 0,
    "failed": 0,
    "details": []
}

TEST_WORDS = [
    "الإسكندرية", "القاهرة", "مصر", "محمد", "أحمد",
    "كتاب", "مدرسة", "الطبيعي"
]

print("=" * 60)
print("MISHKAL BASELINE TEST")
print("=" * 60)

for word in TEST_WORDS:
    diacritized = diacritizer.tashkeel(word).strip()

    # Success = diacritization added (output != input)
    success = diacritized != word and any(c in diacritized for c in 'َُِْ')

    results["tested"] += 1
    if success:
        results["succeeded"] += 1
    else:
        results["failed"] += 1

    results["details"].append({
        "word": word,
        "output": diacritized,
        "success": success
    })

    status = "✓ SUCCESS" if success else "✗ FAILED"
    print(f"{status:12} | {word:15} → {diacritized}")

print("\n" + "=" * 60)
print(f"SUCCESS RATE: {results['succeeded']}/{results['tested']} = {results['succeeded']/results['tested']*100:.1f}%")
print("=" * 60)

# Save results
with open('test_results_mishkal.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

### Test Script 2: CAMeL Tools Only

```python
#!/usr/bin/env python3
"""Test CAMeL Tools diacritization on known failures"""

from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.tokenizers.word import simple_word_tokenize
import json

print("Loading CAMeL Tools (this may take 30-60 seconds)...")
mle = MLEDisambiguator.pretrained()

results = {
    "tested": 0,
    "succeeded": 0,
    "failed": 0,
    "details": []
}

TEST_WORDS = [
    "الإسكندرية", "القاهرة", "مصر", "محمد", "أحمد",
    "كتاب", "مدرسة", "الطبيعي"
]

print("=" * 60)
print("CAMEL TOOLS TEST")
print("=" * 60)

for word in TEST_WORDS:
    try:
        tokens = simple_word_tokenize(word)
        disambig = mle.disambiguate(tokens)

        # Extract diacritized form
        diacritized = ''.join([d.diac for d in disambig])

        # Success = diacritization added
        success = diacritized != word and any(c in diacritized for c in 'َُِْ')

        results["tested"] += 1
        if success:
            results["succeeded"] += 1
        else:
            results["failed"] += 1

        results["details"].append({
            "word": word,
            "output": diacritized,
            "success": success
        })

        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status:12} | {word:15} → {diacritized}")

    except Exception as e:
        print(f"✗ ERROR     | {word:15} → {str(e)[:30]}")
        results["tested"] += 1
        results["failed"] += 1
        results["details"].append({
            "word": word,
            "output": None,
            "success": False,
            "error": str(e)
        })

print("\n" + "=" * 60)
print(f"SUCCESS RATE: {results['succeeded']}/{results['tested']} = {results['succeeded']/results['tested']*100:.1f}%")
print("=" * 60)

# Save results
with open('test_results_camel.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

### Test Script 3: Side-by-Side Comparison

```python
#!/usr/bin/env python3
"""Compare Mishkal vs CAMeL Tools on same words"""

from mishkal.tashkeel import TashkeelClass
from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.tokenizers.word import simple_word_tokenize
import json

print("Loading libraries...")
mishkal = TashkeelClass()
print("Loading CAMeL Tools (may take 30-60 seconds)...")
camel = MLEDisambiguator.pretrained()

TEST_WORDS = [
    "الإسكندرية", "القاهرة", "مصر", "محمد", "أحمد",
    "كتاب", "مدرسة", "الطبيعي"
]

results = []

print("\n" + "=" * 80)
print("MISHKAL vs CAMEL TOOLS COMPARISON")
print("=" * 80)
print(f"{'Word':<15} | {'Mishkal':<25} | {'CAMeL':<25} | {'Winner'}")
print("-" * 80)

for word in TEST_WORDS:
    # Mishkal
    mishkal_output = mishkal.tashkeel(word).strip()
    mishkal_success = mishkal_output != word and any(c in mishkal_output for c in 'َُِْ')

    # CAMeL
    try:
        tokens = simple_word_tokenize(word)
        disambig = camel.disambiguate(tokens)
        camel_output = ''.join([d.diac for d in disambig])
        camel_success = camel_output != word and any(c in camel_output for c in 'َُِْ')
        camel_error = None
    except Exception as e:
        camel_output = None
        camel_success = False
        camel_error = str(e)[:30]

    # Determine winner
    if mishkal_success and camel_success:
        winner = "BOTH ✓✓"
    elif mishkal_success and not camel_success:
        winner = "Mishkal ✓"
    elif camel_success and not mishkal_success:
        winner = "CAMeL ✓"
    else:
        winner = "NEITHER ✗"

    print(f"{word:<15} | {mishkal_output:<25} | {str(camel_output or 'ERROR'):<25} | {winner}")

    results.append({
        "word": word,
        "mishkal": {
            "output": mishkal_output,
            "success": mishkal_success
        },
        "camel": {
            "output": camel_output,
            "success": camel_success,
            "error": camel_error
        },
        "winner": winner
    })

print("=" * 80)

# Calculate statistics
mishkal_wins = sum(1 for r in results if "Mishkal" in r["winner"])
camel_wins = sum(1 for r in results if "CAMeL" in r["winner"])
both_wins = sum(1 for r in results if "BOTH" in r["winner"])
neither_wins = sum(1 for r in results if "NEITHER" in r["winner"])

print("\nSUMMARY:")
print(f"  Mishkal only:  {mishkal_wins}")
print(f"  CAMeL only:    {camel_wins}")
print(f"  Both worked:   {both_wins}")
print(f"  Neither worked: {neither_wins}")
print(f"\n  CAMeL advantage: {camel_wins} words Mishkal couldn't handle")
print("=" * 80)

# Save results
with open('test_results_comparison.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nResults saved to test_results_comparison.json")
```

### Decision Matrix Based on Test Results

```
┌─────────────────────────────────────────────────────────────────┐
│  CAMeL Catches 80%+ of Mishkal Failures                         │
├─────────────────────────────────────────────────────────────────┤
│  DECISION: Use Exception Dict + Mishkal + CAMeL                 │
│  LLM Status: OPTIONAL (luxury feature)                          │
│  Cost: $0/month                                                  │
│  Implementation: Tiers 1-2-3 only                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CAMeL Catches 40-80% of Mishkal Failures                       │
├─────────────────────────────────────────────────────────────────┤
│  DECISION: Use Exception Dict + Mishkal + CAMeL + LLM           │
│  LLM Status: Recommended for remaining edge cases               │
│  Cost: <$5/month (only 5-10% of words)                          │
│  Implementation: Full 5-tier system                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CAMeL Catches <40% of Mishkal Failures (or too slow)           │
├─────────────────────────────────────────────────────────────────┤
│  DECISION: Skip CAMeL, use Exception Dict + Mishkal + LLM       │
│  LLM Status: Primary fallback                                   │
│  Cost: $10-15/month                                              │
│  Implementation: 4-tier system (no CAMeL)                        │
└─────────────────────────────────────────────────────────────────┘
```

### Testing Checklist

- [ ] Install CAMeL Tools: `pip install camel-tools`
- [ ] Run Test Script 1 (Mishkal baseline)
- [ ] Run Test Script 2 (CAMeL standalone)
- [ ] Run Test Script 3 (Side-by-side comparison)
- [ ] Review JSON output files
- [ ] Make decision based on Decision Matrix
- [ ] Update plan with chosen architecture
- [ ] Proceed with implementation

### Expected Testing Time
- Script writing: 10 minutes
- CAMeL Tools download/install: 5 minutes
- Model loading (first time): 1-2 minutes
- Running tests: 5 minutes
- Analysis: 10 minutes
**Total: ~30 minutes**

---

## Deliverable 2: Intelligent Diacritization Fallback System

**NOTE: Architecture below will be finalized AFTER testing CAMeL Tools**

### Architecture: Multi-Tiered Fallback (Post-Testing)

**NOTE**: Final architecture depends on test results. Run tests first!

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT: Undiacritized Text                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  TIER 1: Mishkal (Current - Fast, Free)                         │
│  - MSA-based statistical diacritization                         │
│  - Works well for: 80%+ of MSA vocabulary                       │
│  - Free, fast, offline                                          │
└─────────────────────────────────────────────────────────────────┘
         │ Success: Continue to syllabification
         │ Failure: Continue to Tier 2 (based on test results)
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  TIER 2: CAMeL Tools (Research-Grade, Free, Slower)            │
│  - Columbia University NLP lab                                  │
│  - Better at proper nouns than Mishkal                          │
│  - Morphological analyzer + diacritization                      │
│  - Some dialectal support (including Egyptian)                  │
│  - Install: pip install camel-tools                             │
│  - Heavier (300MB models) but more accurate                     │
│  - TODO: Test to determine if worthwhile                        │
└─────────────────────────────────────────────────────────────────┘
         │ Success: Continue to syllabification
         │ Failure: Continue to Tier 3 (if enabled)
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  TIER 3: LLM Fallback (Optional, User Bears Cost)              │
│  - Only if user opts in via config                             │
│  - User responsible for API costs                               │
│  - Structured JSON prompt (examples below)                      │
│  - JSON response stored for future use                          │
│  - Token usage stats tracked per request                        │
│  - Pluggable provider (Claude, OpenAI, etc.)                    │
│  - TODO: Implement after testing free tools                     │
└─────────────────────────────────────────────────────────────────┘
         │ Success: Continue to syllabification
         │ Failure: Continue to Tier 4
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  TIER 4: Character-Level Fallback (Safety Net)                  │
│  - Already implemented (current fix!)                           │
│  - Direct masterTTS.json lookup per character                   │
│  - Status marked as "diac" failure in Failed_Layers            │
└─────────────────────────────────────────────────────────────────┘
```

### Exception Dictionary (Future Enhancement)

**When to implement**: AFTER testing shows which words consistently fail
**Purpose**: Cache successful diacritizations to avoid repeated API calls
**Priority**: LOW - Only implement if using LLM and want to reduce costs

### Implementation Details

#### Exception Dictionary Schema (FUTURE - Not Needed Yet)

**File**: `data/dictionaries/diacritization_exceptions.json` (NOT CREATED YET)
**Purpose**: Cache diacritizations to avoid repeated LLM calls
**When**: Only implement if using LLM and want to reduce costs
**Starting State**: Empty, populated as LLM diacritizes words

**Structure (User Specification):**
```json
{
  "version": "1.0",
  "last_updated": "2025-01-16T10:30:00Z",
  "entries": {
    "الإسكندرية": {
      "diacritized": "الإِسْكَنْدَرِيَّة",
      "source": "llm",
      "date": "2025-01-16T10:30:00Z",
      "confidence": 0,
      "usage_count": 1,
      "ipa": "ʔælʔɪskændæˈɾɪjjæ",
      "syllable_pattern": "CVCC-CVC-CV-CVC-CV-CV",
      "notes": "Egyptian place name (Alexandria)"
    },
    "القاهرة": {
      "diacritized": "القَاهِرَة",
      "source": "manual",
      "date": "2025-01-16T15:45:00Z",
      "confidence": 1,
      "usage_count": 5,
      "ipa": "ʔælqɑːhɪɾæ",
      "syllable_pattern": "CVC-CVV-CV-CV",
      "notes": "Capital city (Cairo) - validated"
    }
  },
  "statistics": {
    "total_entries": 2,
    "unvalidated_entries": 1,
    "validated_entries": 1
  }
}
```

**Field Definitions:**
- `diacritized`: Fully diacritized Arabic word
- `source`: "manual" | "llm" | "camel" | "mishkal"
- `date`: ISO 8601 timestamp (format: YYYY-MM-DDTHH:MM:SSZ for consistency and sortability)
- `confidence`: 0 (LLM output, not validated) | 1 (human validated)
- `usage_count`: How many times this word has been looked up
- `ipa`: Expected IPA pronunciation (optional, for validation)
- `syllable_pattern`: Expected syllable structure (optional)
- `notes`: Free-form text (optional)

#### File 2: `src/core/diacritization_fallback.py` (NEW)
**Purpose:** Orchestrate multi-tiered fallback logic

**Key Components:**

1. **ExceptionDictionary class**
   - Load/save exceptions.json
   - Fast lookup by word
   - Add new entries with metadata

2. **LLMDiacritizer class (optional)**
   - Wrapper for Claude/OpenAI API
   - Rate limiting and quota tracking
   - Prompt engineering for Arabic diacritization
   - Validation workflow

3. **DiacritizationFallbackOrchestrator class**
   - Main entry point
   - Calls tiers in order
   - Tracks which tier succeeded for each word
   - Logs failures for analysis

#### File 3: `src/core/llm_diacritizer.py` (NEW, Optional)
**Purpose:** LLM integration for diacritization with structured JSON responses

**Features:**

**1. Structured JSON Prompt (User Requirement #8):**

```python
DIACRITIZATION_PROMPT = """You are an expert in Arabic diacritization (تشكيل).

Task: Add full diacritics to the Arabic word provided below.

Rules:
- Add all tashkeel marks (fatha, kasra, damma, sukun, shadda, tanween)
- Use Modern Standard Arabic (MSA) rules
- For proper nouns, use standard Arabic phonetic rules
- Return response in JSON format only

Input word: {word}

Response format (JSON):
{{
  "original": "the undiacritized word",
  "diacritized": "fully diacritized word with all tashkeel",
  "confidence": 0.0 to 1.0 (your confidence in this diacritization),
  "reasoning": "brief explanation of your diacritization choices",
  "word_type": "noun|verb|proper_noun|particle|adjective"
}}

Example 1:
Input: القاهرة
Output:
{{
  "original": "القاهرة",
  "diacritized": "القَاهِرَة",
  "confidence": 0.95,
  "reasoning": "Proper noun (Cairo), standard Arabic pronunciation with fatha on qaf, kasra on ha, final ta marbuta",
  "word_type": "proper_noun"
}}

Example 2:
Input: كتاب
Output:
{{
  "original": "كتاب",
  "diacritized": "كِتَابٌ",
  "confidence": 0.98,
  "reasoning": "Common noun (book), kasra on kaf, fatha on ta, tanween damma on final ba",
  "word_type": "noun"
}}

Example 3:
Input: الإسكندرية
Output:
{{
  "original": "الإسكندرية",
  "diacritized": "الإِسْكَنْدَرِيَّة",
  "confidence": 0.90,
  "reasoning": "Proper noun (Alexandria), Greek origin name with Arabic phonetics. Kasra after hamza, sukun on seen and nun, shadda on ya",
  "word_type": "proper_noun"
}}

Now diacritize this word and respond ONLY with JSON:
Input: {word}
Output:"""
```

**2. Response Parsing & Storage:**
```python
class LLMDiacritizerResponse:
    original: str
    diacritized: str
    confidence: float  # LLM's own confidence
    reasoning: str
    word_type: str

    # System metadata
    system_confidence: int  # 0 (unvalidated) or 1 (validated)
    source: str = "llm"
    date: str  # ISO 8601
    usage_count: int = 1
    tokens_used: dict  # {"input": N, "output": M, "total": N+M}
```

**3. No Validation Workflow (User Requirement #9):**
- LLM response automatically added to exception dictionary
- `system_confidence` set to 0 (unvalidated)
- `source` field: "llm"
- User can manually change confidence to 1 later if validated
- No approval step - output goes straight to production

**4. Token Usage Tracking (User Requirement #6):**
```python
# Track per-request
tokens_per_request = {
    "word": "الإسكندرية",
    "input_tokens": 250,
    "output_tokens": 50,
    "total_tokens": 300,
    "cost_estimate": 0.0003,  # USD
    "timestamp": "2025-01-16T10:30:00Z"
}

# Aggregate statistics (stored in config or separate file)
token_stats = {
    "total_requests": 145,
    "total_input_tokens": 36250,
    "total_output_tokens": 7250,
    "total_tokens": 43500,
    "estimated_total_cost": 0.0435,  # USD
    "last_reset": "2025-01-01T00:00:00Z"
}
```

**5. Cost Control - User Bears Cost (User Requirement #6):**
- No daily/monthly limits enforced by system
- User opts in via config and is responsible for costs
- Token usage stats shown in CSV export (see Deliverable 3)
- Warning if costs seem high (e.g., >$10/day)

#### File 4: `app.py` - Add LLM review UI (Optional)
**Purpose:** Web interface for reviewing LLM diacritizations

**Features:**
- View pending diacritizations
- Side-by-side comparison (undiacritized vs LLM diacritized)
- Approve/Reject buttons
- Bulk approval for high-confidence entries

### Configuration

#### File: `config/diacritization_config.yaml` (NEW)
```yaml
diacritization:
  # Tier 1: Exception Dictionary
  exception_dictionary:
    enabled: true
    file: data/dictionaries/diacritization_exceptions.json
    auto_load: true

  # Tier 2: Mishkal
  mishkal:
    enabled: true
    # No additional config needed

  # Tier 3: LLM Fallback
  llm_fallback:
    enabled: false  # Opt-in, starts disabled
    provider: "anthropic"  # or "openai"
    model: "claude-3-haiku-20240307"  # Cheapest option
    api_key_env: "ANTHROPIC_API_KEY"

    # Cost controls
    daily_quota: 1000  # Max words per day
    rate_limit: 10     # Max requests per minute

    # Validation
    require_human_review: true
    auto_approve_confidence: 0.95  # Future: confidence scoring

    # Learning
    save_to_exceptions: true  # Approved entries → exceptions.json

  # Tier 4: Character Fallback
  character_fallback:
    enabled: true  # Always on (safety net)
```

### Implementation Phases

#### Phase 0: Testing (FIRST - Must Do Before Any Implementation)
**Run**: `test_diacritization_comparison.py` on actual CSV data
**Output**: Decision on which architecture to implement
**Time**: ~30 minutes
**Deliverable**: Test results showing which fallback sequence works best

#### Phase 1: Documentation
- Write `docs/SYLLABLES_AND_DIACRITIZATION.md`
- Comprehensive examples explaining C/V patterns
- Visual diagrams showing syllable structure
- Link from CLARIFICATIONS.md

#### Phase 2: Implement Best Fallback Sequence (Based on Testing)
**Option A**: Mishkal → CAMeL (if CAMeL catches Mishkal failures)
**Option B**: CAMeL → Mishkal (if Mishkal catches CAMeL failures)
**Option C**: Single tool only (if one dominates or they're redundant)
- Integrate into `src/main.py`
- Update configuration
- No breaking changes

#### Phase 3: LLM Integration (Optional - Only if Still High Failure Rate)
- Implement LLMDiacritizer class
- Add configuration system
- User opts in, bears costs
- Token tracking
- Keep as opt-in feature (disabled by default)

#### Phase 4: Exception Dictionary (Future - Only if Using LLM)
- Create dictionary to cache LLM results
- Reduces repeated API calls
- Lowers costs over time
- LOW PRIORITY - only implement if costs become issue

### Modified Files

#### Core Implementation:
1. **NEW:** `docs/SYLLABLES_AND_DIACRITIZATION.md` - Main documentation
2. **NEW:** `data/dictionaries/diacritization_exceptions.json` - Exception dictionary
3. **NEW:** `src/core/diacritization_fallback.py` - Orchestrator
4. **NEW:** `config/diacritization_config.yaml` - Configuration
5. **MODIFIED:** `src/main.py` (lines 359-406) - Integrate fallback tiers
6. **OPTIONAL NEW:** `src/core/llm_diacritizer.py` - LLM integration
7. **OPTIONAL MODIFIED:** `app.py` - Add review UI route

#### Testing:
8. **NEW:** `tests/unit/test_diacritization_fallback.py`
9. **MODIFIED:** `tests/integration/test_diacritization.py` - Test all tiers

### Success Metrics

**Phase 1 (Documentation):**
- ✅ Complete, comprehensive, with examples
- ✅ Answers user's "how C/V varies" question
- ✅ Explains dependency chain clearly

**Phase 2 (Exception Dictionary):**
- ✅ Reduces "diac" failures by 10-20% for common words
- ✅ Zero cost, instant lookups
- ✅ Easy to maintain and expand

**Phase 3 (LLM - Optional):**
- ✅ Catches 50%+ of remaining Mishkal failures
- ✅ Builds local knowledge over time (self-improving)
- ✅ Costs <$10/month with proper quotas
- ✅ User validates before committing to dictionary

### Cost Analysis

**Current State:** $0/month
- Mishkal: Free, open-source
- Character fallback: Free (local masterTTS.json)

**With Exception Dictionary:** $0/month
- One-time effort: 2-4 hours to seed dictionary
- Ongoing: Add 5-10 entries/month as you discover failures

**With LLM (Optional):** $5-15/month
- Claude Haiku: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
- Estimate: 1000 words/month × 20 tokens/word × $0.0003 = $6/month
- With caching and batching: <$10/month realistically
- **ROI:** Each approved diacritization goes into free local dictionary
- After 6 months: 6000+ entries in dictionary, LLM usage drops naturally

### Long-Term Vision Alignment

**Now (MVP):**
- Focus: IPA accuracy (masterTTS.json is source of truth) ✅
- Diacritization: Good enough with Mishkal + exceptions ✅
- Costs: Minimal (<$10/month even with LLM) ✅

**Post-MVP (Prosody & Expressiveness):**
- Use LLM for: Pauses, emotions, personalities, audiobook narration
- Diacritization foundation: Solid and cost-effective
- LLM budget: Allocated to high-value prosody features, not basic diacritization

**This plan keeps pronunciation solid and cheap NOW, so LLM budget can go to expressiveness LATER.**

---

## Questions for User Before Implementation

1. **Seed dictionary**: Should I create an initial list of 20-50 Egyptian proper nouns/place names, or would you prefer to provide a specific list?

2. **LLM timeline**: Implement LLM fallback in Phase 3 (optional) or defer until post-MVP? (Recommendation: Start with Phases 1-2 only)

3. **Documentation location**: Create `docs/SYLLABLES_AND_DIACRITIZATION.md` or prefer different location/name?

4. **Validation UI**: Build web UI for reviewing LLM diacritizations, or use command-line review instead?
