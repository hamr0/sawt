#!/usr/bin/env python3
"""
Diagnose syllable segmentation issues in detail.

Shows exactly how words are being segmented and why they're marked as UNKNOWN.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.syllabifier import ArabicSyllabifier


def diagnose_word(word, dialect='EG'):
    """Diagnose how a single word is being segmented."""

    print(f"\n{'='*70}")
    print(f"Word: {word}")
    print(f"{'='*70}")

    syllabifier = ArabicSyllabifier(dialect)

    # Get raw segmentation
    syllables = syllabifier.segment(word)

    print(f"\nSegmentation ({len(syllables)} syllables):")
    for i, syl in enumerate(syllables, 1):
        pattern = syllabifier.classify_pattern(syl)
        chars_str = ''.join(syl)
        chars_list = ', '.join(syl)

        print(f"  Syllable {i}: [{chars_str}]")
        print(f"    Characters: {chars_list}")
        print(f"    Pattern: {pattern}")

        # Show C/V breakdown
        cv_breakdown = []
        for char in syl:
            if char in syllabifier.short_vowels:
                cv_breakdown.append(f"{char}(V)")
            elif char in syllabifier.long_vowel_markers:
                cv_breakdown.append(f"{char}(V/C?)")
            elif char == syllabifier.sukun:
                cv_breakdown.append(f"{char}(sukun)")
            elif char == syllabifier.shadda:
                cv_breakdown.append(f"{char}(shadda)")
            elif char in syllabifier.tanween:
                cv_breakdown.append(f"{char}(tanween)")
            else:
                cv_breakdown.append(f"{char}(C)")

        print(f"    Breakdown: {' + '.join(cv_breakdown)}")

        if 'UNKNOWN' in pattern:
            print(f"    ⚠ PROBLEM: Invalid pattern!")


def main():
    """Test problem words."""

    print("=" * 70)
    print("Syllable Segmentation Diagnostic")
    print("=" * 70)

    # Test words with known UNKNOWN patterns
    test_cases = [
        # CVVV cases (shadda + vowel issues)
        ('نِيَّة', 'niyyah - ending with shadda + vowel (CVVV)'),
        ('عِيُّ', 'iyy - from الطبيعي (CVVV)'),
        ('سِيُّ', 'siyy - from الرئيسي (CVVV)'),

        # CVCCVV cases (consonant clusters)
        ('لِلْغَاز', 'lilghaaz - article + cluster (CVCCVV)'),
        ('مَعْرُوف', 'maaruuf - cluster + long vowel (CVCCVV)'),

        # CVCCVVC cases
        ('تَخْفِيض', 'takhfiid - complex cluster (CVCCVVC)'),

        # Simple case that should work
        ('مُدَرِّس', 'mudarris - teacher (should be CV+CVC+CVC)'),
    ]

    for word, description in test_cases:
        print(f"\n\n{description}")
        diagnose_word(word)

    print("\n" + "=" * 70)
    print("Diagnostic Complete")
    print("=" * 70)

    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print("""
The syllabifier is likely:
1. Not splitting at shadda (gemination) correctly
2. Keeping too many characters in one syllable
3. Not handling sukun + consonant clusters properly

Expected behavior:
- Shadda should SPLIT syllables: مُدَرِّس → مُ + دَرْ + رِس
- Sukun marks coda: لِلْ → لِ + لْ (but this might need resyllabification)
- Long vowels are: short_vowel + matching_marker (َا, ُو, ِي)
    """)


if __name__ == '__main__':
    main()
