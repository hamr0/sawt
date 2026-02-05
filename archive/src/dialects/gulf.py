from typing import List, Dict
from .base_dialect import BaseDialectProcessor


class GulfProcessor(BaseDialectProcessor):
    def __init__(self):
        super().__init__("Gulf")

    def apply_special_rules(self, ipa_output: List[Dict]) -> List[Dict]:
        """Apply Gulf-specific phonological rules"""
        return ipa_output
