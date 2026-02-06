# Friction Analysis - Detailed Report

**Generated:** 2026-02-05 09:08 UTC

**Sessions Analyzed:** 404
**Interactive Sessions:** 98 (multi-turn conversations)
**BAD Sessions:** 47 (48% of interactive)

## Glossary

**Interactive Session:** A conversation with >1 turn (multi-turn dialogue). Single-turn sessions are filtered from BAD rate calculation.

**BAD Session:** User gave up via `/stash`, `/exit`, or silent abandonment (high friction with no resolution).

**Friction:** Cumulative weight of negative signals. Higher friction = more user frustration.

**Peak Friction:** Maximum friction reached during a session.

---

## Executive Summary

🟡 **WARNING**: 48% of interactive sessions end in failure. Average session: 4.3 turns, 7.2 friction, 40 min.

**Top Issues:**
- **exit_error** (280 occurrences, 280 total friction)
- **compaction** (220 occurrences, 110 total friction)
- **repeated_question** (183 occurrences, 183 total friction)

---

## Friction Weight System

Each signal has a weight representing its severity. Friction accumulates as signals occur.

| Weight | Severity | Meaning |
|--------|----------|----------|
| +10 | CRITICAL | User gave up (intervention, abandonment) |
| +8 | SEVERE | LLM false claims or no progress (false_success, no_resolution) |
| +7 | HIGH | User frustration (interrupt_cascade) |
| +6 | MEDIUM | Stuck patterns (tool_loop, rapid_exit) |
| +4-5 | LOW-MEDIUM | User signals (request_interrupted, user_curse) |
| +1 | MINOR | Technical issues (exit_error, repeated_question) |
| +0.5 | NOISE | Context signals (compaction, long_silence, user_negation) |

---

## Signal Breakdown

| Signal | Count | Weight | Total Friction | What It Means |
|--------|-------|--------|----------------|---------------|
| exit_error | 280 | +1.0 | 280.0 | Command failed (exit code != 0) |
| compaction | 220 | +0.5 | 110.0 | Context overflow, conversation summarized |
| repeated_question | 183 | +1.0 | 183.0 | User asked same question twice |
| long_silence | 129 | +0.5 | 64.5 | User paused >10 min |
| request_interrupted | 129 | +2.5 | 322.5 | User hit Ctrl+C or ESC |
| user_negation | 120 | +0.5 | 60.0 | "no", "didn't work", "still broken" |
| false_success | 81 | +8.0 | 648.0 | LLM claimed success after error |
| sibling_tool_error | 48 | +0.5 | 24.0 | Parallel tools canceled (SDK cascade) |
| user_intervention | 44 | +10.0 | 440.0 | User gave up (/stash, /exit) |
| session_abandoned | 26 | +10.0 | 260.0 | High friction, no resolution |
| no_resolution | 23 | +8.0 | 184.0 | Errors without subsequent success |
| interrupt_cascade | 22 | +5.0 | 110.0 | 2+ interrupts within 60s |
| tool_loop | 20 | +6.0 | 120.0 | Same tool called 3+ times |
| user_curse | 16 | +5.0 | 80.0 | User frustration (profanity) |
| exit_success | 7 | +0.0 | 0.0 | Command succeeded (exit code 0) |
| rapid_exit | 7 | +6.0 | 42.0 | <3 turns, ends with error/interrupt |

## Pattern Analysis

### Common Failure Patterns

**False Success Loop** (81 occurrences): LLM claims task is complete after command fails. This indicates the LLM is not checking exit codes properly.

**High Error Rate** (280 errors): Many commands are failing. This suggests either environment issues or LLM choosing wrong approaches.

**User Interruptions** (129 interrupts): Users frequently canceling operations. Commands may be too slow, stuck, or heading in wrong direction.

**Abandonment Rate** (45%): 44/98 interactive sessions ended with user giving up. This is CRITICAL - users are frequently giving up.

### Friction Level Breakdown

**Low Friction (0-15):** 176 sessions - Normal operation, minor errors quickly resolved

**Medium Friction (15-50):** 28 sessions - Some struggles, multiple retries, but eventually successful

**High Friction (50+):** 22 sessions - Severe issues, user frustration, likely gave up

---

## Top Friction Sessions

| Project | Session | Quality | Peak | Turns | Duration | Top Signals |
|---------|---------|---------|------|-------|----------|-------------|
| aurora | 0203-1630-11eb903a | BAD | 225.0 | 127 | 16h20m | long_silence:6, repeated_question:33, curse:2 |
| aurora | 0203-1227-f073391c | BAD | 196.0 | 78 | 2h48m | long_silence:2, repeated_question:20, intervention:3 |
| aurora | 0129-1503-a3ab0e5e | BAD | 101.0 | 35 | 2h19m | long_silence:4, repeated_question:8, request_interrupted:6 |
| aurora | 0131-1635-49450a25 | BAD | 100.0 | 28 | 1h46m | compaction:2, sibling_tool_error:2, long_silence:1 |
| hamr | 0128-0905-81f57109 | BAD | 96.5 | 79 | 25h58m | long_silence:8, repeated_question:26, negation:12 |
| aurora | 0204-0932-6d389195 | FRICTION | 94.0 | 36 | 3h13m | long_silence:4, repeated_question:4, negation:2 |
| aurora | 0202-1014-7504bc46 | BAD | 92.5 | 17 | 1h58m | long_silence:3, repeated_question:1, request_interrupted:7 |
| aurora | 0131-2012-83a1d5f9 | BAD | 84.0 | 26 | 1h42m | long_silence:1, repeated_question:1, intervention:3 |
| aurora | 0131-1308-2b80385d | BAD | 82.5 | 24 | 3h26m | long_silence:2, intervention:4, negation:4 |
| aurora | 0131-1824-c1027030 | BAD | 82.0 | 16 | 1h47m | long_silence:2, request_interrupted:7, intervention:3 |
| aurora | 0204-1201-111c19f8 | BAD | 78.5 | 26 | 1h26m | long_silence:1, request_interrupted:6, curse:3 |
| hamr | 0127-1941-0289c457 | BAD | 77.5 | 67 | 2h56m | long_silence:3, repeated_question:12, negation:5 |
| aurora | 0202-1107-f0fd485a | BAD | 73.5 | 55 | 9h14m | long_silence:6, repeated_question:7, negation:1 |
| aurora | 0204-1328-9b73a0a3 | BAD | 72.5 | 23 | 2h11m | long_silence:6, intervention:1, negation:3 |
| aurora | 0202-2147-1f196e6f | BAD | 68.0 | 62 | 7h50m | long_silence:3, repeated_question:10, request_interrupted:2 |
| aurora | 0131-0942-a44d15d6 | BAD | 65.0 | 10 | 1h49m | long_silence:2, request_interrupted:2, compaction:1 |
| ArabicTTS | 0205-0755-ea761de4 | BAD | 60.0 | 12 | 52m | long_silence:2, intervention:4, request_interrupted:1 |
| aurora | 0131-1146-b25b4ac8 | BAD | 59.5 | 7 | 5h15m | long_silence:2, request_interrupted:2, negation:2 |
| aurora | 0202-0956-930d3fc1 | BAD | 59.0 | 5 | 13m | compaction:1, sibling_tool_error:2, request_interrupted:7 |
| aurora | 0129-1723-81c00300 | BAD | 55.0 | 19 | 1h55m | long_silence:1, repeated_question:3, negation:3 |

## Session Quality Breakdown

| Quality | Count | Description |
|---------|-------|-------------|
| BAD | 47 | user gave up (/stash) |
| FRICTION | 5 | curse or false_success |
| ROUGH | 1 | high friction but completed |
| OK | 46 | no significant friction |
| ONE-SHOT | 305 | single turn (filtered) |

## Per-Project Statistics

| Project | Interactive | BAD | BAD % | Avg Friction | Avg Turns | Avg Duration |
|---------|-------------|-----|-------|--------------|-----------|-------------|
|  | 0 | 0 | - | 0.0 | 1.0 | - |
| ArabicTTS | 6 | 3 | 50% | 16.2 | 7.3 | 1h58m |
| agentic-toolkit | 1 | 0 | 0% | 0.0 | 1.0 | - |
| aurora | 81 | 42 | 52% | 9.4 | 5.0 | 47m |
| coding-assistant | 1 | 0 | 0% | 7.3 | 9.0 | 33m |
| gitdone | 2 | 0 | 0% | 2.0 | 7.0 | 1h44m |
| hamr | 5 | 2 | 40% | 8.3 | 7.4 | 1h25m |
| liteagents | 1 | 0 | 0% | 0.0 | 4.0 | 3m |
| mcp-gov | 1 | 0 | 0% | 0.5 | 2.0 | 57m |

## Recommendations

1. **High Priority:** Add CLAUDE.md rule to verify exit codes before claiming success

2. **High Priority:** Commands timing out or stuck - review for heavy operations that need optimization

3. **Medium Priority:** Add CLAUDE.md rule to detect and break out of tool loops

4. **Critical:** >40% abandonment rate - major UX issues, review antigens for patterns

5. **Medium Priority:** Many repeated questions - LLM not understanding user intent or context issues

---

## Daily Trend (Last 14 Days)

| Date | Interactive | BAD | Rate | Trend |
|------|-------------|-----|------|-------|
| 2026-01-27 | 3 | 1 | 33% | ███░░░░░░░ |
| 2026-01-28 | 2 | 1 | 50% | █████░░░░░ |
| 2026-01-29 | 10 | 5 | 50% | █████░░░░░ |
| 2026-01-30 | 4 | 2 | 50% | █████░░░░░ |
| 2026-01-31 | 14 | 8 | 57% | █████░░░░░ |
| 2026-02-01 | 2 | 1 | 50% | █████░░░░░ |
| 2026-02-02 | 15 | 10 | 67% | ██████░░░░ |
| 2026-02-03 | 29 | 12 | 41% | ████░░░░░░ |
| 2026-02-04 | 15 | 5 | 33% | ███░░░░░░░ |
| 2026-02-05 | 4 | 2 | 50% | █████░░░░░ |

