#!/usr/bin/env python3
"""
Quick test of hierarchical processor with real data.
"""

import json
from src.main import ArabicTTS
from src.core.hierarchical_processor import HierarchicalProcessor

def test_hierarchical_processor():
    """Test hierarchical processor with sample text."""

    # Initialize processors
    tts = ArabicTTS(dialect='EG')
    processor = HierarchicalProcessor()

    # Test text
    text = "صباح"
    print(f"\nProcessing: {text}")

    # Step 1: Get standard TTS result
    tts_result = tts.process_text(text)
    print("\nTTS Result:")
    print(json.dumps(tts_result, ensure_ascii=False, indent=2))

    # Step 2: Convert to hierarchical structure
    hierarchical = processor.process_result(tts_result, text)
    print("\nHierarchical Result:")
    print(json.dumps(hierarchical, ensure_ascii=False, indent=2))

    # Verify structure
    assert 'words' in hierarchical, "Missing 'words' key"
    assert len(hierarchical['words']) > 0, "No words in result"

    # Check first word has WORD-level entry
    first_word = hierarchical['words'][0]
    assert first_word.get('type') == 'WORD', f"Expected WORD type, got {first_word.get('type')}"
    assert 'characters' in first_word, "Missing 'characters' key in word"

    # Check character entries
    characters = first_word.get('characters', [])
    assert len(characters) > 0, "No character entries"

    for char_entry in characters:
        assert char_entry.get('type') == 'CHAR', f"Expected CHAR type, got {char_entry.get('type')}"
        assert 'syllable_role' in char_entry, "Missing syllable_role"
        assert 'phonology_rules' in char_entry, "Missing phonology_rules"
        print(f"  {char_entry['original']} -> IPA: {char_entry['ipa']}, Role: {char_entry['syllable_role']}")

    print("\n✓ Test passed!")

if __name__ == '__main__':
    test_hierarchical_processor()
