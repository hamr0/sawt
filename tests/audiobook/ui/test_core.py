"""Tests for module 2: local UI shell (real server on port 0, SAWT_HOME in tmp)."""
import http.client
import json
import re
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
        assert "<title>Sawt Runner</title>" in body

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
        assert client.get("/files/a/b/c")[0] == 404  # module 3 not built
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

    def test_folder_name_collision_is_skipped_not_run(self, client, books):
        make_book(books, "same")
        (books / "same.docx").write_bytes(b"x")  # will fail ingest, but shares the stem
        status, data = client.post("/api/runs", {"path": str(books)})
        assert status == 202 and data["queued"] == ["same"]
        assert any("already used" in s["reason"] for s in data["skipped"])
        client.wait_idle()

    def test_folder_book_with_taken_name_is_skipped_not_fatal(self, client, books):
        other = books / "elsewhere"
        other.mkdir()
        client.post("/api/runs", {"path": str(make_book(other, "dup"))})
        client.wait_idle()
        folder = books / "folder"
        folder.mkdir()
        make_book(folder, "dup")
        make_book(folder, "fresh")
        status, data = client.post("/api/runs", {"path": str(folder)})
        assert status == 202 and data["queued"] == ["fresh"]
        assert data["skipped"][0]["file"] == "dup.txt" and "already taken" in data["skipped"][0]["reason"]
        client.wait_idle()

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

    def test_artifacts_tab_is_placeholder_only(self):
        assert "artifacts — module 3, not built yet" in PAGE
        assert "/api/jobs/' + enc" in PAGE and "/artifacts" not in PAGE and "/files/" not in PAGE

    @pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
    def test_page_js_parses(self, tmp_path):
        js = re.search(r"<script>(.*)</script>", PAGE, re.S).group(1)
        f = tmp_path / "page.js"
        f.write_text(js, encoding="utf-8")
        r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
