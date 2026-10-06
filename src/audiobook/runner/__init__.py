"""Module 0: pipeline runner (CLI) — chains steps 1-4 per book, keeps job history."""
from .core import *  # noqa: F403
from .core import _execute, _reject_reason  # Export private for tests
