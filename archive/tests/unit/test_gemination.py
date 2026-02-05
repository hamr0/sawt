"""
Comprehensive unit tests for Gemination Processor
Tests shadda (ّ) detection and consonant gemination marking
Target: 100% detection accuracy
"""
import pytest
from src.core.gemination import GeminationProcessor


@pytest.fixture
def gemination_processor():
    """Universal gemination processor (dialect-independent)"""
    return GeminationProcessor()


class TestGeminationDetection:
    """Test shadda detection in syllables"""
    
    def test_detect_gemination_in_mudarris(self, gemination_processor):
        """Test gemination in مُدَرِّس (teacher)"""
        syllable = {"syllable": "مُدَرِّس"}
        result = gemination_processor.process([syllable])
        
        assert result[0]["has_gemination"] is True
        assert result[0]["geminated_consonant"] == "ر"
    
    def test_detect_gemination_in_kull(self, gemination_processor):
        """Test gemination in كُلّ (all)"""
        syllable = {"syllable": "كُلّ"}
        result = gemination_processor.process([syllable])
        
        assert result[0]["has_gemination"] is True
        assert result[0]["geminated_consonant"] == "ل"
    
    def test_detect_gemination_in_shadd(self, gemination_processor):
        """Test gemination in شَدّ (pulled)"""
        syllable = {"syllable": "شَدّ"}
        result = gemination_processor.process([syllable])
        
        assert result[0]["has_gemination"] is True
        assert result[0]["geminated_consonant"] == "د"
    
    def test_detect_gemination_in_muhimm(self, gemination_processor):
        """Test gemination in مُهِمّ (important)"""
        syllable = {"syllable": "مُهِمّ"}
        result = gemination_processor.process([syllable])
        
        assert result[0]["has_gemination"] is True
        assert result[0]["geminated_consonant"] == "م"
    
    def test_no_gemination_in_kataba(self, gemination_processor):
        """Test word without gemination: كَتَبَ (wrote)"""
        syllable = {"syllable": "كَتَبَ"}
        result = gemination_processor.process([syllable])
        
        assert result[0]["has_gemination"] is False
        assert result[0].get("geminated_consonant") is None
    
    def test_no_gemination_in_madrasa(self, gemination_processor):
        """Test word without gemination: مَدْرَسَة (school)"""
        syllable = {"syllable": "مَدْرَسَة"}
        result = gemination_processor.process([syllable])
        
        assert result[0]["has_gemination"] is False


class TestGeminatedConsonantIdentification:
    """Test identification of which consonant is geminated"""
    
    def test_geminated_raa(self, gemination_processor):
        """Test ر gemination"""
        consonant = gemination_processor._find_geminated_consonant("دَرِّس")
        assert consonant == "ر"
    
    def test_geminated_lam(self, gemination_processor):
        """Test ل gemination"""
        consonant = gemination_processor._find_geminated_consonant("كُلّ")
        assert consonant == "ل"
    
    def test_geminated_daal(self, gemination_processor):
        """Test د gemination"""
        consonant = gemination_processor._find_geminated_consonant("شَدّ")
        assert consonant == "د"
    
    def test_geminated_meem(self, gemination_processor):
        """Test م gemination"""
        consonant = gemination_processor._find_geminated_consonant("مُهِمّ")
        assert consonant == "م"
    
    def test_geminated_taa(self, gemination_processor):
        """Test ت gemination"""
        consonant = gemination_processor._find_geminated_consonant("حَتّى")
        assert consonant == "ت"
    
    def test_geminated_noon(self, gemination_processor):
        """Test ن gemination"""
        consonant = gemination_processor._find_geminated_consonant("جَنّة")
        assert consonant == "ن"
    
    def test_geminated_baa(self, gemination_processor):
        """Test ب gemination"""
        consonant = gemination_processor._find_geminated_consonant("رَبّ")
        assert consonant == "ب"
    
    def test_no_shadda(self, gemination_processor):
        """Test word without shadda"""
        consonant = gemination_processor._find_geminated_consonant("كَتَبَ")
        assert consonant == ""


class TestGeminationPositions:
    """Test gemination detection at different positions"""
    
    def test_detect_positions_in_word(self, gemination_processor):
        """Test detect_gemination method returns positions"""
        # مُدَرِّس has shadda at position (varies based on diacritics)
        positions = gemination_processor.detect_gemination("مُدَرِّس")
        assert len(positions) == 1
        assert positions[0] > 0
    
    def test_multiple_geminations(self, gemination_processor):
        """Test word with multiple geminates (if they exist)"""
        # Most Arabic words have only one gemination
        # But test detection works for multiple
        positions = gemination_processor.detect_gemination("كُلّ")
        assert len(positions) == 1
    
    def test_no_gemination_positions(self, gemination_processor):
        """Test word without gemination returns empty list"""
        positions = gemination_processor.detect_gemination("كَتَبَ")
        assert len(positions) == 0
        assert positions == []


class TestMultipleSyllables:
    """Test processing multiple syllables in a word"""
    
    def test_process_multiple_syllables_with_gemination(self, gemination_processor):
        """Test multi-syllable word with gemination"""
        syllables = [
            {"syllable": "مُ"},
            {"syllable": "دَرِّس"},  # This one has gemination
        ]
        
        result = gemination_processor.process(syllables)
        
        # First syllable: no gemination
        assert result[0]["has_gemination"] is False
        
        # Second syllable: has gemination on ر
        assert result[1]["has_gemination"] is True
        assert result[1]["geminated_consonant"] == "ر"
    
    def test_process_multiple_syllables_no_gemination(self, gemination_processor):
        """Test multi-syllable word without gemination"""
        syllables = [
            {"syllable": "كَ"},
            {"syllable": "تَ"},
            {"syllable": "بَ"},
        ]
        
        result = gemination_processor.process(syllables)
        
        # All syllables should have no gemination
        for syl in result:
            assert syl["has_gemination"] is False


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_syllable(self, gemination_processor):
        """Test empty syllable"""
        syllable = {"syllable": ""}
        result = gemination_processor.process([syllable])
        
        assert result[0]["has_gemination"] is False
    
    def test_syllable_with_only_shadda(self, gemination_processor):
        """Test syllable with only shadda (shouldn't happen but handle gracefully)"""
        syllable = {"syllable": "ّ"}
        result = gemination_processor.process([syllable])
        
        assert result[0]["has_gemination"] is True
        # Should not crash, even if no consonant found
    
    def test_syllable_without_syllable_key(self, gemination_processor):
        """Test syllable dict without 'syllable' key"""
        syllable = {"pattern": "CV"}
        result = gemination_processor.process([syllable])
        
        # Should not crash
        assert result[0]["has_gemination"] is False
    
    def test_empty_syllable_list(self, gemination_processor):
        """Test empty syllable list"""
        result = gemination_processor.process([])
        assert result == []


class TestGeminationConsistency:
    """Test gemination detection consistency across different words"""
    
    def test_common_geminated_words(self, gemination_processor):
        """Test multiple common words with gemination"""
        test_words = [
            ("مُدَرِّس", "ر", "teacher"),
            ("كُلّ", "ل", "all"),
            ("شَدّ", "د", "pulled"),
            ("مُهِمّ", "م", "important"),
            ("حَتّى", "ت", "until"),
            ("جَنّة", "ن", "paradise"),
        ]
        
        for word, expected_consonant, meaning in test_words:
            result = gemination_processor.process([{"syllable": word}])
            assert result[0]["has_gemination"] is True, f"Failed to detect gemination in {word} ({meaning})"
            assert result[0]["geminated_consonant"] == expected_consonant, f"Wrong consonant for {word}"
    
    def test_words_without_gemination(self, gemination_processor):
        """Test multiple words without gemination"""
        test_words = ["كَتَبَ", "مَدْرَسَة", "بَيْت", "كِتَاب", "نُور"]
        
        for word in test_words:
            result = gemination_processor.process([{"syllable": word}])
            assert result[0]["has_gemination"] is False, f"False positive gemination in {word}"


# Test statistics
def test_gemination_accuracy():
    """Calculate overall gemination detection accuracy"""
    processor = GeminationProcessor()
    
    # 6 words with gemination
    geminated_words = ["مُدَرِّس", "كُلّ", "شَدّ", "مُهِمّ", "حَتّى", "جَنّة"]
    
    # 5 words without gemination
    non_geminated_words = ["كَتَبَ", "مَدْرَسَة", "بَيْت", "كِتَاب", "نُور"]
    
    correct = 0
    total = len(geminated_words) + len(non_geminated_words)
    
    # Test geminated words
    for word in geminated_words:
        result = processor.process([{"syllable": word}])
        if result[0]["has_gemination"] is True:
            correct += 1
    
    # Test non-geminated words
    for word in non_geminated_words:
        result = processor.process([{"syllable": word}])
        if result[0]["has_gemination"] is False:
            correct += 1
    
    accuracy = (correct / total) * 100
    print(f"\nGemination detection accuracy: {accuracy:.1f}% ({correct}/{total})")
    
    assert accuracy == 100.0, f"Accuracy {accuracy}% is below 100%"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
