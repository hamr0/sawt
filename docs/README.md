# Documentation

Arabic Audiobook Production — documentation hub.

## Quick Links

| What | Where |
|------|-------|
| Execution plan (source of truth) | [PLAN.md](02-features/azure-audiobooks/PLAN.md) |
| Repo structure & data flow | [REPO_STRUCTURE.md](02-features/azure-audiobooks/REPO_STRUCTURE.md) |
| Product requirements | [PRD](01-product/prd.md) |
| Development workflow | [Dev Workflow](04-process/dev-workflow.md) |
| Definition of done | [DoD](04-process/definition-of-done.md) |

---

## Structure

```
docs/
├── 00-context/                        # WHY and WHAT EXISTS
│   ├── vision.md                      #   Product purpose & boundaries
│   ├── assumptions.md                 #   Constraints, risks, unknowns
│   └── system-state.md               #   What's currently built
│
├── 01-product/                        # WHAT it must do
│   └── prd.md                         #   Product requirements
│
├── 02-features/                       # HOW features are designed
│   └── azure-audiobooks/
│       ├── PLAN.md                    #   Execution plan (source of truth)
│       ├── REPO_STRUCTURE.md          #   Directory layout & data flow
│       └── reference/                 #   Prototype history & research
│           ├── README.md              #     Azure testing framework overview
│           ├── README_MULTIVOICE.md   #     Multi-voice system docs
│           ├── AZURE_INTEGRATION_STATUS.md
│           ├── prototypes/            #     7 iterations of dialogue detection
│           └── results/               #     Evaluation templates
│
├── 03-logs/                           # MEMORY (what changed)
│   ├── implementation-log.md          #   What was built, when
│   ├── decisions-log.md               #   Architecture decisions + rationale
│   ├── bug-log.md                     #   Bugs found and fixed
│   ├── validation-log.md             #   CSV review results per POC
│   └── insights.md                    #   Learnings from development
│
└── 04-process/                        # HOW to work
    ├── dev-workflow.md                #   POC cycle, commands, conventions
    └── definition-of-done.md          #   Completion criteria per POC
```

---

## 00-context/ — Project Context

| Document | Description |
|----------|-------------|
| [vision.md](00-context/vision.md) | What we're building and why |
| [assumptions.md](00-context/assumptions.md) | Constraints, risks, known unknowns |
| [system-state.md](00-context/system-state.md) | Current architecture, POC progress, dependencies |

## 01-product/ — Requirements

| Document | Description |
|----------|-------------|
| [prd.md](01-product/prd.md) | Product requirements for audiobook production |

## 02-features/ — Azure Audiobooks

| Document | Description |
|----------|-------------|
| [PLAN.md](02-features/azure-audiobooks/PLAN.md) | Execution plan — POCs, design principles, success criteria |
| [REPO_STRUCTURE.md](02-features/azure-audiobooks/REPO_STRUCTURE.md) | Directory layout, data flow between POCs |
| [reference/](02-features/azure-audiobooks/reference/) | Prototype history (7 iterations), Azure integration status, research findings |

## 03-logs/ — Project Memory

| Document | Description |
|----------|-------------|
| [POC1_RESULTS.md](03-logs/POC1_RESULTS.md) | POC-1 results: book ingestion (PRODUCTION READY) |
| [POC2_RESULTS.md](03-logs/POC2_RESULTS.md) | POC-2 results: chapter splitting (PRODUCTION READY) |
| [POC3_RESULTS.md](03-logs/POC3_RESULTS.md) | POC-3 results: dialogue detection (PRODUCTION READY) |
| [implementation-log.md](03-logs/implementation-log.md) | What was built, when |
| [decisions-log.md](03-logs/decisions-log.md) | Architecture decisions with rationale |
| [bug-log.md](03-logs/bug-log.md) | Bugs, root causes, fixes |
| [validation-log.md](03-logs/validation-log.md) | CSV review results per POC |
| [insights.md](03-logs/insights.md) | Learnings from prototypes and development |

## 04-process/ — Workflow

| Document | Description |
|----------|-------------|
| [dev-workflow.md](04-process/dev-workflow.md) | POC development cycle, commands, review gates |
| [definition-of-done.md](04-process/definition-of-done.md) | Completion criteria per POC |

---

## Archive

Old documentation (IPA pipeline, Polly, Flask demo) is preserved in [`archive/docs/`](../archive/docs/). The IPA phonological pipeline produced accurate linguistic processing but unusable audio output — the audiobook pipeline takes a fundamentally different approach.
