"""POC 3: Dialogue detection and segmentation."""
from .core import *  # noqa: F403
from .core import (  # Export private for tests
    _find_dialogue_colon,
    _split_at_colon,
    _split_at_review_markers,
    _segments_to_review_text,
    _has_speech_attribution,
    _has_trailing_speech,
    _strip_diacritics,
)
