#!/usr/bin/env python3
"""
Festival TTS Simple Test using text2wave

Tests Festival with text2wave command (more reliable than Festival scripts)
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main import ArabicTTS


def test_festival_with_text2wave():
    """Test Festival using text2wave command"""
    print("=" * 80)
    print("FESTIVAL TTS TEST (using text2wave)")
    print("=" * 80)

    pipeline = ArabicTTS(dialect='EG')
    output_dir = Path("/home/hamr/PycharmProjects/ArabicTTS/audio/festival_tests")
    output_dir.mkdir(parents=True, exist_ok=True)

    test_cases = [
        {
            "text": "السلام عليكم ورحمة الله وبركاته",
            "description": "Greeting"
        },
        {
            "text": "صباح الخير يا صديقي العزيز",
            "description": "Good morning"
        }
    ]

    for test_idx, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {test_idx}: {test['description']}")
        print(f"Text: {test['text']}")
        print("=" * 80)

        # Mode 1: Plain text
        print("\n[Mode 1] Plain Text")
        output_plain = output_dir / f"test_{test_idx}_plain.wav"

        result = subprocess.run(
            ['text2wave', '-eval', '(voice_ara_norm_ziad_hts)', '-o', str(output_plain)],
            input=test['text'],
            text=True,
            capture_output=True,
            timeout=30
        )

        if result.returncode == 0 and output_plain.exists():
            size = output_plain.stat().st_size
            print(f"  ✅ Generated: {output_plain.name} ({size} bytes)")
        else:
            print(f"  ❌ Failed: {result.stderr}")

        # Mode 2: Mishkal diacritized
        print("\n[Mode 2] Mishkal Diacritized")
        result_pipeline = pipeline.process_text(test['text'], dialect='EG')

        # Extract diacritized text
        diacritized_words = []
        for word in result_pipeline.get('words', []):
            if word.get('type') == 'arabic_word':
                syllables = [syl['syllable'] for syl in word.get('syllables', [])]
                diacritized_words.append(''.join(syllables))
            elif word.get('type') == 'punct':
                diacritized_words.append(word.get('original', ''))

        diacritized_text = ''.join(diacritized_words)
        print(f"  Diacritized: {diacritized_text}")

        output_mishkal = output_dir / f"test_{test_idx}_mishkal.wav"

        result = subprocess.run(
            ['text2wave', '-eval', '(voice_ara_norm_ziad_hts)', '-o', str(output_mishkal)],
            input=diacritized_text,
            text=True,
            capture_output=True,
            timeout=30
        )

        if result.returncode == 0 and output_mishkal.exists():
            size = output_mishkal.stat().st_size
            print(f"  ✅ Generated: {output_mishkal.name} ({size} bytes)")
        else:
            print(f"  ❌ Failed: {result.stderr}")

    print("\n" + "=" * 80)
    print("FESTIVAL TEST COMPLETE")
    print("=" * 80)
    print(f"\n📁 Audio files: {output_dir}/")
    print("\n🎧 Files generated:")
    for i in [1, 2]:
        print(f"\n  Test {i}:")
        print(f"    - test_{i}_plain.wav (plain text)")
        print(f"    - test_{i}_mishkal.wav (mishkal diacritized)")
    print("\n📊 Compare:")
    print("  Listen to: test_1_plain.wav vs test_1_mishkal.wav")
    print("  Question: Is mishkal diacritization noticeably better?")


if __name__ == '__main__':
    test_festival_with_text2wave()
