"""Module 2: local UI shell.

A stdlib ``http.server`` on 127.0.0.1 that serves one inline page and a small
JSON API over the runner's public functions. The runner stays the single writer
of ``jobs.json``: runs execute on one worker thread, and anything else that
writes (rename, import) is refused while the worker is busy.
"""

import argparse
import json
import logging
import re
import threading
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from ..runner import (
    OVERWRITE_WARNING, RUN_FAILED, RUN_RUNNING, STEP_DIRS, RunnerError,
    import_existing, list_jobs, load_jobs, rename_job, retry_job, run_book, scan_path,
)
from ..runner.core import _resolve_job
from .page import PAGE

__all__ = ["make_server", "serve", "main"]

logger = logging.getLogger(__name__)

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_BODY_BYTES = 64 * 1024
LOCAL_HOSTNAMES = ("127.0.0.1", "localhost")

# The page is one inline document; fonts come from Google Fonts, everything else is local.
PAGE_CSP = (
    "default-src 'none'; script-src 'unsafe-inline'; "
    "style-src 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src https://fonts.gstatic.com; connect-src 'self'"
)

_JOB_ROUTE = re.compile(r"^/api/jobs/([^/]+)(?:/(retry|rename))?$")


# ---------------------------------------------------------------------------
# Worker: one run at a time
# ---------------------------------------------------------------------------


class _Worker:
    """Runs queued tasks one after another on a single background thread."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self._tasks: deque = deque()  # (job name, callable) not yet started
        self._current: str | None = None
        self._error: dict | None = None  # last failure that could not be reported synchronously
        self._wake = threading.Condition(self.lock)
        threading.Thread(target=self._loop, daemon=True, name="sawt-ui-worker").start()

    def _busy(self) -> bool:  # caller holds the lock
        return self._current is not None or bool(self._tasks)

    def status(self) -> dict:
        with self.lock:
            return {
                "busy": self._busy(),
                "current": self._current,
                "queued": [name for name, _ in self._tasks],
                "error": self._error,
            }

    def submit(self, tasks: list[tuple[str, object]]) -> bool:
        """Queue tasks atomically; False (nothing queued) if a run is already active."""
        with self.lock:
            if self._busy():
                return False
            self._error = None
            self._tasks.extend(tasks)
            self._wake.notify()
            return True

    def _loop(self) -> None:
        while True:
            with self.lock:
                while not self._tasks:
                    self._wake.wait()
                name, task = self._tasks.popleft()
                self._current = name
            try:
                task()
            except RunnerError as exc:
                logger.warning("job %s: %s", name, exc)
                self._fail(name, str(exc))
            except Exception as exc:  # a stage bug must not kill the worker
                logger.exception("job %s crashed", name)
                self._fail(name, f"{type(exc).__name__}: {exc}")
            finally:
                with self.lock:
                    self._current = None

    def _fail(self, name: str, message: str) -> None:
        with self.lock:
            self._error = {"job": name, "message": message}


# ---------------------------------------------------------------------------
# Request handling
# ---------------------------------------------------------------------------


class _HttpError(Exception):
    def __init__(self, status: int, payload: dict) -> None:
        super().__init__(payload.get("error", ""))
        self.status = status
        self.payload = payload


def _bad(message: str, field: str | None = None, **extra) -> _HttpError:
    payload = {"error": message, **extra}
    if field:
        payload["field"] = field
    return _HttpError(400, payload)


class _Handler(BaseHTTPRequestHandler):
    server_version = "sawt-ui"

    def log_message(self, fmt, *args) -> None:  # noqa: D401 - quiet access log
        logger.debug("%s %s", self.address_string(), fmt % args)

    # -- plumbing ----------------------------------------------------------

    def _send(self, status: int, body: bytes, ctype: str, extra: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8")

    def _host_ok(self) -> bool:
        """DNS-rebinding guard: only our own 127.0.0.1/localhost:port names are served."""
        host = self.headers.get("Host", "")
        return any(host == f"{name}:{self.server.server_port}" for name in LOCAL_HOSTNAMES)

    def _body(self) -> dict:
        if (self.headers.get("Content-Type") or "").split(";")[0].strip().lower() != "application/json":
            raise _HttpError(415, {"error": "POST requires Content-Type: application/json"})
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            raise _bad("bad Content-Length") from None
        if length > MAX_BODY_BYTES:
            raise _HttpError(413, {"error": "request body too large"})
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            raise _bad("body is not valid JSON") from None
        if not isinstance(data, dict):
            raise _bad("body must be a JSON object")
        return data

    def _dispatch(self, method: str) -> None:
        if not self._host_ok():
            return self._json(403, {"error": "forbidden host"})
        try:
            path = urlsplit(self.path).path
            if method == "GET" and path == "/":
                return self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8",
                                  {"Content-Security-Policy": PAGE_CSP})
            status, payload = self._route(method, path)
            self._json(status, payload)
        except _HttpError as exc:
            self._json(exc.status, exc.payload)
        except RunnerError as exc:  # e.g. unreadable jobs.json
            self._json(500, {"error": str(exc)})
        except Exception:
            logger.exception("unhandled error on %s %s", method, self.path)
            self._json(500, {"error": "internal error"})

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch("POST")

    # -- routes ------------------------------------------------------------

    def _route(self, method: str, path: str) -> tuple[int, dict]:
        worker: _Worker = self.server.worker
        if method == "GET":
            if path == "/api/jobs":
                return 200, {"jobs": _sorted_rows(list_jobs())}
            if path == "/api/status":
                return 200, worker.status()
            m = _JOB_ROUTE.match(path)
            if m and not m.group(2):
                return 200, _job_detail(unquote(m.group(1)))
        elif method == "POST":
            if path == "/api/runs":
                return self._post_runs(worker, self._body())
            if path == "/api/import":
                self._body()
                with worker.lock:
                    self._refuse_if_busy(worker)
                    result = import_existing()
                return 200, {"imported": result["imported"],
                             "skipped": [{"job": n, "reason": r} for n, r in result["skipped"]]}
            m = _JOB_ROUTE.match(path)
            if m and m.group(2) == "retry":
                self._body()
                return self._post_retry(worker, unquote(m.group(1)))
            if m and m.group(2) == "rename":
                return self._post_rename(worker, unquote(m.group(1)), self._body())
        raise _HttpError(404, {"error": "not found"})

    @staticmethod
    def _refuse_if_busy(worker: _Worker) -> None:  # caller holds worker.lock
        if worker._busy():
            raise _HttpError(409, {"busy": True, "error": "a run is in progress — wait for it to end"})

    def _post_runs(self, worker: _Worker, body: dict) -> tuple[int, dict]:
        raw_path = body.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise _bad("path is required: absolute path to a book file or folder", "path")
        raw_path = raw_path.strip()
        if not Path(raw_path).expanduser().is_absolute():
            raise _bad("use an absolute path (starts with / or ~)", "path")
        name = body.get("name")
        if name is not None and not isinstance(name, str):
            raise _bad("name must be text", "name")
        name = (name or "").strip() or None
        fiction, ssml = body.get("fiction", True) is not False, body.get("ssml", False) is True
        new_job, confirm = body.get("newJob", False) is True, body.get("confirm", False) is True

        try:
            books, skipped = scan_path(raw_path)
        except RunnerError as exc:
            raise _bad(str(exc), "path") from None
        skipped_out = [{"file": f.name, "reason": why} for f, why in skipped]
        if not books:
            raise _bad("no runnable books found", "path", skipped=skipped_out)
        if name and Path(raw_path).expanduser().is_dir():
            raise _bad("name applies to a single book, not a folder", "name", skipped=skipped_out)

        data = load_jobs()
        plan, taken = [], set()  # (book, resolved name, existing job)
        for book in books:
            try:
                job, job_name = _resolve_job(data, book, name, new_job)
            except RunnerError as exc:
                if len(books) > 1:  # one bad book must not block the rest of the folder
                    skipped_out.append({"file": book.name, "reason": str(exc)})
                    continue
                raise _bad(str(exc), "name" if (name or new_job) else "path", skipped=skipped_out) from None
            if job is None and job_name in taken:
                skipped_out.append({"file": book.name,
                                    "reason": f"job name {job_name!r} is already used by another book in this folder"})
                continue
            taken.add(job_name)
            plan.append((book, job_name, job))

        if not plan:
            raise _bad("no runnable books found", "path", skipped=skipped_out)

        # Check busy before asking for any confirmation: there is no point confirming a run that can't start.
        if worker.status()["busy"]:
            raise _HttpError(409, {"busy": True, "error": "a run is in progress — wait for it to end"})
        existing = [n for _, n, j in plan if j and any((Path(j["output"]) / d).exists() for d in STEP_DIRS.values())]
        if existing and not confirm:
            raise _HttpError(409, {"overwrite": True, "message": OVERWRITE_WARNING, "jobs": existing})

        def make(book: Path, job_name: str):
            return lambda: run_book(book, name=job_name, fiction=fiction, ssml=ssml,
                                    new_job=new_job, assume_yes=True, emit=logger.info)

        if not worker.submit([(n, make(b, n)) for b, n, _ in plan]):
            raise _HttpError(409, {"busy": True, "error": "a run is in progress — wait for it to end"})
        return 202, {"queued": [n for _, n, _ in plan], "skipped": skipped_out}

    def _post_retry(self, worker: _Worker, name: str) -> tuple[int, dict]:
        job = next((j for j in load_jobs()["jobs"] if j["name"] == name), None)
        if job is None:
            raise _HttpError(404, {"error": f"no job named {name!r}"})
        last = job["runs"][-1] if job["runs"] else None
        if last is None or last["status"] not in (RUN_FAILED, RUN_RUNNING):
            raise _bad(f"job {name!r}: nothing to retry (latest run is not failed)")
        if not worker.submit([(name, lambda: retry_job(name, emit=logger.info))]):
            raise _HttpError(409, {"busy": True, "error": "a run is in progress — wait for it to end"})
        return 202, {"queued": [name]}

    def _post_rename(self, worker: _Worker, old: str, body: dict) -> tuple[int, dict]:
        new = body.get("name")
        if not isinstance(new, str):
            raise _bad("name is required", "name")
        with worker.lock:  # jobs.json has one writer: never rename while a run is saving
            self._refuse_if_busy(worker)
            try:
                rename_job(old, new.strip())
            except RunnerError as exc:
                if str(exc).startswith("no job named"):
                    raise _HttpError(404, {"error": str(exc)}) from None
                raise _bad(str(exc), "name") from None
        return 200, {"name": new.strip()}


def _sorted_rows(rows: list[dict]) -> list[dict]:
    """Newest first by latest-run date (jobs without runs last); ties by name."""
    return sorted(sorted(rows, key=lambda r: r["name"]), key=lambda r: r["date"], reverse=True)


def _job_detail(name: str) -> dict:
    job = next((j for j in load_jobs()["jobs"] if j["name"] == name), None)
    if job is None:
        raise _HttpError(404, {"error": f"no job named {name!r}"})
    return {**job, "missing": not Path(job["output"]).is_dir()}


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------


class _Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, port: int) -> None:
        super().__init__((HOST, port), _Handler)
        self.worker = _Worker()


def make_server(port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    """A server bound to 127.0.0.1 only (``port=0`` picks a free port)."""
    return _Server(port)


def serve(port: int = DEFAULT_PORT, open_browser: bool = True) -> None:
    server = make_server(port)
    url = f"http://{HOST}:{server.server_port}/"
    logger.info("sawt ui on %s (ctrl-c to stop)", url)
    if open_browser:
        threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m src.audiobook.ui",
                                description="Local UI for the Sawt runner (127.0.0.1 only).")
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--no-open", action="store_true", help="do not open a browser tab")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        serve(args.port, open_browser=not args.no_open)
    except OSError as exc:
        logger.error("cannot start on port %s: %s", args.port, exc)
        return 1
    return 0
