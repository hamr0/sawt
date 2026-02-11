#!/usr/bin/env python3
"""
Character Voice Assignment for Azure TTS Multi-Voice Audiobooks

Automatically analyzes Arabic text and assigns different Azure voices to:
- Narrator (main voice)
- Different characters in dialogue
- Gender-appropriate voices

Supports dialogue detection patterns:
- Quote marks: "..." or «...»
- Dialogue verbs: قال، قالت، صرخ، همس، etc.
- Character names
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


@dataclass
class Character:
    """Represents a character in the text"""
    name: str
    gender: Gender
    voice_id: str
    dialogue_count: int = 0

    def __hash__(self):
        return hash(self.name)


@dataclass
class TextSegment:
    """Represents a segment of text with voice assignment"""
    text: str
    segment_type: str  # 'narration', 'dialogue', 'quote'
    character: Optional[Character] = None
    voice_id: Optional[str] = None


class AzureVoicePool:
    """Available Azure Arabic neural voices"""

    # Egyptian Arabic voices
    EGYPTIAN_FEMALE = "ar-EG-SalmaNeural"
    EGYPTIAN_MALE = "ar-EG-ShakirNeural"

    # Saudi/MSA voices
    SAUDI_FEMALE = "ar-SA-ZariyahNeural"
    SAUDI_MALE = "ar-SA-HamedNeural"

    # Gulf/UAE voices
    UAE_FEMALE = "ar-AE-FatimaNeural"
    UAE_MALE = "ar-AE-HamdanNeural"

    # Levantine/Syria voices
    SYRIA_FEMALE = "ar-SY-AmanyNeural"
    SYRIA_MALE = "ar-SY-LaithNeural"

    # Jordan voices
    JORDAN_FEMALE = "ar-JO-SanaNeural"
    JORDAN_MALE = "ar-JO-TaimNeural"

    # Lebanon voices
    LEBANON_FEMALE = "ar-LB-LaylaNeural"
    LEBANON_MALE = "ar-LB-RamiNeural"

    # Morocco voices
    MOROCCO_FEMALE = "ar-MA-MounaNeural"
    MOROCCO_MALE = "ar-MA-JamalNeural"

    @classmethod
    def get_voice(cls, dialect: str, gender: Gender) -> str:
        """Get appropriate voice for dialect and gender"""
        dialect_map = {
            'EG': (cls.EGYPTIAN_FEMALE, cls.EGYPTIAN_MALE),
            'MSA': (cls.SAUDI_FEMALE, cls.SAUDI_MALE),
            'SA': (cls.SAUDI_FEMALE, cls.SAUDI_MALE),
            'Gulf': (cls.UAE_FEMALE, cls.UAE_MALE),
            'AE': (cls.UAE_FEMALE, cls.UAE_MALE),
            'Levantine': (cls.SYRIA_FEMALE, cls.SYRIA_MALE),
            'SY': (cls.SYRIA_FEMALE, cls.SYRIA_MALE),
            'JO': (cls.JORDAN_FEMALE, cls.JORDAN_MALE),
            'LB': (cls.LEBANON_FEMALE, cls.LEBANON_MALE),
            'MA': (cls.MOROCCO_FEMALE, cls.MOROCCO_MALE),
        }

        voices = dialect_map.get(dialect, (cls.EGYPTIAN_FEMALE, cls.EGYPTIAN_MALE))

        if gender == Gender.FEMALE:
            return voices[0]
        elif gender == Gender.MALE:
            return voices[1]
        else:
            return voices[0]  # Default to female for unknown

    @classmethod
    def get_narrator_voice(cls, dialect: str) -> str:
        """Get default narrator voice (female, warm)"""
        return cls.get_voice(dialect, Gender.FEMALE)

    @classmethod
    def get_unique_voices(cls, dialect: str, count: int) -> List[str]:
        """Get list of unique voices for multiple characters"""
        all_voices = [
            cls.EGYPTIAN_FEMALE, cls.EGYPTIAN_MALE,
            cls.SAUDI_FEMALE, cls.SAUDI_MALE,
            cls.UAE_FEMALE, cls.UAE_MALE,
            cls.SYRIA_FEMALE, cls.SYRIA_MALE,
            cls.JORDAN_FEMALE, cls.JORDAN_MALE,
            cls.LEBANON_FEMALE, cls.LEBANON_MALE,
            cls.MOROCCO_FEMALE, cls.MOROCCO_MALE,
        ]

        # Prioritize dialect-matching voices first
        primary = cls.get_voice(dialect, Gender.FEMALE)
        secondary = cls.get_voice(dialect, Gender.MALE)

        result = [primary, secondary]

        # Add other voices if more needed
        for voice in all_voices:
            if voice not in result and len(result) < count:
                result.append(voice)

        return result[:count]


class CharacterVoiceAssigner:
    """
    Analyzes Arabic text and assigns Azure voices to characters

    Detection Strategies:
    1. Dialogue Verbs - قال، قالت، صرخ، همس
    2. Quote Marks - "..." or «...»
    3. Character Names - أحمد، فاطمة، etc.
    4. Gender Markers - ـة، ـت، masculine/feminine patterns
    """

    # Common dialogue verbs in Arabic
    DIALOGUE_VERBS = [
        'قال', 'قالت', 'قالوا', 'قلت', 'قلنا',  # said
        'صرخ', 'صرخت', 'صرخوا',  # shouted
        'همس', 'همست', 'همسوا',  # whispered
        'أجاب', 'أجابت', 'أجابوا',  # answered
        'سأل', 'سألت', 'سألوا',  # asked
        'رد', 'ردت', 'ردوا',  # replied
        'نادى', 'نادت', 'نادوا',  # called
        'أكمل', 'أكملت', 'أكملوا',  # continued
        'تابع', 'تابعت', 'تابعوا',  # continued
    ]

    # Common female name patterns
    FEMALE_MARKERS = ['ة', 'ـة']  # Ta marbuta
    FEMALE_NAMES = ['فاطمة', 'عائشة', 'خديجة', 'مريم', 'سارة', 'ليلى', 'زينب', 'رقية']

    # Common male names
    MALE_NAMES = ['محمد', 'أحمد', 'علي', 'حسن', 'حسين', 'عمر', 'خالد', 'يوسف', 'إبراهيم']

    def __init__(self, dialect: str = 'EG', narrator_gender: Gender = Gender.FEMALE):
        self.dialect = dialect
        self.narrator_gender = narrator_gender
        self.narrator_voice = AzureVoicePool.get_narrator_voice(dialect)
        self.characters: Dict[str, Character] = {}
        self.used_voices: set = {self.narrator_voice}

    def detect_gender_from_name(self, name: str) -> Gender:
        """Detect gender from Arabic name"""
        name = name.strip()

        # Check against known female names
        if name in self.FEMALE_NAMES:
            return Gender.FEMALE

        # Check against known male names
        if name in self.MALE_NAMES:
            return Gender.MALE

        # Check for ta marbuta (ة) at end
        if any(name.endswith(marker) for marker in self.FEMALE_MARKERS):
            return Gender.FEMALE

        return Gender.UNKNOWN

    def detect_gender_from_verb(self, verb: str) -> Gender:
        """Detect gender from verb conjugation"""
        # Feminine verbs often end with ت
        feminine_verbs = ['قالت', 'صرخت', 'همست', 'أجابت', 'سألت', 'ردت', 'نادت', 'أكملت', 'تابعت']

        if verb in feminine_verbs:
            return Gender.FEMALE

        return Gender.MALE

    def extract_character_from_dialogue_verb(self, text: str) -> Optional[Tuple[str, Gender]]:
        """
        Extract character name from dialogue verb pattern

        Examples:
        - "قال أحمد:" → ("أحمد", MALE)
        - "قالت فاطمة:" → ("فاطمة", FEMALE)
        - "صرخ الرجل:" → ("الرجل", MALE)
        """
        for verb in self.DIALOGUE_VERBS:
            # Pattern: verb + name + colon
            pattern = rf'{verb}\s+([\w\s]+?)[:：]'
            match = re.search(pattern, text)

            if match:
                name = match.group(1).strip()
                gender = self.detect_gender_from_verb(verb)

                # Override with name-based gender if more reliable
                name_gender = self.detect_gender_from_name(name)
                if name_gender != Gender.UNKNOWN:
                    gender = name_gender

                return (name, gender)

        return None

    def get_or_create_character(self, name: str, gender: Gender) -> Character:
        """Get existing character or create new one with unique voice"""
        if name in self.characters:
            return self.characters[name]

        # Assign unique voice
        available_voices = AzureVoicePool.get_unique_voices(self.dialect, 14)

        # Find first unused voice matching gender
        voice_id = None
        for voice in available_voices:
            if voice not in self.used_voices:
                # Check if voice matches gender
                if (gender == Gender.FEMALE and 'Female' in voice) or \
                   (gender == Gender.MALE and 'Male' in voice):
                    voice_id = voice
                    break

        # Fallback: use any unused voice
        if not voice_id:
            for voice in available_voices:
                if voice not in self.used_voices:
                    voice_id = voice
                    break

        # Fallback: reuse voice if all taken
        if not voice_id:
            voice_id = AzureVoicePool.get_voice(self.dialect, gender)

        character = Character(
            name=name,
            gender=gender,
            voice_id=voice_id
        )

        self.characters[name] = character
        self.used_voices.add(voice_id)

        return character

    def split_into_segments(self, text: str) -> List[TextSegment]:
        """
        Split text into segments with voice assignments

        Returns list of TextSegment objects with voice_id assigned
        """
        segments: List[TextSegment] = []

        # Split by paragraphs
        paragraphs = text.split('\n\n')

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check for dialogue patterns
            char_info = self.extract_character_from_dialogue_verb(para)

            if char_info:
                # This paragraph has character dialogue
                name, gender = char_info
                character = self.get_or_create_character(name, gender)
                character.dialogue_count += 1

                # Split into narration + dialogue
                # Pattern: "verb name: dialogue"
                for verb in self.DIALOGUE_VERBS:
                    pattern = rf'({verb}\s+[\w\s]+?[:：])\s*(.*)'
                    match = re.search(pattern, para)

                    if match:
                        intro = match.group(1)
                        dialogue = match.group(2)

                        # Narration (intro)
                        segments.append(TextSegment(
                            text=intro,
                            segment_type='narration',
                            voice_id=self.narrator_voice
                        ))

                        # Dialogue
                        segments.append(TextSegment(
                            text=dialogue,
                            segment_type='dialogue',
                            character=character,
                            voice_id=character.voice_id
                        ))
                        break
                else:
                    # No split found, treat as narration
                    segments.append(TextSegment(
                        text=para,
                        segment_type='narration',
                        voice_id=self.narrator_voice
                    ))
            else:
                # Regular narration
                segments.append(TextSegment(
                    text=para,
                    segment_type='narration',
                    voice_id=self.narrator_voice
                ))

        return segments

    def generate_ssml(self, segments: List[TextSegment], add_pauses: bool = True) -> str:
        """
        Generate SSML with voice switching for Azure TTS

        Args:
            segments: List of TextSegment with voice assignments
            add_pauses: Whether to add pauses between segments

        Returns:
            SSML string ready for Azure Speech Service
        """
        ssml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-{self.dialect}">'
        ]

        for i, segment in enumerate(segments):
            # Add voice tag
            ssml_parts.append(f'  <voice name="{segment.voice_id}">')

            # Add text (escape XML special characters)
            text = segment.text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            ssml_parts.append(f'    {text}')

            # Add pause INSIDE voice tag if not last segment
            if add_pauses and i < len(segments) - 1:
                ssml_parts.append('    <break time="500ms"/>')

            # Close voice tag
            ssml_parts.append('  </voice>')

        ssml_parts.append('</speak>')

        return '\n'.join(ssml_parts)

    def analyze_and_assign(self, text: str) -> Tuple[List[TextSegment], str]:
        """
        Complete pipeline: analyze text and generate SSML

        Args:
            text: Long Arabic text (e.g., audiobook chapter)

        Returns:
            (segments, ssml) - List of segments and generated SSML
        """
        segments = self.split_into_segments(text)
        ssml = self.generate_ssml(segments)

        return segments, ssml

    def get_character_summary(self) -> Dict[str, Dict]:
        """Get summary of all detected characters and their voices"""
        summary = {}

        for name, char in self.characters.items():
            summary[name] = {
                'gender': char.gender.value,
                'voice': char.voice_id,
                'dialogue_count': char.dialogue_count
            }

        return summary


def demo():
    """Demo: Assign voices to a sample Arabic story"""

    # Sample story with multiple characters
    story = """كان يا ما كان في قديم الزمان، في مدينة صغيرة، عاش رجل يدعى أحمد وزوجته فاطمة.

قال أحمد: يا فاطمة، أريد أن أذهب إلى السوق لشراء بعض الطعام.

قالت فاطمة: حسناً يا أحمد، لكن كن حذراً في الطريق.

ذهب أحمد إلى السوق ووجد صديقه القديم علي.

صرخ علي: أحمد! يا لها من مفاجأة! لم أرك منذ سنوات!

رد أحمد: علي! كم أنا سعيد برؤيتك! كيف حالك؟

همس علي: الحمد لله، الأمور جيدة. وأنت؟

قال أحمد: أنا بخير، الحمد لله.

عاد أحمد إلى البيت وحكى لفاطمة عن لقائه.

قالت فاطمة: ما شاء الله! يجب أن ندعو علي لزيارتنا قريباً.

وعاشوا في سعادة وهناء."""

    print("=" * 80)
    print("CHARACTER VOICE ASSIGNMENT DEMO")
    print("=" * 80)

    # Create assigner
    assigner = CharacterVoiceAssigner(dialect='EG', narrator_gender=Gender.FEMALE)

    # Analyze and assign
    segments, ssml = assigner.analyze_and_assign(story)

    # Print results
    print(f"\n📊 ANALYSIS RESULTS")
    print(f"Total segments: {len(segments)}")
    print(f"Narration segments: {sum(1 for s in segments if s.segment_type == 'narration')}")
    print(f"Dialogue segments: {sum(1 for s in segments if s.segment_type == 'dialogue')}")

    print(f"\n👥 DETECTED CHARACTERS:")
    summary = assigner.get_character_summary()
    for name, info in summary.items():
        print(f"  - {name}: {info['gender']} ({info['voice']}) - {info['dialogue_count']} dialogues")

    print(f"\n🎙️ VOICE ASSIGNMENTS:")
    for i, segment in enumerate(segments, 1):
        char_info = f" [{segment.character.name}]" if segment.character else ""
        segment_text = segment.text[:50] + "..." if len(segment.text) > 50 else segment.text
        print(f"  {i}. {segment.segment_type.upper()}{char_info} ({segment.voice_id})")
        print(f"     \"{segment_text}\"")

    print(f"\n📝 GENERATED SSML (first 500 chars):")
    print(ssml[:500] + "...")

    # Save to file
    output_file = '/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/demo_multivoice.ssml'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(ssml)

    print(f"\n✅ Full SSML saved to: {output_file}")
    print(f"\nTo generate audio, use:")
    print(f"  azure.generate_audio_from_ssml('{output_file}', 'output.mp3')")


if __name__ == '__main__':
    demo()
