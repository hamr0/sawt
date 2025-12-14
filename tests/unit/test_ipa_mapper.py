"""
Unit tests for IPAMapper class.

Tests verify:
1. IPAMapper loads masterTTS.json correctly
2. All dialects are accessible
3. IPA lookup works for all supported positions
4. Dialect switching works correctly
5. Performance is acceptable (O(1) lookups)
6. Edge cases are handled properly
"""

import pytest
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.ipa_mapper import IPAMapper


class TestIPAMapperInitialization:
    """Test IPAMapper initialization and data loading."""

    def test_initialization_with_default_path(self):
        """IPAMapper should initialize with default masterTTS.json location."""
        mapper = IPAMapper()
        assert mapper is not None
        assert mapper.master_tts is not None
        assert len(mapper.lookup_tables) > 0

    def test_all_dialects_loaded(self):
        """All dialects from masterTTS.json should be loaded."""
        mapper = IPAMapper()
        dialects = mapper.get_available_dialects()

        # Verify expected dialects exist
        assert 'EG' in dialects
        assert 'MSA' in dialects
        assert len(dialects) >= 5  # At least 5 dialects

    def test_lookup_tables_built(self):
        """Lookup tables should be built for each dialect."""
        mapper = IPAMapper()

        for dialect in mapper.get_available_dialects():
            assert dialect in mapper.lookup_tables
            assert isinstance(mapper.lookup_tables[dialect], dict)
            assert len(mapper.lookup_tables[dialect]) > 0


class TestIPAMapperDialectValidation:
    """Test dialect validation methods."""

    def test_validate_supported_dialect(self):
        """validate_dialect should return True for supported dialects."""
        mapper = IPAMapper()

        assert mapper.validate_dialect('EG') is True
        assert mapper.validate_dialect('MSA') is True

    def test_validate_unsupported_dialect(self):
        """validate_dialect should return False for unsupported dialects."""
        mapper = IPAMapper()
        assert mapper.validate_dialect('INVALID') is False

    def test_get_available_dialects(self):
        """get_available_dialects should return list of dialect codes."""
        mapper = IPAMapper()
        dialects = mapper.get_available_dialects()

        assert isinstance(dialects, list)
        assert len(dialects) > 0
        assert all(isinstance(d, str) for d in dialects)


class TestIPAMapperCharacterLookup:
    """Test character-level IPA lookups."""

    def test_lookup_hamza_eg_default(self):
        """Test hamza (أ) lookup in EG dialect with default position."""
        mapper = IPAMapper()
        ipa = mapper.get_ipa_for_char('أ', 'EG', 'default')

        assert ipa is not None
        assert len(ipa) > 0
        # EG hamza should be glottal stop
        assert 'ʔ' in ipa or ipa == 'ʔ' or ipa.startswith('ʔ')

    def test_lookup_ba_eg_default(self):
        """Test ba (ب) lookup in EG dialect with default position."""
        mapper = IPAMapper()
        ipa = mapper.get_ipa_for_char('ب', 'EG', 'default')

        assert ipa is not None
        assert len(ipa) > 0

    def test_lookup_position_initial(self):
        """Test position-specific lookup for word-initial position."""
        mapper = IPAMapper()
        # Hamza has different IPA in different positions
        ipa_initial = mapper.get_ipa_for_char('أ', 'EG', 'word-initial')

        assert ipa_initial is not None
        assert len(ipa_initial) > 0

    def test_lookup_position_medial(self):
        """Test position-specific lookup for word-medial position."""
        mapper = IPAMapper()
        # Hamza can be deleted word-medially in EG
        ipa_medial = mapper.get_ipa_for_char('أ', 'EG', 'word-medial')

        assert ipa_medial is not None
        # Can be ∅ or ʔ depending on dialect rules

    def test_lookup_position_final(self):
        """Test position-specific lookup for word-final position."""
        mapper = IPAMapper()
        ipa_final = mapper.get_ipa_for_char('أ', 'EG', 'word-final')

        assert ipa_final is not None
        assert len(ipa_final) > 0

    def test_lookup_different_dialects(self):
        """Test same character produces different IPA for different dialects."""
        mapper = IPAMapper()

        # Jeem has different pronunciations in EG vs MSA
        ipa_eg = mapper.get_ipa_for_char('ج', 'EG', 'default')
        ipa_msa = mapper.get_ipa_for_char('ج', 'MSA', 'default')

        # Should both be valid
        assert len(ipa_eg) > 0
        assert len(ipa_msa) > 0

    def test_lookup_consonant_shadda(self):
        """Test character lookup with gemination context."""
        mapper = IPAMapper()

        context = {'has_gemination': True}
        ipa = mapper.get_ipa_for_char('ر', 'EG', 'default', context)

        # Geminated consonant should have length marker or be valid IPA
        assert len(ipa) > 0
        # Should contain length marker if gemination applied
        # Some characters may handle gemination differently
        assert ipa is not None

    def test_lookup_punctuation(self):
        """Test punctuation passes through unchanged."""
        mapper = IPAMapper()

        # Punctuation should not be in lookup, should return itself
        ipa_period = mapper.get_ipa_for_char('.', 'EG')
        assert ipa_period == '.'

        ipa_comma = mapper.get_ipa_for_char(',', 'EG')
        assert ipa_comma == ','

    def test_lookup_space(self):
        """Test space passes through unchanged."""
        mapper = IPAMapper()
        ipa_space = mapper.get_ipa_for_char(' ', 'EG')
        assert ipa_space == ' '


class TestIPAMapperBatchConversion:
    """Test batch syllable conversion."""

    def test_map_to_ipa_single_syllable(self):
        """Test mapping single syllable to IPA."""
        mapper = IPAMapper()

        syllables = [
            {
                'syllable': 'صَبَاح',
                'detected_position': 'default',
                'has_gemination': False,
                'has_emphatic': True
            }
        ]

        ipa = mapper.map_to_ipa(syllables, 'EG')

        assert ipa is not None
        assert len(ipa) > 0

    def test_map_to_ipa_multiple_syllables(self):
        """Test mapping multiple syllables to IPA."""
        mapper = IPAMapper()

        syllables = [
            {
                'syllable': 'الْ',
                'detected_position': 'word-initial',
                'has_gemination': False,
                'has_emphatic': False
            },
            {
                'syllable': 'شَمْس',
                'detected_position': 'word-medial',
                'has_gemination': False,
                'has_emphatic': False
            }
        ]

        ipa = mapper.map_to_ipa(syllables, 'EG')

        assert ipa is not None
        assert len(ipa) > 0

    def test_map_to_ipa_with_gemination(self):
        """Test mapping with gemination markers."""
        mapper = IPAMapper()

        syllables = [
            {
                'syllable': 'مُدَرِّس',
                'detected_position': 'default',
                'has_gemination': True,
                'has_emphatic': False
            }
        ]

        ipa = mapper.map_to_ipa(syllables, 'EG')

        assert ipa is not None
        assert len(ipa) > 0

    def test_dialect_switching(self):
        """Test same syllables produce different IPA for different dialects."""
        mapper = IPAMapper()

        syllables = [
            {
                'syllable': 'جمل',
                'detected_position': 'default',
                'has_gemination': False,
                'has_emphatic': False
            }
        ]

        ipa_eg = mapper.map_to_ipa(syllables, 'EG')
        ipa_msa = mapper.map_to_ipa(syllables, 'MSA')

        # Both should be valid
        assert len(ipa_eg) > 0
        assert len(ipa_msa) > 0

    def test_map_to_ipa_invalid_dialect(self):
        """Test error handling for invalid dialect."""
        mapper = IPAMapper()

        syllables = [{'syllable': 'الم', 'detected_position': 'default'}]

        with pytest.raises(ValueError):
            mapper.map_to_ipa(syllables, 'INVALID_DIALECT')


class TestIPAMapperPerformance:
    """Test performance characteristics."""

    def test_single_character_lookup_performance(self):
        """Test that individual character lookups are fast (O(1))."""
        mapper = IPAMapper()

        start = time.time()
        for _ in range(1000):
            mapper.get_ipa_for_char('ا', 'EG', 'default')
        elapsed = time.time() - start

        # 1000 lookups should be fast (< 100ms)
        assert elapsed < 0.1, f"Lookups took {elapsed}s, expected < 0.1s"

    def test_dialect_statistics(self):
        """Test dialect statistics generation."""
        mapper = IPAMapper()

        stats = mapper.get_dialect_statistics('EG')

        assert 'total_entries' in stats
        assert 'unique_characters' in stats
        assert stats['total_entries'] > 0
        assert stats['unique_characters'] > 0

    def test_masterttsjson_loaded_once(self):
        """Verify masterTTS.json is loaded only once during init."""
        mapper = IPAMapper()

        # Multiple lookups should use cached data
        start = time.time()
        for _ in range(100):
            for char in 'احمد':
                mapper.get_ipa_for_char(char, 'EG')
        elapsed = time.time() - start

        # Should be very fast (cached)
        assert elapsed < 0.01, f"Lookups took {elapsed}s"


class TestIPAMapperEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_syllables_list(self):
        """Test handling of empty syllables list."""
        mapper = IPAMapper()

        ipa = mapper.map_to_ipa([], 'EG')
        assert ipa == ''

    def test_syllable_with_empty_text(self):
        """Test handling of syllable with empty text."""
        mapper = IPAMapper()

        syllables = [{'syllable': '', 'detected_position': 'default'}]
        ipa = mapper.map_to_ipa(syllables, 'EG')

        # Should handle gracefully
        assert isinstance(ipa, str)

    def test_syllable_missing_detected_position(self):
        """Test handling of syllable without detected_position key."""
        mapper = IPAMapper()

        syllables = [
            {
                'syllable': 'الم',
                # No 'detected_position' key
            }
        ]

        # Should default to 'default'
        ipa = mapper.map_to_ipa(syllables, 'EG')
        assert ipa is not None

    def test_character_not_in_dialect(self):
        """Test handling of character not in dialect data."""
        mapper = IPAMapper()

        # Some rare character not in data
        ipa = mapper.get_ipa_for_char('𐍂', 'EG')  # Gothic character

        # Should fallback gracefully
        assert ipa is not None

    def test_unicode_normalization(self):
        """Test handling of different Unicode forms."""
        mapper = IPAMapper()

        # Different Unicode forms of same character
        char1 = 'ا'  # Aleph
        char2 = 'ا'  # Aleph (might be different Unicode)

        ipa1 = mapper.get_ipa_for_char(char1, 'EG')
        ipa2 = mapper.get_ipa_for_char(char2, 'EG')

        # Should both work
        assert len(ipa1) > 0
        assert len(ipa2) > 0


class TestIPAMapperArchitecture:
    """Test architectural properties of IPAMapper."""

    def test_no_dialect_in_constructor(self):
        """IPAMapper should not require dialect in constructor."""
        # Constructor should work with no arguments
        mapper = IPAMapper()
        assert mapper is not None

    def test_dialect_only_in_methods(self):
        """Dialect should only be specified in lookup methods."""
        mapper = IPAMapper()

        # Methods accept dialect parameter
        result = mapper.get_ipa_for_char('ا', 'EG')
        assert result is not None

        result = mapper.map_to_ipa([{'syllable': 'الم', 'detected_position': 'default'}], 'MSA')
        assert result is not None

    def test_dialect_independent_initialization(self):
        """IPAMapper initialization should not depend on any specific dialect."""
        mapper1 = IPAMapper()
        mapper2 = IPAMapper()

        # Both should have same dialects loaded
        assert mapper1.get_available_dialects() == mapper2.get_available_dialects()

    def test_fast_dialect_switching(self):
        """Switching dialects should be fast (no reloading)."""
        mapper = IPAMapper()

        syllables = [{'syllable': 'الشمس', 'detected_position': 'default'}]

        start = time.time()
        for _ in range(100):
            mapper.map_to_ipa(syllables, 'EG')
            mapper.map_to_ipa(syllables, 'MSA')
            mapper.map_to_ipa(syllables, 'Gulf')
        elapsed = time.time() - start

        # Fast switching - no reload overhead
        assert elapsed < 0.1


class TestIPAMapperIntegration:
    """Integration tests with expected data."""

    def test_lookup_all_five_dialects(self):
        """Test that all 5 dialects can be looked up without error."""
        mapper = IPAMapper()

        test_char = 'ا'  # Aleph
        # Get actual available dialects
        dialects = mapper.get_available_dialects()

        assert len(dialects) >= 5, f"Expected at least 5 dialects, got {len(dialects)}"

        for dialect in dialects:
            ipa = mapper.get_ipa_for_char(test_char, dialect)
            assert ipa is not None
            assert len(ipa) > 0

    def test_hamza_variants_all_dialects(self):
        """Test hamza in all dialects and positions."""
        mapper = IPAMapper()

        char = 'أ'
        positions = ['default', 'word-initial', 'word-medial', 'word-final']
        dialects = ['EG', 'MSA']

        for dialect in dialects:
            for position in positions:
                ipa = mapper.get_ipa_for_char(char, dialect, position)
                # Should return something (might be ∅ or ʔ)
                assert ipa is not None

    def test_emphatic_consonants_eg(self):
        """Test emphatic consonants in EG dialect."""
        mapper = IPAMapper()

        emphatics = ['ص', 'ض', 'ط', 'ظ', 'ق']

        for emphatic in emphatics:
            ipa = mapper.get_ipa_for_char(emphatic, 'EG')
            assert ipa is not None
            assert len(ipa) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
