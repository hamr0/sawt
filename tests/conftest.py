"""Session-wide guard: no test may ever read or write the real ~/.config/sawt/jobs.json.

SAWT_HOME points at a session tmp dir for the whole run, so a straggler thread (e.g. a UI
worker still saving after its test's monkeypatch is undone) can never fall back to the real
home. Per-test ``home`` fixtures still override it. At session end the real file must be unchanged.
"""
import hashlib
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from src.audiobook.runner.core import DEFAULT_HOME, HOME_ENV, JOBS_FILE


def _fingerprint(path: Path):
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns


@pytest.fixture(scope="session", autouse=True)
def _isolated_sawt_home():
    real = DEFAULT_HOME / JOBS_FILE
    before = _fingerprint(real)
    previous = os.environ.get(HOME_ENV)
    tmp = tempfile.mkdtemp(prefix="sawt_session_home_")
    os.environ[HOME_ENV] = tmp
    try:
        yield Path(tmp)
    finally:
        if previous is None:
            os.environ.pop(HOME_ENV, None)
        else:
            os.environ[HOME_ENV] = previous
        shutil.rmtree(tmp, ignore_errors=True)
    after = _fingerprint(real)
    assert after == before, f"tests modified the real {real}"
