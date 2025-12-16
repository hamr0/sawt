#!/usr/bin/env python3
"""
Test script to verify masterTTS.json improvements for MSA dialect.

This script tests the Phase 1 & 2 improvements:
- 36 MSA format fixes (slash removal)
- 48 NEW MSA position mappings
- 29 NEW Gulf entries
- 26 NEW Levantine entries
- 25 NEW Maghreb entries

Expected improvements:
- MSA: 39.4% → 67-75% success rate
- Other dialects: improved character coverage
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.main import ArabicTTS


def test_msa_improvements():
    """Test MSA dialect with words that were failing before."""

    print("=" * 70)
    print("Testing MSA Dialect Improvements")
    print("=" * 70)

    # Test words that were failing in baseline (39.4% success)
    # These should now succeed with the new position mappings
    test_cases = [
        # Basic consonants that got position mappings
        ('محمد', 'Muhammad - was failing with IPA lookup'),
        ('نور', 'Light - tests new ن position entries'),
        ('ليل', 'Night - tests new ل position entries'),
        ('كتاب', 'Book - tests new ك position entries'),
        ('بيت', 'House - tests new ب position entries'),
        ('سلام', 'Peace - tests new س position entries'),
        ('ماء', 'Water - tests hamza position entries'),
        ('أحمد', 'Ahmed - tests hamza variants'),

        # Words with multiple characters to test position detection
        ('الباب', 'The door - tests word-initial/medial/final'),
        ('المدرسة', 'The school - tests complex positions'),
        ('الله', 'Allah - tests special cases'),
    ]

    tts = ArabicTTS('MSA')

    results = {
        'success': 0,
        'warning': 0,
        'error': 0,
        'total': len(test_cases)
    }

    print(f"\nProcessing {len(test_cases)} test words...\n")

    for word, description in test_cases:
        try:
            result = tts.process_text(word)

            # DEBUG: Print raw result for first word
            if word == 'محمد':
                print("\n[DEBUG] Raw result keys:", list(result.keys()))
                print("[DEBUG] Full result:", json.dumps(result, ensure_ascii=False, indent=2)[:500])
                print()

            # Extract status from result - data is under words
            words = result.get('words', [])
            if not words:
                status = 'error'
                failed_layers = ['no_words']
                ipa = 'N/A'
            else:
                # Get syllables from first word
                syllables = words[0].get('syllables', [])
                if not syllables:
                    status = 'error'
                    failed_layers = ['no_syllables']
                    ipa = 'N/A'
                else:
                    # Get the first syllable's data
                    syl = syllables[0]
                    ipa = syl.get('ipa', 'N/A')

                    # Determine status based on IPA presence
                    if ipa and ipa != 'N/A' and not any(c in ipa for c in ['�', '?', '\ufffd']):
                        # Check for UNKNOWN patterns
                        has_unknown = any('UNKNOWN' in s.get('pattern', '') for s in syllables)
                        if has_unknown:
                            status = 'warning'
                            failed_layers = ['syllable_unknown']
                        else:
                            status = 'success'
                            failed_layers = []
                    else:
                        status = 'warning'
                        failed_layers = ['ipa']

                    # Build full IPA from all syllables
                    ipa = ''.join([s.get('ipa', '') for s in syllables])

            results[status] += 1

            # Visual status indicator
            if status == 'success':
                indicator = '✓'
            elif status == 'warning':
                indicator = '⚠'
            else:
                indicator = '✗'

            print(f"{indicator} {word:15} | {status:8} | {description}")
            if failed_layers:
                print(f"  {'':17} Failed: {', '.join(failed_layers)}")
            print(f"  {'':17} IPA: {ipa}")

        except Exception as e:
            results['error'] += 1
            print(f"✗ {word:15} | error    | {description}")
            print(f"  {'':17} Exception: {str(e)[:60]}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    success_rate = (results['success'] / results['total']) * 100
    print(f"Success:  {results['success']:3}/{results['total']} ({success_rate:.1f}%)")
    print(f"Warnings: {results['warning']:3}/{results['total']}")
    print(f"Errors:   {results['error']:3}/{results['total']}")

    print(f"\nBaseline: 39.4% success (before improvements)")
    print(f"Current:  {success_rate:.1f}% success")
    print(f"Target:   67-75% success (Phase 1 & 2 goal)")

    if success_rate >= 67:
        print("\n✓ Phase 1 & 2 target ACHIEVED!")
    elif success_rate > 39.4:
        print(f"\n⚠ Improvement seen (+{success_rate - 39.4:.1f}%), but below target")
    else:
        print("\n✗ No improvement - investigate masterTTS.json loading")

    return results


def test_other_dialects():
    """Quick test of other dialects to verify new entries work."""

    print("\n" + "=" * 70)
    print("Testing Other Dialects")
    print("=" * 70)

    dialects = ['Gulf', 'Levantine', 'Maghreb']
    test_word = 'نور'  # Simple word - tests ن entry

    for dialect in dialects:
        try:
            tts = ArabicTTS(dialect)
            result = tts.process_text(test_word)

            words = result.get('words', [])
            if words:
                syllables = words[0].get('syllables', [])
                if syllables:
                    ipa = ''.join([s.get('ipa', '') for s in syllables])
                    status = '✓' if ipa and ipa != 'N/A' else '✗'
                    print(f"{status} {dialect:12} | {test_word} → {ipa}")
                else:
                    print(f"✗ {dialect:12} | No syllables returned")
            else:
                print(f"✗ {dialect:12} | No words returned")

        except Exception as e:
            print(f"✗ {dialect:12} | Error: {str(e)[:50]}")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("MasterTTS.json Improvements Test Suite")
    print("=" * 70)
    print("\nPhase 1 & 2 Changes:")
    print("  - 36 MSA format fixes (slash removal)")
    print("  - 48 NEW MSA position mappings")
    print("  - 29 NEW Gulf entries")
    print("  - 26 NEW Levantine entries")
    print("  - 25 NEW Maghreb entries")
    print("  TOTAL: 128 new entries")
    print()

    # Run tests
    results = test_msa_improvements()
    test_other_dialects()

    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)
