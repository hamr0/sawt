#!/usr/bin/env python3
"""
Test edge cases for syllabification:
- Multiple shadda (gemination)
- Complex consonant clusters
- Long vowel chains
"""

import sys
import os
sys.path.insert(0, '/home/hamr/PycharmProjects/ArabicTTS')

from src.main import ArabicSyllabifier

def test_edge_cases():
    syllabifier = ArabicSyllabifier()

    # Edge case test words
    test_cases = [
        # Multiple shadda cases
        ("مُحَمَّد", "Multiple shadda (gemination)"),
        ("مُشَدَّد", "Double shadda"),

        # Complex consonant clusters
        ("اِسْتَخْرَجَ", "Complex initial cluster (str)"),
        ("مُسْتَقْبَل", "Multiple clusters"),
        ("اِسْتِثْنَاء", "Triple consonant cluster"),

        # Long vowel chains
        ("جَاءَ", "Hamza with long vowel"),
        ("سَاءَ", "Long vowel + hamza"),
        ("مَاءٌ", "Word-final long vowel"),

        # Complex combinations
        ("الْمُسْتَشْفَى", "Clusters + long vowel"),
        ("اَلإِسْكَنْدَرِيَّة", "Clusters + shadda + long vowel"),

        # Edge case patterns from corpus
        ("تَخْفِيضٍ", "CVCCVVC pattern"),
        ("بِأَعْلَى", "CCVC pattern"),
        ("حُسِيَتْ", "CVVVC pattern"),
    ]

    print("=" * 70)
    print("Edge Case Testing for ArabicSyllabifier")
    print("=" * 70)
    print()

    success_count = 0
    total_count = len(test_cases)

    for word, description in test_cases:
        # Syllabify the word
        syllables = syllabifier.resyllabify([[char] for char in word])

        # Check if syllabification succeeded
        if syllables and len(syllables) > 0:
            # Classify each syllable
            patterns = []
            all_valid = True
            for syll in syllables:
                pattern = syllabifier.classify_pattern(syll)
                patterns.append(pattern)
                if pattern.startswith('UNKNOWN'):
                    all_valid = False

            # Format output
            syllable_strs = [' '.join(s) for s in syllables]
            pattern_str = ', '.join(patterns)

            if all_valid:
                status = "✓ PASS"
                success_count += 1
            else:
                status = "✗ FAIL (UNKNOWN pattern)"

            print(f"{status:20} {word:15} | {description:30}")
            print(f"                     Syllables: {' | '.join(syllable_strs)}")
            print(f"                     Patterns:  {pattern_str}")
        else:
            status = "✗ FAIL (no syllables)"
            print(f"{status:20} {word:15} | {description:30}")

        print()

    print("=" * 70)
    print(f"RESULTS: {success_count}/{total_count} edge cases passed ({100*success_count/total_count:.1f}%)")
    print("=" * 70)

    return success_count == total_count

if __name__ == '__main__':
    success = test_edge_cases()
    sys.exit(0 if success else 1)
