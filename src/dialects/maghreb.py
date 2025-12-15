from typing import List, Dict
from .base_dialect import BaseDialectProcessor


class MaghrebProcessor(BaseDialectProcessor):
    def __init__(self):
        super().__init__("Maghreb")

    def apply_special_rules(self, ipa_output: List[Dict]) -> List[Dict]:
        """Apply Maghreb-specific phonological rules"""
        return ipa_output
