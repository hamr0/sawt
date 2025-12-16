#!/usr/bin/env python3
"""
PROOF OF CONCEPT: Test if using the proper syllabifier fixes UNKNOWN patterns.

This script compares:
1. Current (broken) syllabifier in main.py
2. Proper syllabifier in syllabifier.py

Goal: Prove that switching to the proper syllabifier will fix the 26.9% UNKNOWN patterns.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.syllabifier import ArabicSyllabifier as ProperSyllabifier
from src.main import ArabicTTS


def test_proof_of_concept():
    """Compare broken vs proper syllabifier on problem words."""

    print("=" * 70)
    print("PROOF OF CONCEPT: Proper Syllabifier vs Broken Syllabifier")
    print("=" * 70)

    # Words that currently have UNKNOWN patterns
    test_cases = [
        'للغاز',      # Currently: UNKNOWN(CVCCVV)
        'الطبيعي',    # Currently: UNKNOWN(CVVV) in last syllable
        'الرئيسي',    # Currently: UNKNOWN(CVVV) in last syllable
        'البدري',     # Currently: UNKNOWN(CVCCVVV)
        'الوطنية',    # Currently: UNKNOWN(CVVV)
        'تخفيض',      # Currently: UNKNOWN(CVCCVVC)
    ]

    # Get TTS instance (uses broken syllabifier)
    tts = ArabicTTS('MSA')

    # Get proper syllabifier (from syllabifier.py)
    proper_syllabifier = ProperSyllabifier('EG')  # Use EG since MSA patterns not in JSON

    print("\nTesting on problem words:\n")

    total_tested = 0
    fixed_count = 0

    for word in test_cases:
        print(f"{'='*70}")
        print(f"Word: {word}")
        print(f"{'='*70}")

        # Step 1: Get diacritized form from TTS
        result = tts.process_text(word)
        words_data = result.get('words', [])

        if not words_data:
            print("  ERROR: No words in TTS result\n")
            continue

        syllables = words_data[0].get('syllables', [])
        if not syllables:
            print("  ERROR: No syllables in TTS result\n")
            continue

        # Find syllables with UNKNOWN patterns
        unknown_syllables = []
        for syl in syllables:
            pattern = syl.get('pattern', '')
            if 'UNKNOWN' in pattern:
                unknown_syllables.append({
                    'text': syl.get('syllable', ''),
                    'diacritized': syl.get('diacritized', ''),
                    'pattern': pattern,
                    'chars': syl.get('chars', [])
                })

        if not unknown_syllables:
            print("  ✓ No UNKNOWN patterns (already fixed)\n")
            continue

        print(f"\n  CURRENT (Broken): {len(unknown_syllables)} UNKNOWN syllable(s)")
        for unk in unknown_syllables:
            print(f"    [{unk['text']}] → {unk['pattern']}")

        # Step 2: Test with PROPER syllabifier
        print(f"\n  TESTING WITH PROPER SYLLABIFIER:")

        all_fixed = True
        for unk in unknown_syllables:
            diacritized = unk['diacritized']
            syllable_text = unk['text']

            # DEBUG: Show what we're working with
            print(f"\n    Syllable text: [{syllable_text}]")
            print(f"    Diacritized:   [{diacritized}]")
            print(f"    Chars: {unk['chars']}")

            # Use whichever is not empty
            text_to_test = diacritized if diacritized else syllable_text
            if not text_to_test:
                print(f"      ⚠ Empty syllable, skipping")
                continue

            total_tested += 1

            # Use proper syllabifier
            proper_segments = proper_syllabifier.segment(text_to_test)

            print(f"      Testing: [{text_to_test}]")
            print(f"      Proper segmentation: {len(proper_segments)} segment(s)")

            has_unknown = False
            for i, seg in enumerate(proper_segments, 1):
                pattern = proper_syllabifier.classify_pattern(seg)
                seg_text = ''.join(seg)
                print(f"        {i}. [{seg_text}] → {pattern}")

                if 'UNKNOWN' in pattern:
                    has_unknown = True

            if has_unknown:
                print(f"      ✗ Still has UNKNOWN patterns")
                all_fixed = False
            else:
                print(f"      ✓ FIXED! All patterns valid")
                fixed_count += 1

        if all_fixed:
            print(f"\n  ✅ ALL UNKNOWN PATTERNS FIXED by proper syllabifier!")
        else:
            print(f"\n  ⚠ Some patterns still UNKNOWN (needs more work)")

        print()

    # Summary
    print("=" * 70)
    print("PROOF OF CONCEPT SUMMARY")
    print("=" * 70)
    print(f"\nTotal UNKNOWN syllables tested: {total_tested}")
    print(f"Fixed by proper syllabifier:     {fixed_count} ({fixed_count/total_tested*100:.1f}%)")
    print(f"Still UNKNOWN:                   {total_tested - fixed_count}")

    if fixed_count == total_tested:
        print("\n✅ PROOF OF CONCEPT SUCCESSFUL!")
        print("   Switching to proper syllabifier will fix ALL UNKNOWN patterns!")
    elif fixed_count > 0:
        print(f"\n⚠ PARTIAL SUCCESS")
        print(f"   Proper syllabifier fixes {fixed_count/total_tested*100:.1f}% of cases")
        print(f"   Remaining {100 - fixed_count/total_tested*100:.1f}% need additional work")
    else:
        print("\n✗ PROOF OF CONCEPT FAILED")
        print("   Proper syllabifier doesn't solve the problem")

    return fixed_count, total_tested


if __name__ == '__main__':
    fixed, total = test_proof_of_concept()

    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    if fixed == total:
        print("""
1. Replace broken ArabicSyllabifier in main.py with proper one
2. Update all method calls (segment_syllables → segment)
3. Remove resyllabify logic (proper syllabifier doesn't need it)
4. Test on full corpus (expect 26.9% warnings → near 0%)
5. Should reach ~95% success rate (69.1% + 26.9%)
        """)
    else:
        print(f"""
The proper syllabifier fixes {fixed}/{total} cases ({fixed/total*100:.1f}%).
Additional work needed for remaining cases.
        """)
