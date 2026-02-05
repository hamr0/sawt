#!/usr/bin/env python3
"""
Analyze UNKNOWN syllable patterns to understand what's failing.

This will help us identify what patterns the syllabifier doesn't recognize.
"""

import sys
import csv
from pathlib import Path
from collections import Counter

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.main import ArabicTTS


def analyze_unknown_patterns(dialect='MSA', baseline_csv=None):
    """Analyze words with UNKNOWN patterns to identify what needs fixing."""

    print("=" * 70)
    print(f"Analyzing UNKNOWN Syllable Patterns - {dialect}")
    print("=" * 70)

    # Load words from baseline
    words = []
    if baseline_csv:
        with open(baseline_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Type') == 'WORD':
                    original = row.get('Original', '').strip()
                    if original:
                        words.append(original)

    print(f"\nAnalyzing {len(words)} words...\n")

    # Initialize TTS
    tts = ArabicTTS(dialect)

    # Track UNKNOWN patterns
    unknown_cases = []
    pattern_counts = Counter()

    # Process words
    for word in words:
        try:
            result = tts.process_text(word)

            # Check for UNKNOWN patterns
            words_data = result.get('words', [])
            if words_data:
                syllables = words_data[0].get('syllables', [])

                for syl in syllables:
                    pattern = syl.get('pattern', '')
                    if 'UNKNOWN' in pattern:
                        syllable_text = syl.get('syllable', '')
                        diacritized = syl.get('diacritized', syllable_text)
                        chars = syl.get('chars', [])

                        unknown_cases.append({
                            'word': word,
                            'syllable': syllable_text,
                            'diacritized': diacritized,
                            'pattern': pattern,
                            'chars': chars,
                            'char_count': len(chars)
                        })

                        pattern_counts[pattern] += 1
                        break  # Only count first UNKNOWN per word

        except Exception as e:
            continue

    # Print results
    print(f"Found {len(unknown_cases)} words with UNKNOWN patterns\n")

    print("=" * 70)
    print("TOP 10 MOST COMMON UNKNOWN PATTERNS")
    print("=" * 70)
    for pattern, count in pattern_counts.most_common(10):
        print(f"{count:3} words | {pattern}")

    print("\n" + "=" * 70)
    print("SAMPLE WORDS WITH UNKNOWN PATTERNS (First 30)")
    print("=" * 70)
    print(f"{'Word':15} {'Syllable':12} {'Pattern':25} {'Chars'}")
    print("-" * 70)

    for case in unknown_cases[:30]:
        word = case['word'][:15]
        syllable = case['syllable'][:12]
        pattern = case['pattern'][:25]
        chars = ','.join(case['chars'])[:20]
        print(f"{word:15} {syllable:12} {pattern:25} {chars}")

    # Analyze by character count
    print("\n" + "=" * 70)
    print("UNKNOWN PATTERNS BY CHARACTER COUNT")
    print("=" * 70)

    by_count = {}
    for case in unknown_cases:
        count = case['char_count']
        if count not in by_count:
            by_count[count] = []
        by_count[count].append(case)

    for count in sorted(by_count.keys()):
        cases = by_count[count]
        print(f"\n{count} characters: {len(cases)} cases")
        # Show a few examples
        for case in cases[:3]:
            print(f"  {case['word']:15} | {case['syllable']:10} | chars: {','.join(case['chars'])}")

    # Analyze what makes these UNKNOWN
    print("\n" + "=" * 70)
    print("PATTERN ANALYSIS")
    print("=" * 70)

    # Look for common characteristics
    has_gemination = sum(1 for c in unknown_cases if 'ّ' in ''.join(c['chars']))
    has_sukun = sum(1 for c in unknown_cases if 'ْ' in ''.join(c['chars']))
    has_tanween = sum(1 for c in unknown_cases if any(t in ''.join(c['chars']) for t in ['ً', 'ٌ', 'ٍ']))

    print(f"Cases with shadda (ّ):     {has_gemination} ({has_gemination/len(unknown_cases)*100:.1f}%)")
    print(f"Cases with sukun (ْ):      {has_sukun} ({has_sukun/len(unknown_cases)*100:.1f}%)")
    print(f"Cases with tanween:       {has_tanween} ({has_tanween/len(unknown_cases)*100:.1f}%)")

    return unknown_cases


if __name__ == '__main__':
    baseline_csv = '/home/hamr/Downloads/tts_matrix_20251216_144128-MSA.csv'

    if not Path(baseline_csv).exists():
        print(f"ERROR: Baseline CSV not found: {baseline_csv}")
        sys.exit(1)

    unknown_cases = analyze_unknown_patterns('MSA', baseline_csv)

    print("\n" + "=" * 70)
    print(f"Analysis Complete - {len(unknown_cases)} UNKNOWN cases found")
    print("=" * 70)
