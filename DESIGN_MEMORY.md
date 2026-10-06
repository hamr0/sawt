# DESIGN_MEMORY — Sawt Runner UI

Source of truth for look and feel. Reference: variant D preview (owner-approved 2026-10-05). Tokens: see `DESIGN_PLAN.md`.

## Brand Tone
- Adjectives: utilitarian, warm, terminal-like, minimal, compact.
- Avoid: fancy styling, gradients, shadows, animation for show, icons-as-decoration, marketing copy, modals, density that clutters.
- Voice of copy: lowercase, plain, literal (`ready for audio — paused`, `no jobs yet`).

## Layout & Spacing
- Desktop-first, must not break at phone width. Two panes: left 300px job list, right fluid.
- Left list and right log scroll inside their own panes; page and right pane chrome stay put.
- Below 720px: single column, list becomes a `<select>`, targets 44px.
- Density compact: paddings 6px 8px (tight), 10px (base), 10px 16px (section). Gap 6-8px.
- Radius 0 (4px only if rare). No drop shadows; borders 1px; active tab = inset 2px accent underline.

## Typography
- Courier Prime, fallback Courier New, monospace. Body 13px/1.5; small 12; subhead 15; title 17.
- Weights 400 and 700 only. Bold for names, selected tab, primary action, final gate line.
- Arabic names: `unicode-bidi: plaintext`, wrap anywhere; never mirror layout.

## Color
- Primary/accent: blue (`#215aa8` light, `#7aa2f7` dark) for links, primary button, selection.
- Secondary: none; dim text for metadata.
- Neutral strategy: pale blue-grey surfaces (bg/panel/panel2), 2-3 colours max on screen; status colours only for state.
- Semantic: green ready/ok, red failed, amber missing/warning/overwrite, cyan running, dim grey imported/skipped.
- Themes: light default; dark via toggle or `prefers-color-scheme` (guarded by `:root:not([data-theme=light])`). Contrast-tuned tokens in `DESIGN_PLAN.md` win over the brief. Colour is never the only signal.

## Interaction Patterns
- Forms: one panel opened from `[ + new job ]`; path box (not upload), name, fiction/non-fiction, SSML checkbox (off), Start. Inline validation under the field; disabled button shows why.
- Modals/drawers: no modals, ever. Overwrite warning = inline amber banner with `[ overwrite and run ]` / `[ start as new job ]`. Panel is inline above the list/tabs.
- Lists: one card per job (name, status mark, date); selected card gets accent border. Runs expand in place (progressive disclosure).
- Buttons: bracketed text `[ start ]`; primary = accent + bold; disabled = dashed, faint.
- Tabs: numbered `[1] Run [2] History [3] Artifacts`, keys 1/2/3.
- Feedback: live append-only log with `✓ ✗ >`; status marks `[✓] [×] […] [!]`; errors in red banner with Retry; messages in a quiet `.msg` line, no toasts that vanish.
- Theme choice in localStorage inside try/catch, per-viewer convenience only; page works without it.
- Lab-only items (demo strip, lab note, fixtures) never ship.

## Accessibility Rules
- Visible focus ring (2px accent, 1px offset) on all controls; keyboard-complete.
- Targets 32px desktop min, 44px on phone. AA contrast for text and borders in both themes.
- Semantic roles: tablist/tab/tabpanel, `role=log` + `aria-live=polite`, `aria-expanded` on run rows, labelled inputs with `aria-describedby` errors.
- Honour `prefers-reduced-motion`; no motion required to understand state.

## Repo Conventions
- Package `src/audiobook/ui/`: `core.py` (handlers, server), `page.py` (inline HTML/CSS/JS constant), `__main__.py`; tests in `tests/audiobook/ui/test_core.py`.
- Python stdlib `http.server` only, 127.0.0.1, no new deps, no JS framework, no build step, no CSS framework.
- Styling: plain CSS with `:root` custom properties; classes scoped under one root class; no inline colours, always tokens.
- JS: vanilla, one `state` object, small `render*()` per component, event delegation.
- Primitives to reuse: `.btn` (`.pri`, `.warn`, `.mini`), `.lnk`, `.field`, `.opt`, `.card`, `.tab`, `.banner` (`b-amber|b-red|b-cyan`), `.log`, `.run`, `.art`, `.empty`, `.drawer`.
- The UI only calls `src/audiobook/runner` public functions; runner is the single writer of `jobs.json`. Data boundaries, not stage imports.
- Files served only from known job `_sawt/` folders and repo `output/`; folder opening via argv list, never a shell.
