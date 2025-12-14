"""
Integration tests for IPAMapper and PositionDetector components.

Tests verify that:
1. IPAMapper and PositionDetector work together correctly
2. The new components integrate with existing pipeline
3. Correct processing order is maintained
4. Output compatibility between components
5. Real-world Egyptian Arabic text processing
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.ipa_mapper import IPAMapper
from src.core.position_detector import PositionDetector


class TestPositionDetectorAndIPAMapperIntegration:
    """Test integration between PositionDetector and IPAMapper"""

    @pytest.fixture
    def position_detector(self):
        """Create PositionDetector instance"""
        return PositionDetector()

    @pytest.fixture
    def ipa_mapper(self):
        """Create IPAMapper instance"""
        return IPAMapper()

    def test_position_detector_output_compatible_with_ipa_mapper(
        self, position_detector, ipa_mapper
    ):
        """
        Test that PositionDetector output is compatible with IPAMapper input.

        IPAMapper expects syllables dict with 'detected_position' key,
        which PositionDetector provides.
        """
        # Create sample syllables
        syllables = [
            {"syllable": "مَ", "word_index": 0, "position_in_word": 0},
            {"syllable": "دْ", "word_index": 0, "position_in_word": 1},
        ]

        # Process with PositionDetector
        positioned_syllables = position_detector.detect_positions(syllables)

        # Verify output has required keys
        for syll in positioned_syllables:
            assert "detected_position" in syll
            assert "syllable" in syll
            assert "word_index" in syll

        # Process with IPAMapper
        ipa_result = ipa_mapper.map_to_ipa(positioned_syllables, "EG")
        assert ipa_result is not None
        assert len(ipa_result) > 0

    def test_pipeline_order_position_before_ipa_mapping(
        self, position_detector, ipa_mapper
    ):
        """
        Test correct processing order: PositionDetector → IPAMapper

        This verifies the architectural decision that position detection
        happens before dialect-specific IPA mapping.
        """
        syllables = [
            {"syllable": "شَ", "word_index": 0, "position_in_word": 0},
            {"syllable": "مْ", "word_index": 0, "position_in_word": 1},
            {"syllable": "سْ", "word_index": 0, "position_in_word": 2},
        ]

        # Step 1: Detect positions (must happen first)
        positioned = position_detector.detect_positions(syllables)

        # Verify positions detected
        assert positioned[0]["detected_position"] == "word-initial"
        assert positioned[1]["detected_position"] == "word-medial"
        assert positioned[2]["detected_position"] == "word-final"

        # Step 2: Map to IPA (uses position information)
        ipa = ipa_mapper.map_to_ipa(positioned, "EG")
        assert ipa is not None

    def test_multi_word_sentence_integration(self, position_detector, ipa_mapper):
        """
        Test complete integration on multi-word sentence.

        Verifies that position detection resets correctly for each word,
        and IPA mapping respects position information.
        """
        # الشمس (the sun) - 2 words
        syllables = [
            # Word 1: ال (the)
            {"syllable": "الْ", "word_index": 0, "position_in_word": 0},
            # Word 2: شمس (sun)
            {"syllable": "شَ", "word_index": 1, "position_in_word": 0},
            {"syllable": "مْ", "word_index": 1, "position_in_word": 1},
            {"syllable": "سْ", "word_index": 1, "position_in_word": 2},
        ]

        # Detect positions
        positioned = position_detector.detect_positions(syllables)

        # Verify position reset between words
        word1_syll = positioned[0]
        word2_syll1 = positioned[1]

        assert word1_syll["detected_position"] == "word-initial"
        assert word2_syll1["detected_position"] == "word-initial"

        # Map to IPA
        ipa = ipa_mapper.map_to_ipa(positioned, "EG")
        assert ipa is not None

    def test_dialect_independence_of_position_detector(self, position_detector):
        """
        Test that PositionDetector is truly dialect-independent.

        Position detection should produce identical results regardless
        of which dialect will be used for IPA mapping.
        """
        syllables = [
            {"syllable": "كَ", "word_index": 0, "position_in_word": 0},
            {"syllable": "تَ", "word_index": 0, "position_in_word": 1},
            {"syllable": "بْ", "word_index": 0, "position_in_word": 2},
        ]

        # Position detection should not depend on dialect
        result = position_detector.detect_positions(syllables)

        # Results should be identical regardless of future dialect choice
        assert result[0]["detected_position"] == "word-initial"
        assert result[1]["detected_position"] == "word-medial"
        assert result[2]["detected_position"] == "word-final"

    def test_position_information_preserved_through_pipeline(
        self, position_detector, ipa_mapper
    ):
        """
        Test that position information is preserved when passed to IPAMapper.

        Verifies that PositionDetector's position markers are not lost
        when IPAMapper processes the syllables.
        """
        syllables = [
            {"syllable": "أَ", "word_index": 0, "position_in_word": 0},
            {"syllable": "بْ", "word_index": 0, "position_in_word": 1},
        ]

        positioned = position_detector.detect_positions(syllables)

        # Record original positions
        original_positions = [s["detected_position"] for s in positioned]

        # Process with IPAMapper
        ipa_mapper.map_to_ipa(positioned, "EG")

        # Verify positions still present in syllables
        current_positions = [s["detected_position"] for s in positioned]
        assert current_positions == original_positions

    def test_real_arabic_word_complete_flow(self, position_detector, ipa_mapper):
        """
        Test complete integration with real Egyptian Arabic word.

        Word: مدرسة (school) - 2 syllables
        Tests the complete flow from syllables through position detection
        to IPA mapping.
        """
        syllables = [
            {"syllable": "مَدْ", "word_index": 0, "position_in_word": 0},
            {"syllable": "رَسَة", "word_index": 0, "position_in_word": 1},
        ]

        # Step 1: Detect positions
        positioned = position_detector.detect_positions(syllables)

        # Step 2: Verify positions
        assert positioned[0]["detected_position"] == "word-initial"
        assert positioned[1]["detected_position"] == "word-final"

        # Step 3: Map to IPA
        ipa = ipa_mapper.map_to_ipa(positioned, "EG")

        # Verify result
        assert ipa is not None
        assert len(ipa) > 0

    def test_dialect_switching_with_positioned_syllables(
        self, position_detector, ipa_mapper
    ):
        """
        Test that same positioned syllables can be mapped to different dialects.

        Verifies that PositionDetector output (universal) can be used
        with IPAMapper for multiple dialects.
        """
        syllables = [
            {"syllable": "جَ", "word_index": 0, "position_in_word": 0},
            {"syllable": "مَل", "word_index": 0, "position_in_word": 1},
        ]

        # Detect positions once
        positioned = position_detector.detect_positions(syllables)

        # Map to different dialects
        ipa_eg = ipa_mapper.map_to_ipa(positioned, "EG")
        ipa_msa = ipa_mapper.map_to_ipa(positioned, "MSA")

        # Both should produce valid results
        assert ipa_eg is not None and len(ipa_eg) > 0
        assert ipa_msa is not None and len(ipa_msa) > 0

    def test_position_detection_with_context_for_ipa_mapping(
        self, position_detector, ipa_mapper
    ):
        """
        Test that position information provides correct context for IPA mapping.

        Some characters have different IPA based on position, and IPAMapper
        should use the position information from PositionDetector.
        """
        # Example: ء (hamza) has different IPA in initial vs medial positions
        syllables = [
            {"syllable": "أَ", "word_index": 0, "position_in_word": 0},  # Initial
            {"syllable": "نَ", "word_index": 0, "position_in_word": 1},  # Medial
        ]

        positioned = position_detector.detect_positions(syllables)

        # Verify positions are correctly detected
        assert positioned[0]["detected_position"] == "word-initial"
        assert positioned[1]["detected_position"] == "word-final"

        # Map to IPA - mapper should consider position
        ipa = ipa_mapper.map_to_ipa(positioned, "EG")
        assert ipa is not None


class TestIntegrationWithComplexSentences:
    """Integration tests with complex real-world Arabic sentences"""

    @pytest.fixture
    def position_detector(self):
        return PositionDetector()

    @pytest.fixture
    def ipa_mapper(self):
        return IPAMapper()

    def test_sentence_with_sun_letters(self, position_detector, ipa_mapper):
        """
        Test integration with sentence containing sun letters.

        Sentence: الشمس (the sun)
        Sun letter ش should assimilate with ال
        Position detection should identify initial/final positions.
        """
        syllables = [
            {"syllable": "الْ", "word_index": 0, "position_in_word": 0},
            {"syllable": "شَ", "word_index": 0, "position_in_word": 1},
            {"syllable": "مْ", "word_index": 0, "position_in_word": 2},
            {"syllable": "سْ", "word_index": 0, "position_in_word": 3},
        ]

        positioned = position_detector.detect_positions(syllables)
        ipa = ipa_mapper.map_to_ipa(positioned, "EG")

        assert ipa is not None
        assert len(ipa) > 0

    def test_sentence_with_emphatic_consonants(
        self, position_detector, ipa_mapper
    ):
        """
        Test integration with emphatic consonants.

        Sentence: صباح (morning)
        Emphatic ص should affect adjacent vowel pharyngealization.
        """
        syllables = [
            {"syllable": "صَ", "word_index": 0, "position_in_word": 0},
            {"syllable": "بَ", "word_index": 0, "position_in_word": 1},
            {"syllable": "احْ", "word_index": 0, "position_in_word": 2},
        ]

        positioned = position_detector.detect_positions(syllables)

        # Verify position detection
        assert positioned[0]["detected_position"] == "word-initial"
        assert positioned[1]["detected_position"] == "word-medial"
        assert positioned[2]["detected_position"] == "word-final"

        ipa = ipa_mapper.map_to_ipa(positioned, "EG")
        assert ipa is not None

    def test_sentence_with_multiple_words(self, position_detector, ipa_mapper):
        """
        Test integration with multi-word sentence.

        Sentence: صباح الخير (good morning)
        Multiple words with position reset.
        """
        syllables = [
            # Word 1: صباح
            {"syllable": "صَ", "word_index": 0, "position_in_word": 0},
            {"syllable": "بَ", "word_index": 0, "position_in_word": 1},
            {"syllable": "احْ", "word_index": 0, "position_in_word": 2},
            # Word 2: الخير
            {"syllable": "الْ", "word_index": 1, "position_in_word": 0},
            {"syllable": "خَ", "word_index": 1, "position_in_word": 1},
            {"syllable": "يْ", "word_index": 1, "position_in_word": 2},
            {"syllable": "رْ", "word_index": 1, "position_in_word": 3},
        ]

        positioned = position_detector.detect_positions(syllables)

        # Verify positions reset at word boundary
        word1_positions = [positioned[0]["detected_position"],
                          positioned[1]["detected_position"],
                          positioned[2]["detected_position"]]
        word2_positions = [positioned[3]["detected_position"],
                          positioned[4]["detected_position"],
                          positioned[5]["detected_position"],
                          positioned[6]["detected_position"]]

        assert word1_positions[0] == "word-initial"
        assert word1_positions[-1] == "word-final"
        assert word2_positions[0] == "word-initial"
        assert word2_positions[-1] == "word-final"

        ipa = ipa_mapper.map_to_ipa(positioned, "EG")
        assert ipa is not None

    def test_sentence_with_gemination(self, position_detector, ipa_mapper):
        """
        Test integration with geminated consonants.

        Sentence: مدرس (teacher root)
        Tests handling of doubled consonants with position information.
        """
        syllables = [
            {"syllable": "مُ", "word_index": 0, "position_in_word": 0},
            {"syllable": "دَ", "word_index": 0, "position_in_word": 1},
            {"syllable": "رِّ", "word_index": 0, "position_in_word": 2},  # Geminated r
            {"syllable": "سْ", "word_index": 0, "position_in_word": 3},
        ]

        positioned = position_detector.detect_positions(syllables)

        # Verify position detection with gemination
        assert positioned[0]["detected_position"] == "word-initial"
        assert positioned[-1]["detected_position"] == "word-final"

        ipa = ipa_mapper.map_to_ipa(positioned, "EG")
        assert ipa is not None


class TestArchitecturalProperties:
    """Test architectural properties of integration"""

    @pytest.fixture
    def position_detector(self):
        return PositionDetector()

    @pytest.fixture
    def ipa_mapper(self):
        return IPAMapper()

    def test_universal_processor_before_dialect_specific(
        self, position_detector, ipa_mapper
    ):
        """
        Verify architectural pattern: Universal processors → Dialect-specific processors.

        PositionDetector (universal) must run before IPAMapper (dialect-specific).
        """
        syllables = [
            {"syllable": "كَ", "word_index": 0, "position_in_word": 0},
            {"syllable": "تَب", "word_index": 0, "position_in_word": 1},
        ]

        # PositionDetector should not care about dialect
        positioned = position_detector.detect_positions(syllables)

        # IPAMapper should be able to use positioned output for any dialect
        for dialect in ["EG", "MSA"]:
            ipa = ipa_mapper.map_to_ipa(positioned, dialect)
            assert ipa is not None

    def test_no_data_loss_through_pipeline(self, position_detector, ipa_mapper):
        """
        Test that no data is lost when passing through pipeline.

        Original input keys should be preserved when output goes through
        both PositionDetector and IPAMapper.
        """
        original_syllables = [
            {
                "syllable": "كَ",
                "word_index": 0,
                "position_in_word": 0,
                "custom_field": "test_value",
            },
            {"syllable": "تَب", "word_index": 0, "position_in_word": 1},
        ]

        positioned = position_detector.detect_positions(original_syllables)

        # Verify original fields preserved
        assert positioned[0]["syllable"] == "كَ"
        assert positioned[0]["word_index"] == 0
        assert positioned[0]["position_in_word"] == 0
        assert positioned[0]["custom_field"] == "test_value"

        # Position info added
        assert "detected_position" in positioned[0]

    def test_stateless_universal_processor(self, position_detector):
        """
        Test that PositionDetector is stateless (no side effects).

        Multiple calls with same input should produce identical results.
        """
        syllables = [
            {"syllable": "أَ", "word_index": 0, "position_in_word": 0},
            {"syllable": "نَ", "word_index": 0, "position_in_word": 1},
        ]

        # Run multiple times
        result1 = position_detector.detect_positions(syllables.copy())
        result2 = position_detector.detect_positions(syllables.copy())

        # Results should be identical
        for r1, r2 in zip(result1, result2):
            assert r1["detected_position"] == r2["detected_position"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
