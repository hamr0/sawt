"""
Positional Allophone Processor for Arabic TTS
Handles position-dependent pronunciation variants (allophones)

Allophones are variants of a phoneme that occur in specific positions:
- Initial position (word-initial): Beginning of word
- Medial position (word-medial): Middle of word
- Final position (word-final): End of word

Example: ء (hamza)
- Initial: [ʔ] - أكل → [ʔakl]
- Medial: ∅ (deleted in casual speech) - سأل → [sal]
- Final: [ʔ] - ماء → [maːʔ]

This is the THIRD phonological rule in the processing pipeline.
Applied after gemination and sun letter assimilation.
"""
import json
import warnings
from typing import List, Dict, Optional
from pathlib import Path


class AllophoneProcessor:
    """
    DEPRECATED: This class is deprecated.

    Use PositionDetector + IPAMapper instead:
    - PositionDetector for position detection (universal)
    - IPAMapper for IPA generation (dialect-specific)

    This class kept for backward compatibility only.

    Migration example:

        # Old (deprecated):
        processor = AllophoneProcessor(dialect="EG")
        processor.process(syllables)

        # New (recommended):
        pos_detector = PositionDetector()
        ipa_mapper = IPAMapper()

        syllables = pos_detector.detect_positions(syllables)
        ipa = ipa_mapper.map_to_ipa(syllables, dialect="EG")
    """

    def __init__(self, dialect: Optional[str] = None, master_tts_path: Optional[str] = None):
        """
        Initialize AllophoneProcessor.

        WARNING: This class is deprecated. Use PositionDetector + IPAMapper.

        Args:
            dialect: (Deprecated) Dialect code - not used
            master_tts_path: (Deprecated) Path to masterTTS.json - not used
        """
        # Issue deprecation warning
        warnings.warn(
            "AllophoneProcessor is deprecated. "
            "Use PositionDetector for position detection "
            "and IPAMapper for IPA mapping.",
            DeprecationWarning,
            stacklevel=2
        )

        # Initialize new components for delegation
        from .position_detector import PositionDetector
        from .ipa_mapper import IPAMapper

        self.position_detector = PositionDetector()
        self.ipa_mapper = IPAMapper(master_tts_path)

        # Store dialect locally for use in process() but don't expose as attribute
        self._dialect = dialect

        # Diacritics to skip during character processing
        self.diacritics = {'َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٓ'}
    
    def process(self, syllables: List[Dict], word_text: str = "") -> List[Dict]:
        """
        Process syllables using the new architecture (delegated to components).

        This method now delegates to:
        1. PositionDetector for position detection
        2. IPAMapper for IPA generation (if dialect specified)

        Args:
            syllables: List of syllable dictionaries
            word_text: Full word text for context (optional)

        Returns:
            Syllables with detected position and IPA information
        """
        # Use PositionDetector to detect positions
        syllables = self.position_detector.detect_positions(syllables)

        # For backward compatibility, also get IPA from IPAMapper
        # (This allows existing code to continue working)
        if self._dialect:
            for i, syll in enumerate(syllables):
                ipa = self.ipa_mapper.get_ipa_for_char(
                    syll.get('syllable', ''),
                    self._dialect,
                    syll.get('detected_position', 'default')
                )
                syll['ipa'] = ipa

        return syllables

    def detect_positions(self, syllables: List[Dict], word_text: str = "") -> List[Dict]:
        """
        Detect positions in syllables (delegated to PositionDetector).

        Args:
            syllables: List of syllable dictionaries
            word_text: Full word text for context (optional)

        Returns:
            Syllables with detected position information
        """
        return self.position_detector.detect_positions(syllables)

    def get_ipa_mapping(self, syllables: List[Dict], dialect: str) -> List[Dict]:
        """
        Get IPA mapping for syllables (delegated to IPAMapper).

        Args:
            syllables: List of syllable dictionaries
            dialect: Target dialect code

        Returns:
            Syllables with IPA information added
        """
        for i, syll in enumerate(syllables):
            ipa = self.ipa_mapper.get_ipa_for_char(
                syll.get('syllable', ''),
                dialect,
                syll.get('detected_position', 'default')
            )
            syll['ipa'] = ipa
        return syllables


if __name__ == "__main__":
    # Quick test
    import warnings

    # Suppress deprecation warning for demo
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        processor = AllophoneProcessor()

    print("Testing DEPRECATED AllophoneProcessor")
    print("=" * 70)
    print("NOTE: This class is deprecated. Use PositionDetector + IPAMapper instead.")
    print("This demo shows backward compatibility.")

    # Test with syllables
    print("\nTesting syllable processing (backward compatibility):")

    test_cases = [
        # Word: أكل (ate)
        {
            "word": "أكل",
            "syllables": [
                {"syllable": "أَ"},   # Initial
                {"syllable": "كَ"},   # Medial
                {"syllable": "لَ"},   # Final
            ]
        },
        # Word: ماء (water)
        {
            "word": "ماء",
            "syllables": [
                {"syllable": "مَا"},  # Initial
                {"syllable": "ء"},    # Final
            ]
        }
    ]

    # Test with dialect for IPA generation
    processor._dialect = "EG"  # Egyptian Arabic

    for test in test_cases:
        print(f"\nWord: {test['word']}")
        print("-" * 70)

        # Process (now delegates to PositionDetector + IPAMapper)
        result = processor.process(test['syllables'], test['word'])

        for i, syl in enumerate(result):
            print(f"  Syllable {i+1}: {syl.get('syllable')}")
            print(f"    Detected Position: {syl.get('detected_position')}")
            if 'ipa' in syl:
                print(f"    IPA: {syl.get('ipa')}")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("\nFor new code, use:")
    print("  from src.core.position_detector import PositionDetector")
    print("  from src.core.ipa_mapper import IPAMapper")
    print("\n  # Position detection (universal)")
    print("  positions = PositionDetector()")
    print("  syllables = positions.detect_positions(syllables)")
    print("")
    print("  # IPA mapping (dialect-specific)")
    print("  ipa_mapper = IPAMapper()")
    print("  ipa = ipa_mapper.map_to_ipa(syllables, dialect='EG')")
