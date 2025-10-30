"""
Comprehensive unit tests for Sun Letter Assimilation Processor
Tests ال (al-) assimilation with sun letters and moon letters
Target: 100% detection and assimilation accuracy
"""
import pytest
from src.core.sun_letters import SunLetterProcessor


@pytest.fixture
def sun_processor():
    """Egyptian Arabic sun letter processor"""
    return SunLetterProcessor("EG")


class TestSunLetterDetection:
    """Test detection of sun vs moon letters"""
    
    def test_is_sun_letter_sheen(self, sun_processor):
        """Test ش is sun letter"""
        assert sun_processor.is_sun_letter('ش') is True
    
    def test_is_sun_letter_taa(self, sun_processor):
        """Test ت is sun letter"""
        assert sun_processor.is_sun_letter('ت') is True
    
    def test_is_sun_letter_daal(self, sun_processor):
        """Test د is sun letter"""
        assert sun_processor.is_sun_letter('د') is True
    
    def test_is_sun_letter_raa(self, sun_processor):
        """Test ر is sun letter"""
        assert sun_processor.is_sun_letter('ر') is True
    
    def test_is_sun_letter_noon(self, sun_processor):
        """Test ن is sun letter"""
        assert sun_processor.is_sun_letter('ن') is True
    
    def test_is_sun_letter_lam(self, sun_processor):
        """Test ل is sun letter"""
        assert sun_processor.is_sun_letter('ل') is True
    
    def test_is_moon_letter_qaaf(self, sun_processor):
        """Test ق is moon letter"""
        assert sun_processor.is_moon_letter('ق') is True
        assert sun_processor.is_sun_letter('ق') is False
    
    def test_is_moon_letter_kaaf(self, sun_processor):
        """Test ك is moon letter"""
        assert sun_processor.is_moon_letter('ك') is True
        assert sun_processor.is_sun_letter('ك') is False
    
    def test_is_moon_letter_meem(self, sun_processor):
        """Test م is moon letter"""
        assert sun_processor.is_moon_letter('م') is True
        assert sun_processor.is_sun_letter('م') is False


class TestSunLetterPatternDetection:
    """Test detection of ال + sun_letter patterns in words"""
    
    def test_pattern_alshams(self, sun_processor):
        """Test الشمس (the sun) has sun letter pattern"""
        assert sun_processor.detect_sun_letter_pattern("الشمس") is True
    
    def test_pattern_aldars(self, sun_processor):
        """Test الدرس (the lesson) has sun letter pattern"""
        assert sun_processor.detect_sun_letter_pattern("الدرس") is True
    
    def test_pattern_arrajul(self, sun_processor):
        """Test الرجل (the man) has sun letter pattern"""
        assert sun_processor.detect_sun_letter_pattern("الرجل") is True
    
    def test_pattern_annur(self, sun_processor):
        """Test النور (the light) has sun letter pattern"""
        assert sun_processor.detect_sun_letter_pattern("النور") is True
    
    def test_pattern_alqamar_moon(self, sun_processor):
        """Test القمر (the moon) does NOT have sun letter pattern"""
        assert sun_processor.detect_sun_letter_pattern("القمر") is False
    
    def test_pattern_alkitab_moon(self, sun_processor):
        """Test الكتاب (the book) does NOT have sun letter pattern"""
        assert sun_processor.detect_sun_letter_pattern("الكتاب") is False
    
    def test_pattern_almadrasa_moon(self, sun_processor):
        """Test المدرسة (the school) does NOT have sun letter pattern"""
        assert sun_processor.detect_sun_letter_pattern("المدرسة") is False
    
    def test_pattern_no_definite_article(self, sun_processor):
        """Test word without ال returns False"""
        assert sun_processor.detect_sun_letter_pattern("شمس") is False


class TestAll14SunLetters:
    """Test all 14 sun letters are correctly identified"""
    
    def test_all_sun_letters(self, sun_processor):
        """Test all 14 sun letters"""
        sun_letters = ['ت', 'ث', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ل', 'ن']
        
        for letter in sun_letters:
            assert sun_processor.is_sun_letter(letter) is True, f"{letter} should be sun letter"
            assert sun_processor.is_moon_letter(letter) is False, f"{letter} should not be moon letter"
    
    def test_all_moon_letters(self, sun_processor):
        """Test all 14 moon letters"""
        moon_letters = ['ء', 'ب', 'ج', 'ح', 'خ', 'ع', 'غ', 'ف', 'ق', 'ك', 'م', 'ه', 'و', 'ي']
        
        for letter in moon_letters:
            assert sun_processor.is_moon_letter(letter) is True, f"{letter} should be moon letter"
            assert sun_processor.is_sun_letter(letter) is False, f"{letter} should not be sun letter"


class TestSyllableProcessing:
    """Test syllable-level sun letter detection"""
    
    def test_process_syllables_with_sun_letter(self, sun_processor):
        """Test processing syllables with sun letter"""
        syllables = [
            {"syllable": "ال"},
            {"syllable": "شمس"}
        ]
        
        result = sun_processor.process(syllables)
        
        assert result[0]["sun_letter_assimilation"] is True
        assert result[0]["assimilated_sun_letter"] == "ش"
        assert result[0]["rule_applied"] == "lam_deleted_sun_geminated"
    
    def test_process_syllables_with_moon_letter(self, sun_processor):
        """Test processing syllables with moon letter"""
        syllables = [
            {"syllable": "ال"},
            {"syllable": "قمر"}
        ]
        
        result = sun_processor.process(syllables)
        
        assert result[0]["sun_letter_assimilation"] is False
        assert result[0]["moon_letter"] == "ق"
    
    def test_process_syllables_without_al(self, sun_processor):
        """Test processing syllables without ال"""
        syllables = [
            {"syllable": "كَ"},
            {"syllable": "تَبَ"}
        ]
        
        result = sun_processor.process(syllables)
        
        assert result[0]["sun_letter_assimilation"] is False
        assert result[1]["sun_letter_assimilation"] is False


class TestAssimilationApplication:
    """Test application of sun letter assimilation to IPA"""
    
    def test_apply_assimilation_sun_letter(self, sun_processor):
        """Test assimilation removes /l/ and marks gemination for sun letter"""
        syllables = [
            {"syllable": "ال", "ipa": "al"},
            {"syllable": "شمس", "ipa": "ʃams"}
        ]
        
        # First detect
        detected = sun_processor.process(syllables)
        
        # Then apply assimilation
        result = sun_processor.apply_assimilation(detected, "الشمس")
        
        # Check first syllable: /l/ removed
        assert result[0]["ipa"] == "a"
        assert result[0]["original_ipa"] == "al"
        
        # Check second syllable: gemination marked
        assert result[1]["has_sun_gemination"] is True
        assert result[1]["geminated_by_sun_rule"] == "ش"
    
    def test_apply_assimilation_moon_letter(self, sun_processor):
        """Test assimilation does NOT modify moon letter words"""
        syllables = [
            {"syllable": "ال", "ipa": "al"},
            {"syllable": "قمر", "ipa": "qamar"}
        ]
        
        detected = sun_processor.process(syllables)
        result = sun_processor.apply_assimilation(detected, "القمر")
        
        # Check first syllable: /l/ NOT removed
        assert result[0]["ipa"] == "al"
        assert result[0].get("original_ipa") is None
        
        # Check second syllable: NO gemination
        assert result[1].get("has_sun_gemination", False) is False
    
    def test_apply_assimilation_multiple_sun_letters(self, sun_processor):
        """Test assimilation on multiple sun letter examples"""
        test_cases = [
            ("الدرس", "د", "al", "a"),
            ("الرجل", "ر", "al", "a"),
            ("النور", "ن", "al", "a"),
        ]
        
        for word, sun_letter, original_ipa, expected_ipa in test_cases:
            syllables = [
                {"syllable": "ال", "ipa": original_ipa},
                {"syllable": word[2:], "ipa": "x"}
            ]
            
            detected = sun_processor.process(syllables)
            result = sun_processor.apply_assimilation(detected, word)
            
            assert result[0]["ipa"] == expected_ipa, f"Failed for {word}"
            assert result[1]["has_sun_gemination"] is True, f"Failed gemination for {word}"
            assert result[1]["geminated_by_sun_rule"] == sun_letter, f"Wrong letter for {word}"


class TestIPAModificationHelper:
    """Test IPA modification helper function"""
    
    def test_modify_ipa_sheen(self, sun_processor):
        """Test IPA modification for ش"""
        consonant_map = {'ش': 'ʃ'}
        result = sun_processor.modify_ipa_for_sun_letter("ʃams", "ش", consonant_map)
        assert result == "ʃːams"
    
    def test_modify_ipa_daal(self, sun_processor):
        """Test IPA modification for د"""
        consonant_map = {'د': 'd'}
        result = sun_processor.modify_ipa_for_sun_letter("dars", "د", consonant_map)
        assert result == "dːars"
    
    def test_modify_ipa_raa(self, sun_processor):
        """Test IPA modification for ر"""
        consonant_map = {'ر': 'r'}
        result = sun_processor.modify_ipa_for_sun_letter("radʒul", "ر", consonant_map)
        assert result == "rːadʒul"
    
    def test_modify_ipa_noon(self, sun_processor):
        """Test IPA modification for ن"""
        consonant_map = {'ن': 'n'}
        result = sun_processor.modify_ipa_for_sun_letter("nuːr", "ن", consonant_map)
        assert result == "nːuːr"
    
    def test_modify_ipa_no_match(self, sun_processor):
        """Test IPA modification when consonant not in map"""
        consonant_map = {'ش': 'ʃ'}
        result = sun_processor.modify_ipa_for_sun_letter("dars", "د", consonant_map)
        assert result == "dars"  # Unchanged


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_syllable_list(self, sun_processor):
        """Test empty syllable list"""
        result = sun_processor.process([])
        assert result == []
    
    def test_single_syllable_with_al(self, sun_processor):
        """Test single syllable with ال (no next syllable to check)"""
        syllables = [{"syllable": "ال"}]
        result = sun_processor.process(syllables)
        
        assert result[0]["sun_letter_assimilation"] is False
    
    def test_syllable_without_syllable_key(self, sun_processor):
        """Test syllable dict without 'syllable' key"""
        syllables = [{"ipa": "al"}]
        result = sun_processor.process(syllables)
        
        assert result[0]["sun_letter_assimilation"] is False
    
    def test_word_without_definite_article(self, sun_processor):
        """Test word that doesn't start with ال"""
        assert sun_processor.detect_sun_letter_pattern("شمس") is False
        assert sun_processor.detect_sun_letter_pattern("قمر") is False


class TestRealWorldExamples:
    """Test real Arabic words with sun and moon letters"""
    
    def test_common_sun_letter_words(self, sun_processor):
        """Test common words with sun letters"""
        sun_words = [
            "الشمس",  # the sun
            "الدرس",  # the lesson
            "الرجل",  # the man
            "النور",  # the light
            "الصباح", # the morning
            "الطعام", # the food
            "السماء", # the sky
            "الليل",  # the night
        ]
        
        for word in sun_words:
            assert sun_processor.detect_sun_letter_pattern(word) is True, f"Failed: {word}"
    
    def test_common_moon_letter_words(self, sun_processor):
        """Test common words with moon letters"""
        moon_words = [
            "القمر",   # the moon
            "الكتاب", # the book
            "المدرسة",# the school
            "البيت",  # the house
            "الولد",  # the boy
            "الجبل",  # the mountain
        ]
        
        for word in moon_words:
            assert sun_processor.detect_sun_letter_pattern(word) is False, f"Failed: {word}"


# Test statistics
def test_sun_letter_accuracy():
    """Calculate overall sun letter detection accuracy"""
    processor = SunLetterProcessor("EG")
    
    # 8 sun letter words
    sun_words = ["الشمس", "الدرس", "الرجل", "النور", "الصباح", "الطعام", "السماء", "الليل"]
    
    # 6 moon letter words
    moon_words = ["القمر", "الكتاب", "المدرسة", "البيت", "الولد", "الجبل"]
    
    correct = 0
    total = len(sun_words) + len(moon_words)
    
    # Test sun words
    for word in sun_words:
        if processor.detect_sun_letter_pattern(word) is True:
            correct += 1
    
    # Test moon words
    for word in moon_words:
        if processor.detect_sun_letter_pattern(word) is False:
            correct += 1
    
    accuracy = (correct / total) * 100
    print(f"\nSun/moon letter detection accuracy: {accuracy:.1f}% ({correct}/{total})")
    
    assert accuracy == 100.0, f"Accuracy {accuracy}% is below 100%"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
