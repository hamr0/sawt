"""POC 4: SSML generation + voice selection."""
from .core import (  # noqa: F401
    SEGMENT_COLUMNS,
    VOICE_INVENTORY,
    VoiceConfig,
    build_ssml,
    generate_book_ssml,
    generate_chapter_ssml,
    make_voice_config,
)
