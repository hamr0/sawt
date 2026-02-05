#!/usr/bin/env python3
"""
Test diacritization with Mishkal on actual CSV data.

This script:
1. Extracts words from CSV exports
2. Tests Mishkal diacritization on all words
3. Generates detailed results CSV
4. Provides statistics on success rates
"""

import sys
import csv
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from mishkal.tashkeel import TashkeelClass


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


def save_results_csv(mishkal_results: list, output_path: str):
    """Save Mishkal test results to CSV."""
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = [
            'Original', 'Current_Status', 'Current_Failed_Layers',
            'Mishkal_Output', 'Mishkal_Success'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Track stats
        stats = {
            'total_words': len(mishkal_results),
            'success': 0,
            'error': 0,
            'error_layers': {}  # Track failed layers for errors
        }

        for m in mishkal_results:
            writer.writerow({
                'Original': m.get('original', ''),
                'Current_Status': m.get('current_status', ''),
                'Current_Failed_Layers': m.get('current_failed_layers', ''),
                'Mishkal_Output': m.get('mishkal_output', ''),
                'Mishkal_Success': 'YES' if m.get('mishkal_success') else 'NO'
            })

            # Count stats
            if m.get('mishkal_success'):
                stats['success'] += 1
            else:
                stats['error'] += 1
                # Track failed layers for errors
                failed_layers = m.get('current_failed_layers', '')
                if failed_layers and failed_layers != '-':
                    stats['error_layers'][failed_layers] = stats['error_layers'].get(failed_layers, 0) + 1

        # Add Processing Stats row
        if stats['total_words'] > 0:
            success_rate = (stats['success'] / stats['total_words'] * 100) if stats['total_words'] > 0 else 0

            # Format error with failed layers (most common)
            error_str = f"Error: {stats['error']}"
            if stats['error_layers']:
                most_common_error = max(stats['error_layers'].items(), key=lambda x: x[1])
                error_str += f" {most_common_error[0]}"

            writer.writerow({
                'Original': 'Processing Stats',
                'Current_Status': f"Total: {stats['total_words']}",
                'Current_Failed_Layers': f"Success: {stats['success']}",
                'Mishkal_Output': error_str,
                'Mishkal_Success': f"Success Rate: {success_rate:.1f}%"
            })

            # Add Notes row explaining failed layer codes
            writer.writerow({
                'Original': 'Notes',
                'Current_Status': 'Failed Layer Codes:',
                'Current_Failed_Layers': 'diac=Diacritization',
                'Mishkal_Output': 'ipa=IPA Generation',
                'Mishkal_Success': 'syl=Syllabification'
            })

    print(f"\n✓ Results saved to: {output_path}")


def main():
    """Main test execution."""
    import argparse

    parser = argparse.ArgumentParser(description='Test Mishkal diacritization on CSV data')
    parser.add_argument('csv_file', help='Path to CSV file with words to test')
    parser.add_argument('--output', default='mishkal_test_results.csv',
                       help='Output CSV file for test results')
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

    # Save results CSV
    save_results_csv(mishkal_results, args.output)

    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
