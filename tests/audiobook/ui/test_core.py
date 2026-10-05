"""Tests for module 2: local UI shell (real server on port 0, SAWT_HOME in tmp)."""
import http.client
import json
import re
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path
from urllib.parse import quote

import pytest

import src.audiobook.runner.core as runner_core
import src.audiobook.ui.core as ui_core
from src.audiobook.runner import OVERWRITE_WARNING, import_existing, load_jobs, save_jobs
from src.audiobook.ui import _Worker, make_server
from src.audiobook.ui.page import PAGE

NARRATION = "كان الرجل يمشي في الطريق الطويل وحده بينما الشمس تغرب خلف البيوت القديمة"
DIALOGUE = "قال أحمد: كيف حالك اليوم يا صديقي وهل وصلت إلى البيت قبل المساء"


def make_book(folder: Path, stem: str = "novel", n: int = 40) -> Path:
    paras = [(DIALOGUE if i % 2 else NARRATION) + f" {i}" for i in range(n)]
    path = folder / f"{stem}.txt"
    path.write_text("\n\n".join(paras), encoding="utf-8")
    return path


class Client:
    def __init__(self, server):
        self.server = server
        self.port = server.server_port

    def call(self, method, path, body=None, host=None, ctype="application/json", raw=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        headers = {"Host": host or f"127.0.0.1:{self.port}"}
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        if method == "POST" and ctype:
            headers["Content-Type"] = ctype
        conn.request(method, path, body=data, headers=headers)
        r = conn.getresponse()
        payload = r.read()
        conn.close()
        try:
            return r.status, json.loads(payload)
        except ValueError:
            return r.status, payload.decode("utf-8")

    def get(self, path, **kw):
        return self.call("GET", path, **kw)

    def post(self, path, body=None, **kw):
        return self.call("POST", path, {} if body is None else body, **kw)

    def wait_idle(self, timeout=30):
        end = time.time() + timeout
        while time.time() < end:
            if not self.server.worker.status()["busy"]:
                return
            time.sleep(0.02)
        raise AssertionError("worker still busy")

    def job(self, name):
        status, data = self.get("/api/jobs/" + quote(name))
        assert status == 200, data
        return data


def start_server():
    server = make_server(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


@pytest.fixture
def home(tmp_path, monkeypatch):
    h = tmp_path / "sawt_home"
    monkeypatch.setenv("SAWT_HOME", str(h))
    return h


@pytest.fixture
def books(tmp_path):
    d = tmp_path / "books"
    d.mkdir()
    return d


@pytest.fixture
def client(home):
    server = start_server()
    yield Client(server)
    server.shutdown()
    server.server_close()


class TestServer:
    def test_binds_loopback_only(self, client):
        assert client.server.server_address[0] == "127.0.0.1"

    def test_page_served_with_csp(self, client):
        conn = http.client.HTTPConnection("127.0.0.1", client.port)
        conn.request("GET", "/", headers={"Host": f"127.0.0.1:{client.port}"})
        r = conn.getresponse()
        body = r.read().decode()
        assert r.status == 200
        assert "Content-Security-Policy" in dict(r.getheaders())
        assert "<title>sawt - every book has a voice</title>" in body
        assert "<b>[sawt]</b>" in body and "- every book has a voice</span>" in body

    def test_foreign_host_rejected(self, client):
        for path in ("/", "/api/jobs", "/api/status"):
            status, _ = client.get(path, host="evil.example.com")
            assert status == 403
        status, _ = client.post("/api/runs", {"path": "/x"}, host=f"evil.example.com:{client.port}")
        assert status == 403

    def test_localhost_host_accepted(self, client):
        status, _ = client.get("/api/jobs", host=f"localhost:{client.port}")
        assert status == 200

    def test_post_requires_json_content_type(self, client):
        status, data = client.call("POST", "/api/runs", raw=b'{"path": "/x"}', ctype="text/plain")
        assert status == 415
        status, _ = client.call("POST", "/api/runs", raw=b'{"path": "/x"}', ctype=None)
        assert status == 415

    def test_bad_json_and_oversize_body(self, client):
        status, _ = client.call("POST", "/api/runs", raw=b"{nope")
        assert status == 400
        status, _ = client.call("POST", "/api/runs", raw=b"x" * (ui_core.MAX_BODY_BYTES + 1))
        assert status == 413

    def test_unknown_routes_404(self, client):
        assert client.get("/nope")[0] == 404
        assert client.get("/files/a/b/c")[0] == 404
        assert client.get("/api/jobs/x/artifacts")[0] == 404


class TestReadEndpoints:
    def test_empty(self, client):
        assert client.get("/api/jobs") == (200, {"jobs": []})
        status, data = client.get("/api/status")
        assert status == 200 and data["busy"] is False

    def test_populated_newest_first_and_detail(self, client, books):
        a, b = make_book(books, "alpha"), make_book(books, "beta")
        for book in (a, b):
            assert client.post("/api/runs", {"path": str(book)})[0] == 202
            client.wait_idle()
        data = load_jobs()  # run dates have 1s granularity: make the order unambiguous
        data["jobs"][0]["runs"][0]["date"] = "2026-01-01T00:00:00"
        data["jobs"][1]["runs"][0]["date"] = "2026-02-01T00:00:00"
        save_jobs(data)
        rows = client.get("/api/jobs")[1]["jobs"]
        assert [r["name"] for r in rows] == ["beta", "alpha"]
        assert rows[0]["status"].startswith("ready for audio")
        job = client.job("alpha")
        assert job["missing"] is False and len(job["runs"]) == 1
        assert client.get("/api/jobs/nope")[0] == 404

    def test_corrupt_jobs_file_gives_clear_error(self, client, home):
        home.mkdir(parents=True)
        (home / "jobs.json").write_text("{not json", encoding="utf-8")
        status, data = client.get("/api/jobs")
        assert status == 500 and "unreadable" in data["error"]

    def test_arabic_job_name_roundtrip(self, client, books):
        book = make_book(books, "رواية")
        assert client.post("/api/runs", {"path": str(book)})[1]["queued"] == ["رواية"]
        client.wait_idle()
        assert client.job("رواية")["name"] == "رواية"


class TestStartRuns:
    def test_file_run_reaches_gate(self, client, books):
        book = make_book(books)
        status, data = client.post("/api/runs", {"path": str(book)})
        assert status == 202 and data == {"queued": ["novel"], "skipped": []}
        client.wait_idle()
        run = client.job("novel")["runs"][-1]
        assert run["status"] == runner_core.RUN_READY
        assert run["log"][-1] == runner_core.GATE_LINE
        assert run["settings"] == {"ssml": False, "fiction": True}
        assert (books / "novel_sawt" / "01_ingestion").is_dir()
        assert not (books / "novel_sawt" / "04_ssml").exists()

    def test_settings_passed_through(self, client, books):
        book = make_book(books)
        client.post("/api/runs", {"path": str(book), "fiction": False, "ssml": True})
        client.wait_idle()
        run = client.job("novel")["runs"][-1]
        assert run["settings"] == {"ssml": True, "fiction": False}
        assert run["steps"]["dialogue"] == "skipped"

    def test_folder_queues_and_lists_skipped(self, client, books):
        make_book(books, "one")
        make_book(books, "two")
        (books / "old.doc").write_bytes(b"x")
        (books / "scan.pdf").write_bytes(b"x")
        status, data = client.post("/api/runs", {"path": str(books)})
        assert status == 202
        assert data["queued"] == ["one", "two"]
        skipped = {s["file"]: s["reason"] for s in data["skipped"]}
        assert set(skipped) == {"old.doc", "scan.pdf"}
        assert "save it as .docx" in skipped["old.doc"]
        client.wait_idle()
        assert {r["name"] for r in client.get("/api/jobs")[1]["jobs"]} == {"one", "two"}
        assert all(r["status"].startswith("ready") for r in client.get("/api/jobs")[1]["jobs"])

    def test_folder_same_stem_gets_free_default_name(self, client, books):
        make_book(books, "same")
        (books / "same.docx").write_bytes(b"x")  # will fail ingest, but shares the stem
        status, data = client.post("/api/runs", {"path": str(books)})
        assert status == 202 and data["queued"] == ["same", "same-2"]  # default names stay unique
        client.wait_idle()

    def test_folder_book_with_taken_default_name_gets_free_name(self, client, books):
        other = books / "elsewhere"
        other.mkdir()
        client.post("/api/runs", {"path": str(make_book(other, "dup"))})
        client.wait_idle()
        folder = books / "folder"
        folder.mkdir()
        make_book(folder, "dup")
        make_book(folder, "fresh")
        status, data = client.post("/api/runs", {"path": str(folder)})
        assert status == 202 and data["queued"] == ["dup-2", "fresh"] and data["skipped"] == []
        client.wait_idle()

    def test_explicit_taken_name_is_still_an_error(self, client, books):
        other = books / "elsewhere"
        other.mkdir()
        client.post("/api/runs", {"path": str(make_book(other, "dup"))})
        client.wait_idle()
        status, data = client.post("/api/runs", {"path": str(make_book(books, "x")), "name": "dup"})
        assert status == 400 and data["field"] == "name" and "already taken" in data["error"]

    @pytest.mark.parametrize("body,field", [
        ({"path": ""}, "path"),
        ({}, "path"),
        ({"path": "relative/book.txt"}, "path"),
        ({"path": "/definitely/not/here.txt"}, "path"),
    ])
    def test_path_validation(self, client, body, field):
        status, data = client.post("/api/runs", body)
        assert status == 400 and data["field"] == field and data["error"]

    def test_single_doc_rejected_with_reason(self, client, books):
        doc = books / "old.doc"
        doc.write_bytes(b"x")
        status, data = client.post("/api/runs", {"path": str(doc)})
        assert status == 400 and "save it as .docx" in data["error"]

    def test_pdf_rejected(self, client, books):
        pdf = books / "scan.pdf"
        pdf.write_bytes(b"x")
        status, data = client.post("/api/runs", {"path": str(pdf)})
        assert status == 400 and "unsupported format" in data["error"]

    def test_folder_with_nothing_runnable(self, client, books):
        (books / "old.doc").write_bytes(b"x")
        status, data = client.post("/api/runs", {"path": str(books)})
        assert status == 400 and data["skipped"][0]["file"] == "old.doc"

    def test_name_with_folder_rejected(self, client, books):
        make_book(books, "a")
        status, data = client.post("/api/runs", {"path": str(books), "name": "x"})
        assert status == 400 and data["field"] == "name"

    def test_duplicate_name_rejected_synchronously(self, client, books):
        make_book(books, "a")
        other = make_book(books, "b")
        client.post("/api/runs", {"path": str(books / "a.txt")})
        client.wait_idle()
        status, data = client.post("/api/runs", {"path": str(other), "name": "a"})
        assert status == 400 and data["field"] == "name" and "already taken" in data["error"]
        assert client.get("/api/status")[1]["busy"] is False

    def test_overwrite_needs_confirmation(self, client, books):
        book = make_book(books)
        client.post("/api/runs", {"path": str(book)})
        client.wait_idle()
        marker = books / "novel_sawt" / "01_ingestion" / "marker.txt"
        marker.write_text("old", encoding="utf-8")
        status, data = client.post("/api/runs", {"path": str(book)})
        assert status == 409
        assert data == {"overwrite": True, "message": OVERWRITE_WARNING, "jobs": ["novel"]}
        assert marker.exists() and len(client.job("novel")["runs"]) == 1  # nothing ran
        status, _ = client.post("/api/runs", {"path": str(book), "confirm": True})
        assert status == 202
        client.wait_idle()
        assert len(client.job("novel")["runs"]) == 2 and not marker.exists()

    def test_new_job_for_same_book_skips_overwrite_warning(self, client, books):
        book = make_book(books)
        client.post("/api/runs", {"path": str(book)})
        client.wait_idle()
        status, data = client.post("/api/runs", {"path": str(book), "newJob": True, "name": "novel-2"})
        assert status == 202 and data["queued"] == ["novel-2"]
        client.wait_idle()
        assert (books / "novel-2_sawt").is_dir() and (books / "novel_sawt").is_dir()
        # without a distinct name the duplicate is rejected inline
        status, data = client.post("/api/runs", {"path": str(book), "newJob": True})
        assert status == 400 and data["field"] == "name"

    def test_busy_rejects_second_run_and_rename(self, client, books, monkeypatch):
        book, other = make_book(books, "a"), make_book(books, "b")
        gate, entered = threading.Event(), threading.Event()
        real = runner_core._STEP_FUNCS["ingest"]

        def slow(job, run):
            entered.set()
            gate.wait(10)
            return real(job, run)

        monkeypatch.setitem(runner_core._STEP_FUNCS, "ingest", slow)
        assert client.post("/api/runs", {"path": str(book)})[0] == 202
        assert entered.wait(10)
        status, data = client.post("/api/runs", {"path": str(other)})
        assert status == 409 and data["busy"] is True
        assert client.get("/api/status")[1]["current"] == "a"
        assert client.post("/api/jobs/a/rename", {"name": "z"})[0] == 409
        assert client.post("/api/import")[0] == 409
        gate.set()
        client.wait_idle()
        assert client.post("/api/runs", {"path": str(other)})[0] == 202
        client.wait_idle()

    def test_folder_runs_one_at_a_time_in_order(self, client, books, monkeypatch):
        make_book(books, "one")
        make_book(books, "two")
        order, active, peak = [], [0], [0]
        real = runner_core._STEP_FUNCS["ingest"]

        def watch(job, run):
            active[0] += 1
            peak[0] = max(peak[0], active[0])
            order.append(job["name"])
            time.sleep(0.05)
            try:
                return real(job, run)
            finally:
                active[0] -= 1

        monkeypatch.setitem(runner_core._STEP_FUNCS, "ingest", watch)
        client.post("/api/runs", {"path": str(books)})
        assert client.get("/api/status")[1]["busy"] is True
        client.wait_idle()
        assert order == ["one", "two"] and peak[0] == 1


class TestFailureAndRetry:
    def test_failure_logged_then_retry_resumes_untouched_earlier_steps(self, client, books, monkeypatch):
        book = make_book(books)

        def boom(job, run):
            raise RuntimeError("detector exploded")

        real = runner_core._STEP_FUNCS["dialogue"]
        monkeypatch.setitem(runner_core._STEP_FUNCS, "dialogue", boom)
        client.post("/api/runs", {"path": str(book)})
        client.wait_idle()
        job = client.job("novel")
        run = job["runs"][-1]
        assert run["status"] == "failed" and run["steps"]["dialogue"] == "failed"
        assert any(line.startswith("✗") and "detector exploded" in line for line in run["log"])
        first = {p.name: p.stat().st_mtime_ns for p in (books / "novel_sawt" / "02_chapters").iterdir()}

        monkeypatch.setitem(runner_core._STEP_FUNCS, "dialogue", real)
        status, data = client.post("/api/jobs/novel/retry")
        assert status == 202 and data == {"queued": ["novel"]}
        client.wait_idle()
        run = client.job("novel")["runs"][-1]
        assert run["status"] == runner_core.RUN_READY and len(client.job("novel")["runs"]) == 1
        assert {p.name: p.stat().st_mtime_ns for p in (books / "novel_sawt" / "02_chapters").iterdir()} == first

    def test_retry_with_nothing_to_retry(self, client, books):
        book = make_book(books)
        client.post("/api/runs", {"path": str(book)})
        client.wait_idle()
        status, data = client.post("/api/jobs/novel/retry")
        assert status == 400 and "nothing to retry" in data["error"]
        assert client.post("/api/jobs/ghost/retry")[0] == 404

    def test_retry_error_reported_via_status(self, client, books, monkeypatch):
        book = make_book(books)
        monkeypatch.setitem(runner_core._STEP_FUNCS, "ingest", lambda j, r: (_ for _ in ()).throw(OSError("disk")))
        client.post("/api/runs", {"path": str(book)})
        client.wait_idle()
        book.unlink()  # source gone: retry from ingest must be refused
        assert client.post("/api/jobs/novel/retry")[0] == 202
        client.wait_idle()
        err = client.get("/api/status")[1]["error"]
        assert err["job"] == "novel" and "source file is gone" in err["message"]

    def test_worker_survives_a_crashing_task(self, home):
        w = _Worker()
        done = threading.Event()
        assert w.submit([("a", lambda: 1 / 0)])
        while w.status()["busy"]:
            time.sleep(0.01)
        assert "ZeroDivisionError" in w.status()["error"]["message"]
        assert w.submit([("b", done.set)])
        assert done.wait(5)


class TestRename:
    def test_label_only(self, client, books):
        book = make_book(books)
        client.post("/api/runs", {"path": str(book)})
        client.wait_idle()
        status, data = client.post("/api/jobs/novel/rename", {"name": "الرواية"})
        assert status == 200 and data == {"name": "الرواية"}
        job = client.job("الرواية")
        assert job["output"].endswith("novel_sawt") and Path(job["output"]).is_dir()
        assert client.get("/api/jobs/novel")[0] == 404

    def test_rejections(self, client, books):
        for stem in ("a", "b"):
            client.post("/api/runs", {"path": str(make_book(books, stem))})
            client.wait_idle()
        status, data = client.post("/api/jobs/a/rename", {"name": "b"})
        assert status == 400 and data["field"] == "name" and "already taken" in data["error"]
        assert client.post("/api/jobs/a/rename", {"name": "bad/name"})[0] == 400
        assert client.post("/api/jobs/a/rename", {})[0] == 400
        assert client.post("/api/jobs/ghost/rename", {"name": "x"})[0] == 404


class TestImport:
    def test_import_endpoint(self, client, tmp_path, monkeypatch):
        out = tmp_path / "output" / "txt" / "oldbook"
        (out / "01_ingestion").mkdir(parents=True)
        monkeypatch.setattr(ui_core, "import_existing",
                            lambda: import_existing(tmp_path / "output", tmp_path / "data"))
        status, data = client.post("/api/import")
        assert status == 200 and data["imported"] == ["oldbook"]
        row = client.get("/api/jobs")[1]["jobs"][0]
        assert row["name"] == "oldbook" and row["status"] == "imported"
        again = client.post("/api/import")[1]
        assert again["imported"] == [] and again["skipped"][0]["job"] == "oldbook"


class TestPersistence:
    def test_restart_sees_jobs_and_runs(self, home, books):
        book = make_book(books)
        s1 = start_server()
        c1 = Client(s1)
        c1.post("/api/runs", {"path": str(book)})
        c1.wait_idle()
        c1.post("/api/jobs/novel/rename", {"name": "kept"})
        s1.shutdown()
        s1.server_close()

        s2 = start_server()
        try:
            c2 = Client(s2)
            rows = c2.get("/api/jobs")[1]["jobs"]
            assert [r["name"] for r in rows] == ["kept"] and rows[0]["runs"] == 1
            assert c2.job("kept")["runs"][0]["log"][-1] == runner_core.GATE_LINE
        finally:
            s2.shutdown()
            s2.server_close()

    def test_missing_output_folder_shows_missing(self, client, books):
        book = make_book(books)
        client.post("/api/runs", {"path": str(book)})
        client.wait_idle()
        shutil.rmtree(books / "novel_sawt")
        assert client.get("/api/jobs")[1]["jobs"][0]["status"] == "missing"
        assert client.job("novel")["missing"] is True


class TestStaticFonts:
    def test_page_has_no_external_hosts_and_csp_is_self_only(self, client):
        assert "googleapis" not in PAGE and "gstatic" not in PAGE and "<link" not in PAGE
        assert "@font-face" in PAGE and "/static/CourierPrime-Regular.woff2" in PAGE
        assert "font-src 'self'" in ui_core.PAGE_CSP and "google" not in ui_core.PAGE_CSP
        conn = http.client.HTTPConnection("127.0.0.1", client.port)
        conn.request("GET", "/", headers={"Host": f"127.0.0.1:{client.port}"})
        csp = conn.getresponse().getheader("Content-Security-Policy")
        assert csp == ui_core.PAGE_CSP

    @pytest.mark.parametrize("name", ["CourierPrime-Regular.woff2", "CourierPrime-Bold.woff2"])
    def test_font_served_with_type_and_cache(self, client, name):
        status, headers, body = raw_get(client, "/static/" + name)
        assert status == 200 and headers["content-type"] == "font/woff2"
        assert body[:4] == b"wOF2" and "max-age=31536000" in headers["cache-control"]
        assert headers["cache-control"].count("no-store") == 0 and headers["x-content-type-options"] == "nosniff"

    @pytest.mark.parametrize("name", ["OFL.txt", "../core.py", "..%2Fcore.py", "%2e%2e/core.py", "nope.woff2",
                                      "CourierPrime-Regular.woff2/", "", "CourierPrime-Regular.woff2%00"])
    def test_only_allow_listed_names(self, client, name):
        assert raw_get(client, "/static/" + name)[0] == 404

    def test_foreign_host_rejected(self, client):
        conn = http.client.HTTPConnection("127.0.0.1", client.port)
        conn.request("GET", "/static/CourierPrime-Regular.woff2", headers={"Host": "evil.example.com"})
        assert conn.getresponse().status == 403

    def test_files_and_license_ship_in_repo(self):
        for n in (*ui_core.STATIC_FILES, "OFL.txt"):
            assert (ui_core.STATIC_DIR / n).is_file()
        assert "SIL Open Font License" in (ui_core.STATIC_DIR / "OFL.txt").read_text(encoding="utf-8")

    def test_viewer_uses_bundled_font_too(self, client, job):
        _, headers, body = view(client, "01_ingestion/clean_text.txt")
        assert "font-src 'self'" in headers["content-security-policy"] and b"/static/CourierPrime-Bold.woff2" in body

    def test_job_pane_is_360px_with_narrow_fallback(self):
        assert "grid-template-columns:360px minmax(0,1fr)" in PAGE
        narrow = PAGE.split("@media (max-width:720px)")[1]
        assert "grid-template-columns:minmax(0,1fr)" in narrow


class TestPage:
    def test_theme_and_scroll_contract(self):
        assert "prefers-color-scheme: dark" in PAGE
        assert ':root:not([data-theme="light"])' in PAGE
        assert "localStorage" in PAGE and PAGE.count("try {") >= 2
        assert "unicode-bidi:plaintext" in PAGE
        assert 'role="log"' in PAGE and 'aria-live="polite"' in PAGE
        assert "overflow-y:auto" in PAGE and "overflow:hidden" in PAGE

    def test_no_lab_only_content(self):
        for lab in ("labnote", "fixtures.js", "LiveCanvas", "overlay-vanilla", "data-lab"):
            assert lab not in PAGE

    def test_file_grid_is_auto_fill_capped_at_four_columns(self):
        rule = re.search(r"\.v \.fgrid\{[^}]*\}", PAGE).group(0)
        assert "repeat(auto-fill,minmax(max(200px,calc((100% - 36px)/4)),1fr))" in rule

    def test_artifacts_tab_is_wired(self):
        assert "module 3, not built" not in PAGE
        assert "/files'" in PAGE and "/open'" in PAGE and "/view?job=" in PAGE
        assert 'target="_blank" rel="noopener"' in PAGE
        assert "[ open folder ]" in PAGE and "not produced" in PAGE and "folder missing" in PAGE

    @pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
    def test_page_js_parses(self, tmp_path):
        js = re.search(r"<script>(.*)</script>", PAGE, re.S).group(1)
        f = tmp_path / "page.js"
        f.write_text(js, encoding="utf-8")
        r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr


# Fake-DOM harness: runs the real page JS under node, drives the new-job panel.
_HARNESS = r"""
var listeners = {}, busy = process.argv[2] === 'busy';
function node(extra) { return Object.assign({ disabled: false, attrs: {}, textContent: '', placeholder: '',
  setAttribute: function (k, v) { this.attrs[k] = v; }, removeAttribute: function (k) { delete this.attrs[k]; } }, extra); }
var btn = node(), why = node(), nm = node();
var app = { innerHTML: '', addEventListener: function (t, f) { listeners[t] = f; }, contains: function () { return true; },
  querySelector: function (s) { return s === '[data-start]' ? btn : s === '[data-start-why]' ? why : s === '#f-name' ? nm : null; },
  querySelectorAll: function () { return []; } };
var tbtn = node({ addEventListener: function () {} });
global.document = { activeElement: null, documentElement: node({ getAttribute: function () { return 'light'; } }),
  getElementById: function (i) { return i === 'app' ? app : tbtn; }, addEventListener: function () {} };
global.window = { addEventListener: function () {} }; global.location = { hash: '' };
global.matchMedia = function () { return { matches: false }; }; global.localStorage = { getItem: function () { return null; } };
global.history = { replaceState: function () {} };
global.fetch = function (u) { var d = u === '/api/status' ? { busy: busy, current: null, queued: [] } : u === '/api/jobs' ? { jobs: [] } : {};
  return Promise.resolve({ ok: true, status: 200, json: function () { return Promise.resolve(d); } }); };
//DRIVER
var conflict = process.argv[2] === 'conflict', overwrite = process.argv[2] === 'overwrite';
var started = process.argv[2] === 'start', arts = process.argv[2] === 'arts';
var scanning = process.argv[2] === 'scan', queueMode = process.argv[2] === 'queue', actsMode = process.argv[2] === 'acts', cardsMode = process.argv[2] === 'cards';
function jr(name, status, steps, extra) {
  return Object.assign({ name: name, status: status, date: '2026-01-02T03:04:05', runs: 2, source: '/s/' + name + '.txt', output: '/o/' + name, steps: steps, missing: false }, extra || {});
}
var ALLOK = { ingest: 'ok', chapters: 'ok', dialogue: 'ok', ssml: 'skipped' };
var CARDS = [jr('a', 'ready for audio \u2014 paused', ALLOK), jr('b', 'ready for audio \u2014 paused', Object.assign({ audio: 'ok' }, ALLOK)),
  jr('c', 'failed', { ingest: 'ok', chapters: 'failed', dialogue: 'pending', ssml: 'pending' }),
  jr('d', 'running', { ingest: 'ok', chapters: 'ok', dialogue: 'running', ssml: 'pending' }),
  jr('e', 'stopped', { ingest: 'ok', chapters: 'ok', dialogue: 'pending', ssml: 'pending' }),
  jr('f', 'running', { ingest: 'running', chapters: 'pending', dialogue: 'pending', ssml: 'pending' }),
  jr('g', 'imported', ALLOK), jr('h', 'missing', ALLOK, { missing: true }), jr('i', 'ready for audio \u2014 paused', ALLOK),
  jr('\u0631\u0648\u0627\u064a\u0629', 'ready for audio \u2014 paused', ALLOK, { source: '/s/\u0643\u062a\u0627\u0628.epub' }), jr('mybook-job', 'failed', ALLOK, { source: '/s/MyBook.EPUB' })];
if (queueMode || actsMode || cardsMode) global.fetch = function (u, o) {
  global.calls.push([(o && o.method) || 'GET', u, o && o.body]);
  var run = { date: '2026-01-01T00:00:00', status: actsMode ? 'stopped' : 'running', settings: { ssml: false, fiction: true },
    steps: { ingest: 'ok', chapters: 'pending', dialogue: 'pending', ssml: 'pending' }, log: ['\u2713 ingesting', '\u25a0 stopped by user after ingesting'], errors: [] };
  var d = u === '/api/status' && cardsMode ? { busy: true, current: 'd', queued: ['i'], stopping: false }
    : u === '/api/status' ? (queueMode ? { busy: true, current: 'a', queued: ['b', 'c'], stopping: false } : { busy: false, current: null, queued: [] })
    : u === '/api/jobs' && cardsMode ? { jobs: CARDS }
    : u === '/api/jobs' ? { jobs: [{ name: actsMode ? 'x' : 'a', status: actsMode ? 'stopped' : 'running', date: '2026-01-01T00:00:00', runs: 1 }] }
    : u === '/api/stop' ? { dropped: ['b', 'c'] }
    : { name: actsMode ? 'x' : 'a', output: '/out/x_sawt', source: '/s/x.txt', runs: [run], missing: false };
  return Promise.resolve({ ok: true, status: 200, json: function () { return Promise.resolve(d); } }); };
global.calls = [];
if (scanning) global.fetch = function (u, o) {
  global.calls.push([(o && o.method) || 'GET', u, o && o.body]);
  var d = u === '/api/status' ? { busy: false, current: null, queued: [] }
    : u === '/api/jobs' ? { jobs: [{ name: 'taken', status: 'imported', date: '', runs: 0 }] }
    : u.indexOf('/api/scan') === 0 ? { kind: 'folder', books: [
        { path: '/b/one.epub', file: 'one.epub', name: 'one', free_name: 'one', job: null },
        { path: '/b/two.txt', file: 'two.txt', name: 'two', free_name: 'two', job: null },
        { path: '/b/old.txt', file: 'old.txt', name: 'taken', free_name: 'taken-2', job: 'taken' }],
      skipped: [{ file: 'scan.pdf', reason: 'unsupported format' }] }
    : u === '/api/runs' ? { queued: ['one'], skipped: [] }
    : { name: 'taken', output: '/x', source: '', runs: [], missing: false };
  return Promise.resolve({ ok: true, status: u === '/api/runs' ? 202 : 200, json: function () { return Promise.resolve(d); } }); };
if (arts) global.fetch = function (u, o) {
  global.calls.push([(o && o.method) || 'GET', u, o && o.body]);
  var files = { missing: false, output: '/x/out', steps: [
    { name: '01_ingestion', present: true, count: 3, mtime: 1760000000, groups: [{ dir: '', files: [
      { name: 'clean_text.txt', rel: 'clean_text.txt', path: '01_ingestion/clean_text.txt', size: 2048 },
      { name: 'p<b>.csv', rel: 'p<b>.csv', path: '01_ingestion/p<b>.csv', size: 12 }] },
      { dir: 'ssml', files: [{ name: 'c1.csv', rel: 'ssml/c1.csv', path: '01_ingestion/ssml/c1.csv', size: 5 }] }] },
    { name: '02_chapters', present: true, count: 11, mtime: null, groups: [{ dir: '', files: [] }] },
    { name: '03_segments', present: false }] };
  var d = u === '/api/status' ? { busy: false, current: null, queued: [] }
    : u === '/api/jobs' ? { jobs: [{ name: '\u0631\u0648\u0627\u064a\u0629', status: 'imported', date: '', runs: 0 }] }
    : u.slice(-6) === '/files' ? files : u.slice(-5) === '/open' ? { opened: '02_chapters' }
    : { name: '\u0631\u0648\u0627\u064a\u0629', output: '/x/out', source: '', runs: [], missing: false };
  return Promise.resolve({ ok: true, status: 200, json: function () { return Promise.resolve(d); } }); };
if (started) global.fetch = function (u, o) {
  var d = u === '/api/status' ? { busy: false, current: null, queued: [] } : u === '/api/jobs' ? { jobs: [] }
    : u === '/api/runs' ? { queued: ['one'], skipped: [] } : {};
  return Promise.resolve({ ok: true, status: u === '/api/runs' ? 202 : 200, json: function () { return Promise.resolve(d); } }); };
if (conflict || overwrite) global.fetch = function (u, o) {
  var d = u === '/api/status' ? { busy: false, current: null, queued: [] } : u === '/api/jobs' ? { jobs: [] }
    : conflict ? { error: "this book already has job '\u0635\u062f\u0649-\u0627\u0644\u0646\u0633\u064a\u0627\u0646'; re-run it under that job name (\u0635\u062f\u0649-\u0627\u0644\u0646\u0633\u064a\u0627\u0646) or tick \"new job\"", field: 'name' }
    : { overwrite: true, message: 'x', jobs: ['old'] };
  return Promise.resolve({ ok: u.indexOf('/api/runs') !== 0, status: u === '/api/runs' ? (conflict ? 400 : 409) : 200, json: function () { return Promise.resolve(d); } }); };
function fire(t, target) { listeners[t]({ target: target }); }
function type(v) { fire('input', { value: v, dataset: { f: 'path' } }); }
fire('click', { closest: function () { return { dataset: { act: 'drawer' }, disabled: false }; } });
setTimeout(function () {
  var out = { html: app.innerHTML };
  type(''); out.empty = [btn.disabled, why.textContent];
  type('/books/my-novel.epub'); out.typed = [btn.disabled, btn.attrs['aria-disabled'], why.textContent, nm.placeholder];
  type('   '); out.blank = [btn.disabled, why.textContent];
  if (conflict || overwrite) {
    type('/books/one.txt');
    fire('click', { closest: function () { return { dataset: { act: 'start' }, disabled: false }; } });
    setTimeout(function () {
      out.afterStart = app.innerHTML;
      if (overwrite) fire('click', { closest: function () { return { dataset: { act: 'newjob' }, disabled: false }; } });
      out.afterAct = app.innerHTML;
      console.log(JSON.stringify(out)); process.exit(0); }, 100);
    return;
  }
  if (cardsMode) {
    var cl = function (act) { fire('click', { closest: function () { return { dataset: { act: act }, disabled: false }; } }); };
    var srch = function (v) { fire('input', { value: v, dataset: { f: 'search' } }); };
    cl('reload');
    setTimeout(function () {
      out.cards = app.innerHTML;
      var snap = function (v) { srch(v); return app.innerHTML; };
      out.latin = snap('MYBOOK-JOB'); out.src = snap('myBOOK.epub'); out.ar = snap('\u0631\u0648\u0627\u064a\u0629'); out.arsrc = snap('\u0643\u062a\u0627\u0628'); out.none = snap('zzz');
      cl('searchclear'); out.cleared = app.innerHTML;
      console.log(JSON.stringify(out)); process.exit(0);
    }, 100);
    return;
  }
  if (queueMode || actsMode) {
    var clk = function (act, arg) { fire('click', { closest: function () { return { dataset: { act: act, arg: arg }, disabled: false }; } }); };
    clk('reload');  /* the page's first refresh ran before this mock was installed */
    setTimeout(function () {
    out.first = app.innerHTML;
    if (queueMode) {
      clk('sel', 'b'); out.placeholder = app.innerHTML;
      clk('sel', 'a');
      setTimeout(function () { out.running = app.innerHTML; clk('stop'); }, 60);
    } else {
      clk('delask'); out.ask = app.innerHTML;
      clk('delno'); out.cancelled = app.innerHTML;
      clk('delask'); clk('delyes');
    }
    setTimeout(function () { out.calls = global.calls; console.log(JSON.stringify(out)); process.exit(0); }, 250);
    }, 100);
    return;
  }
  if (scanning) {
    type('/b');
    setTimeout(function () {
      var click = function (act) { fire('click', { closest: function () { return { dataset: { act: act }, disabled: false }; } }); };
      var change = function (f, i, checked) { fire('change', { dataset: { f: f, i: String(i) }, checked: checked }); };
      out.scan = app.innerHTML;
      change('rowon', 0, false); out.untick = app.innerHTML;
      click('rowsnone'); out.none = app.innerHTML;
      click('rowsall'); out.all = app.innerHTML;
      fire('input', { value: 'two', dataset: { f: 'rowname', i: '0' } });      // duplicate of ticked row 1
      out.dup = [btn.disabled, why.textContent, btn.textContent];
      fire('input', { value: 'taken', dataset: { f: 'rowname', i: '0' } });    // duplicate of an existing job
      out.dupJob = [btn.disabled, why.textContent];
      fire('input', { value: 'fresh', dataset: { f: 'rowname', i: '0' } });
      out.fixed = [btn.disabled, why.textContent, btn.textContent];
      change('rownew', 2, true); out.newjob = app.innerHTML;
      change('rownew', 2, false); change('rowon', 0, false);
      click('start');
      setTimeout(function () { out.calls = global.calls; console.log(JSON.stringify(out)); process.exit(0); }, 100);
    }, 450);
    return;
  }
  if (arts) {
    fire('click', { closest: function () { return { dataset: { act: 'tab', arg: '3' }, disabled: false }; } });
    setTimeout(function () {
      out.html3 = app.innerHTML;
      fire('click', { closest: function () { return { dataset: { act: 'ftoggle', arg: '01_ingestion' }, disabled: false }; } });
      out.afterToggle = app.innerHTML;
      fire('click', { closest: function () { return { dataset: { act: 'tab', arg: '1' }, disabled: false }; } });
      fire('click', { closest: function () { return { dataset: { act: 'tab', arg: '3' }, disabled: false }; } });
      setTimeout(function () {
      out.afterRetab = app.innerHTML;
      fire('click', { closest: function () { return { dataset: { act: 'openfolder', arg: '02_chapters' }, disabled: false }; } });
      setTimeout(function () { out.calls = global.calls; out.afterOpen = app.innerHTML; console.log(JSON.stringify(out)); process.exit(0); }, 100);
      }, 100);
    }, 100);
    return;
  }
  if (started) {
    type('/books/one.txt');
    fire('click', { closest: function () { return { dataset: { act: 'start' }, disabled: false }; } });
    setTimeout(function () { out.afterStart = app.innerHTML; console.log(JSON.stringify(out)); process.exit(0); }, 100);
    return;
  }
  console.log(JSON.stringify(out)); process.exit(0);
}, 50);
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
class TestStartButtonSync:
    def _run(self, tmp_path, mode):
        js = re.search(r"<script>(.*)</script>", PAGE, re.S).group(1)
        f = tmp_path / "run.js"
        setup, driver = _HARNESS.split("//DRIVER")
        f.write_text(setup + "\n" + js + "\n" + driver, encoding="utf-8")
        r = subprocess.run(["node", str(f), mode], capture_output=True, text=True, timeout=20)
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout.strip().splitlines()[-1])

    def test_typing_a_path_enables_start_in_place(self, tmp_path):
        out = self._run(tmp_path, "idle")
        assert out["empty"] == [True, "enter a path to start"]
        assert out["typed"] == [False, None, "", "my-novel"]
        assert out["blank"] == [True, "enter a path to start"]

    def test_busy_keeps_start_disabled_with_reason(self, tmp_path):
        out = self._run(tmp_path, "busy")
        # status poll flipped busy while the panel was open: the re-render reflects it
        assert 'data-start disabled aria-disabled="true"' in out["html"]
        assert out["typed"][0] is True and "run is in progress" in out["typed"][2]

    def test_single_queued_run_shows_no_empty_banner(self, tmp_path):
        html = self._run(tmp_path, "start")["afterStart"]
        assert "started one" in html
        assert "dismissSkip" not in html and "b-cyan" not in html

    def test_name_conflict_renders_unchecked_new_job_checkbox(self, tmp_path):
        html = self._run(tmp_path, "conflict")["afterStart"]
        box = re.search(r'<input type="checkbox" data-f="newJob"[^>]*>', html)
        assert box and "checked" not in box.group(0)

    def test_overwrite_conflict_new_job_action_ticks_the_box(self, tmp_path):
        out = self._run(tmp_path, "overwrite")
        assert re.search(r'<input type="checkbox" data-f="newJob"[^>]*>', out["afterStart"])
        box = re.search(r'<input type="checkbox" data-f="newJob"[^>]*>', out["afterAct"])
        assert box and "checked" in box.group(0)

    def test_message_isolates_arabic_names_and_paths(self, tmp_path):
        html = self._run(tmp_path, "conflict")["afterStart"]
        assert "&#39;<bdi dir=\"auto\" class=\"nmi\">\u0635\u062f\u0649-\u0627\u0644\u0646\u0633\u064a\u0627\u0646</bdi>&#39;" in html
        assert "(<bdi dir=\"auto\" class=\"nmi\">\u0635\u062f\u0649" in html


    def test_artifacts_tab_renders_blocks_links_and_open(self, tmp_path):
        out = self._run(tmp_path, "arts")
        collapsed, html = out["html3"], out["afterToggle"]
        assert "files" in " ".join(c[1] for c in out["calls"])
        # every block starts collapsed: headers only, whatever the file count
        assert collapsed.count("[ open folder ]") == 2 and collapsed.count('aria-expanded="false"') == 2
        assert 'aria-expanded="true"' not in collapsed and "/view?job=" not in collapsed and "fgrid" not in collapsed
        assert "· 3 files" in collapsed and "· 11 files" in collapsed
        assert ('<span class="stepmiss">\u2013 <b>03 segments</b> <span class="dim">\u00b7 not produced</span></span>') in collapsed
        assert "03_segments" not in collapsed.replace('data-arg="03_segments"', "") and "not produced" in collapsed
        # underscores are display-only: the toggle/open args keep the real folder name, headers show spaces
        assert "<b>01 ingestion</b>" in collapsed and 'data-arg="01_ingestion"' in collapsed and "<b>01_ingestion" not in collapsed
        assert re.search(r"· 3 files · \d{4}-\d{2}-\d{2} \d{2}:\d{2}</span>", collapsed)  # date after the count
        assert "· 11 files</span>" in collapsed  # no files -> no date
        # clicking a header expands just that block
        assert html.count('aria-expanded="true"') == 1 and html.count('aria-expanded="false"') == 1
        assert 'href="/view?job=%D8%B1' in html and 'target="_blank" rel="noopener"' in html
        assert "01_ingestion%2Fp%3Cb%3E.csv" in html and "p&lt;b&gt;.csv" in html and "<b>.csv" not in html
        assert "(2.0 KB)</span>" in html and 'title="clean_text.txt"' in html and 'class="fgrid"' in html
        # root files first with no subheader; subfolder gets "ssml/ · 1 file" label after them
        assert html.index("clean_text.txt") < html.index('class="gname"') < html.index("c1.csv")
        assert html.count('class="gname"') == 1 and "1 file</div>" in html
        # leaving and re-opening the tab collapses everything again
        assert 'aria-expanded="true"' not in out["afterRetab"] and "c1.csv" not in out["afterRetab"]
        assert ["POST", "/api/jobs/%D8%B1%D9%88%D8%A7%D9%8A%D8%A9/open", '{"path":"02_chapters"}'] in out["calls"]
        assert "opened 02_chapters" in out["afterOpen"]


    def test_folder_pick_list_rows_all_none_label_and_disabled(self, tmp_path):
        out = self._run(tmp_path, "scan")
        html = out["scan"]
        assert html.count('data-f="rowon"') == 3 and html.count('data-f="rowon"') == html.count(" checked>") - html.count('data-f="rownew"')
        assert "[ start 3 books ]" in html and "[ all ]" in html and "[ none ]" in html
        assert "job name (single file only)" not in html and 'id="f-name"' not in html
        assert "existing job \u2192 new run" in html and html.count('data-f="rownew"') == 1
        assert "scan.pdf" in html and "unsupported format" in html and "skiprow" in html
        assert "[ start 2 books ]" in out["untick"] and "[ start 0 books ]" in out["none"]
        assert 'data-start disabled aria-disabled="true"' in out["none"] and "tick at least one book" in out["none"]
        assert "[ start 3 books ]" in out["all"] and 'data-start disabled' not in out["all"]
        # live name validation: errors on a duplicate of a ticked row or of an existing job
        assert out["dup"] == [True, "fix the name errors first", "[ start 3 books ]"]
        assert out["dupJob"] == [True, "fix the name errors first"]
        assert out["fixed"] == [False, "", "[ start 3 books ]"]
        assert 'data-f="rownew" data-i="2" data-fid="rnew-2" checked' in out["newjob"]
        assert 'value="taken-2"' in out["newjob"] and "name already taken" not in out["newjob"].split('data-rerr="2"')[1][:80]
        # start sends only ticked rows, in list order
        body = json.loads(next(c[2] for c in out["calls"] if c[1] == "/api/runs"))
        assert body["books"] == [{"path": "/b/two.txt", "name": "two", "new_job": False},
                                 {"path": "/b/old.txt", "name": "taken", "new_job": False}]


    def test_queue_view_placeholders_and_stop(self, tmp_path):
        out = self._run(tmp_path, "queue")
        first = out["first"]
        assert first.count('<div class="card') == 3 and 'st-queued">queued</span> \u00b7 2 of 3' in first and 'st-queued">queued</span> \u00b7 3 of 3' in first
        assert "[\u2026]" in first  # queued status mark
        ph = out["placeholder"]  # selecting a placeholder card: its Run tab, no job entry needed
        assert "queued \u2014 position 2 of 3" in ph and "[ stop ]" in ph and "[ delete ]" not in ph and "[ rename ]" not in ph.split('class="rhead"')[1]
        assert not any(c[1] == "/api/jobs/b" for c in out["calls"])  # placeholder never fetches a job
        running = out["running"]
        assert "[ stop ]" in running and '[ delete ]</button><span class="dim">running or queued' in running
        assert ["POST", "/api/stop", "{}"] in out["calls"]

    def test_action_row_retry_delete_confirm(self, tmp_path):
        out = self._run(tmp_path, "acts")
        first = out["first"]
        assert first.index("[ retry ]") < first.index("[ delete ]") < first.index('data-log')  # actions sit above the log
        assert "[ stop ]" not in first and 'resumes from "splitting chapters"' in first
        ask = out["ask"]
        assert "Remove " in ask and "from history? Files on disk stay: " in ask and '<bdi class="pth" dir="ltr">' in ask and 'class="seg">x_sawt</bdi>' in ask
        assert "[ remove ]" not in out["cancelled"] and "from history?" not in out["cancelled"]
        assert ["POST", "/api/jobs/x/delete", "{}"] in out["calls"]


    def test_card_status_mapping_and_search(self, tmp_path):
        out = self._run(tmp_path, "cards")

        def card(html, name):
            m = re.search(r'<div class="card[^"]*"><button[^>]*data-arg="%s".*?</span></button>' % re.escape(name), html)
            assert m, name
            return re.sub(r"<[^>]+>", "", m.group(0)).strip()

        h = out["cards"]
        assert "jobs (11)" in h
        expect = {
            "a": ("[\u00b7]", "partial \u00b7 artifacts ready, audio pending"),
            "b": ("[\u2713]", "complete \u00b7 artifacts + audio"),
            "c": ("[\u00d7]", "failed \u00b7 chapters error"),
            "d": ("[>]", "running \u00b7 detecting dialogue"),
            "e": ("[\u25a0]", "stopped \u00b7 after chapters, retry to continue"),
            "f": ("[!]", "interrupted \u00b7 retry to continue"),
            "g": ("[\u00b7]", "imported \u00b7 artifacts only, no run log"),
            "h": ("[?]", "missing \u00b7 output folder deleted"),
            "i": ("[\u2026]", "queued \u00b7 2 of 2"),  # queued wins over its old run status
        }
        for name, (mark, line2) in expect.items():
            text = card(h, name)
            assert text.startswith(mark + " " + name) and text.endswith(line2), (name, text)
            assert "2026-01-02 \u00b7 2 runs" in text
        # status word carries its status colour class; line 2 is the muted row
        assert 'class="row2"><span class="st-failed">failed</span> \u00b7 chapters error' in h
        assert "ready for audio" not in re.sub(r"<[^>]+>", "", h.split('class="rpanel"')[0].split("jobsel")[1].split("</select>")[1])
        # search: case-insensitive on name or source file name, Latin and Arabic, live count, clear
        assert "jobs (1 of 11)" in out["latin"] and "jobs (1 of 11)" in out["src"] and "jobs (1 of 11)" in out["ar"] and "jobs (1 of 11)" in out["arsrc"]
        assert 'data-arg="mybook-job"' in out["src"] and 'data-arg="a"' not in out["src"].split('class="list"')[1].split("</aside>")[0]
        assert 'data-arg="\u0631\u0648\u0627\u064a\u0629"' in out["arsrc"].split('class="list"')[1]
        assert 'dir="auto" autocomplete="off" placeholder="search jobs"' in h and "[ \u00d7 ]" in out["ar"] and "[ \u00d7 ]" not in h
        assert "no jobs match" in out["none"] and "jobs (0 of 11)" in out["none"]
        # the selected job stays selected while filtered out of the list
        assert 'class="rhead"><span class="mk' in out["ar"] and '<span class="nm" dir="auto">a</span>' in out["ar"].split('class="rhead"')[1]
        assert "jobs (11)" in out["cleared"] and "[ \u00d7 ]" not in out["cleared"]


class TestPathsAndWording:
    def test_path_segments_are_isolates_with_wbr_after_slashes(self):
        js = PAGE.split("<script>")[1]
        for fn in ("function esc", "function pthInner", "function pth", "function msgHtml"):
            assert fn in js
        assert "<wbr>" in js and "unicode-bidi:isolate" in PAGE
        assert "white-space:nowrap" in PAGE.split(".pth .seg")[1].split("}")[0]
        assert "overflow-wrap:anywhere" not in re.search(r"\.v \.pth\{[^}]*\}", PAGE).group(0)

    def test_underscore_not_clipped_in_paths(self):
        rule = re.search(r"\.v \.pth[^{]*\{[^}]*line-height:([\d.]+)", PAGE)
        assert rule and float(rule.group(1)) >= 1.5

    def test_paths_render_ltr_isolated(self):
        assert re.search(r"function pth\(s\) \{ return '<bdi class=\"pth\" dir=\"ltr\">'", PAGE)
        assert "unicode-bidi:isolate" in PAGE
        assert "pth(job.source)" in PAGE and "pth(job.output)" in PAGE
        assert "dir=\"ltr\"" in PAGE.split("function msgHtml")[1].split("function when")[0]
        assert "esc(job.source" not in PAGE and "esc(job.output" not in PAGE

    def test_ui_errors_have_no_cli_flags(self, client, books):
        book = make_book(books)
        client.post("/api/runs", {"path": str(book)})
        client.wait_idle()
        other = make_book(books, stem="other")
        st, d = client.post("/api/runs", {"path": str(other), "name": "novel"})
        assert st == 400 and "job name" in d["error"] and "--" not in d["error"]
        st, d = client.post("/api/runs", {"path": str(book), "name": "x", "newJob": True})
        assert "--" not in d.get("error", "")
        st, d = client.post("/api/runs", {"path": str(book), "name": "novel", "newJob": True})
        assert st == 400 and "pick another job name" in d["error"] and "--" not in d["error"]
        st, d = client.post("/api/runs", {"path": str(books), "name": "z"})
        assert "--" not in d["error"]


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_path_renders_one_isolate_per_segment(tmp_path):
    js = re.search(r"<script>(.*)</script>", PAGE, re.S).group(1)
    helpers = js[js.index("function esc"):js.index("function when")]
    f = tmp_path / "h.js"
    f.write_text(helpers + "\nconsole.log(JSON.stringify([pth('/tmp/x/books/رحلة-ابن-فطومة.txt'),"
                 "msgHtml('bad /tmp/a/صدى b')]));", encoding="utf-8")
    r = subprocess.run(["node", str(f)], capture_output=True, text=True, timeout=20)
    assert r.returncode == 0, r.stderr
    a, b = json.loads(r.stdout)
    assert a.count('<bdi dir="ltr" class="seg">') == 4 and a.count("/<wbr>") == 4
    assert '<bdi dir="ltr" class="seg">رحلة-ابن-فطومة.txt</bdi>' in a
    assert 'dir="ltr"' in a and '<bdi dir="ltr" class="seg">صدى</bdi>' in b


# ---------------------------------------------------------------------------
# Module 3: artifacts
# ---------------------------------------------------------------------------


@pytest.fixture
def opened(monkeypatch):
    """Every test that can reach /open records the call; no file manager is ever launched."""
    calls = []
    monkeypatch.setattr(ui_core, "_open_folder", lambda path: calls.append(path))
    return calls


@pytest.fixture
def job(client, home, tmp_path):
    """A job (name 'bk') whose output folder holds a small pipeline tree; returns the output Path."""
    out = tmp_path / "bk_sawt"
    (out / "01_ingestion").mkdir(parents=True)
    (out / "01_ingestion" / "clean_text.txt").write_text(NARRATION + "\n\n" + DIALOGUE, encoding="utf-8")
    (out / "01_ingestion" / "paragraphs.csv").write_text("n,text\n1,x\n", encoding="utf-8")
    seg = out / "03_segments"
    (seg / "ssml").mkdir(parents=True)
    (seg / "review").mkdir()
    (seg / "segments.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    for i in range(3):
        (seg / "ssml" / f"chapter_{i}.csv").write_text("n,text\n1,x\n", encoding="utf-8")
    (seg / "review" / "chapter_0.txt").write_text("review", encoding="utf-8")
    save_jobs({"version": load_jobs().get("version", 1), "jobs": [
        {"name": "bk", "source": str(tmp_path / "bk.txt"), "output": str(out), "runs": []}]})
    return out


def raw_get(client, path):
    conn = http.client.HTTPConnection("127.0.0.1", client.port, timeout=10)
    conn.request("GET", path, headers={"Host": f"127.0.0.1:{client.port}"})
    r = conn.getresponse()
    body = r.read()
    conn.close()
    return r.status, {k.lower(): v for k, v in r.getheaders()}, body


def view(client, rel, name="bk"):
    return raw_get(client, f"/view?job={quote(name)}&path={quote(rel)}")


class TestArtifactListing:
    def test_steps_in_order_with_groups_sizes_and_missing_step(self, client, job):
        status, data = client.get("/api/jobs/bk/files")
        assert status == 200 and data["missing"] is False and data["output"] == str(job)
        assert [(s["name"], s["present"]) for s in data["steps"]] == [
            ("01_ingestion", True), ("02_chapters", False), ("03_segments", True), ("04_ssml", False)]
        ing = data["steps"][0]
        assert ing["count"] == 2 and "collapsed" not in ing
        assert ing["mtime"] == max((job / "01_ingestion" / n).stat().st_mtime for n in ("clean_text.txt", "paragraphs.csv"))
        assert data["steps"][1].get("mtime") is None
        assert [f["name"] for f in ing["groups"][0]["files"]] == ["clean_text.txt", "paragraphs.csv"]
        assert ing["groups"][0]["files"][1] == {"name": "paragraphs.csv", "rel": "paragraphs.csv",
                                                "path": "01_ingestion/paragraphs.csv", "size": 11}
        seg = data["steps"][2]
        assert [g["dir"] for g in seg["groups"]] == ["", "review", "ssml"]  # top level first
        assert seg["count"] == 5
        assert [f["path"] for f in seg["groups"][2]["files"]][0] == "03_segments/ssml/chapter_0.csv"
        assert seg["groups"][2]["files"][0]["rel"] == "ssml/chapter_0.csv"

    def test_05_audio_listed_only_when_present(self, client, job):
        assert "05_audio" not in [s["name"] for s in client.get("/api/jobs/bk/files")[1]["steps"]]
        (job / "05_audio" / "gemini").mkdir(parents=True)
        (job / "05_audio" / "gemini" / "chapter_1.mp3").write_bytes(b"id3")
        steps = client.get("/api/jobs/bk/files")[1]["steps"]
        assert steps[-1]["name"] == "05_audio" and steps[-1]["groups"][0]["dir"] == "gemini"

    def test_missing_job_folder(self, client, job):
        shutil.rmtree(job)
        status, data = client.get("/api/jobs/bk/files")
        assert status == 200 and data == {"missing": True, "output": str(job), "steps": []}

    def test_unknown_job_404_and_foreign_host_403(self, client, job):
        assert client.get("/api/jobs/ghost/files")[0] == 404
        assert client.get("/api/jobs/bk/files", host="evil.example.com")[0] == 403

    def test_symlinks_out_are_not_listed(self, client, job, tmp_path):
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("secret", encoding="utf-8")
        (job / "01_ingestion" / "linkdir").symlink_to(outside, target_is_directory=True)
        (job / "01_ingestion" / "linkfile.txt").symlink_to(outside / "secret.txt")
        ing = client.get("/api/jobs/bk/files")[1]["steps"][0]
        assert [f["name"] for g in ing["groups"] for f in g["files"]] == ["clean_text.txt", "paragraphs.csv"]
        # a step folder that is itself a symlink out counts as not produced
        (job / "02_chapters").symlink_to(outside, target_is_directory=True)
        assert client.get("/api/jobs/bk/files")[1]["steps"][1]["present"] is False

    def test_symlink_that_stays_inside_is_listed(self, client, job):
        (job / "01_ingestion" / "alias.txt").symlink_to(job / "01_ingestion" / "clean_text.txt")
        names = [f["name"] for g in client.get("/api/jobs/bk/files")[1]["steps"][0]["groups"] for f in g["files"]]
        assert "alias.txt" in names

    def test_imported_job_listing(self, client, tmp_path, monkeypatch):
        out = tmp_path / "output" / "txt" / "oldbook"
        (out / "01_ingestion").mkdir(parents=True)
        (out / "01_ingestion" / "clean_text.txt").write_text("x", encoding="utf-8")
        monkeypatch.setattr(ui_core, "import_existing", lambda: import_existing(tmp_path / "output", tmp_path / "data"))
        client.post("/api/import")
        data = client.get("/api/jobs/oldbook/files")[1]
        assert data["steps"][0]["count"] == 1 and data["steps"][1]["present"] is False

    def test_arabic_job_name(self, client, job):
        data = load_jobs()
        data["jobs"][0]["name"] = "رواية"
        save_jobs(data)
        assert client.get("/api/jobs/" + quote("رواية") + "/files")[0] == 200


class TestPathGuard:
    @pytest.mark.parametrize("rel", [
        "../outside.txt", "01_ingestion/../../outside.txt", "..", "/etc/passwd",
        "\\windows\\x", "01_ingestion/clean_text.txt\0.png", "\0",
    ])
    def test_escapes_rejected_everywhere(self, client, job, tmp_path, opened, rel):
        (tmp_path / "outside.txt").write_text("out", encoding="utf-8")
        assert view(client, rel)[0] == 403
        assert client.post("/api/jobs/bk/open", {"path": rel})[0] == 403
        assert opened == []

    def test_absolute_path_inside_output_still_rejected(self, client, job):
        assert view(client, str(job / "01_ingestion" / "clean_text.txt"))[0] == 403

    def test_symlink_file_pointing_out_rejected(self, client, job, tmp_path):
        (tmp_path / "secret.txt").write_text("secret", encoding="utf-8")
        (job / "01_ingestion" / "leak.txt").symlink_to(tmp_path / "secret.txt")
        status, _, body = view(client, "01_ingestion/leak.txt")
        assert status == 403 and b"secret" not in body

    def test_symlink_dir_pointing_out_rejected(self, client, job, tmp_path, opened):
        outside = tmp_path / "outdir"
        outside.mkdir()
        (outside / "a.txt").write_text("x", encoding="utf-8")
        (job / "01_ingestion" / "lnk").symlink_to(outside, target_is_directory=True)
        assert view(client, "01_ingestion/lnk/a.txt")[0] == 403
        assert client.post("/api/jobs/bk/open", {"path": "01_ingestion/lnk"})[0] == 403
        assert opened == []

    def test_dangling_symlink_out_rejected(self, client, job, tmp_path):
        (job / "01_ingestion" / "gone.txt").symlink_to(tmp_path / "nowhere.txt")
        assert view(client, "01_ingestion/gone.txt")[0] == 403

    def test_unknown_job_404(self, client, job, opened):
        assert view(client, "01_ingestion/clean_text.txt", name="ghost")[0] == 404
        assert client.post("/api/jobs/ghost/open", {"path": ""})[0] == 404
        assert opened == []

    def test_missing_file_404_and_non_string_path(self, client, job, opened):
        assert view(client, "01_ingestion/nope.txt")[0] == 404
        assert client.post("/api/jobs/bk/open", {"path": 5})[0] == 403
        assert client.post("/api/jobs/bk/open", {"path": ["a"]})[0] == 403
        assert opened == []

    def test_dotdot_that_stays_inside_is_fine(self, client, job):
        assert view(client, "03_segments/../01_ingestion/clean_text.txt")[0] == 200

    def test_view_foreign_host_rejected(self, client, job):
        conn = http.client.HTTPConnection("127.0.0.1", client.port, timeout=10)
        conn.request("GET", "/view?job=bk&path=01_ingestion/clean_text.txt", headers={"Host": "evil.example.com"})
        assert conn.getresponse().status == 403
        conn.close()


class TestViewer:
    def test_arabic_csv_is_a_table_and_escaped(self, client, job):
        (job / "01_ingestion" / "paragraphs.csv").write_text(
            f'n,text\n1,"{NARRATION}"\n2,"<script>alert(1)</script> & ""q"""\n', encoding="utf-8")
        status, headers, body = view(client, "01_ingestion/paragraphs.csv")
        page = body.decode("utf-8")
        assert status == 200 and headers["content-type"] == "text/html; charset=utf-8"
        assert "<table dir=\"ltr\">" in page and "<thead><tr><th dir=\"auto\" class=\"n\">n</th>" in page
        assert f'<td dir="auto">{NARRATION}</td>' in page
        assert "<script>" not in page and "&lt;script&gt;alert(1)&lt;/script&gt; &amp; &quot;q&quot;" in page
        assert "position:sticky" in page and "<title>paragraphs.csv</title>" in page
        assert "job <bdi" in page and "01_ingestion/paragraphs.csv" in page

    def test_csv_with_bom_and_embedded_newline(self, client, job):
        (job / "01_ingestion" / "p.csv").write_bytes("\ufeffn,text\n1,\"a\nb\"\n".encode("utf-8"))
        page = view(client, "01_ingestion/p.csv")[2].decode("utf-8")
        assert '<th dir="auto" class="n">n</th>' in page and "a\nb" in page

    def test_csv_narrow_columns_nowrap_text_column_wraps(self, client, job):
        (job / "01_ingestion" / "s.csv").write_text(
            "segment_number,type,char_count,text\n1,narrator,5," + NARRATION + "\n", encoding="utf-8")
        page = view(client, "01_ingestion/s.csv")[2].decode("utf-8")
        assert '<th dir="auto" class="n">segment_number</th>' in page and '<td dir="auto" class="n">narrator</td>' in page
        assert '<th dir="auto">text</th>' in page and f'<td dir="auto">{NARRATION}</td>' in page
        assert ".n{white-space:nowrap;width:1%}" in page
        # no "text" header: the last column is the wide one
        (job / "01_ingestion" / "t.csv").write_text("a,b\nx,y\n", encoding="utf-8")
        page = view(client, "01_ingestion/t.csv")[2].decode("utf-8")
        assert '<td dir="auto" class="n">x</td><td dir="auto">y</td>' in page

    def test_neutral_lines_default_rtl_latin_stays_auto(self, client, job):
        (job / "01_ingestion" / "n.txt").write_text("\u0661\nHello\n12:30\n" + NARRATION, encoding="utf-8")
        page = view(client, "01_ingestion/n.txt")[2].decode("utf-8")
        assert '<div dir="rtl">\u0661</div><div dir="auto">Hello</div><div dir="rtl">12:30</div>' in page
        (job / "01_ingestion" / "n.csv").write_text("n,text\n\u0661,Hello\n", encoding="utf-8")
        page = view(client, "01_ingestion/n.csv")[2].decode("utf-8")
        assert '<td dir="rtl" class="n">\u0661</td><td dir="auto">Hello</td>' in page

    def test_txt_lines_each_dir_auto_and_escaped(self, client, job):
        (job / "01_ingestion" / "clean_text.txt").write_text(f"{NARRATION}\n\n<b>x</b>\n{DIALOGUE}", encoding="utf-8")
        status, _, body = view(client, "01_ingestion/clean_text.txt")
        page = body.decode("utf-8")
        assert status == 200 and '<pre dir="rtl">' in page
        assert f'<div dir="auto">{NARRATION}</div><div dir="rtl"></div><div dir="auto">&lt;b&gt;x&lt;/b&gt;</div>' in page
        assert "<b>x</b>" not in page

    @pytest.mark.parametrize("ext", [".ssml", ".json", ".xml"])
    def test_other_text_types_use_pre(self, client, job, ext):
        (job / "01_ingestion" / f"f{ext}").write_text("<speak>x</speak>", encoding="utf-8")
        page = view(client, f"01_ingestion/f{ext}")[2].decode("utf-8")
        assert '<pre dir="rtl"><div dir="auto">&lt;speak&gt;x&lt;/speak&gt;</div></pre>' in page

    def test_unknown_extension_is_a_download(self, client, job):
        (job / "01_ingestion" / "ملف.mp3").write_bytes(b"ID3\x00audio")
        status, headers, body = view(client, "01_ingestion/ملف.mp3")
        assert status == 200 and body == b"ID3\x00audio"
        assert headers["content-disposition"].startswith("attachment; filename*=UTF-8''")
        assert quote("ملف.mp3") in headers["content-disposition"]
        assert headers["content-type"] == "application/octet-stream" and headers["x-content-type-options"] == "nosniff"

    def test_html_file_is_never_rendered(self, client, job):
        (job / "01_ingestion" / "x.html").write_text("<script>alert(1)</script>", encoding="utf-8")
        _, headers, _ = view(client, "01_ingestion/x.html")
        assert "attachment" in headers["content-disposition"] and headers["content-type"] == "application/octet-stream"

    def test_oversize_file_gets_a_message(self, client, job, monkeypatch):
        monkeypatch.setattr(ui_core, "VIEW_MAX_BYTES", 10)
        (job / "01_ingestion" / "big.txt").write_text("x" * 50, encoding="utf-8")
        status, _, body = view(client, "01_ingestion/big.txt")
        page = body.decode("utf-8")
        assert status == 200 and "too large to show" in page and "xxxxx" not in page

    def test_csp_and_no_scripts(self, client, job):
        status, headers, body = view(client, "01_ingestion/clean_text.txt")
        csp = headers["content-security-policy"]
        assert csp == ui_core.VIEW_CSP and "default-src 'none'" in csp and "script-src" not in csp
        assert b"<script" not in body and headers["cache-control"] == "no-store"
        assert "prefers-color-scheme: dark" in body.decode("utf-8")

    def test_directory_is_404(self, client, job):
        assert view(client, "01_ingestion")[0] == 404

    def test_bad_utf8_does_not_crash(self, client, job):
        (job / "01_ingestion" / "bad.txt").write_bytes(b"ok \xff\xfe end")
        assert view(client, "01_ingestion/bad.txt")[0] == 200


class TestOpenFolder:
    def test_opens_resolved_directory(self, client, job, opened):
        status, data = client.post("/api/jobs/bk/open", {"path": "03_segments/ssml"})
        assert status == 200 and data == {"opened": "03_segments/ssml"}
        assert opened == [(job / "03_segments" / "ssml").resolve()]

    def test_empty_path_opens_output_folder(self, client, job, opened):
        assert client.post("/api/jobs/bk/open", {})[0] == 200
        assert client.post("/api/jobs/bk/open", {"path": ""})[0] == 200
        assert opened == [job.resolve()] * 2

    def test_file_rejected(self, client, job, opened):
        status, data = client.post("/api/jobs/bk/open", {"path": "01_ingestion/clean_text.txt"})
        assert status == 400 and "folders" in data["error"] and opened == []

    def test_missing_folder_404(self, client, job, opened):
        assert client.post("/api/jobs/bk/open", {"path": "04_ssml"})[0] == 404
        assert opened == []

    def test_foreign_host_and_content_type(self, client, job, opened):
        assert client.post("/api/jobs/bk/open", {}, host="evil.example.com")[0] == 403
        assert client.call("POST", "/api/jobs/bk/open", raw=b"{}", ctype="text/plain")[0] == 415
        assert opened == []

    def test_opener_failure_is_reported(self, client, job, monkeypatch):
        def boom(path):
            raise FileNotFoundError("xdg-open")
        monkeypatch.setattr(ui_core, "_open_folder", boom)
        status, data = client.post("/api/jobs/bk/open", {})
        assert status == 500 and "file manager" in data["error"]

    @pytest.mark.parametrize("platform,cmd", [("linux", "xdg-open"), ("darwin", "open")])
    def test_opener_uses_arg_list_no_shell_no_wait(self, monkeypatch, tmp_path, platform, cmd):
        seen = {}

        class FakePopen:
            def __init__(self, args, **kw):
                seen["args"], seen["kw"] = args, kw

            def wait(self, *a, **k):
                raise AssertionError("must not wait")

        monkeypatch.setattr(ui_core.sys, "platform", platform)
        monkeypatch.setattr(ui_core.subprocess, "Popen", FakePopen)
        ui_core._open_folder(tmp_path)
        assert seen["args"] == [cmd, str(tmp_path)] and not seen["kw"].get("shell")

    def test_windows_uses_startfile(self, monkeypatch, tmp_path):
        calls = []
        monkeypatch.setattr(ui_core.sys, "platform", "win32")
        monkeypatch.setattr(os, "startfile", calls.append, raising=False)
        ui_core._open_folder(tmp_path)
        assert calls == [tmp_path]


# ---------------------------------------------------------------------------
# Folder pick list: scan endpoint and the books-list form of POST /api/runs
# ---------------------------------------------------------------------------


class TestScan:
    def test_folder_lists_books_and_skipped(self, client, books):
        make_book(books, "one")
        make_book(books, "two")
        (books / "scan.pdf").write_bytes(b"x")
        (books / "old.doc").write_bytes(b"x")
        (books / ".hidden.txt").write_text("x", encoding="utf-8")
        (books / "sub").mkdir()
        make_book(books / "sub", "deep")  # one level only
        status, data = client.get("/api/scan?path=" + quote(str(books)))
        assert status == 200 and data["kind"] == "folder"
        assert [(b["file"], b["name"], b["job"]) for b in data["books"]] == [("one.txt", "one", None), ("two.txt", "two", None)]
        assert data["books"][0]["path"] == str((books / "one.txt").resolve())
        skipped = {s["file"]: s["reason"] for s in data["skipped"]}
        assert set(skipped) == {"old.doc", "scan.pdf"} and "save it as .docx" in skipped["old.doc"]

    def test_existing_job_reported(self, client, books):
        book = make_book(books, "one")
        client.post("/api/runs", {"path": str(book)})
        client.wait_idle()
        client.post("/api/jobs/one/rename", {"name": "renamed"})
        data = client.get("/api/scan?path=" + quote(str(books)))[1]
        assert data["books"][0]["job"] == "renamed" and data["books"][0]["name"] == "renamed"

    def test_single_file(self, client, books):
        book = make_book(books, "solo")
        data = client.get("/api/scan?path=" + quote(str(book)))[1]
        assert data["kind"] == "file" and [b["file"] for b in data["books"]] == ["solo.txt"]

    def test_errors_in_bad_style(self, client, books):
        (books / "scan.pdf").write_bytes(b"x")
        for raw, text in (("/definitely/not/here", "path not found"), ("relative/dir", "absolute path"),
                          ("", "path is required"), (str(books / "scan.pdf"), "unsupported format")):
            status, data = client.get("/api/scan?path=" + quote(raw))
            assert status == 400 and data["field"] == "path" and text in data["error"], raw
        assert client.get("/api/scan")[0] == 400

    def test_foreign_host_rejected(self, client, books):
        assert client.get("/api/scan?path=" + quote(str(books)), host="evil.example.com")[0] == 403

    def test_empty_folder_is_not_an_error(self, client, books):
        assert client.get("/api/scan?path=" + quote(str(books)))[1]["books"] == []


def book_item(book, name=None, new_job=False):
    item = {"path": str(book), "new_job": new_job}
    if name is not None:
        item["name"] = name
    return item


class TestBooksListRun:
    def test_subset_runs_in_list_order(self, client, books):
        a, b, c = (make_book(books, s) for s in ("a", "b", "c"))
        status, data = client.post("/api/runs", {"books": [book_item(c, "c"), book_item(a, "a")]})
        assert status == 202 and data == {"queued": ["c", "a"], "skipped": []}
        client.wait_idle()
        assert {r["name"] for r in client.get("/api/jobs")[1]["jobs"]} == {"a", "c"}
        assert not (books / "b_sawt").exists()

    def test_rename_per_row(self, client, books):
        a = make_book(books, "a")
        status, data = client.post("/api/runs", {"books": [book_item(a, "الرواية")], "ssml": True, "fiction": False})
        assert status == 202 and data["queued"] == ["الرواية"]
        client.wait_idle()
        assert (books / "الرواية_sawt").is_dir()
        assert client.job("الرواية")["runs"][-1]["settings"] == {"ssml": True, "fiction": False}

    def test_duplicate_name_skipped_not_fatal(self, client, books):
        a, b, c = (make_book(books, s) for s in ("a", "b", "c"))
        status, data = client.post("/api/runs", {"books": [book_item(a, "same"), book_item(b, "same"), book_item(c, "c")]})
        assert status == 202 and data["queued"] == ["same", "c"]
        assert data["skipped"][0]["file"] == "b.txt" and "already used" in data["skipped"][0]["reason"]
        client.wait_idle()

    def test_name_taken_by_existing_job_skipped_among_many_rejected_alone(self, client, books):
        other = books / "elsewhere"
        other.mkdir()
        client.post("/api/runs", {"path": str(make_book(other, "dup"))})
        client.wait_idle()
        a, b = make_book(books, "a"), make_book(books, "b")
        status, data = client.post("/api/runs", {"books": [book_item(a, "dup"), book_item(b, "b")]})
        assert status == 202 and data["queued"] == ["b"] and "already taken" in data["skipped"][0]["reason"]
        client.wait_idle()
        status, data = client.post("/api/runs", {"books": [book_item(a, "dup")]})
        assert status == 400 and data["field"] == "books" and "already taken" in data["error"]

    def test_existing_job_new_run_vs_new_job(self, client, books):
        book = make_book(books, "novel")
        client.post("/api/runs", {"path": str(book)})
        client.wait_idle()
        (books / "novel_sawt" / "01_ingestion" / "marker.txt").write_text("old", encoding="utf-8")
        # unticked "new job": a new run on the existing job, behind the overwrite warning
        status, data = client.post("/api/runs", {"books": [book_item(book, "novel")]})
        assert status == 409 and data["overwrite"] is True and data["jobs"] == ["novel"]
        assert client.post("/api/runs", {"books": [book_item(book, "novel")], "confirm": True})[0] == 202
        client.wait_idle()
        assert len(client.job("novel")["runs"]) == 2
        # ticked "new job": a separate job with its own folder, no warning
        status, data = client.post("/api/runs", {"books": [book_item(book, "novel-2", True)]})
        assert status == 202 and data["queued"] == ["novel-2"]
        client.wait_idle()
        assert (books / "novel-2_sawt").is_dir()
        # a different name without new_job is refused for that book
        assert client.post("/api/runs", {"books": [book_item(book, "other")]})[0] == 400

    @pytest.mark.parametrize("make_items", [
        lambda books: [{"path": str(books)}],                      # a folder
        lambda books: [{"path": str(books / "ghost.txt")}],        # missing
        lambda books: [{"path": "relative.txt"}],
        lambda books: [{"path": str(books / "scan.pdf")}],         # unsupported
        lambda books: [{"path": str(books / "old.doc")}],
        lambda books: ["not-an-object"],
        lambda books: [{"path": 5}],
        lambda books: [],
        lambda books: "nope",
    ])
    def test_revalidates_every_path(self, client, books, make_items):
        for n in ("scan.pdf", "old.doc"):
            (books / n).write_bytes(b"x")
        good = make_book(books, "good")
        status, data = client.post("/api/runs", {"books": [book_item(good), *make_items(books)]}
                                   if make_items(books) else {"books": make_items(books)})
        assert status == 400 and data["field"] == "books" and data["error"]
        assert client.get("/api/status")[1]["busy"] is False and client.get("/api/jobs")[1]["jobs"] == []

    def test_non_text_name_rejected(self, client, books):
        a = make_book(books, "a")
        assert client.post("/api/runs", {"books": [{"path": str(a), "name": 3}]})[0] == 400

    def test_busy_refused(self, client, books, monkeypatch):
        a, b = make_book(books, "a"), make_book(books, "b")
        gate, entered = threading.Event(), threading.Event()
        real = runner_core._STEP_FUNCS["ingest"]

        def slow(job, run):
            entered.set()
            gate.wait(10)
            return real(job, run)

        monkeypatch.setitem(runner_core._STEP_FUNCS, "ingest", slow)
        assert client.post("/api/runs", {"books": [book_item(a, "a")]})[0] == 202
        assert entered.wait(10)
        assert client.post("/api/runs", {"books": [book_item(b, "b")]})[0] == 409
        gate.set()
        client.wait_idle()


class TestFreeDefaultNames:
    def _job(self, client, books, sub, stem):
        d = books / sub
        d.mkdir(exist_ok=True)
        client.post("/api/runs", {"path": str(make_book(d, stem))})
        client.wait_idle()

    def test_scan_taken_stem_gets_dash_2_then_dash_3(self, client, books):
        self._job(client, books, "old1", "novel")
        folder = books / "new"
        folder.mkdir()
        make_book(folder, "novel")
        make_book(folder, "other")
        rows = client.get("/api/scan?path=" + quote(str(folder)))[1]["books"]
        assert [(r["name"], r["free_name"], r["job"]) for r in rows] == [("novel-2", "novel-2", None), ("other", "other", None)]
        self._job(client, books, "old2", "novel")  # a job named novel-2 now exists too
        assert client.get("/api/scan?path=" + quote(str(folder)))[1]["books"][0]["name"] == "novel-3"

    def test_single_file_default(self, client, books):
        self._job(client, books, "old", "novel")
        solo = make_book(books, "novel")
        data = client.get("/api/scan?path=" + quote(str(solo)))[1]
        assert data["kind"] == "file" and data["books"][0]["name"] == "novel-2"
        status, out = client.post("/api/runs", {"path": str(solo)})
        assert status == 202 and out["queued"] == ["novel-2"]
        client.wait_idle()

    def test_existing_job_row_unchanged_but_offers_free_name_for_new_job(self, client, books):
        self._job(client, books, "same", "novel")
        row = client.get("/api/scan?path=" + quote(str(books / "same")))[1]["books"][0]
        assert row["job"] == "novel" and row["name"] == "novel" and row["free_name"] == "novel-2"
        # re-running that book without a name keeps targeting the existing job
        status, out = client.post("/api/runs", {"path": str(books / "same" / "novel.txt"), "confirm": True})
        assert status == 202 and out["queued"] == ["novel"]
        client.wait_idle()

    def test_free_job_name_helper(self):
        data = {"jobs": [{"name": "a"}, {"name": "a-2"}]}
        assert runner_core.free_job_name(data, "b") == "b"
        assert runner_core.free_job_name(data, "a") == "a-3"
        assert runner_core.free_job_name(data, "a", reserved={"a-3"}) == "a-4"


class TestStepMtime:
    def test_newest_file_anywhere_in_step_wins(self, client, job):
        old, new = 1_600_000_000, 1_700_000_000
        for f in (job / "03_segments").rglob("*"):
            if f.is_file():
                os.utime(f, (old, old))
        os.utime(job / "03_segments" / "review" / "chapter_0.txt", (new, new))
        steps = client.get("/api/jobs/bk/files")[1]["steps"]
        assert steps[2]["mtime"] == new

    def test_symlinked_file_out_does_not_count(self, client, job, tmp_path):
        outside = tmp_path / "later.txt"
        outside.write_text("x", encoding="utf-8")
        for f in (job / "01_ingestion").iterdir():
            os.utime(f, (1_600_000_000, 1_600_000_000))
        os.utime(outside, (1_900_000_000, 1_900_000_000))
        (job / "01_ingestion" / "leak.txt").symlink_to(outside)
        assert client.get("/api/jobs/bk/files")[1]["steps"][0]["mtime"] == 1_600_000_000

    def test_empty_step_has_no_mtime(self, client, job):
        (job / "04_ssml").mkdir()
        step = client.get("/api/jobs/bk/files")[1]["steps"][3]
        assert step["present"] is True and step["count"] == 0 and step["mtime"] is None


# ---------------------------------------------------------------------------
# Job actions: stop, delete, queue view
# ---------------------------------------------------------------------------


class Gate:
    """Holds the 'ingest' step of every book until released, so a run can be inspected mid-step."""

    def __init__(self, monkeypatch):
        self.go, self.entered, self.real = threading.Event(), threading.Event(), runner_core._STEP_FUNCS["ingest"]
        monkeypatch.setitem(runner_core._STEP_FUNCS, "ingest", self)

    def __call__(self, job, run):
        self.entered.set()
        self.go.wait(10)
        return self.real(job, run)


class TestStop:
    def test_stop_clears_queue_and_current_stops_at_step_boundary_then_retry_resumes(self, client, books, monkeypatch):
        for n in "abc":
            make_book(books, n)
        gate = Gate(monkeypatch)
        assert client.post("/api/runs", {"path": str(books)})[0] == 202
        assert gate.entered.wait(10)
        st = client.get("/api/status")[1]
        assert st["current"] == "a" and st["queued"] == ["b", "c"] and st["stopping"] is False
        assert [r["name"] for r in client.get("/api/jobs")[1]["jobs"]] == ["a"]  # queued books have no job entry
        status, data = client.post("/api/stop")
        assert status == 200 and data == {"dropped": ["b", "c"]}
        st = client.get("/api/status")[1]
        assert st["queued"] == [] and st["current"] == "a" and st["stopping"] is True
        # never killed mid-step: the step is still marked running until it finishes
        assert client.job("a")["runs"][-1]["steps"]["ingest"] == "running"
        gate.go.set()
        client.wait_idle()
        jobs = client.get("/api/jobs")[1]["jobs"]
        assert [r["name"] for r in jobs] == ["a"]
        run = client.job("a")["runs"][-1]
        assert run["status"] == runner_core.RUN_STOPPED == "stopped"
        assert run["steps"] == {"ingest": "ok", "chapters": "pending", "dialogue": "pending", "ssml": "pending"}
        assert run["log"][-1] == "■ stopped by user after ingesting"
        assert client.get("/api/status")[1]["stopping"] is False
        # stopped is retryable: resumes from the next undone step, ingest output untouched
        ing = {p.name: p.stat().st_mtime_ns for p in (books / "a_sawt" / "01_ingestion").iterdir()}
        assert client.post("/api/jobs/a/retry")[0] == 202
        client.wait_idle()
        run = client.job("a")["runs"][-1]
        assert run["status"] == runner_core.RUN_READY and len(client.job("a")["runs"]) == 1
        assert {p.name: p.stat().st_mtime_ns for p in (books / "a_sawt" / "01_ingestion").iterdir()} == ing

    def test_stop_while_idle_is_a_noop(self, client):
        assert client.post("/api/stop") == (200, {"dropped": []})

    def test_stop_during_last_real_step_finishes_normally(self, client, books, monkeypatch):
        make_book(books, "a")
        gate, last = threading.Event(), threading.Event()
        real = runner_core._STEP_FUNCS["dialogue"]

        def slow(job, run):
            last.set()
            gate.wait(10)
            return real(job, run)

        monkeypatch.setitem(runner_core._STEP_FUNCS, "dialogue", slow)
        client.post("/api/runs", {"path": str(books / "a.txt")})  # ssml off: dialogue is the last step that runs
        assert last.wait(10)
        client.post("/api/stop")
        gate.set()
        client.wait_idle()
        assert client.job("a")["runs"][-1]["status"] == runner_core.RUN_READY

    def test_new_run_after_stop_is_not_stopped(self, client, books, monkeypatch):
        make_book(books, "a")
        gate = Gate(monkeypatch)
        client.post("/api/runs", {"path": str(books / "a.txt")})
        assert gate.entered.wait(10)
        client.post("/api/stop")
        gate.go.set()
        client.wait_idle()
        assert client.post("/api/jobs/a/retry")[0] == 202
        client.wait_idle()
        assert client.job("a")["runs"][-1]["status"] == runner_core.RUN_READY

    def test_stop_rejects_foreign_host_and_needs_json(self, client):
        assert client.post("/api/stop", host="evil.example.com")[0] == 403
        assert client.call("POST", "/api/stop", raw=b"{}", ctype="text/plain")[0] == 415

    def test_runner_should_stop_is_polled_between_steps_only(self, home, books):
        seen = []

        def stop_after_two():
            seen.append(1)
            return len(seen) >= 2

        run = runner_core.run_book(make_book(books, "a"), assume_yes=True, emit=lambda m: None, should_stop=stop_after_two)
        assert run["status"] == "stopped" and run["log"][-1].startswith("■ stopped by user after ")
        assert [s for s, v in run["steps"].items() if v == "ok"] == ["ingest", "chapters"]
        # without should_stop (the CLI) nothing changes
        assert runner_core.run_book(make_book(books, "b"), assume_yes=True, emit=lambda m: None)["status"] == runner_core.RUN_READY


class TestDelete:
    def test_removes_history_only(self, client, books):
        book = make_book(books, "novel")
        client.post("/api/runs", {"path": str(book)})
        client.wait_idle()
        out = books / "novel_sawt"
        status, data = client.post("/api/jobs/novel/delete")
        assert status == 200 and data == {"deleted": "novel"}
        assert client.get("/api/jobs")[1]["jobs"] == [] and client.get("/api/jobs/novel")[0] == 404
        assert load_jobs()["jobs"] == []
        assert (out / "01_ingestion" / "clean_text.txt").is_file() and book.is_file()  # files stay on disk

    def test_unknown_job_404(self, client):
        assert client.post("/api/jobs/ghost/delete")[0] == 404

    def test_refused_while_running_or_queued_and_while_busy(self, client, books, monkeypatch):
        for n in "abc":
            make_book(books, n)
        client.post("/api/runs", {"path": str(books / "c.txt")})
        client.wait_idle()
        gate = Gate(monkeypatch)
        client.post("/api/runs", {"path": str(books / "a.txt")})
        assert gate.entered.wait(10)
        status, data = client.post("/api/jobs/a/delete")  # running
        assert status == 400 and "running or queued" in data["error"]
        status, data = client.post("/api/jobs/c/delete")  # other job: jobs.json has one writer, refused while busy
        assert status == 409 and data["busy"] is True
        gate.go.set()
        client.wait_idle()
        assert {r["name"] for r in client.get("/api/jobs")[1]["jobs"]} == {"a", "c"}
        # queued: a re-run of c waits behind a gated run of a
        gate.go.clear()
        gate.entered.clear()
        client.post("/api/runs", {"books": [{"path": str(books / "a.txt"), "name": "a"},
                                             {"path": str(books / "c.txt"), "name": "c"}], "confirm": True})
        assert gate.entered.wait(10)
        assert client.get("/api/status")[1]["queued"] == ["c"]
        status, data = client.post("/api/jobs/c/delete")
        assert status == 400 and "running or queued" in data["error"]
        gate.go.set()
        client.wait_idle()
        assert client.post("/api/jobs/c/delete")[0] == 200

    def test_runner_delete_job_helper(self, home, books):
        runner_core.run_book(make_book(books, "a"), assume_yes=True, emit=lambda m: None)
        runner_core.delete_job("a")
        assert load_jobs()["jobs"] == []
        with pytest.raises(runner_core.RunnerError):
            runner_core.delete_job("a")
