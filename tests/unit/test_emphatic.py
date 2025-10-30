"""
Comprehensive unit tests for Emphatic Spread Processor
Tests pharyngealization spread from emphatic consonants to adjacent vowels
Target: 100% detection and pharyngealization accuracy
"""
import pytest
from src.core.emphatic import EmphaticProcessor


@pytest.fixture
def emphatic_processor():
    """Egyptian Arabic emphatic processor"""
    return EmphaticProcessor("EG")


class TestEmphaticConsonantDetection:
    """Test detection of emphatic consonants"""
    
    def test_sad_is_emphatic(self, emphatic_processor):
        """Test ص is emphatic"""
        assert emphatic_processor.is_emphatic_consonant('ص') is True
    
    def test_daad_is_emphatic(self, emphatic_processor):
        """Test ض is emphatic"""
        assert emphatic_processor.is_emphatic_consonant('ض') is True
    
    def test_taa_is_emphatic(self, emphatic_processor):
        """Test ط is emphatic"""
        assert emphatic_processor.is_emphatic_consonant('ط') is True
    
    def test_dhaa_is_emphatic(self, emphatic_processor):
        """Test ظ is emphatic"""
        assert emphatic_processor.is_emphatic_consonant('ظ') is True
    
    def test_qaaf_is_emphatic(self, emphatic_processor):
        """Test ق is emphatic"""
        assert emphatic_processor.is_emphatic_consonant('ق') is True
    
    def test_kaaf_not_emphatic(self, emphatic_processor):
        """Test ك is not emphatic"""
        assert emphatic_processor.is_emphatic_consonant('ك') is False
    
    def test_baa_not_emphatic(self, emphatic_processor):
        """Test ب is not emphatic"""
        assert emphatic_processor.is_emphatic_consonant('ب') is False
    
    def test_meem_not_emphatic(self, emphatic_processor):
        """Test م is not emphatic"""
        assert emphatic_processor.is_emphatic_consonant('م') is False


class TestWordEmphaticDetection:
    """Test detection of emphatic consonants in words"""
    
    def test_sabaah_has_emphatic(self, emphatic_processor):
        """Test صباح (morning) has emphatic"""
        assert emphatic_processor.detect_emphatic_words("صباح") is True
    
    def test_daw_has_emphatic(self, emphatic_processor):
        """Test ضوء (light) has emphatic"""
        assert emphatic_processor.detect_emphatic_words("ضوء") is True
    
    def test_taaaam_has_emphatic(self, emphatic_processor):
        """Test طعام (food) has emphatic"""
        assert emphatic_processor.detect_emphatic_words("طعام") is True
    
    def test_dhil_has_emphatic(self, emphatic_processor):
        """Test ظل (shadow) has emphatic"""
        assert emphatic_processor.detect_emphatic_words("ظل") is True
    
    def test_qamar_has_emphatic(self, emphatic_processor):
        """Test قمر (moon) has emphatic"""
        assert emphatic_processor.detect_emphatic_words("قمر") is True
    
    def test_kitaab_no_emphatic(self, emphatic_processor):
        """Test كتاب (book) has no emphatic"""
        assert emphatic_processor.detect_emphatic_words("كتاب") is False
    
    def test_bayt_no_emphatic(self, emphatic_processor):
        """Test بيت (house) has no emphatic"""
        assert emphatic_processor.detect_emphatic_words("بيت") is False
    
    def test_madrasa_no_emphatic(self, emphatic_processor):
        """Test مدرسة (school) has no emphatic"""
        assert emphatic_processor.detect_emphatic_words("مدرسة") is False


class TestSyllableProcessing:
    """Test processing syllables to detect emphatic spread"""
    
    def test_process_syllable_with_sad(self, emphatic_processor):
        """Test processing syllable with ص"""
        syllables = [{"syllable": "صَ"}]
        result = emphatic_processor.process(syllables)
        
        assert result[0]["has_emphatic"] is True
        assert result[0]["pharyngealization_spread"] is True
        assert result[0]["emphatic_consonants"] == ['ص']
    
    def test_process_syllable_with_daad(self, emphatic_processor):
        """Test processing syllable with ض"""
        syllables = [{"syllable": "ضَ"}]
        result = emphatic_processor.process(syllables)
        
        assert result[0]["has_emphatic"] is True
        assert result[0]["emphatic_consonants"] == ['ض']
    
    def test_process_syllable_with_taa(self, emphatic_processor):
        """Test processing syllable with ط"""
        syllables = [{"syllable": "طَ"}]
        result = emphatic_processor.process(syllables)
        
        assert result[0]["has_emphatic"] is True
        assert result[0]["emphatic_consonants"] == ['ط']
    
    def test_process_syllable_without_emphatic(self, emphatic_processor):
        """Test processing syllable without emphatic"""
        syllables = [{"syllable": "كَ"}]
        result = emphatic_processor.process(syllables)
        
        assert result[0]["has_emphatic"] is False
        assert result[0]["pharyngealization_spread"] is False
    
    def test_process_multiple_syllables(self, emphatic_processor):
        """Test processing multiple syllables"""
        syllables = [
            {"syllable": "صَ"},
            {"syllable": "بَاح"}
        ]
        result = emphatic_processor.process(syllables)
        
        # First syllable has emphatic
        assert result[0]["has_emphatic"] is True
        # Second syllable does not
        assert result[1]["has_emphatic"] is False


class TestPharyngealizedVowelMapping:
    """Test vowel pharyngealization mapping"""
    
    def test_a_to_backed_a(self, emphatic_processor):
        """Test /a/ → /ɑ/"""
        result = emphatic_processor.get_pharyngealized_vowel('a')
        assert result == 'ɑ'
    
    def test_i_to_backed_i(self, emphatic_processor):
        """Test /i/ → /ɪ/"""
        result = emphatic_processor.get_pharyngealized_vowel('i')
        assert result == 'ɪ'
    
    def test_u_to_backed_u(self, emphatic_processor):
        """Test /u/ → /ʊ/"""
        result = emphatic_processor.get_pharyngealized_vowel('u')
        assert result == 'ʊ'
    
    def test_aa_to_backed_aa(self, emphatic_processor):
        """Test /aː/ → /ɑː/"""
        result = emphatic_processor.get_pharyngealized_vowel('aː')
        assert result == 'ɑː'
    
    def test_ii_to_backed_ii(self, emphatic_processor):
        """Test /iː/ → /ɪː/"""
        result = emphatic_processor.get_pharyngealized_vowel('iː')
        assert result == 'ɪː'
    
    def test_uu_to_backed_uu(self, emphatic_processor):
        """Test /uː/ → /ʊː/"""
        result = emphatic_processor.get_pharyngealized_vowel('uː')
        assert result == 'ʊː'


class TestPharyngealizationApplication:
    """Test application of pharyngealization to IPA"""
    
    def test_apply_pharyngealization_sad(self, emphatic_processor):
        """Test pharyngealization with ص"""
        syllables = [{"syllable": "صَ", "ipa": "sa"}]
        detected = emphatic_processor.process(syllables)
        result = emphatic_processor.apply_pharyngealization(detected)
        
        assert result[0]["pharyngealized_ipa"] == "sˁɑ"
        assert result[0]["original_ipa_before_emphatic"] == "sa"
    
    def test_apply_pharyngealization_daad(self, emphatic_processor):
        """Test pharyngealization with ض"""
        syllables = [{"syllable": "ضَ", "ipa": "da"}]
        detected = emphatic_processor.process(syllables)
        result = emphatic_processor.apply_pharyngealization(detected)
        
        assert result[0]["pharyngealized_ipa"] == "dˁɑ"
        assert result[0]["original_ipa_before_emphatic"] == "da"
    
    def test_apply_pharyngealization_taa(self, emphatic_processor):
        """Test pharyngealization with ط"""
        syllables = [{"syllable": "طَ", "ipa": "ta"}]
        detected = emphatic_processor.process(syllables)
        result = emphatic_processor.apply_pharyngealization(detected)
        
        assert result[0]["pharyngealized_ipa"] == "tˁɑ"
    
    def test_apply_pharyngealization_dhaa(self, emphatic_processor):
        """Test pharyngealization with ظ"""
        syllables = [{"syllable": "ظَ", "ipa": "ða"}]
        detected = emphatic_processor.process(syllables)
        result = emphatic_processor.apply_pharyngealization(detected)
        
        assert result[0]["pharyngealized_ipa"] == "ðˁɑ"
    
    def test_apply_pharyngealization_qaaf(self, emphatic_processor):
        """Test pharyngealization with ق"""
        syllables = [{"syllable": "قَ", "ipa": "qa"}]
        detected = emphatic_processor.process(syllables)
        result = emphatic_processor.apply_pharyngealization(detected)
        
        assert result[0]["pharyngealized_ipa"] == "qˁɑ"
    
    def test_no_pharyngealization_on_non_emphatic(self, emphatic_processor):
        """Test no pharyngealization on non-emphatic syllables"""
        syllables = [{"syllable": "كَ", "ipa": "ka"}]
        detected = emphatic_processor.process(syllables)
        result = emphatic_processor.apply_pharyngealization(detected)
        
        # Should not have pharyngealized_ipa key
        assert "pharyngealized_ipa" not in result[0]


class TestVowelBacking:
    """Test vowel backing implementation"""
    
    def test_vowel_backing_a(self, emphatic_processor):
        """Test backing /a/ in IPA"""
        ipa = emphatic_processor._apply_vowel_backing("sa")
        assert ipa == "sɑ"
    
    def test_vowel_backing_i(self, emphatic_processor):
        """Test backing /i/ in IPA"""
        ipa = emphatic_processor._apply_vowel_backing("si")
        assert ipa == "sɪ"
    
    def test_vowel_backing_u(self, emphatic_processor):
        """Test backing /u/ in IPA"""
        ipa = emphatic_processor._apply_vowel_backing("su")
        assert ipa == "sʊ"
    
    def test_vowel_backing_long_a(self, emphatic_processor):
        """Test backing /aː/ in IPA"""
        ipa = emphatic_processor._apply_vowel_backing("saː")
        assert ipa == "sɑː"
    
    def test_vowel_backing_multiple_vowels(self, emphatic_processor):
        """Test backing multiple vowels"""
        ipa = emphatic_processor._apply_vowel_backing("satiba")
        assert ipa == "sɑtɪbɑ"


class TestPharyngealizationMarkers:
    """Test adding pharyngealization markers"""
    
    def test_add_marker_to_sad(self, emphatic_processor):
        """Test adding ˁ marker to ص"""
        ipa = emphatic_processor._add_pharyngealization_markers("sa", ['ص'])
        assert ipa == "sˁa"
    
    def test_add_marker_to_daad(self, emphatic_processor):
        """Test adding ˁ marker to ض"""
        ipa = emphatic_processor._add_pharyngealization_markers("da", ['ض'])
        assert ipa == "dˁa"
    
    def test_add_marker_to_taa(self, emphatic_processor):
        """Test adding ˁ marker to ط"""
        ipa = emphatic_processor._add_pharyngealization_markers("ta", ['ط'])
        assert ipa == "tˁa"
    
    def test_no_marker_without_emphatic(self, emphatic_processor):
        """Test no marker added without emphatic consonants"""
        ipa = emphatic_processor._add_pharyngealization_markers("ka", [])
        assert ipa == "ka"


class TestRealWorldExamples:
    """Test with real Arabic words"""
    
    def test_sabaah_morning(self, emphatic_processor):
        """Test صباح (morning)"""
        syllables = [
            {"syllable": "صَ", "ipa": "sa"},
            {"syllable": "بَاح", "ipa": "baːħ"}
        ]
        detected = emphatic_processor.process(syllables)
        result = emphatic_processor.apply_pharyngealization(detected)
        
        # First syllable should be pharyngealized
        assert result[0]["pharyngealized_ipa"] == "sˁɑ"
        # Second syllable should not
        assert "pharyngealized_ipa" not in result[1]
    
    def test_taaaam_food(self, emphatic_processor):
        """Test طعام (food)"""
        syllables = [
            {"syllable": "طَ", "ipa": "ta"},
            {"syllable": "عَام", "ipa": "ʕaːm"}
        ]
        detected = emphatic_processor.process(syllables)
        result = emphatic_processor.apply_pharyngealization(detected)
        
        assert result[0]["pharyngealized_ipa"] == "tˁɑ"
    
    def test_kitaab_book_no_emphatic(self, emphatic_processor):
        """Test كتاب (book) - no emphatic"""
        syllables = [
            {"syllable": "كِ", "ipa": "ki"},
            {"syllable": "تَاب", "ipa": "taːb"}
        ]
        detected = emphatic_processor.process(syllables)
        result = emphatic_processor.apply_pharyngealization(detected)
        
        # No syllables should be pharyngealized
        assert "pharyngealized_ipa" not in result[0]
        assert "pharyngealized_ipa" not in result[1]


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_syllable_list(self, emphatic_processor):
        """Test empty syllable list"""
        result = emphatic_processor.process([])
        assert result == []
    
    def test_syllable_without_syllable_key(self, emphatic_processor):
        """Test syllable without 'syllable' key"""
        syllables = [{"ipa": "test"}]
        result = emphatic_processor.process(syllables)
        
        assert len(result) == 1
        assert result[0]["has_emphatic"] is False
    
    def test_syllable_without_ipa(self, emphatic_processor):
        """Test syllable without IPA"""
        syllables = [{"syllable": "صَ"}]
        detected = emphatic_processor.process(syllables)
        result = emphatic_processor.apply_pharyngealization(detected)
        
        # Should not crash, just no pharyngealized_ipa
        assert len(result) == 1


class TestEmphaticConsonantSet:
    """Test the complete set of emphatic consonants"""
    
    def test_all_five_emphatic_consonants(self, emphatic_processor):
        """Test all 5 emphatic consonants are defined"""
        emphatics = ['ص', 'ض', 'ط', 'ظ', 'ق']
        
        for char in emphatics:
            assert emphatic_processor.is_emphatic_consonant(char) is True, f"{char} should be emphatic"
    
    def test_non_emphatic_consonants(self, emphatic_processor):
        """Test non-emphatic consonants"""
        non_emphatics = ['ك', 'ب', 'م', 'ن', 'ل', 'ر', 'س', 'ت', 'د']
        
        for char in non_emphatics:
            assert emphatic_processor.is_emphatic_consonant(char) is False, f"{char} should not be emphatic"


# Test statistics
def test_emphatic_detection_accuracy():
    """Calculate overall emphatic detection accuracy"""
    processor = EmphaticProcessor("EG")
    
    # Words with emphatic consonants (5 words)
    emphatic_words = ["صباح", "ضوء", "طعام", "ظل", "قمر"]
    
    # Words without emphatic consonants (5 words)
    non_emphatic_words = ["كتاب", "بيت", "مدرسة", "ولد", "جبل"]
    
    correct = 0
    total = len(emphatic_words) + len(non_emphatic_words)
    
    # Test emphatic words
    for word in emphatic_words:
        if processor.detect_emphatic_words(word) is True:
            correct += 1
    
    # Test non-emphatic words
    for word in non_emphatic_words:
        if processor.detect_emphatic_words(word) is False:
            correct += 1
    
    accuracy = (correct / total) * 100
    print(f"\nEmphatic detection accuracy: {accuracy:.1f}% ({correct}/{total})")
    
    assert accuracy == 100.0, f"Accuracy {accuracy}% is below 100%"


def test_pharyngealization_application_accuracy():
    """Calculate pharyngealization application accuracy"""
    processor = EmphaticProcessor("EG")
    
    test_cases = [
        ('ص', 'sa', 'sˁɑ'),
        ('ض', 'da', 'dˁɑ'),
        ('ط', 'ta', 'tˁɑ'),
        ('ظ', 'ða', 'ðˁɑ'),
        ('ق', 'qa', 'qˁɑ'),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for char, input_ipa, expected_ipa in test_cases:
        syllables = [{'syllable': char + 'َ', 'ipa': input_ipa}]
        detected = processor.process(syllables)
        result = processor.apply_pharyngealization(detected)
        
        if result[0].get('pharyngealized_ipa') == expected_ipa:
            correct += 1
    
    accuracy = (correct / total) * 100
    print(f"\nPharyngealization application accuracy: {accuracy:.1f}% ({correct}/{total})")
    
    assert accuracy == 100.0, f"Accuracy {accuracy}% is below 100%"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
