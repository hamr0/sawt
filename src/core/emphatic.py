"""
Emphatic Spread Processor for Arabic TTS
Handles pharyngealization spread from emphatic consonants to adjacent vowels

Emphatic Consonants (5 in Arabic):
ص /sˁ/, ض /dˁ/, ط /tˁ/, ظ /ðˁ/, ق /q/

Pharyngealization Rule:
- Emphatic consonants cause adjacent vowels to be pharyngealized
- The "emphatic" quality spreads to nearby sounds
- In Egyptian Arabic, this affects vowels within the same syllable
- Marked in IPA with superscript ˁ (pharyngealization marker)

Examples:
- صباح → /sˁɑbɑːħ/ (not /sabɑːħ/)
- ضوء → /dˁɑwʔ/ (not /dɑwʔ/)
- طعام → /tˁɑʕɑːm/ (not /taʕɑːm/)

This is the FOURTH and final phonological rule in the processing pipeline.
Applied after gemination, sun letter assimilation, and positional allophones.
"""
from typing import List, Dict, Set


class EmphaticProcessor:
    """
    Processes emphatic (pharyngealized) consonant effects on adjacent vowels

    Emphatic consonants cause pharyngealization to spread to nearby vowels,
    resulting in a "darker" or "backed" pronunciation quality.

    ARCHITECTURE NOTE: This is a UNIVERSAL component with NO dialect parameter.
    Emphatic consonant detection and pharyngealization spreading is identical
    across all Arabic dialects. Dialect selection happens later in the IPAMapper
    component during final IPA generation.
    """

    def __init__(self):
        """
        Initialize emphatic spread processor

        Note: No dialect parameter needed - emphatic detection is universal
        and independent of dialect selection.
        """
        
        # Define emphatic consonants
        # These are the Arabic letters that trigger pharyngealization
        self.emphatic_consonants = {
            'ص',  # /sˁ/ - emphatic s
            'ض',  # /dˁ/ - emphatic d
            'ط',  # /tˁ/ - emphatic t
            'ظ',  # /ðˁ/ - emphatic dh
            'ق',  # /q/ - uvular stop (also triggers some backing)
        }
        
        # Vowels that can be affected by pharyngealization
        self.vowels = {
            'ا',  # alif
            'و',  # waw
            'ي',  # yaa
            'ى',  # alif maqsura
        }
        
        # Diacritics (short vowels)
        self.diacritics = {
            'َ',  # fatha (a)
            'ُ',  # damma (u)
            'ِ',  # kasra (i)
            'ْ',  # sukun
            'ّ',  # shadda
            'ً',  # tanween fath
            'ٌ',  # tanween damm
            'ٍ',  # tanween kasr
        }
    
    def process(self, syllables: List[Dict]) -> List[Dict]:
        """
        Process syllables to detect and mark emphatic spread
        
        Args:
            syllables: List of syllable dictionaries
        
        Returns:
            List of syllable dictionaries with emphatic spread markers
        
        Rule:
            If syllable contains emphatic consonant,
            mark adjacent vowels as pharyngealized
        """
        processed = []
        
        for syllable in syllables:
            syllable_copy = syllable.copy()
            syllable_text = syllable.get("syllable", "")
            
            # Check if syllable contains emphatic consonant
            has_emphatic = self._contains_emphatic(syllable_text)
            
            if has_emphatic:
                syllable_copy["has_emphatic"] = True
                
                # Find which emphatic consonant
                emphatic_chars = self._find_emphatic_consonants(syllable_text)
                syllable_copy["emphatic_consonants"] = emphatic_chars
                
                # Mark that pharyngealization should be applied
                syllable_copy["pharyngealization_spread"] = True
            else:
                syllable_copy["has_emphatic"] = False
                syllable_copy["pharyngealization_spread"] = False
            
            processed.append(syllable_copy)
        
        return processed
    
    def _contains_emphatic(self, text: str) -> bool:
        """
        Check if text contains emphatic consonant
        
        Args:
            text: Arabic text
        
        Returns:
            True if contains emphatic consonant, False otherwise
        """
        for char in text:
            if char in self.emphatic_consonants:
                return True
        return False
    
    def _find_emphatic_consonants(self, text: str) -> List[str]:
        """
        Find all emphatic consonants in text
        
        Args:
            text: Arabic text
        
        Returns:
            List of emphatic consonant characters
        """
        emphatic_chars = []
        for char in text:
            if char in self.emphatic_consonants:
                emphatic_chars.append(char)
        return emphatic_chars
    
    def apply_pharyngealization(self, syllables: List[Dict]) -> List[Dict]:
        """
        Apply pharyngealization to vowels in syllables with emphatic consonants
        
        Args:
            syllables: List of syllable dictionaries with IPA
        
        Returns:
            Syllables with pharyngealized vowels in IPA
        
        Rule:
            In syllables with emphatic consonants,
            apply pharyngealization (backing) to adjacent vowels
        
        Example:
            صَ /sa/ → /sˁɑ/ (a→ɑ, adds ˁ after emphatic)
        """
        processed = []
        
        for syllable in syllables:
            syllable_copy = syllable.copy()
            
            # Check if syllable has emphatic consonant
            if syllable.get("has_emphatic") and syllable.get("pharyngealization_spread"):
                # Get current IPA
                current_ipa = syllable.get("ipa", syllable.get("generated_ipa", ""))
                
                if current_ipa:
                    # Apply vowel backing
                    modified_ipa = self._apply_vowel_backing(current_ipa)
                    
                    # Add pharyngealization marker to emphatic consonants
                    modified_ipa = self._add_pharyngealization_markers(
                        modified_ipa, 
                        syllable.get("emphatic_consonants", [])
                    )
                    
                    syllable_copy["pharyngealized_ipa"] = modified_ipa
                    syllable_copy["original_ipa_before_emphatic"] = current_ipa
            
            processed.append(syllable_copy)
        
        return processed
    
    def _apply_vowel_backing(self, ipa: str) -> str:
        """
        Apply vowel backing (pharyngealization) to vowels in IPA
        
        Args:
            ipa: IPA string
        
        Returns:
            IPA with backed vowels
        
        Changes:
            a → ɑ (front low → back low)
            i → ɪ (high front → lowered)
            u → ʊ (high back → lowered)
        """
        # Apply vowel backing
        ipa = ipa.replace('aː', 'ɑː')  # Long vowels first
        ipa = ipa.replace('iː', 'ɪː')
        ipa = ipa.replace('uː', 'ʊː')
        ipa = ipa.replace('a', 'ɑ')    # Then short vowels
        ipa = ipa.replace('i', 'ɪ')
        ipa = ipa.replace('u', 'ʊ')
        
        return ipa
    
    def _add_pharyngealization_markers(self, ipa: str, emphatic_chars: List[str]) -> str:
        """
        Add pharyngealization marker (ˁ) after emphatic consonants in IPA
        
        Args:
            ipa: IPA string
            emphatic_chars: List of emphatic consonants in syllable
        
        Returns:
            IPA with ˁ markers after emphatic consonants
        """
        # Map Arabic emphatic consonants to their IPA
        emphatic_ipa_map = {
            'ص': 's',   # /s/ → /sˁ/
            'ض': 'd',   # /d/ → /dˁ/
            'ط': 't',   # /t/ → /tˁ/
            'ظ': 'ð',   # /ð/ → /ðˁ/
            'ق': 'q',   # /q/ (already uvular, optionally add ˁ)
        }
        
        # Add ˁ marker after each emphatic consonant
        for char in emphatic_chars:
            if char in emphatic_ipa_map:
                base_ipa = emphatic_ipa_map[char]
                # Replace base IPA with pharyngealized version
                # Only if not already marked
                if base_ipa in ipa and base_ipa + 'ˁ' not in ipa:
                    ipa = ipa.replace(base_ipa, base_ipa + 'ˁ')
        
        return ipa
    
    def get_pharyngealized_vowel(self, vowel_ipa: str) -> str:
        """
        Get pharyngealized version of vowel IPA
        
        Args:
            vowel_ipa: IPA of vowel
        
        Returns:
            Pharyngealized version of vowel
        
        Examples:
            /a/ → /ɑ/ (backed)
            /i/ → /ɪ/ (lowered/backed)
            /u/ → /ʊ/ (lowered/backed)
        """
        # Map vowels to pharyngealized variants
        pharyngealized_map = {
            'a': 'ɑ',   # front low → back low
            'i': 'ɪ',   # high front → lowered
            'u': 'ʊ',   # high back → lowered
            'aː': 'ɑː',
            'iː': 'ɪː',
            'uː': 'ʊː',
        }
        
        return pharyngealized_map.get(vowel_ipa, vowel_ipa)
    
    def is_emphatic_consonant(self, char: str) -> bool:
        """
        Check if character is emphatic consonant
        
        Args:
            char: Arabic character
        
        Returns:
            True if emphatic, False otherwise
        """
        return char in self.emphatic_consonants
    
    def detect_emphatic_words(self, word: str) -> bool:
        """
        Detect if word contains any emphatic consonants
        
        Args:
            word: Arabic word
        
        Returns:
            True if word has emphatic consonants, False otherwise
        """
        return self._contains_emphatic(word)


if __name__ == "__main__":
    # Quick test
    processor = EmphaticProcessor()
    
    print("Testing Emphatic Spread Processor")
    print("=" * 70)
    
    # Test emphatic consonant detection
    print("\nEmphatic consonants:")
    for char in processor.emphatic_consonants:
        print(f"  {char} - is emphatic: {processor.is_emphatic_consonant(char)}")
    
    # Test words with emphatic consonants
    print("\n" + "=" * 70)
    print("Testing words:")
    
    test_words = [
        ("صباح", "sabaah", "morning - has ص"),
        ("ضوء", "daw'", "light - has ض"),
        ("طعام", "ta'aam", "food - has ط"),
        ("ظل", "dhil", "shadow - has ظ"),
        ("قمر", "qamar", "moon - has ق"),
        ("كتاب", "kitaab", "book - no emphatic"),
    ]
    
    for word, transliteration, description in test_words:
        has_emphatic = processor.detect_emphatic_words(word)
        print(f"\n{word} ({transliteration}) - {description}")
        print(f"  Has emphatic: {has_emphatic}")
    
    # Test syllable processing
    print("\n" + "=" * 70)
    print("Testing syllable processing with pharyngealization spread:")
    
    test_cases = [
        # صباح (morning) - emphatic ص
        {
            "word": "صباح",
            "syllables": [
                {"syllable": "صَ", "ipa": "sa"},
                {"syllable": "بَاح", "ipa": "baːħ"},
            ]
        },
        # طعام (food) - emphatic ط
        {
            "word": "طعام",
            "syllables": [
                {"syllable": "طَ", "ipa": "ta"},
                {"syllable": "عَام", "ipa": "ʕaːm"},
            ]
        },
        # كتاب (book) - no emphatic
        {
            "word": "كتاب",
            "syllables": [
                {"syllable": "كِ", "ipa": "ki"},
                {"syllable": "تَاب", "ipa": "taːb"},
            ]
        }
    ]
    
    for test in test_cases:
        print(f"\nWord: {test['word']}")
        print("-" * 70)
        
        # Process to detect emphatic
        detected = processor.process(test['syllables'])
        
        # Apply pharyngealization
        result = processor.apply_pharyngealization(detected)
        
        for i, syl in enumerate(result):
            print(f"  Syllable {i+1}: {syl.get('syllable')}")
            print(f"    Has emphatic: {syl.get('has_emphatic')}")
            if syl.get('emphatic_consonants'):
                print(f"    Emphatic consonants: {syl.get('emphatic_consonants')}")
            
            # Show IPA transformation
            original_ipa = syl.get('original_ipa_before_emphatic')
            pharyngealized_ipa = syl.get('pharyngealized_ipa')
            
            if original_ipa and pharyngealized_ipa:
                print(f"    IPA transformation: /{original_ipa}/ → /{pharyngealized_ipa}/")
    
    # Test pharyngealized vowel conversion
    print("\n" + "=" * 70)
    print("Testing pharyngealized vowel conversion:")
    
    test_vowels = ['a', 'i', 'u', 'aː', 'iː', 'uː']
    for vowel in test_vowels:
        pharyngealized = processor.get_pharyngealized_vowel(vowel)
        print(f"  /{vowel}/ → /{pharyngealized}/")
