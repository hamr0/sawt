# ArabicTTS Knowledge Base

Table of contents for comprehensive project documentation. For daily essentials, see CLAUDE.md.

---

## 00-context/ - Project Context (WHY)

| Document | Summary |
|----------|---------|
| vision.md | Market research, competitive analysis, IPA-first strategy, target users |
| assumptions.md | Constraints, risks, unknowns, key phonology assumptions |
| system-state.md | HLA/HLD, processing pipeline, component interactions, data flows |
| tech-stack.md | Tech decisions: Python, mishkal, eSpeak, Polly, Flask |

---

## 01-product/ - Product Requirements (WHAT)

| Document | Summary |
|----------|---------|
| prd.md | Problem, solution, requirements, success metrics, milestones |

---

## 02-features/ - Feature Documentation (HOW)

### Amazon Polly Integration -> docs/02-features/polly/
Neural TTS for production audiobooks. POC complete, testing long-form.

| Document | Purpose |
|----------|---------|
| QUICKSTART_GUIDE.md | 5-minute Polly setup |
| AWS_SETUP_GUIDE.md | AWS credentials and IAM |
| POLLY_USAGE_GUIDE.md | Production usage patterns |
| TTS_TECHNOLOGY_RESEARCH_2024.md | 60+ source TTS SOTA research |
| POLLY_INTEGRATION_ANALYSIS.md | Technical compatibility |
| COLLABORATIVE_DECISION_POLLY.md | Strategic decision rationale |
| POLLY_IMPLEMENTATION_PLAN.md | Implementation roadmap |

### Other Features

| Document | Summary |
|----------|---------|
| demo/DEMO_PAGE_GUIDE.md | Web demo for testing TTS interactively |
| csv-stats/README.md | Export phonetic analysis as CSV |
| migration/README.md | API version migration guide |

---

## 03-logs/ - Project Memory (WHAT CHANGED)

| Document | Summary |
|----------|---------|
| implementation-log.md | Milestones, features, version history |
| decisions-log.md | Architectural decisions with rationale |
| bug-log.md | Bugs, root causes, fixes |
| validation-log.md | Test results, accuracy metrics over time |
| insights.md | Learnings on Arabic phonology and TTS patterns |

---

## 04-process/ - Development Process (HOW TO WORK)

| Document | Summary |
|----------|---------|
| setup/QUICK_START.md | 3-minute environment setup |
| setup/LOCALHOST_SETUP_GUIDE.md | Detailed setup guide |
| testing.md | 329 tests: smoke, unit, integration. CI/CD |
| dev-workflow.md | Git workflow, pre-commit, code style, TDD |
| definition-of-done.md | Completion criteria for features/fixes |
| llm-prompts.md | AI assistant prompts for this codebase |

---

## archive/ - Historical Documents

MVP Phase 1 reports, old architecture, previous README versions -> docs/archive/
