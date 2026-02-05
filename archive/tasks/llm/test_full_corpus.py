#!/usr/bin/env python3
"""
Test masterTTS.json improvements against the full 353-word baseline corpus.

Compares against: /home/hamr/Downloads/tts_matrix_20251216_144128-MSA.csv
Baseline: 39.4% success rate
Target: 67-75% success rate
"""

import sys
import csv
from pathlib import Path
from collections import Counter

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.main import ArabicTTS


def load_baseline_csv(csv_path):
    """Load baseline CSV and extract words + expected results."""
    words_data = []

    # Handle UTF-8 BOM explicitly
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only test WORD-level entries (not CHAR-level)
            if row.get('Type') == 'WORD':
                original = row.get('Original', '').strip()
                if original:  # Skip empty words
                    words_data.append({
                        'original': original,
                        'baseline_status': row.get('Status', '').strip(),
                        'baseline_failed': row.get('Failed_Layers', '').strip()
                    })

    print(f"  Sample baseline entries:")
    for i, word in enumerate(words_data[:3]):
        print(f"    {i+1}. {word['original']} (status: {word['baseline_status']})")

    return words_data


def test_corpus(dialect='MSA', baseline_csv=None):
    """Test full corpus and compare with baseline."""

    print("=" * 70)
    print(f"Testing {dialect} Dialect - Full Corpus Comparison")
    print("=" * 70)

    # Load baseline data
    if baseline_csv:
        words_data = load_baseline_csv(baseline_csv)
        print(f"\nLoaded {len(words_data)} words from baseline CSV")
    else:
        print("ERROR: No baseline CSV provided")
        return

    # Initialize TTS
    tts = ArabicTTS(dialect)

    # Track results
    results = {
        'success': 0,
        'warning': 0,
        'error': 0,
        'total': len(words_data)
    }

    # Track improvements
    improvements = {
        'error_to_success': 0,  # baseline: error/warning → current: success
        'error_to_warning': 0,  # baseline: error → current: warning
        'same_error': 0,        # both failed
        'same_success': 0,      # both succeeded
        'success_to_error': 0   # regression (shouldn't happen!)
    }

    # Track failure types
    failure_types = Counter()

    print("\nProcessing words...")
    print("(Showing first 20 results, then summary)\n")

    for idx, word_data in enumerate(words_data):
        word = word_data['original']

        if not word or word.strip() == '':
            continue

        try:
            result = tts.process_text(word)

            # Extract status
            words = result.get('words', [])
            if not words:
                status = 'error'
                failed_layers = ['no_words']
            else:
                syllables = words[0].get('syllables', [])
                if not syllables:
                    status = 'error'
                    failed_layers = ['no_syllables']
                else:
                    # Check IPA
                    ipa = ''.join([s.get('ipa', '') for s in syllables])

                    if ipa and not any(c in ipa for c in ['\ufffd', '�']):
                        # Check for UNKNOWN patterns
                        has_unknown = any('UNKNOWN' in s.get('pattern', '') for s in syllables)
                        if has_unknown:
                            status = 'warning'
                            failed_layers = ['syllable_unknown']
                        else:
                            status = 'success'
                            failed_layers = []
                    else:
                        status = 'error'
                        failed_layers = ['ipa_missing']

            results[status] += 1
            if failed_layers:
                failure_types[','.join(failed_layers)] += 1

            # Compare with baseline
            baseline_status = word_data['baseline_status']
            baseline_failed = word_data['baseline_failed']

            if baseline_status in ['error', 'warning'] and status == 'success':
                improvements['error_to_success'] += 1
                change = '✓✓✓'  # Big improvement
            elif baseline_status == 'error' and status == 'warning':
                improvements['error_to_warning'] += 1
                change = '✓✓'   # Partial improvement
            elif baseline_status == 'success' and status == 'success':
                improvements['same_success'] += 1
                change = '✓'    # Maintained
            elif baseline_status in ['error', 'warning'] and status in ['error', 'warning']:
                improvements['same_error'] += 1
                change = '✗'    # Still failing
            elif baseline_status == 'success' and status in ['error', 'warning']:
                improvements['success_to_error'] += 1
                change = '⚠⚠⚠'  # REGRESSION!
            else:
                change = '?'

            # Show first 20 results
            if idx < 20:
                print(f"{change} {word:15} | {baseline_status:8} → {status:8}")

        except Exception as e:
            results['error'] += 1
            failure_types['exception'] += 1
            if idx < 20:
                print(f"✗ {word:15} | Exception: {str(e)[:40]}")

    # Print summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    success_rate = (results['success'] / results['total']) * 100
    baseline_success = 39.4  # From CONTINUATION_SUMMARY.md

    print(f"\nOverall Success Rates:")
    print(f"  Baseline: {baseline_success:.1f}% (139/353 words)")
    print(f"  Current:  {success_rate:.1f}% ({results['success']}/{results['total']} words)")
    print(f"  Change:   +{success_rate - baseline_success:.1f} percentage points")

    print(f"\nDetailed Breakdown:")
    print(f"  Success:  {results['success']:3}/{results['total']} ({(results['success']/results['total'])*100:.1f}%)")
    print(f"  Warnings: {results['warning']:3}/{results['total']} ({(results['warning']/results['total'])*100:.1f}%)")
    print(f"  Errors:   {results['error']:3}/{results['total']} ({(results['error']/results['total'])*100:.1f}%)")

    print(f"\nImprovement Analysis:")
    print(f"  Error→Success:   {improvements['error_to_success']:3} words (BIG WIN!)")
    print(f"  Error→Warning:   {improvements['error_to_warning']:3} words (partial improvement)")
    print(f"  Still Success:   {improvements['same_success']:3} words (maintained)")
    print(f"  Still Failing:   {improvements['same_error']:3} words (needs more work)")
    print(f"  Regressions:     {improvements['success_to_error']:3} words (⚠ investigate!)")

    print(f"\nTop Failure Types:")
    for failure, count in failure_types.most_common(5):
        print(f"  {failure:20} {count:3} words")

    print(f"\nPhase 1 & 2 Target: 67-75% success")
    if success_rate >= 67:
        print("✓ TARGET ACHIEVED!")
    elif success_rate > baseline_success:
        print(f"⚠ Improvement seen (+{success_rate - baseline_success:.1f}%), but below target")
        remaining = 67 - success_rate
        print(f"  Need +{remaining:.1f}% more to reach Phase 1 & 2 goal")
    else:
        print("✗ No improvement - investigate!")

    return results, improvements


if __name__ == '__main__':
    baseline_csv = '/home/hamr/Downloads/tts_matrix_20251216_144128-MSA.csv'

    if not Path(baseline_csv).exists():
        print(f"ERROR: Baseline CSV not found: {baseline_csv}")
        sys.exit(1)

    results, improvements = test_corpus('MSA', baseline_csv)

    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)
