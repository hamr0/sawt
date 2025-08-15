from abc import ABC, abstractmethod


class BaseDialectProcessor(ABC):
    def __init__(self, dialect: str):
        self.dialect = dialect
        self.load_resources()

    def load_resources(self):
        """Load dialect-specific resources"""
        pass

    @abstractmethod
    def apply_special_rules(self, ipa_output: List[Dict]) -> List[Dict]:
        """Apply dialect-specific phonological rules"""
        pass

    def handle_gemination(self, syllables: List[Dict]) -> List[Dict]:
        """Default gemination handling"""
        for syl in syllables:
            if 'ّ' in syl['syllable']:
                # Find the geminated consonant
                gem_index = syl['syllable'].index('ّ') - 1
                consonant = syl['syllable'][gem_index]
                # Apply gemination in IPA
                syl['ipa'] = syl['ipa'].replace(consonant, consonant + "ː")
        return syllables