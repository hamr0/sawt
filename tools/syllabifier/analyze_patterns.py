#!/usr/bin/env python3
"""
Analyze Patterns CLI Tool

Analyzes the aggregated failures database and generates a comprehensive markdown
report with pattern frequency ranking, examples, and insights for prioritization.

Usage:
    python analyze_patterns.py

Output:
    - Creates tools/syllabifier/reports/pattern_report_YYYYMMDD_HHMMSS.md
    - Prints summary statistics
    - Returns pattern frequency ranking for prioritization
"""

import csv
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple


def load_aggregated_database(db_path: Path) -> List[Dict]:
    """
    Load all entries from aggregated failures database.

    Args:
        db_path: Path to aggregated_failures.csv

    Returns:
        List of failure dictionaries
    """
    failures = []

    if not db_path.exists():
        print(f"Warning: Database not found at {db_path}")
        return failures

    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                failures.append(row)
    except Exception as e:
        print(f"Error reading database: {e}")
        return []

    return failures


def analyze_patterns(failures: List[Dict]) -> Dict:
    """
    Analyze patterns and generate statistics.

    Args:
        failures: List of failure dictionaries

    Returns:
        Dictionary with analysis results
    """
    # Count pattern frequencies
    pattern_counts = Counter()
    pattern_examples = defaultdict(list)
    pattern_layers = defaultdict(list)

    for failure in failures:
        pattern = failure.get('Pattern', '')
        word = failure.get('Word', '')
        diacritized = failure.get('Diacritized', '')
        failed_layers = failure.get('Failed_Layers', '')

        pattern_counts[pattern] += 1

        # Store up to 3 examples per pattern
        if len(pattern_examples[pattern]) < 3:
            pattern_examples[pattern].append({
                'word': word,
                'diacritized': diacritized,
                'failed_layers': failed_layers
            })

        # Track which layers fail for each pattern
        if failed_layers:
            pattern_layers[pattern].append(failed_layers)

    # Calculate statistics
    total_failures = len(failures)
    unique_patterns = len(pattern_counts)
    most_common = pattern_counts.most_common()

    analysis = {
        'total_failures': total_failures,
        'unique_patterns': unique_patterns,
        'pattern_counts': pattern_counts,
        'pattern_examples': pattern_examples,
        'pattern_layers': pattern_layers,
        'most_common': most_common
    }

    return analysis


def categorize_pattern(pattern: str) -> str:
    """
    Categorize pattern by type for grouping.

    Args:
        pattern: Pattern string (e.g., 'CVVV', 'CVCCVV')

    Returns:
        Category string
    """
    length = len(pattern)
    c_count = pattern.count('C')
    v_count = pattern.count('V')

    # Identify pattern characteristics
    if v_count >= 4:
        return "Very Long Vowel Sequences (4+ V)"
    elif v_count == 3:
        return "Long Vowel Sequences (3 V)"
    elif c_count >= 4:
        return "Complex Consonant Clusters (4+ C)"
    elif c_count == 3:
        return "Consonant Clusters (3 C)"
    elif length >= 6:
        return "Complex Patterns (6+ chars)"
    else:
        return "Other Patterns"


def detect_gemination_likelihood(examples: List[Dict]) -> bool:
    """
    Heuristic to detect if pattern likely involves gemination (shadda).

    Args:
        examples: List of example dictionaries

    Returns:
        True if gemination is likely present
    """
    # Simple heuristic: check if diacritized forms contain shadda (ّ)
    for example in examples:
        if 'ّ' in example.get('diacritized', ''):
            return True
    return False


def generate_markdown_report(analysis: Dict, report_path: Path):
    """
    Generate comprehensive markdown report.

    Args:
        analysis: Analysis results dictionary
        report_path: Path to output markdown file
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(report_path, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"# Syllabifier Pattern Analysis Report\n\n")
        f.write(f"**Generated**: {timestamp}\n\n")
        f.write(f"---\n\n")

        # Summary Statistics
        f.write(f"## Summary Statistics\n\n")
        f.write(f"- **Total Failures**: {analysis['total_failures']}\n")
        f.write(f"- **Unique Pattern Types**: {analysis['unique_patterns']}\n")
        f.write(f"- **Most Common Pattern**: {analysis['most_common'][0][0]} ({analysis['most_common'][0][1]} occurrences)\n\n")
        f.write(f"---\n\n")

        # Pattern Frequency Ranking
        f.write(f"## Pattern Frequency Ranking\n\n")
        f.write(f"Patterns ordered by frequency (highest to lowest) for prioritization:\n\n")

        for rank, (pattern, count) in enumerate(analysis['most_common'], 1):
            percentage = (count / analysis['total_failures']) * 100
            f.write(f"### {rank}. `{pattern}` - {count} occurrences ({percentage:.1f}%)\n\n")

            # Category
            category = categorize_pattern(pattern)
            f.write(f"**Category**: {category}\n\n")

            # Gemination detection
            examples = analysis['pattern_examples'][pattern]
            has_gemination = detect_gemination_likelihood(examples)
            if has_gemination:
                f.write(f"**Gemination Detected**: Yes (likely contains shadda ّ)\n\n")

            # Failed Layers
            layers = analysis['pattern_layers'][pattern]
            if layers:
                layer_counts = Counter(layers)
                f.write(f"**Failed Layers**: {', '.join([f'{k} ({v}x)' for k, v in layer_counts.most_common()])}\n\n")

            # Examples
            f.write(f"**Examples**:\n\n")
            for i, example in enumerate(examples, 1):
                word = example['word']
                diac = example['diacritized']
                failed = example['failed_layers']
                f.write(f"{i}. Word: `{word}` | Diacritized: `{diac}` | Failed: `{failed}`\n")

            f.write(f"\n")

        # Category Summary
        f.write(f"---\n\n")
        f.write(f"## Pattern Categories Summary\n\n")

        category_counts = defaultdict(int)
        for pattern, count in analysis['pattern_counts'].items():
            category = categorize_pattern(pattern)
            category_counts[category] += count

        f.write(f"| Category | Total Occurrences | Percentage |\n")
        f.write(f"|----------|-------------------|------------|\n")

        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / analysis['total_failures']) * 100
            f.write(f"| {category} | {count} | {percentage:.1f}% |\n")

        # Recommendations
        f.write(f"\n---\n\n")
        f.write(f"## Recommended Fix Priority\n\n")
        f.write(f"Based on frequency analysis, recommend addressing patterns in this order:\n\n")

        top_5 = analysis['most_common'][:5]
        for rank, (pattern, count) in enumerate(top_5, 1):
            percentage = (count / analysis['total_failures']) * 100
            category = categorize_pattern(pattern)
            f.write(f"{rank}. **{pattern}** ({count} cases, {percentage:.1f}%) - {category}\n")

        f.write(f"\n")
        f.write(f"Fixing these top 5 patterns would address **{sum(c for _, c in top_5)} failures** ")
        f.write(f"({(sum(c for _, c in top_5) / analysis['total_failures'] * 100):.1f}% of total).\n\n")


def main():
    """Main entry point for analyze_patterns CLI tool."""
    # Setup paths
    script_dir = Path(__file__).parent
    db_path = script_dir / 'data' / 'aggregated_failures.csv'
    reports_dir = script_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = reports_dir / f'pattern_report_{timestamp}.md'

    print(f"Analyzing patterns from: {db_path}")

    # Load database
    failures = load_aggregated_database(db_path)

    if not failures:
        print("No failures found in database. Run aggregate_failures.py first.")
        return

    print(f"Loaded {len(failures)} failure records")

    # Analyze patterns
    analysis = analyze_patterns(failures)

    # Generate report
    generate_markdown_report(analysis, report_path)

    print(f"\nAnalysis complete!")
    print(f"Report generated: {report_path}")
    print(f"\nTop 5 patterns:")
    for rank, (pattern, count) in enumerate(analysis['most_common'][:5], 1):
        percentage = (count / analysis['total_failures']) * 100
        print(f"  {rank}. {pattern}: {count} ({percentage:.1f}%)")


if __name__ == '__main__':
    main()
