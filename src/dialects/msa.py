from typing import List, Dict
from .base_dialect import BaseDialectProcessor


class MSAProcessor(BaseDialectProcessor):
    def __init__(self):
        super().__init__("MSA")

    def apply_special_rules(self, ipa_output: List[Dict]) -> List[Dict]:
        """Apply MSA-specific phonological rules"""
        for word in ipa_output:
            for i, syllable in enumerate(word["syllables"]):
                # Example: Final devoicing rule
                if syllable["position"] == "final":
                    if syllable["ipa"].endswith(('b', 'd', 'g')):
                        syllable["ipa"] = syllable["ipa"][:-1] + \
                                          {'b': 'p', 'd': 't', 'g': 'k'}[syllable["ipa"][-1]]
        return ipa_output