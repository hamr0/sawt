#!/usr/bin/env python3
"""
XTTS (Coqui TTS) Integration Test

Test voice cloning with Arabic text from our pipeline
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def check_xtts_installation():
    """Check if XTTS is installed"""
    try:
        from TTS.api import TTS
        print("✅ XTTS installed")
        return True
    except ImportError:
        print("❌ XTTS not installed")
        print("\nInstall with:")
        print("  pip install TTS")
        print("\nOptional (for GPU acceleration):")
        print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        return False


def test_xtts_simple():
    """Test XTTS with simple Arabic text"""
    print("\n" + "=" * 80)
    print("XTTS SIMPLE TEST")
    print("=" * 80)

    try:
        from TTS.api import TTS

        # Initialize XTTS
        print("\n📥 Loading XTTS model (first time downloads ~1.8GB)...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        print("✅ Model loaded")

        # Test text
        test_text = "صباح الخير يا صديقي العزيز"
        print(f"\n📝 Test text: {test_text}")

        # You need a voice sample (10 seconds of Arabic speech)
        # For testing, we'll show what the code would be
        voice_sample = "/path/to/voice_sample.wav"

        print("\n⚠️  NOTE: You need to provide a voice sample!")
        print("   Record 10 seconds of Arabic speech and save as WAV")
        print(f"   Expected path: {voice_sample}")

        # Check if sample exists
        if not Path(voice_sample).exists():
            print("\n💡 To create a voice sample:")
            print("   1. Record yourself or someone speaking Arabic (10 seconds)")
            print("   2. Save as 'voice_sample.wav'")
            print("   3. Place in: /home/hamr/PycharmProjects/ArabicTTS/audio/voice_samples/")
            print("\nSkipping synthesis for now...")
            return False

        # Generate audio
        output_path = "/home/hamr/PycharmProjects/ArabicTTS/audio/xtts_tests/simple_test.wav"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        print(f"\n🎤 Synthesizing with XTTS...")
        tts.tts_to_file(
            text=test_text,
            speaker_wav=voice_sample,
            language="ar",
            file_path=output_path
        )

        print(f"✅ Audio generated: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_xtts_pipeline_integration():
    """Test XTTS with our full pipeline"""
    print("\n" + "=" * 80)
    print("XTTS + PIPELINE INTEGRATION TEST")
    print("=" * 80)

    try:
        from TTS.api import TTS
        from src.main import ArabicTTS

        # Initialize
        print("\n📥 Loading models...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        pipeline = ArabicTTS(dialect='EG')
        print("✅ Models loaded")

        # Test text
        test_text = "كان يا ما كان في قديم الزمان رجل فقير"
        print(f"\n📝 Test text: {test_text}")

        # Process through pipeline
        print("\n🔄 Processing through pipeline...")
        result = pipeline.process_text(test_text, dialect='EG')

        # Extract processed text (with diacritics)
        processed_words = []
        for word in result.get('words', []):
            if word.get('type') == 'arabic_word':
                syllables = [syl['syllable'] for syl in word.get('syllables', [])]
                processed_words.append(''.join(syllables))

        processed_text = ' '.join(processed_words)
        print(f"   Processed: {processed_text}")

        # Voice sample
        voice_sample = "/home/hamr/PycharmProjects/ArabicTTS/audio/voice_samples/narrator.wav"

        if not Path(voice_sample).exists():
            print(f"\n⚠️  Voice sample not found: {voice_sample}")
            print("   Skipping synthesis...")
            return False

        # Generate audio
        output_path = "/home/hamr/PycharmProjects/ArabicTTS/audio/xtts_tests/pipeline_test.wav"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        print(f"\n🎤 Synthesizing with XTTS...")
        tts.tts_to_file(
            text=processed_text,  # Use diacritized text
            speaker_wav=voice_sample,
            language="ar",
            file_path=output_path
        )

        print(f"✅ Audio generated: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_xtts_multivoice():
    """Test XTTS with multiple character voices"""
    print("\n" + "=" * 80)
    print("XTTS MULTI-VOICE TEST")
    print("=" * 80)

    try:
        from TTS.api import TTS
        import soundfile as sf
        import numpy as np

        # Initialize
        print("\n📥 Loading XTTS model...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        print("✅ Model loaded")

        # Story with multiple characters
        story_segments = [
            {
                'text': 'كان يا ما كان في قديم الزمان رجل اسمه أحمد',
                'character': 'narrator',
                'voice_sample': 'audio/voice_samples/narrator.wav'
            },
            {
                'text': 'قال أحمد: مرحباً يا فاطمة!',
                'character': 'أحمد',
                'voice_sample': 'audio/voice_samples/male_character.wav'
            },
            {
                'text': 'قالت فاطمة: أهلاً يا أحمد! كيف حالك؟',
                'character': 'فاطمة',
                'voice_sample': 'audio/voice_samples/female_character.wav'
            },
            {
                'text': 'وعاشوا في سعادة وهناء',
                'character': 'narrator',
                'voice_sample': 'audio/voice_samples/narrator.wav'
            }
        ]

        print(f"\n📖 Story with {len(story_segments)} segments")

        # Check voice samples
        voice_samples_dir = Path("/home/hamr/PycharmProjects/ArabicTTS/audio/voice_samples")
        missing_samples = []

        for seg in story_segments:
            sample_path = Path(seg['voice_sample'])
            if not sample_path.exists():
                missing_samples.append(str(sample_path))

        if missing_samples:
            print("\n⚠️  Missing voice samples:")
            for sample in set(missing_samples):
                print(f"   - {sample}")

            print("\n💡 Create voice samples:")
            print("   1. Narrator: Record warm, neutral voice (10 sec)")
            print("   2. Male character: Record male voice (10 sec)")
            print("   3. Female character: Record female voice (10 sec)")
            print(f"\n   Save to: {voice_samples_dir}/")
            return False

        # Generate audio for each segment
        audio_segments = []

        for i, seg in enumerate(story_segments, 1):
            print(f"\n🎤 Segment {i}/{len(story_segments)}: {seg['character']}")
            print(f"   Text: {seg['text'][:50]}...")

            output_path = f"/home/hamr/PycharmProjects/ArabicTTS/audio/xtts_tests/segment_{i}.wav"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            tts.tts_to_file(
                text=seg['text'],
                speaker_wav=seg['voice_sample'],
                language="ar",
                file_path=output_path
            )

            print(f"   ✅ Generated: {output_path}")
            audio_segments.append(output_path)

        # Combine all segments
        print("\n🔗 Combining segments...")
        combined_audio = []
        sample_rate = None

        for segment_path in audio_segments:
            audio, sr = sf.read(segment_path)
            if sample_rate is None:
                sample_rate = sr
            combined_audio.append(audio)

            # Add 0.5 second pause
            pause = np.zeros(int(0.5 * sr))
            combined_audio.append(pause)

        # Concatenate
        full_audio = np.concatenate(combined_audio)

        # Save combined audiobook
        output_path = "/home/hamr/PycharmProjects/ArabicTTS/audio/xtts_tests/multivoice_story.wav"
        sf.write(output_path, full_audio, sample_rate)

        print(f"✅ Multi-voice audiobook generated: {output_path}")
        print(f"   Duration: ~{len(full_audio)/sample_rate:.1f} seconds")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_setup_instructions():
    """Show setup instructions for XTTS"""
    print("\n" + "=" * 80)
    print("XTTS SETUP INSTRUCTIONS")
    print("=" * 80)

    print("\n📦 Installation:")
    print("   pip install TTS")
    print("\n   Optional (GPU acceleration):")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")

    print("\n🎤 Voice Sample Requirements:")
    print("   - Length: 6-10 seconds minimum")
    print("   - Format: WAV (16-bit PCM, 22050 Hz recommended)")
    print("   - Quality: Clear recording, minimal background noise")
    print("   - Content: Natural speech in Arabic")

    print("\n📁 Directory Structure:")
    print("   audio/")
    print("   ├── voice_samples/")
    print("   │   ├── narrator.wav       # Narrator voice (10 sec)")
    print("   │   ├── male_character.wav # Male character voice")
    print("   │   └── female_character.wav # Female character voice")
    print("   └── xtts_tests/")
    print("       └── (generated audio)")

    print("\n💡 Recording Tips:")
    print("   1. Use Audacity or any audio recorder")
    print("   2. Speak naturally (not reading, conversing)")
    print("   3. Good example: Tell a short story in Arabic")
    print("   4. Save as WAV format")

    print("\n⚡ Performance:")
    print("   - CPU: ~10-30 seconds per minute of audio")
    print("   - GPU: ~2-5 seconds per minute of audio")
    print("   - First run downloads 1.8GB model")

    print("\n🔗 Resources:")
    print("   - GitHub: https://github.com/coqui-ai/TTS")
    print("   - Docs: https://tts.readthedocs.io/")


def main():
    """Main test runner"""
    print("=" * 80)
    print("XTTS (Coqui TTS) Integration Test")
    print("=" * 80)

    # Check installation
    if not check_xtts_installation():
        show_setup_instructions()
        return

    print("\n📋 Test Options:")
    print("   1. Simple test (single voice)")
    print("   2. Pipeline integration test (mishkal + XTTS)")
    print("   3. Multi-voice test (3 characters)")

    # For now, run simple test
    print("\n🚀 Running simple test...")
    success = test_xtts_simple()

    if success:
        print("\n✅ XTTS test passed!")
        print("\nNext steps:")
        print("   1. Create voice samples (see instructions above)")
        print("   2. Run multi-voice test")
        print("   3. Compare quality to Azure and Festival")
    else:
        print("\n⚠️  Test incomplete - voice samples needed")
        show_setup_instructions()


if __name__ == '__main__':
    main()
