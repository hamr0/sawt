# Arabic TTS Documentation

**Version:** 2.0 (Reorganized)
**Last Updated:** February 2026

Welcome to the Arabic TTS documentation. This hub provides navigation to all project documentation, organized into 5 tiers for easy discovery.

---

## Quick Links

| Need | Go To |
|------|-------|
| Get started fast | [Quick Start](04-process/setup/QUICK_START.md) |
| Understand the architecture | [System State](00-context/system-state.md) |
| See product requirements | [PRD](01-product/prd.md) |
| Set up Polly | [Polly Quickstart](02-features/polly/QUICKSTART_GUIDE.md) |
| Run tests | [Testing Guide](04-process/testing.md) |

---

## Documentation Structure

```
docs/
├── 00-context/      # WHY - Vision, assumptions, current state
├── 01-product/      # WHAT - Product requirements
├── 02-features/     # HOW - Feature documentation
├── 03-logs/         # MEMORY - History and decisions
├── 04-process/      # WORKFLOW - How to work
└── archive/         # Old docs (preserved)
```

---

## 00-context/ - Project Context

*Understanding WHY the project exists and WHAT currently exists.*

| Document | Description |
|----------|-------------|
| [vision.md](00-context/vision.md) | Business analysis, market research, strategic goals |
| [assumptions.md](00-context/assumptions.md) | Constraints, risks, unknowns |
| [system-state.md](00-context/system-state.md) | Current architecture, components, data flows |
| [tech-stack.md](00-context/tech-stack.md) | Technology decisions and rationale |

---

## 01-product/ - Product Requirements

*WHAT the product must do.*

| Document | Description |
|----------|-------------|
| [prd.md](01-product/prd.md) | Product requirements, success metrics, milestones |

---

## 02-features/ - Feature Documentation

*HOW features are designed and built.*

### Amazon Polly Integration
| Document | Description |
|----------|-------------|
| [README.md](02-features/polly/README.md) | Polly integration overview |
| [QUICKSTART_GUIDE.md](02-features/polly/QUICKSTART_GUIDE.md) | Get started in 5 minutes |
| [AWS_SETUP_GUIDE.md](02-features/polly/AWS_SETUP_GUIDE.md) | AWS credentials setup |
| [POLLY_USAGE_GUIDE.md](02-features/polly/POLLY_USAGE_GUIDE.md) | Usage reference |
| [TTS_TECHNOLOGY_RESEARCH_2024.md](02-features/polly/TTS_TECHNOLOGY_RESEARCH_2024.md) | Research (60+ sources) |
| [POLLY_INTEGRATION_ANALYSIS.md](02-features/polly/POLLY_INTEGRATION_ANALYSIS.md) | Technical compatibility |
| [COLLABORATIVE_DECISION_POLLY.md](02-features/polly/COLLABORATIVE_DECISION_POLLY.md) | Strategic decision |
| [POLLY_IMPLEMENTATION_PLAN.md](02-features/polly/POLLY_IMPLEMENTATION_PLAN.md) | Implementation roadmap |

### Other Features
| Document | Description |
|----------|-------------|
| [Demo Page Guide](02-features/demo/DEMO_PAGE_GUIDE.md) | Interactive demo documentation |
| [CSV Stats](02-features/csv-stats/README.md) | CSV export statistics feature |
| [Migration Guide](02-features/migration/README.md) | API migration guide |

---

## 03-logs/ - Project Memory

*WHAT changed over time.*

| Document | Description |
|----------|-------------|
| [implementation-log.md](03-logs/implementation-log.md) | Implementation milestones |
| [decisions-log.md](03-logs/decisions-log.md) | Architectural decisions with rationale |
| [bug-log.md](03-logs/bug-log.md) | Bugs, root causes, and fixes |
| [validation-log.md](03-logs/validation-log.md) | Test results and quality metrics |
| [insights.md](03-logs/insights.md) | Learnings and patterns |

---

## 04-process/ - Development Process

*HOW to work with this system.*

### Setup
| Document | Description |
|----------|-------------|
| [README.md](04-process/setup/README.md) | Setup overview |
| [QUICK_START.md](04-process/setup/QUICK_START.md) | 3-minute setup |
| [LOCALHOST_SETUP_GUIDE.md](04-process/setup/LOCALHOST_SETUP_GUIDE.md) | Detailed setup |

### Development
| Document | Description |
|----------|-------------|
| [testing.md](04-process/testing.md) | Testing guide (329 tests) |
| [dev-workflow.md](04-process/dev-workflow.md) | Pre-commit hooks, workflow |
| [definition-of-done.md](04-process/definition-of-done.md) | Completion criteria |
| [llm-prompts.md](04-process/llm-prompts.md) | AI assistant prompts |

### Templates
| Document | Description |
|----------|-------------|
| [WEEKLY_REPORT_TEMPLATE.md](04-process/templates/WEEKLY_REPORT_TEMPLATE.md) | Progress report template |

---

## archive/ - Historical Documents

*Old or superseded documents preserved for reference.*

| Document | Original Purpose |
|----------|------------------|
| ARCHITECTURE_OLD.md | Previous architecture version |
| TECH_STACK_OLD.md | Previous tech stack version |
| INDEX.md | Previous documentation index |
| DOCUMENTATION_SUMMARY.md | Previous docs summary |
| DEMO_PRESENTATION.md | MVP demo presentation |
| DEMO_SUMMARY.md | MVP demo summary |
| TEST_DOCUMENTATION.md | Previous testing docs |
| MVP_PHASE1_COMPLETE.md | Phase 1 completion report |
| MVP_VALIDATION_RESULTS.md | Phase 1 validation results |
| PROJECT_DOCUMENTATION.md | Previous project docs |
| README_OLD.md | Previous README |
| POC_RESULTS_TEMPLATE.md | Polly POC template |

---

## Related Files (Project Root)

| File | Purpose |
|------|---------|
| [CLAUDE.md](../CLAUDE.md) | Auto-loaded context for Claude Code |
| [KNOWLEDGE_BASE.md](../KNOWLEDGE_BASE.md) | Comprehensive reference |
| [README.md](../README.md) | Project overview |

---

## Navigation Tips

1. **New to the project?** Start with [Quick Start](04-process/setup/QUICK_START.md)
2. **Understanding architecture?** Read [System State](00-context/system-state.md)
3. **Adding a feature?** Check [PRD](01-product/prd.md) and relevant feature docs
4. **Making a decision?** Log it in [decisions-log.md](03-logs/decisions-log.md)
5. **Using AI assistant?** See [llm-prompts.md](04-process/llm-prompts.md)
