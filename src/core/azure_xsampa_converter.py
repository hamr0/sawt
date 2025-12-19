"""
Azure-compatible X-SAMPA Converter

This module provides X-SAMPA conversion compatible with Azure Speech Service.
Azure supports a simplified X-SAMPA notation without underscore modifiers
or backslash notations.
"""


class AzureXSAMPAConverter:
    """
    Convert IPA to Azure-compatible X-SAMPA notation

    Azure limitations:
    - No underscore modifiers (_?)
    - No backslash notations (X\, ?\)
    - Simpler phoneme set
    """

    # Azure-compatible IPA to X-SAMPA mappings
    MAPPINGS = {
        # Consonants - Basic
        'b': 'b',
        't': 't',
        'tˁ': 't',      # Emphatic t → plain t (Azure limitation)
        'tˤ': 't',      # Alternative emphatic marker
        'd': 'd',
        'dˁ': 'd',      # Emphatic d → plain d
        'dˤ': 'd',
        'k': 'k',
        'q': 'q',
        'qˁ': 'q',      # Emphatic q → plain q
        'qˤ': 'q',

        # Glottals and Pharyngeals
        'ʔ': '?',       # Glottal stop
        'ħ': 'H',       # Voiceless pharyngeal (CAPITAL H)
        'ʕ': 'Q',       # Voiced pharyngeal (use Q as alternative)
        'h': 'h',

        # Fricatives
        'f': 'f',
        'θ': 'T',       # th as in "think"
        'ð': 'D',       # th as in "this"
        'ðˁ': 'D',      # Emphatic dh → plain D
        'ðˤ': 'D',
        's': 's',
        'sˁ': 's',      # Emphatic s → plain s (Azure limitation)
        'sˤ': 's',
        'z': 'z',
        'ʃ': 'S',       # sh
        'ʒ': 'Z',       # zh
        'x': 'x',       # kh (velar)
        'χ': 'X',       # kh (uvular) - capital X
        'ɣ': 'G',       # gh (velar)
        'ʁ': 'R',       # gh (uvular) - capital R

        # Nasals and Liquids
        'm': 'm',
        'n': 'n',
        'l': 'l',
        'l~': 'l',      # Velarized l
        'lˁ': 'l',      # Emphatic l
        'lˤ': 'l',
        'r': 'r',
        'ɾ': 'r',       # Flap r → plain r (simpler)
        'w': 'w',
        'j': 'j',

        # Vowels - Short
        'a': 'a',
        'ɑ': 'a',       # Back a → plain a (Azure limitation)
        'i': 'i',
        'ɪ': 'i',       # Lowered i → plain i
        'u': 'u',
        'ʊ': 'u',       # Lowered u → plain u
        'e': 'e',
        'ɛ': 'e',
        'o': 'o',
        'ɔ': 'o',
        'ə': '@',       # Schwa

        # Long vowels (multi-character, must be matched first)
        'aː': 'a:',
        'ɑː': 'a:',     # Long back a → long a
        'iː': 'i:',
        'ɪː': 'i:',
        'uː': 'u:',
        'ʊː': 'u:',
        'eː': 'e:',
        'oː': 'o:',

        # Diphthongs
        'aj': 'aj',
        'aw': 'aw',

        # Length marker (standalone)
        'ː': ':',

        # Remove pharyngealization markers (Azure doesn't support them)
        'ˁ': '',        # Remove pharyngealization marker
        'ˤ': '',        # Remove alternative marker

        # Special characters to remove/replace
        '∅': '',        # Null/empty symbol (remove)
        'æ': 'a',       # ash → plain a (Azure doesn't support æ)
    }

    @classmethod
    def convert(cls, ipa: str) -> str:
        """
        Convert IPA to Azure-compatible X-SAMPA

        Args:
            ipa: IPA transcription string

        Returns:
            Azure-compatible X-SAMPA string

        Example:
            >>> AzureXSAMPAConverter.convert("sˁɑbɑːħ")
            'sabaH'
        """
        result = ipa

        # Remove Arabic diacritics that may be mixed in
        arabic_diacritics = [
            '\u064B',  # Fathatan
            '\u064C',  # Dammatan
            '\u064D',  # Kasratan
            '\u064E',  # Fatha
            '\u064F',  # Damma
            '\u0650',  # Kasra
            '\u0651',  # Shadda
            '\u0652',  # Sukun
            '\u0653',  # Maddah
            '\u0654',  # Hamza above
            '\u0655',  # Hamza below
            '\u0670',  # Alif khanjariyah
        ]

        for diacritic in arabic_diacritics:
            result = result.replace(diacritic, '')

        # Remove square brackets (positional markers)
        result = result.replace('[', '').replace(']', '')

        # Sort by length (longest first) to match multi-character sequences
        sorted_mappings = sorted(cls.MAPPINGS.items(), key=lambda x: len(x[0]), reverse=True)

        for ipa_char, xsampa_char in sorted_mappings:
            result = result.replace(ipa_char, xsampa_char)

        return result


# Convenience function
def ipa_to_azure_xsampa(ipa: str) -> str:
    """
    Convert IPA to Azure-compatible X-SAMPA

    This is a convenience wrapper around AzureXSAMPAConverter.convert()

    Args:
        ipa: IPA transcription

    Returns:
        Azure-compatible X-SAMPA
    """
    return AzureXSAMPAConverter.convert(ipa)


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("sˁɑbɑːħ", "صباح - morning"),
        ("ʔakal", "أكل - ate"),
        ("ʃams", "شمس - sun"),
        ("ħamːad", "حمد - praised"),
        ("ʕarabijː", "عربي - Arabic"),
    ]

    print("Azure X-SAMPA Converter Test")
    print("=" * 70)

    for ipa, description in test_cases:
        xsampa = ipa_to_azure_xsampa(ipa)
        print(f"{description}")
        print(f"  IPA:     /{ipa}/")
        print(f"  X-SAMPA: [{xsampa}]")
        print()
