# Task List: Amazon Polly TTS Integration POC

**Source PRD:** `0001-prd-polly-integration.md`  
**Status:** Phase 2 - Detailed Sub-Tasks Generated  
**Target Timeline:** 1 week (5 working days)  
**Target Code Changes:** ≤50 lines (≤100 lines maximum)

---

## Relevant Files

### Files to Create
- `.env.example` - AWS credential template (CREATED)
- `docs/polly/AWS_SETUP_GUIDE.md` - Step-by-step AWS configuration instructions (CREATED)
- `src/integrations/polly.py` - PollyTTS wrapper class following espeak.py pattern (CREATED - 123 lines)
- `tests/unit/test_polly.py` - Unit tests for PollyTTS class (CREATED - 329 lines)
- `demo_output/polly_test/README.md` - Explanation of output files and evaluation criteria (CREATED)
- `demo_output/polly_test/.gitkeep` - Output directory for test audio files (CREATED)
- `docs/polly/POLLY_USAGE_GUIDE.md` - Usage examples and API reference

### Files to Modify
- `requirements.txt` - Add boto3>=1.28.0 dependency
- `scripts/test_polly_integration.py` - Refactor to use new PollyTTS class from src/integrations/polly.py
- `docs/polly/POLLY_IMPLEMENTATION_PLAN.md` - Update with POC results (post-execution)

### Files to Reference (No Changes)
- `src/main.py` - ArabicTTS class with process_text() method (lines 1-343)
- `src/integrations/espeak.py` - Pattern reference for integration class structure (lines 1-359)
- `data/dictionaries/masterTTS.json` - Phonetic mappings (no modifications needed)

---

## Implementation Notes

### Testing Framework
- **Pytest** is used for all tests (see `pytest.ini` if exists)
- Unit tests go in `tests/unit/`
- Integration tests go in `tests/integration/`
- Smoke tests go in `tests/smoke/`
- Run tests: `pytest tests/unit/test_polly.py -v`
- Run all tests: `pytest tests/ -v --cov=src`

### Architectural Patterns
- **Integration class pattern** (from `espeak.py`):
  - Class initializer checks dependency availability
  - Graceful degradation if dependencies missing
  - Clear error messages guide user to setup steps
  - Methods return `(success: bool, message: str)` tuples
- **Keep it minimal**: Target ~50 lines for PollyTTS class (vs 359 for ESpeakTTS)
- **No pipeline modifications**: Use existing `ArabicTTS.process_text()` output as-is

### Potential Challenges
1. **AWS credentials not configured**: Handle with clear error message pointing to setup guide
2. **boto3 import fails**: Provide installation command in error message
3. **X-SAMPA compatibility**: Polly may interpret X-SAMPA differently than expected; fallback to plain text
4. **Network latency**: First API call may be slow; document expected ~1-2 second delay
5. **IAM permissions**: User needs `polly:SynthesizeSpeech` permission; document in setup guide

### Cost Monitoring
- Each test run: ~200-500 characters (negligible)
- Free tier: 5M characters/month for 12 months
- POC total usage: <1000 characters (well within free tier)
- No cost tracking needed for POC phase

---

## Tasks

- [x] 1.0 Setup AWS Dependencies and Configuration
  - [x] 1.1 Add `boto3>=1.28.0` to requirements.txt (append to existing dependencies)
  - [x] 1.2 Install boto3 in virtual environment: `source venv/bin/activate && pip install boto3`
  - [x] 1.3 Create `.env.example` file with AWS credential template (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
  - [x] 1.4 Document AWS credential configuration options in setup guide (environment variables vs ~/.aws/credentials)
  - [x] 1.5 Test boto3 import and AWS connection with simple script: `python -c "import boto3; print(boto3.__version__)"`

- [x] 2.0 Implement PollyTTS Wrapper Class
  - [x] 2.1 Create `src/integrations/polly.py` with PollyTTS class structure (follow espeak.py pattern but keep minimal)
  - [x] 2.2 Implement `__init__(self, region='us-east-1')` method with boto3 client initialization and graceful error handling for missing credentials/imports
  - [x] 2.3 Implement `xsampa_to_ssml(self, xsampa: str, text: str) -> str` method to convert X-SAMPA to Polly SSML format with phoneme tags
  - [x] 2.4 Implement `generate_audio(self, text: str, xsampa: str, output_path: str, voice_id='Zeina', engine='neural') -> Tuple[bool, str]` method with Polly API call
  - [x] 2.5 Add comprehensive error handling for: missing credentials, network failures, invalid X-SAMPA, API rate limits, insufficient permissions (FR-011)
  - [x] 2.6 Add docstrings to all methods with type hints, parameter descriptions, and return value documentation
  - [x] 2.7 Write unit tests in `tests/unit/test_polly.py`: test initialization, SSML conversion, error handling (mock boto3 calls)
  - [x] 2.8 Run unit tests and verify 100% pass rate: `pytest tests/unit/test_polly.py -v`

- [x] 3.0 Enhance POC Test Script (COMPLETED - Commit 43af1c3)
  - [x] 3.1 Refactor `scripts/test_polly_integration.py` to import and use PollyTTS class from `src.integrations.polly` (remove inline PollyIntegration class)
  - [x] 3.2 Define 5 test sentences in script covering: simple sentence, consonant clusters, tanween, long sentence (10-15 words), challenging phonemes (FR-013, Appendix A)
  - [x] 3.3 Implement comparison mode to generate both eSpeak and Polly audio for same input text (FR-015)
  - [x] 3.4 Update output file naming to: `test_polly_001_zeina_neural.mp3`, `test_polly_001_espeak.mp3` for clear identification (FR-014)
  - [x] 3.5 Create `demo_output/polly_test/` directory structure with README.md explaining output files
  - [x] 3.6 Add summary report generation: total tests, success/failure count, file sizes, estimated costs, next steps
  - [x] 3.7 Test the script end-to-end with mock AWS credentials (should fail gracefully) and document expected output

- [x] 4.0 Create Documentation (COMPLETED - Commit b602377)
  - [x] 4.1 Create `docs/polly/AWS_SETUP_GUIDE.md` with step-by-step instructions: AWS account creation, IAM user setup, access key generation, credential configuration (FR-020) - Already created in task 1.4
  - [x] 4.2 Add IAM policy requirements section to setup guide: minimal permissions needed (polly:SynthesizeSpeech, required for FR-002/003) - Already included in AWS_SETUP_GUIDE.md
  - [x] 4.3 Create `docs/polly/POLLY_USAGE_GUIDE.md` with usage examples: basic usage, voice options (Zeina/Hala), engine options (neural/standard), error handling (FR-022)
  - [x] 4.4 Add "Troubleshooting" section to usage guide: common errors (credentials, network, permissions) and solutions
  - [x] 4.5 Document test execution procedure in usage guide: how to run test script, interpret results, listen to audio (FR-021)
  - [x] 4.6 Add code examples to usage guide: Python snippets showing integration with existing ArabicTTS pipeline
  - [x] 4.7 Review all documentation for clarity, completeness, and alignment with PRD requirements

- [ ] 5.0 Execute POC Validation and Testing
  - [ ] 5.1 Run existing test suite to establish baseline: `pytest tests/ -v` (verify all 329 tests pass - SM-005)
  - [ ] 5.2 Configure AWS credentials following AWS_SETUP_GUIDE.md (use personal AWS account or create new free tier account)
  - [ ] 5.3 Execute test script: `python scripts/test_polly_integration.py` and verify 5 audio files generated successfully (SM-001)
  - [ ] 5.4 Manual listening evaluation: compare Polly vs eSpeak audio quality for all 5 test sentences, document subjective assessment (SM-006)
  - [ ] 5.5 Verify code changes are within target: `git diff --stat` should show ≤100 lines added (SM-002)
  - [ ] 5.6 Verify AWS costs: check AWS billing dashboard, confirm $0 usage within free tier (SM-004)
  - [ ] 5.7 Re-run existing test suite: `pytest tests/ -v` to confirm zero breaking changes, all 329 tests still pass (SM-005)
  - [ ] 5.8 Schedule native speaker validation session (optional for POC, required for production decision - OQ-003)
  - [ ] 5.9 Create POC results document in `docs/polly/POC_RESULTS.md`: findings, metrics achieved, audio quality assessment, cost analysis, recommendation (Go/No-Go/Iterate)
  - [ ] 5.10 Update `docs/polly/POLLY_IMPLEMENTATION_PLAN.md` with actual POC results and next steps based on decision criteria (Section 8.3)

---

## Success Criteria Checklist

Before marking POC complete, verify:

- [ ] boto3 dependency added and installed successfully
- [ ] PollyTTS class created in `src/integrations/polly.py` (~50 lines)
- [ ] Unit tests written and passing (100%)
- [ ] Test script refactored and functional
- [ ] 5 test audio files generated successfully
- [ ] AWS setup guide complete and tested
- [ ] Usage guide complete with examples
- [ ] All 329 existing tests still pass (zero breaking changes)
- [ ] Code changes ≤100 lines total
- [ ] AWS costs: $0 (within free tier)
- [ ] Subjective audio quality: Polly > eSpeak
- [ ] POC results documented with clear recommendation
- [ ] Native speaker validation scheduled (if proceeding to production)

---

## Estimated Time Breakdown

| Task | Estimated Time | Priority |
|------|---------------|----------|
| 1.0 Setup AWS Dependencies | 30 minutes | High |
| 2.0 Implement PollyTTS Class | 2-3 hours | High |
| 3.0 Enhance Test Script | 1-2 hours | High |
| 4.0 Create Documentation | 2-3 hours | Medium |
| 5.0 Execute POC Validation | 1-2 hours | High |
| **Total** | **7-11 hours** | **(~1.5 days)** |

**Timeline:** Complete within 2-3 working days, well within 1-week POC deadline (SM-001)

---

## Next Steps After Completion

1. Review POC results document with stakeholders
2. If successful (meets success metrics), proceed to Phase 2: expand testing to 25 sentences (Section 10)
3. If issues found, iterate on X-SAMPA mapping or test alternative approach (IPA instead of X-SAMPA)
4. If unsuccessful, evaluate alternatives: XTTS, commercial TTS, or continue with eSpeak (OQ-008)
