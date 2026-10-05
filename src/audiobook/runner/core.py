"""Module 0: pipeline runner.

Chains the four mechanical stages (ingest → chapters → dialogue → ssml) for a
book, writes the output next to the source in ``<job name>_sawt/``, and keeps
one history file (``jobs.json``) with every run of every job.

Stages stay isolated by data: the runner only calls each stage's entry point
with explicit directories, and a retry reads nothing but the files already on
disk. The runner is the single writer of ``jobs.json``.
"""

import argparse
import json
import logging
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, TypedDict

from ..chapters import split_book
from ..dialogue import segment_book
from ..ingest import EXTRACTORS, ingest
from ..ssml import generate_book_ssml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STEPS = ("ingest", "chapters", "dialogue", "ssml")
STEP_DIRS = {
    "ingest": "01_ingestion",
    "chapters": "02_chapters",
    "dialogue": "03_segments",
    "ssml": "04_ssml",
}
STEP_LABELS = {
    "ingest": "ingesting",
    "chapters": "splitting chapters",
    "dialogue": "detecting dialogue",
    "ssml": "generating SSML",
}

STEP_OK = "ok"
STEP_FAILED = "failed"
STEP_SKIPPED = "skipped"
STEP_PENDING = "pending"
STEP_RUNNING = "running"

RUN_READY = "ready for audio — paused"
RUN_FAILED = "failed"
RUN_RUNNING = "running"
RUN_IMPORTED = "imported"

JOB_DIR_SUFFIX = "_sawt"
HOME_ENV = "SAWT_HOME"
DEFAULT_HOME = Path.home() / ".config" / "sawt"
JOBS_FILE = "jobs.json"

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "output"
DEFAULT_BOOKS_ROOT = REPO_ROOT / "data" / "books"
IMPORT_FORMATS = ("epub", "docx", "txt")  # pdf is out of scope

OVERWRITE_WARNING = (
    "overwriting the last run's files — start a new job instead to keep them"
)
GATE_LINE = "ready for audio — paused before paid step"


# ---------------------------------------------------------------------------
# Types and errors
# ---------------------------------------------------------------------------


class RunnerError(ValueError):
    """A runner-level rejection (bad path, duplicate name, nothing to retry…)."""


class Settings(TypedDict):
    ssml: bool
    fiction: bool


class Run(TypedDict):
    date: str
    settings: Settings
    status: str
    steps: dict[str, str]
    log: list[str]
    errors: list[dict]


class Job(TypedDict):
    name: str
    source: str
    output: str
    runs: list[Run]


Emit = Callable[[str], None]


def _stdout(line: str) -> None:
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def _ask(prompt: str) -> bool:
    try:
        return input(prompt).strip().lower() in ("y", "yes")
    except EOFError:
        return False


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# History file (single writer, atomic)
# ---------------------------------------------------------------------------


def jobs_path() -> Path:
    """Location of jobs.json; ``SAWT_HOME`` overrides ``~/.config/sawt``."""
    home = os.environ.get(HOME_ENV)
    return (Path(home) if home else DEFAULT_HOME) / JOBS_FILE


def load_jobs() -> dict:
    path = jobs_path()
    if not path.exists():
        return {"jobs": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data.get("jobs"), list):
            raise ValueError("missing 'jobs' list")
    except (ValueError, AttributeError) as exc:
        raise RunnerError(f"{path} is unreadable ({exc}); fix or remove it") from exc
    return data


def save_jobs(data: dict) -> None:
    """Write jobs.json atomically: temp file in the same folder, then rename."""
    path = jobs_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".jobs-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _find_job(data: dict, name: str) -> Job | None:
    return next((j for j in data["jobs"] if j["name"] == name), None)


def free_job_name(data: dict, stem: str, reserved: Iterable[str] = ()) -> str:
    """``stem`` if no job (or reserved name) uses it, else the first free ``stem-2``, ``stem-3``, ..."""
    used = {j["name"] for j in data["jobs"]} | set(reserved)
    name, n = stem, 1
    while name in used:
        n += 1
        name = f"{stem}-{n}"
    return name


# ---------------------------------------------------------------------------
# Input scanning
# ---------------------------------------------------------------------------


def _reject_reason(path: Path) -> str | None:
    """Why a file cannot be run, or None if it can."""
    suffix = path.suffix.lower()
    if suffix == ".doc":
        return "legacy .doc is not supported — save it as .docx and run that"
    if suffix not in EXTRACTORS:
        return f"unsupported format (supported: {', '.join(sorted(EXTRACTORS))})"
    return None


def scan_path(path: str) -> tuple[list[Path], list[tuple[Path, str]]]:
    """Resolve a file or folder into (books to run, skipped files with reasons).

    A folder is scanned one level deep; hidden files and sub-folders are ignored.
    A single file that cannot be run is an error, not a skip.
    """
    p = Path(path).expanduser()
    if not p.exists():
        raise RunnerError(f"path not found: {path}")
    if p.is_file():
        reason = _reject_reason(p)
        if reason:
            raise RunnerError(f"{p.name}: {reason}")
        return [p.resolve()], []
    books, skipped = [], []
    for f in sorted(p.iterdir()):
        if not f.is_file() or f.name.startswith("."):
            continue
        reason = _reject_reason(f)
        if reason:
            skipped.append((f, reason))
        else:
            books.append(f.resolve())
    return books, skipped


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------


def _step_ingest(job: Job, run: Run) -> list[str]:
    s = ingest(job["source"], ingestion_dir=str(Path(job["output"]) / STEP_DIRS["ingest"]))
    return [f"{s['paragraph_count']:,} paragraphs, {s['total_chars']:,} chars"]


def _step_chapters(job: Job, run: Run) -> list[str]:
    out = Path(job["output"])
    s = split_book(str(out / STEP_DIRS["ingest"]), str(out / STEP_DIRS["chapters"]))
    how = "size-based fallback" if s["delimiter_type"].startswith("none") else f"by {s['delimiter_type']}"
    return [f"{s['total_units']} chapters ({how})"]


def _step_dialogue(job: Job, run: Run) -> list[str]:
    out = Path(job["output"])
    s = segment_book(str(out / STEP_DIRS["chapters"]), str(out / STEP_DIRS["dialogue"]))
    return [f"{s['total_segments']:,} segments, {s['dialogue_ratio'] * 100:.0f}% dialogue"]


def _step_ssml(job: Job, run: Run) -> list[str]:
    out = Path(job["output"])
    s = generate_book_ssml(str(out / STEP_DIRS["dialogue"]), str(out / STEP_DIRS["ssml"]))
    return [f"{s['total_chapters']} SSML files, {s['total_segments']:,} segments"]


_STEP_FUNCS = {
    "ingest": _step_ingest,
    "chapters": _step_chapters,
    "dialogue": _step_dialogue,
    "ssml": _step_ssml,
}


def _skip_reason(step: str, settings: Settings) -> str | None:
    if step == "ssml":
        if not settings["ssml"]:
            return "skipped (off)"
        if not settings["fiction"]:
            return "skipped (non-fiction: SSML needs dialogue segments)"
    if step == "dialogue" and not settings["fiction"]:
        return "skipped (non-fiction)"
    return None


def _say(run: Run, emit: Emit, line: str) -> None:
    run["log"].append(line)
    emit(line)


def _execute(data: dict, job: Job, run: Run, first_step: str, emit: Emit = _stdout) -> bool:
    """Run steps from ``first_step`` on. Saves history after every step.

    Returns True if the run reached the gate, False if a step failed.
    """
    out = Path(job["output"])
    for step in STEPS[STEPS.index(first_step):]:
        label = STEP_LABELS[step]
        reason = _skip_reason(step, run["settings"])
        if reason:
            run["steps"][step] = STEP_SKIPPED
            _say(run, emit, f"{label} — {reason}")
            save_jobs(data)
            continue
        shutil.rmtree(out / STEP_DIRS[step], ignore_errors=True)  # this step's own partial output
        run["steps"][step] = STEP_RUNNING
        save_jobs(data)
        try:
            details = _STEP_FUNCS[step](job, run)
        except (Exception, KeyboardInterrupt) as exc:
            message = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
            run["steps"][step] = STEP_FAILED
            run["status"] = RUN_FAILED
            run["errors"].append({"step": step, "message": message})
            _say(run, emit, f"✗ {label} — {message}")
            save_jobs(data)
            if isinstance(exc, KeyboardInterrupt):
                raise
            return False
        run["steps"][step] = STEP_OK
        _say(run, emit, f"✓ {label}")
        for d in details:
            _say(run, emit, f"  > {d}")
        save_jobs(data)
    run["status"] = RUN_READY
    _say(run, emit, GATE_LINE)
    save_jobs(data)
    return True


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------


def _check_name(name: str) -> None:
    if not name or name.startswith(".") or "/" in name or "\\" in name:
        raise RunnerError(f"invalid job name {name!r}")


def _resolve_job(data: dict, book: Path, name: str | None, new_job: bool) -> tuple[Job | None, str]:
    """Pick the existing job to re-run, or return (None, name) for a new one."""
    source = str(book)
    chosen = name or book.stem
    _check_name(chosen)
    same_source = [j for j in data["jobs"] if j["source"] == source]
    if new_job:
        if _find_job(data, chosen):
            raise RunnerError(f"job name {chosen!r} is already taken — pick another with --name")
        return None, chosen
    if same_source:
        job = next((j for j in same_source if j["name"] == chosen), same_source[0])
        if name and job["name"] != name:
            raise RunnerError(
                f"this book already has job {job['name']!r}; "
                f"re-run it (--name {job['name']}) or use --new-job"
            )
        return job, job["name"]
    if _find_job(data, chosen):
        raise RunnerError(f"job name {chosen!r} is already taken by another book — pick another with --name")
    return None, chosen


def _new_run(settings: Settings) -> Run:
    return {
        "date": _now(),
        "settings": settings,
        "status": RUN_RUNNING,
        "steps": {s: STEP_PENDING for s in STEPS},
        "log": [],
        "errors": [],
    }


def run_book(
    book: Path,
    *,
    name: str | None = None,
    fiction: bool = True,
    ssml: bool = False,
    new_job: bool = False,
    assume_yes: bool = False,
    confirm: Callable[[str], bool] = _ask,
    emit: Emit = _stdout,
) -> Run | None:
    """Run steps 1-4 on one book. Returns the run, or None if the user declined the overwrite."""
    data = load_jobs()
    job, job_name = _resolve_job(data, book, name, new_job)
    if job is None:
        output = book.parent / f"{job_name}{JOB_DIR_SUFFIX}"
        if any(j["output"] == str(output) for j in data["jobs"]):
            raise RunnerError(f"output folder {output} already belongs to another job")
        job = {"name": job_name, "source": str(book), "output": str(output), "runs": []}
        data["jobs"].append(job)
    else:
        out = Path(job["output"])
        if any((out / d).exists() for d in STEP_DIRS.values()):
            emit(f"warning: {OVERWRITE_WARNING}")
            if not assume_yes and not confirm("continue? [y/N] "):
                emit("not confirmed — nothing changed")
                return None

    run = _new_run({"ssml": ssml, "fiction": fiction})
    job["runs"].append(run)
    out = Path(job["output"])
    for d in STEP_DIRS.values():
        shutil.rmtree(out / d, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    emit(f"job {job['name']}: {job['source']} → {out}")
    _execute(data, job, run, STEPS[0], emit)
    return run


def retry_job(name: str, emit: Emit = _stdout) -> Run:
    """Resume the job's latest failed run from its failed step, using files on disk only."""
    data = load_jobs()
    job = _find_job(data, name)
    if job is None:
        raise RunnerError(f"no job named {name!r}")
    run = job["runs"][-1] if job["runs"] else None
    if run is None or run["status"] not in (RUN_FAILED, RUN_RUNNING):
        raise RunnerError(f"job {name!r}: nothing to retry (latest run is not failed)")
    first = next(s for s in STEPS if run["steps"][s] not in (STEP_OK, STEP_SKIPPED))
    out = Path(job["output"])
    if first == "ingest":
        if not Path(job["source"]).is_file():
            raise RunnerError(f"source file is gone: {job['source']}")
    else:
        needed = out / STEP_DIRS[STEPS[STEPS.index(first) - 1]]
        if not needed.is_dir():
            raise RunnerError(f"cannot retry: {needed} is missing — start a new run")
    for s in STEPS[STEPS.index(first):]:
        if run["steps"][s] != STEP_SKIPPED:
            run["steps"][s] = STEP_PENDING
    run["status"] = RUN_RUNNING
    emit(f"job {job['name']}: retrying from {STEP_LABELS[first]}")
    _say(run, emit, f"retry {_now()}: from {STEP_LABELS[first]}")
    _execute(data, job, run, first, emit)
    return run


def rename_job(old: str, new: str) -> None:
    """Change the job's label only; its output folder name stays fixed."""
    _check_name(new)
    data = load_jobs()
    job = _find_job(data, old)
    if job is None:
        raise RunnerError(f"no job named {old!r}")
    if _find_job(data, new):
        raise RunnerError(f"job name {new!r} is already taken")
    job["name"] = new
    save_jobs(data)


def list_jobs() -> list[dict]:
    """One row per job: name, status of the latest run, date, run count, output, missing flag."""
    rows = []
    for job in load_jobs()["jobs"]:
        last = job["runs"][-1] if job["runs"] else None
        missing = not Path(job["output"]).is_dir()
        rows.append({
            "name": job["name"],
            "status": "missing" if missing else (last["status"] if last else "no runs"),
            "date": last["date"] if last else "",
            "runs": len(job["runs"]),
            "output": job["output"],
            "missing": missing,
        })
    return rows


def import_existing(
    output_root: Path = DEFAULT_OUTPUT_ROOT, books_root: Path = DEFAULT_BOOKS_ROOT
) -> dict:
    """Add the books already under ``output_root/{format}/{book}/`` to history, in place."""
    data = load_jobs()
    imported, skipped = [], []
    for fmt in IMPORT_FORMATS:
        fmt_dir = Path(output_root) / fmt
        if not fmt_dir.is_dir():
            continue
        for book_dir in sorted(p for p in fmt_dir.iterdir() if p.is_dir()):
            present = {s: (book_dir / d).is_dir() for s, d in STEP_DIRS.items()}
            if not any(present.values()):
                continue
            name = book_dir.name
            if _find_job(data, name):
                skipped.append((name, "already in history"))
                continue
            src = Path(books_root) / fmt / f"{name}.{fmt}"
            mtime = max((book_dir / STEP_DIRS[s]).stat().st_mtime for s, ok in present.items() if ok)
            data["jobs"].append({
                "name": name,
                "source": str(src.resolve()) if src.is_file() else "",
                "output": str(book_dir.resolve()),
                "runs": [{
                    "date": datetime.fromtimestamp(mtime).isoformat(timespec="seconds"),
                    "settings": {"ssml": present["ssml"], "fiction": present["dialogue"]},
                    "status": RUN_IMPORTED,
                    "steps": {s: STEP_OK if ok else STEP_SKIPPED for s, ok in present.items()},
                    "log": ["imported from existing output (in place)"],
                    "errors": [],
                }],
            })
            imported.append(name)
    save_jobs(data)
    return {"imported": imported, "skipped": skipped}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m src.audiobook.runner",
        description="Run steps 1-4 (ingest, chapters, dialogue, SSML) on a book or folder of books.",
    )
    p.add_argument("path", nargs="?", help="book file (.epub/.docx/.txt) or folder of books")
    p.add_argument("--ssml", action="store_true", help="also generate SSML (off by default)")
    p.add_argument("--non-fiction", action="store_true",
                   help="skip dialogue detection (and so SSML, which needs its segments)")
    p.add_argument("--name", help="job name (default: the book's file name)")
    p.add_argument("--new-job", action="store_true", help="new job for a book that already has one")
    p.add_argument("--yes", action="store_true", help="skip the overwrite confirmation")
    p.add_argument("--retry", metavar="JOB", help="resume a failed job from its failed step")
    p.add_argument("--list", action="store_true", help="list jobs")
    p.add_argument("--rename", nargs=2, metavar=("OLD", "NEW"), help="change a job's label")
    p.add_argument("--import-existing", nargs="?", const=str(DEFAULT_OUTPUT_ROOT), metavar="DIR",
                   help="import books already under DIR/{epub,docx,txt}/ (default: repo output/)")
    return p


def _print_list(emit: Emit) -> None:
    rows = list_jobs()
    if not rows:
        emit("no jobs yet")
    for r in rows:
        emit(f"{r['name']}  [{r['status']}]  {r['date']}  {r['runs']} run(s)  {r['output']}")


def main(argv: list[str] | None = None, emit: Emit = _stdout) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    actions = [bool(args.path), bool(args.retry), args.list, bool(args.rename),
               args.import_existing is not None]
    if sum(actions) != 1:
        parser.error("give exactly one of: PATH, --retry, --list, --rename, --import-existing")

    try:
        if args.list:
            _print_list(emit)
            return 0
        if args.rename:
            rename_job(*args.rename)
            emit(f"renamed {args.rename[0]} → {args.rename[1]} (output folder unchanged)")
            return 0
        if args.import_existing is not None:
            result = import_existing(Path(args.import_existing))
            emit(f"imported {len(result['imported'])} job(s)")
            for name, why in result["skipped"]:
                emit(f"  skipped {name}: {why}")
            return 0
        if args.retry:
            run = retry_job(args.retry, emit)
            return 0 if run["status"] == RUN_READY else 1

        books, skipped = scan_path(args.path)
        for f, why in skipped:
            emit(f"skipped {f.name}: {why}")
        if len(books) > 1 and (args.name or args.new_job):
            raise RunnerError("--name and --new-job apply to a single book, not a folder")
        if not books:
            raise RunnerError("no runnable books found")
    except RunnerError as exc:
        emit(f"error: {exc}")
        return 2

    rc = 0
    for book in books:
        try:
            run = run_book(
                book, name=args.name, fiction=not args.non_fiction, ssml=args.ssml,
                new_job=args.new_job, assume_yes=args.yes, emit=emit,
            )
        except RunnerError as exc:
            emit(f"error: {book.name}: {exc}")
            rc = 1
            continue
        if run is None or run["status"] != RUN_READY:
            rc = 1
    return rc
