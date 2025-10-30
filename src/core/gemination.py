"""
Gemination Processor for Arabic TTS
Detects and processes shadda (ّ) markers for consonant gemination (doubling)

Gemination Rules:
- Shadda (ّ) marks that a consonant should be pronounced with double length
- In IPA, gemination is marked with [:] after the consonant
- Example: مُدَرِّس (mudarris - teacher) → [mudarːis]
- Gemination is the FIRST phonological rule to apply (highest priority)
"""
from typing import List, Dict


class GeminationProcessor:
    """
    Processes gemination (consonant doubling) marked by shadda (ّ)
    
    This is the first phonological rule in the processing pipeline.
    Must be applied before sun letter assimilation, allophones, and emphatic spread.
    """
    
    def __init__(self, dialect: str):
        """
        Initialize gemination processor
        
        Args:
            dialect: Arabic dialect code (e.g., "EG" for Egyptian Arabic)
        """
        self.dialect = dialect
        self.shadda = 'ّ'  # Gemination marker
    
    def process(self, syllables: List[Dict]) -> List[Dict]:
        """
        Process syllables to detect and mark gemination
        
        Args:
            syllables: List of syllable dictionaries with structure:
                {
                    "syllable": "مَدْ",
                    "pattern": "CVC",
                    "ipa": "...",
                    "chars": [...]
                }
        
        Returns:
            List of syllable dictionaries with gemination markers added to IPA
        """
        processed = []
        
        for syllable in syllables:
            # Get syllable characters
            syllable_text = syllable.get("syllable", "")
            
            # Check if shadda is present
            if self.shadda in syllable_text:
                # Mark as geminated
                syllable["has_gemination"] = True
                syllable["gemination_marker"] = self.shadda
                
                # Find the consonant that is geminated
                geminated_consonant = self._find_geminated_consonant(syllable_text)
                if geminated_consonant:
                    syllable["geminated_consonant"] = geminated_consonant
            else:
                syllable["has_gemination"] = False
            
            processed.append(syllable)
        
        return processed
    
    def _find_geminated_consonant(self, syllable_text: str) -> str:
        """
        Find the consonant that has shadda marker
        
        Args:
            syllable_text: Arabic text of syllable
        
        Returns:
            The consonant character that is geminated, or empty string if not found
        """
        # Shadda appears after the consonant it modifies
        # But there may be diacritics between consonant and shadda
        # Pattern: consonant + (optional diacritics) + shadda
        
        diacritics = {'َ', 'ُ', 'ِ', 'ْ', 'ً', 'ٌ', 'ٍ', 'ٓ'}
        
        for i, char in enumerate(syllable_text):
            if char == self.shadda:
                # Look backward to find the consonant
                j = i - 1
                while j >= 0:
                    if syllable_text[j] not in diacritics and syllable_text[j] != self.shadda:
                        # Found the consonant
                        return syllable_text[j]
                    j -= 1
        
        return ""
    
    def mark_ipa_gemination(self, ipa: str, geminated_consonant: str) -> str:
        """
        Add gemination marker [:] to IPA transcription
        
        Args:
            ipa: Current IPA transcription
            geminated_consonant: Arabic consonant that is geminated
        
        Returns:
            IPA with [:] marker added after the geminated consonant
        
        Example:
            Input: "mudarris" with geminated 'ر'
            Output: "mudarːis" (adds : after r)
        """
        # This will be enhanced when we integrate with IPA mapper
        # For now, just mark that gemination should be applied
        return ipa
    
    def detect_gemination(self, word: str) -> List[int]:
        """
        Detect positions of gemination markers in a word
        
        Args:
            word: Arabic text
        
        Returns:
            List of character positions where shadda appears
        """
        positions = []
        for i, char in enumerate(word):
            if char == self.shadda:
                positions.append(i)
        
        return positions


if __name__ == "__main__":
    # Quick test
    processor = GeminationProcessor("EG")
    
    test_syllable = {
        "syllable": "مُدَرِّس",
        "pattern": "CVCC",
        "ipa": "mudarris"
    }
    
    result = processor.process([test_syllable])
    print(f"Test syllable: {test_syllable['syllable']}")
    print(f"Has gemination: {result[0].get('has_gemination')}")
    print(f"Geminated consonant: {result[0].get('geminated_consonant')}")
