from .base_dialect import BaseDialectProcessor


class EgyptianProcessor(BaseDialectProcessor):
    def __init__(self):
        super().__init__("EG")

    def apply_special_rules(self, ipa_output: List[Dict]) -> List[Dict]:
        """EG-specific rules like glottal stop deletion"""
        for word in ipa_output:
            if word["type"] != "arabic_word":
                continue

            for syl in word["syllables"]:
                # Medial glottal stop deletion
                if syl["position"] == "medial" and "ʔ" in syl["ipa"]:
                    syl["ipa"] = syl["ipa"].replace("ʔ", "")

                # Final devoicing not applied in EG
        return ipa_output