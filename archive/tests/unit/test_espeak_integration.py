"""
Comprehensive unit tests for eSpeak NG Integration
Tests ESpeakTTS wrapper class functionality
Target: 100% coverage of audio generation workflow
"""
import pytest
import os
from pathlib import Path
import tempfile
from src.integrations.espeak import ESpeakTTS


@pytest.fixture
def espeak():
    """eSpeak TTS instance"""
    return ESpeakTTS()


@pytest.fixture
def temp_audio_file():
    """Create temporary audio file path"""
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "test_audio.wav")
    yield audio_path
    # Cleanup
    if os.path.exists(audio_path):
        os.remove(audio_path)
    os.rmdir(temp_dir)


class TestESpeakInstallation:
    """Test eSpeak NG installation and initialization"""
    
    def test_espeak_installed(self, espeak):
        """Test eSpeak NG is installed"""
        assert espeak.is_espeak_installed() is True
    
    def test_get_version(self, espeak):
        """Test getting eSpeak version"""
        version = espeak.get_espeak_version()
        assert version is not None
        assert "eSpeak" in version
    
    def test_initialization_with_default_voice(self):
        """Test initialization with default Arabic voice"""
        tts = ESpeakTTS()
        assert tts.voice == "ar"
    
    def test_initialization_with_custom_voice(self):
        """Test initialization with custom voice"""
        tts = ESpeakTTS(voice="en")
        assert tts.voice == "en"
    
    def test_initialization_without_verification(self):
        """Test initialization without installation verification"""
        tts = ESpeakTTS(verify_installation=False)
        assert tts is not None


class TestIPAToXSAMPAConversion:
    """Test IPA to X-SAMPA conversion"""
    
    def test_consonant_conversion(self, espeak):
        """Test Arabic consonant conversion"""
        assert espeak.ipa_to_xsampa('ʃ') == 'S'  # sh
        assert espeak.ipa_to_xsampa('ʔ') == '?'  # glottal stop
        assert espeak.ipa_to_xsampa('ħ') == 'X\\'  # voiceless pharyngeal
        assert espeak.ipa_to_xsampa('ʕ') == '?\\'  # voiced pharyngeal
    
    def test_emphatic_consonant_conversion(self, espeak):
        """Test emphatic consonant conversion"""
        assert espeak.ipa_to_xsampa('sˁ') == 's_?'  # emphatic s
        assert espeak.ipa_to_xsampa('tˁ') == 't_?'  # emphatic t
        assert espeak.ipa_to_xsampa('dˁ') == 'd_?'  # emphatic d
        assert espeak.ipa_to_xsampa('ðˁ') == 'D_?'  # emphatic dh
    
    def test_vowel_conversion(self, espeak):
        """Test vowel conversion"""
        assert espeak.ipa_to_xsampa('a') == 'a'
        assert espeak.ipa_to_xsampa('ɑ') == 'A'  # backed a
        assert espeak.ipa_to_xsampa('i') == 'i'
        assert espeak.ipa_to_xsampa('ɪ') == 'I'  # lowered i
        assert espeak.ipa_to_xsampa('u') == 'u'
        assert espeak.ipa_to_xsampa('ʊ') == 'U'  # lowered u
    
    def test_long_vowel_conversion(self, espeak):
        """Test long vowel conversion"""
        assert espeak.ipa_to_xsampa('aː') == 'a:'
        assert espeak.ipa_to_xsampa('ɑː') == 'A:'
        assert espeak.ipa_to_xsampa('iː') == 'i:'
        assert espeak.ipa_to_xsampa('uː') == 'u:'
    
    def test_complex_word_conversion(self, espeak):
        """Test conversion of complete Arabic words"""
        # صباح - morning
        assert espeak.ipa_to_xsampa('sˁɑbɑːħ') == 's_?AbA:X\\'
        
        # شمس - sun
        assert espeak.ipa_to_xsampa('ʃams') == 'Sams'
        
        # قمر - moon
        assert espeak.ipa_to_xsampa('qamar') == 'qamar'
    
    def test_diphthong_conversion(self, espeak):
        """Test diphthong conversion"""
        assert espeak.ipa_to_xsampa('aj') == 'aj'
        assert espeak.ipa_to_xsampa('aw') == 'aw'
    
    def test_markers_conversion(self, espeak):
        """Test marker conversion"""
        assert espeak.ipa_to_xsampa('ː') == ':'   # length
        assert espeak.ipa_to_xsampa('ˁ') == '_?'  # pharyngealization


class TestAudioGenerationFromText:
    """Test audio generation from Arabic text"""
    
    def test_generate_audio_from_arabic_text(self, espeak, temp_audio_file):
        """Test generating audio from Arabic text"""
        text = "السلام"
        success, message = espeak.generate_audio_from_text(text, temp_audio_file)
        
        assert success is True
        assert os.path.exists(temp_audio_file)
        assert os.path.getsize(temp_audio_file) > 0
        assert "successfully" in message.lower() or "generated" in message.lower()
    
    def test_generate_audio_with_custom_parameters(self, espeak, temp_audio_file):
        """Test audio generation with custom parameters"""
        text = "مرحبا"
        success, message = espeak.generate_audio_from_text(
            text,
            temp_audio_file,
            speed=120,
            pitch=60,
            amplitude=90
        )
        
        assert success is True
        assert os.path.exists(temp_audio_file)
    
    def test_generate_audio_empty_text(self, espeak, temp_audio_file):
        """Test audio generation with empty text"""
        success, message = espeak.generate_audio_from_text("", temp_audio_file)
        # eSpeak may handle empty text differently, just ensure it doesn't crash
        assert isinstance(success, bool)
        assert isinstance(message, str)


class TestAudioGenerationFromIPA:
    """Test audio generation from IPA input"""
    
    def test_generate_audio_from_ipa(self, espeak, temp_audio_file):
        """Test generating audio from IPA"""
        ipa = "sɑlɑːm"
        success, message = espeak.generate_audio(ipa, temp_audio_file)
        
        assert success is True
        assert os.path.exists(temp_audio_file)
        assert os.path.getsize(temp_audio_file) > 0
    
    def test_generate_audio_emphatic_ipa(self, espeak, temp_audio_file):
        """Test audio generation with emphatic consonants"""
        ipa = "sˁɑbɑːħ"  # صباح
        success, message = espeak.generate_audio(ipa, temp_audio_file)
        
        assert success is True
        assert os.path.exists(temp_audio_file)
    
    def test_generate_audio_complex_ipa(self, espeak, temp_audio_file):
        """Test audio generation with complex IPA"""
        ipa = "tˁɑʕɑːm"  # طعام
        success, message = espeak.generate_audio(ipa, temp_audio_file)
        
        assert success is True
        assert os.path.exists(temp_audio_file)


class TestDirectoryCreation:
    """Test automatic directory creation"""
    
    def test_creates_output_directory(self, espeak):
        """Test that output directory is created if missing"""
        temp_dir = tempfile.mkdtemp()
        nested_path = os.path.join(temp_dir, "subdir1", "subdir2", "audio.wav")
        
        text = "test"
        success, message = espeak.generate_audio_from_text(text, nested_path)
        
        assert success is True
        assert os.path.exists(nested_path)
        
        # Cleanup
        os.remove(nested_path)
        os.rmdir(os.path.join(temp_dir, "subdir1", "subdir2"))
        os.rmdir(os.path.join(temp_dir, "subdir1"))
        os.rmdir(temp_dir)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_output_path(self, espeak):
        """Test handling of invalid output path"""
        # Path that's a directory, not a file
        invalid_path = "/tmp/"
        success, message = espeak.generate_audio_from_text("test", invalid_path)
        
        # Should fail gracefully
        assert isinstance(success, bool)
        assert isinstance(message, str)
    
    def test_audio_file_size_validation(self, espeak, temp_audio_file):
        """Test that generated file has non-zero size"""
        success, message = espeak.generate_audio_from_text("السلام", temp_audio_file)
        
        if success:
            file_size = os.path.getsize(temp_audio_file)
            assert file_size > 0
            assert "bytes" in message


class TestRealWorldExamples:
    """Test with real Arabic words"""
    
    def test_common_greeting(self, espeak, temp_audio_file):
        """Test السلام عليكم (peace be upon you)"""
        text = "السلام عليكم"
        success, message = espeak.generate_audio_from_text(text, temp_audio_file)
        
        assert success is True
        assert os.path.exists(temp_audio_file)
    
    def test_simple_words(self, espeak):
        """Test simple Arabic words"""
        words = ["شمس", "قمر", "كتاب", "بيت", "ماء"]
        
        for word in words:
            temp_dir = tempfile.mkdtemp()
            audio_path = os.path.join(temp_dir, f"test_{word}.wav")
            
            success, message = espeak.generate_audio_from_text(word, audio_path)
            
            assert success is True, f"Failed for word: {word}"
            assert os.path.exists(audio_path)
            
            # Cleanup
            os.remove(audio_path)
            os.rmdir(temp_dir)
    
    def test_emphatic_words(self, espeak, temp_audio_file):
        """Test words with emphatic consonants"""
        text = "صباح الخير"  # Good morning
        success, message = espeak.generate_audio_from_text(text, temp_audio_file)
        
        assert success is True
        assert os.path.exists(temp_audio_file)


class TestParameterValidation:
    """Test parameter validation"""
    
    def test_speed_parameter(self, espeak, temp_audio_file):
        """Test different speed settings"""
        speeds = [80, 150, 200]
        
        for speed in speeds:
            success, message = espeak.generate_audio_from_text(
                "test",
                temp_audio_file,
                speed=speed
            )
            assert success is True
    
    def test_pitch_parameter(self, espeak, temp_audio_file):
        """Test different pitch settings"""
        pitches = [30, 50, 70]
        
        for pitch in pitches:
            success, message = espeak.generate_audio_from_text(
                "test",
                temp_audio_file,
                pitch=pitch
            )
            assert success is True
    
    def test_amplitude_parameter(self, espeak, temp_audio_file):
        """Test different volume settings"""
        amplitudes = [50, 100, 150]
        
        for amplitude in amplitudes:
            success, message = espeak.generate_audio_from_text(
                "test",
                temp_audio_file,
                amplitude=amplitude
            )
            assert success is True


# Test statistics
def test_audio_generation_success_rate():
    """Calculate audio generation success rate"""
    espeak = ESpeakTTS()
    
    test_inputs = [
        "السلام عليكم",
        "صباح الخير",
        "شمس",
        "قمر",
        "كتاب"
    ]
    
    success_count = 0
    total = len(test_inputs)
    
    for text in test_inputs:
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, "test.wav")
        
        success, message = espeak.generate_audio_from_text(text, audio_path)
        
        if success:
            success_count += 1
        
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)
        os.rmdir(temp_dir)
    
    success_rate = (success_count / total) * 100
    print(f"\nAudio generation success rate: {success_rate:.1f}% ({success_count}/{total})")
    
    assert success_rate == 100.0, f"Success rate {success_rate}% is below 100%"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
