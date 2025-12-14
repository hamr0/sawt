"""
HierarchicalProcessor - Builds hierarchical data structure for matrix display.

This module extends the existing TTS processing pipeline to generate
hierarchical data with both WORD-level and CHARACTER-level analysis,
including syllable role detection and phonology rules tracking.

Architecture:
- Accepts processed syllable data from the TTS pipeline
- Enriches with character-level analysis
- Detects syllable roles (onset, nucleus, coda)
- Tracks which phonology rules were applied to each character
- Returns hierarchical structure suitable for matrix display

Outputs hierarchical JSON structure with:
{
    "original_text": "صباح الخير",
    "dialect": "EG",
    "words": [
        {
            "type": "WORD",
            "word": "صباح",
            "position": "-",
            "original": "صباح",
            "diacritized": "صَبَاح",
            "syllable_pattern": "CV.CV",
            "syllable_index": "-",
            "syllable_role": "-",
            "phonology_rules": ["emphatic_spread"],
            "ipa": "sˁɑbɑːħ",
            "xsampa": "s_?Aba:X\\",
            "characters": [
                {
                    "type": "CHAR",
                    "word": "صباح",
                    "position": "1-initial",
                    "original": "ص",
                    "diacritized": "صَ",
                    "syllable_pattern": "-",
                    "syllable_index": "1",
                    "syllable_role": "onset",
                    "phonology_rules": ["emphatic_spread"],
                    "ipa": "sˁ",
                    "xsampa": "s_?"
                },
                ...
            ]
        },
        ...
    ]
}
"""

from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path


class HierarchicalProcessor:
    """
    Processes syllables to generate hierarchical word and character-level data.

    Responsibility:
    - Convert flat syllable data to hierarchical structure
    - Add character-level analysis with syllable role detection
    - Track which phonology rules affected each character
    - Generate matrix-compatible output format

    Attributes:
        vowels: Set of Arabic vowel characters
        consonants: Set of Arabic consonants
    """

    def __init__(self):
        """Initialize hierarchical processor with Arabic phonetic data."""
        # Vowels (tashkeel markers and long vowels)
        self.vowels = {'َ', 'ُ', 'ِ', 'ً', 'ٌ', 'ٍ', 'ْ', 'ا', 'ي', 'و', 'ى'}

        # Diacritization marks
        self.diacritics = {'َ', 'ُ', 'ِ', 'ً', 'ٌ', 'ٍ', 'ْ', 'ّ', 'ٓ'}

        # Known consonants (comprehensive list)
        self.consonants = {
            'ء', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز',
            'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك',
            'ل', 'م', 'ن', 'ه', 'و', 'ي'
        }

    def process_result(
        self,
        tts_result: Dict,
        original_text: str,
        applied_rules_mapping: Optional[Dict[str, Set[str]]] = None
    ) -> Dict:
        """
        Convert TTS result to hierarchical structure with word and character levels.

        Args:
            tts_result: Output from ArabicTTS.process_text()
            original_text: Original input text
            applied_rules_mapping: Optional mapping of syllables to applied rules

        Returns:
            Hierarchical structure with WORD and CHAR level rows
        """
        dialect = tts_result.get('dialect', 'EG')
        result = {
            "original_text": original_text,
            "dialect": dialect,
            "words": []
        }

        # Track word index for hierarchical grouping
        word_index = 0

        for word_data in tts_result.get('words', []):
            if word_data.get('type') != 'arabic_word':
                continue

            # Extract word information
            original_word = word_data.get('original', '')
            word_ipa = word_data.get('ipa', '')
            syllables = word_data.get('syllables', [])

            # Get diacritized version from syllables
            diacritized = self._reconstruct_diacritized(syllables, original_word)

            # Get syllable pattern
            syllable_pattern = self._get_syllable_pattern(syllables)

            # Extract applied rules for this word
            word_rules = self._extract_applied_rules(syllables, applied_rules_mapping)

            # Get X-SAMPA conversion
            xsampa = self._convert_to_xsampa(word_ipa)

            # Create WORD-level entry
            word_entry = {
                "type": "WORD",
                "word": original_word,
                "position": "-",
                "original": original_word,
                "diacritized": diacritized,
                "syllable_pattern": syllable_pattern,
                "syllable_index": "-",
                "syllable_role": "-",
                "phonology_rules": list(word_rules) if word_rules else [],
                "ipa": word_ipa,
                "xsampa": xsampa,
                "characters": []
            }

            # Create CHAR-level entries
            char_entries = self._create_character_entries(
                original_word,
                diacritized,
                syllables,
                word_rules,
                applied_rules_mapping
            )

            word_entry["characters"] = char_entries

            result["words"].append(word_entry)
            word_index += 1

        return result

    def _create_character_entries(
        self,
        original_word: str,
        diacritized: str,
        syllables: List[Dict],
        word_rules: Set[str],
        applied_rules_mapping: Optional[Dict]
    ) -> List[Dict]:
        """
        Create character-level entries with syllable roles and phonology tracking.

        Args:
            original_word: Original Arabic word
            diacritized: Diacritized version of the word
            syllables: Syllable data from processing
            word_rules: Rules applied at word level
            applied_rules_mapping: Per-syllable rule mapping

        Returns:
            List of character-level entries
        """
        char_entries = []
        char_index = 0

        # Map each character to its syllable for role detection
        char_to_syllable = self._map_chars_to_syllables(original_word, syllables)

        for i, char in enumerate(original_word):
            # Determine position (initial/medial/final)
            position = self._get_char_position(i, original_word)

            # Find corresponding diacritized character(s)
            diacritized_char = self._get_diacritized_char(i, original_word, diacritized)

            # Determine syllable role (onset, nucleus, coda)
            syllable_index, syllable_role = self._detect_syllable_role(
                char, i, original_word, syllables, char_to_syllable
            )

            # Extract character IPA
            char_ipa = self._extract_char_ipa(
                char, syllable_index, syllables, word_rules
            )

            # Extract character X-SAMPA
            char_xsampa = self._convert_to_xsampa(char_ipa)

            # Extract rules affecting this character
            char_rules = self._extract_char_rules(
                char, syllable_index, word_rules, applied_rules_mapping
            )

            # Create character entry
            char_entry = {
                "type": "CHAR",
                "word": original_word,
                "position": position,
                "original": char,
                "diacritized": diacritized_char,
                "syllable_pattern": "-",  # Not applicable at char level
                "syllable_index": str(syllable_index) if syllable_index >= 0 else "-",
                "syllable_role": syllable_role,
                "phonology_rules": list(char_rules) if char_rules else [],
                "ipa": char_ipa,
                "xsampa": char_xsampa
            }

            char_entries.append(char_entry)
            char_index += 1

        return char_entries

    def _map_chars_to_syllables(self, word: str, syllables: List[Dict]) -> Dict[int, int]:
        """
        Map character position to syllable index.

        Args:
            word: Original word
            syllables: List of syllables from processing

        Returns:
            Dict mapping char index to syllable index
        """
        mapping = {}
        char_pos = 0

        for syll_idx, syllable in enumerate(syllables):
            syllable_text = syllable.get('syllable', '')
            for j in range(len(syllable_text)):
                if char_pos < len(word):
                    mapping[char_pos] = syll_idx
                    char_pos += 1

        return mapping

    def _get_char_position(self, char_index: int, word: str) -> str:
        """
        Determine position label for character (initial/medial/final).

        Args:
            char_index: Index of character in word
            word: The word

        Returns:
            Position string (e.g., "1-initial", "2-medial", "3-final")
        """
        if char_index == 0:
            return f"{char_index + 1}-initial"
        elif char_index == len(word) - 1:
            return f"{char_index + 1}-final"
        else:
            return f"{char_index + 1}-medial"

    def _get_diacritized_char(self, char_index: int, original: str, diacritized: str) -> str:
        """
        Extract diacritized version of character at given index.

        Args:
            char_index: Character index in original word
            original: Original word
            diacritized: Diacritized word

        Returns:
            Diacritized character (original + diacritics)
        """
        if char_index >= len(original):
            return ""

        # Simple approach: find the diacritized version by searching
        # This is a heuristic and may need refinement for complex cases
        char = original[char_index]

        # If original and diacritized have same length, direct mapping
        if len(original) == len(diacritized):
            return diacritized[char_index]

        # Otherwise, search for the character in diacritized string
        # Look for it with any surrounding diacritics
        pos = 0
        for i, d_char in enumerate(diacritized):
            if d_char == char:
                # Found matching character
                result = d_char
                # Include any following diacritics
                j = i + 1
                while j < len(diacritized) and diacritized[j] in self.diacritics:
                    result += diacritized[j]
                    j += 1
                return result
            elif d_char not in self.diacritics:
                pos += 1
                if pos > char_index:
                    break

        return char

    def _detect_syllable_role(
        self,
        char: str,
        char_index: int,
        word: str,
        syllables: List[Dict],
        char_to_syllable: Dict[int, int]
    ) -> Tuple[int, str]:
        """
        Detect syllable role (onset, nucleus, coda) for character.

        Args:
            char: The character
            char_index: Position in word
            word: The word
            syllables: Syllable data
            char_to_syllable: Mapping of char positions to syllable indices

        Returns:
            Tuple of (syllable_index, syllable_role)
        """
        # Find which syllable contains this character
        syll_idx = char_to_syllable.get(char_index, 0)

        if syll_idx >= len(syllables):
            return (syll_idx, "unknown")

        syllable = syllables[syll_idx]
        syllable_text = syllable.get('syllable', '')

        # Detect role based on phonetic properties
        if char in self.consonants or char in {'ء', 'ل', 'ر', 'ن'}:
            # Check if it's onset or coda based on position in syllable
            char_pos_in_syll = self._get_char_pos_in_syllable(char, syllable_text, char_index)

            if char_pos_in_syll <= 0:
                role = "onset"
            else:
                # Check if there's a vowel after it in the syllable
                remaining = syllable_text[char_pos_in_syll + 1:]
                has_vowel_after = any(c in self.vowels for c in remaining)
                role = "coda" if has_vowel_after else "onset"
        else:
            # Vowel or diacritic
            role = "nucleus"

        return (syll_idx, role)

    def _get_char_pos_in_syllable(self, char: str, syllable_text: str, char_index: int) -> int:
        """
        Find position of character within its syllable.

        Args:
            char: The character
            syllable_text: The syllable text
            char_index: Index in original word (for disambiguation)

        Returns:
            Position of character in syllable (-1 if not found)
        """
        # Find first occurrence (simplified)
        try:
            return syllable_text.index(char)
        except ValueError:
            return -1

    def _extract_char_ipa(
        self,
        char: str,
        syll_idx: int,
        syllables: List[Dict],
        word_rules: Set[str]
    ) -> str:
        """
        Extract IPA for a single character.

        Args:
            char: The character
            syll_idx: Index of containing syllable
            syllables: All syllables
            word_rules: Rules applied at word level

        Returns:
            IPA representation of character
        """
        if syll_idx < 0 or syll_idx >= len(syllables):
            return ""

        syllable = syllables[syll_idx]

        # Get the syllable IPA (now properly populated by IPAMapper)
        syllable_ipa = syllable.get('ipa', '')
        syllable_text = syllable.get('syllable', '')

        # For now, return full syllable IPA
        # Full char-by-char IPA extraction would require complex phonetic analysis
        # This is acceptable for the matrix view as it shows per-syllable IPA
        return syllable_ipa

    def _extract_char_rules(
        self,
        char: str,
        syll_idx: int,
        word_rules: Set[str],
        applied_rules_mapping: Optional[Dict]
    ) -> Set[str]:
        """
        Extract rules that applied to this character.

        Args:
            char: The character
            syll_idx: Syllable index
            word_rules: Rules at word level
            applied_rules_mapping: Per-syllable rule tracking

        Returns:
            Set of rule names
        """
        char_rules = set()

        # All word-level rules affect all characters
        char_rules.update(word_rules)

        # Add syllable-specific rules if available
        if applied_rules_mapping and syll_idx in applied_rules_mapping:
            char_rules.update(applied_rules_mapping[syll_idx])

        return char_rules

    def _extract_applied_rules(
        self,
        syllables: List[Dict],
        applied_rules_mapping: Optional[Dict]
    ) -> Set[str]:
        """
        Extract all rules applied to word.

        Args:
            syllables: Syllable data
            applied_rules_mapping: Per-syllable rule mapping

        Returns:
            Set of unique rule names
        """
        rules = set()

        # Extract from each syllable if available
        for syll in syllables:
            # Check for rule tracking in syllable data (supports multiple field names)
            if 'applied_rules' in syll:
                rules.update(syll['applied_rules'])

            # Check for phonology rule flags
            if syll.get('has_gemination'):
                rules.add('gemination')
            if syll.get('sun_letter_assimilation'):
                rules.add('sun_letters')
            if syll.get('has_emphatic'):
                rules.add('emphatic_spread')

        return rules

    def _reconstruct_diacritized(self, syllables: List[Dict], original: str) -> str:
        """
        Reconstruct diacritized version from syllables.

        Args:
            syllables: Processed syllables
            original: Original word

        Returns:
            Diacritized word
        """
        # Simple concatenation of syllables
        diacritized = ''.join(syll.get('syllable', '') for syll in syllables)

        # Fallback to original if no diacritization found
        return diacritized if diacritized else original

    def _get_syllable_pattern(self, syllables: List[Dict]) -> str:
        """
        Get overall syllable pattern for word.

        Args:
            syllables: Syllables from processing

        Returns:
            Pattern string like "CV.CVC.CV"
        """
        patterns = []
        for syll in syllables:
            pattern = syll.get('pattern', 'UNKNOWN')
            patterns.append(pattern)

        return '.'.join(patterns) if patterns else "UNKNOWN"

    def _convert_to_xsampa(self, ipa: str) -> str:
        """
        Convert IPA to X-SAMPA notation (simplified).

        Args:
            ipa: IPA string

        Returns:
            X-SAMPA representation

        Note:
            This is a simplified conversion. A full implementation would
            require complete IPA-to-X-SAMPA mapping table.
        """
        # Common IPA to X-SAMPA mappings
        mappings = {
            'ɑ': 'A',
            'ː': ':',
            'ħ': 'X\\',
            'ɛ': 'E',
            'ɪ': 'I',
            'ʊ': 'U',
            'ɔ': 'O',
            'ə': '@',
            'ʃ': 'S',
            'ʒ': 'Z',
            'θ': 'T',
            'ð': 'D',
            'ŋ': 'N',
            'ʁ': 'X',
            'χ': 'X\\',
            'ʤ': 'd_z',
            'ʧ': 't_s',
            'ˁ': '_?',
            'ˤ': '_?',
        }

        result = ipa
        for ipa_char, xsampa_char in mappings.items():
            result = result.replace(ipa_char, xsampa_char)

        return result
