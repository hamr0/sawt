"""
Positional Allophone Processor for Arabic TTS
Handles position-dependent pronunciation variants (allophones)

Allophones are variants of a phoneme that occur in specific positions:
- Initial position (word-initial): Beginning of word
- Medial position (word-medial): Middle of word  
- Final position (word-final): End of word

Example: ء (hamza)
- Initial: [ʔ] - أكل → [ʔakl]
- Medial: ∅ (deleted in casual speech) - سأل → [sal]
- Final: [ʔ] - ماء → [maːʔ]

This is the THIRD phonological rule in the processing pipeline.
Applied after gemination and sun letter assimilation.
"""
import json
from typing import List, Dict, Optional
from pathlib import Path


class AllophoneProcessor:
    """
    Processes positional allophones based on syllable/word position
    
    Loads position-specific IPA from masterTTS.json and applies
    the correct allophone based on where the character appears.
    """
    
    def __init__(self, dialect: str, master_tts_path: Optional[str] = None):
        """
        Initialize allophone processor
        
        Args:
            dialect: Arabic dialect code (e.g., "EG" for Egyptian Arabic)
            master_tts_path: Path to masterTTS.json (optional, uses default if None)
        """
        self.dialect = dialect
        
        # Load masterTTS.json
        if master_tts_path is None:
            project_root = Path(__file__).parent.parent.parent
            master_tts_path = project_root / "data" / "dictionaries" / "masterTTS.json"
        
        with open(master_tts_path, 'r', encoding='utf-8') as f:
            self.master_tts = json.load(f)
        
        # Build position-specific IPA lookup tables
        self._build_allophone_maps()
    
    def _build_allophone_maps(self):
        """
        Build lookup tables for position-specific IPA
        
        Creates maps:
        - char -> {position -> IPA}
        - char -> default_IPA (fallback)
        """
        self.allophone_map = {}  # {char: {position: IPA}}
        self.default_ipa_map = {}  # {char: default_IPA}
        
        # Get dialect-specific entries
        if self.dialect not in self.master_tts:
            raise ValueError(f"Dialect '{self.dialect}' not found in masterTTS.json")
        
        dialect_data = self.master_tts[self.dialect]
        
        for entry in dialect_data:
            char = entry.get("Arabic letter")
            ipa = entry.get("IPA")
            position = entry.get("Position", "default")
            
            if not char or not ipa:
                continue
            
            # Initialize char entry if needed
            if char not in self.allophone_map:
                self.allophone_map[char] = {}
            
            # Store position-specific IPA
            if position == "default":
                self.default_ipa_map[char] = ipa
            else:
                self.allophone_map[char][position] = ipa
    
    def process(self, syllables: List[Dict], word_text: str = "") -> List[Dict]:
        """
        Process syllables to apply position-specific allophones
        
        Args:
            syllables: List of syllable dictionaries
            word_text: Full word text for position detection
        
        Returns:
            List of syllable dictionaries with position-specific IPA applied
        
        Example:
            Input: [{'char': 'ء', 'position': 'initial', ...}]
            Output: [{'char': 'ء', 'position': 'initial', 'ipa': 'ʔ', ...}]
        """
        processed = []
        
        for i, syllable in enumerate(syllables):
            syllable_copy = syllable.copy()
            
            # Determine position
            if i == 0:
                position = "word-initial"
            elif i == len(syllables) - 1:
                position = "word-final"
            else:
                position = "word-medial"
            
            syllable_copy["detected_position"] = position
            
            # Apply position-specific IPA if available
            syllable_text = syllable.get("syllable", "")
            if syllable_text:
                # Get IPA for each character
                self._apply_positional_ipa(syllable_copy, syllable_text, position)
            
            processed.append(syllable_copy)
        
        return processed
    
    def _apply_positional_ipa(self, syllable: Dict, text: str, position: str):
        """
        Apply position-specific IPA to syllable
        
        Args:
            syllable: Syllable dictionary to modify
            text: Arabic text of syllable
            position: Position in word (word-initial/medial/final)
        """
        syllable["allophone_position"] = position
        
        # Check if any characters have position-specific variants
        has_positional = False
        positional_chars = []
        
        # Diacritics to skip
        diacritics = {'َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٓ'}
        
        # Build character-level IPA mapping
        char_ipa_map = {}
        
        for char in text:
            if char in diacritics:
                continue
            
            # Get position-specific IPA
            char_ipa = self.get_ipa_for_char(char, position)
            
            if char_ipa:
                char_ipa_map[char] = char_ipa
                
                # Check if this is different from default
                default_ipa = self.get_ipa_for_char(char, "default")
                if char_ipa != default_ipa and char in self.allophone_map:
                    has_positional = True
                    positional_chars.append(char)
        
        syllable["has_positional_allophone"] = has_positional
        syllable["positional_chars"] = positional_chars
        syllable["char_ipa_map"] = char_ipa_map
    
    def apply_ipa_to_syllables(self, syllables: List[Dict]) -> List[Dict]:
        """
        Apply position-specific IPA to generate full IPA transcription
        
        Args:
            syllables: List of syllable dictionaries with char_ipa_map
        
        Returns:
            Syllables with generated IPA field
        """
        processed = []
        
        for syllable in syllables:
            syllable_copy = syllable.copy()
            
            # Get character IPA map
            char_ipa_map = syllable.get("char_ipa_map", {})
            syllable_text = syllable.get("syllable", "")
            
            if char_ipa_map and syllable_text:
                # Build IPA from character map
                ipa_parts = []
                diacritics = {'َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٓ'}
                
                for char in syllable_text:
                    if char in diacritics:
                        continue  # Skip diacritics in IPA
                    
                    if char in char_ipa_map:
                        char_ipa = char_ipa_map[char]
                        # Skip empty IPA (∅ = deletion)
                        if char_ipa and char_ipa != '∅':
                            # Remove brackets if present
                            char_ipa = char_ipa.replace('[', '').replace(']', '')
                            ipa_parts.append(char_ipa)
                
                syllable_copy["generated_ipa"] = ''.join(ipa_parts)
            
            processed.append(syllable_copy)
        
        return processed
    
    def get_ipa_for_char(self, char: str, position: str) -> str:
        """
        Get position-specific IPA for a character
        
        Args:
            char: Arabic character
            position: Position in word (word-initial/medial/final)
        
        Returns:
            IPA string for the character in given position
        """
        # Check for position-specific IPA
        if char in self.allophone_map:
            if position in self.allophone_map[char]:
                return self.allophone_map[char][position]
        
        # Fall back to default IPA
        if char in self.default_ipa_map:
            return self.default_ipa_map[char]
        
        # No IPA found
        return ""
    
    def has_positional_variant(self, char: str) -> bool:
        """
        Check if character has position-dependent variants
        
        Args:
            char: Arabic character
        
        Returns:
            True if character has allophones, False otherwise
        """
        return char in self.allophone_map and len(self.allophone_map[char]) > 0
    
    def get_positions_for_char(self, char: str) -> List[str]:
        """
        Get all positions where character has specific IPA
        
        Args:
            char: Arabic character
        
        Returns:
            List of positions (e.g., ['word-initial', 'word-final'])
        """
        if char in self.allophone_map:
            return list(self.allophone_map[char].keys())
        return []


if __name__ == "__main__":
    # Quick test
    processor = AllophoneProcessor("EG")
    
    print("Testing Positional Allophone Processor")
    print("=" * 70)
    
    # Test hamza (ء) which has positional variants
    test_char = 'أ'
    print(f"\nCharacter: {test_char}")
    print(f"Has positional variants: {processor.has_positional_variant(test_char)}")
    print(f"Positions: {processor.get_positions_for_char(test_char)}")
    
    positions = ["word-initial", "word-medial", "word-final"]
    for pos in positions:
        ipa = processor.get_ipa_for_char(test_char, pos)
        print(f"  {pos}: /{ipa}/")
    
    # Test with syllables
    print("\n" + "=" * 70)
    print("Testing syllable processing with position-based IPA:")
    
    test_cases = [
        # Word: أكل (ate) - hamza at initial position
        {
            "word": "أكل",
            "syllables": [
                {"syllable": "أَ"},   # Initial - should be [ʔ]
                {"syllable": "كَ"},   # Medial
                {"syllable": "لَ"},   # Final
            ]
        },
        # Word: ماء (water) - hamza at final position
        {
            "word": "ماء",
            "syllables": [
                {"syllable": "مَا"},  # Initial
                {"syllable": "ء"},    # Final - should be [ʔ]
            ]
        }
    ]
    
    for test in test_cases:
        print(f"\nWord: {test['word']}")
        print("-" * 70)
        
        result = processor.process(test['syllables'], test['word'])
        result_with_ipa = processor.apply_ipa_to_syllables(result)
        
        for i, syl in enumerate(result_with_ipa):
            print(f"  Syllable {i+1}: {syl.get('syllable')}")
            print(f"    Position: {syl.get('detected_position')}")
            print(f"    Has positional allophone: {syl.get('has_positional_allophone')}")
            if syl.get('positional_chars'):
                print(f"    Positional chars: {syl.get('positional_chars')}")
            if syl.get('generated_ipa'):
                print(f"    Generated IPA: /{syl.get('generated_ipa')}/")
