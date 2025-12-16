#!/usr/bin/env python3
"""
Test diacritization tools (Mishkal vs CAMeL) on actual CSV data.

This script:
1. Extracts failed words from CSV exports
2. Tests Mishkal separately on all words
3. Tests CAMeL separately on same words
4. Generates comparison CSV with both results
5. Tests different fallback sequences (Mishkal→CAMeL, CAMeL alone, etc.)
"""

import sys
import csv
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from mishkal.tashkeel import TashkeelClass

try:
    from camel_tools.disambig.mle import MLEDisambiguator
    from camel_tools.tokenizers.word import simple_word_tokenize
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    print("[WARNING] CAMeL Tools not installed. Install with: pip install camel-tools")


def has_diacritics(text: str) -> bool:
    """Check if text contains Arabic diacritics."""
    diacritics = {'\u064B', '\u064C', '\u064D', '\u064E', '\u064F', '\u0650', '\u0651', '\u0652'}
    return any(c in diacritics for c in text)


def extract_words_from_csv(csv_path: str) -> list:
    """
    Extract unique words from CSV export.

    Returns list of dicts with:
    - original: undiacritized word
    - diacritized: result from current system
    - status: current processing status
    - failed_layers: which layers failed
    """
    words = []
    seen = set()

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only process WORD-level rows
            if row.get('Type') != 'WORD':
                continue

            original = row.get('Original', '').strip()
            diacritized = row.get('Diacritized', '').strip()
            status = row.get('Status', '').strip()
            failed_layers = row.get('Failed_Layers', '').strip()

            # Skip empty or duplicate words
            if not original or original in seen:
                continue

            seen.add(original)
            words.append({
                'original': original,
                'current_diacritized': diacritized,
                'current_status': status,
                'current_failed_layers': failed_layers
            })

    return words


def test_mishkal(words: list) -> list:
    """Test Mishkal on all words."""
    print("\n" + "="*60)
    print("TESTING MISHKAL")
    print("="*60)

    mishkal = TashkeelClass()
    results = []

    for word_data in words:
        original = word_data['original']

        try:
            diacritized = mishkal.tashkeel(original).strip()

            # Success if diacritics were added
            success = diacritized != original and has_diacritics(diacritized)

            results.append({
                **word_data,
                'mishkal_output': diacritized,
                'mishkal_success': success
            })

            status = "✓" if success else "✗"
            print(f"{status} {original:20} → {diacritized}")

        except Exception as e:
            results.append({
                **word_data,
                'mishkal_output': None,
                'mishkal_success': False,
                'mishkal_error': str(e)
            })
            print(f"✗ {original:20} → ERROR: {str(e)[:30]}")

    success_count = sum(1 for r in results if r.get('mishkal_success'))
    print(f"\nMishkal Success Rate: {success_count}/{len(results)} = {success_count/len(results)*100:.1f}%")

    return results


def test_camel(words: list) -> list:
    """Test CAMeL Tools on all words."""
    if not CAMEL_AVAILABLE:
        print("\n[SKIPPED] CAMeL Tools not installed")
        return [{'camel_available': False} for _ in words]

    print("\n" + "="*60)
    print("TESTING CAMEL TOOLS")
    print("="*60)
    print("Loading CAMeL models (may take 30-60 seconds)...")

    try:
        camel = MLEDisambiguator.pretrained()
    except Exception as e:
        print(f"[ERROR] Failed to load CAMeL: {e}")
        return [{'camel_error': str(e)} for _ in words]

    results = []

    for word_data in words:
        original = word_data['original']

        try:
            tokens = simple_word_tokenize(original)
            disambig = camel.disambiguate(tokens)
            # Extract diacritized form from analyses
            diacritized = ''.join([d.analyses[0].diac if d.analyses else d.word for d in disambig])

            # Success if diacritics were added
            success = diacritized != original and has_diacritics(diacritized)

            results.append({
                **word_data,
                'camel_output': diacritized,
                'camel_success': success
            })

            status = "✓" if success else "✗"
            print(f"{status} {original:20} → {diacritized}")

        except Exception as e:
            results.append({
                **word_data,
                'camel_output': None,
                'camel_success': False,
                'camel_error': str(e)
            })
            print(f"✗ {original:20} → ERROR: {str(e)[:30]}")

    success_count = sum(1 for r in results if r.get('camel_success'))
    print(f"\nCAMeL Success Rate: {success_count}/{len(results)} = {success_count/len(results)*100:.1f}%")

    return results


def test_fallback_sequences(mishkal_results: list, camel_results: list) -> dict:
    """
    Test different fallback sequences and calculate success rates.

    Sequences:
    1. Mishkal only
    2. CAMeL only
    3. Mishkal → CAMeL (use CAMeL if Mishkal fails)
    4. CAMeL → Mishkal (use Mishkal if CAMeL fails)
    """
    print("\n" + "="*60)
    print("FALLBACK SEQUENCE ANALYSIS")
    print("="*60)

    total = len(mishkal_results)

    # Sequence 1: Mishkal only
    mishkal_only = sum(1 for r in mishkal_results if r.get('mishkal_success'))

    # Sequence 2: CAMeL only
    camel_only = sum(1 for r in camel_results if r.get('camel_success'))

    # Sequence 3: Mishkal → CAMeL
    mishkal_then_camel = 0
    camel_rescued = 0
    for m, c in zip(mishkal_results, camel_results):
        if m.get('mishkal_success'):
            mishkal_then_camel += 1
        elif c.get('camel_success'):
            mishkal_then_camel += 1
            camel_rescued += 1

    # Sequence 4: CAMeL → Mishkal
    camel_then_mishkal = 0
    mishkal_rescued = 0
    for m, c in zip(mishkal_results, camel_results):
        if c.get('camel_success'):
            camel_then_mishkal += 1
        elif m.get('mishkal_success'):
            camel_then_mishkal += 1
            mishkal_rescued += 1

    results = {
        'mishkal_only': {'count': mishkal_only, 'rate': mishkal_only/total*100},
        'camel_only': {'count': camel_only, 'rate': camel_only/total*100},
        'mishkal_then_camel': {
            'count': mishkal_then_camel,
            'rate': mishkal_then_camel/total*100,
            'camel_rescued': camel_rescued
        },
        'camel_then_mishkal': {
            'count': camel_then_mishkal,
            'rate': camel_then_mishkal/total*100,
            'mishkal_rescued': mishkal_rescued
        }
    }

    print(f"\n1. Mishkal Only:        {mishkal_only}/{total} ({mishkal_only/total*100:.1f}%)")
    print(f"2. CAMeL Only:          {camel_only}/{total} ({camel_only/total*100:.1f}%)")
    print(f"3. Mishkal → CAMeL:     {mishkal_then_camel}/{total} ({mishkal_then_camel/total*100:.1f}%)")
    print(f"   └─ CAMeL rescued:    {camel_rescued} words")
    print(f"4. CAMeL → Mishkal:     {camel_then_mishkal}/{total} ({camel_then_mishkal/total*100:.1f}%)")
    print(f"   └─ Mishkal rescued:  {mishkal_rescued} words")

    # Recommendation
    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("="*60)

    if camel_rescued > mishkal_rescued:
        improvement = camel_rescued - mishkal_only
        print(f"✓ Use Mishkal → CAMeL fallback")
        print(f"  Improves success by {improvement} words ({improvement/total*100:.1f}%)")
    elif mishkal_rescued > camel_rescued:
        improvement = mishkal_rescued - camel_only
        print(f"✓ Use CAMeL → Mishkal fallback")
        print(f"  Improves success by {improvement} words ({improvement/total*100:.1f}%)")
    else:
        print(f"⚠ Both sequences perform equally")
        print(f"  Recommend: Mishkal → CAMeL (Mishkal is faster)")

    return results


def save_comparison_csv(mishkal_results: list, camel_results: list, output_path: str):
    """Save comparison results to CSV."""
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = [
            'Original', 'Current_Status', 'Current_Failed_Layers',
            'Mishkal_Output', 'Mishkal_Success',
            'CAMeL_Output', 'CAMeL_Success',
            'Best_Result'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for m, c in zip(mishkal_results, camel_results):
            # Determine best result
            if m.get('mishkal_success') and c.get('camel_success'):
                best = 'BOTH'
            elif m.get('mishkal_success'):
                best = 'Mishkal'
            elif c.get('camel_success'):
                best = 'CAMeL'
            else:
                best = 'NEITHER'

            writer.writerow({
                'Original': m.get('original', ''),
                'Current_Status': m.get('current_status', ''),
                'Current_Failed_Layers': m.get('current_failed_layers', ''),
                'Mishkal_Output': m.get('mishkal_output', ''),
                'Mishkal_Success': 'YES' if m.get('mishkal_success') else 'NO',
                'CAMeL_Output': c.get('camel_output', ''),
                'CAMeL_Success': 'YES' if c.get('camel_success') else 'NO',
                'Best_Result': best
            })

    print(f"\n✓ Comparison saved to: {output_path}")


def main():
    """Main test execution."""
    import argparse

    parser = argparse.ArgumentParser(description='Test Mishkal vs CAMeL on CSV data')
    parser.add_argument('csv_file', help='Path to CSV file with words to test')
    parser.add_argument('--output', default='diacritization_comparison.csv',
                       help='Output CSV file for comparison results')
    args = parser.parse_args()

    # Check input file
    if not Path(args.csv_file).exists():
        print(f"[ERROR] File not found: {args.csv_file}")
        sys.exit(1)

    # Extract words from CSV
    print("Extracting words from CSV...")
    words = extract_words_from_csv(args.csv_file)
    print(f"Found {len(words)} unique words to test")

    if len(words) == 0:
        print("[ERROR] No words found in CSV")
        sys.exit(1)

    # Test Mishkal
    mishkal_results = test_mishkal(words)

    # Test CAMeL
    camel_results = test_camel(words)

    # Analyze fallback sequences
    if CAMEL_AVAILABLE:
        fallback_analysis = test_fallback_sequences(mishkal_results, camel_results)

    # Save comparison CSV
    save_comparison_csv(mishkal_results, camel_results, args.output)

    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
