# DESIGN_PLAN — Sawt Runner UI

## Summary
- **Scope**: PRD §5 modules 2 (UI shell) and 3 (artifacts tab). Module 1 (look) is done: owner picked **variant D**.
- **Target**: new package `src/audiobook/ui/`, served by stdlib `http.server`, 127.0.0.1 only, no new deps, no JS framework, no build step.
- **Winner D**: left job-card list, right pane with tabs `[1] Run  [2] History  [3] Artifacts`. New-run form lives in a panel opened from `[ + new job ]`; the overwrite warning is inline (banner in the panel), never a modal. Layout approved as-is; expect tweaks during build.
- **Key improvements over the CLI / earlier variants**: one screen for start, live log, history, outputs; compact monospace look (bareloop style); light + dark theme (toggle, default follows `prefers-color-scheme`); **left job list scrolls on its own** and so does the right log (page and right pane stay put); phone width collapses the list to a `<select>`; Arabic names render RTL-correct (`unicode-bidi: plaintext`).
- **Lab-only, not product**: the preview's demo strip, lab note, `fixtures.js`. Reference: `.../scratchpad/design-ref/preview/index.html` (copy CSS tokens + rules from it).

## Files to Change
- [ ] `src/audiobook/ui/__init__.py` — `from .core import *` (+ underscore helpers tests need), per repo convention
- [ ] `src/audiobook/ui/core.py` — handlers, `serve()`, background run worker, path-safety helpers
- [ ] `src/audiobook/ui/page.py` — `PAGE` string constant: inline HTML + CSS (tokens) + vanilla JS (single file; no static dir)
- [ ] `src/audiobook/ui/__main__.py` — `python -m src.audiobook.ui [--port 8765] [--no-open]`
- [ ] `tests/audiobook/ui/test_core.py` — mirrors package; handlers tested against a real server on port 0 with `SAWT_HOME` in tmp
- [ ] `tests/audiobook/ui/__init__.py` only if sibling test dirs have one
- [ ] `CLAUDE.md` / `docs/product/prd.md` — one-line status update after module 3 (additive only)
- Do NOT touch `runner/core.py` unless a gap below forces it (see Gaps). No cross-stage imports beyond `..runner`.

## Implementation Steps
**Module 2 — UI shell**
1. Server skeleton: `ThreadingHTTPServer` on 127.0.0.1, `GET /` returns `PAGE`; `serve(port)` + `__main__`. Reject non-local `Host` headers (DNS-rebinding guard); POSTs require JSON content type.
2. Read endpoints: `GET /api/jobs` (wraps `list_jobs()` plus `name`-keyed ordering newest first), `GET /api/jobs/<name>` (one job from `load_jobs()`).
3. Page shell: tokens, appbar (title + theme toggle), two-pane grid, independent scroll areas, tabs, empty/loading states.
4. Left pane: job cards, `[ + new job ]`, selection (`#job=<name>` in URL hash so reload keeps selection).
5. New-job panel + `POST /api/runs`; single in-process worker thread (one run at a time, queue for folders); worker passes an `emit` that appends to an in-memory buffer.
6. Run tab: poll `GET /api/jobs/<name>` every 1s while running (log lines come from `run["log"]`, which the runner saves after every step); steps rendered `✓ / ✗ / > / skipped`; Retry button -> `POST /api/jobs/<name>/retry`.
7. History tab: runs newest first, expandable to log; rename job (`POST /api/jobs/<name>/rename`).
8. Theme toggle + localStorage; restart test: stop server, start, history intact.

**Module 3 — Artifacts tab**
9. `GET /api/jobs/<name>/artifacts` — one entry per `STEP_DIRS` folder (exists?, file list, sizes).
10. `GET /files/<job>/<step>/<file>` — serve text/csv/ssml/json inside the job's `output` only (resolve + `is_relative_to`; also allow repo `output/`). No directory listing outside known step dirs.
11. `POST /api/jobs/<name>/open` `{step}` — `xdg-open` (Linux; `open` on darwin) on the step folder via `subprocess.run([...])`, no shell.
12. Artifacts tab UI: step entry, `[ open folder ]`, file links; missing/skipped steps dashed.
13. Proof per PRD: point at a book + a folder, watch 1-4 tick, open every step folder, restart server, find history.

**Gaps in runner to handle in UI layer (not by editing runner unless unavoidable)**: `run_book` blocks until done -> run it in the worker thread; `confirm` callback -> handler pre-checks overwrite (any `STEP_DIRS` folder exists in the job's output) and returns 409, client re-posts with `confirm:true` -> `assume_yes=True`; folder runs use `scan_path()` and report `skipped` list.

## Component API
Vanilla JS: one `state` object, `render*()` functions per component, event delegation on `#app`. Names below are state keys / function names.

| Component | Props / state | Events |
|---|---|---|
| **Job card** | `{name, status, date, runs, missing}`; `selected` | click -> `selectJob(name)`; `[rename]` (inline field, Enter save, Esc cancel) -> rename endpoint |
| **Job list** (left, `overflow-y:auto`) | `jobs[]`, `selected`, `loading`, `error`; <720px renders as `<select>` | select; `[ + new job ]` -> `openPanel()` |
| **New-job panel** | `path`, `name` (placeholder = file stem), `fiction` (default on), `ssml` (default off), `newJob` (shown only when path resolves to an existing job), `overwrite` banner, `busy`, `errors{}`, `skipped[]` | `[ start ]` -> POST `/api/runs`; `[ cancel ]` closes; Esc closes |
| **Run log** (right, `overflow-y:auto`, `role=log`) | `run` (steps, log, status, errors); autoscroll only if already at bottom | `[ retry ]` (failed), `[ rename ]`; gate line "ready for audio — paused before paid step"; no audio button in v1 |
| **History list** | `runs[]` newest first; `expanded` set | toggle run (button, `aria-expanded`) -> shows settings, steps, log, errors, note (imported runs) |
| **Artifacts list** | `artifacts[{step, dir, exists, files[]}]` | `[ open folder ]` -> POST open; file link -> `/files/...` (new tab); toast/msg line on failure |
| **Theme toggle** | `theme: auto|light|dark` | click cycles; sets `data-theme` on `<html>`; try/catch `localStorage['sawt-theme']` |

**HTTP endpoints -> runner**
| Endpoint | Runner call |
|---|---|
| `GET /api/jobs` | `list_jobs()` |
| `GET /api/jobs/<n>` | `load_jobs()` -> job (404 if none) |
| `POST /api/runs` `{path,name?,fiction,ssml,newJob,confirm}` | `scan_path()` then `run_book(book, name=, fiction=, ssml=, new_job=, assume_yes=confirm, emit=)` in worker. Returns `202 {queued:[names], skipped:[{file,reason}]}`; `409 {overwrite:true,message:OVERWRITE_WARNING}`; `409 {busy:true}` if a run is active; `400 {error}` on `RunnerError` |
| `POST /api/jobs/<n>/retry` | `retry_job(n, emit)` in worker |
| `POST /api/jobs/<n>/rename` `{name}` | `rename_job(old, new)` |
| `GET /api/status` | `{busy, current_job}` from worker (drives the "running" state) |
| `GET /api/jobs/<n>/artifacts` | derived from `STEP_DIRS` + job `output` |
| `POST /api/jobs/<n>/open` `{step}` | `xdg-open` on `output/<STEP_DIRS[step]>` |
| `GET /files/<n>/<step>/<file>` | path-checked file read |
| First start | if `jobs.json` absent, offer `[ import existing output/ ]` -> `import_existing()` (empty-state action) |

## Required UI States
- **Loading**: `loading...` line in list / tab; buttons keep size.
- **Empty**: no jobs -> dashed box "no jobs yet — [ + new job ] or [ import existing output/ ]"; no runs / no artifacts likewise.
- **Error**: banner (red) with message and `[ retry ]`/`[ dismiss ]`; server-unreachable banner while polling; unreadable `jobs.json` shows `RunnerError` text.
- **Disabled**: `[ start ]` disabled while path empty or a run is active (dashed, faint, `disabled` attr + reason text); `[ retry ]` only on failed latest run.
- **Validation**: inline, per field, `aria-describedby`: path not found, `.doc` rejected with reason, unsupported format, invalid/duplicate job name (server message verbatim). Folder skips listed after start.
- **Running**: card shows `[…]` cyan, steps tick live, current step `run`, Start disabled, `aria-busy` on log; polling stops when status leaves running.
- **Missing folder**: card status `missing` (amber); Run/Artifacts tab shows amber banner "output folder is gone"; open-folder and retry disabled with reason; history still readable.
- **Overwrite warning**: inline amber banner in the panel with runner text "overwriting the last run's files — start a new job instead to keep them"; actions `[ overwrite and run ]` and `[ start as new job ]` (sets `newJob` + asks for a name).
- **Failed**: red `✗ step — message`, `[ retry ]` resumes from failed step; retry errors (source gone, step folder missing) shown inline.
- **Imported**: grey status, note "imported in place — not run by the runner".

## Accessibility Checklist
- [ ] Visible `:focus-visible` outline (2px accent) on every control; full keyboard path: list -> tabs -> actions -> panel
- [ ] Tabs: `role=tablist/tab/tabpanel`, `aria-selected`, arrow keys + keys `1/2/3`
- [ ] Touch targets >= 44px at <=720px (32px desktop compact)
- [ ] Status never colour-only: always `[✓] [×] […] [!]` marks + word
- [ ] Contrast AA for text and borders in both themes (use final tokens below; recheck after edits)
- [ ] Log is `role=log`, `aria-live=polite`, focusable (`tabindex=0`) for keyboard scroll
- [ ] Panel: focus moves to path field on open, returns to `[ + new job ]` on close; Esc closes
- [ ] Form labels bound (`<label for>`), errors via `aria-describedby`, `aria-invalid`
- [ ] `prefers-reduced-motion`: no transitions/spinner animation
- [ ] RTL: names `unicode-bidi: plaintext`, `dir=auto`; layout stays LTR
- [ ] `lang`, `<title>`, `color-scheme` set; works at 320px with no horizontal page scroll

## Testing Checklist
- [ ] `pytest tests/audiobook/ui -v` (real server on port 0, `SAWT_HOME` -> tmp, runner steps stubbed or tiny fixture book)
- [ ] `/api/jobs` empty, populated, corrupt `jobs.json` -> clear error
- [ ] `POST /api/runs`: file, folder (skips listed, `.doc` rejected), bad path, duplicate name, overwrite -> 409 then confirmed, busy -> 409
- [ ] Forced failure -> `✗` in log, retry resumes from failed step, earlier steps untouched
- [ ] Rename changes label only; output folder fixed
- [ ] Path safety: `..`, symlink escape, absolute path outside job dirs, unknown step -> 403/404; `open` never uses a shell
- [ ] Binds 127.0.0.1 only; foreign `Host` rejected
- [ ] Restart persistence: new server instance sees same jobs/runs
- [ ] Manual (browser, `/run`): light + dark, theme persists, left list scrolls independently with 30+ jobs, log scrolls inside pane, 360px width, Arabic job names, keyboard-only pass, reduced motion
- [ ] Full suite still green (`pytest tests/ -v`)

## Design Tokens (final; from preview `:root`)
| Token | Light | Dark |
|---|---|---|
| bg | #e1e2e7 | #1a1b26 |
| panel | #d0d5e3 | #1f2335 |
| panel2 | #e9e9ed | #24283b |
| text | #3257ad | #c0caf5 |
| textDim | #4c598a | #a9b1d6 |
| textFaint | #6b74a6 | #66709f |
| border | #c4c8da | #292e42 |
| borderStrong | #7b84ad | #626d99 |
| accent | #215aa8 | #7aa2f7 |
| fieldBg | #ffffff | #16161e |
| green / greenBg | #496130 / #dfe7d4 | #9ece6a / #1c2b23 |
| red / redBg | #af1e48 / #fbe0e8 | #f7768e / #2b1822 |
| amber / amberBg | #705632 / #f0e6d3 | #e0af68 / #2b2416 |
| cyan / cyanBg | #006283 / #d6ecf1 | #7dcfff / #182634 |

- Font `'Courier Prime','Courier New',monospace` (Google Fonts stylesheet, fallback system mono); 13px/1.5 body, 12 small, 15 sub, 17 title; weights 400/700.
- Radius 0 (4px rare), no shadows; active tab `inset 0 -2px 0 var(--accent)`. Left pane 300px, breakpoint 720px.
- Theme CSS: `:root` light; `:root[data-theme=dark]`; `@media (prefers-color-scheme: dark){:root:not([data-theme=light])}`; `:root[data-theme=light]{color-scheme:light}`.
