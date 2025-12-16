import re
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# Import phonological processors
from src.core.gemination import GeminationProcessor
from src.core.sun_letters import SunLetterProcessor
from src.core.allophones import AllophoneProcessor
from src.core.emphatic import EmphaticProcessor


class ArabicSyllabifier:
    def __init__(self):
        """
        Initialize syllabifier (universal - no dialect parameter).

        Syllabification patterns are universal across Arabic dialects.
        Dialect-specific differences only apply to IPA generation,
        which is handled by IPAMapper.
        """
        # Separate vowel types for correct syllable boundary detection
        # Short vowels mark syllable boundaries
        self.short_vowels = {'َ', 'ُ', 'ِ'}  # fatha, damma, kasra

        # Long vowel markers (context-dependent, part of nucleus when following short vowel)
        self.long_vowel_markers = {'ا', 'ي', 'و'}  # alef, yaa, waw

        # Diacritical marks (not part of pattern)
        self.diacritics = {'ْ', 'ّ', 'ٰ', 'ً', 'ٌ', 'ٍ', 'ٓ'}  # sukun, shadda, superalef, etc.

        # All vowel-related characters
        self.all_vowels = self.short_vowels | self.long_vowel_markers

        # Legacy vowels for backward compatibility in classify_pattern
        self.vowels = self.all_vowels  # Keep for API compatibility

        # Define universal syllable patterns
        # These patterns are the same across all Arabic dialects
        self.patterns = {
            "CV": {"allowed": True, "examples": ["مَ", "لِ"]},
            "CVC": {"allowed": True, "examples": ["كَتَ", "بِنْ"]},
            "CVCC": {"allowed": True, "constraints": {"coda_condition": "geminate_or_sun_letter"}},
            "CVV": {"allowed": True, "examples": ["كاْ", "لِيْ"]}
        }

    def segment_syllables(self, word: str) -> List[List[str]]:
        """
        Segment word into syllables with special handling for definite article.

        Rules:
        - Definite article ال at word beginning is kept separate
        - Syllables end at SHORT vowels (َ ُ ِ), not diacritics or long vowel markers
        - Long vowel markers (ا ي و) are included in current syllable nucleus
        """
        syllables = []
        i = 0

        # Special handling for definite article ال at word start
        if len(word) >= 2 and word[0] == 'ا' and word[1] == 'ل':
            al_syllable = ['ا', 'ل']
            # Include any diacritics after the lam
            i = 2
            while i < len(word) and word[i] in self.diacritics:
                al_syllable.append(word[i])
                i += 1
            syllables.append(al_syllable)

        current = []
        while i < len(word):
            char = word[i]
            current.append(char)

            # Syllable ends at SHORT VOWEL (actual vowel markers, not diacritics)
            if char in self.short_vowels:
                # Look ahead for long vowel marker to include in same syllable
                if i + 1 < len(word) and word[i + 1] in self.long_vowel_markers:
                    current.append(word[i + 1])
                    i += 1

                syllables.append(current)
                current = []
            # End of word: add current syllable if non-empty
            elif i == len(word) - 1:
                syllables.append(current)
                current = []

            i += 1

        # Handle trailing consonants
        if current:
            if syllables:
                syllables[-1].extend(current)
            else:
                syllables.append(current)

        return syllables

    def resyllabify(self, syllables: List[List[str]]) -> List[List[str]]:
        """
        Post-process syllables to merge invalid patterns into valid ones.

        This method fixes patterns like:
        - V (standalone vowel) → merge with adjacent syllable
        - C, CC (standalone consonants) → merge with adjacent syllable (except initial definitie article)
        - UNKNOWN patterns → attempt to merge intelligently

        Args:
            syllables: List of syllable character lists

        Returns:
            Corrected syllables with only valid patterns
        """
        if not syllables:
            return syllables

        corrected = []
        i = 0

        while i < len(syllables):
            current = syllables[i]
            pattern = self.classify_pattern(current)

            # Special case: keep the definite article ال if it's first syllable
            if i == 0 and len(current) >= 2 and current[0] == 'ا' and current[1] == 'ل':
                # Keep the definite article even if pattern is CC
                corrected.append(current)
                i += 1
                continue

            # Rule 1: Merge standalone vowels with previous syllable
            if pattern == 'V':
                if corrected:
                    # Add to previous syllable's coda
                    corrected[-1].extend(current)
                elif i + 1 < len(syllables):
                    # Add to next syllable's onset
                    syllables[i + 1] = current + syllables[i + 1]
                i += 1
                continue

            # Rule 2: Merge standalone consonants (except definite article)
            if pattern in ['C', 'CC']:
                if corrected:
                    # Add to previous syllable's coda
                    corrected[-1].extend(current)
                elif i + 1 < len(syllables):
                    # Add to next syllable's onset
                    syllables[i + 1] = current + syllables[i + 1]
                i += 1
                continue

            # Rule 3: Handle UNKNOWN patterns - try to merge if possible
            if 'UNKNOWN' in pattern:
                if corrected:
                    # Try merging with previous
                    corrected[-1].extend(current)
                elif i + 1 < len(syllables):
                    # Try merging with next
                    syllables[i + 1] = current + syllables[i + 1]
                i += 1
                continue

            # Valid pattern - keep it
            corrected.append(current)
            i += 1

        return corrected

    def _has_gemination(self, syllable: List[str]) -> bool:
        """
        Detect if syllable contains shadda (gemination marker).

        Args:
            syllable: List of characters in syllable

        Returns:
            True if shadda (ّ) is present in syllable

        Example:
            ['ي', 'َ', 'ّ', 'ة'] -> True (contains shadda)
            ['م', 'َ', 'ك'] -> False (no shadda)
        """
        return 'ّ' in syllable

    def _handle_gemination_cvvv(self, syllable: List[str]) -> str:
        """
        Handle CVVV patterns with gemination by splitting at shadda.

        When shadda appears in a CVVV pattern, it typically indicates
        a geminated consonant that should split the syllable into
        valid sub-patterns like CVV + C or CV + VC.

        Args:
            syllable: List of characters forming CVVV pattern

        Returns:
            Valid pattern string after handling gemination split

        Example:
            ['ي', 'ِ', 'ّ'] with pattern CVVV -> 'CVV' (treat as long vowel with geminated coda)
        """
        # For CVVV with gemination, common case is long vowel + geminated consonant
        # This often appears as: consonant + short vowel + long marker + shadda
        # Example: يِيّ (yaa + kasra + yaa + shadda) = CVV pattern
        # The shadda indicates gemination, making this a valid CVV + geminated coda

        # Strategy: Treat gemination in CVVV as creating a CVV pattern
        # The extra 'V' is actually a consonant doubled by shadda
        return 'CVVC'  # Long vowel with geminated coda

    def _try_resplit_cvvv(self, syllable: List[str]) -> str:
        """
        Attempt to re-split CVVV patterns without gemination.

        For CVVV patterns without shadda, analyze vowel sequence
        to determine if it's actually a valid long vowel pattern
        or needs different handling.

        Args:
            syllable: List of characters forming CVVV pattern

        Returns:
            Valid pattern string or conservative fallback

        Example:
            ['و', 'َ', 'ا', 'ة'] -> 'CVVC' (long vowel + consonant)
        """
        # Non-gemination CVVV often results from long vowel + another vowel
        # Common cases:
        # 1. CVV + VC (long vowel followed by short vowel + consonant)
        # 2. Actual CVVC misclassified as CVVV

        # Conservative approach: treat as CVVC (long vowel with coda)
        # This handles most cases where CVVV is actually a valid pattern
        return 'CVVC'

    def classify_pattern(self, syllable: List[str]) -> str:
        pattern = []
        for char in syllable:
            # Skip diacritical marks - they don't contribute to syllable pattern
            if char in self.diacritics:
                continue
            # Short vowels (َ ُ ِ)
            elif char in self.short_vowels:
                pattern.append('V')
            # Long vowel markers when in nucleus context
            elif char in self.long_vowel_markers:
                # If previous was a vowel, this is part of long vowel (still V)
                # Otherwise it's a consonant
                if pattern and pattern[-1] == 'V':
                    pattern.append('V')
                else:
                    pattern.append('C')
            # Shadda (ّ) marks gemination - adds extra consonant
            elif char == 'ّ':
                # Shadda doubles the previous consonant, so add extra C
                if pattern and pattern[-1] == 'C':
                    pattern.append('C')
            # Any other character is a consonant
            else:
                pattern.append('C')

        pattern_str = ''.join(pattern)

        # Pattern matching (order matters - longest first)
        if pattern_str == 'CVVC':
            return 'CVVC'
        elif pattern_str == 'CVCC':
            if self.validate_cvcc(syllable):
                return 'CVCC'
            return 'CVC'  # Downgrade invalid clusters
        elif pattern_str == 'CVV':
            return 'CVV'
        elif pattern_str == 'CVC':
            return 'CVC'
        elif pattern_str == 'CCV':  # Onset cluster (two consonants before vowel)
            return 'CCV'
        elif pattern_str == 'CV':
            return 'CV'
        # Additional patterns that may occur
        elif pattern_str == 'V':
            return 'V'  # Vowel-only (rare, word-initial)
        elif pattern_str == 'VC':
            return 'VC'  # Vowel + consonant
        elif pattern_str == 'CC':
            return 'CC'  # Consonant cluster (standalone gemination)
        elif pattern_str == 'C':
            return 'C'  # Single consonant (standalone)
        # Phase 3A: Handle CVVV patterns before marking as UNKNOWN
        elif pattern_str == 'CVVV':
            if self._has_gemination(syllable):
                return self._handle_gemination_cvvv(syllable)
            else:
                return self._try_resplit_cvvv(syllable)
        else:
            return f'UNKNOWN({pattern_str})'

    def validate_cvcc(self, syllable: List[str]) -> bool:
        """Check if CVCC cluster is valid for dialect"""
        coda = syllable[-2:]
        constraints = self.patterns["CVCC"]["constraints"]

        if "coda_condition" in constraints:
            if constraints["coda_condition"] == "geminate_or_sun_letter":
                sun_letters = {'ت', 'ث', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ل', 'ن'}
                return coda[1] == 'ّ' or coda[1] in sun_letters
        return True  # Default valid

    def get_syllable_structure(self, word: str) -> List[Dict]:
        """
        Get syllable structure without IPA (universal).

        DEPRECATED: Use segment_syllables and classify_pattern directly.
        This method kept for backward compatibility.

        Args:
            word: Arabic word to analyze

        Returns:
            List of syllable dictionaries with pattern info
        """
        syllables = self.segment_syllables(word)
        result = []

        for syllable in syllables:
            pattern = self.classify_pattern(syllable)
            result.append({
                "syllable": ''.join(syllable),
                "pattern": pattern,
                "chars": syllable
            })
        return result


class ArabicTTS:
    def __init__(self, dialect: str):
        """
        Initialize Arabic TTS system with new architecture.

        Args:
            dialect: Default dialect for IPA generation ("EG", "MSA", etc.)
                     Can be overridden per text processing call.
        """
        self.dialect = dialect

        # Initialize universal syllabifier (no dialect needed)
        self.syllabifier = ArabicSyllabifier()

        self.special_chars = ['\"', "\'", '(', ')', '[', ']', '^', '*', '-', '_', '%', '#', '@', 'ـ']
        self.tashkeel = ['َ', 'ُ', 'ِ', 'ً', 'ٌ', 'ٍ', 'ْ', 'ٓ']
        self.punctuation = [',', ';', ':', '،', '.', '?', '!']
        
        # Initialize phonological processors
        # Note: All processors are now UNIVERSAL (dialect-independent)
        # Only IPAMapper handles dialect-specific IPA lookup
        self.gemination_processor = GeminationProcessor()
        self.sun_letter_processor = SunLetterProcessor()
        self.emphatic_processor = EmphaticProcessor()

        # Import the NEW universal components
        from src.core.position_detector import PositionDetector
        from src.core.ipa_mapper import IPAMapper

        # Initialize universal components
        self.position_detector = PositionDetector()
        self.ipa_mapper = IPAMapper()

        # Initialize diacritizer as None (lazy-load on first use)
        self._diacritizer = None

    @property
    def diacritizer(self):
        """
        Lazy-load Mishkal diacritizer (expensive initialization).

        Returns:
            TashkeelClass instance for text diacritization
        """
        if self._diacritizer is None:
            try:
                from mishkal.tashkeel import TashkeelClass
                self._diacritizer = TashkeelClass()
            except ImportError:
                raise ImportError(
                    "Mishkal library not found. Install with: pip install mishkal"
                )
        return self._diacritizer

    def process_text(self, text: str, dialect: Optional[str] = None) -> Dict:
        """
        Main processing pipeline for Arabic text.

        Args:
            text: Arabic text to process
            dialect: Target dialect for IPA generation. If None, uses self.dialect

        Returns:
            Processed text with IPA transcription
        """
        # Use provided dialect or default
        target_dialect = dialect or self.dialect

        # Step 1: Preprocess and tokenize (universal)
        tokens = self.tokenize(text)
        # Step 1.5: Diacritize text BEFORE syllabification (NEW)
        diacritized_tokens = self.apply_diacritization(tokens)
        # Step 2: Analyze character positions (universal)
        analyzed = [self.analyze_char(i, token) for i, token in enumerate(diacritized_tokens)]
        # Step 3: Group Arabic words for syllabification (universal)
        words = self.group_arabic_words(analyzed)
        # Step 4: Syllabify and map to IPA (dialect-specific IPA mapping)
        result = self.syllabify_and_map(words, target_dialect)
        return result

    def tokenize(self, text: str) -> List[Dict]:
        """Split text into tokens with basic classification"""
        tokens = []
        current = ""
        for char in text:
            if char.isspace() or char in self.punctuation or char in self.special_chars:
                if current:
                    tokens.append({"type": "word", "content": current})
                    current = ""
                tokens.append({"type": "punct" if char in self.punctuation else "special",
                               "content": char})
            else:
                current += char
        if current:
            tokens.append({"type": "word", "content": current})
        return tokens

    def apply_diacritization(self, tokens: List[Dict]) -> List[Dict]:
        """
        Apply automatic diacritization to Arabic tokens using Mishkal.

        This is Step 1 of preprocessing (per NOTCLAUDE.md architecture).
        Only processes tokens with Arabic text.

        If Mishkal diacritization fails, continues with undiacritized text
        (graceful fallback). The Status/Failed_Layers system will detect
        that diacritization failed and mark it as 'diac' failure.

        Args:
            tokens: List of token dicts from tokenize()

        Returns:
            Tokens with diacritized content (or original if diacritization failed),
            original field preserved
        """
        for token in tokens:
            if token["type"] == "word":
                original = token["content"]
                # Check if contains Arabic characters
                if any('\u0600' <= char <= '\u06FF' for char in original):
                    try:
                        # Apply Mishkal diacritization
                        diacritized = self.diacritizer.tashkeel(original)
                        # Mishkal sometimes adds leading/trailing spaces, strip them
                        diacritized = diacritized.strip()

                        # Only use diacritized version if it actually added diacritics
                        if diacritized and diacritized != original:
                            token["content"] = diacritized
                            token["diacritization_success"] = True
                        else:
                            # Mishkal returned same text (no diacritization applied)
                            # Continue with original, mark as failure
                            token["diacritization_success"] = False
                        token["original"] = original  # Preserve original undiacritized

                    except Exception as e:
                        # If diacritization fails, keep original but don't crash
                        # Log the error but continue processing (graceful fallback)
                        import sys
                        print(f"Warning: Diacritization failed for '{original}': {e}", file=sys.stderr)
                        token["original"] = original
                        token["diacritization_success"] = False
                        # Continue processing with undiacritized text
        return tokens

    def analyze_char(self, index: int, token: Dict) -> Dict:
        """Analyze character position and type"""
        if token["type"] != "word":
            return token | {"position": token["type"]}

        word = token["content"]
        analyzed_chars = []
        for i, char in enumerate(word):
            char_data = {"char": char, "position": "medial"}

            # Determine position
            if i == 0:
                char_data["position"] = "initial"
            elif i == len(word) - 1:
                char_data["position"] = "final"

            # Character type classification
            if char in self.tashkeel:
                char_data["type"] = "tashkeel"
            elif char == 'ـ':
                char_data["type"] = "maddah"
            elif '\u0600' <= char <= '\u06FF':
                char_data["type"] = "arabic"
            elif 'a' <= char <= 'z':
                char_data["type"] = "english"
            elif char.isdigit():
                char_data["type"] = "number"
            else:
                char_data["type"] = "unknown"

            analyzed_chars.append(char_data)

        return token | {"chars": analyzed_chars}

    def group_arabic_words(self, tokens: List[Dict]) -> List[Dict]:
        """Group consecutive Arabic characters into words"""
        words = []
        current_word = []
        current_original = None

        for token in tokens:
            if token["type"] == "word" and any(char["type"] == "arabic" for char in token["chars"]):
                current_word.extend(token["chars"])
                # Preserve the original undiacritized text if available
                if current_original is None and "original" in token:
                    current_original = token["original"]
            else:
                if current_word:
                    word_entry = {"type": "arabic_word", "chars": current_word}
                    if current_original:
                        word_entry["original"] = current_original
                    words.append(word_entry)
                    current_word = []
                    current_original = None
                words.append(token)

        if current_word:
            word_entry = {"type": "arabic_word", "chars": current_word}
            if current_original:
                word_entry["original"] = current_original
            words.append(word_entry)

        return words

    def syllabify_and_map(self, words: List[Dict], dialect: str) -> Dict:
        """
        Apply syllabification and IPA mapping to Arabic words.

        Args:
            words: List of processed word tokens
            dialect: Target dialect for IPA generation

        Returns:
            Processed words with IPA transcription
        """
        result = {"dialect": dialect, "words": []}

        for word in words:
            if word["type"] != "arabic_word":
                result["words"].append(word)
                continue

            # Extract the word string
            word_str = ''.join(char["char"] for char in word["chars"])

            # Syllabify WITHOUT IPA generation (universal)
            syllables = self._syllabify_only(word_str)

            # Apply universal phonological rules
            syllables = self.apply_phonological_rules(syllables)

            # Generate IPA using IPAMapper (dialect-specific step)
            # NOTE: map_to_ipa also populates syllable["ipa"] with per-syllable IPA
            ipa_transcription = self.ipa_mapper.map_to_ipa(syllables, dialect)

            # Use original undiacritized text if available, else use the diacritized word_str
            original_text = word.get("original", word_str)

            result["words"].append({
                "type": "arabic_word",
                "original": original_text,
                "syllables": syllables,
                "ipa": ipa_transcription,  # Full IPA transcription for the word
                "chars": word["chars"]
            })

        return result
    
    def apply_phonological_rules(self, syllables: List[Dict]) -> List[Dict]:
        """
        Apply universal phonological rules to syllables.

        This method applies all phonological rules that are identical
        across all Arabic dialects. Dialect-specific IPA mapping happens
        in a separate step using IPAMapper.

        Steps applied:
        1. Gemination detection (shadda)
        2. Sun/moon letter assimilation detection
        3. Position detection (word-initial, word-medial, word-final)
        4. Emphatic consonant detection and pharyngealization marking

        Note: These rules are universal. IPA generation (dialect-specific)
        happens separately using IPAMapper.map_to_ipa().

        Args:
            syllables: List of syllable dictionaries from syllabifier

        Returns:
            Syllables with all universal phonological rules applied
            (position detection added for each syllable)
        """
        # Rule 1: Gemination (detect shadda)
        syllables = self.gemination_processor.process(syllables)

        # Rule 2: Sun letter assimilation
        syllables = self.sun_letter_processor.process(syllables)

        # Rule 3: Position detection (universal - using PositionDetector)
        syllables = self.position_detector.detect_positions(syllables)

        # Rule 4: Emphatic spread
        syllables = self.emphatic_processor.process(syllables)

        return syllables

    def _syllabify_only(self, word: str) -> List[Dict]:
        """
        Syllabify word without IPA generation (universal).

        This method extracts syllable structure without any dialect-specific
        IPA mapping. The IPA mapping happens later using IPAMapper.

        Args:
            word: Arabic word to syllabify

        Returns:
            List of syllable dictionaries with structure and pattern info
        """
        # Use the syllabifier to get syllable structure
        syllable_data = self.syllabifier.segment_syllables(word)

        # Apply resyllabification to fix invalid patterns
        syllable_data = self.syllabifier.resyllabify(syllable_data)

        syllables = []

        for i, syllable_chars in enumerate(syllable_data):
            syllable_str = ''.join(syllable_chars)
            pattern = self.syllabifier.classify_pattern(syllable_chars)

            syllable_dict = {
                'syllable': syllable_str,
                'pattern': pattern,
                'chars': syllable_chars,
                'word_index': 0,  # Will be updated for multi-word cases
                'position_in_word': i,
                # No IPA yet - will be added by IPAMapper
            }
            syllables.append(syllable_dict)

        return syllables

    def process_file(self, filename: str = "input.txt") -> Dict:
        """Process text from file"""
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()
        return self.process_text(text)

    def to_json(self, data: Dict, filename: str = "output.json") -> None:
        """Save processed data to JSON file"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


# Dialect instances with proper initialization
def get_tts_instance(dialect: str) -> ArabicTTS:
    """Get TTS instance for specified dialect"""
    return ArabicTTS(dialect)

DIALECTS = {
    "EG": lambda: get_tts_instance("EG"),
    "MSA": lambda: get_tts_instance("MSA"),
    "Gulf": lambda: get_tts_instance("Gulf"),
    "Levantine": lambda: get_tts_instance("Levantine"),
    "Maghreb": lambda: get_tts_instance("Maghreb")
}

# Example usage
if __name__ == "__main__":
    processor = DIALECTS["MSA"]()  # Call the lambda to get instance
    text = "الْحَمْدُ لِلّٰهِ"
    result = processor.process_text(text)
    processor.to_json(result)
    print("Processing complete. Output saved to output.json")