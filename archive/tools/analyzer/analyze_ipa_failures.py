#!/usr/bin/env python3
"""
Analyze IPA failures from TTS matrix CSV to identify missing masterTTS.json entries.

Usage:
    python analyze_ipa_failures.py <csv_file> [--dialect=MSA]
"""

import csv
import sys
import json
from collections import Counter
from pathlib import Path

def analyze_ipa_failures(csv_path: str, dialect: str = "MSA"):
    """
    Analyze IPA failures in CSV to identify missing dictionary entries.

    Args:
        csv_path: Path to TTS matrix CSV file
        dialect: Dialect to analyze (default: MSA)
    """
    print(f"\n{'='*80}")
    print(f"IPA Failure Analysis for {dialect}")
    print(f"{'='*80}\n")

    ipa_failures = []
    failure_chars = Counter()

    with open(csv_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)

        for row in reader:
            # Only analyze WORD-level rows
            if row.get('Type') != 'WORD':
                continue

            failed_layers = row.get('Failed_Layers', '')

            # Check if IPA failed
            if 'ipa' in failed_layers:
                word = row.get('Word', '')
                original = row.get('Original', '')
                diacritized = row.get('Diacritized', '')
                ipa = row.get('IPA', '')

                ipa_failures.append({
                    'word': word,
                    'original': original,
                    'diacritized': diacritized,
                    'ipa': ipa,
                    'failed_layers': failed_layers
                })

                # Count unmapped characters in IPA (Arabic chars that didn't convert)
                for char in ipa:
                    if '\u0600' <= char <= '\u06FF':
                        # Skip diacritics (they're expected to pass through)
                        # Diacritic ranges: 064B-0652 (main), 0670 (superscript alef)
                        if not ('\u064B' <= char <= '\u0652' or char == '\u0670'):
                            failure_chars[char] += 1

    print(f"Total IPA Failures: {len(ipa_failures)}")
    print(f"\n{'='*80}")
    print("Top 20 Unmapped Characters")
    print(f"{'='*80}\n")

    for char, count in failure_chars.most_common(20):
        print(f"  {char}  ({hex(ord(char))})  -  {count} occurrences")

    print(f"\n{'='*80}")
    print("Sample Failed Words (first 20)")
    print(f"{'='*80}\n")

    for i, failure in enumerate(ipa_failures[:20], 1):
        print(f"{i:2d}. {failure['word']:15s} → {failure['ipa']}")
        print(f"    Original: {failure['original']}")
        print(f"    Diacritized: {failure['diacritized']}")
        print(f"    Failed layers: {failure['failed_layers']}")
        print()

    # Load masterTTS.json to check coverage
    master_tts_path = Path(__file__).parent.parent.parent / "data" / "dictionaries" / "masterTTS.json"

    if master_tts_path.exists():
        with open(master_tts_path, 'r', encoding='utf-8') as f:
            master_tts = json.load(f)

        print(f"\n{'='*80}")
        print(f"masterTTS.json Coverage for {dialect}")
        print(f"{'='*80}\n")

        # Get dialect array from masterTTS.json
        dialect_entries = master_tts.get(dialect, [])

        print(f"Total {dialect} entries: {len(dialect_entries)}")

        # Get unique Arabic letters covered in this dialect
        covered_chars = set()
        for entry in dialect_entries:
            if isinstance(entry, dict):
                char = entry.get('Arabic letter', '')
                if char:
                    covered_chars.add(char)

        print(f"Unique Arabic letters covered: {len(covered_chars)}")

        # Check which failing characters exist in dictionary
        missing_chars = []
        for char, count in failure_chars.most_common():
            if char not in covered_chars:
                missing_chars.append((char, count))

        print(f"\nCharacters NOT found in {dialect} entries: {len(missing_chars)}")
        for char, count in missing_chars[:10]:
            print(f"  {char}  ({hex(ord(char))})  -  {count} occurrences - NOT IN DICTIONARY")

    print(f"\n{'='*80}")
    print("Recommendations")
    print(f"{'='*80}\n")

    print("1. Add missing character entries to masterTTS.json")
    print("2. Ensure all position variants (initial, medial, final) are covered")
    print("3. Check if existing entries are using correct dialect key")
    print("4. Run Phase 1-2 improvements for MSA (similar to what was done for EG)")
    print()
    print("Next steps:")
    print("  - Review the top unmapped characters above")
    print("  - Add IPA mappings for each to masterTTS.json")
    print("  - Test with the failed words to verify improvements")
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_ipa_failures.py <csv_file> [--dialect=MSA]")
        sys.exit(1)

    csv_file = sys.argv[1]
    dialect = "MSA"

    for arg in sys.argv[2:]:
        if arg.startswith('--dialect='):
            dialect = arg.split('=')[1]

    analyze_ipa_failures(csv_file, dialect)
