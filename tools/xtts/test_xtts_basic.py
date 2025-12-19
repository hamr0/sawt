#!/usr/bin/env python3
"""
XTTS Basic Test Script
Test XTTS (Coqui TTS) with Arabic text using mishkal diacritization

Based on: OPENSOURCE_ARABIC_TTS_OPTIONS.md
Purpose: Evaluate if XTTS can provide production-quality Arabic TTS
         as a FREE alternative to Azure
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from TTS.api import TTS
from src.main import ArabicTTS
import time


def test_xtts_arabic():
    """Test XTTS with Arabic text"""

    print("=" * 80)
    print("XTTS Arabic TTS Test")
    print("=" * 80)

    # Test samples
    test_samples = [
        {
            'name': 'Simple greeting',
            'text': 'صباح الخير يا أصدقائي'
        },
        {
            'name': 'Short sentence',
            'text': 'هذا اختبار لنظام تحويل النص إلى كلام باللغة العربية'
        },
        {
            'name': 'Longer passage',
            'text': '''في يوم من الأيام، كان هناك رجل حكيم يعيش في قرية صغيرة.
كان الناس يأتون إليه من كل مكان لطلب النصيحة والحكمة.
وكان دائماً يقول لهم: الصبر مفتاح الفرج.'''
        }
    ]

    # Initialize our pipeline for mishkal diacritization
    print("\n1. Initializing Arabic TTS pipeline (for mishkal diacritization)...")
    pipeline = ArabicTTS(dialect='EG')

    # Initialize XTTS
    print("\n2. Initializing XTTS...")
    print("   Checking available models...")

    # Set environment variable to agree to license (non-commercial use)
    os.environ['COQUI_TOS_AGREED'] = '1'

    # List available models
    print("\n   Available XTTS models:")
    try:
        # XTTS v2 is multilingual and supports Arabic
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        print(f"   Using: {model_name}")
        print("   Note: Using XTTS under non-commercial CPML license")

        tts = TTS(model_name, progress_bar=True, gpu=False)
        print(f"   ✓ Model loaded successfully")
        print(f"   Languages supported: {tts.languages if hasattr(tts, 'languages') else 'Multiple including Arabic'}")

    except Exception as e:
        print(f"   ✗ Error loading model: {e}")
        return

    # Output directory
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    # Reference audio for voice cloning
    ref_audio = Path(__file__).parent / "reference_audio" / "arabic_ref.wav"
    print(f"\n   Using reference audio: {ref_audio}")

    # Test each sample
    for idx, sample in enumerate(test_samples, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {idx}/{len(test_samples)}: {sample['name']}")
        print(f"{'=' * 80}")

        text = sample['text']
        print(f"Original text: {text[:100]}...")

        # Option 1: Plain text
        print(f"\n   Testing: Plain text (no diacritization)")
        output_path_plain = output_dir / f"test{idx}_plain.wav"

        try:
            start_time = time.time()

            tts.tts_to_file(
                text=text,
                language="ar",  # Arabic
                speaker_wav=str(ref_audio),  # Voice cloning reference
                file_path=str(output_path_plain)
            )

            elapsed = time.time() - start_time
            file_size = output_path_plain.stat().st_size / 1024  # KB

            print(f"   ✓ Generated: {output_path_plain}")
            print(f"   Time: {elapsed:.2f}s")
            print(f"   Size: {file_size:.1f} KB")

        except Exception as e:
            print(f"   ✗ Error: {e}")
            continue

        # Option 2: With mishkal diacritization
        print(f"\n   Testing: Mishkal diacritized text")
        output_path_mishkal = output_dir / f"test{idx}_mishkal.wav"

        try:
            # Get diacritized text from our pipeline
            result = pipeline.process_text(text, dialect='EG')

            # Extract diacritized text
            diacritized_words = []
            for word in result.get('words', []):
                if word.get('type') == 'arabic_word':
                    diacritized_words.append(word.get('text', ''))
                elif word.get('type') == 'non_arabic':
                    diacritized_words.append(word.get('text', ''))

            diacritized_text = ' '.join(diacritized_words)
            print(f"   Diacritized: {diacritized_text[:100]}...")

            start_time = time.time()

            tts.tts_to_file(
                text=diacritized_text,
                language="ar",
                speaker_wav=str(ref_audio),  # Voice cloning reference
                file_path=str(output_path_mishkal)
            )

            elapsed = time.time() - start_time
            file_size = output_path_mishkal.stat().st_size / 1024  # KB

            print(f"   ✓ Generated: {output_path_mishkal}")
            print(f"   Time: {elapsed:.2f}s")
            print(f"   Size: {file_size:.1f} KB")

        except Exception as e:
            print(f"   ✗ Error: {e}")

    # Summary
    print(f"\n{'=' * 80}")
    print("Test Complete!")
    print(f"{'=' * 80}")
    print(f"\nGenerated audio files in: {output_dir}")
    print("\nNext steps:")
    print("1. Listen to the audio files to evaluate quality")
    print("2. Compare with eSpeak baseline")
    print("3. Compare with Azure/Festival quality")
    print("\nKey questions:")
    print("- Is quality acceptable for audiobook production? (Target: ⭐⭐⭐⭐)")
    print("- Does mishkal diacritization improve quality?")
    print("- Is it better than Festival (⭐⭐⭐)?")
    print("- Does it approach Azure quality (⭐⭐⭐⭐⭐)?")


if __name__ == "__main__":
    test_xtts_arabic()
