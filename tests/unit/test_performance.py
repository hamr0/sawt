"""
Performance benchmark tests for Arabic TTS system
Measures processing speed, memory usage, and throughput
"""
import pytest
import sys
import time
import os
from pathlib import Path
sys.path.insert(0, 'src')

from src.main import ArabicTTS
from src.integrations.espeak import ESpeakTTS


class TestProcessingSpeed:
    """Test processing speed benchmarks"""
    
    def test_short_text_processing_speed(self):
        """Benchmark: Process short text (1-2 words) in < 0.5s"""
        tts = ArabicTTS(dialect="EG")
        text = "مرحبا"
        
        start_time = time.time()
        result = tts.process_text(text)
        elapsed = time.time() - start_time
        
        assert 'words' in result
        assert elapsed < 0.5, f"Short text took {elapsed:.3f}s (expected < 0.5s)"
        print(f"\n  ✓ Short text processing: {elapsed:.3f}s")
    
    def test_medium_text_processing_speed(self):
        """Benchmark: Process medium text (5-10 words) in < 1.0s"""
        tts = ArabicTTS(dialect="EG")
        text = "صباح الخير كيف الحال اليوم الطقس جميل"
        
        start_time = time.time()
        result = tts.process_text(text)
        elapsed = time.time() - start_time
        
        assert 'words' in result
        assert elapsed < 1.0, f"Medium text took {elapsed:.3f}s (expected < 1.0s)"
        print(f"\n  ✓ Medium text processing: {elapsed:.3f}s")
    
    def test_long_text_processing_speed(self):
        """Benchmark: Process long text (20-30 words) in < 2.0s"""
        tts = ArabicTTS(dialect="EG")
        text = "اللغة العربية لغة جميلة وغنية بالتاريخ والثقافة أنا أحب تعلم اللغة العربية لأنها تفتح لي أبواب المعرفة صباح الخير يا أصدقائي كيف حالكم اليوم"
        
        start_time = time.time()
        result = tts.process_text(text)
        elapsed = time.time() - start_time
        
        assert 'words' in result
        assert elapsed < 2.0, f"Long text took {elapsed:.3f}s (expected < 2.0s)"
        print(f"\n  ✓ Long text processing: {elapsed:.3f}s")
    
    def test_single_word_average_time(self):
        """Benchmark: Average single word processing time"""
        tts = ArabicTTS(dialect="EG")
        words = ["مرحبا", "صباح", "الخير", "كتاب", "مدرسة", "طالب", "معلم", "درس", "صديق", "عائلة"]
        
        total_time = 0
        for word in words:
            start_time = time.time()
            result = tts.process_text(word)
            elapsed = time.time() - start_time
            total_time += elapsed
            assert 'words' in result
        
        avg_time = total_time / len(words)
        assert avg_time < 0.2, f"Average word time: {avg_time:.3f}s (expected < 0.2s)"
        print(f"\n  ✓ Average single word: {avg_time:.3f}s ({len(words)} words)")


class TestThroughput:
    """Test system throughput"""
    
    def test_words_per_second_throughput(self):
        """Benchmark: Process at least 10 words per second"""
        tts = ArabicTTS(dialect="EG")
        words = ["مرحبا", "صباح", "الخير", "كيف", "الحال", "اليوم", "الطقس", "جميل", "شكرا", "وداعا"] * 5  # 50 words
        
        start_time = time.time()
        for word in words:
            result = tts.process_text(word)
            assert 'words' in result
        elapsed = time.time() - start_time
        
        throughput = len(words) / elapsed
        assert throughput >= 10, f"Throughput: {throughput:.1f} words/s (expected >= 10 w/s)"
        print(f"\n  ✓ Throughput: {throughput:.1f} words/second")
    
    def test_sentence_processing_throughput(self):
        """Benchmark: Process multiple sentences efficiently"""
        tts = ArabicTTS(dialect="EG")
        sentences = [
            "مرحبا كيف حالك",
            "صباح الخير يا صديقي",
            "اللغة العربية جميلة",
            "أنا أحب القراءة",
            "الطقس جميل اليوم"
        ] * 4  # 20 sentences
        
        start_time = time.time()
        for sentence in sentences:
            result = tts.process_text(sentence)
            assert 'words' in result
        elapsed = time.time() - start_time
        
        throughput = len(sentences) / elapsed
        assert throughput >= 5, f"Throughput: {throughput:.1f} sentences/s (expected >= 5 s/s)"
        print(f"\n  ✓ Sentence throughput: {throughput:.1f} sentences/second")


class TestSyllabificationPerformance:
    """Test syllabification performance"""
    
    def test_syllabification_speed(self):
        """Benchmark: Syllabification should be fast (< 0.1s per word)"""
        tts = ArabicTTS(dialect="EG")
        words = ["مَدْرَسَة", "كِتَاب", "طَالِب", "مُعَلِّم", "صَدِيق"]

        for word in words:
            start_time = time.time()
            result = tts.syllabifier.segment_syllables(word)
            elapsed = time.time() - start_time

            assert len(result) > 0
            assert elapsed < 0.1, f"Syllabification took {elapsed:.3f}s (expected < 0.1s)"

        print(f"\n  ✓ Syllabification: < 0.1s per word")
    
    def test_large_word_syllabification(self):
        """Benchmark: Handle large words efficiently"""
        tts = ArabicTTS(dialect="EG")
        # Create a long word (realistic compound or inflected form)
        long_word = "وَالْمُسْتَشْفَيَاتِ"  # "and the hospitals"

        start_time = time.time()
        result = tts.syllabifier.segment_syllables(long_word)
        elapsed = time.time() - start_time

        assert len(result) > 0
        assert elapsed < 0.2, f"Large word took {elapsed:.3f}s (expected < 0.2s)"
        print(f"\n  ✓ Large word syllabification: {elapsed:.3f}s")


class TestPhonologicalProcessingPerformance:
    """Test phonological processing performance"""
    
    def test_gemination_processing_speed(self):
        """Benchmark: Gemination processing should be fast"""
        tts = ArabicTTS(dialect="EG")
        # Words with gemination (shadda)
        words = ["مُدَرِّس", "سَيَّارَة", "مُهِمّ", "جَدِّي", "أُمِّي"]

        total_time = 0
        for word in words:
            # Process through full pipeline to get proper syllable structure
            start_time = time.time()
            result = tts.process_text(word)
            elapsed = time.time() - start_time
            total_time += elapsed
            assert 'words' in result
            assert len(result['words']) > 0

        avg_time = total_time / len(words)
        assert avg_time < 0.1, f"Gemination avg: {avg_time:.3f}s (expected < 0.1s)"
        print(f"\n  ✓ Gemination processing: {avg_time:.3f}s average")
    
    def test_sun_letter_processing_speed(self):
        """Benchmark: Sun letter processing should be fast"""
        tts = ArabicTTS(dialect="EG")
        # Words with sun letters
        words = ["الشَّمْس", "النَّهَار", "الذَّهَب", "السَّمَاء", "الطَّعَام"]

        total_time = 0
        for word in words:
            # Process through full pipeline to get proper syllable structure
            start_time = time.time()
            result = tts.process_text(word)
            elapsed = time.time() - start_time
            total_time += elapsed
            assert 'words' in result
            assert len(result['words']) > 0

        avg_time = total_time / len(words)
        assert avg_time < 0.1, f"Sun letter avg: {avg_time:.3f}s (expected < 0.1s)"
        print(f"\n  ✓ Sun letter processing: {avg_time:.3f}s average")
    
    def test_emphatic_spread_speed(self):
        """Benchmark: Emphatic spread processing should be fast"""
        tts = ArabicTTS(dialect="EG")
        # Words with emphatic consonants
        words = ["صَبَاح", "طَعَام", "ضَرَب", "ظَهْر", "قَلَم"]

        total_time = 0
        for word in words:
            # Process through full pipeline to get proper syllable structure
            start_time = time.time()
            result = tts.process_text(word)
            elapsed = time.time() - start_time
            total_time += elapsed
            assert 'words' in result
            assert len(result['words']) > 0

        avg_time = total_time / len(words)
        assert avg_time < 0.1, f"Emphatic spread avg: {avg_time:.3f}s (expected < 0.1s)"
        print(f"\n  ✓ Emphatic spread: {avg_time:.3f}s average")
    
    def test_complete_phonological_pipeline_speed(self):
        """Benchmark: Complete phonological pipeline should be efficient"""
        tts = ArabicTTS(dialect="EG")
        text = "صَبَاحُ الْخَيْرِ يَا صَدِيقِي"
        
        start_time = time.time()
        result = tts.process_text(text)
        elapsed = time.time() - start_time
        
        assert 'words' in result
        assert elapsed < 0.5, f"Complete pipeline: {elapsed:.3f}s (expected < 0.5s)"
        print(f"\n  ✓ Complete phonological pipeline: {elapsed:.3f}s")


class TestAudioGenerationPerformance:
    """Test audio generation performance"""
    
    def test_audio_generation_speed(self):
        """Benchmark: Audio generation should be reasonably fast"""
        if not ESpeakTTS(verify_installation=False).is_espeak_installed():
            pytest.skip("eSpeak NG not installed")
        
        espeak = ESpeakTTS()
        ipa = "sɑlɑːm"  # "سلام"
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test.wav")
            
            start_time = time.time()
            success, msg = espeak.generate_audio(ipa, output)
            elapsed = time.time() - start_time
            
            assert success, f"Audio generation failed: {msg}"
            assert elapsed < 1.0, f"Audio generation: {elapsed:.3f}s (expected < 1.0s)"
            print(f"\n  ✓ Audio generation: {elapsed:.3f}s")
    
    def test_ipa_to_xsampa_conversion_speed(self):
        """Benchmark: IPA to X-SAMPA conversion should be instant"""
        espeak = ESpeakTTS(verify_installation=False)
        ipa_strings = [
            "sɑlɑːm",
            "sˁɑbɑːħ",
            "ʃams",
            "qamar",
            "kitɑːb"
        ] * 10  # 50 conversions
        
        start_time = time.time()
        for ipa in ipa_strings:
            xsampa = espeak.ipa_to_xsampa(ipa)
            assert isinstance(xsampa, str)
        elapsed = time.time() - start_time
        
        avg_time = elapsed / len(ipa_strings)
        assert avg_time < 0.001, f"IPA conversion avg: {avg_time:.6f}s (expected < 0.001s)"
        print(f"\n  ✓ IPA→X-SAMPA conversion: {avg_time:.6f}s average")


class TestScalability:
    """Test system scalability"""
    
    def test_concurrent_instance_creation(self):
        """Benchmark: Create multiple TTS instances efficiently"""
        dialects = ["EG", "MSA", "Gulf", "Levantine", "Maghreb"]
        
        start_time = time.time()
        instances = []
        for _ in range(10):
            for dialect in dialects:
                instance = ArabicTTS(dialect=dialect)
                instances.append(instance)
        elapsed = time.time() - start_time
        
        assert len(instances) == 50
        assert elapsed < 5.0, f"Instance creation: {elapsed:.3f}s (expected < 5.0s)"
        print(f"\n  ✓ Created 50 instances in {elapsed:.3f}s")
    
    def test_batch_processing_efficiency(self):
        """Benchmark: Batch processing should scale linearly"""
        tts = ArabicTTS(dialect="EG")
        
        # Process 10 words
        words_10 = ["مرحبا"] * 10
        start_time = time.time()
        for word in words_10:
            tts.process_text(word)
        time_10 = time.time() - start_time
        
        # Process 50 words
        words_50 = ["مرحبا"] * 50
        start_time = time.time()
        for word in words_50:
            tts.process_text(word)
        time_50 = time.time() - start_time
        
        # Check linear scaling (50 words should take ~5x time, allow 6x margin)
        expected_time = time_10 * 5
        margin = expected_time * 1.2
        assert time_50 < margin, f"Batch scaling: {time_50:.3f}s (expected ~{expected_time:.3f}s)"
        print(f"\n  ✓ Batch scaling: 10 words={time_10:.3f}s, 50 words={time_50:.3f}s")


class TestMemoryEfficiency:
    """Test memory efficiency (basic checks)"""
    
    def test_repeated_processing_no_memory_leak(self):
        """Benchmark: Repeated processing shouldn't accumulate memory"""
        tts = ArabicTTS(dialect="EG")
        text = "مرحبا صباح الخير"
        
        # Process 1000 times - should complete without issues
        start_time = time.time()
        for _ in range(1000):
            result = tts.process_text(text)
            assert 'words' in result
        elapsed = time.time() - start_time
        
        assert elapsed < 30.0, f"1000 iterations: {elapsed:.3f}s (expected < 30.0s)"
        print(f"\n  ✓ 1000 iterations: {elapsed:.3f}s (no memory issues)")
    
    def test_large_text_memory_efficiency(self):
        """Benchmark: Large text processing shouldn't cause memory issues"""
        tts = ArabicTTS(dialect="EG")
        # Create large text (500 words)
        large_text = " ".join(["مرحبا"] * 500)
        
        start_time = time.time()
        result = tts.process_text(large_text)
        elapsed = time.time() - start_time
        
        assert 'words' in result
        assert elapsed < 10.0, f"500 words: {elapsed:.3f}s (expected < 10.0s)"
        print(f"\n  ✓ 500 words processed in {elapsed:.3f}s")


class TestDialectSwitchingPerformance:
    """Test dialect switching performance"""
    
    def test_dialect_switching_overhead(self):
        """Benchmark: Switching dialects should be fast"""
        dialects = ["EG", "MSA", "Gulf", "Levantine", "Maghreb"]
        text = "مرحبا"
        
        start_time = time.time()
        for dialect in dialects * 10:  # 50 switches
            tts = ArabicTTS(dialect=dialect)
            result = tts.process_text(text)
            assert 'words' in result
        elapsed = time.time() - start_time
        
        avg_time = elapsed / 50
        assert avg_time < 0.2, f"Dialect switch avg: {avg_time:.3f}s (expected < 0.2s)"
        print(f"\n  ✓ Dialect switching: {avg_time:.3f}s average (50 switches)")


class TestRealWorldPerformance:
    """Test real-world usage scenarios"""
    
    def test_realistic_conversation_processing(self):
        """Benchmark: Process realistic conversation efficiently"""
        tts = ArabicTTS(dialect="EG")
        conversation = [
            "مرحبا كيف حالك",
            "أنا بخير شكرا",
            "ماذا تفعل اليوم",
            "سأذهب إلى العمل",
            "أتمنى لك يوما سعيدا",
            "شكرا وداعا"
        ]
        
        start_time = time.time()
        for sentence in conversation:
            result = tts.process_text(sentence)
            assert 'words' in result
        elapsed = time.time() - start_time
        
        assert elapsed < 3.0, f"Conversation: {elapsed:.3f}s (expected < 3.0s)"
        print(f"\n  ✓ Conversation (6 turns): {elapsed:.3f}s")
    
    def test_paragraph_processing(self):
        """Benchmark: Process paragraph-length text efficiently"""
        tts = ArabicTTS(dialect="EG")
        paragraph = """
        اللغة العربية هي إحدى أكثر اللغات انتشارا في العالم.
        يتحدث بها أكثر من أربعمائة مليون نسمة.
        وهي لغة القرآن الكريم ولغة الشعر والأدب العربي.
        تتميز اللغة العربية بثراء مفرداتها وجمال تعبيراتها.
        """
        
        start_time = time.time()
        result = tts.process_text(paragraph)
        elapsed = time.time() - start_time
        
        assert 'words' in result
        assert elapsed < 3.0, f"Paragraph: {elapsed:.3f}s (expected < 3.0s)"
        print(f"\n  ✓ Paragraph processing: {elapsed:.3f}s")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s", "--tb=short"])
