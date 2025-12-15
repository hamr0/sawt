from typing import List, Dict
from .base_dialect import BaseDialectProcessor


class LevantineProcessor(BaseDialectProcessor):
    def __init__(self):
        super().__init__("Levantine")

    def apply_special_rules(self, ipa_output: List[Dict]) -> List[Dict]:
        """Apply Levantine-specific phonological rules"""
        return ipa_output
