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
        # Load syllable patterns (same for all dialects)
        self.vowels = {'َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ا', 'ي', 'و'}

        # Define universal syllable patterns
        # These patterns are the same across all Arabic dialects
        self.patterns = {
            "CV": {"allowed": True, "examples": ["مَ", "لِ"]},
            "CVC": {"allowed": True, "examples": ["كَتَ", "بِنْ"]},
            "CVCC": {"allowed": True, "constraints": {"coda_condition": "geminate_or_sun_letter"}},
            "CVV": {"allowed": True, "examples": ["كاْ", "لِيْ"]}
        }

    def segment_syllables(self, word: str) -> List[List[str]]:
        syllables = []
        current = []
        i = 0

        while i < len(word):
            char = word[i]
            current.append(char)

            # Syllable ends at vowel or word boundary
            if char in self.vowels or i == len(word) - 1:
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

    def classify_pattern(self, syllable: List[str]) -> str:
        pattern = []
        for char in syllable:
            if char in self.vowels - {'ْ', 'ّ'}:
                pattern.append('V')
            elif char == 'ّ':
                pattern.append('C')  # Gemination marker
            elif char not in {'ْ', 'ّ'}:
                pattern.append('C')

        pattern_str = ''.join(pattern)

        # Apply dialect-specific pattern rules
        if pattern_str == 'CV':
            return 'CV'
        elif pattern_str == 'CVC':
            return 'CVC'
        elif pattern_str == 'CVCC':
            if self.validate_cvcc(syllable):
                return 'CVCC'
            return 'CVC'  # Downgrade invalid clusters
        elif 'VV' in pattern_str:
            return 'CVV'
        else:
            return 'UNKNOWN'

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
        # Step 2: Analyze character positions (universal)
        analyzed = [self.analyze_char(i, token) for i, token in enumerate(tokens)]
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

        for token in tokens:
            if token["type"] == "word" and any(char["type"] == "arabic" for char in token["chars"]):
                current_word.extend(token["chars"])
            else:
                if current_word:
                    words.append({"type": "arabic_word", "chars": current_word})
                    current_word = []
                words.append(token)

        if current_word:
            words.append({"type": "arabic_word", "chars": current_word})

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
            ipa_transcription = self.ipa_mapper.map_to_ipa(syllables, dialect)

            # Add IPA to syllables for output compatibility
            for i, syllable in enumerate(syllables):
                # For backward compatibility, add basic IPA if needed
                # The full IPA is already in ipa_transcription
                syllable["ipa"] = syllable.get("syllable", "")

            result["words"].append({
                "type": "arabic_word",
                "original": word_str,
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
        # but we need to modify it to not generate IPA
        syllable_data = self.syllabifier.segment_syllables(word)
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