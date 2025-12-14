"""
Unit tests for PositionDetector class.

Tests verify:
1. PositionDetector initializes with no parameters
2. Word position detection (initial, medial, final)
3. Single-character word handling
4. Multi-word input processing
5. Punctuation and edge cases
6. Output format validation
7. Real Arabic sentences
8. Universality (no dialect dependency)
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.position_detector import PositionDetector


class TestPositionDetectorInitialization:
    """Test PositionDetector initialization."""

    def test_initialization_no_parameters(self):
        """PositionDetector should initialize with no parameters."""
        detector = PositionDetector()
        assert detector is not None

    def test_initialization_stateless(self):
        """PositionDetector should be stateless."""
        detector = PositionDetector()
        # Should be able to call methods multiple times
        result1 = detector.detect_positions([])
        result2 = detector.detect_positions([])
        assert result1 == result2 == []


class TestPositionDetection:
    """Test word position detection."""

    def test_detect_word_initial_position(self):
        """First syllable in word should be marked as word-initial."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'دْ', 'word_index': 0, 'position_in_word': 1},
        ]
        result = detector.detect_positions(syllables)

        assert result[0]['detected_position'] == 'word-initial'

    def test_detect_word_final_position(self):
        """Last syllable in word should be marked as word-final."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'دْ', 'word_index': 0, 'position_in_word': 1},
            {'syllable': 'رَ', 'word_index': 0, 'position_in_word': 2},
            {'syllable': 'سَة', 'word_index': 0, 'position_in_word': 3},
        ]
        result = detector.detect_positions(syllables)

        assert result[-1]['detected_position'] == 'word-final'

    def test_detect_word_medial_position(self):
        """Middle syllables should be marked as word-medial."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'دْ', 'word_index': 0, 'position_in_word': 1},
            {'syllable': 'رَ', 'word_index': 0, 'position_in_word': 2},
            {'syllable': 'سَة', 'word_index': 0, 'position_in_word': 3},
        ]
        result = detector.detect_positions(syllables)

        # Middle syllables (indices 1 and 2) should be medial
        assert result[1]['detected_position'] == 'word-medial'
        assert result[2]['detected_position'] == 'word-medial'

    def test_single_character_word(self):
        """Single-syllable word should be marked as word-initial (by convention)."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'كِ', 'word_index': 0, 'position_in_word': 0},
        ]
        result = detector.detect_positions(syllables)

        assert result[0]['detected_position'] == 'word-initial'
        assert len(result) == 1

    def test_single_word_three_syllables(self):
        """Three-syllable word should have initial, medial, final."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مُ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'دَ', 'word_index': 0, 'position_in_word': 1},
            {'syllable': 'رِّس', 'word_index': 0, 'position_in_word': 2},
        ]
        result = detector.detect_positions(syllables)

        assert result[0]['detected_position'] == 'word-initial'
        assert result[1]['detected_position'] == 'word-medial'
        assert result[2]['detected_position'] == 'word-final'


class TestMultiWordHandling:
    """Test handling of multi-word input."""

    def test_multi_word_position_reset(self):
        """Positions should reset for each word."""
        detector = PositionDetector()
        syllables = [
            # Word 1: 2 syllables
            {'syllable': 'الْ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'شَمْس', 'word_index': 0, 'position_in_word': 1},
            # Word 2: 2 syllables
            {'syllable': 'الْ', 'word_index': 1, 'position_in_word': 0},
            {'syllable': 'قَمَر', 'word_index': 1, 'position_in_word': 1},
        ]
        result = detector.detect_positions(syllables)

        # Word 1 first syllable
        assert result[0]['detected_position'] == 'word-initial'
        # Word 1 last syllable
        assert result[1]['detected_position'] == 'word-final'
        # Word 2 first syllable (not medial even though it's the 3rd overall)
        assert result[2]['detected_position'] == 'word-initial'
        # Word 2 last syllable
        assert result[3]['detected_position'] == 'word-final'

    def test_three_word_sentence(self):
        """Test sentence with three words."""
        detector = PositionDetector()
        syllables = [
            # Word 1: 1 syllable
            {'syllable': 'الْ', 'word_index': 0, 'position_in_word': 0},
            # Word 2: 3 syllables
            {'syllable': 'كِ', 'word_index': 1, 'position_in_word': 0},
            {'syllable': 'تَ', 'word_index': 1, 'position_in_word': 1},
            {'syllable': 'ب', 'word_index': 1, 'position_in_word': 2},
            # Word 3: 2 syllables
            {'syllable': 'جَ', 'word_index': 2, 'position_in_word': 0},
            {'syllable': 'دِيد', 'word_index': 2, 'position_in_word': 1},
        ]
        result = detector.detect_positions(syllables)

        # Word 1: single syllable
        assert result[0]['detected_position'] == 'word-initial'

        # Word 2: three syllables
        assert result[1]['detected_position'] == 'word-initial'
        assert result[2]['detected_position'] == 'word-medial'
        assert result[3]['detected_position'] == 'word-final'

        # Word 3: two syllables
        assert result[4]['detected_position'] == 'word-initial'
        assert result[5]['detected_position'] == 'word-final'


class TestOutputFormat:
    """Test output format and structure."""

    def test_output_includes_detected_position_key(self):
        """Output should include 'detected_position' key for each syllable."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'دَ', 'word_index': 0, 'position_in_word': 1},
            {'syllable': 'رِس', 'word_index': 0, 'position_in_word': 2},
        ]
        result = detector.detect_positions(syllables)

        for syll in result:
            assert 'detected_position' in syll

    def test_output_preserves_original_keys(self):
        """Output should preserve all original keys from input."""
        detector = PositionDetector()
        syllables = [
            {
                'syllable': 'مَ',
                'word_index': 0,
                'position_in_word': 0,
                'has_gemination': False,
                'has_emphatic': False,
                'custom_field': 'test_value',
            },
        ]
        result = detector.detect_positions(syllables)

        assert result[0]['syllable'] == 'مَ'
        assert result[0]['word_index'] == 0
        assert result[0]['has_gemination'] == False
        assert result[0]['has_emphatic'] == False
        assert result[0]['custom_field'] == 'test_value'
        assert result[0]['detected_position'] == 'word-initial'

    def test_output_list_length_matches_input(self):
        """Output list should have same length as input list."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'دَ', 'word_index': 0, 'position_in_word': 1},
            {'syllable': 'رِس', 'word_index': 0, 'position_in_word': 2},
        ]
        result = detector.detect_positions(syllables)

        assert len(result) == len(syllables)


class TestRealArabicSentences:
    """Test with real Arabic sentences from test dataset."""

    def test_sentence_assalamu_alaikum(self):
        """Test: السلام عليكم (Peace be upon you)."""
        detector = PositionDetector()
        # Simplified representation: السلام (as-salam) | عليكم ('alaikum)
        syllables = [
            {'syllable': 'السْ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'لاّم', 'word_index': 0, 'position_in_word': 1},
            {'syllable': 'عَلَ', 'word_index': 1, 'position_in_word': 0},
            {'syllable': 'يْ', 'word_index': 1, 'position_in_word': 1},
            {'syllable': 'كُم', 'word_index': 1, 'position_in_word': 2},
        ]
        result = detector.detect_positions(syllables)

        # Word 1 positions
        assert result[0]['detected_position'] == 'word-initial'
        assert result[1]['detected_position'] == 'word-final'

        # Word 2 positions
        assert result[2]['detected_position'] == 'word-initial'
        assert result[3]['detected_position'] == 'word-medial'
        assert result[4]['detected_position'] == 'word-final'

    def test_sentence_good_morning(self):
        """Test: صباح الخير (Good morning)."""
        detector = PositionDetector()
        # Simplified: صباح (sabah) | الخير (al-khair)
        syllables = [
            {'syllable': 'صَ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'باح', 'word_index': 0, 'position_in_word': 1},
            {'syllable': 'الْ', 'word_index': 1, 'position_in_word': 0},
            {'syllable': 'خَيْ', 'word_index': 1, 'position_in_word': 1},
            {'syllable': 'ر', 'word_index': 1, 'position_in_word': 2},
        ]
        result = detector.detect_positions(syllables)

        # Word 1
        assert result[0]['detected_position'] == 'word-initial'
        assert result[1]['detected_position'] == 'word-final'

        # Word 2
        assert result[2]['detected_position'] == 'word-initial'
        assert result[3]['detected_position'] == 'word-medial'
        assert result[4]['detected_position'] == 'word-final'

    def test_sentence_complex(self):
        """Test longer sentence: اللغة العربية لغة جميلة."""
        detector = PositionDetector()
        # Simplified representation
        syllables = [
            # Word 1: اللغة
            {'syllable': 'الْ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'لُغَة', 'word_index': 0, 'position_in_word': 1},
            # Word 2: العربية
            {'syllable': 'الْ', 'word_index': 1, 'position_in_word': 0},
            {'syllable': 'عَ', 'word_index': 1, 'position_in_word': 1},
            {'syllable': 'رَ', 'word_index': 1, 'position_in_word': 2},
            {'syllable': 'بِيَة', 'word_index': 1, 'position_in_word': 3},
            # Word 3: لغة
            {'syllable': 'لُ', 'word_index': 2, 'position_in_word': 0},
            {'syllable': 'غَة', 'word_index': 2, 'position_in_word': 1},
            # Word 4: جميلة
            {'syllable': 'جَ', 'word_index': 3, 'position_in_word': 0},
            {'syllable': 'مِ', 'word_index': 3, 'position_in_word': 1},
            {'syllable': 'يلَة', 'word_index': 3, 'position_in_word': 2},
        ]
        result = detector.detect_positions(syllables)

        # Verify all positions are assigned
        for syll in result:
            assert 'detected_position' in syll
            assert syll['detected_position'] in ['word-initial', 'word-medial', 'word-final']


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_syllables_list(self):
        """Empty syllables list should return empty list."""
        detector = PositionDetector()
        result = detector.detect_positions([])

        assert result == []

    def test_single_syllable(self):
        """Single syllable should be marked as word-initial."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'كِ', 'word_index': 0, 'position_in_word': 0},
        ]
        result = detector.detect_positions(syllables)

        assert len(result) == 1
        assert result[0]['detected_position'] == 'word-initial'

    def test_syllables_without_word_index(self):
        """Syllables without word_index should be treated as separate words."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ'},
            {'syllable': 'دَ'},
            {'syllable': 'رِس'},
        ]
        result = detector.detect_positions(syllables)

        # Each should be marked as word-initial (being the only syllable)
        assert all(syll['detected_position'] == 'word-initial' for syll in result)

    def test_mixed_word_index_present_absent(self):
        """Mix of syllables with and without word_index."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'دَ'},
            {'syllable': 'رِس', 'word_index': 1, 'position_in_word': 0},
        ]
        result = detector.detect_positions(syllables)

        # All should have detected_position
        assert len(result) == 3
        assert all('detected_position' in syll for syll in result)


class TestUniversality:
    """Test that PositionDetector is dialect-agnostic."""

    def test_no_dialect_parameter(self):
        """detect_positions should not require dialect parameter."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'دَ', 'word_index': 0, 'position_in_word': 1},
        ]
        # Should work without any dialect specification
        result = detector.detect_positions(syllables)

        assert len(result) == 2
        assert all('detected_position' in syll for syll in result)

    def test_dialect_independent_output(self):
        """Same input should produce same output regardless of use case."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'word_index': 0, 'position_in_word': 0},
            {'syllable': 'دَ', 'word_index': 0, 'position_in_word': 1},
            {'syllable': 'رِس', 'word_index': 0, 'position_in_word': 2},
        ]

        # Call multiple times
        result1 = detector.detect_positions(syllables.copy())
        result2 = detector.detect_positions(syllables.copy())

        # Results should be identical
        assert len(result1) == len(result2)
        for r1, r2 in zip(result1, result2):
            assert r1['detected_position'] == r2['detected_position']


class TestUtilityMethods:
    """Test utility methods."""

    def test_verify_positions_valid(self):
        """verify_positions should return True for valid positions."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'detected_position': 'word-initial'},
            {'syllable': 'دَ', 'detected_position': 'word-final'},
        ]

        assert detector.verify_positions(syllables) == True

    def test_verify_positions_invalid_missing_key(self):
        """verify_positions should return False for missing key."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'detected_position': 'word-initial'},
            {'syllable': 'دَ'},  # Missing detected_position
        ]

        assert detector.verify_positions(syllables) == False

    def test_verify_positions_invalid_value(self):
        """verify_positions should return False for invalid position value."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'detected_position': 'word-initial'},
            {'syllable': 'دَ', 'detected_position': 'invalid-position'},
        ]

        assert detector.verify_positions(syllables) == False

    def test_mark_positions_simple(self):
        """mark_positions_simple should handle simple text input."""
        detector = PositionDetector()
        result = detector.mark_positions_simple("الشمس القمر")

        # Should have detected positions
        assert all('detected_position' in syll for syll in result)

        # First character should be word-initial
        assert result[0]['detected_position'] == 'word-initial'

    def test_get_position_statistics(self):
        """get_position_statistics should count positions."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'مَ', 'detected_position': 'word-initial'},
            {'syllable': 'دَ', 'detected_position': 'word-medial'},
            {'syllable': 'رِس', 'detected_position': 'word-final'},
        ]

        stats = detector.get_position_statistics(syllables)

        assert stats['word-initial'] == 1
        assert stats['word-medial'] == 1
        assert stats['word-final'] == 1
        assert stats['total'] == 3


class TestIntegrationWithIPAMapper:
    """Test compatibility with IPAMapper."""

    def test_output_compatible_with_ipamapper_input(self):
        """PositionDetector output should be compatible with IPAMapper input."""
        detector = PositionDetector()
        syllables = [
            {'syllable': 'الْ', 'word_index': 0, 'position_in_word': 0, 'has_gemination': False},
            {'syllable': 'شَمْس', 'word_index': 0, 'position_in_word': 1, 'has_gemination': False},
        ]

        result = detector.detect_positions(syllables)

        # Result should have all keys IPAMapper expects
        for syll in result:
            assert 'syllable' in syll
            assert 'detected_position' in syll
            assert 'word_index' in syll


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
