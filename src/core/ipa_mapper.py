class IPAMapper:
    def __init__(self, syllabifier):
        self.syllabifier = syllabifier

    def map_word(self, word: str) -> List[Dict]:
        syllables = self.syllabifier.segment(word)
        result = []

        for syl in syllables:
            pattern = self.syllabifier.classify_pattern(syl)
            ipa = self.get_ipa_for_syllable(syl, pattern)
            result.append({
                "syllable": ''.join(syl),
                "pattern": pattern,
                "ipa": ipa
            })
        return result

    def get_ipa_for_syllable(self, syllable: List[str], pattern: str) -> str:
        ipa_parts = []
        for char in syllable:
            # Lookup in masterTTS data
            char_data = next(
                (item for item in self.syllabifier.master_data[self.syllabifier.dialect]
                 if item["Arabic letter"] == char),
                None
            )

            if char_data:
                # Check for pattern-specific adjustment
                syllable_info = char_data.get("Syllable_Position", {})
                if pattern in syllable_info:
                    ipa_parts.append(syllable_info[pattern]["ipa_adjustment"])
                else:
                    ipa_parts.append(char_data["IPA"])
            else:
                ipa_parts.append(char)  # Fallback

        return ''.join(ipa_parts)