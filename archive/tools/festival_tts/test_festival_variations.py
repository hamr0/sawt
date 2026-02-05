#!/usr/bin/env python3
"""
Festival TTS Comprehensive Variation Test

Tests Festival with:
1. Plain text → Festival (baseline)
2. Mishkal diacritized → Festival (with voice variations)
3. X-SAMPA phonemes → Festival (with voice variations)

Voice Variations:
- Normal male (baseline)
- Female (higher pitch)
- Older male (lower pitch, slower)
- Fast-talking (higher pitch, faster)
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main import ArabicTTS
from src.core.azure_xsampa_converter import ipa_to_azure_xsampa


def check_festival():
    """Check if Festival is installed"""
    try:
        result = subprocess.run(['festival', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Festival installed")
            return True
        else:
            print("❌ Festival not installed")
            return False
    except Exception as e:
        print(f"❌ Festival not found: {e}")
        print("\nInstall with:")
        print("  sudo apt-get install festival")
        return False


def create_festival_script_with_variations(text, output_path, voice_type='normal'):
    """
    Create Festival script with voice variations

    Voice types:
    - normal: Male voice, normal pitch/speed
    - female: Higher pitch (female character)
    - older: Lower pitch, slower (older character)
    - fast: Higher pitch, faster (excited character)
    """

    # Voice parameter mappings
    voice_params = {
        'normal': {
            'pitch_start': 100,
            'pitch_end': 100,
            'duration_stretch': 1.0,
            'description': 'Normal male voice'
        },
        'female': {
            'pitch_start': 150,
            'pitch_end': 150,
            'duration_stretch': 1.0,
            'description': 'Female voice (higher pitch)'
        },
        'older': {
            'pitch_start': 80,
            'pitch_end': 80,
            'duration_stretch': 1.2,
            'description': 'Older male (lower, slower)'
        },
        'fast': {
            'pitch_start': 120,
            'pitch_end': 120,
            'duration_stretch': 0.85,
            'description': 'Fast-talking (faster tempo)'
        }
    }

    params = voice_params.get(voice_type, voice_params['normal'])

    # Create Festival script with voice modifications
    script = f'''
; Voice parameters for: {params['description']}
(set! text "{text}")

; Set pitch (F0) parameters
(set! duffint_params '((start {params['pitch_start']}) (end {params['pitch_end']})))

; Set duration/speed parameters
(Parameter.set 'Duration_Stretch {params['duration_stretch']})

; Synthesize
(utt.save.wave
  (utt.synth (eval (list 'Utterance 'Text text)))
  "{output_path}")
'''

    return script, params['description']


def test_mode_1_plain_text():
    """Test Mode 1: Plain Arabic text with voice variations"""
    print("\n" + "=" * 80)
    print("MODE 1: PLAIN TEXT → FESTIVAL (with voice variations)")
    print("=" * 80)

    test_cases = [
        {
            "text": "السلام عليكم ورحمة الله وبركاته",
            "description": "Greeting"
        },
        {
            "text": "صباح الخير يا صديقي العزيز",
            "description": "Good morning"
        }
    ]

    output_dir = Path("/home/hamr/PycharmProjects/ArabicTTS/audio/festival_tests")
    output_dir.mkdir(parents=True, exist_ok=True)

    voice_types = ['normal', 'female', 'older', 'fast']

    for test_idx, test in enumerate(test_cases, 1):
        print(f"\n--- Test {test_idx}: {test['description']} ---")
        print(f"Text: {test['text']}")

        for voice_type in voice_types:
            output_file = output_dir / f"mode1_test{test_idx}_{voice_type}.wav"
            script, voice_desc = create_festival_script_with_variations(
                test['text'],
                str(output_file),
                voice_type
            )

            # Write script to temp file
            script_file = output_dir / f"temp_mode1_test{test_idx}_{voice_type}.scm"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)

            # Run Festival
            result = subprocess.run(
                ['festival', '-b', str(script_file)],
                capture_output=True,
                timeout=30
            )

            if result.returncode == 0 and output_file.exists():
                size = output_file.stat().st_size
                print(f"  ✅ {voice_type.upper()}: {output_file.name} ({size} bytes) - {voice_desc}")
            else:
                print(f"  ❌ {voice_type.upper()} failed")

            # Clean up script
            script_file.unlink()


def test_mode_2_mishkal():
    """Test Mode 2: Mishkal diacritized text with voice variations"""
    print("\n" + "=" * 80)
    print("MODE 2: MISHKAL DIACRITIZED → FESTIVAL (with voice variations)")
    print("=" * 80)

    pipeline = ArabicTTS(dialect='EG')

    test_cases = [
        {
            "text": "السلام عليكم ورحمة الله وبركاته",
            "description": "Greeting"
        },
        {
            "text": "صباح الخير يا صديقي العزيز",
            "description": "Good morning"
        }
    ]

    output_dir = Path("/home/hamr/PycharmProjects/ArabicTTS/audio/festival_tests")
    voice_types = ['normal', 'female', 'older', 'fast']

    for test_idx, test in enumerate(test_cases, 1):
        print(f"\n--- Test {test_idx}: {test['description']} ---")
        print(f"Original: {test['text']}")

        # Process through pipeline to get diacritized text
        result = pipeline.process_text(test['text'], dialect='EG')

        # Extract diacritized text
        diacritized_words = []
        for word in result.get('words', []):
            if word.get('type') == 'arabic_word':
                syllables = [syl['syllable'] for syl in word.get('syllables', [])]
                diacritized_words.append(''.join(syllables))
            elif word.get('type') == 'punct':
                diacritized_words.append(word.get('original', ''))

        diacritized_text = ''.join(diacritized_words)
        print(f"Diacritized: {diacritized_text}")

        for voice_type in voice_types:
            output_file = output_dir / f"mode2_test{test_idx}_{voice_type}.wav"
            script, voice_desc = create_festival_script_with_variations(
                diacritized_text,
                str(output_file),
                voice_type
            )

            # Write script
            script_file = output_dir / f"temp_mode2_test{test_idx}_{voice_type}.scm"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)

            # Run Festival
            result = subprocess.run(
                ['festival', '-b', str(script_file)],
                capture_output=True,
                timeout=30
            )

            if result.returncode == 0 and output_file.exists():
                size = output_file.stat().st_size
                print(f"  ✅ {voice_type.upper()}: {output_file.name} ({size} bytes) - {voice_desc}")
            else:
                print(f"  ❌ {voice_type.upper()} failed")

            script_file.unlink()


def test_mode_3_xsampa():
    """Test Mode 3: X-SAMPA phonemes with voice variations"""
    print("\n" + "=" * 80)
    print("MODE 3: X-SAMPA PHONEMES → FESTIVAL (with voice variations)")
    print("=" * 80)

    pipeline = ArabicTTS(dialect='EG')

    test_cases = [
        {
            "text": "السلام عليكم ورحمة الله وبركاته",
            "description": "Greeting"
        },
        {
            "text": "صباح الخير يا صديقي العزيز",
            "description": "Good morning"
        }
    ]

    output_dir = Path("/home/hamr/PycharmProjects/ArabicTTS/audio/festival_tests")
    voice_types = ['normal', 'female', 'older', 'fast']

    for test_idx, test in enumerate(test_cases, 1):
        print(f"\n--- Test {test_idx}: {test['description']} ---")
        print(f"Text: {test['text']}")

        # Process through pipeline to get IPA
        result = pipeline.process_text(test['text'], dialect='EG')

        # Extract IPA
        ipa_parts = []
        for word in result.get('words', []):
            if word.get('type') == 'arabic_word':
                for syl in word.get('syllables', []):
                    ipa = syl.get('ipa', '').replace('[', '').replace(']', '')
                    # Remove diacritics
                    for code in ['\u064B', '\u064C', '\u064D', '\u064E', '\u064F', '\u0650', '\u0651', '\u0652']:
                        ipa = ipa.replace(code, '')
                    ipa_parts.append(ipa)
            elif word.get('type') == 'punct' and word.get('original') == ' ':
                ipa_parts.append(' ')

        full_ipa = ''.join(ipa_parts)
        print(f"IPA: {full_ipa[:60]}{'...' if len(full_ipa) > 60 else ''}")

        # Convert to X-SAMPA (simplified for Festival)
        xsampa = ipa_to_azure_xsampa(full_ipa)
        print(f"X-SAMPA: {xsampa[:60]}{'...' if len(xsampa) > 60 else ''}")

        # Note: Festival phoneme input is complex and may not work directly with X-SAMPA
        # For now, we'll use the diacritized text as a proxy
        # A proper implementation would convert X-SAMPA to Festival phoneme format

        print("  ⚠️  Note: Festival phoneme input requires format conversion")
        print("  Using diacritized text as best approximation for now")

        # Extract diacritized text as fallback
        diacritized_words = []
        for word in result.get('words', []):
            if word.get('type') == 'arabic_word':
                syllables = [syl['syllable'] for syl in word.get('syllables', [])]
                diacritized_words.append(''.join(syllables))
            elif word.get('type') == 'punct':
                diacritized_words.append(word.get('original', ''))

        diacritized_text = ''.join(diacritized_words)

        for voice_type in voice_types:
            output_file = output_dir / f"mode3_test{test_idx}_{voice_type}.wav"
            script, voice_desc = create_festival_script_with_variations(
                diacritized_text,
                str(output_file),
                voice_type
            )

            # Write script
            script_file = output_dir / f"temp_mode3_test{test_idx}_{voice_type}.scm"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)

            # Run Festival
            result = subprocess.run(
                ['festival', '-b', str(script_file)],
                capture_output=True,
                timeout=30
            )

            if result.returncode == 0 and output_file.exists():
                size = output_file.stat().st_size
                print(f"  ✅ {voice_type.upper()}: {output_file.name} ({size} bytes) - {voice_desc}")
            else:
                print(f"  ❌ {voice_type.upper()} failed")

            script_file.unlink()


def main():
    """Run all Festival variation tests"""
    print("=" * 80)
    print("FESTIVAL TTS COMPREHENSIVE VARIATION TEST")
    print("=" * 80)
    print("\nTesting Festival with:")
    print("  1. Plain text (baseline)")
    print("  2. Mishkal diacritized (recommended)")
    print("  3. X-SAMPA phonemes (full pipeline)")
    print("\nVoice Variations:")
    print("  - Normal male (pitch 100, speed 1.0)")
    print("  - Female (pitch 150, speed 1.0)")
    print("  - Older male (pitch 80, speed 1.2 - slower)")
    print("  - Fast-talking (pitch 120, speed 0.85)")
    print("=" * 80)

    # Check Festival
    if not check_festival():
        return

    # Run all tests
    try:
        test_mode_1_plain_text()
        test_mode_2_mishkal()
        test_mode_3_xsampa()

        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETE")
        print("=" * 80)

        output_dir = Path("/home/hamr/PycharmProjects/ArabicTTS/audio/festival_tests")
        print(f"\n📁 Audio files generated: {output_dir}/")
        print("\n📊 Files to compare:")
        print("\nMode 1 (Plain text):")
        print("  - mode1_test1_normal.wav")
        print("  - mode1_test1_female.wav")
        print("  - mode1_test1_older.wav")
        print("  - mode1_test1_fast.wav")
        print("\nMode 2 (Mishkal):")
        print("  - mode2_test1_normal.wav")
        print("  - mode2_test1_female.wav")
        print("  - mode2_test1_older.wav")
        print("  - mode2_test1_fast.wav")
        print("\nMode 3 (X-SAMPA):")
        print("  - mode3_test1_normal.wav")
        print("  - mode3_test1_female.wav")
        print("  - mode3_test1_older.wav")
        print("  - mode3_test1_fast.wav")

        print("\n🎧 LISTENING GUIDE:")
        print("\n1. Compare MODES (which preprocessing is best?):")
        print("   mode1_test1_normal vs mode2_test1_normal vs mode3_test1_normal")
        print("\n2. Compare VOICES (which variation sounds best?):")
        print("   mode2_test1_normal vs mode2_test1_female vs mode2_test1_older vs mode2_test1_fast")
        print("\n3. Rate quality:")
        print("   - Can you distinguish characters with different voices?")
        print("   - Do female/older voices sound natural?")
        print("   - Is mishkal better than plain text?")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
