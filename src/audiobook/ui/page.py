"""The single inline page: HTML + CSS (tokens) + vanilla JS. No static dir, no build step.

Look follows DESIGN_PLAN.md / DESIGN_MEMORY.md (owner-approved variant D).
"""

# Courier Prime (SIL OFL, see static/OFL.txt), latin subset, served from /static/ by the UI server.
FONT_FACE = """@font-face{font-family:'Courier Prime';font-style:normal;font-weight:400;font-display:swap;src:url(/static/CourierPrime-Regular.woff2) format('woff2')}
@font-face{font-family:'Courier Prime';font-style:normal;font-weight:700;font-display:swap;src:url(/static/CourierPrime-Bold.woff2) format('woff2')}"""

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>sawt - every book has a voice</title>
<style>
__FONT_FACE__
:root{
  --bg:#e1e2e7;--panel:#d0d5e3;--panel2:#e9e9ed;--text:#3257ad;--textDim:#4c598a;--textFaint:#6b74a6;
  --border:#c4c8da;--borderStrong:#7b84ad;--accent:#215aa8;--fieldBg:#ffffff;
  --green:#496130;--greenBg:#dfe7d4;--red:#af1e48;--redBg:#fbe0e8;--amber:#705632;--amberBg:#f0e6d3;--cyan:#006283;--cyanBg:#d6ecf1;
  --font:'Courier Prime','Courier New',monospace;
  color-scheme:light;
}
:root[data-theme="dark"]{
  --bg:#1a1b26;--panel:#1f2335;--panel2:#24283b;--text:#c0caf5;--textDim:#a9b1d6;--textFaint:#66709f;
  --border:#292e42;--borderStrong:#626d99;--accent:#7aa2f7;--fieldBg:#16161e;
  --green:#9ece6a;--greenBg:#1c2b23;--red:#f7768e;--redBg:#2b1822;--amber:#e0af68;--amberBg:#2b2416;--cyan:#7dcfff;--cyanBg:#182634;
  color-scheme:dark;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
  --bg:#1a1b26;--panel:#1f2335;--panel2:#24283b;--text:#c0caf5;--textDim:#a9b1d6;--textFaint:#66709f;
  --border:#292e42;--borderStrong:#626d99;--accent:#7aa2f7;--fieldBg:#16161e;
  --green:#9ece6a;--greenBg:#1c2b23;--red:#f7768e;--redBg:#2b1822;--amber:#e0af68;--amberBg:#2b2416;--cyan:#7dcfff;--cyanBg:#182634;
  color-scheme:dark;
  }
}
:root[data-theme="light"]{color-scheme:light}

*{box-sizing:border-box}
html{background:var(--bg)}
body{margin:0;background:var(--bg);color:var(--text);font:13px/1.5 var(--font);height:100vh;display:flex;flex-direction:column;overflow:hidden}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.appbar{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:4px 16px;min-height:44px;border-bottom:1px solid var(--border);background:var(--panel);flex:none}
.themebtn{font:inherit;font-size:15px;color:var(--text);background:none;border:1px solid var(--borderStrong);border-radius:0;padding:2px 8px;min-height:32px;cursor:pointer;white-space:nowrap}
.themebtn:hover{background:var(--panel2)}
.themebtn:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
#app{flex:1;min-height:0}

.v{font:13px/1.5 var(--font);color:var(--text);background:var(--bg);min-width:0}
.v button,.v input,.v select{font:inherit;color:inherit}
.v .dim{color:var(--textDim)}
.v .pth{direction:ltr;unicode-bidi:isolate;text-align:left;line-height:1.8;padding-bottom:2px}
.v .pth .seg{display:inline-block;max-width:100%;white-space:nowrap;overflow-wrap:anywhere;unicode-bidi:isolate;overflow:visible}
.v .nmi{white-space:nowrap;overflow-wrap:anywhere}
.v .nm{unicode-bidi:plaintext;text-align:start;overflow-wrap:anywhere}
.v .btn{background:var(--panel2);border:1px solid var(--borderStrong);border-radius:0;padding:6px 10px;min-height:32px;cursor:pointer;color:var(--text);white-space:normal}
.v .btn:hover{background:var(--panel)}
.v .btn:active{background:var(--border)}
.v .btn:focus-visible,.v .lnk:focus-visible,.v .tab:focus-visible,.v .cardmain:focus-visible,.v .runhead:focus-visible,.v .field:focus-visible,.v a:focus-visible,.v .log:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.v .opt:focus-within{outline:2px solid var(--accent);outline-offset:1px}
.v .btn[disabled]{color:var(--textFaint);background:none;border-color:var(--border);border-style:dashed;cursor:not-allowed}
.v .btn.pri{color:var(--accent);border-color:var(--accent);font-weight:700}
.v .btn.warn{color:var(--amber);border-color:var(--amber)}
.v .btn.pri[disabled]{color:var(--textFaint);border-color:var(--border);font-weight:400}
.v .btn.mini{min-height:26px;padding:2px 6px;font-size:12px}
.v .lnk{background:none;border:0;padding:0;color:var(--accent);cursor:pointer;text-decoration:underline;font-size:12px}
.v .field{background:var(--fieldBg);border:1px solid var(--borderStrong);border-radius:0;padding:6px 8px;min-height:32px;width:100%;min-width:0}
.v .field[aria-invalid="true"]{border-color:var(--red)}
.v .field::placeholder{color:var(--textDim);opacity:1}
.v label.lbl{display:block;color:var(--textDim);font-size:12px;margin:0 0 2px}
.v .ferr{color:var(--red);font-size:12px;margin:-4px 0 8px}
.v .fhint{color:var(--textDim);font-size:12px;margin:-4px 0 8px}
.v fieldset{border:0;margin:0;padding:0;min-width:0;display:flex;gap:12px;flex-wrap:wrap}
.v .opt{display:inline-flex;align-items:center;gap:6px;cursor:pointer}
.v .opt input{margin:0;width:16px;height:16px;accent-color:var(--accent)}
.v .mk{font-weight:700;white-space:nowrap}
.v .st-ready{color:var(--green)}.v .st-running{color:var(--cyan)}.v .st-failed{color:var(--red)}.v .st-missing{color:var(--amber)}.v .st-imported,.v .st-none{color:var(--textDim)}.v .st-queued{color:var(--cyan)}.v .st-partial,.v .st-complete{color:var(--green)}.v .st-interrupted{color:var(--amber)}.v .st-stopped{color:var(--amber)}
.v .main{display:grid;grid-template-columns:360px minmax(0,1fr);grid-template-rows:minmax(0,1fr);height:100%}
.v .left{padding:10px;border-right:1px solid var(--border);min-width:0;overflow-y:auto}
.v .right{padding:10px 16px;min-width:0;min-height:0;display:flex;flex-direction:column;overflow:hidden}
.v .right>*{flex:none}
.v .right>.rpanel{flex:1 1 0;min-height:0;overflow-y:auto;display:flex;flex-direction:column}
.v .rpanel>*{flex:none}
.v .rpanel>.log{flex:1 1 0;min-height:160px}
.v .lh{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px;color:var(--textDim)}
.v .jobsel{display:none;margin-bottom:8px}
.v .card{display:flex;gap:4px;align-items:stretch;border:1px solid var(--border);background:var(--panel2);margin-bottom:6px}
.v .card.sel{background:var(--panel);border-color:var(--accent)}
.v .cardmain{flex:1;min-width:0;text-align:left;background:none;border:0;padding:6px 8px;cursor:pointer;display:block}
.v .card:hover{border-color:var(--borderStrong)}
.v .card.sel:hover{border-color:var(--accent)}
.v .card .btn{align-self:center;margin-right:6px}
.v .card .row2{display:block;color:var(--textDim);font-size:12px}
.v .rhead{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;margin-bottom:8px;font-size:15px}
.v .rhead .nm{font-weight:700;font-size:17px}
.v .rhead .btn{font-size:12px}
.v .hdr-ren{display:none}
.v .tabs{display:flex;border-bottom:1px solid var(--border);margin-bottom:10px;flex-wrap:wrap}
.v .tab{background:none;border:0;border-radius:0;padding:8px 12px;color:var(--textDim);cursor:pointer}
.v .tab:hover{background:var(--panel2)}
.v .tab[aria-selected="true"]{color:var(--text);font-weight:700;box-shadow:inset 0 -2px 0 var(--accent)}
.v .log{background:var(--fieldBg);border:1px solid var(--border);padding:10px;white-space:pre-wrap;overflow-wrap:anywhere;overflow-y:auto;margin-bottom:10px}
.v .log.small{margin:6px 0;max-height:50vh}
.v .l-ok{color:var(--green)}.v .l-fail{color:var(--red)}.v .l-det{color:var(--textDim);padding-left:2ch}
.v .l-skip{color:var(--textDim)}.v .l-run{color:var(--cyan)}.v .l-note{color:var(--amber)}.v .l-final{color:var(--amber);font-weight:700;margin-top:4px}
.v .acts{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0 0 10px}
.v dl.det{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:2px 12px;margin:0 0 10px}
.v dl.det dt{color:var(--textDim)}.v dl.det dd{margin:0;overflow-wrap:anywhere;line-height:1.8;padding-bottom:2px}
.v .banner{padding:8px 10px;border:1px solid;margin:8px 0;overflow-wrap:anywhere}
.v .b-amber{background:var(--amberBg);border-color:var(--amber);color:var(--amber)}
.v .b-red{background:var(--redBg);border-color:var(--red);color:var(--red)}
.v .b-cyan{background:var(--cyanBg);border-color:var(--cyan);color:var(--cyan)}
.v .banner .bacts{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
.v .banner .btn{background:var(--panel2)}
.v .banner .lnk{color:inherit}
.v .banner ul{margin:4px 0 0;padding-left:2ch}
.v .run{border:1px solid var(--border);background:var(--panel2);margin-bottom:6px}
.v .runhead{width:100%;text-align:left;background:none;border:0;padding:6px 8px;cursor:pointer;display:block;overflow-wrap:anywhere}
.v .runhead:hover{background:var(--panel)}
.v .runbody{padding:0 8px 8px}
.v .msg{min-height:20px;color:var(--textDim);margin-top:6px;overflow-wrap:anywhere}
.v .empty{border:1px dashed var(--borderStrong);padding:14px;color:var(--textDim);margin:8px 0}
.v .empty .bacts{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.v .ren{display:flex;gap:6px;flex-wrap:wrap;align-items:center;padding:6px 8px;width:100%}
.v .ren .field{flex:1 1 140px}
.v .ren .hint{flex-basis:100%;font-size:12px;color:var(--textDim)}
.v .ren .rerr{flex-basis:100%;color:var(--red);font-size:12px}
.v .busy{font-size:12px}
.v .ren-card .ren{padding:6px}
.v .ren-hdr{display:none}
.v a{color:var(--accent)}
.v .step{border:1px solid var(--border);background:var(--panel2);margin-bottom:8px}
.v .stephead{display:flex;gap:8px;align-items:center;justify-content:space-between;flex-wrap:wrap;padding:4px 8px}
.v .steptog{flex:1;min-width:0;text-align:left;background:none;border:0;padding:4px 0;cursor:pointer;overflow-wrap:anywhere}
.v .steptog:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.v .stepmiss{padding:4px 0}
.v .stepbody{padding:0 8px 8px}
.v .gname{color:var(--textDim);font-size:12px;margin:10px 0 4px;padding-top:6px;border-top:1px solid var(--border)}
.v .fgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(max(200px,calc((100% - 36px)/4)),1fr));gap:2px 12px}
.v .fcell{display:flex;gap:4px;align-items:baseline;min-width:0;direction:ltr}
.v .fcell a{flex:0 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.v .fcell .sz{flex:none;color:var(--textDim);font-size:12px;white-space:nowrap}
.v .srch{display:flex;gap:6px;align-items:center;margin:0 0 8px}
.v .srch .field{flex:1}
.v .rowsbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0 0 6px}
.v .brow{border:1px solid var(--border);background:var(--panel2);padding:4px 8px;margin-bottom:4px}
.v .brow .bline{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:2px;padding-left:22px}
.v .brow .bline .field{flex:1 1 140px;width:auto}
.v .brow .stat{font-size:12px;color:var(--textDim)}
.v .brow .ferr{margin:2px 0 0 22px}
.v .brow.off{opacity:.6}
.v .skiprow{color:var(--textFaint);font-size:12px;padding:1px 0;overflow-wrap:anywhere}
.v .drawer{border:1px solid var(--accent);background:var(--panel);padding:10px;margin-bottom:10px}
.v .drawer h3{margin:0 0 8px;font-size:13px;display:flex;justify-content:space-between;align-items:center}
.v .drawer .field{margin-bottom:8px}
.v .drawer fieldset{margin-bottom:8px}
.v .drawer .banner{margin:8px 0 0}
.v .drawer .go{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:8px}

@media (max-width:720px){
  body{height:auto;min-height:100vh;overflow:visible}
  .v .main{grid-template-columns:minmax(0,1fr);grid-template-rows:auto;height:auto}
  .v .left{border-right:0;border-bottom:1px solid var(--border);padding:10px 12px;overflow:visible}
  .v .right{padding:10px 12px;overflow:visible}
  .v .right>.rpanel{overflow:visible;display:block}
  .v .rpanel>.log{max-height:60vh;min-height:0}
  .v .jobsel{display:block}
  .v .list{display:none}
  .v .btn,.v .field,.v .tab,.v .cardmain,.v .runhead,.v .opt,.v .jobsel{min-height:44px}
  .v .btn.mini{min-height:44px;padding:4px 10px}
  .v .lnk{min-height:44px;padding:0 6px}
  .v .opt{padding:0 4px}
  .v .tab{flex:1 1 auto;text-align:center}
  .v .hdr-ren{display:inline-block}
  .v .ren-hdr{display:flex}
  .v .cardren,.v .ren-card{display:none}
  .v dl.det{grid-template-columns:minmax(0,1fr)}
  .v dl.det dd{margin-bottom:6px}
  .appbar{padding-left:12px;padding-right:12px}
  .themebtn{min-height:44px;min-width:44px}
}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important;animation:none!important}}
</style>
</head>
<body>
<div class="appbar"><span><b>[sawt]</b> <span style="color:var(--textDim)">- every book has a voice</span></span><button type="button" class="themebtn" id="themeBtn" aria-label="Toggle theme">[ &#9728; ]</button></div>
<div class="v" id="app"><div class="empty" style="margin:16px">loading...</div></div>

<script>
(function () {
  'use strict';
  var MK = { ready: '[✓]', running: '[>]', failed: '[×]', missing: '[?]', imported: '[·]', none: '[ ]', queued: '[…]', stopped: '[■]', partial: '[·]', complete: '[✓]', interrupted: '[!]' };
  var STX = { ready: 'ready for audio — paused', running: 'running', failed: 'failed', missing: 'missing', imported: 'imported', none: 'no runs', queued: 'queued', stopped: 'stopped', partial: 'partial', complete: 'complete', interrupted: 'interrupted' };
  var LABEL = { ingest: 'ingesting', chapters: 'splitting chapters', dialogue: 'detecting dialogue', ssml: 'generating SSML' };
  var STEPS = ['ingest', 'chapters', 'dialogue', 'ssml'];
  var GATE = 'ready for audio — paused before paid step';
  var TABS = ['Run', 'History', 'Artifacts'];
  var el = document.getElementById('app');

  var state = {
    jobs: [], loading: true, jobsErr: '', unreachable: false,
    selected: null, job: null, jobLoading: false, jobErr: '',
    tab: 1, view: null, open: {},
    busy: false, current: null, queued: [], runError: null, dismissedErr: '', statusKnown: false,
    panel: false, form: { path: '', name: '', fiction: true, ssml: false, newJob: false },
    offerNew: false, formErr: {}, formNote: '', generalErr: '', overwrite: null, starting: false,
    skipped: [], queuedNames: [], msg: '', retryErr: '',
    renaming: null, renameVal: '', renameErr: '', focusNext: null, stopping: false, confirmDel: null, delErr: '', search: '',
    files: null, filesErr: '', fexp: {},
    freeName: '', freeFor: '', scan: null  /* folder pick list: { rows: [{path,file,job,stem,on,nm,newJob}], skipped: [] }; null = single file or no path */
  };
  var polling = false, scanTimer = null, SCAN_DELAY_MS = 250;

  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function nm(s) { return '<span class="nm" dir="auto">' + esc(s) + '</span>'; }
  /* a path: LTR overall, each /-separated segment its own bidi isolate, line breaks only after "/" */
  function pthInner(escaped) {
    return escaped.split('/').map(function (seg) { return seg ? '<bdi dir="ltr" class="seg">' + seg + '</bdi>' : ''; }).join('/<wbr>');
  }
  function pth(s) { return '<bdi class="pth" dir="ltr">' + pthInner(esc(s)) + '</bdi>'; }
  function isPath(t) { return /^(\/|~\/)/.test(t); }
  /* message text (plain from the server): paths render LTR per segment; quoted 'names' and (names) are isolates */
  function msgHtml(s) {
    return esc(s).replace(/&#39;([^&]*?)&#39;|\(([^()]*)\)|(^|[\s])((?:\/|~\/)[^\s,;)]*)/g, function (m, q, par, sp, p) {
      if (p !== undefined) return sp + '<bdi class="pth" dir="ltr">' + pthInner(p) + '</bdi>';
      var t = q !== undefined ? q : par, inner = isPath(t) ? '<bdi class="pth" dir="ltr">' + pthInner(t) + '</bdi>' : '<bdi dir="auto" class="nmi">' + t + '</bdi>';
      return q !== undefined ? '&#39;' + inner + '&#39;' : '(' + inner + ')';
    });
  }
  function when(d) { return d ? String(d).replace('T', ' ') : ''; }
  function dayOf(d) { return d ? String(d).slice(0, 10) : ''; }
  function key(s) {
    if (s === 'missing') return 'missing';
    if (s === 'failed') return 'failed';
    if (s === 'running') return 'running';
    if (s === 'imported') return 'imported';
    if (s === 'stopped') return 'stopped';
    if (s && s.indexOf('ready') === 0) return 'ready';
    return 'none';
  }
  function mk(k) { return '<span class="mk st-' + k + '" title="' + esc(STX[k]) + '">' + MK[k] + '</span>'; }
  function settingsText(r) { return (r.settings.fiction ? 'fiction' : 'non-fiction') + ' · SSML ' + (r.settings.ssml ? 'on' : 'off'); }
  function stale(k) { return k === 'running' && state.statusKnown && !state.busy; }
  /* queue view: a queued book's card comes from worker status; a book that never ran has no job entry yet */
  function qinfo(name) {
    var i = state.queued.indexOf(name);
    if (i < 0) return null;
    var base = state.current ? 1 : 0;
    return { n: base + i + 1, total: base + state.queued.length };
  }
  function allRows() {
    var names = state.jobs.map(function (j) { return j.name; });
    return state.jobs.concat(state.queued.filter(function (n) { return names.indexOf(n) < 0; }).map(function (n) {
      return { name: n, status: 'queued', date: '', runs: 0, placeholder: true };
    }));
  }
  /* the one place that maps a job (latest run + worker status) to its card status; "missing" wins over everything */
  function cardStatus(r) {
    var steps = r.steps || {}, q = qinfo(r.name), s = r.status, ok = STEPS.filter(function (x) { return steps[x] === 'ok'; });
    if (r.missing || s === 'missing') return { k: 'missing', word: 'missing', why: 'output folder deleted' };
    if (q) return { k: 'queued', word: 'queued', why: qtext(q) };
    if (s === 'running') {
      if (state.statusKnown && state.current !== r.name) return { k: 'interrupted', word: 'interrupted', why: 'retry to continue' };
      var cur = STEPS.filter(function (x) { return steps[x] === 'running'; })[0];
      return { k: 'running', word: 'running', why: cur ? LABEL[cur] : 'starting' };
    }
    if (s === 'failed') return { k: 'failed', word: 'failed', why: (STEPS.filter(function (x) { return steps[x] === 'failed'; })[0] || 'a step') + ' error' };
    if (s === 'stopped') return { k: 'stopped', word: 'stopped', why: 'after ' + (ok.length ? ok[ok.length - 1] : 'start') + ', retry to continue' };
    if (s === 'imported') return { k: 'imported', word: 'imported', why: 'artifacts only, no run log' };
    if (s && s.indexOf('ready') === 0) {
      return steps.audio === 'ok' ? { k: 'complete', word: 'complete', why: 'artifacts + audio' } : { k: 'partial', word: 'partial', why: 'artifacts ready, audio pending' };
    }
    return { k: 'none', word: 'no runs', why: 'not started yet' };
  }
  function rowKey(r) { return qinfo(r.name) ? 'queued' : key(r.status); }
  function matches(r) {
    var q = state.search.trim().toLowerCase();
    if (!q) return true;
    var src = (r.source || '').split('/').pop();
    return r.name.toLowerCase().indexOf(q) >= 0 || src.toLowerCase().indexOf(q) >= 0;
  }
  function visibleRows() { return allRows().filter(matches); }
  function qtext(q) { return q.n + ' of ' + q.total; }
  function stem(p) {
    var b = p.replace(/\/+$/, '').split('/').pop() || '';
    return b.replace(/\.(epub|docx|txt)$/i, '');
  }

  /* ---------- api ---------- */
  function api(method, path, body) {
    var opt = { method: method, headers: {} };
    if (body !== undefined) { opt.headers['Content-Type'] = 'application/json'; opt.body = JSON.stringify(body); }
    return fetch(path, opt).then(function (r) {
      return r.json().then(function (d) { return d; }, function () { return {}; }).then(function (d) {
        state.unreachable = false;
        return { ok: r.ok, status: r.status, data: d };
      });
    }, function () {
      state.unreachable = true;
      return { ok: false, status: 0, data: { error: 'server unreachable' } };
    });
  }
  function enc(n) { return encodeURIComponent(n); }

  function loadStatus() {
    return api('GET', '/api/status').then(function (r) {
      if (!r.ok) return;
      state.busy = !!r.data.busy; state.current = r.data.current; state.queued = r.data.queued || [];
      state.runError = r.data.error; state.stopping = !!r.data.stopping; state.statusKnown = true;
    });
  }
  function loadJobs() {
    return api('GET', '/api/jobs').then(function (r) {
      state.loading = false;
      if (!r.ok) { state.jobsErr = r.data.error || 'could not load jobs'; return; }
      state.jobsErr = ''; state.jobs = r.data.jobs;
      var names = allRows().map(function (j) { return j.name; });
      if (state.selected === null || names.indexOf(state.selected) < 0) {
        var want = hashJob();
        state.selected = names.indexOf(want) >= 0 ? want : (names[0] || null);
        state.job = null; state.files = null;
      }
    });
  }
  function loadJob() {
    var name = state.selected;
    if (name === null) { state.job = null; return Promise.resolve(); }
    if (!state.jobs.some(function (j) { return j.name === name; })) { state.job = null; state.jobErr = ''; state.jobLoading = false; return Promise.resolve(); }  /* queued placeholder: no job entry yet */
    return api('GET', '/api/jobs/' + enc(name)).then(function (r) {
      if (state.selected !== name) return;
      state.jobLoading = false;
      if (r.ok) { state.job = r.data; state.jobErr = ''; } else { state.job = null; state.jobErr = r.data.error || 'could not load job'; }
    });
  }
  /* artifacts listing: loaded when the tab opens, the job changes while it is open, or a run finishes (no watching) */
  function loadFiles() {
    var name = state.selected;
    if (name === null) { state.files = null; return Promise.resolve(); }
    return api('GET', '/api/jobs/' + enc(name) + '/files').then(function (r) {
      if (state.selected !== name) return;
      if (r.ok) { state.files = r.data; state.filesErr = ''; } else { state.files = null; state.filesErr = r.data.error || 'could not list files'; }
    });
  }
  function onTab() { if (state.tab === 3 && state.selected !== null) { state.fexp = {}; loadFiles().then(render); } }
  function refreshAll() {
    var was = state.busy, finished = false;
    return loadStatus().then(function () { finished = was && !state.busy; }).then(loadJobs).then(loadJob).then(function () {
      if (state.tab === 3 && (finished || state.files === null)) return loadFiles();
    }).then(function () { render(); });
  }

  function tick() {
    refreshAll().then(function () {
      if (state.busy && !state.unreachable) setTimeout(tick, 1000);
      else if (state.unreachable) setTimeout(tick, 3000);
      else polling = false;
    });
  }
  function startPolling() { if (!polling) { polling = true; tick(); } }

  /* ---------- selection / hash ---------- */
  function hashJob() {
    var m = /^#job=(.*)$/.exec(location.hash);
    if (!m) return null;
    try { return decodeURIComponent(m[1]); } catch (e) { return null; }
  }
  function selectJob(name) {
    state.selected = name; state.job = null; state.jobLoading = true; state.view = null; state.files = null; state.filesErr = '';
    state.msg = ''; state.retryErr = ''; state.renaming = null; state.confirmDel = null; state.delErr = '';
    try { history.replaceState(null, '', '#job=' + enc(name)); } catch (e) { }
    render();
    loadJob().then(render);
    onTab();
  }
  window.addEventListener('hashchange', function () {
    var h = hashJob();
    if (h !== null && h !== state.selected && allRows().some(function (j) { return j.name === h; })) selectJob(h);
  });

  /* ---------- log ---------- */
  function runLines(run) {
    var L = [];
    if (run.status === 'imported') L.push(['note', '# imported in place — not run by the runner']);
    (run.log || []).forEach(function (line) {
      var t = line.replace(/^\s+/, '');
      if (line.indexOf('✓') === 0) L.push(['ok', line]);
      else if (line.indexOf('✗') === 0) L.push(['fail', line]);
      else if (t.indexOf('>') === 0) L.push(['det', t]);
      else if (line === GATE) L.push(['final', line]);
      else if (/ — skipped/.test(line)) L.push(['skip', '– ' + line]);
      else L.push(['note', line]);
    });
    if (run.status === 'running') {
      STEPS.forEach(function (s) { if (run.steps[s] === 'running') L.push(['run', '▶ ' + LABEL[s] + ' …']); });
    }
    var failed = STEPS.filter(function (s) { return run.steps[s] === 'failed'; })[0];
    if (failed) L.push(['note', 'stopped on error — retry resumes from "' + LABEL[failed] + '"; earlier steps are kept']);
    return L;
  }
  function logHtml(run) {
    var L = runLines(run);
    if (!L.length) return '<div class="l l-skip">no log lines yet</div>';
    return L.map(function (l) { return '<div class="l l-' + l[0] + '">' + esc(l[1]) + '</div>'; }).join('');
  }

  /* ---------- pieces ---------- */
  function tabsHtml() {
    return '<div class="tabs" role="tablist" aria-label="Job views">' + TABS.map(function (t, i) {
      var sel = state.tab === i + 1;
      return '<button type="button" role="tab" id="tab-' + (i + 1) + '" class="tab" aria-selected="' + sel + '" aria-controls="tabpanel" tabindex="' + (sel ? 0 : -1) + '" data-act="tab" data-arg="' + (i + 1) + '">[' + (i + 1) + '] ' + t + '</button>';
    }).join('') + '</div>';
  }
  function detailsHtml(job, run) {
    return '<dl class="det"><dt>source</dt><dd>' + (job.source ? pth(job.source) : '(unknown)') + '</dd><dt>output</dt><dd>' + pth(job.output) +
      '</dd><dt>settings</dt><dd>' + settingsText(run) + '</dd><dt>started</dt><dd>' + esc(when(run.date)) + '</dd></dl>';
  }
  function failedStep(run) { return STEPS.filter(function (s) { return run.steps[s] === 'failed'; })[0] || null; }

  function resumeStep(run) { return STEPS.filter(function (s) { return run.steps[s] !== 'ok' && run.steps[s] !== 'skipped'; })[0] || null; }
  /* job actions: retry (restart), stop, delete; job is null for a queued book that has no history yet */
  function actsHtml(name, job, run, canRetry) {
    var h = '<div class="acts" data-acts>';
    if (canRetry) {
      var why = job.missing ? 'output folder is gone' : state.busy ? 'a run is in progress' : '';
      var from = resumeStep(run);
      h += '<button type="button" class="btn pri" data-act="retry" data-fid="retry"' + (why ? ' disabled aria-disabled="true"' : '') + '>[ retry ]</button>' +
        (why ? '<span class="dim">' + esc(why) + '</span>' : from ? '<span class="dim">resumes from "' + esc(LABEL[from]) + '"</span>' : '');
    }
    if (state.busy) {
      h += '<button type="button" class="btn warn" data-act="stop" data-fid="stop">[ stop ]</button>' +
        (state.stopping ? '<span class="dim">stopping after the current step…</span>' : '<span class="dim">clears the queue; the running book stops after its current step</span>');
    }
    if (job) {
      var held = state.current === name || state.queued.indexOf(name) >= 0;
      h += '<button type="button" class="btn" data-act="delask" data-fid="delask"' + (held ? ' disabled aria-disabled="true"' : '') + '>[ delete ]</button>' + (held ? '<span class="dim">running or queued — stop it first</span>' : '');
    }
    h += '</div>';
    if (job && state.confirmDel === name) {
      h += '<div class="banner b-amber" role="group" aria-label="Confirm delete">Remove ' + nm(name) + ' from history? Files on disk stay: ' + pth(job.output) +
        '<div class="bacts"><button type="button" class="btn warn" data-act="delyes" data-fid="delyes">[ remove ]</button><button type="button" class="btn" data-act="delno" data-fid="delno">[ cancel ]</button></div></div>';
    }
    if (state.delErr) h += '<div class="banner b-red" role="alert">' + msgHtml(state.delErr) + '</div>';
    return h;
  }
  function queuedBody(name) {
    var q = qinfo(name);
    return actsHtml(name, null, null, false) + '<div class="empty">queued — position ' + (q ? qtext(q) : '?') + '</div>';
  }
  function runTab(job) {
    if (!job.runs.length) return actsHtml(job.name, job, null, false) + '<div class="empty">no runs yet</div>';
    var latest = job.runs.length - 1;
    var idx = state.view === null || state.view > latest ? latest : state.view;
    var run = job.runs[idx], k = key(run.status), st = stale(k) && idx === latest;
    var h = actsHtml(job.name, job, run, idx === latest && (k === 'failed' || k === 'stopped' || st));
    var q = qinfo(job.name);
    if (q) h += '<div class="banner b-cyan">queued — position ' + qtext(q) + '</div>';
    if (state.retryErr) h += '<div class="banner b-red" role="alert">' + msgHtml(state.retryErr) + '</div>';
    if (idx !== latest) h += '<div class="banner b-cyan">viewing an older run — <button type="button" class="lnk" data-act="latest">[ show latest ]</button></div>';
    if (st) h += '<div class="banner b-amber">no run is active — this run was interrupted. retry resumes from the step that did not finish.</div>';
    h += '<div class="log" data-log role="log" aria-live="polite" tabindex="0" aria-label="Run log" aria-busy="' + (k === 'running' && !st) + '">' + logHtml(run) + '</div>';
    return h + detailsHtml(job, run);
  }
  function histTab(job) {
    if (!job.runs.length) return '<div class="empty">no runs yet</div>';
    var out = '';
    for (var i = job.runs.length - 1; i >= 0; i--) {
      var r = job.runs[i], open = !!state.open[job.name + '#' + i], k = key(r.status);
      if (i === job.runs.length - 1 && stale(k)) k = 'running';
      out += '<div class="run"><button type="button" class="runhead" data-act="toggle" data-arg="' + i + '" aria-expanded="' + open + '">' + (open ? '▾' : '▸') + ' ' + mk(k) + ' ' + esc(when(r.date)) +
        ' <span class="dim">· ' + settingsText(r) + (k === 'imported' ? ' · imported' : '') + '</span></button>';
      if (open) {
        out += '<div class="runbody">' + (k === 'imported' ? '<div class="dim">imported in place — not run by the runner</div>' : '') +
          '<div class="log small" tabindex="0">' + logHtml(r) + '</div>';
        if (r.errors && r.errors.length) {
          out += '<div class="banner b-red">' + r.errors.map(function (e) { return esc(LABEL[e.step] || e.step) + ' — ' + msgHtml(e.message); }).join('<br>') + '</div>';
        }
        out += '<button type="button" class="btn mini" data-act="viewrun" data-arg="' + i + '">[ open in run ]</button></div>';
      }
      out += '</div>';
    }
    return out;
  }
  function fmtSize(n) { return n < 1024 ? n + ' B' : n < 1048576 ? (n / 1024).toFixed(1) + ' KB' : (n / 1048576).toFixed(1) + ' MB'; }
  function fileLink(job, f) {
    return '<div class="fcell"><a href="/view?job=' + enc(job) + '&amp;path=' + enc(f.path) + '" target="_blank" rel="noopener" dir="auto" title="' + esc(f.name) + '">' + esc(f.name) + '</a><span class="sz">(' + fmtSize(f.size) + ')</span></div>';
  }
  function disp(n) { return n.replace(/_/g, ' '); }
  function fmtTime(sec) {
    var d = new Date(sec * 1000), p = function (n) { return (n < 10 ? '0' : '') + n; };
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
  }
  function stepHtml(job, s) {
    if (!s.present) return '<div class="step"><div class="stephead"><span class="stepmiss">– <b>' + esc(disp(s.name)) + '</b> <span class="dim">· not produced</span></span></div></div>';
    var k = job + '|' + s.name, open = state.fexp[k] === true;  /* blocks start collapsed; reset on tab open and job change, kept on refresh */
    var h = '<div class="step"><div class="stephead"><button type="button" class="steptog" data-act="ftoggle" data-arg="' + esc(s.name) + '" aria-expanded="' + open + '">' + (open ? '▾' : '▸') + ' <b>' + esc(disp(s.name)) + '</b> <span class="dim">· ' + s.count + ' file' + (s.count === 1 ? '' : 's') + (s.mtime ? ' · ' + fmtTime(s.mtime) : '') + '</span></button>' +
      '<button type="button" class="btn mini" data-act="openfolder" data-arg="' + esc(s.name) + '">[ open folder ]</button></div>';
    if (open) {
      h += '<div class="stepbody">' + (s.count ? s.groups.map(function (g) {
        return (g.dir ? '<div class="gname">' + pth(g.dir + '/') + ' · ' + g.files.length + ' file' + (g.files.length === 1 ? '' : 's') + '</div>' : '') +
          '<div class="fgrid">' + g.files.map(function (f) { return fileLink(job, f); }).join('') + '</div>';
      }).join('') : '<div class="dim">empty</div>') + '</div>';
    }
    return h + '</div>';
  }
  function artTab(job) {
    if (state.filesErr) return '<div class="banner b-red" role="alert">' + msgHtml(state.filesErr) + '</div>';
    var f = state.files;
    if (!f) return '<div class="empty">loading...</div>';
    if (f.missing) return '<div class="banner b-amber">folder missing — ' + pth(f.output) + '</div>';
    return f.steps.map(function (s) { return stepHtml(job.name, s); }).join('');
  }

  function renameForm(cls) {
    var id = 'rn-' + cls;
    return '<form class="ren ' + cls + '" onsubmit="return false"><label class="sr" for="' + id + '">Job name</label><input class="field" id="' + id + '" data-f="rename" data-fid="rename" value="' + esc(state.renameVal) + '" dir="auto" autocomplete="off"' + (state.renameErr ? ' aria-invalid="true" aria-describedby="' + id + '-e"' : '') + '>' +
      '<button type="button" class="btn mini pri" data-act="rsave">[ save ]</button><button type="button" class="btn mini" data-act="rcancel">[ cancel ]</button>' +
      (state.renameErr ? '<span class="rerr" id="' + id + '-e" role="alert">' + esc(state.renameErr) + '</span>' : '') + '<span class="hint">display label only; the folder keeps its name</span></form>';
  }
  function banners() {
    var h = '';
    if (state.unreachable) h += '<div class="banner b-red" role="alert">server unreachable — <button type="button" class="lnk" data-act="reload">[ retry ]</button></div>';
    var e = state.runError;
    if (e && state.dismissedErr !== e.job + '|' + e.message) {
      h += '<div class="banner b-red" role="alert">run could not complete for ' + nm(e.job) + ' — ' + msgHtml(e.message) +
        ' <button type="button" class="lnk" data-act="dismissErr">[ dismiss ]</button></div>';
    }
    var note = '';
    if (state.queuedNames.length > 1) note += 'queued: ' + state.queuedNames.map(nm).join(', ') + '<br>';
    if (state.skipped.length) note += 'skipped ' + state.skipped.length + ' file(s):<ul>' + state.skipped.map(function (s) { return '<li>' + nm(s.file) + ' — ' + msgHtml(s.reason) + '</li>'; }).join('') + '</ul>';
    if (note) h += '<div class="banner b-cyan" role="status">' + note + '<div class="bacts"><button type="button" class="lnk" data-act="dismissSkip">[ dismiss ]</button></div></div>';
    return h;
  }
  function rightHtml() {
    var top = banners();
    if (state.jobsErr) return top + '<div class="banner b-red" role="alert">' + msgHtml(state.jobsErr) + ' <button type="button" class="lnk" data-act="reload">[ retry ]</button></div>';
    if (state.loading) return '<div class="empty">loading...</div>';
    if (!allRows().length) {
      return top + '<div class="empty">no jobs yet — [ + new job ] or [ import existing output/ ]<br>paste the absolute path of a book file or folder; steps 1-4 run straight through, then pause before the paid audio step.' +
        '<div class="bacts"><button type="button" class="btn" data-act="import" data-fid="import"' + (state.busy ? ' disabled aria-disabled="true"' : '') + '>[ import existing output/ ]</button></div></div><div class="msg" role="status">' + esc(state.msg) + '</div>';
    }
    var row = allRows().filter(function (j) { return j.name === state.selected; })[0];
    if (!row) return top + '<div class="empty">select a job</div>';
    if (row.placeholder) {
      var pq = qinfo(row.name), pb = state.tab === 1 ? queuedBody(row.name) : '<div class="empty">no runs yet</div>';
      return top + '<div class="rhead">' + mk('queued') + nm(row.name) + '<span class="dim"><span class="st-queued">queued</span>' + (pq ? ' · ' + qtext(pq) : '') + '</span></div>' + tabsHtml() +
        '<div class="rpanel" role="tabpanel" id="tabpanel" aria-labelledby="tab-' + state.tab + '">' + pb + '</div><div class="msg" role="status">' + esc(state.msg) + '</div>';
    }
    var job = state.job, cs = cardStatus(row);  /* the same mapping the card uses, so heading and card always agree */
    var h = top + '<div class="rhead">' + mk(cs.k) + nm(row.name) + '<span class="dim"><span class="st-' + cs.k + '">' + esc(cs.word) + '</span> · ' + esc(cs.why) + '</span><button type="button" class="btn mini hdr-ren" data-act="rename" data-arg="' + esc(row.name) + '">[ rename ]</button></div>';
    if (state.renaming === row.name) h += renameForm('ren-hdr');
    if (job && job.missing) h += '<div class="banner b-amber">output folder is gone — ' + pth(job.output) + '. history is still readable; retry is disabled.</div>';
    h += tabsHtml();
    var body;
    if (state.jobErr) body = '<div class="banner b-red" role="alert">' + msgHtml(state.jobErr) + '</div>';
    else if (!job) body = '<div class="empty">loading...</div>';
    else body = state.tab === 1 ? runTab(job) : state.tab === 2 ? histTab(job) : artTab(job);
    return h + '<div class="rpanel" role="tabpanel" id="tabpanel" aria-labelledby="tab-' + state.tab + '">' + body + '</div><div class="msg" role="status">' + esc(state.msg) + '</div>';
  }

  function cardHtml(j) {
    var sel = j.name === state.selected, name = esc(j.name), c = cardStatus(j);
    if (state.renaming === j.name) return '<div class="card sel ren-card">' + renameForm('ren-card-f') + '</div>';
    var line1 = mk(c.k) + ' ' + nm(j.name) + (j.placeholder ? '' : ' <span class="dim">' + esc(dayOf(j.date)) + ' · ' + j.runs + ' run' + (j.runs === 1 ? '' : 's') + '</span>');
    return '<div class="card' + (sel ? ' sel' : '') + '"><button type="button" class="cardmain" data-act="sel" data-arg="' + name + '" aria-current="' + sel + '"><span>' + line1 +
      '</span><span class="row2"><span class="st-' + c.k + '">' + esc(c.word) + '</span> · ' + esc(c.why) + '</span></button>' +
      (sel && !j.placeholder ? '<button type="button" class="btn mini cardren" data-act="rename" data-arg="' + name + '" aria-label="Rename ' + name + '">[ rename ]</button>' : '') + '</div>';
  }
  function jobSelect() {
    return '<select class="field jobsel" data-f="sel" data-fid="sel" aria-label="Select job">' + allRows().filter(function (j) { return matches(j) || j.name === state.selected; }).map(function (j) {
      var oq = qinfo(j.name);
      return '<option value="' + esc(j.name) + '"' + (j.name === state.selected ? ' selected' : '') + '>' + MK[cardStatus(j).k] + ' ' + esc(j.name) + ' — ' + (oq ? 'queued ' + qtext(oq) : esc(dayOf(j.date))) + '</option>';
    }).join('') + '</select>';
  }

  /* ---------- folder pick list ---------- */
  function rowName(r) { return r.job && !r.newJob ? r.job : r.nm.trim(); }
  /* mirrors the runner's _check_name (the server re-validates): same limits, same wording */
  var NAME_MAX = 100, NAME_INVISIBLE = /[\u0000-\u001f\u007f-\u009f\u00ad\u0600-\u0605\u061c\u06dd\u070f\u180e\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u206f\ufeff\ufff9-\ufffb]/;
  function nameProblem(n) {
    if (n.charAt(0) === '.') return 'job name cannot start with a dot';
    if (/[\/\\]/.test(n)) return 'job name cannot contain / or \\';
    if (NAME_INVISIBLE.test(n)) return 'job name cannot contain control or invisible characters';
    if (Array.from(n).length > NAME_MAX) return 'job name is too long (max ' + NAME_MAX + ' characters)';
    return '';
  }
  function rowErr(r, i) {
    if (!r.on || (r.job && !r.newJob)) return '';
    var n = r.nm.trim();
    if (!n) return 'name required';
    var bad = nameProblem(n);
    if (bad) return bad;
    if (state.jobs.some(function (j) { return j.name === n; })) return 'name already taken by another job';
    var rows = state.scan.rows;
    for (var k = 0; k < rows.length; k++) if (k !== i && rows[k].on && rowName(rows[k]) === n) return 'same name as another ticked book';
    return '';
  }
  function ticked() { return state.scan ? state.scan.rows.filter(function (r) { return r.on; }).length : 0; }
  function startLabel() {
    if (!state.scan) return '[ start ]';
    var n = ticked();
    return '[ start ' + n + ' book' + (n === 1 ? '' : 's') + ' ]';
  }
  /* single source of truth for the Start button; used by panelHtml() and syncStart() */
  function startState() {
    var why;
    if (state.scan) {
      var rows = state.scan.rows;
      why = !rows.length ? 'no runnable books in this folder' : !ticked() ? 'tick at least one book' :
        rows.some(function (r, i) { return rowErr(r, i); }) ? 'fix the name errors first' : '';
      if (!why && state.busy) why = 'a run is in progress; start unlocks when it ends';
    } else why = !state.form.path.trim() ? 'enter a path to start' : state.busy ? 'a run is in progress; start unlocks when it ends' : '';
    return { why: why, disabled: !!(why || state.starting) };
  }
  function rowsHtml() {
    var sc = state.scan, h = '<div class="rows" role="group" aria-label="Books found">';
    if (sc.rows.length) {
      h += '<div class="rowsbar"><button type="button" class="btn mini" data-act="rowsall" data-fid="rall">[ all ]</button><button type="button" class="btn mini" data-act="rowsnone" data-fid="rnone">[ none ]</button><span class="dim">' + ticked() + ' of ' + sc.rows.length + ' ticked</span></div>';
    }
    sc.rows.forEach(function (r, i) {
      var locked = r.job && !r.newJob;
      h += '<div class="brow' + (r.on ? '' : ' off') + '"><label class="opt"><input type="checkbox" data-f="rowon" data-i="' + i + '" data-fid="ron-' + i + '"' + (r.on ? ' checked' : '') + '> ' + nm(r.file) + '</label>' +
        '<div class="bline"><label class="sr" for="rn-f' + i + '">Job name for ' + esc(r.file) + '</label><input class="field" id="rn-f' + i + '" data-f="rowname" data-i="' + i + '" data-fid="rname-' + i + '" dir="auto" autocomplete="off" value="' + esc(locked ? r.job : r.nm) + '"' + (locked ? ' disabled' : '') + '>' +
        '<span class="stat">' + (locked ? 'existing job → new run' : 'new job') + '</span>' +
        (r.job ? '<label class="opt"><input type="checkbox" data-f="rownew" data-i="' + i + '" data-fid="rnew-' + i + '"' + (r.newJob ? ' checked' : '') + '> new job</label>' : '') + '</div>' +
        '<div class="ferr" data-rerr="' + i + '" role="alert">' + esc(rowErr(r, i)) + '</div></div>';
    });
    if (sc.skipped.length) h += '<div class="lbl">skipped</div>' + sc.skipped.map(function (k) { return '<div class="skiprow">' + nm(k.file) + ' — ' + msgHtml(k.reason) + '</div>'; }).join('');
    return h + '</div>';
  }
  function namePh() { return (state.freeName && state.freeFor === state.form.path.trim() ? state.freeName : stem(state.form.path.trim())) || 'defaults to the file name'; }
  /* in-place update (no re-render: that would steal focus/caret from the field) */
  function syncStart() {
    var b = el.querySelector('[data-start]'), w = el.querySelector('[data-start-why]'), n = el.querySelector('#f-name');
    var s = startState();
    if (state.scan) {
      var errs = el.querySelectorAll('[data-rerr]');
      for (var i = 0; i < errs.length; i++) errs[i].textContent = rowErr(state.scan.rows[+errs[i].dataset.rerr], +errs[i].dataset.rerr);
    }
    if (b) {
      b.textContent = startLabel();
      b.disabled = s.disabled;
      if (s.disabled) b.setAttribute('aria-disabled', 'true'); else b.removeAttribute('aria-disabled');
    }
    if (w) w.textContent = s.why;
    if (n) n.placeholder = namePh();
  }
  function panelHtml() {
    var f = state.form, e = state.formErr, ph = namePh(), why = startState().why;
    var h = '<div class="drawer" role="region" aria-label="New job"><h3><span>new job</span><button type="button" class="btn mini" data-act="drawer" data-fid="drawer-x">[ × close ]</button></h3>';
    h += '<label class="lbl" for="f-path">path to a book file or folder</label><input class="field" id="f-path" data-f="path" data-fid="path" dir="ltr" autocomplete="off" spellcheck="false" placeholder="absolute path to a book file or folder" value="' + esc(f.path) + '"' +
      (e.path ? ' aria-invalid="true" aria-describedby="e-path"' : '') + '>';
    if (e.path) h += '<div class="ferr" id="e-path" role="alert">' + msgHtml(e.path) + '</div>';
    if (state.scan) h += rowsHtml();
    else h += '<label class="lbl" for="f-name">job name (single file only)</label><input class="field" id="f-name" data-f="name" data-fid="name" dir="auto" autocomplete="off" placeholder="' + esc(ph) + '" value="' + esc(f.name) + '"' +
      (e.name ? ' aria-invalid="true" aria-describedby="e-name"' : state.formNote ? ' aria-describedby="e-name"' : '') + '>';
    if (!state.scan && e.name) h += '<div class="ferr" id="e-name" role="alert">' + msgHtml(e.name) + '</div>';
    else if (!state.scan && state.formNote) h += '<div class="fhint" id="e-name">' + esc(state.formNote) + '</div>';
    h += '<fieldset><legend class="sr">Book type</legend><label class="opt"><input type="radio" name="mode" data-f="mode" data-fid="mode-fic" value="fic"' + (f.fiction ? ' checked' : '') + '> fiction</label><label class="opt"><input type="radio" name="mode" data-f="mode" data-fid="mode-non" value="non"' + (!f.fiction ? ' checked' : '') + '> non-fiction</label></fieldset>';
    h += '<fieldset><label class="opt"><input type="checkbox" data-f="ssml" data-fid="ssml"' + (f.ssml ? ' checked' : '') + '> SSML (Azure only)</label>' +
      (!state.scan && (f.newJob || state.offerNew) ? '<label class="opt"><input type="checkbox" data-f="newJob" data-fid="newJob"' + (f.newJob ? ' checked' : '') + '> new job (keep the old files)</label>' : '') + '</fieldset>';
    h += '<div class="go"><button type="button" class="btn pri" data-act="start" data-fid="start" data-start' + (startState().disabled ? ' disabled aria-disabled="true"' : '') + '>' + startLabel() + '</button><span class="dim busy" data-start-why>' + esc(why) + '</span></div>';
    if (state.generalErr) h += '<div class="banner b-red" role="alert">' + msgHtml(state.generalErr) + '</div>';
    if (state.overwrite) {
      h += '<div class="banner b-amber" role="group" aria-label="Overwrite warning"><b>this path already has a job: ' + state.overwrite.jobs.map(nm).join(', ') + '</b><br>' + msgHtml(state.overwrite.message) +
        '<div class="bacts"><button type="button" class="btn warn" data-act="overwrite" data-fid="overwrite">[ overwrite and run ]</button>' + (state.scan ? '' : '<button type="button" class="btn pri" data-act="newjob" data-fid="newjob">[ start as new job ]</button>') + '<button type="button" class="btn" data-act="cancel" data-fid="cancel">[ cancel ]</button></div></div>';
    }
    return h + '</div>';
  }

  function layout() {
    var left = '<div class="lh"><span>jobs (' + (state.search.trim() ? visibleRows().length + ' of ' : '') + allRows().length + ')</span>' + (state.panel ? '' : '<button type="button" class="btn pri" data-act="drawer" data-fid="drawer">[ + new job ]</button>') + '</div>';
    if (state.panel) left += panelHtml();
    if (allRows().length) {
      left += '<div class="srch"><label class="sr" for="job-search">Search jobs</label><input class="field" id="job-search" type="text" data-f="search" data-fid="search" dir="auto" autocomplete="off" placeholder="search jobs" value="' + esc(state.search) + '">' +
        (state.search ? '<button type="button" class="btn mini" data-act="searchclear" data-fid="searchclear" aria-label="Clear search">[ × ]</button>' : '') + '</div>';
    }
    if (state.loading) left += '<div class="dim">loading...</div>';
    else if (allRows().length) left += jobSelect() + '<div class="list">' + (visibleRows().length ? visibleRows().map(cardHtml).join('') : '<div class="dim">no jobs match</div>') + '</div>';
    else left += '<div class="empty">no jobs yet</div>';
    return '<div class="main"><aside class="left" data-left>' + left + '</aside><section class="right">' + rightHtml() + '</section></div>';
  }

  /* ---------- render ---------- */
  function fid(a) { return a.dataset.fid || (a.dataset.act ? a.dataset.act + '|' + (a.dataset.arg || '') : null); }
  function render() {
    var a = document.activeElement, k = null, pos = null;
    if (a && el.contains(a)) {
      k = fid(a);
      if (typeof a.selectionStart === 'number' && a.type === 'text') pos = [a.selectionStart, a.selectionEnd];
    }
    if (state.focusNext) { k = state.focusNext; pos = null; state.focusNext = null; }
    var log = el.querySelector('[data-log]'), left = el.querySelector('[data-left]');
    var logTop = log ? log.scrollTop : 0, atBottom = !log || (log.scrollHeight - log.scrollTop - log.clientHeight < 24);
    var leftTop = left ? left.scrollTop : 0;
    el.innerHTML = layout();
    var nlog = el.querySelector('[data-log]'), nleft = el.querySelector('[data-left]');
    if (nlog) nlog.scrollTop = atBottom ? nlog.scrollHeight : logTop;
    if (nleft) nleft.scrollTop = leftTop;
    if (k) {
      var els = el.querySelectorAll('[data-fid],[data-act]');
      for (var i = 0; i < els.length; i++) {
        if (els[i].offsetParent !== null && fid(els[i]) === k) {
          els[i].focus();
          if (pos && els[i].setSelectionRange) { try { els[i].setSelectionRange(pos[0], pos[1]); } catch (e) { } }
          break;
        }
      }
    }
  }

  /* ---------- actions ---------- */
  function openPanel() { state.panel = true; state.focusNext = 'path'; }
  function closePanel() {
    state.panel = false; state.overwrite = null; state.offerNew = false; state.formErr = {}; state.formNote = ''; state.generalErr = '';
    state.focusNext = 'drawer';
  }
  function start(confirm) {
    var f = state.form, p = f.path.trim();
    state.formErr = {}; state.formNote = ''; state.generalErr = ''; state.overwrite = null; state.offerNew = false;
    if (!p) { state.formErr.path = 'path is required: absolute path to a book file or folder'; render(); return; }
    var body = { path: p, fiction: f.fiction, ssml: f.ssml, newJob: f.newJob, confirm: !!confirm };
    if (state.scan) {  /* folder: only the ticked rows, in list order */
      if (startState().disabled) { render(); return; }
      body = { books: state.scan.rows.filter(function (r) { return r.on; }).map(function (r) { return { path: r.path, name: rowName(r), new_job: !!r.newJob }; }), fiction: f.fiction, ssml: f.ssml, confirm: !!confirm };
    } else if (f.name.trim()) body.name = f.name.trim();
    state.starting = true; render();
    api('POST', '/api/runs', body).then(function (r) {
      state.starting = false;
      var d = r.data;
      if (r.status === 202) {
        state.form = { path: '', name: '', fiction: true, ssml: false, newJob: false }; state.offerNew = false; state.scan = null;
        state.skipped = d.skipped || []; state.queuedNames = d.queued || [];
        state.panel = false; state.tab = 1; state.view = null; state.focusNext = 'drawer';
        state.msg = 'started ' + d.queued.join(', ');
        state.busy = true;
        state.selected = null; state.job = null;
        startPolling();
        refreshAll().then(function () { if (state.jobs.some(function (j) { return j.name === d.queued[0]; })) selectJob(d.queued[0]); });
        return;
      }
      if (r.status === 409 && d.overwrite) { state.overwrite = { message: d.message, jobs: d.jobs || [] }; state.offerNew = !state.scan; state.focusNext = state.scan ? 'overwrite' : 'newjob'; }
      else if (r.status === 409 && d.busy) { state.busy = true; state.generalErr = d.error; startPolling(); }
      else if (d.field === 'path' || d.field === 'name') { state.formErr[d.field] = d.error; if (d.field === 'name' && /tick "new job"/.test(d.error)) state.offerNew = true; if (d.skipped) state.skipped = d.skipped; }
      else state.generalErr = d.error || 'request failed';
      render();
    });
  }
  function doRetry() {
    state.retryErr = '';
    api('POST', '/api/jobs/' + enc(state.selected) + '/retry', {}).then(function (r) {
      if (r.status === 202) { state.view = null; state.busy = true; state.dismissedErr = ''; startPolling(); }
      else state.retryErr = r.data.error || 'retry failed';
      render();
    });
  }
  function saveRename() {
    var val = (state.renameVal || '').trim(), old = state.renaming;
    if (!val) { state.renameErr = 'name cannot be empty'; render(); return; }
    api('POST', '/api/jobs/' + enc(old) + '/rename', { name: val }).then(function (r) {
      if (r.ok) {
        state.renaming = null; state.renameErr = ''; state.selected = val; state.msg = 'renamed to "' + val + '" (folder unchanged)';
        try { history.replaceState(null, '', '#job=' + enc(val)); } catch (e) { }
        refreshAll();
      } else { state.renameErr = r.data.error || 'rename failed'; render(); }
    });
  }
  function doOpen(rel) {
    api('POST', '/api/jobs/' + enc(state.selected) + '/open', { path: rel }).then(function (r) {
      state.msg = r.ok ? 'opened ' + rel + ' in the file manager' : (r.data.error || 'could not open folder');
      render();
    });
  }
  function doScan() {
    var p = state.form.path.trim();
    if (!/^(\/|~)/.test(p)) { if (state.scan) { state.scan = null; render(); } return; }
    api('GET', '/api/scan?path=' + enc(p)).then(function (r) {
      if (state.form.path.trim() !== p) return;  /* typed on since: a newer scan is coming */
      var d = r.data;
      if (r.ok && d.kind === 'file' && d.books.length && !d.books[0].job) { state.freeName = d.books[0].free_name; state.freeFor = p; syncStart(); }
      if (!r.ok || !d.books || d.kind !== 'folder') { if (state.scan) { state.scan = null; render(); } return; }
      var old = {};
      if (state.scan) state.scan.rows.forEach(function (x) { old[x.path] = x; });
      state.scan = {
        skipped: d.skipped || [],
        rows: d.books.map(function (b) {
          var o = old[b.path];
          return o || { path: b.path, file: b.file, job: b.job, stem: b.file.replace(/\.[^.]*$/, ''), on: true, nm: b.name, free: b.free_name, newJob: false };
        })
      };
      state.overwrite = null; state.generalErr = '';
      render();
    });
  }
  function doStop() {
    api('POST', '/api/stop', {}).then(function (r) {
      state.msg = r.ok ? 'stop requested' + (r.data.dropped && r.data.dropped.length ? ' — dropped ' + r.data.dropped.length + ' queued' : '') + '; the running book stops after its current step' : (r.data.error || 'stop failed');
      startPolling(); refreshAll();
    });
  }
  function doDelete() {
    var name = state.confirmDel, rows = allRows(), i = rows.map(function (j) { return j.name; }).indexOf(name);
    api('POST', '/api/jobs/' + enc(name) + '/delete', {}).then(function (r) {
      if (!r.ok) { state.delErr = r.data.error || 'delete failed'; state.confirmDel = null; render(); return; }
      var rest = rows.filter(function (j) { return j.name !== name; }), next = rest[i] || rest[i - 1] || null;
      state.confirmDel = null; state.delErr = '';
      state.selected = next ? next.name : null; state.job = null; state.files = null; state.view = null;
      state.msg = 'removed ' + name + ' from history (files on disk stay)';
      try { history.replaceState(null, '', next ? '#job=' + enc(next.name) : '#'); } catch (e) { }
      refreshAll();
    });
  }
  function importExisting() {
    api('POST', '/api/import', {}).then(function (r) {
      state.msg = r.ok ? 'imported ' + r.data.imported.length + ' job(s)' : (r.data.error || 'import failed');
      refreshAll();
    });
  }
  function act(a, arg) {
    switch (a) {
      case 'sel': selectJob(arg); return;
      case 'tab': state.tab = +arg; state.msg = ''; onTab(); break;
      case 'ftoggle': var fk = state.job.name + '|' + arg; state.fexp[fk] = !state.fexp[fk]; break;
      case 'openfolder': doOpen(arg); return;
      case 'toggle': var k = (state.job ? state.job.name : '') + '#' + arg; state.open[k] = !state.open[k]; break;
      case 'viewrun': state.view = +arg; state.tab = 1; break;
      case 'latest': state.view = null; break;
      case 'drawer': if (state.panel) closePanel(); else openPanel(); break;
      case 'rowsall': case 'rowsnone': state.scan.rows.forEach(function (r) { r.on = a === 'rowsall'; }); state.overwrite = null; break;
      case 'start': start(false); return;
      case 'cancel': state.overwrite = null; state.focusNext = 'path'; break;
      case 'overwrite': start(true); return;
      case 'newjob':
        state.overwrite = null; state.form.newJob = true; state.focusNext = 'name';
        state.formNote = 'new job: pick a name different from the existing one, then press start'; break;
      case 'retry': doRetry(); return;
      case 'stop': doStop(); return;
      case 'searchclear': state.search = ''; state.focusNext = 'search'; break;
      case 'delask': state.confirmDel = state.selected; state.delErr = ''; state.focusNext = 'delno'; break;
      case 'delno': state.confirmDel = null; state.focusNext = 'delask'; break;
      case 'delyes': doDelete(); return;
      case 'rename': state.renaming = arg; state.renameVal = arg; state.renameErr = ''; state.focusNext = 'rename'; break;
      case 'rcancel': state.renaming = null; break;
      case 'rsave': saveRename(); return;
      case 'import': importExisting(); return;
      case 'dismissErr': state.dismissedErr = state.runError ? state.runError.job + '|' + state.runError.message : ''; break;
      case 'dismissSkip': state.skipped = []; state.queuedNames = []; break;
      case 'reload': state.jobsErr = ''; refreshAll(); return;
    }
    render();
  }

  el.addEventListener('click', function (e) {
    var b = e.target.closest('[data-act]');
    if (!b || b.disabled || !el.contains(b)) return;
    act(b.dataset.act, b.dataset.arg);
  });
  el.addEventListener('input', function (e) {
    var f = e.target.dataset.f;
    if (f === 'path') {
      state.form.path = e.target.value;
      if (state.overwrite || state.formErr.path || state.generalErr) { state.overwrite = null; state.formErr = {}; state.generalErr = ''; render(); }
      else syncStart();
      clearTimeout(scanTimer); scanTimer = setTimeout(doScan, SCAN_DELAY_MS);
    } else if (f === 'rowname') { state.scan.rows[+e.target.dataset.i].nm = e.target.value; syncStart(); }
    else if (f === 'name') state.form.name = e.target.value;
    else if (f === 'rename') state.renameVal = e.target.value;
    else if (f === 'search') { state.search = e.target.value; render(); }
  });
  el.addEventListener('change', function (e) {
    var f = e.target.dataset.f;
    if (f === 'mode') state.form.fiction = e.target.value === 'fic';
    else if (f === 'ssml') state.form.ssml = e.target.checked;
    else if (f === 'newJob') { state.form.newJob = e.target.checked; render(); }
    else if (f === 'rowon') { state.scan.rows[+e.target.dataset.i].on = e.target.checked; state.overwrite = null; render(); }
    else if (f === 'rownew') {
      var r = state.scan.rows[+e.target.dataset.i];
      r.newJob = e.target.checked; r.nm = r.newJob ? r.free : r.job; state.overwrite = null; render();
    }
    else if (f === 'sel') selectJob(e.target.value);
  });
  el.addEventListener('keydown', function (e) {
    var f = e.target.dataset && e.target.dataset.f;
    if ((f === 'path' || f === 'name') && e.key === 'Enter') {
      e.preventDefault();
      if (state.form.path.trim() && !startState().disabled) start(false);
    } else if (f === 'rename' && e.key === 'Enter') { e.preventDefault(); saveRename(); }
    else if (f === 'rename' && e.key === 'Escape') { state.renaming = null; render(); }
    else if (e.target.getAttribute && e.target.getAttribute('role') === 'tab' && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')) {
      e.preventDefault();
      state.tab = ((state.tab - 1 + (e.key === 'ArrowRight' ? 1 : TABS.length - 1)) % TABS.length) + 1;
      state.focusNext = 'tab|' + state.tab; onTab(); render();
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && state.panel && !state.renaming) { closePanel(); render(); return; }
    var t = e.target, tag = t && t.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || e.ctrlKey || e.metaKey || e.altKey) return;
    if ((e.key === '1' || e.key === '2' || e.key === '3') && state.job) { state.tab = +e.key; state.msg = ''; onTab(); render(); }
  });

  /* theme: light <-> dark; default follows prefers-color-scheme */
  var root = document.documentElement, tb = document.getElementById('themeBtn');
  function eff() { var t = root.getAttribute('data-theme'); return t || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'); }
  function themeLabel() { var t = eff(); tb.textContent = t === 'dark' ? '[ ☾ ]' : '[ ☀ ]'; tb.setAttribute('aria-label', 'Theme: ' + t + '. Switch to ' + (t === 'dark' ? 'light' : 'dark')); tb.title = 'theme: ' + t; }
  try { var saved = localStorage.getItem('sawt-theme'); if (saved === 'light' || saved === 'dark') root.setAttribute('data-theme', saved); } catch (e) { }
  tb.addEventListener('click', function () {
    var n = eff() === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', n);
    try { localStorage.setItem('sawt-theme', n); } catch (e) { }
    themeLabel();
  });
  themeLabel();

  render();
  refreshAll().then(function () { if (state.busy) startPolling(); });
})();
</script>
</body>
</html>
"""
PAGE = PAGE.replace("__FONT_FACE__", FONT_FACE)
