#!/usr/bin/env python3
"""
Test syllabification with ACTUAL diacritized output from TTS.

This will show us what the real issue is.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.main import ArabicTTS
from src.core.syllabifier import ArabicSyllabifier


def test_real_output():
    """Test with actual TTS diacritized output."""

    print("=" * 70)
    print("Testing Real TTS Output")
    print("=" * 70)

    test_words = [
        'للغاز',     # Should be simple
        'الطبيعي',   # Has نِيَّ problem
        'الرئيسي',   # Has سِيُّ problem
        'البدري',    # Has بَدْرِيُّ problem
        'مدرس',      # Simpler version of teacher
    ]

    tts = ArabicTTS('MSA')
    syllabifier = ArabicSyllabifier('EG')

    for word in test_words:
        print(f"\n{'='*70}")
        print(f"Original: {word}")
        print(f"{'='*70}")

        result = tts.process_text(word)
        words_data = result.get('words', [])

        if not words_data:
            print("  ERROR: No words in result")
            continue

        # Get diacritized form
        syllables = words_data[0].get('syllables', [])

        if not syllables:
            print("  ERROR: No syllables in result")
            continue

        print(f"\nTTS produced {len(syllables)} syllables:")

        for i, syl in enumerate(syllables, 1):
            syllable_text = syl.get('syllable', '')
            diacritized = syl.get('diacritized', syllable_text)
            pattern = syl.get('pattern', '')
            chars = syl.get('chars', [])

            print(f"\n  Syllable {i}: [{syllable_text}]")
            print(f"    Diacritized: {diacritized}")
            print(f"    Pattern: {pattern}")
            print(f"    Chars: {', '.join(chars)}")

            if 'UNKNOWN' in pattern:
                print(f"    ⚠ UNKNOWN PATTERN!")

                # Try to manually segment and classify
                print(f"\n    Manual analysis:")
                manual_segs = syllabifier.segment(diacritized)
                for j, seg in enumerate(manual_segs, 1):
                    manual_pattern = syllabifier.classify_pattern(seg)
                    print(f"      Seg {j}: {''.join(seg)} → {manual_pattern}")


if __name__ == '__main__':
    test_real_output()
