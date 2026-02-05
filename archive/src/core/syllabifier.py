import json
from typing import List, Dict


class ArabicSyllabifier:
    def __init__(self, dialect: str):
        self.dialect = dialect
        
        # Fixed: Separate vowels, diacritics, and long vowel markers
        self.short_vowels = {'َ', 'ُ', 'ِ'}  # fatha, damma, kasra
        self.long_vowel_markers = {'ا', 'و', 'ي'}  # alif, waw, yaa
        self.sukun = 'ْ'  # marks no vowel (coda consonant)
        self.shadda = 'ّ'  # gemination marker
        self.diacritics = {'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٓ'}  # all diacritical marks
        self.tanween = {'ً', 'ٌ', 'ٍ'}  # nunation marks
        
        # Combined set for quick checks
        self.all_vowels = self.short_vowels | self.long_vowel_markers
        
        self.load_resources()

    def load_resources(self):
        with open('data/dictionaries/masterTTS.json', 'r', encoding='utf-8') as f:
            self.master_data = json.load(f)
        with open('data/dictionaries/syllable_patterns.json', 'r', encoding='utf-8') as f:
            patterns_data = json.load(f)
            self.patterns = patterns_data["dialects"][self.dialect]["patterns"]

    def segment(self, word: str) -> List[List[str]]:
        """
        Improved syllable segmentation using onset-nucleus-coda analysis.

        Fixed Rules (v2):
        - Each syllable: onset (C) + nucleus (V) + optional coda (C)
        - Sukun (ْ) marks that PREVIOUS consonant is in coda (has no vowel)
        - Shadda (ّ) doubles previous consonant: one in coda, one in next onset
        - Long vowels: short_vowel + matching long_marker (َا, ُو, ِي)
        - Diphthongs: َيْ (ay), َوْ (aw)
        - Special handling: definite article ال is kept together as CV syllable
        """
        # Special handling for definite article at word beginning
        syllables = []
        i = 0

        # Check if word starts with definite article ال (alef + lam)
        if len(word) >= 2 and word[0] == 'ا' and word[1] == 'ل':
            # Keep ال together as first syllable (CV pattern)
            syllables.append(['ا', 'ل'])
            i = 2

        while i < len(word):
            current_syl = []
            
            # Step 1: Collect onset (initial consonant(s))
            # Skip leading diacritics
            while i < len(word) and word[i] in self.diacritics and word[i] not in {self.sukun, self.shadda}:
                i += 1
            
            # Get consonant(s) for onset
            while i < len(word) and not self._is_vowel(word[i]) and word[i] not in self.diacritics:
                current_syl.append(word[i])
                i += 1
            
            # Handle shadda after onset consonant (gemination)
            if i < len(word) and word[i] == self.shadda:
                current_syl.append(word[i])
                i += 1
            
            # Step 2: Get nucleus (vowel - short or long)
            if i < len(word) and self._is_vowel(word[i]):
                current_syl.append(word[i])
                i += 1
                
                # Check for long vowel: short_vowel + long_marker
                if i < len(word) and word[i] in self.long_vowel_markers:
                    # Determine if this is a long vowel or consonant
                    # Long vowel rules: fatha+alif, kasra+yaa, damma+waw
                    prev_vowel = current_syl[-1]
                    long_marker = word[i]
                    
                    is_long_vowel = False
                    if prev_vowel == 'َ' and long_marker == 'ا':  # fatha + alif = aa
                        is_long_vowel = True
                    elif prev_vowel == 'ِ' and long_marker == 'ي':  # kasra + yaa = ii
                        is_long_vowel = True
                    elif prev_vowel == 'ُ' and long_marker == 'و':  # damma + waw = uu
                        is_long_vowel = True
                    
                    if is_long_vowel:
                        current_syl.append(word[i])
                        i += 1
                        
                        # Check for diphthong pattern: long_marker + sukun + consonant
                        if i < len(word) and word[i] == self.sukun:
                            current_syl.append(word[i])
                            i += 1
                            # Coda consonant after sukun
                            if i < len(word) and not self._is_vowel(word[i]) and word[i] not in self.diacritics:
                                current_syl.append(word[i])
                                i += 1
            
            # Step 3: Get coda (consonants after the nucleus)
            # The coda can be:
            # - A consonant followed by sukun (marks no vowel on that C)
            # - A consonant at end of word
            # - A consonant before another consonant
            
            # Look ahead for consonant(s) that belong to this syllable's coda
            while i < len(word):
                # Case 1: Consonant followed by sukun (CVC pattern)
                if not self._is_vowel(word[i]) and word[i] not in self.diacritics:
                    # Check if followed by sukun
                    if i + 1 < len(word) and word[i + 1] == self.sukun:
                        # This consonant + sukun are coda
                        current_syl.append(word[i])
                        current_syl.append(word[i + 1])
                        i += 2
                        
                        # Check for CVCC: another consonant after sukun
                        if i < len(word) and not self._is_vowel(word[i]) and word[i] not in self.diacritics:
                            # Check if this second consonant also has sukun or is word-final
                            if i + 1 >= len(word) or word[i + 1] == self.sukun:
                                current_syl.append(word[i])
                                i += 1
                                if i < len(word) and word[i] == self.sukun:
                                    current_syl.append(word[i])
                                    i += 1
                        break
                    
                    # Case 2: Consonant followed by vowel (starts next syllable)
                    elif i + 1 < len(word) and self._is_vowel(word[i + 1]):
                        # Don't include, it's next syllable's onset
                        break
                    
                    # Case 3: Consonant at end of word
                    elif i + 1 >= len(word):
                        current_syl.append(word[i])
                        i += 1
                        break
                    
                    # Case 4: Consonant followed by another consonant (coda)
                    else:
                        current_syl.append(word[i])
                        i += 1
                        # Don't continue - next consonant starts new syllable
                        break
                
                # Skip standalone sukun (shouldn't happen but handle it)
                elif word[i] == self.sukun:
                    current_syl.append(word[i])
                    i += 1
                
                # Skip other diacritics
                elif word[i] in self.diacritics:
                    current_syl.append(word[i])
                    i += 1
                
                else:
                    break
            
            if current_syl:
                syllables.append(current_syl)
        
        return syllables
    
    def _is_vowel(self, char: str) -> bool:
        """Check if character is a vowel (short vowel diacritic)"""
        return char in self.short_vowels

    def classify_pattern(self, syllable: List[str]) -> str:
        """
        Classify syllable pattern based on C/V structure.
        
        Improved to handle:
        - Short vowels (َ ُ ِ) as V
        - Long vowel markers (ا و ي) as V when following short vowel
        - Sukun (ْ) as marker (not counted in pattern)
        - Shadda (ّ) as marker for gemination (adds extra C)
        - All other Arabic letters as C
        """
        pattern = []
        has_gemination = False
        
        for i, char in enumerate(syllable):
            # Short vowels are V
            if char in self.short_vowels:
                pattern.append('V')
            
            # Long vowel markers (ا و ي) after a vowel count as V
            elif char in self.long_vowel_markers:
                # Check if previous element was a vowel
                if pattern and pattern[-1] == 'V':
                    pattern.append('V')
                else:
                    # At word start or after consonant, treat as consonant (rare)
                    pattern.append('C')
            
            # Sukun doesn't add to pattern, it's just a marker
            elif char == self.sukun:
                continue
            
            # Shadda marks gemination - adds virtual consonant
            elif char == self.shadda:
                has_gemination = True
                # Add extra C for the doubled consonant
                if pattern and pattern[-1] == 'C':
                    pattern.append('C')
                continue
            
            # Other diacritics (tanween) don't affect pattern
            elif char in self.diacritics:
                continue
            
            # Everything else is a consonant
            else:
                pattern.append('C')
        
        pattern_str = ''.join(pattern)
        
        # Pattern matching (order matters - longest first)
        if pattern_str == 'CVVC':
            return 'CVVC'
        elif pattern_str == 'CVCC':
            if self.validate_cvcc(syllable):
                return 'CVCC'
            return 'CVC'  # Downgrade if invalid
        elif pattern_str == 'CVV':
            return 'CVV'
        elif pattern_str == 'CVC':
            return 'CVC'
        elif pattern_str == 'CV':
            return 'CV'
        
        # Additional patterns that may occur
        elif pattern_str == 'V':
            return 'V'  # Vowel-only (rare, word-initial alif)
        elif pattern_str == 'VC':
            return 'VC'  # Vowel + consonant
        elif pattern_str == 'CCV':
            return 'CCV'  # Double consonant + vowel (rare)
        elif pattern_str == 'CC':
            return 'CC'  # Consonant cluster (error case)
        elif pattern_str == 'C':
            return 'C'  # Single consonant (error case)
        
        # If pattern doesn't match any known pattern
        return f'UNKNOWN({pattern_str})'

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