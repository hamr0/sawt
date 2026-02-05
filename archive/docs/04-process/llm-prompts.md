# LLM Prompts & Context

Useful prompts for AI-assisted development on this project.

---

## Context Files

### CLAUDE.md (Auto-loaded)
- Location: `/CLAUDE.md` (project root)
- Purpose: Lightweight context for Claude Code sessions
- Size: ~400 lines
- Contents: Status, architecture, commands, critical notes

### KNOWLEDGE_BASE.md (On-demand)
- Location: `/KNOWLEDGE_BASE.md` (project root)
- Purpose: Comprehensive reference
- Size: ~1,500 lines
- Contents: Full project details, API reference, troubleshooting

---

## Common Prompts

### Understanding the Codebase

```
Read CLAUDE.md and explain the processing pipeline for Arabic text.
```

```
What are the 4 phonological processors and why does their order matter?
```

### Adding Features

```
I want to add [feature]. What files would need to change and what tests should I write?
```

```
How do I add a new entry to masterTTS.json for dialect [X]?
```

### Debugging

```
This test is failing: [test name]. Help me understand why and fix it.
```

```
The IPA output for "[Arabic text]" seems wrong. Can you trace through the pipeline?
```

### Testing

```
Write tests for [component/feature] following the patterns in tests/unit/.
```

```
Run the test suite and summarize any failures.
```

### Documentation

```
Update the docs to reflect [change]. Which files need updating?
```

```
Add a new entry to the decisions log for [decision].
```

---

## Project-Specific Context

### Key Facts to Include

When starting a new session, these facts help orient the AI:

1. **Architecture:** IPA-first approach - we own linguistics, voice is commodity
2. **Processor Order:** Gemination → Sun Letters → Allophones → Emphatic Spread
3. **Dictionary Timing:** masterTTS.json lookup happens AFTER processing
4. **Test Count:** 329 tests must all pass
5. **Primary Dialect:** MSA and Egyptian Arabic
6. **Voice Engines:** eSpeak (dev), Polly (prod)

### Common Mistakes to Avoid

```
Don't:
- Skip phonological processing
- Change processor order
- Commit without running tests
- Use Polly neural engine for Zeina
- Modify masterTTS.json structure
```

---

## Prompt Templates

### Feature Request

```
Project: Arabic TTS (see CLAUDE.md for context)

I want to implement: [description]

Requirements:
- [requirement 1]
- [requirement 2]

Questions:
1. What files need to change?
2. What tests should I add?
3. Are there any architectural considerations?
```

### Bug Report

```
Project: Arabic TTS

Bug: [description]

Steps to reproduce:
1. [step]
2. [step]

Expected: [expected behavior]
Actual: [actual behavior]

Relevant files: [files]
```

### Code Review

```
Please review this change for:
- Correctness (does it work?)
- Tests (adequate coverage?)
- Style (follows codebase patterns?)
- Performance (any concerns?)
- Security (any vulnerabilities?)
```

---

## Session Starters

### Quick Start
```
I'm working on Arabic TTS. Read CLAUDE.md for context. I need to [task].
```

### Deep Dive
```
I'm working on Arabic TTS. Read CLAUDE.md and KNOWLEDGE_BASE.md for full context. I need to understand [topic] in detail.
```

### Debugging Session
```
I'm debugging an issue in Arabic TTS. The problem is [description]. Help me trace through the code to find the root cause.
```
