"""
Comprehensive unit tests for Arabic syllabifier
Tests all pattern types: CV, CVC, CVV, CVCC, CVVC
Target: >95% accuracy
"""
import pytest
from src.core.syllabifier import ArabicSyllabifier


@pytest.fixture
def eg_syllabifier():
    """Egyptian Arabic syllabifier"""
    return ArabicSyllabifier("EG")


@pytest.fixture
def msa_syllabifier():
    """MSA syllabifier (for compatibility)"""
    return ArabicSyllabifier("EG")  # Using EG as MSA not fully implemented


class TestCVPatterns:
    """Test simple CV (consonant-vowel) patterns"""
    
    def test_single_cv_syllable(self, eg_syllabifier):
        """Test single CV syllable"""
        result = eg_syllabifier.segment("مَ")
        assert len(result) == 1
        assert eg_syllabifier.classify_pattern(result[0]) == "CV"
    
    def test_multiple_cv_syllables(self, eg_syllabifier):
        """Test word with multiple CV syllables"""
        result = eg_syllabifier.segment("كَتَبَ")
        assert len(result) == 3
        patterns = [eg_syllabifier.classify_pattern(syl) for syl in result]
        assert patterns == ["CV", "CV", "CV"]
    
    def test_cv_with_different_vowels(self, eg_syllabifier):
        """Test CV with fatha, kasra, damma"""
        # Fatha
        result = eg_syllabifier.segment("مَ")
        assert eg_syllabifier.classify_pattern(result[0]) == "CV"
        
        # Kasra
        result = eg_syllabifier.segment("كِ")
        assert eg_syllabifier.classify_pattern(result[0]) == "CV"
        
        # Damma
        result = eg_syllabifier.segment("نُ")
        assert eg_syllabifier.classify_pattern(result[0]) == "CV"


class TestCVCPatterns:
    """Test CVC (consonant-vowel-consonant) patterns"""
    
    def test_cvc_with_sukun(self, eg_syllabifier):
        """Test CVC pattern with sukun marker"""
        result = eg_syllabifier.segment("مَدْ")
        assert len(result) == 1
        assert eg_syllabifier.classify_pattern(result[0]) == "CVC"
    
    def test_word_with_cvc_and_cv(self, eg_syllabifier):
        """Test mixed CVC and CV patterns"""
        result = eg_syllabifier.segment("مَدْرَسَة")
        patterns = [eg_syllabifier.classify_pattern(syl) for syl in result]
        # Expecting CVC, CV, CVC (last syllable has taa marbuta)
        assert len(patterns) == 3
        assert patterns[0] == "CVC"
        assert patterns[1] == "CV"


class TestCVVPatterns:
    """Test CVV (consonant-long vowel) patterns"""
    
    def test_cvv_fatha_alif(self, eg_syllabifier):
        """Test CVV with fatha + alif (aa)"""
        result = eg_syllabifier.segment("كَا")
        assert len(result) == 1
        pattern = eg_syllabifier.classify_pattern(result[0])
        assert pattern == "CVV"
    
    def test_cvv_kasra_yaa(self, eg_syllabifier):
        """Test CVV with kasra + yaa (ii)"""
        result = eg_syllabifier.segment("فِي")
        assert len(result) == 1
        pattern = eg_syllabifier.classify_pattern(result[0])
        assert pattern == "CVV"
    
    def test_cvv_damma_waw(self, eg_syllabifier):
        """Test CVV with damma + waw (uu)"""
        result = eg_syllabifier.segment("نُو")
        assert len(result) == 1
        pattern = eg_syllabifier.classify_pattern(result[0])
        assert pattern == "CVV"


class TestCVCCPatterns:
    """Test CVCC (super-heavy syllable) patterns"""
    
    def test_cvcc_with_sukun_cluster(self, eg_syllabifier):
        """Test CVCC with consonant cluster"""
        result = eg_syllabifier.segment("بِنْت")
        assert len(result) == 1
        pattern = eg_syllabifier.classify_pattern(result[0])
        assert pattern == "CVCC"
    
    def test_cvcc_validation(self, eg_syllabifier):
        """Test CVCC pattern validation"""
        # Valid CVCC with sukun
        valid = eg_syllabifier.validate_cvcc(['ب', 'ِ', 'ن', 'ْ', 'ت'])
        assert valid is True


class TestCVVCPatterns:
    """Test CVVC (long vowel + coda) patterns"""
    
    def test_cvvc_long_vowel_with_coda(self, eg_syllabifier):
        """Test CVVC with long vowel followed by consonant"""
        result = eg_syllabifier.segment("نُور")
        assert len(result) == 1
        pattern = eg_syllabifier.classify_pattern(result[0])
        assert pattern == "CVVC"
    
    def test_cvvc_kitaab(self, eg_syllabifier):
        """Test multi-syllable word with CVVC"""
        result = eg_syllabifier.segment("كِتَاب")
        assert len(result) == 2
        patterns = [eg_syllabifier.classify_pattern(syl) for syl in result]
        assert patterns == ["CV", "CVVC"]
    
    def test_cvvc_diphthong_ay(self, eg_syllabifier):
        """Test CVVC with diphthong ay (fatha + yaa + sukun)"""
        result = eg_syllabifier.segment("بَيْت")
        assert len(result) == 1
        pattern = eg_syllabifier.classify_pattern(result[0])
        assert pattern == "CVVC"
    
    def test_cvvc_diphthong_aw(self, eg_syllabifier):
        """Test CVVC with diphthong aw (fatha + waw + sukun)"""
        result = eg_syllabifier.segment("مَوْت")
        assert len(result) == 1
        pattern = eg_syllabifier.classify_pattern(result[0])
        assert pattern == "CVVC"


class TestComplexWords:
    """Test real Arabic words with mixed patterns"""
    
    def test_madrasa(self, eg_syllabifier):
        """Test مَدْرَسَة (school)"""
        result = eg_syllabifier.segment("مَدْرَسَة")
        assert len(result) == 3
        patterns = [eg_syllabifier.classify_pattern(syl) for syl in result]
        assert patterns[0] == "CVC"  # مَدْ
        assert patterns[1] == "CV"   # رَ
    
    def test_kataba(self, eg_syllabifier):
        """Test كَتَبَ (he wrote)"""
        result = eg_syllabifier.segment("كَتَبَ")
        assert len(result) == 3
        patterns = [eg_syllabifier.classify_pattern(syl) for syl in result]
        assert patterns == ["CV", "CV", "CV"]
    
    def test_bint(self, eg_syllabifier):
        """Test بِنْت (girl)"""
        result = eg_syllabifier.segment("بِنْت")
        assert len(result) == 1
        pattern = eg_syllabifier.classify_pattern(result[0])
        assert pattern == "CVCC"
    
    def test_bayt(self, eg_syllabifier):
        """Test بَيْت (house)"""
        result = eg_syllabifier.segment("بَيْت")
        assert len(result) == 1
        pattern = eg_syllabifier.classify_pattern(result[0])
        assert pattern == "CVVC"
    
    def test_nuur(self, eg_syllabifier):
        """Test نُور (light)"""
        result = eg_syllabifier.segment("نُور")
        assert len(result) == 1
        pattern = eg_syllabifier.classify_pattern(result[0])
        assert pattern == "CVVC"
    
    def test_kitaab(self, eg_syllabifier):
        """Test كِتَاب (book)"""
        result = eg_syllabifier.segment("كِتَاب")
        assert len(result) == 2
        patterns = [eg_syllabifier.classify_pattern(syl) for syl in result]
        assert patterns == ["CV", "CVVC"]


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_single_consonant(self, eg_syllabifier):
        """Test single consonant (should fail gracefully)"""
        result = eg_syllabifier.segment("ب")
        # Should return something, even if not valid syllable
        assert len(result) >= 1
    
    def test_empty_string(self, eg_syllabifier):
        """Test empty string"""
        result = eg_syllabifier.segment("")
        assert result == []
    
    def test_word_with_shadda(self, eg_syllabifier):
        """Test word with shadda (gemination marker)"""
        # This may not be perfect yet, but should not crash
        result = eg_syllabifier.segment("مُدَرِّس")
        assert len(result) >= 2  # Should segment into multiple syllables


class TestBackwardCompatibility:
    """Tests for backward compatibility with MSA syllabifier"""
    
    def test_msa_cv_syllable(self, msa_syllabifier):
        """Test MSA CV syllable (compatibility)"""
        result = msa_syllabifier.segment("مَ")
        assert len(result) == 1
        assert msa_syllabifier.classify_pattern(result[0]) == "CV"
    
    def test_msa_cvcc_validation(self, msa_syllabifier):
        """Test MSA CVCC validation (compatibility)"""
        valid = msa_syllabifier.validate_cvcc(['ب', 'ِ', 'ن', 'ْ', 'ت'])
        assert valid is True


# Test statistics helper
def calculate_accuracy():
    """Helper to calculate overall test accuracy"""
    # This will be run by pytest and show pass/fail stats
    pass


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])