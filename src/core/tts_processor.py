from typing import Dict, List
from .syllabifier import ArabicSyllabifier
from .ipa_mapper import IPAMapper
from src.dialects import get_dialect_processor


class TTSProcessor:
    def __init__(self, dialect: str = "MSA"):
        self.dialect = dialect
        self.syllabifier = ArabicSyllabifier(dialect)
        self.ipa_mapper = IPAMapper(self.syllabifier)
        self.dialect_processor = get_dialect_processor(dialect)

    def process_text(self, text: str) -> Dict:
        # Step 1: Tokenization
        tokens = self.tokenize(text)

        # Step 2: Word processing
        processed_words = []
        for token in tokens:
            if token["type"] == "arabic_word":
                syllables = self.ipa_mapper.map_word(token["content"])
                processed_words.append({
                    "original": token["content"],
                    "syllables": syllables,
                    "type": "arabic_word"
                })
            else:
                processed_words.append(token)

        # Step 3: Apply dialect-specific rules
        output = self.dialect_processor.apply_special_rules(processed_words)

        return {
            "dialect": self.dialect,
            "words": output
        }

    def tokenize(self, text: str) -> List[Dict]:
        # Implementation from previous refactoring
        pass