"""
Universality Verification Tests for Arabic TTS Processors

This test suite verifies that phonological processors produce identical output
regardless of the target dialect. This is a critical architectural requirement:

- GeminationProcessor should detect shadda identically for all dialects
- SunLetterProcessor should detect sun letter assimilation identically for all dialects
- PositionDetector should detect word positions identically for all dialects
- EmphaticProcessor should detect emphatic consonants identically for all dialects

Only IPAMapper should produce dialect-specific output.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.gemination import GeminationProcessor
from src.core.sun_letters import SunLetterProcessor
from src.core.position_detector import PositionDetector
from src.core.emphatic import EmphaticProcessor


class TestGeminationProcessorUniversality:
    """Verify GeminationProcessor produces identical output regardless of dialect."""

    def test_gemination_detection_is_dialect_independent(self):
        """Gemination detection should be identical across all dialects."""
        processor = GeminationProcessor()

        # Test data with various gemination patterns
        test_cases = [
            {"syllable": "مُدَرِّس", "has_gemination": True, "geminated_consonant": "ر"},
            {"syllable": "كُلّ", "has_gemination": True, "geminated_consonant": "ل"},
            {"syllable": "شَدّ", "has_gemination": True, "geminated_consonant": "د"},
            {"syllable": "مُهِمّ", "has_gemination": True, "geminated_consonant": "م"},
            {"syllable": "حَتّى", "has_gemination": True, "geminated_consonant": "ت"},
            {"syllable": "كَتَبَ", "has_gemination": False},
            {"syllable": "مَدْرَسَة", "has_gemination": False},
            {"syllable": "", "has_gemination": False},
        ]

        # Process each test case
        for test_case in test_cases:
            input_syllable = {"syllable": test_case["syllable"]}
            result = processor.process([input_syllable])[0]

            # Verify results match expected
            assert result.get("has_gemination") == test_case["has_gemination"]
            if test_case.get("geminated_consonant"):
                assert result.get("geminated_consonant") == test_case["geminated_consonant"]

    def test_gemination_processor_has_no_dialect_parameter(self):
        """GeminationProcessor constructor should not accept dialect parameter."""
        # Should instantiate without any parameters
        processor = GeminationProcessor()
        assert processor is not None

        # Should not have dialect attribute
        assert not hasattr(processor, "dialect")

    def test_gemination_processor_same_output_multiple_runs(self):
        """Processor should produce identical output across multiple runs."""
        processor = GeminationProcessor()
        syllable = {"syllable": "مُدَرِّس"}

        # Run multiple times
        results = []
        for _ in range(5):
            result = processor.process([syllable])[0]
            results.append(result)

        # All results should be identical
        for result in results[1:]:
            assert result == results[0]


class TestSunLetterProcessorUniversality:
    """Verify SunLetterProcessor produces identical output regardless of dialect."""

    def test_sun_letter_detection_is_dialect_independent(self):
        """Sun letter detection should be identical across all dialects."""
        processor = SunLetterProcessor()

        # Test patterns
        test_patterns = [
            # ال + sun letter
            (["ال", "شَمْس"], True, "ش"),  # الشمس
            (["ال", "قَمَر"], False, None),  # القمر (moon letter)
            (["ال", "رَجُل"], True, "ر"),  # الرجل
            (["ال", "كِتَاب"], False, None),  # الكتاب
            (["ال", "نُور"], True, "ن"),  # النور
            (["ال", "بَيْت"], False, None),  # البيت
            # Without ال
            (["شَمْس"], False, None),  # No article
            (["كِتَاب"], False, None),  # No article
        ]

        for syllables, expected_assimilation, expected_sun_letter in test_patterns:
            input_syllables = [{"syllable": s} for s in syllables]
            results = processor.process(input_syllables)

            # Check assimilation marking
            assert results[0].get("sun_letter_assimilation") == expected_assimilation
            if expected_sun_letter:
                assert results[0].get("assimilated_sun_letter") == expected_sun_letter

    def test_sun_letter_processor_has_no_dialect_parameter(self):
        """SunLetterProcessor constructor should not accept dialect parameter."""
        processor = SunLetterProcessor()
        assert processor is not None
        assert not hasattr(processor, "dialect")

    def test_all_sun_letters_detected_universally(self):
        """All 14 sun letters should be detected consistently."""
        processor = SunLetterProcessor()

        sun_letters = ['ت', 'ث', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ل', 'ن']

        for sun_letter in sun_letters:
            syllables = [{"syllable": "ال"}, {"syllable": sun_letter + "َ"}]
            results = processor.process(syllables)

            assert results[0]["sun_letter_assimilation"] is True
            assert results[0]["assimilated_sun_letter"] == sun_letter


class TestPositionDetectorUniversality:
    """Verify PositionDetector produces identical output regardless of dialect."""

    def test_position_detection_is_dialect_independent(self):
        """Position detection should be identical across all dialects."""
        detector = PositionDetector()

        # Test cases
        test_cases = [
            # Single word
            ([
                {"syllable": "مَ", "word_index": 0, "position_in_word": 0},
                {"syllable": "دْ", "word_index": 0, "position_in_word": 1},
                {"syllable": "رَ", "word_index": 0, "position_in_word": 2},
                {"syllable": "سَة", "word_index": 0, "position_in_word": 3},
            ], ["word-initial", "word-medial", "word-medial", "word-final"]),

            # Multiple words
            ([
                {"syllable": "ال", "word_index": 0, "position_in_word": 0},
                {"syllable": "شَمْس", "word_index": 0, "position_in_word": 1},
                {"syllable": "مُ", "word_index": 1, "position_in_word": 0},
                {"syllable": "ضِي", "word_index": 1, "position_in_word": 1},
                {"syllable": "ئَة", "word_index": 1, "position_in_word": 2},
            ], ["word-initial", "word-final", "word-initial", "word-medial", "word-final"]),
        ]

        for syllables, expected_positions in test_cases:
            results = detector.detect_positions(syllables)

            # Verify positions
            for result, expected in zip(results, expected_positions):
                assert result["detected_position"] == expected

    def test_position_detector_has_no_dialect_parameter(self):
        """PositionDetector constructor should not accept dialect parameter."""
        detector = PositionDetector()
        assert detector is not None
        assert not hasattr(detector, "dialect")

    def test_single_syllable_word_position(self):
        """Single-syllable words should consistently be marked as word-initial."""
        detector = PositionDetector()

        syllables = [
            {"syllable": "كِ", "word_index": 0, "position_in_word": 0},
            {"syllable": "تَ", "word_index": 1, "position_in_word": 0},
            {"syllable": "ب", "word_index": 2, "position_in_word": 0},
        ]

        results = detector.detect_positions(syllables)

        # All should be word-initial
        for result in results:
            assert result["detected_position"] == "word-initial"


class TestEmphaticProcessorUniversality:
    """Verify EmphaticProcessor produces identical output regardless of dialect."""

    def test_emphatic_detection_is_dialect_independent(self):
        """Emphatic consonant detection should be identical across all dialects."""
        processor = EmphaticProcessor()

        # Test cases with emphatic consonants
        emphatic_words = [
            {"syllable": "صَبَاح", "has_emphatic": True},
            {"syllable": "ضَوْء", "has_emphatic": True},
            {"syllable": "طَعَام", "has_emphatic": True},
            {"syllable": "ظَرِيف", "has_emphatic": True},
            {"syllable": "قَلَم", "has_emphatic": True},
        ]

        # Test cases without emphatic consonants
        non_emphatic_words = [
            {"syllable": "كِتَاب", "has_emphatic": False},
            {"syllable": "بَيْت", "has_emphatic": False},
            {"syllable": "مَدْرَسَة", "has_emphatic": False},
            {"syllable": "وَلَد", "has_emphatic": False},
        ]

        # Test emphatic words
        for test_case in emphatic_words:
            result = processor.process([test_case])[0]
            assert result.get("has_emphatic") == test_case["has_emphatic"]
            assert "emphatic_consonants" in result

        # Test non-emphatic words
        for test_case in non_emphatic_words:
            result = processor.process([test_case])[0]
            assert result.get("has_emphatic") == test_case["has_emphatic"]

    def test_emphatic_processor_has_no_dialect_parameter(self):
        """EmphaticProcessor constructor should not accept dialect parameter."""
        processor = EmphaticProcessor()
        assert processor is not None
        assert not hasattr(processor, "dialect")

    def test_all_five_emphatic_consonants_detected(self):
        """All 5 emphatic consonants should be detected consistently."""
        processor = EmphaticProcessor()

        emphatic_consonants = {
            'ص': "صَباح",
            'ض': "ضَوْء",
            'ط': "طَعام",
            'ظ': "ظَرِيف",
            'ق': "قَلَم",
        }

        for consonant, word in emphatic_consonants.items():
            result = processor.process([{"syllable": word}])[0]
            assert result["has_emphatic"] is True
            assert consonant in result.get("emphatic_consonants", [])


class TestProcessorPipelineUniversality:
    """Test that the universal processor pipeline produces consistent output."""

    def test_complete_phonological_pipeline_is_universal(self):
        """The complete phonological pipeline should be dialect-independent."""
        # Initialize all processors
        gemination = GeminationProcessor()
        sun_letters = SunLetterProcessor()
        position_detector = PositionDetector()
        emphatic = EmphaticProcessor()

        # Test with a complex sentence
        syllables = [
            {"syllable": "ال", "word_index": 0, "position_in_word": 0},
            {"syllable": "مُدَرِّس", "word_index": 0, "position_in_word": 1},
            {"syllable": "جَ", "word_index": 1, "position_in_word": 0},
            {"syllable": "دِيد", "word_index": 1, "position_in_word": 1},
        ]

        # Run complete pipeline
        processed = syllables.copy()

        # 1. Gemination detection
        processed = gemination.process(processed)

        # 2. Sun letter assimilation
        processed = sun_letters.process(processed)

        # 3. Position detection
        processed = position_detector.detect_positions(processed)

        # 4. Emphatic detection
        processed = emphatic.process(processed)

        # Verify no dialect-specific information was added
        for syllable in processed:
            assert "dialect" not in syllable
            assert "EG" not in str(syllable)
            assert "MSA" not in str(syllable)
            assert "Gulf" not in str(syllable)

        # Verify expected markers
        assert processed[0]["detected_position"] == "word-initial"
        assert processed[1]["has_gemination"] is True
        assert processed[1]["geminated_consonant"] == "ر"
        assert processed[2]["detected_position"] == "word-initial"
        assert processed[3]["detected_position"] == "word-final"

    def test_processor_output_is_deterministic(self):
        """Processor output should be deterministic (same input → same output)."""
        processors = [
            GeminationProcessor(),
            SunLetterProcessor(),
            PositionDetector(),
            EmphaticProcessor()
        ]

        test_syllables = [
            {"syllable": "الشَّمْس", "word_index": 0, "position_in_word": 0},
            {"syllable": "مُشْرِقَة", "word_index": 0, "position_in_word": 1},
        ]

        # Run multiple times for each processor
        for processor in processors:
            results = []
            for _ in range(10):
                if isinstance(processor, PositionDetector):
                    result = processor.detect_positions([s.copy() for s in test_syllables])
                else:
                    result = processor.process([s.copy() for s in test_syllables])
                results.append(result)

            # All results should be identical
            for result in results[1:]:
                assert result == results[0]


class TestArchitecturalSeparation:
    """Test that architectural separation between universal and dialect-specific is maintained."""

    def test_only_ipamapper_is_dialect_aware(self):
        """Only IPAMapper should have dialect-aware methods."""
        from src.core.ipa_mapper import IPAMapper

        # Universal processors should not have dialect in their methods
        universal_processors = [
            GeminationProcessor(),
            SunLetterProcessor(),
            PositionDetector(),
            EmphaticProcessor()
        ]

        for processor in universal_processors:
            # Check constructor doesn't take dialect
            init_method = processor.__init__
            import inspect
            sig = inspect.signature(init_method)
            assert 'dialect' not in sig.parameters

            # Check main processing methods don't take dialect
            if hasattr(processor, 'process'):
                process_sig = inspect.signature(processor.process)
                assert 'dialect' not in process_sig.parameters

            # Should not have dialect attribute
            assert not hasattr(processor, 'dialect')

        # IPAMapper should accept dialect
        ipa_mapper = IPAMapper()
        map_sig = inspect.signature(ipa_mapper.map_to_ipa)
        assert 'dialect' in map_sig.parameters

        get_ipa_sig = inspect.signature(ipa_mapper.get_ipa_for_char)
        assert 'dialect' in get_ipa_sig.parameters

    def test_universal_processors_produce_features_only(self):
        """Universal processors should only produce feature markers, not IPA."""
        processors = [
            GeminationProcessor(),
            SunLetterProcessor(),
            PositionDetector(),
            EmphaticProcessor()
        ]

        test_syllable = {"syllable": "الْمُدَرِّسُون"}

        for processor in processors:
            if isinstance(processor, PositionDetector):
                result = processor.detect_positions([test_syllable.copy()])
            else:
                result = processor.process([test_syllable.copy()])

            # Check for feature markers (not IPA)
            for syllable in result:
                # Should have feature markers
                if isinstance(processor, GeminationProcessor):
                    assert 'has_gemination' in syllable or syllable.get('has_gemination') is False
                elif isinstance(processor, SunLetterProcessor):
                    assert 'sun_letter_assimilation' in syllable or syllable.get('sun_letter_assimilation') is False
                elif isinstance(processor, PositionDetector):
                    assert 'detected_position' in syllable
                elif isinstance(processor, EmphaticProcessor):
                    assert 'has_emphatic' in syllable or syllable.get('has_emphatic') is False

                # Should NOT have IPA output
                assert 'ipa' not in syllable
                assert '/' not in str(syllable) or str(syllable).count('/') < 2  # Not IPA format


if __name__ == '__main__':
    pytest.main([__file__, '-v'])