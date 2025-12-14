"""
Sun Letter Assimilation Processor for Arabic TTS
Handles definite article ال (al-) assimilation with sun letters

Sun Letter Rule:
- In Arabic, the definite article ال (al-) assimilates with "sun letters"
- The ل (lam) is deleted and the sun letter is geminated (doubled)
- Example: الشمس /alʃams/ → [aʃːams] (not [alʃams])

Sun Letters (14 total):
ت، ث، د، ذ، ر، ز، س، ش، ص، ض، ط، ظ، ل، ن

Moon Letters (remaining 14 letters):
The ل is NOT assimilated, pronounced as /al/
Example: القمر /alqamar/ → [alqamar] (ل is pronounced)

This is the SECOND phonological rule in the processing pipeline.
Applied after gemination, before positional allophones and emphatic spread.
"""
from typing import List, Dict


class SunLetterProcessor:
    """
    Processes sun letter assimilation in Arabic definite article ال (al-)

    ARCHITECTURE NOTE: This is a UNIVERSAL component with NO dialect parameter.
    Sun letter assimilation detection is identical across all Arabic dialects.
    Dialect selection happens later in the IPAMapper component.

    Sun letter assimilation is a critical phonological rule in Arabic where
    the /l/ sound of the definite article assimilates with the following
    consonant if it's a "sun letter", causing gemination.
    """

    def __init__(self):
        """
        Initialize sun letter processor

        Note: No dialect parameter needed - sun letter detection is universal
        and independent of dialect selection.
        """
        
        # Define sun letters (14 consonants)
        self.sun_letters = {
            'ت', 'ث', 'د', 'ذ',  # Dental/alveolar
            'ر', 'ز',            # Alveolar
            'س', 'ش',            # Sibilants
            'ص', 'ض', 'ط', 'ظ',  # Emphatic
            'ل', 'ن'             # Lateral, nasal
        }
        
        # Define moon letters (remaining 14 letters) - for reference
        self.moon_letters = {
            'ء', 'ب', 'ج', 'ح', 'خ',
            'ع', 'غ', 'ف', 'ق',
            'ك', 'م', 'ه', 'و', 'ي'
        }
        
        # Definite article patterns
        self.definite_article = 'ال'
        self.alif = 'ا'
        self.lam = 'ل'
    
    def process(self, syllables: List[Dict]) -> List[Dict]:
        """
        Process syllables to detect and apply sun letter assimilation
        
        Args:
            syllables: List of syllable dictionaries
        
        Returns:
            List of syllable dictionaries with sun letter assimilation applied
        
        Rule:
            If pattern is: ال + sun_letter
            Then: Remove ل sound, geminate sun letter
            Example: الشمس → اش + شمس (with shadda on ش)
        """
        processed = []
        
        for i, syllable in enumerate(syllables):
            syllable_text = syllable.get("syllable", "")
            
            # Check if this syllable contains definite article ال
            if self._contains_definite_article(syllable_text):
                # Look ahead to next syllable to check for sun letter
                if i + 1 < len(syllables):
                    next_syllable_text = syllables[i + 1].get("syllable", "")
                    
                    # Get first consonant of next syllable
                    first_consonant = self._get_first_consonant(next_syllable_text)
                    
                    if first_consonant in self.sun_letters:
                        # Apply sun letter assimilation
                        syllable["sun_letter_assimilation"] = True
                        syllable["assimilated_sun_letter"] = first_consonant
                        syllable["rule_applied"] = "lam_deleted_sun_geminated"
                    else:
                        # Moon letter - no assimilation
                        syllable["sun_letter_assimilation"] = False
                        syllable["moon_letter"] = first_consonant
                else:
                    syllable["sun_letter_assimilation"] = False
            else:
                syllable["sun_letter_assimilation"] = False
            
            processed.append(syllable)
        
        return processed
    
    def _contains_definite_article(self, text: str) -> bool:
        """
        Check if syllable contains definite article ال
        
        Args:
            text: Arabic syllable text
        
        Returns:
            True if contains ال, False otherwise
        """
        return self.definite_article in text or (self.alif in text and self.lam in text)
    
    def _get_first_consonant(self, text: str) -> str:
        """
        Get the first consonant in syllable (skipping diacritics)
        
        Args:
            text: Arabic syllable text
        
        Returns:
            First consonant character, or empty string if not found
        """
        diacritics = {'َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٓ'}
        
        for char in text:
            if char not in diacritics:
                return char
        
        return ""
    
    def detect_sun_letter_pattern(self, word: str) -> bool:
        """
        Detect if word has ال + sun_letter pattern
        
        Args:
            word: Full Arabic word
        
        Returns:
            True if word starts with ال followed by sun letter
        """
        # Check if word starts with definite article
        if not word.startswith(self.definite_article):
            return False
        
        # Get the character after ال (position 2)
        if len(word) > 2:
            # Skip diacritics to find actual consonant
            diacritics = {'َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٓ'}
            for i in range(2, len(word)):
                if word[i] not in diacritics:
                    return word[i] in self.sun_letters
        
        return False
    
    def is_sun_letter(self, letter: str) -> bool:
        """
        Check if a letter is a sun letter
        
        Args:
            letter: Arabic character
        
        Returns:
            True if sun letter, False otherwise
        """
        return letter in self.sun_letters
    
    def is_moon_letter(self, letter: str) -> bool:
        """
        Check if a letter is a moon letter
        
        Args:
            letter: Arabic character
        
        Returns:
            True if moon letter, False otherwise
        """
        return letter in self.moon_letters
    
    def apply_assimilation(self, syllables: List[Dict], arabic_text: str) -> List[Dict]:
        """
        Apply sun letter assimilation to syllables with IPA modification
        
        Rule: ال + sun_letter → /a/ + geminated_sun_letter
        - Remove the /l/ sound from IPA
        - Add gemination marker [:] to sun letter
        
        Args:
            syllables: List of syllable dictionaries with IPA
            arabic_text: Original Arabic text for reference
        
        Returns:
            Modified syllables with assimilation applied to IPA
        
        Example:
            Input: الشمس → [{'ipa': 'al', ...}, {'ipa': 'ʃams', ...}]
            Output: [{'ipa': 'a', ...}, {'ipa': 'ʃːams', ...}]
        """
        processed = syllables.copy()
        
        for i in range(len(processed)):
            syllable = processed[i]
            
            # Check if this syllable has sun letter assimilation marked
            if syllable.get("sun_letter_assimilation"):
                sun_letter = syllable.get("assimilated_sun_letter")
                
                if sun_letter and i + 1 < len(processed):
                    # Modify current syllable: remove /l/ from IPA
                    current_ipa = syllable.get("ipa", "")
                    if 'l' in current_ipa:
                        # Remove /l/ sound, keep only /a/
                        modified_ipa = current_ipa.replace('l', '')
                        syllable["ipa"] = modified_ipa
                        syllable["original_ipa"] = current_ipa
                    
                    # Modify next syllable: add gemination to sun letter
                    next_syllable = processed[i + 1]
                    next_ipa = next_syllable.get("ipa", "")
                    
                    # Add gemination marker [:] after the sun letter
                    # This will be handled by IPA mapper, but we mark it here
                    next_syllable["has_sun_gemination"] = True
                    next_syllable["geminated_by_sun_rule"] = sun_letter
        
        return processed
    
    def modify_ipa_for_sun_letter(self, ipa: str, sun_letter_char: str, 
                                   consonant_to_ipa_map: Dict[str, str]) -> str:
        """
        Modify IPA string to apply sun letter assimilation
        
        Args:
            ipa: Current IPA transcription
            sun_letter_char: The Arabic sun letter character
            consonant_to_ipa_map: Mapping from Arabic consonant to IPA
        
        Returns:
            Modified IPA with gemination marker
        
        Example:
            Input: "ʃams", sun_letter='ش', map={'ش': 'ʃ'}
            Output: "ʃːams" (adds : for gemination)
        """
        if sun_letter_char in consonant_to_ipa_map:
            sun_ipa = consonant_to_ipa_map[sun_letter_char]
            
            # If IPA starts with the sun letter sound, add gemination marker
            if ipa.startswith(sun_ipa):
                return sun_ipa + 'ː' + ipa[len(sun_ipa):]
        
        return ipa


if __name__ == "__main__":
    # Quick test
    processor = SunLetterProcessor()
    
    test_words = [
        ("الشمس", "ash-shams", "the sun - sun letter ش"),
        ("الدرس", "ad-dars", "the lesson - sun letter د"),
        ("الرجل", "ar-rajul", "the man - sun letter ر"),
        ("القمر", "al-qamar", "the moon - moon letter ق"),
        ("الكتاب", "al-kitaab", "the book - moon letter ك"),
    ]
    
    print("Testing Sun Letter Processor:")
    print("=" * 70)
    
    for word, expected, description in test_words:
        has_sun = processor.detect_sun_letter_pattern(word)
        first_letter = processor._get_first_consonant(word[2:]) if len(word) > 2 else ""
        letter_type = "SUN" if first_letter in processor.sun_letters else "MOON"
        
        print(f"Word: {word} ({expected})")
        print(f"  {description}")
        print(f"  First letter after ال: {first_letter} ({letter_type})")
        print(f"  Has sun letter pattern: {has_sun}")
        print()
