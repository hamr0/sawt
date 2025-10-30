import re
import json
from typing import List, Dict, Tuple
from pathlib import Path

# Import phonological processors
from src.core.gemination import GeminationProcessor
from src.core.sun_letters import SunLetterProcessor
from src.core.allophones import AllophoneProcessor
from src.core.emphatic import EmphaticProcessor


class ArabicSyllabifier:
    def __init__(self, dialect: str):
        self.dialect = dialect
        with open("data/dictionaries/masterTTS.json", "r", encoding="utf-8") as f:
            self.master = json.load(f)
        
        # Create default syllable patterns if missing
        if "syllable_patterns" not in self.master:
            self.master["syllable_patterns"] = {
                "EG": {
                    "CV": {"allowed": True, "examples": ["مَ", "لِ"]},
                    "CVC": {"allowed": True, "examples": ["كَتَ", "بِنْ"]},
                    "CVCC": {"allowed": True, "constraints": {"coda_condition": "geminate_or_sun_letter"}},
                    "CVV": {"allowed": True, "examples": ["كاْ", "لِيْ"]}
                },
                "MSA": {
                    "CV": {"allowed": True, "examples": ["مَ", "لِ"]},
                    "CVC": {"allowed": True, "examples": ["كَتَ", "بِنْ"]},
                    "CVCC": {"allowed": True, "constraints": {"coda_condition": "geminate_or_sun_letter"}},
                    "CVV": {"allowed": True, "examples": ["كاْ", "لِيْ"]}
                },
                "Gulf": {
                    "CV": {"allowed": True, "examples": ["مَ", "لِ"]},
                    "CVC": {"allowed": True, "examples": ["كَتَ", "بِنْ"]},
                    "CVCC": {"allowed": True, "constraints": {"coda_condition": "geminate_or_sun_letter"}},
                    "CVV": {"allowed": True, "examples": ["كاْ", "لِيْ"]}
                },
                "Levantine": {
                    "CV": {"allowed": True, "examples": ["مَ", "لِ"]},
                    "CVC": {"allowed": True, "examples": ["كَتَ", "بِنْ"]},
                    "CVCC": {"allowed": True, "constraints": {"coda_condition": "geminate_or_sun_letter"}},
                    "CVV": {"allowed": True, "examples": ["كاْ", "لِيْ"]}
                },
                "Maghreb": {
                    "CV": {"allowed": True, "examples": ["مَ", "لِ"]},
                    "CVC": {"allowed": True, "examples": ["كَتَ", "بِنْ"]},
                    "CVCC": {"allowed": True, "constraints": {"coda_condition": "geminate_or_sun_letter"}},
                    "CVV": {"allowed": True, "examples": ["كاْ", "لِيْ"]}
                }
            }
        
        self.patterns = self.master["syllable_patterns"].get(dialect, self.master["syllable_patterns"]["MSA"])
        self.vowels = {'َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ا', 'ي', 'و'}

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

    def map_to_ipa(self, word: str) -> List[Dict]:
        syllables = self.segment_syllables(word)
        ipa_result = []

        for syllable in syllables:
            pattern = self.classify_pattern(syllable)
            ipa_syllable = self.apply_ipa_rules(syllable, pattern)
            ipa_result.append({
                "syllable": ''.join(syllable),
                "pattern": pattern,
                "ipa": ipa_syllable
            })
        return ipa_result

    def apply_ipa_rules(self, syllable: List[str], pattern: str) -> str:
        ipa_parts = []
        for char in syllable:
            # Find letter in dialect data
            for entry in self.master[self.dialect]:
                if entry["Arabic letter"] == char:
                    # Try pattern-specific IPA first
                    syllable_info = entry.get("Syllable_Position", {})
                    if pattern in syllable_info:
                        ipa_parts.append(syllable_info[pattern]["ipa_adjustment"])
                    else:
                        ipa_parts.append(entry["IPA"])
                    break
            else:  # Character not found
                ipa_parts.append(char)

        return ''.join(ipa_parts)


class ArabicTTS:
    def __init__(self, dialect: str):
        self.dialect = dialect
        self.syllabifier = ArabicSyllabifier(dialect)
        self.special_chars = ['\"', "\'", '(', ')', '[', ']', '^', '*', '-', '_', '%', '#', '@', 'ـ']
        self.tashkeel = ['َ', 'ُ', 'ِ', 'ً', 'ٌ', 'ٍ', 'ْ', 'ٓ']
        self.punctuation = [',', ';', ':', '،', '.', '?', '!']
        
        # Initialize phonological processors
        self.gemination_processor = GeminationProcessor(dialect)
        self.sun_letter_processor = SunLetterProcessor(dialect)
        self.allophone_processor = AllophoneProcessor(dialect)
        self.emphatic_processor = EmphaticProcessor(dialect)

    def process_text(self, text: str) -> Dict:
        """Main processing pipeline for Arabic text"""
        # Step 1: Preprocess and tokenize
        tokens = self.tokenize(text)
        # Step 2: Analyze character positions
        analyzed = [self.analyze_char(i, token) for i, token in enumerate(tokens)]
        # Step 3: Group Arabic words for syllabification
        words = self.group_arabic_words(analyzed)
        # Step 4: Syllabify and map to IPA
        result = self.syllabify_and_map(words)
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

    def syllabify_and_map(self, words: List[Dict]) -> Dict:
        """Apply syllabification and IPA mapping to Arabic words"""
        result = {"dialect": self.dialect, "words": []}

        for word in words:
            if word["type"] != "arabic_word":
                result["words"].append(word)
                continue

            # Extract the word string
            word_str = ''.join(char["char"] for char in word["chars"])
            # Syllabify and get IPA
            syllables = self.syllabifier.map_to_ipa(word_str)
            
            # Apply phonological rules in correct order
            syllables = self.apply_phonological_rules(syllables, word_str)
            
            # Add position info to each syllable
            for syllable in syllables:
                start = word_str.find(syllable["syllable"])
                syllable["position"] = word["chars"][start]["position"]

            result["words"].append({
                "type": "arabic_word",
                "original": word_str,
                "syllables": syllables,
                "chars": word["chars"]
            })

        return result
    
    def apply_phonological_rules(self, syllables: List[Dict], word_text: str) -> List[Dict]:
        """
        Apply all phonological rules in the correct order
        
        Order of application:
        1. Gemination (shadda detection) - highest priority
        2. Sun letter assimilation (/al/ + sun letter)
        3. Positional allophones (position-dependent IPA)
        4. Emphatic spread (pharyngealization)
        
        Args:
            syllables: List of syllable dictionaries from syllabifier
            word_text: Original Arabic word text
        
        Returns:
            Syllables with all phonological rules applied
        """
        # Rule 1: Gemination (detect shadda)
        syllables = self.gemination_processor.process(syllables)
        
        # Rule 2: Sun letter assimilation
        syllables = self.sun_letter_processor.process(syllables)
        syllables = self.sun_letter_processor.apply_assimilation(syllables, word_text)
        
        # Rule 3: Positional allophones
        syllables = self.allophone_processor.process(syllables, word_text)
        syllables = self.allophone_processor.apply_ipa_to_syllables(syllables)
        
        # Rule 4: Emphatic spread
        syllables = self.emphatic_processor.process(syllables)
        syllables = self.emphatic_processor.apply_pharyngealization(syllables)
        
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