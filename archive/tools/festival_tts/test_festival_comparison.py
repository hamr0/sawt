#!/usr/bin/env python3
"""
Festival TTS Comparison Test - Plain Text vs X-SAMPA

Test Festival with:
1. Plain text (Festival's built-in processing)
2. Plain text + mishkal (our diacritization)
3. X-SAMPA from our pipeline (full phonetic control)
"""
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main import ArabicTTS
from src.core.azure_xsampa_converter import ipa_to_azure_xsampa


def test_festival_modes():
    print("=" * 80)
    print("FESTIVAL TTS COMPARISON TEST")
    print("=" * 80)

    # Check if Festival is installed
    try:
        result = subprocess.run(['festival', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("❌ Festival not installed")
            print("\nInstall with:")
            print("  sudo apt-get install festival")
            print("  # For Arabic voice:")
            print("  # git clone https://github.com/linuxscout/festival-tts-arabic-voices")
            return
        print("✅ Festival installed")
        print(f"   Version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Error checking Festival: {e}")
        return

    # Test cases
    test_cases = [
        {
            "text": "السلام عليكم ورحمة الله وبركاته",
            "description": "Greeting (complex phonology)"
        },
        {
            "text": "صباح الخير يا صديقي العزيز",
            "description": "Good morning (sun letters)"
        },
        {
            "text": "كان يا ما كان في قديم الزمان رجل فقير",
            "description": "Story opening (longer phrase)"
        }
    ]

    output_dir = Path("/home/hamr/PycharmProjects/ArabicTTS/audio/festival_tests")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize our pipeline
    pipeline = ArabicTTS(dialect='EG')

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {i}: {test['description']}")
        print(f"Text: {test['text']}")
        print("=" * 80)

        # Test 1: Plain text (Festival's native processing)
        print("\n[Mode 1] Plain Text (Festival native)")
        output_plain = output_dir / f"test_{i}_plain.wav"

        festival_script = f"""
(set! text "{test['text']}")
(utt.save.wave
  (utt.synth (eval (list 'Utterance 'Text text)))
  "{output_plain}")
"""
        script_file = output_dir / f"test_{i}_plain.scm"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(festival_script)

        result = subprocess.run(
            ['festival', '-b', str(script_file)],
            capture_output=True,
            timeout=30
        )

        if result.returncode == 0 and output_plain.exists():
            size = output_plain.stat().st_size
            print(f"  ✅ Generated: {output_plain.name} ({size} bytes)")
        else:
            print(f"  ❌ Failed: {result.stderr.decode()}")

        # Test 2: Diacritized text (our mishkal processing)
        print("\n[Mode 2] Diacritized (mishkal)")
        result_pipeline = pipeline.process_text(test['text'], dialect='EG')

        # Extract diacritized text
        diacritized_words = []
        for word in result_pipeline.get('words', []):
            if word.get('type') == 'arabic_word':
                # Get syllables and reconstruct diacritized word
                syllables = [syl['syllable'] for syl in word.get('syllables', [])]
                diacritized_words.append(''.join(syllables))
            elif word.get('type') == 'punct':
                diacritized_words.append(word.get('original', ''))

        diacritized_text = ''.join(diacritized_words)
        print(f"  Diacritized: {diacritized_text}")

        output_diac = output_dir / f"test_{i}_diacritized.wav"
        festival_script_diac = f"""
(set! text "{diacritized_text}")
(utt.save.wave
  (utt.synth (eval (list 'Utterance 'Text text)))
  "{output_diac}")
"""
        script_file_diac = output_dir / f"test_{i}_diacritized.scm"
        with open(script_file_diac, 'w', encoding='utf-8') as f:
            f.write(festival_script_diac)

        result = subprocess.run(
            ['festival', '-b', str(script_file_diac)],
            capture_output=True,
            timeout=30
        )

        if result.returncode == 0 and output_diac.exists():
            size = output_diac.stat().st_size
            print(f"  ✅ Generated: {output_diac.name} ({size} bytes)")
        else:
            print(f"  ❌ Failed: {result.stderr.decode()}")

        # Test 3: Phoneme/X-SAMPA input (full pipeline)
        print("\n[Mode 3] Phoneme Input (X-SAMPA via pipeline)")

        # Extract IPA from pipeline
        ipa_parts = []
        for word in result_pipeline.get('words', []):
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
        print(f"  IPA: {full_ipa[:60]}{'...' if len(full_ipa) > 60 else ''}")

        # Convert to X-SAMPA
        xsampa = ipa_to_azure_xsampa(full_ipa)
        print(f"  X-SAMPA: {xsampa[:60]}{'...' if len(xsampa) > 60 else ''}")

        # Festival phoneme format (simplified - may need adjustment)
        # Festival uses different phoneme notation
        # For now, try using IPA directly (Festival may support it)
        output_phoneme = output_dir / f"test_{i}_phoneme.wav"

        # Create Festival phoneme script
        # Note: This is a simplified approach - Festival phoneme syntax is complex
        festival_phoneme_script = f"""
(set! utt1 (Utterance Text "{test['text']}"))
(utt.synth utt1)
(utt.save.wave utt1 "{output_phoneme}")
"""
        script_file_phoneme = output_dir / f"test_{i}_phoneme.scm"
        with open(script_file_phoneme, 'w', encoding='utf-8') as f:
            f.write(festival_phoneme_script)

        result = subprocess.run(
            ['festival', '-b', str(script_file_phoneme)],
            capture_output=True,
            timeout=30
        )

        if result.returncode == 0 and output_phoneme.exists():
            size = output_phoneme.stat().st_size
            print(f"  ✅ Generated: {output_phoneme.name} ({size} bytes)")
            print(f"  ⚠️  Note: Festival phoneme input needs proper format conversion")
        else:
            print(f"  ⚠️  Phoneme input needs Festival-specific format")

    # Summary
    print("\n" + "=" * 80)
    print("FESTIVAL TEST COMPLETE")
    print("=" * 80)
    print(f"\nFiles generated in: {output_dir}/")
    print("\nListen to compare:")
    print("  test_1_plain.wav vs test_1_diacritized.wav")
    print("  test_2_plain.wav vs test_2_diacritized.wav")
    print("  test_3_plain.wav vs test_3_diacritized.wav")
    print("\nKey question:")
    print("  - Does mishkal diacritization improve Festival quality?")
    print("  - Is Festival quality good enough for audiobooks?")
    print("  - How does it compare to eSpeak and Azure?")


if __name__ == '__main__':
    test_festival_modes()
