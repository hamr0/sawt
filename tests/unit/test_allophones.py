"""
Unit tests for Positional Allophone Processor (Universal)
Tests position detection for syllables (initial, medial, final)

ARCHITECTURE NOTE: This processor is now UNIVERSAL (dialect-independent).
It only detects word positions. Actual IPA generation happens in IPAMapper,
which is dialect-aware. These tests validate position detection.
"""
import pytest
from src.core.allophones import AllophoneProcessor


@pytest.fixture
def allophone_processor():
    """Universal allophone processor (dialect-independent)"""
    return AllophoneProcessor()


class TestProcessorInitialization:
    """Test processor initialization without dialect parameter"""

    def test_processor_initialization(self, allophone_processor):
        """Test processor initializes successfully without dialect"""
        # Processor should exist and be usable
        assert allophone_processor is not None
        # Should have diacritics set
        assert allophone_processor.diacritics is not None
        assert len(allophone_processor.diacritics) > 0

    def test_processor_has_no_dialect_attribute(self, allophone_processor):
        """Test processor does NOT have dialect parameter (universal design)"""
        assert not hasattr(allophone_processor, 'dialect')

    def test_processor_has_no_masterTTS_loaded(self, allophone_processor):
        """Test processor does NOT load masterTTS.json (dialect-agnostic)"""
        assert not hasattr(allophone_processor, 'master_tts')
        assert not hasattr(allophone_processor, 'allophone_map')
        assert not hasattr(allophone_processor, 'default_ipa_map')


class TestPositionDetection:
    """Test syllable position detection in words"""
    
    def test_single_syllable_is_initial_and_final(self, allophone_processor):
        """Test single syllable word - first syllable is initial"""
        syllables = [{"syllable": "بَ"}]
        result = allophone_processor.process(syllables, "بَ")
        
        # First (and only) syllable is word-initial
        assert result[0]["detected_position"] == "word-initial"
    
    def test_two_syllable_positions(self, allophone_processor):
        """Test two-syllable word positions"""
        syllables = [
            {"syllable": "كَ", "word_index": 0},
            {"syllable": "تَبَ", "word_index": 0}
        ]
        result = allophone_processor.process(syllables, "كتب")

        assert result[0]["detected_position"] == "word-initial"
        assert result[1]["detected_position"] == "word-final"
    
    def test_three_syllable_positions(self, allophone_processor):
        """Test three-syllable word positions"""
        syllables = [
            {"syllable": "أَ", "word_index": 0},
            {"syllable": "كَ", "word_index": 0},
            {"syllable": "لَ", "word_index": 0}
        ]
        result = allophone_processor.process(syllables, "أكل")

        assert result[0]["detected_position"] == "word-initial"
        assert result[1]["detected_position"] == "word-medial"
        assert result[2]["detected_position"] == "word-final"
    
    def test_five_syllable_positions(self, allophone_processor):
        """Test five-syllable word positions"""
        syllables = [
            {"syllable": "مَ", "word_index": 0},
            {"syllable": "دْ", "word_index": 0},
            {"syllable": "رَ", "word_index": 0},
            {"syllable": "سَ", "word_index": 0},
            {"syllable": "ة", "word_index": 0}
        ]
        result = allophone_processor.process(syllables)

        assert result[0]["detected_position"] == "word-initial"
        assert result[1]["detected_position"] == "word-medial"
        assert result[2]["detected_position"] == "word-medial"
        assert result[3]["detected_position"] == "word-medial"
        assert result[4]["detected_position"] == "word-final"




class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_syllable_list(self, allophone_processor):
        """Test empty syllable list"""
        result = allophone_processor.process([])
        assert result == []
    
    def test_syllable_without_syllable_key(self, allophone_processor):
        """Test syllable without 'syllable' key"""
        syllables = [{"ipa": "test"}]
        result = allophone_processor.process(syllables)
        
        # Should not crash
        assert len(result) == 1
    
    def test_single_character_syllable(self, allophone_processor):
        """Test single character syllable"""
        syllables = [{"syllable": "ب"}]
        result = allophone_processor.process(syllables)
        
        assert result[0]["detected_position"] == "word-initial"


class TestRealWorldExamples:
    """Test with real Arabic words - position detection"""

    def test_word_akala_ate(self, allophone_processor):
        """Test أكل (ate) - position detection"""
        syllables = [
            {"syllable": "أَ", "word_index": 0},
            {"syllable": "كَ", "word_index": 0},
            {"syllable": "لَ", "word_index": 0}
        ]
        result = allophone_processor.process(syllables, "أكل")

        # Verify positions are detected correctly
        assert len(result) == 3
        assert result[0]["detected_position"] == "word-initial"
        assert result[1]["detected_position"] == "word-medial"
        assert result[2]["detected_position"] == "word-final"

    def test_word_maa_water(self, allophone_processor):
        """Test ماء (water) - position detection"""
        syllables = [
            {"syllable": "مَا", "word_index": 0},
            {"syllable": "ء", "word_index": 0}
        ]
        result = allophone_processor.process(syllables, "ماء")

        assert len(result) == 2
        assert result[0]["detected_position"] == "word-initial"
        assert result[1]["detected_position"] == "word-final"

    def test_word_kataba_wrote(self, allophone_processor):
        """Test كتب (wrote) - position detection"""
        syllables = [
            {"syllable": "كَ", "word_index": 0},
            {"syllable": "تَ", "word_index": 0},
            {"syllable": "بَ", "word_index": 0}
        ]
        result = allophone_processor.process(syllables, "كتب")

        assert result[0]["detected_position"] == "word-initial"
        assert result[1]["detected_position"] == "word-medial"
        assert result[2]["detected_position"] == "word-final"


# Test statistics
def test_position_detection_accuracy():
    """Calculate position detection accuracy"""
    processor = AllophoneProcessor()

    test_cases = [
        # (syllables, expected_positions)
        ([{"syllable": "أَ", "word_index": 0}], ["word-initial"]),
        (
            [
                {"syllable": "كَ", "word_index": 0},
                {"syllable": "تَبَ", "word_index": 0}
            ],
            ["word-initial", "word-final"]
        ),
        (
            [
                {"syllable": "أَ", "word_index": 0},
                {"syllable": "كَ", "word_index": 0},
                {"syllable": "لَ", "word_index": 0}
            ],
            ["word-initial", "word-medial", "word-final"]
        ),
    ]

    correct = 0
    total = 0

    for syllables, expected in test_cases:
        result = processor.process(syllables)
        for i, syl in enumerate(result):
            if syl["detected_position"] == expected[i]:
                correct += 1
            total += 1

    accuracy = (correct / total) * 100 if total > 0 else 0
    print(f"\nPosition detection accuracy: {accuracy:.1f}% ({correct}/{total})")

    assert accuracy >= 95.0, f"Accuracy {accuracy}% is below 95%"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
