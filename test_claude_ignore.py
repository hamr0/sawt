#!/usr/bin/env python3
"""
Test script to verify Claude ignore patterns are working.
"""

import os
import sys
from pathlib import Path

def test_file_access():
    """Test which files Claude can access"""
    print("Testing Claude file access patterns...\n")

    # Essential files that SHOULD be accessible
    essential_files = [
        'CLAUDE.md',
        'README.md',
        'src/main.py',
        '.claudeignore',
        '.claude/settings.json'
    ]

    # Files that SHOULD be excluded
    excluded_files = [
        'docs/ARCHITECTURE.md',
        'docs/TECH_STACK.md',
        'docs/TESTING.md',
        'docs/polly/README.md',
        'tasks/TASK_LIST.md',
        'tasks/0001-prd-mvp-phase1.md',
        'reports/MVP_PHASE1_COMPLETE.md',
        'demo_output/polly_test/README.md'
    ]

    print("Essential Files (should be accessible):")
    for file_path in essential_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✓ {file_path} ({size} bytes)")
        else:
            print(f"  ✗ {file_path} (NOT FOUND)")

    print("\nExcluded Files (should NOT be loaded by Claude):")
    for file_path in excluded_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ⚠ {file_path} ({size} bytes) - SHOULD BE EXCLUDED")
        else:
            print(f"  ✓ {file_path} (not found)")

def count_files():
    """Count total files by type"""
    print("\nFile Count Summary:")

    # Count all markdown files
    md_files = list(Path('.').rglob('*.md'))
    print(f"  Total .md files: {len(md_files)}")

    # Count files in excluded directories
    excluded_dirs = ['docs', 'tasks', 'reports', 'demo_output']
    total_excluded = 0
    for dir_name in excluded_dirs:
        if os.path.exists(dir_name):
            total_excluded += len(list(Path(dir_name).rglob('*.md')))

    print(f"  Markdown files in excluded dirs: {total_excluded}")
    print(f"  Remaining markdown files: {len(md_files) - total_excluded}")

if __name__ == "__main__":
    test_file_access()
    count_files()

    print("\nNote: If you still see markdown files being loaded by Claude,")
    print("      1. Restart Claude completely")
    print("      2. Clear Claude's cache: rm -rf ~/.claude/cache/*")
    print("      3. Ensure .claudeignore is in the project root")