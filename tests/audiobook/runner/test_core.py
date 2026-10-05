"""Tests for module 0: pipeline runner (CLI + job history)."""
import hashlib
import json
import os
from pathlib import Path

import pytest

import src.audiobook.runner.core as runner_core
from src.audiobook.runner import (
    RunnerError, import_existing, jobs_path, list_jobs, main, rename_job,
    retry_job, run_book, save_jobs, scan_path,
)

NARRATION = "كان الرجل يمشي في الطريق الطويل وحده بينما الشمس تغرب خلف البيوت القديمة"
DIALOGUE = "قال أحمد: كيف حالك اليوم يا صديقي وهل وصلت إلى البيت قبل المساء"


def make_book(folder: Path, stem: str = "novel", n: int = 40) -> Path:
    paras = [(DIALOGUE if i % 2 else NARRATION) + f" {i}" for i in range(n)]
    path = folder / f"{stem}.txt"
    path.write_text("\n\n".join(paras), encoding="utf-8")
    return path


def tree_hash(d: Path) -> str:
    m = hashlib.sha256()
    for p in sorted(d.rglob("*")):
        if p.is_file():
            m.update(str(p.relative_to(d)).encode())
            m.update(p.read_bytes())
    return m.hexdigest()


@pytest.fixture
def home(tmp_path, monkeypatch):
    h = tmp_path / "sawt_home"
    monkeypatch.setenv("SAWT_HOME", str(h))
    return h


@pytest.fixture
def lines():
    return []


def go(book, lines, **kw):
    kw.setdefault("assume_yes", True)
    return run_book(book, emit=lines.append, **kw)


class TestFullRun:
    def test_runs_steps_1_to_3_and_pauses_at_gate(self, tmp_path, home, lines):
        book = make_book(tmp_path)
        run = go(book, lines)
        out = tmp_path / "novel_sawt"
        assert run["status"] == "ready for audio — paused"
        assert (out / "01_ingestion" / "clean_text.txt").is_file()
        assert (out / "02_chapters" / "chapters.csv").is_file()
        assert (out / "03_segments" / "segments.csv").is_file()
        assert not (out / "04_ssml").exists()
        assert run["steps"] == {"ingest": "ok", "chapters": "ok", "dialogue": "ok", "ssml": "skipped"}

    def test_progress_lines_carry_real_numbers(self, tmp_path, home, lines):
        go(make_book(tmp_path), lines)
        text = "\n".join(lines)
        assert "✓ ingesting" in text
        assert "  > 40 paragraphs, " in text
        assert "(size-based fallback)" in text
        assert "% dialogue" in text
        assert "generating SSML — skipped (off)" in text
        assert lines[-1] == "ready for audio — paused before paid step"

    def test_ssml_opt_in_writes_04(self, tmp_path, home, lines):
        run = go(make_book(tmp_path), lines, ssml=True)
        assert list((tmp_path / "novel_sawt" / "04_ssml").glob("chapter_*.ssml"))
        assert run["steps"]["ssml"] == "ok"

    def test_non_fiction_skips_dialogue_and_ssml_even_if_asked(self, tmp_path, home, lines):
        run = go(make_book(tmp_path), lines, fiction=False, ssml=True)
        out = tmp_path / "novel_sawt"
        assert run["steps"] == {"ingest": "ok", "chapters": "ok", "dialogue": "skipped", "ssml": "skipped"}
        assert not (out / "03_segments").exists() and not (out / "04_ssml").exists()
        assert run["status"] == "ready for audio — paused"

    def test_job_name_sets_folder(self, tmp_path, home, lines):
        go(make_book(tmp_path), lines, name="mine")
        assert (tmp_path / "mine_sawt" / "01_ingestion").is_dir()


class TestScan:
    def test_folder_filters_and_rejects_doc(self, tmp_path):
        for n in ("a.txt", "b.DOCX", "c.epub", "d.doc", "e.pdf", ".hidden.txt"):
            (tmp_path / n).write_text("x")
        (tmp_path / "sub").mkdir()
        books, skipped = scan_path(str(tmp_path))
        assert [b.name for b in books] == ["a.txt", "b.DOCX", "c.epub"]
        reasons = {f.name: r for f, r in skipped}
        assert set(reasons) == {"d.doc", "e.pdf"}
        assert ".docx" in reasons["d.doc"]

    def test_single_doc_is_an_error(self, tmp_path):
        f = tmp_path / "old.doc"
        f.write_text("x")
        with pytest.raises(RunnerError, match="legacy .doc"):
            scan_path(str(f))

    def test_missing_path(self, tmp_path):
        with pytest.raises(RunnerError, match="not found"):
            scan_path(str(tmp_path / "nope"))

    def test_cli_runs_folder_books_in_order(self, tmp_path, home, lines):
        make_book(tmp_path, "b_book")
        make_book(tmp_path, "a_book")
        (tmp_path / "old.doc").write_text("x")
        rc = main([str(tmp_path)], emit=lines.append)
        assert rc == 0
        assert [j["name"] for j in json.loads(jobs_path().read_text())["jobs"]] == ["a_book", "b_book"]
        assert any(l.startswith("skipped old.doc: legacy .doc") for l in lines)


class TestFailureAndRetry:
    def _fail_dialogue(self, monkeypatch):
        def boom(*a, **k):
            raise RuntimeError("boom at step 3")
        monkeypatch.setattr(runner_core, "segment_book", boom)

    def test_failure_marks_step_and_cli_exits_nonzero(self, tmp_path, home, lines, monkeypatch):
        self._fail_dialogue(monkeypatch)
        make_book(tmp_path)
        rc = main([str(tmp_path / "novel.txt")], emit=lines.append)
        assert rc == 1
        run = json.loads(jobs_path().read_text())["jobs"][0]["runs"][0]
        assert run["status"] == "failed"
        assert run["steps"] == {"ingest": "ok", "chapters": "ok", "dialogue": "failed", "ssml": "pending"}
        assert run["errors"] == [{"step": "dialogue", "message": "RuntimeError: boom at step 3"}]
        assert "✗ detecting dialogue — RuntimeError: boom at step 3" in lines

    def test_retry_resumes_from_failed_step_leaving_done_steps_untouched(
        self, tmp_path, home, lines, monkeypatch
    ):
        book = make_book(tmp_path)
        with monkeypatch.context() as m:
            self._fail_dialogue(m)
            go(book, lines)
        out = tmp_path / "novel_sawt"
        before = {d: tree_hash(out / d) for d in ("01_ingestion", "02_chapters")}
        book.unlink()  # retry must use only files on disk, not the source
        lines.clear()
        run = retry_job("novel", emit=lines.append)
        assert run["status"] == "ready for audio — paused"
        assert {d: tree_hash(out / d) for d in before} == before
        assert (out / "03_segments" / "segments.csv").is_file()
        assert not any("ingesting" in l for l in lines)
        jobs = json.loads(jobs_path().read_text())["jobs"]
        assert len(jobs[0]["runs"]) == 1  # same run resumed, not a new one
        assert jobs[0]["runs"][0]["errors"][0]["step"] == "dialogue"  # failure stays on record

    def test_retry_when_not_failed_is_rejected(self, tmp_path, home, lines):
        go(make_book(tmp_path), lines)
        with pytest.raises(RunnerError, match="nothing to retry"):
            retry_job("novel", emit=lines.append)

    def test_retry_needs_previous_step_output(self, tmp_path, home, lines, monkeypatch):
        self._fail_dialogue(monkeypatch)
        go(make_book(tmp_path), lines)
        import shutil
        shutil.rmtree(tmp_path / "novel_sawt" / "02_chapters")
        with pytest.raises(RunnerError, match="02_chapters"):
            retry_job("novel", emit=lines.append)


class TestRerunAndNames:
    def test_rerun_appends_run_and_overwrites(self, tmp_path, home, lines):
        book = make_book(tmp_path)
        go(book, lines)
        stale = tmp_path / "novel_sawt" / "03_segments" / "stale.txt"
        stale.write_text("old")
        lines.clear()
        go(book, lines)
        job = json.loads(jobs_path().read_text())["jobs"][0]
        assert len(job["runs"]) == 2
        assert not stale.exists()
        assert "warning: overwriting the last run's files — start a new job instead to keep them" in lines
        assert len(json.loads(jobs_path().read_text())["jobs"]) == 1

    def test_declined_overwrite_changes_nothing(self, tmp_path, home, lines):
        book = make_book(tmp_path)
        go(book, lines)
        marker = tmp_path / "novel_sawt" / "03_segments" / "keep.txt"
        marker.write_text("keep")
        result = run_book(book, emit=lines.append, confirm=lambda _: False)
        assert result is None
        assert marker.exists()
        assert len(list_jobs()) == 1 and list_jobs()[0]["runs"] == 1

    def test_duplicate_name_for_other_book_rejected(self, tmp_path, home, lines):
        go(make_book(tmp_path, "one"), lines, name="shared")
        with pytest.raises(RunnerError, match="already taken"):
            go(make_book(tmp_path, "two"), lines, name="shared")
        assert len(list_jobs()) == 1

    def test_new_job_needs_a_new_name_then_gets_own_folder(self, tmp_path, home, lines):
        book = make_book(tmp_path)
        go(book, lines)
        with pytest.raises(RunnerError, match="already taken"):
            go(book, lines, new_job=True)
        go(book, lines, new_job=True, name="novel-v2")
        assert {j["name"] for j in list_jobs()} == {"novel", "novel-v2"}
        assert (tmp_path / "novel_sawt").is_dir() and (tmp_path / "novel-v2_sawt").is_dir()

    def test_rename_changes_label_not_folder(self, tmp_path, home, lines):
        book = make_book(tmp_path)
        go(book, lines)
        rename_job("novel", "better")
        job = json.loads(jobs_path().read_text())["jobs"][0]
        assert job["name"] == "better" and job["output"] == str(tmp_path / "novel_sawt")
        go(book, lines)  # re-run finds the renamed job, same folder
        assert len(list_jobs()) == 1 and list_jobs()[0]["runs"] == 2

    def test_rename_to_taken_name_rejected(self, tmp_path, home, lines):
        go(make_book(tmp_path, "a"), lines)
        go(make_book(tmp_path, "b"), lines)
        with pytest.raises(RunnerError, match="already taken"):
            rename_job("a", "b")


class TestHistory:
    def test_jobs_json_shape(self, tmp_path, home, lines):
        go(make_book(tmp_path), lines)
        data = json.loads(jobs_path().read_text(encoding="utf-8"))
        job = data["jobs"][0]
        assert set(job) == {"name", "source", "output", "runs"}
        assert job["source"] == str((tmp_path / "novel.txt").resolve())
        run = job["runs"][0]
        assert set(run) == {"date", "settings", "status", "steps", "log", "errors"}
        assert run["settings"] == {"ssml": False, "fiction": True}
        assert run["log"][-1] == "ready for audio — paused before paid step"

    def test_missing_folder_listed_as_missing(self, tmp_path, home, lines):
        go(make_book(tmp_path), lines)
        import shutil
        shutil.rmtree(tmp_path / "novel_sawt")
        row = list_jobs()[0]
        assert row["missing"] and row["status"] == "missing"

    def test_write_is_atomic(self, home, monkeypatch):
        save_jobs({"jobs": [{"name": "orig"}]})
        before = jobs_path().read_text()

        def die(*a, **k):
            raise OSError("disk gone")
        monkeypatch.setattr(os, "replace", die)
        with pytest.raises(OSError):
            save_jobs({"jobs": [{"name": "new"}]})
        assert jobs_path().read_text() == before
        assert [p.name for p in home.iterdir()] == ["jobs.json"]  # no temp file left behind

    def test_corrupt_history_is_not_overwritten(self, tmp_path, home, lines):
        home.mkdir()
        jobs_path().write_text("{not json")
        with pytest.raises(RunnerError, match="unreadable"):
            go(make_book(tmp_path), lines)
        assert jobs_path().read_text() == "{not json"


class TestImport:
    def _tree(self, root: Path):
        for fmt, book, dirs in [
            ("epub", "alpha", ["01_ingestion", "02_chapters", "03_segments", "04_ssml"]),
            ("txt", "beta", ["01_ingestion", "02_chapters"]),
            ("pdf", "gamma", ["01_ingestion"]),
            ("docx", "empty", []),
        ]:
            (root / fmt / book).mkdir(parents=True)
            for d in dirs:
                (root / fmt / book / d).mkdir()
                (root / fmt / book / d / "f.txt").write_text("x")

    def test_import_in_place_and_idempotent(self, tmp_path, home):
        out = tmp_path / "output"
        self._tree(out)
        res = import_existing(out, tmp_path / "books")
        assert res["imported"] == ["alpha", "beta"]  # pdf out of scope, empty dir ignored
        jobs = {j["name"]: j for j in json.loads(jobs_path().read_text())["jobs"]}
        assert jobs["alpha"]["output"] == str((out / "epub" / "alpha").resolve())
        assert (out / "epub" / "alpha" / "01_ingestion" / "f.txt").exists()  # not moved
        assert jobs["alpha"]["runs"][0]["steps"] == {s: "ok" for s in runner_core.STEPS}
        assert jobs["beta"]["runs"][0]["steps"]["dialogue"] == "skipped"
        assert jobs["alpha"]["runs"][0]["status"] == "imported"
        again = import_existing(out, tmp_path / "books")
        assert again["imported"] == [] and len(again["skipped"]) == 2
        assert len(list_jobs()) == 2

    def test_cli_import(self, tmp_path, home, lines):
        out = tmp_path / "output"
        self._tree(out)
        assert main(["--import-existing", str(out)], emit=lines.append) == 0
        assert lines[0] == "imported 2 job(s)"
        lines.clear()
        main(["--list"], emit=lines.append)
        assert len(lines) == 2 and "[imported]" in lines[0]
