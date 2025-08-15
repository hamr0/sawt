import json
from typing import List, Dict


class ArabicSyllabifier:
    def __init__(self, dialect: str):
        self.dialect = dialect
        self.vowels = {'َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ا', 'ي', 'و'}
        self.load_resources()

    def load_resources(self):
        with open('data/dictionaries/masterTTS.json', 'r', encoding='utf-8') as f:
            self.master_data = json.load(f)
        with open('data/dictionaries/syllable_patterns.json', 'r', encoding='utf-8') as f:
            self.patterns = json.load(f)["syllable_patterns"][self.dialect]

    def segment(self, word: str) -> List[List[str]]:
        syllables = []
        current_syl = []

        for char in word:
            current_syl.append(char)
            if char in self.vowels or char == 'ّ':
                syllables.append(current_syl)
                current_syl = []

        if current_syl:
            if syllables:
                syllables[-1].extend(current_syl)
            else:
                syllables.append(current_syl)

        return syllables

    def classify_pattern(self, syllable: List[str]) -> str:
        pattern = []
        for char in syllable:
            if char in self.vowels - {'ْ', 'ّ'}:
                pattern.append('V')
            elif char in ['ّ', 'ْ']:
                continue
            else:
                pattern.append('C')

        pattern_str = ''.join(pattern)

        # CV Pattern
        if pattern_str == 'CV':
            return 'CV'

        # CVC Pattern
        elif pattern_str == 'CVC':
            return 'CVC'

        # CVCC Pattern
        elif pattern_str == 'CVCC':
            if self.validate_cvcc(syllable):
                return 'CVCC'
            return 'CVC'  # Downgrade if invalid

        # CVV Pattern
        elif pattern_str == 'CVV':
            return 'CVV'

        return 'UNKNOWN'

    def validate_cvcc(self, syllable: List[str]) -> bool:
        """Validate CVCC pattern against dialect rules"""
        constraints = self.patterns["CVCC"].get("constraints", {})
        coda_condition = constraints.get("coda_condition", "")

        # Last two characters form the coda cluster
        coda_cluster = syllable[-2:]

        if coda_condition == "geminate_or_sun_letter":
            sun_letters = {'ت', 'ث', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ل', 'ن'}
            return coda_cluster[1] == 'ّ' or coda_cluster[1] in sun_letters

        return True  # Default valid if no constraints