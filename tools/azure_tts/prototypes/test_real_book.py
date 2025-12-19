#!/usr/bin/env python3
"""
Test character detection on real Arabic book
"""

import sys
from pathlib import Path
from datetime import datetime

# Import from prototype 1
sys.path.insert(0, str(Path(__file__).parent))
from importlib.util import spec_from_file_location, module_from_spec

# Load the character detector module
spec = spec_from_file_location("char_detector", Path(__file__).parent / "01_character_detection.py")
module = module_from_spec(spec)
spec.loader.exec_module(module)

CharacterDetector = module.CharacterDetector


def main():
    """Test on real book file"""

    book_path = Path("/home/hamr/Documents/PycharmProjects/ArabicTTS/tools/azure_tts/awalad-7aretna.txt")

    if not book_path.exists():
        print(f"ERROR: File not found: {book_path}")
        sys.exit(1)

    print("=" * 80)
    print("Character Detection Test: Real Arabic Book")
    print("=" * 80)
    print(f"\nBook: {book_path.name}")

    # Read book text
    print("\n1. Reading book text...")
    with open(book_path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = len(text.split('\n'))
    chars = len(text)
    print(f"   ✓ {lines} lines, {chars:,} characters")

    # Run detection
    print("\n2. Running character detection...")
    detector = CharacterDetector()
    segments = detector.segment_text(text)
    print(f"   ✓ Detected {len(segments)} segments")

    # Calculate stats
    print("\n3. Calculating statistics...")
    stats = detector.calculate_stats(segments)

    print(f"\n{'=' * 80}")
    print("DETECTION RESULTS")
    print(f"{'=' * 80}")

    print(f"\nProcessing Stats:")
    print(f"  Total Segments: {stats['total']}")
    print(f"  Success: {stats['success']} ({stats['success_rate']}%)")
    print(f"  Warning: {stats['warning']}")
    print(f"  Error: {stats['error']}")
    print(f"  Flagged for Review: {stats['flagged']} ({stats['flagged_pct']}%)")

    print(f"\nConfidence Breakdown:")
    high_pct = round(stats['high_conf'] / stats['total'] * 100, 1)
    medium_pct = round(stats['medium_conf'] / stats['total'] * 100, 1)
    low_pct = round(stats['low_conf'] / stats['total'] * 100, 1)
    print(f"  High: {stats['high_conf']} ({high_pct}%)")
    print(f"  Medium: {stats['medium_conf']} ({medium_pct}%)")
    print(f"  Low: {stats['low_conf']} ({low_pct}%)")

    print(f"\nDetected Characters: {len(stats['speakers'])}")
    for speaker, counts in sorted(stats['speakers'].items(), key=lambda x: x[1]['segments'], reverse=True):
        if counts['speeches'] > 0:
            print(f"  {speaker}: {counts['segments']} segments ({counts['speeches']} speeches)")
        else:
            print(f"  {speaker}: {counts['segments']} segments")

    print(f"\nDetection Methods:")
    for method, count in sorted(stats['detection_methods'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {method}: {count}")

    if stats['review_flags']:
        print(f"\nReview Flags:")
        for flag, count in sorted(stats['review_flags'].items()):
            print(f"  {flag}: {count}")

    # Export to CSV
    output_dir = Path(__file__).parent / 'outputs'
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'book_detection_{timestamp}.csv'

    print(f"\n4. Exporting to CSV...")
    detector.export_to_csv(segments, output_path)
    print(f"   ✓ Saved to: {output_path}")

    # Validation
    print(f"\n{'=' * 80}")
    print("VALIDATION")
    print(f"{'=' * 80}")

    print(f"\nTarget: >80% high confidence")
    print(f"Actual: {high_pct}%")
    print(f"Status: {'✓ PASS' if high_pct >= 80 else '✗ FAIL'}")

    print(f"\nTarget: <20% flagged for review")
    print(f"Actual: {stats['flagged_pct']}%")
    print(f"Status: {'✓ PASS' if stats['flagged_pct'] < 20 else '✗ FAIL'}")

    print(f"\n{'=' * 80}")
    print("Next Steps:")
    print(f"1. Review CSV: {output_path}")
    print(f"2. Filter in Excel: Status=warning to see flagged segments")
    print(f"3. Check character names for accuracy")
    print(f"4. Validate dialogue vs narrative detection")
    print(f"{'=' * 80}")


if __name__ == '__main__':
    main()
