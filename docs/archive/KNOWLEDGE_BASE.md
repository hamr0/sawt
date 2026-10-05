# Knowledge Base

Topic index for Arabic Audiobook Production. Each entry summarizes what a doc covers and where to find details.

## Context

| Topic | Summary | Details |
|-------|---------|---------|
| Vision | Two-voice Arabic audiobooks from PDF/TXT via Azure Neural TTS. Text processing is the product. | docs/product/vision.md |
| Assumptions | Constraints, risks, known unknowns for the audiobook pipeline. | docs/product/assumptions.md |
| System state | Current architecture, POC progress (none started), active code paths, dependencies. | docs/archive/system-state.md |

## Product

| Topic | Summary | Details |
|-------|---------|---------|
| Requirements | POC-1 ingestion, POC-2 chapters, POC-3a two-voice, POC-3b multi-voice (stretch). CSV review at every stage. | docs/product/prd.md |

## Feature Design

| Topic | Summary | Details |
|-------|---------|---------|
| Execution plan | Source of truth. POC specs, success criteria, architecture decisions, risk register. | docs/02-features/azure-audiobooks/PLAN.md |
| Repo structure | Directory layout, data flow between POCs, migration from IPA archive, output conventions. | docs/02-features/azure-audiobooks/REPO_STRUCTURE.md |
| Prototype reference | 7 iterations of dialogue detection R&D. Production detector: 06_simplified_detector.py (63.5% attribution). | docs/02-features/azure-audiobooks/reference/ |

## Logs

| Topic | Summary | Details |
|-------|---------|---------|
| Implementation log | What was built and when. | docs/logs/03-logs/implementation-log.md |
| Decisions log | Architecture decisions with rationale. | docs/logs/03-logs/decisions-log.md |
| Bug log | Bugs found, root causes, fixes. | docs/logs/03-logs/bug-log.md |
| Validation log | CSV review results per POC. | docs/logs/03-logs/validation-log.md |
| Insights | Learnings from prototypes and development. | docs/logs/03-logs/insights.md |

## Process

| Topic | Summary | Details |
|-------|---------|---------|
| Dev workflow | POC development cycle: implement, test, run on real book, review CSV, fix, move on. | docs/wiki/dev-workflow.md |
| Definition of done | Completion criteria per POC. Human verification of output at every stage. | docs/wiki/definition-of-done.md |

## Archive

Old IPA pipeline code and documentation preserved in `archive/`. Zero code shared with audiobook pipeline. Reference only.
