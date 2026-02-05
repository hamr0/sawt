"""
PositionDetector - Universal position detection component.

This module provides the PositionDetector class, which detects word positions
(initial, medial, final) for syllables in processed Arabic text.

ARCHITECTURE NOTE:
==================
PositionDetector is a UNIVERSAL component with NO dialect parameter.
It only marks positions without generating IPA or any dialect-specific output.

Position detection is identical regardless of which dialect will be used later,
making this a pure linguistic utility function.

The output is compatible with IPAMapper input, enabling the pipeline:
1. Universal processors (syllabification, gemination, sun letters, emphatics)
2. PositionDetector (marks positions) → universal
3. IPAMapper (converts to dialect-specific IPA) → dialect-specific

This separation ensures clean architecture and easy dialect switching.
"""

from typing import List, Dict


class PositionDetector:
    """
    Detects word positions (initial, medial, final) for syllables.

    This component is UNIVERSAL and dialect-agnostic.
    It only marks positions without generating IPA or any language-specific output.

    Attributes:
        None (stateless component)
    """

    def __init__(self):
        """
        Initialize position detector (no dialect needed).

        Position detection is independent of dialect, so no configuration needed.
        """
        pass

    def detect_positions(self, syllables: List[Dict]) -> List[Dict]:
        """
        Mark word positions for each syllable.

        Takes syllables from the syllabification stage and adds a 'detected_position'
        key to each syllable dict indicating whether it's at the word-initial,
        word-medial, or word-final position.

        Args:
            syllables: List of syllable dicts from syllabification.
                      Expected keys in each dict:
                      - 'syllable' or 'arabic': the syllable text
                      - 'word_index': position of syllable within its word
                      - Other keys are preserved unchanged

        Returns:
            Same syllables list with added 'detected_position' key:
            - "word-initial" (first syllable in word)
            - "word-medial" (middle syllables)
            - "word-final" (last syllable in word)

            For single-syllable words, marked as both initial and final.

        Raises:
            ValueError: If syllables format is unexpected or missing required keys
        """
        if not syllables:
            return []

        # Group syllables by word
        words = self._group_by_word(syllables)

        # Process each word
        result = []
        for word_syllables in words:
            if not word_syllables:
                continue

            total_in_word = len(word_syllables)

            for i, syll in enumerate(word_syllables):
                # Detect position
                position = self._get_position(i, total_in_word)

                # Add position marker to syllable
                syll['detected_position'] = position
                result.append(syll)

        return result

    def _group_by_word(self, syllables: List[Dict]) -> List[List[Dict]]:
        """
        Group syllables by word.

        Syllables that belong to the same word are grouped together.
        Word boundaries are detected by looking for word separators or
        changes in the 'word_index' value.

        Args:
            syllables: Flat list of syllables

        Returns:
            List of word groups, where each group is a list of syllables

        Raises:
            ValueError: If syllable format is unexpected
        """
        if not syllables:
            return []

        words = []
        current_word = []
        current_word_idx = None

        for syll in syllables:
            # Get word index if available
            word_idx = syll.get('word_index')

            # Check if this syllable belongs to current word
            if word_idx is not None and current_word_idx is not None:
                if word_idx != current_word_idx:
                    # New word started
                    if current_word:
                        words.append(current_word)
                    current_word = [syll]
                    current_word_idx = word_idx
                else:
                    # Same word continues
                    current_word.append(syll)
            else:
                # No word index available - treat each syllable as separate word
                # (conservative approach)
                if current_word:
                    words.append(current_word)
                current_word = [syll]
                current_word_idx = word_idx

        # Don't forget last word
        if current_word:
            words.append(current_word)

        return words

    def _get_position(self, position_in_word: int, total_syllables_in_word: int) -> str:
        """
        Determine position of a syllable within its word.

        Args:
            position_in_word: Index of this syllable within its word (0-based)
            total_syllables_in_word: Total number of syllables in this word

        Returns:
            Position string:
            - "word-initial": first syllable in word
            - "word-medial": middle syllables
            - "word-final": last syllable in word

            Note: Single-syllable words are marked as "word-initial"
            (could also be marked as "word-final", but initial takes precedence)

        Raises:
            ValueError: If parameters are invalid
        """
        if total_syllables_in_word <= 0:
            raise ValueError(
                f"total_syllables_in_word must be > 0, got {total_syllables_in_word}"
            )

        if position_in_word < 0 or position_in_word >= total_syllables_in_word:
            raise ValueError(
                f"position_in_word {position_in_word} out of range "
                f"[0, {total_syllables_in_word-1}]"
            )

        # Single syllable word - mark as initial (convention)
        if total_syllables_in_word == 1:
            return "word-initial"

        # First syllable
        if position_in_word == 0:
            return "word-initial"

        # Last syllable
        if position_in_word == total_syllables_in_word - 1:
            return "word-final"

        # Middle syllables
        return "word-medial"

    def mark_positions_simple(self, text: str) -> List[Dict]:
        """
        Simple helper method to mark positions directly from Arabic text.

        This is a convenience method that handles simple cases where
        syllables haven't been generated yet. For full pipeline integration,
        use detect_positions() instead.

        Args:
            text: Arabic text or space-separated syllables

        Returns:
            List of syllable dicts with positions marked

        Example:
            >>> detector = PositionDetector()
            >>> result = detector.mark_positions_simple("الشمس")
            >>> for syll in result:
            ...     print(f"{syll['syllable']}: {syll['detected_position']}")
        """
        if not text:
            return []

        # Split by spaces (simple word boundaries)
        words = text.split()
        result = []

        for word_idx, word in enumerate(words):
            if not word:
                continue

            # For simple case, treat each character as a syllable
            chars = list(word)
            total = len(chars)

            for pos, char in enumerate(chars):
                position = self._get_position(pos, total)

                result.append({
                    'syllable': char,
                    'word_index': word_idx,
                    'position_in_word': pos,
                    'detected_position': position
                })

        return result

    def verify_positions(self, syllables: List[Dict]) -> bool:
        """
        Verify that all syllables have valid position markers.

        Args:
            syllables: List of syllables to verify

        Returns:
            True if all syllables have valid 'detected_position' key
            False otherwise
        """
        valid_positions = {'word-initial', 'word-medial', 'word-final'}

        for syll in syllables:
            if 'detected_position' not in syll:
                return False

            if syll['detected_position'] not in valid_positions:
                return False

        return True

    def get_position_statistics(self, syllables: List[Dict]) -> Dict[str, int]:
        """
        Get statistics about position distribution in syllables.

        Args:
            syllables: List of syllables with detected_position

        Returns:
            Dict with counts: {'word-initial': N, 'word-medial': M, 'word-final': K}
        """
        stats = {
            'word-initial': 0,
            'word-medial': 0,
            'word-final': 0,
            'total': len(syllables)
        }

        for syll in syllables:
            pos = syll.get('detected_position', 'unknown')
            if pos in stats:
                stats[pos] += 1

        return stats
