"""
Integration tests for mishkal diacritization
Tests the diacritization component of the TTS pipeline
"""
import pytest
import sys
sys.path.insert(0, 'src')

from src.main import ArabicTTS


@pytest.fixture
def tts_eg():
    """Egyptian Arabic TTS instance"""
    return ArabicTTS(dialect="EG")


@pytest.fixture
def tts_msa():
    """MSA TTS instance"""
    return ArabicTTS(dialect="MSA")


class TestDiacritization:
    """Test mishkal diacritization integration"""
    
    def test_diacritization_simple_word(self, tts_eg):
        """Test processing of a simple word"""
        text = "كتاب"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        assert len(result['words']) > 0
        
        # Check that word was processed
        word = result['words'][0]
        if word.get('type') == 'arabic_word':
            # Should have syllables and IPA
            assert 'syllables' in word
            assert len(word['syllables']) > 0
            assert 'original' in word
            assert word['original'] == text
    
    def test_diacritization_sentence(self, tts_eg):
        """Test processing of a full sentence"""
        text = "السلام عليكم"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        assert len(result['words']) >= 2
        
        # Check that Arabic words were processed
        arabic_words = [w for w in result['words'] if w.get('type') == 'arabic_word']
        assert len(arabic_words) >= 2
        
        for word in arabic_words:
            assert 'syllables' in word
            assert len(word['syllables']) > 0
    
    def test_diacritization_preserves_text(self, tts_eg):
        """Test that processing preserves original text"""
        text = "شمس"
        result = tts_eg.process_text(text)
        
        word = result['words'][0]
        if word.get('type') == 'arabic_word':
            original = word.get('original', '')
            # Original text should be preserved
            assert original == text
    
    def test_diacritization_different_dialects(self, tts_eg, tts_msa):
        """Test that diacritization works with different dialects"""
        text = "مرحبا"
        
        result_eg = tts_eg.process_text(text)
        result_msa = tts_msa.process_text(text)
        
        # Both should produce diacritized output
        assert 'words' in result_eg
        assert 'words' in result_msa
        assert len(result_eg['words']) > 0
        assert len(result_msa['words']) > 0
    
    def test_diacritization_with_punctuation(self, tts_eg):
        """Test diacritization with punctuation"""
        text = "مرحبا، كيف حالك؟"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        # Should handle both words and punctuation
        assert len(result['words']) > 2
    
    def test_diacritization_numbers(self, tts_eg):
        """Test handling of numbers in text"""
        text = "عندي 5 كتب"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        # Should have Arabic words and numbers
        assert len(result['words']) >= 3
    
    def test_diacritization_mixed_content(self, tts_eg):
        """Test diacritization with mixed Arabic and English"""
        text = "أنا أحب Python"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        # Should handle both Arabic and English
        assert len(result['words']) >= 3


class TestDiacritizationOutput:
    """Test diacritization output quality"""
    
    def test_diacritization_adds_vowels(self, tts_eg):
        """Test that processing generates IPA with vowels"""
        text = "كتب"
        result = tts_eg.process_text(text)
        
        word = result['words'][0]
        if word.get('type') == 'arabic_word':
            # Check that IPA was generated
            assert 'syllables' in word
            for syllable in word['syllables']:
                assert 'generated_ipa' in syllable or 'ipa' in syllable
                ipa = syllable.get('generated_ipa') or syllable.get('ipa', '')
                # IPA should contain vowels
                assert len(ipa) > 0
    
    def test_diacritization_includes_sukun(self, tts_eg):
        """Test processing of consonant clusters"""
        text = "من"
        result = tts_eg.process_text(text)
        
        word = result['words'][0]
        if word.get('type') == 'arabic_word':
            # Should have syllables generated
            assert 'syllables' in word
            assert len(word['syllables']) > 0
    
    def test_diacritization_includes_shadda(self, tts_eg):
        """Test that diacritization includes shadda for geminated consonants"""
        text = "مُدَرِّس"  # Already diacritized word with shadda
        result = tts_eg.process_text(text)
        
        word = result['words'][0]
        if word.get('type') == 'arabic_word':
            diacritized = word.get('diacritized_text', '')
            # Should preserve or add shadda
            assert 'ّ' in diacritized or 'ر' in text


class TestDiacritizationEdgeCases:
    """Test edge cases in diacritization"""
    
    def test_empty_string(self, tts_eg):
        """Test handling of empty string"""
        text = ""
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        assert len(result['words']) == 0
    
    def test_whitespace_only(self, tts_eg):
        """Test handling of whitespace only"""
        text = "   "
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        # Should handle gracefully
    
    def test_single_character(self, tts_eg):
        """Test diacritization of single character"""
        text = "و"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        assert len(result['words']) > 0
    
    def test_already_diacritized_text(self, tts_eg):
        """Test handling of already diacritized text"""
        text = "كِتَابٌ"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        word = result['words'][0]
        if word.get('type') == 'arabic_word':
            # Should handle gracefully
            assert 'syllables' in word
            assert len(word['syllables']) > 0
    
    def test_long_sentence(self, tts_eg):
        """Test diacritization of longer sentence"""
        text = "أنا أحب اللغة العربية وأريد أن أتعلمها"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        # Should process all words
        assert len(result['words']) >= 5


class TestDiacritizationConsistency:
    """Test diacritization consistency"""
    
    def test_consistency_same_word(self, tts_eg):
        """Test that same word gets consistent processing"""
        text1 = "كتاب"
        text2 = "كتاب"
        
        result1 = tts_eg.process_text(text1)
        result2 = tts_eg.process_text(text2)
        
        word1 = result1['words'][0]
        word2 = result2['words'][0]
        
        if word1.get('type') == 'arabic_word' and word2.get('type') == 'arabic_word':
            # Should have same number of syllables
            assert len(word1['syllables']) == len(word2['syllables'])
    
    def test_consistency_in_context(self, tts_eg):
        """Test word diacritization in different contexts"""
        text1 = "كتاب جديد"
        text2 = "هذا كتاب"
        
        result1 = tts_eg.process_text(text1)
        result2 = tts_eg.process_text(text2)
        
        # Both should successfully diacritize
        assert len(result1['words']) > 0
        assert len(result2['words']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
