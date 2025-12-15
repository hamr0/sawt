"""
IPAMapper - Dialect-specific IPA generation component.

This module provides the IPAMapper class, which is responsible for converting
processed Arabic syllables to IPA (International Phonetic Alphabet) notation
using dialect-specific phonetic data.

ARCHITECTURE NOTE:
==================
IPAMapper is the ONLY component that is dialect-aware. All phonological
processing (syllabification, gemination, sun letters, emphatics) happens
BEFORE this mapper and is universal (dialect-independent).

Dialect selection happens AT THIS STEP ONLY, making it easy to:
1. Switch dialects between calls
2. Debug IPA output
3. Understand dialect-specific phonological differences
4. Add new dialects without changing other components

The lookup precedence is:
1. Position-specific IPA (word-initial, word-medial, word-final)
2. Context-specific IPA (if context provided)
3. Default IPA
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path


class IPAMapper:
    """
    Maps processed Arabic syllables to IPA using dialect-specific data.

    This is the ONLY component that is dialect-aware. All phonological
    processing is universal; dialect selection happens here.

    Attributes:
        master_tts: Dict containing all dialect phonetic data
        lookup_tables: Pre-built lookup tables for each dialect (O(1) access)
    """

    def __init__(self, master_tts_path: Optional[str] = None):
        """
        Initialize IPAMapper by loading masterTTS.json ONCE.

        Does NOT select a dialect - dialect is passed to lookup methods.
        All dialects are loaded at initialization for fast switching.

        Args:
            master_tts_path: Path to masterTTS.json
                           Defaults to data/dictionaries/masterTTS.json
                           relative to project root.

        Raises:
            FileNotFoundError: If masterTTS.json not found
            json.JSONDecodeError: If masterTTS.json is invalid JSON
        """
        # Determine path to masterTTS.json
        if master_tts_path is None:
            # Default to project structure
            project_root = Path(__file__).parent.parent.parent
            master_tts_path = project_root / "data" / "dictionaries" / "masterTTS.json"
        else:
            master_tts_path = Path(master_tts_path)

        # Load master TTS data ONCE
        self.master_tts = self._load_master_tts(str(master_tts_path))

        # Build lookup tables for ALL dialects (one-time cost)
        # This enables O(1) lookups and fast dialect switching
        self.lookup_tables = {}
        for dialect in self.master_tts.keys():
            self.lookup_tables[dialect] = self._build_lookup_table(dialect)

        # Track available dialects
        self.available_dialects = list(self.master_tts.keys())

    def _load_master_tts(self, path: str) -> Dict:
        """
        Load masterTTS.json from disk.

        Args:
            path: Path to masterTTS.json file

        Returns:
            Dict with structure: {dialect: [entries...]}
            Each entry has keys like "Arabic letter", "IPA", "Position", etc.

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"masterTTS.json not found at: {path}\n"
                f"Expected location: data/dictionaries/masterTTS.json"
            )

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    def _normalize_arabic_char(self, char: str) -> str:
        """
        Normalize Arabic character variants to standard forms.

        This handles common variants that should be treated identically:
        - Alef maksura (ى) -> Regular alef (ا) for vowel lookup
        - Hamza variants -> Standard forms

        Args:
            char: Arabic character to normalize

        Returns:
            Normalized character
        """
        # Map alef maksura to regular alef (common vowel variant)
        if char == 'ى':  # ARABIC LETTER ALEF MAKSURA
            return 'ا'   # ARABIC LETTER ALEF

        # Map hamza variants
        if char == 'إ':  # ARABIC LETTER ALEF WITH HAMZA BELOW
            return 'أ'   # ARABIC LETTER ALEF WITH HAMZA ABOVE

        if char == 'آ':  # ARABIC LETTER ALEF WITH MADDA ABOVE
            return 'ا'   # ARABIC LETTER ALEF

        # No normalization needed
        return char

    def _build_lookup_table(self, dialect: str) -> Dict[str, Dict[str, str]]:
        """
        Build efficient lookup structure for a dialect.

        Structure:
        {
            'أ': {
                'default': 'ʔ',
                'word-initial': '[ʔ]',
                'word-medial': '∅',
                'word-final': '[ʔ]'
            },
            'ب': { ... },
            ...
        }

        This structure enables O(1) character lookups with position context.

        Args:
            dialect: Dialect name ("EG", "MSA", "Gulf", etc.)

        Returns:
            Dict with character -> position -> IPA mappings

        Raises:
            KeyError: If dialect not in master_tts
        """
        lookup = {}

        if dialect not in self.master_tts:
            raise KeyError(
                f"Dialect '{dialect}' not found in masterTTS. "
                f"Available: {list(self.master_tts.keys())}"
            )

        # Iterate through all entries for this dialect
        for entry in self.master_tts[dialect]:
            char = entry.get("Arabic letter")
            position = entry.get("Position", "default")
            ipa = entry.get("IPA", "")

            if not char:
                continue

            # Initialize character entry if needed
            if char not in lookup:
                lookup[char] = {}

            # Store IPA for this position
            lookup[char][position] = ipa

        return lookup

    def map_to_ipa(
        self,
        syllables: List[Dict],
        dialect: str
    ) -> str:
        """
        Convert processed syllables to IPA for specified dialect.

        Takes syllables that have been processed by universal processors
        (gemination, sun letters, position detection, emphatic spread)
        and converts them to IPA using dialect-specific mappings.

        Args:
            syllables: Processed syllables from phonological processors.
                      Each should have keys like:
                      - 'syllable': the text
                      - 'detected_position': position in word
                      - 'has_gemination': if geminated
                      - 'sun_letter_assimilation': if assimilated
                      - 'has_emphatic': if emphatic
            dialect: Target dialect ("EG", "MSA", "Gulf", "Levantine", "Maghrebi")

        Returns:
            Complete IPA transcription string

        Raises:
            ValueError: If dialect not supported
            KeyError: If character not in dialect data
        """
        if dialect not in self.available_dialects:
            raise ValueError(
                f"Unsupported dialect: {dialect}\n"
                f"Available dialects: {self.available_dialects}"
            )

        ipa_parts = []

        for syllable_dict in syllables:
            syllable_text = syllable_dict.get('syllable', '')
            position = syllable_dict.get('detected_position', 'default')
            has_gemination = syllable_dict.get('has_gemination', False)
            has_emphatic = syllable_dict.get('has_emphatic', False)

            # Build context for lookup
            context = {
                'has_gemination': has_gemination,
                'has_emphatic': has_emphatic,
                'position': position
            }

            # Convert syllable to IPA
            syllable_ipa = self._convert_syllable(
                syllable_text,
                dialect,
                position,
                context
            )

            # IMPORTANT: Store the IPA back in the syllable for hierarchical processor
            syllable_dict['ipa'] = syllable_ipa
            ipa_parts.append(syllable_ipa)

        return ''.join(ipa_parts)

    def _convert_syllable(
        self,
        syllable: str,
        dialect: str,
        position: str = "default",
        context: Optional[Dict] = None
    ) -> str:
        """
        Convert a single syllable to IPA.

        Args:
            syllable: The syllable text to convert
            dialect: Target dialect
            position: Position context
            context: Optional context dict

        Returns:
            IPA string for this syllable
        """
        if not syllable:
            return ''

        ipa_chars = []
        for char in syllable:
            ipa = self.get_ipa_for_char(
                char,
                dialect,
                position,
                context
            )
            ipa_chars.append(ipa)

        return ''.join(ipa_chars)

    def get_ipa_for_char(
        self,
        char: str,
        dialect: str,
        position: str = "default",
        context: Optional[Dict] = None
    ) -> str:
        """
        Get IPA for a single character in specified dialect and position.

        Lookup precedence:
        1. Position-specific IPA (word-initial, word-medial, word-final)
        2. Context-specific IPA (if context provided and relevant)
        3. Default IPA

        Args:
            char: Arabic character to look up
            dialect: Target dialect ("EG", "MSA", etc.)
            position: Position context ("default", "word-initial", "word-medial", "word-final")
            context: Optional context dict with keys like:
                    - 'has_gemination': if consonant is geminated
                    - 'has_emphatic': if near emphatic consonant
                    - 'after_emphatic': if follows emphatic

        Returns:
            IPA string for this character in this context

        Raises:
            ValueError: If dialect not supported
            KeyError: If character not found and no fallback available
        """
        if dialect not in self.lookup_tables:
            raise ValueError(
                f"Unsupported dialect: {dialect}\n"
                f"Available: {list(self.lookup_tables.keys())}"
            )

        lookup = self.lookup_tables[dialect]

        # Normalize character variants before lookup
        normalized_char = self._normalize_arabic_char(char)

        # Try to find character in lookup table
        if normalized_char not in lookup:
            # Character not in dialect data
            # Try fallback strategies
            if char.isspace() or char in '.,!?;:':
                # Punctuation/whitespace - pass through
                return char
            else:
                # Warn but return character as fallback
                # In production, might raise KeyError instead
                return char

        char_ipa_map = lookup[normalized_char]

        # Try position-specific lookup first
        if position in char_ipa_map:
            return char_ipa_map[position]

        # Try default if position not found
        if 'default' in char_ipa_map:
            return char_ipa_map['default']

        # Handle gemination marker if applicable
        if context and context.get('has_gemination'):
            # Add length marker for doubled consonants
            base_ipa = char_ipa_map.get('default', char)
            # In IPA, length is marked with ː (long mark)
            if base_ipa and base_ipa != '∅':
                return base_ipa + 'ː'
            return base_ipa

        # Fallback to first available IPA
        for pos, ipa in char_ipa_map.items():
            if ipa and ipa != '∅':
                return ipa

        # Last resort - return character itself
        return char

    def get_available_dialects(self) -> List[str]:
        """
        Get list of available dialects.

        Returns:
            List of dialect codes ("EG", "MSA", etc.)
        """
        return self.available_dialects.copy()

    def validate_dialect(self, dialect: str) -> bool:
        """
        Check if dialect is supported.

        Args:
            dialect: Dialect code to validate

        Returns:
            True if dialect is available, False otherwise
        """
        return dialect in self.available_dialects

    def get_dialect_statistics(self, dialect: str) -> Dict:
        """
        Get statistics about a dialect's phonetic coverage.

        Args:
            dialect: Dialect code

        Returns:
            Dict with statistics like entry_count, unique_chars, etc.

        Raises:
            ValueError: If dialect not supported
        """
        if not self.validate_dialect(dialect):
            raise ValueError(f"Unsupported dialect: {dialect}")

        entries = self.master_tts[dialect]
        unique_chars = set(e.get("Arabic letter") for e in entries if e.get("Arabic letter"))

        return {
            'dialect': dialect,
            'total_entries': len(entries),
            'unique_characters': len(unique_chars),
            'available_positions': set(
                e.get("Position", "default") for e in entries
            )
        }
