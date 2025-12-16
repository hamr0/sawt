#!/usr/bin/env python3
"""
Aggregate Failures CLI Tool

Extracts UNKNOWN syllable patterns from TTS test CSV results and aggregates them
into a growing database for pattern analysis and tracking over time.

Usage:
    python aggregate_failures.py <test_csv_path>

Example:
    python aggregate_failures.py /home/hamr/Downloads/tts_matrix_20251216_144123-EG.csv

Output:
    - Appends new UNKNOWN patterns to tools/syllabifier/data/aggregated_failures.csv
    - Prints summary: "Added X new failures to database (total: Y)"
"""

import sys
import csv
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Set


def extract_unknown_patterns(csv_path: str) -> List[Tuple[str, str, str, str]]:
    """
    Extract UNKNOWN patterns from test CSV.

    Args:
        csv_path: Path to the test results CSV file

    Returns:
        List of tuples: (word, diacritized, pattern, failed_layers)
    """
    unknown_patterns = []

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Only process WORD rows with UNKNOWN patterns
                if row.get('Type') != 'WORD':
                    continue

                syllable_pattern = row.get('Syllable_Pattern', '')

                # Check if pattern contains UNKNOWN
                if 'UNKNOWN' in syllable_pattern:
                    word = row.get('Word', '')
                    diacritized = row.get('Diacritized', '')
                    failed_layers = row.get('Failed_Layers', '')

                    # Extract the actual UNKNOWN pattern(s) from syllable string
                    # Pattern format: "CV.UNKNOWN(CVVV).CV" or "UNKNOWN(CCCCCCCCCC)"
                    unknown_matches = re.findall(r'UNKNOWN\(([^)]+)\)', syllable_pattern)

                    for unknown_pattern in unknown_matches:
                        unknown_patterns.append((
                            word,
                            diacritized,
                            unknown_pattern,
                            failed_layers
                        ))

    except FileNotFoundError:
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)

    return unknown_patterns


def load_existing_database(db_path: Path) -> Set[Tuple[str, str, str]]:
    """
    Load existing aggregated failures database.

    Args:
        db_path: Path to aggregated_failures.csv

    Returns:
        Set of existing entries (word, diacritized, pattern) for deduplication
    """
    existing = set()

    if not db_path.exists():
        return existing

    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row.get('Word', '')
                diacritized = row.get('Diacritized', '')
                pattern = row.get('Pattern', '')
                existing.add((word, diacritized, pattern))
    except Exception as e:
        print(f"Warning: Could not read existing database: {e}")

    return existing


def append_to_database(
    db_path: Path,
    new_failures: List[Tuple[str, str, str, str]],
    existing: Set[Tuple[str, str, str]]
) -> int:
    """
    Append new failures to aggregated database.

    Args:
        db_path: Path to aggregated_failures.csv
        new_failures: List of (word, diacritized, pattern, failed_layers)
        existing: Set of existing entries for deduplication

    Returns:
        Number of new entries added
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    added_count = 0

    # Create file with headers if it doesn't exist
    file_exists = db_path.exists()

    try:
        with open(db_path, 'a', encoding='utf-8', newline='') as f:
            fieldnames = ['Timestamp', 'Word', 'Diacritized', 'Pattern', 'Failed_Layers']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for word, diacritized, pattern, failed_layers in new_failures:
                # Skip duplicates
                if (word, diacritized, pattern) in existing:
                    continue

                writer.writerow({
                    'Timestamp': timestamp,
                    'Word': word,
                    'Diacritized': diacritized,
                    'Pattern': pattern,
                    'Failed_Layers': failed_layers
                })
                added_count += 1

                # Add to existing set to avoid duplicates within same batch
                existing.add((word, diacritized, pattern))

    except Exception as e:
        print(f"Error writing to database: {e}")
        sys.exit(1)

    return added_count


def count_total_entries(db_path: Path) -> int:
    """Count total entries in database."""
    if not db_path.exists():
        return 0

    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return sum(1 for _ in reader)
    except:
        return 0


def main():
    """Main entry point for aggregate_failures CLI tool."""
    if len(sys.argv) < 2:
        print("Usage: python aggregate_failures.py <test_csv_path>")
        print("\nExample:")
        print("  python aggregate_failures.py /home/hamr/Downloads/tts_matrix_20251216_144123-EG.csv")
        sys.exit(1)

    csv_path = sys.argv[1]

    # Setup paths
    script_dir = Path(__file__).parent
    db_path = script_dir / 'data' / 'aggregated_failures.csv'

    print(f"Extracting UNKNOWN patterns from: {csv_path}")

    # Extract patterns from test CSV
    new_failures = extract_unknown_patterns(csv_path)
    print(f"Found {len(new_failures)} UNKNOWN pattern instances")

    # Load existing database
    existing = load_existing_database(db_path)

    # Append new failures
    added_count = append_to_database(db_path, new_failures, existing)

    # Count total
    total_count = count_total_entries(db_path)

    print(f"\nAdded {added_count} new failures to database (total: {total_count})")
    print(f"Database location: {db_path}")


if __name__ == '__main__':
    main()
