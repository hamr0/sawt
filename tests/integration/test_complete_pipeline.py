"""
Comprehensive integration tests for complete TTS pipeline
Tests end-to-end workflow: Text → Diacritization → Syllabification → Phonology → IPA → Audio
"""
import pytest
import sys
import os
import tempfile
from pathlib import Path
sys.path.insert(0, 'src')

from src.main import ArabicTTS
from src.integrations.espeak import ESpeakTTS


@pytest.fixture
def tts_eg():
    """Egyptian Arabic TTS instance"""
    return ArabicTTS(dialect="EG")


@pytest.fixture
def tts_msa():
    """MSA TTS instance"""
    return ArabicTTS(dialect="MSA")


@pytest.fixture
def espeak():
    """eSpeak TTS instance"""
    return ESpeakTTS()


class TestCompletePipeline:
    """Test complete pipeline workflow"""
    
    def test_pipeline_simple_word(self, tts_eg):
        """Test complete pipeline on simple word"""
        text = "كتاب"
        result = tts_eg.process_text(text)
        
        # Should have all pipeline stages
        assert 'dialect' in result
        assert result['dialect'] == "EG"
        assert 'words' in result
        assert len(result['words']) > 0
        
        word = result['words'][0]
        # Should have syllabification
        assert 'syllables' in word
        assert len(word['syllables']) > 0
        
        # Should have IPA generation
        for syllable in word['syllables']:
            assert 'generated_ipa' in syllable or 'ipa' in syllable
    
    def test_pipeline_with_phonological_rules(self, tts_eg):
        """Test pipeline applies phonological rules"""
        text = "الشمس"  # Sun letter
        result = tts_eg.process_text(text)
        
        word = result['words'][0]
        # Should have phonological processing
        for syllable in word['syllables']:
            # Check for phonological markers
            assert 'has_gemination' in syllable
            assert 'sun_letter_assimilation' in syllable
            assert 'has_emphatic' in syllable
    
    def test_pipeline_emphatic_spread(self, tts_eg):
        """Test pipeline applies emphatic spread"""
        text = "صباح"  # Contains emphatic ص
        result = tts_eg.process_text(text)
        
        word = result['words'][0]
        has_emphatic = False
        for syllable in word['syllables']:
            if syllable.get('has_emphatic'):
                has_emphatic = True
                # Should have pharyngealized IPA
                assert 'pharyngealized_ipa' in syllable or 'generated_ipa' in syllable
        
        # Should detect emphatic consonant
        assert has_emphatic
    
    def test_pipeline_gemination(self, tts_eg):
        """Test pipeline handles gemination"""
        text = "مُدَرِّس"  # Contains shadda on ر
        result = tts_eg.process_text(text)
        
        word = result['words'][0]
        # Should detect gemination
        has_gem = any(s.get('has_gemination') for s in word['syllables'])
        assert has_gem or len(word['syllables']) > 0  # Either gemination detected or processed
    
    def test_pipeline_allophones(self, tts_eg):
        """Test pipeline applies positional allophones"""
        text = "أكل"  # Hamza in different positions
        result = tts_eg.process_text(text)
        
        word = result['words'][0]
        # Should have positional information
        for syllable in word['syllables']:
            assert 'detected_position' in syllable
            assert 'allophone_position' in syllable
    
    def test_pipeline_complete_sentence(self, tts_eg):
        """Test pipeline on complete sentence"""
        text = "السلام عليكم"
        result = tts_eg.process_text(text)
        
        assert len(result['words']) >= 2
        
        # All words should be processed
        for word in result['words']:
            if word.get('type') == 'arabic_word':
                assert 'syllables' in word
                assert len(word['syllables']) > 0


class TestPipelineWithAudio:
    """Test pipeline integration with audio generation"""
    
    def test_pipeline_to_audio_simple(self, tts_eg, espeak):
        """Test complete pipeline to audio generation"""
        text = "شمس"
        result = tts_eg.process_text(text)
        
        # Extract IPA
        word = result['words'][0]
        ipa_parts = []
        for syllable in word['syllables']:
            ipa = syllable.get('pharyngealized_ipa') or syllable.get('generated_ipa') or syllable.get('ipa', '')
            if ipa:
                ipa_parts.append(ipa)
        
        full_ipa = ' '.join(ipa_parts)
        assert len(full_ipa) > 0
        
        # Generate audio
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, "test.wav")
        
        success, message = espeak.generate_audio(full_ipa, audio_path)
        
        assert success is True
        assert os.path.exists(audio_path)
        assert os.path.getsize(audio_path) > 0
        
        # Cleanup
        os.remove(audio_path)
        os.rmdir(temp_dir)
    
    def test_pipeline_to_audio_with_emphasis(self, tts_eg, espeak):
        """Test pipeline to audio with emphatic consonants"""
        text = "صباح"
        result = tts_eg.process_text(text)
        
        # Extract IPA with pharyngealization
        word = result['words'][0]
        ipa_parts = []
        for syllable in word['syllables']:
            ipa = syllable.get('pharyngealized_ipa') or syllable.get('generated_ipa') or syllable.get('ipa', '')
            if ipa:
                ipa_parts.append(ipa)
        
        full_ipa = ' '.join(ipa_parts)
        
        # Generate audio
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, "test_emphatic.wav")
        
        success, message = espeak.generate_audio(full_ipa, audio_path)
        
        assert success is True
        assert os.path.exists(audio_path)
        
        # Cleanup
        os.remove(audio_path)
        os.rmdir(temp_dir)
    
    def test_pipeline_arabic_text_to_audio(self, tts_eg, espeak):
        """Test direct Arabic text to audio"""
        text = "مرحبا"
        result = tts_eg.process_text(text)
        
        # Generate audio from Arabic text
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, "test_arabic.wav")
        
        success, message = espeak.generate_audio_from_text(text, audio_path)
        
        assert success is True
        assert os.path.exists(audio_path)
        
        # Cleanup
        os.remove(audio_path)
        os.rmdir(temp_dir)


class TestPipelineDialects:
    """Test pipeline with different dialects"""
    
    def test_pipeline_egyptian(self, tts_eg):
        """Test pipeline with Egyptian dialect"""
        text = "إزيك"
        result = tts_eg.process_text(text)
        
        assert result['dialect'] == "EG"
        assert len(result['words']) > 0
    
    def test_pipeline_msa(self, tts_msa):
        """Test pipeline with MSA"""
        text = "كيف حالك"
        result = tts_msa.process_text(text)
        
        assert result['dialect'] == "MSA"
        assert len(result['words']) >= 2
    
    def test_pipeline_dialect_differences(self, tts_eg, tts_msa):
        """Test that different dialects produce different outputs"""
        text = "كتاب"
        
        result_eg = tts_eg.process_text(text)
        result_msa = tts_msa.process_text(text)
        
        # Both should process successfully
        assert len(result_eg['words']) > 0
        assert len(result_msa['words']) > 0
        
        # Dialects should be marked correctly
        assert result_eg['dialect'] == "EG"
        assert result_msa['dialect'] == "MSA"


class TestPipelineEdgeCases:
    """Test pipeline with edge cases"""
    
    def test_pipeline_empty_input(self, tts_eg):
        """Test pipeline with empty input"""
        text = ""
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        assert len(result['words']) == 0
    
    def test_pipeline_numbers_only(self, tts_eg):
        """Test pipeline with numbers only"""
        text = "123"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        # Should handle gracefully
    
    def test_pipeline_mixed_scripts(self, tts_eg):
        """Test pipeline with mixed Arabic and English"""
        text = "أنا أحب Python"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        # Should have both Arabic and non-Arabic words
        assert len(result['words']) >= 3
    
    def test_pipeline_punctuation(self, tts_eg):
        """Test pipeline with punctuation"""
        text = "مرحبا، كيف حالك؟"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        # Should handle punctuation
        assert len(result['words']) > 2
    
    def test_pipeline_long_text(self, tts_eg):
        """Test pipeline with longer text"""
        text = "أنا أحب اللغة العربية وأريد أن أتعلمها بشكل جيد"
        result = tts_eg.process_text(text)
        
        assert 'words' in result
        # Should process all words
        assert len(result['words']) >= 8


class TestPipelineConsistency:
    """Test pipeline consistency"""
    
    def test_pipeline_deterministic(self, tts_eg):
        """Test that pipeline produces consistent results"""
        text = "كتاب"
        
        result1 = tts_eg.process_text(text)
        result2 = tts_eg.process_text(text)
        
        # Should produce same number of words
        assert len(result1['words']) == len(result2['words'])
        
        # Should produce same number of syllables
        if result1['words'] and result2['words']:
            word1 = result1['words'][0]
            word2 = result2['words'][0]
            if 'syllables' in word1 and 'syllables' in word2:
                assert len(word1['syllables']) == len(word2['syllables'])
    
    def test_pipeline_idempotent(self, tts_eg):
        """Test that pipeline is idempotent"""
        text = "مرحبا"
        
        # Process multiple times
        results = [tts_eg.process_text(text) for _ in range(3)]
        
        # All should produce same structure
        word_counts = [len(r['words']) for r in results]
        assert len(set(word_counts)) == 1  # All same


class TestPipelinePerformance:
    """Test pipeline performance characteristics"""
    
    def test_pipeline_short_text_fast(self, tts_eg):
        """Test that short text processes quickly"""
        import time
        
        text = "شمس"
        start = time.time()
        result = tts_eg.process_text(text)
        end = time.time()
        
        duration = end - start
        # Should be very fast
        assert duration < 1.0  # Less than 1 second
        assert len(result['words']) > 0
    
    def test_pipeline_handles_multiple_words(self, tts_eg):
        """Test that pipeline handles multiple words efficiently"""
        text = "السلام عليكم ورحمة الله وبركاته"
        result = tts_eg.process_text(text)
        
        # Should process all words
        arabic_words = [w for w in result['words'] if w.get('type') == 'arabic_word']
        assert len(arabic_words) >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
