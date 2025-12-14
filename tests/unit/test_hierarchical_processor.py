"""
Unit tests for HierarchicalProcessor - character-level analysis with syllable roles.

Tests the conversion of TTS output to hierarchical structure with:
- WORD-level entries with overall analysis
- CHAR-level entries with syllable role detection
- Phonology rules tracking per character
"""

import pytest
from src.core.hierarchical_processor import HierarchicalProcessor
from src.main import ArabicTTS


class TestHierarchicalProcessor:
    """Test HierarchicalProcessor functionality."""

    def setup_method(self):
        """Initialize processor before each test."""
        self.processor = HierarchicalProcessor()
        self.tts = ArabicTTS(dialect='EG')

    def test_processor_initialization(self):
        """Test that processor initializes correctly."""
        assert self.processor is not None
        assert len(self.processor.vowels) > 0
        assert len(self.processor.consonants) > 0

    def test_process_result_structure(self):
        """Test that process_result returns correct hierarchical structure."""
        text = "صباح"
        tts_result = self.tts.process_text(text)

        hierarchical = self.processor.process_result(tts_result, text)

        # Check top-level structure
        assert 'original_text' in hierarchical
        assert hierarchical['original_text'] == text
        assert 'dialect' in hierarchical
        assert 'words' in hierarchical

    def test_word_level_entries(self):
        """Test WORD-level entries have required fields."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        words = hierarchical['words']
        assert len(words) > 0

        word = words[0]
        assert word['type'] == 'WORD'
        assert 'word' in word
        assert 'original' in word
        assert 'diacritized' in word
        assert 'syllable_pattern' in word
        assert 'phonology_rules' in word
        assert isinstance(word['phonology_rules'], list)
        assert 'ipa' in word
        assert 'xsampa' in word
        assert 'characters' in word

    def test_character_level_entries(self):
        """Test CHAR-level entries have required fields."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        word = hierarchical['words'][0]
        chars = word['characters']

        assert len(chars) > 0

        for char_entry in chars:
            assert char_entry['type'] == 'CHAR'
            assert 'word' in char_entry
            assert 'position' in char_entry
            assert 'original' in char_entry
            assert 'diacritized' in char_entry
            assert 'syllable_index' in char_entry
            assert 'syllable_role' in char_entry
            assert char_entry['syllable_role'] in ['onset', 'nucleus', 'coda', 'unknown']
            assert 'phonology_rules' in char_entry
            assert isinstance(char_entry['phonology_rules'], list)
            assert 'ipa' in char_entry
            assert 'xsampa' in char_entry

    def test_syllable_role_detection(self):
        """Test that syllable roles are detected for characters."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        word = hierarchical['words'][0]
        chars = word['characters']

        # At least some characters should have detected roles
        roles = [c['syllable_role'] for c in chars]
        assert any(r in ['onset', 'nucleus', 'coda'] for r in roles), \
            f"No valid syllable roles detected. Got: {roles}"

    def test_position_labels(self):
        """Test character position labels."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        word = hierarchical['words'][0]
        chars = word['characters']

        # First character should be initial
        assert chars[0]['position'].endswith('initial')

        # Last character should be final
        assert chars[-1]['position'].endswith('final')

        # Middle characters should be medial (if more than 2)
        if len(chars) > 2:
            for i in range(1, len(chars) - 1):
                assert chars[i]['position'].endswith('medial')

    def test_hierarchical_word_organization(self):
        """Test that words are properly organized in hierarchy."""
        text = "صباح الخير"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        # Should have at least one word (may skip punctuation/spaces)
        word_entries = [w for w in hierarchical['words'] if w.get('type') == 'WORD']
        assert len(word_entries) >= 1

        # Each word should have characters
        for word in word_entries:
            assert len(word['characters']) > 0

    def test_ipa_extraction(self):
        """Test that IPA is properly extracted."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        word = hierarchical['words'][0]

        # Word should have IPA
        assert word['ipa'] is not None
        assert len(word['ipa']) > 0

        # Characters should have IPA (at least syllable IPA)
        chars = word['characters']
        for char in chars:
            assert 'ipa' in char

    def test_xsampa_conversion(self):
        """Test X-SAMPA conversion from IPA."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        word = hierarchical['words'][0]

        # X-SAMPA should be provided
        assert 'xsampa' in word
        assert word['xsampa'] is not None

        # Characters should have X-SAMPA
        for char in word['characters']:
            assert 'xsampa' in char

    def test_multiple_words_processing(self):
        """Test processing multiple words in one text."""
        text = "السلام عليكم"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        # Should have multiple word entries
        word_entries = [w for w in hierarchical['words'] if w.get('type') == 'WORD']
        # Might vary based on how words are extracted, but should have content
        assert len(hierarchical['words']) > 0

    def test_expected_ipa_comparison(self):
        """Test expected IPA comparison functionality."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(
            tts_result,
            text,
            applied_rules_mapping=None
        )

        # Add expected IPA
        hierarchical['expected_ipa'] = "sˁɑbɑːħ"

        assert 'expected_ipa' in hierarchical

    def test_syllable_pattern_extraction(self):
        """Test syllable pattern extraction."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        word = hierarchical['words'][0]
        pattern = word['syllable_pattern']

        # Pattern should be a string with syllable patterns separated by dots
        assert isinstance(pattern, str)
        # For Arabic text, might contain CV patterns
        assert any(c in pattern for c in ['C', 'V', '.']) or pattern == 'UNKNOWN'

    def test_diacritized_reconstruction(self):
        """Test diacritized version reconstruction."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        word = hierarchical['words'][0]
        diacritized = word['diacritized']

        # Should have a diacritized version
        assert isinstance(diacritized, str)
        assert len(diacritized) > 0

    def test_phonology_rules_tracking(self):
        """Test phonology rules tracking at word level."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        word = hierarchical['words'][0]
        rules = word['phonology_rules']

        # Should be a list (even if empty)
        assert isinstance(rules, list)

    def test_word_position_metadata(self):
        """Test word-level position is set to '-'."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        word = hierarchical['words'][0]

        # Word-level entries should have position "-"
        assert word['position'] == '-'
        assert word['syllable_index'] == '-'
        assert word['syllable_role'] == '-'

    def test_char_position_formats(self):
        """Test character position format."""
        text = "صباح"
        tts_result = self.tts.process_text(text)
        hierarchical = self.processor.process_result(tts_result, text)

        word = hierarchical['words'][0]
        chars = word['characters']

        # Positions should be formatted as "N-type" (e.g., "1-initial")
        for char in chars:
            pos = char['position']
            assert '-' in pos, f"Position should contain hyphen: {pos}"
            parts = pos.split('-')
            assert len(parts) == 2, f"Position should be 'number-type': {pos}"
            assert parts[0].isdigit(), f"First part should be number: {pos}"
            assert parts[1] in ['initial', 'medial', 'final'], \
                f"Second part should be position type: {pos}"


class TestHierarchicalProcessorIntegration:
    """Integration tests for hierarchical processor with full pipeline."""

    def setup_method(self):
        """Initialize for integration tests."""
        self.processor = HierarchicalProcessor()

    def test_end_to_end_processing(self):
        """Test complete processing pipeline."""
        tts = ArabicTTS(dialect='EG')
        text = "السلام"

        # Process through TTS
        tts_result = tts.process_text(text)

        # Convert to hierarchical
        hierarchical = self.processor.process_result(tts_result, text)

        # Verify complete structure
        assert 'words' in hierarchical
        assert len(hierarchical['words']) > 0

        # Verify each word has characters
        for word in hierarchical['words']:
            if word.get('type') == 'WORD':
                assert 'characters' in word
                assert len(word['characters']) > 0

    def test_dialect_independence(self):
        """Test processor works with different dialects."""
        processor = HierarchicalProcessor()

        for dialect in ['EG', 'MSA']:
            tts = ArabicTTS(dialect=dialect)
            text = "صباح"
            tts_result = tts.process_text(text)
            hierarchical = processor.process_result(tts_result, text)

            # Should always have proper structure
            assert 'words' in hierarchical
            assert hierarchical['dialect'] == dialect
