#!/usr/bin/env python3
"""
Test script to verify CSV stats row is added correctly.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import ArabicTTS

def test_csv_with_stats():
    """Test that CSV generation includes stats row."""

    # Test with a simple sentence
    text = "صباح الخير يا صديقي"
    dialect = "MSA"

    print("=" * 60)
    print("Testing CSV Stats Row Generation")
    print("=" * 60)
    print(f"\nInput text: {text}")
    print(f"Dialect: {dialect}\n")

    # Process text
    tts = ArabicTTS(dialect)
    result = tts.process_text(text)

    # Import hierarchical processor
    from src.core.hierarchical_processor import HierarchicalProcessor
    hierarchical_processor = HierarchicalProcessor()

    # Convert to hierarchical structure
    hierarchical_result = hierarchical_processor.process_result(
        result,
        text,
        applied_rules_mapping=None
    )

    # Import the CSV generation function from app.py
    import io
    import csv

    # Inline the _generate_hierarchical_csv function logic to test
    from app import _generate_hierarchical_csv

    csv_content = _generate_hierarchical_csv(hierarchical_result)

    # Parse and display CSV
    lines = csv_content.strip().split('\n')

    print(f"CSV Output ({len(lines)} lines):")
    print("-" * 60)

    # Show first 5 lines
    print("\nFirst 5 lines:")
    for i, line in enumerate(lines[:5]):
        print(f"  {i+1}: {line[:80]}...")

    # Show last 3 lines (should include stats)
    print("\nLast 3 lines (should include Processing Stats):")
    for i, line in enumerate(lines[-3:]):
        line_num = len(lines) - 3 + i + 1
        print(f"  {line_num}: {line}")

    # Verify stats row exists
    second_to_last = lines[-2] if len(lines) >= 2 else ""
    last_line = lines[-1]

    if 'Processing Stats' in second_to_last and 'Notes' in last_line:
        print("\n✓ SUCCESS: Both Processing Stats and Notes rows found!")
        print(f"  Stats row: {second_to_last}")
        print(f"  Notes row: {last_line}")
    else:
        print("\n✗ ERROR: Stats or Notes row missing!")
        print(f"  Second to last: {second_to_last}")
        print(f"  Last row: {last_line}")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == '__main__':
    test_csv_with_stats()
