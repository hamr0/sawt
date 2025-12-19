#!/usr/bin/env python3
"""
Test Polly with corrected X-SAMPA (no spaces between syllables)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import ArabicTTS
from src.integrations.polly import PollyTTS

# Test words
test_words = [
    ('صباح', 'morning'),
    ('طعام', 'food'),
    ('قلب', 'heart'),
]

def main():
    print("=" * 80)
    print("POLLY X-SAMPA FIX TEST")
    print("=" * 80)

    try:
        polly = PollyTTS()
        print("✅ Polly client initialized")
    except Exception as e:
        print(f"❌ Polly not available: {e}")
        return

    tts = ArabicTTS('MSA')

    for arabic_word, english in test_words:
        print(f"\n{'-' * 80}")
        print(f"Word: {arabic_word} ({english})")
        print(f"{'-' * 80}")

        # Process text
        result = tts.process_text(arabic_word)

        # Extract X-SAMPA (CORRECTED - no spaces)
        xsampa_parts = []
        for word in result.get('words', []):
            if word.get('type') == 'arabic_word':
                for syllable in word.get('syllables', []):
                    syl_xsampa = syllable.get('xsampa', '')
                    if syl_xsampa:
                        xsampa_parts.append(syl_xsampa)

        full_xsampa = ''.join(xsampa_parts)  # NO SPACES

        print(f"  Arabic:  {arabic_word}")
        print(f"  X-SAMPA: {full_xsampa}")

        # Generate audio
        output_path = f"static/audio/polly_test_{english}.mp3"
        success, message = polly.generate_audio(
            text=arabic_word,
            xsampa=full_xsampa,
            output_path=output_path,
            voice_id='Zeina',
            engine='neural'
        )

        if success:
            print(f"  ✅ {message}")
        else:
            print(f"  ❌ {message}")

    print(f"\n{'=' * 80}")
    print("TEST COMPLETE")
    print(f"{'=' * 80}")
    print("\nListen to the generated files:")
    for word, english in test_words:
        print(f"  - static/audio/polly_test_{english}.mp3")

if __name__ == '__main__':
    main()
