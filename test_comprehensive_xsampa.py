#!/usr/bin/env python3
"""
Test comprehensive X-SAMPA conversion with 10 sample Arabic words.
Compares old (20 mappings) vs new (50+ mappings) converter.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import ArabicTTS

# Test words covering different phonetic features
test_words = [
    ("صباح", "morning - emphatic s + pharyngeal"),
    ("طعام", "food - emphatic t + pharyngeal"),
    ("ضرب", "hit - emphatic d"),
    ("ظهر", "back - emphatic dh"),
    ("قلب", "heart - qaf"),
    ("عين", "eye - pharyngeal ayn"),
    ("حب", "love - pharyngeal h"),
    ("غيم", "cloud - gh"),
    ("خير", "good - kh"),
    ("ذهب", "gold - dh"),
]

def main():
    print("=" * 80)
    print("COMPREHENSIVE X-SAMPA TEST")
    print("=" * 80)
    print("\nTesting 10 Arabic words with comprehensive X-SAMPA converter")
    print("Focus: Emphatics, pharyngeals, and dialect-specific phonemes\n")

    tts = ArabicTTS('MSA')

    for word, description in test_words:
        print(f"\n{'='*80}")
        print(f"Word: {word} ({description})")
        print(f"{'='*80}")

        result = tts.process_text(word)

        if result['words']:
            word_obj = result['words'][0]
            print(f"  Diacritized: {word_obj.get('diacritized', 'N/A')}")

            # Extract IPA and X-SAMPA
            ipa_parts = []
            xsampa_parts = []

            for syllable in word_obj.get('syllables', []):
                ipa = syllable.get('ipa', '')
                xsampa = syllable.get('xsampa', '')

                ipa_parts.append(ipa)
                xsampa_parts.append(xsampa)

                print(f"  Syllable: {syllable.get('syllable', '')} | Pattern: {syllable.get('pattern', '')}")
                print(f"    IPA:     {ipa}")
                print(f"    X-SAMPA: {xsampa}")

            full_ipa = ''.join(ipa_parts)
            full_xsampa = ''.join(xsampa_parts)

            print(f"\n  FULL IPA:     {full_ipa}")
            print(f"  FULL X-SAMPA: {full_xsampa}")

            # Check if X-SAMPA is ASCII-safe (no unconverted IPA)
            has_unconverted = any(ord(c) > 127 for c in full_xsampa if c not in ['[', ']'])

            if has_unconverted:
                print(f"  ⚠️  WARNING: X-SAMPA contains non-ASCII characters (unconverted IPA)")
            else:
                print(f"  ✅ X-SAMPA is ASCII-safe (ready for Polly)")

        else:
            print(f"  ❌ ERROR: No words returned")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\nNext step: Test these X-SAMPA strings with Polly to verify pronunciation quality")
    print("Expected: All X-SAMPA should be ASCII-safe with no unconverted IPA characters")


if __name__ == '__main__':
    main()
