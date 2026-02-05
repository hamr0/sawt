#!/usr/bin/env python3
"""
Test Full Pipeline → Azure Integration

Process Arabic text through the full pipeline and send to Azure TTS
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main import ArabicTTS
from src.core.azure_xsampa_converter import ipa_to_azure_xsampa
from tools.azure_tts.azure_integration import AzureTTS


def test_pipeline_to_azure():
    print("=" * 80)
    print("FULL PIPELINE → AZURE TTS TEST")
    print("=" * 80)

    # Initialize
    print("\nInitializing...")
    arabic_tts = ArabicTTS(dialect='EG')
    azure_tts = AzureTTS()
    print("✅ Both engines initialized")

    # Test cases
    test_cases = [
        "السلام عليكم",
        "صباح الخير",
        "الشمس ساطعة اليوم",
        "الحمد لله"
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {i}: {text}")
        print("=" * 80)

        # Process through pipeline
        print("\n[1] Processing through Arabic TTS pipeline...")
        result = arabic_tts.process_text(text, dialect='EG')

        # Extract IPA from all words
        ipa_parts = []
        for word in result.get('words', []):
            if word.get('type') == 'arabic_word':
                for syl in word.get('syllables', []):
                    ipa_parts.append(syl.get('ipa', ''))

        # Join and clean IPA (remove square brackets and diacritics)
        full_ipa = ''.join(ipa_parts)
        # Remove square brackets
        full_ipa = full_ipa.replace('[', '').replace(']', '')
        # Remove Arabic diacritics
        for code in ['\u064B', '\u064C', '\u064D', '\u064E', '\u064F', '\u0650', '\u0651', '\u0652']:
            full_ipa = full_ipa.replace(chr(int(code, 16)) if isinstance(code, str) and code.startswith('0x') else code, '')

        print(f"    IPA (raw): /{full_ipa}/")

        # Convert to Azure-compatible X-SAMPA
        print("\n[2] Converting to Azure-compatible X-SAMPA...")
        azure_xsampa = ipa_to_azure_xsampa(full_ipa)
        print(f"    X-SAMPA: [{azure_xsampa}]")

        # Generate audio - Plain text
        print("\n[3] Generating Azure audio (plain text)...")
        output_plain = f"/tmp/test_pipeline_{i}_plain.mp3"
        success, msg = azure_tts.generate_audio(
            text, '', output_plain,
            voice='ar-EG-ShakirNeural',
            use_phonetic=False
        )
        print(f"    {'✅' if success else '❌'} {msg}")

        # Generate audio - X-SAMPA
        print("\n[4] Generating Azure audio (Azure-compatible X-SAMPA)...")
        output_xsampa = f"/tmp/test_pipeline_{i}_xsampa.mp3"
        success, msg = azure_tts.generate_audio(
            text, azure_xsampa, output_xsampa,
            voice='ar-EG-ShakirNeural',
            use_phonetic=True
        )
        print(f"    {'✅' if success else '❌'} {msg}")

    print("\n" + "=" * 80)
    print("PIPELINE TEST COMPLETE")
    print("=" * 80)
    print("\nGenerated files in /tmp/:")
    print("  test_pipeline_1_plain.mp3 / test_pipeline_1_xsampa.mp3")
    print("  test_pipeline_2_plain.mp3 / test_pipeline_2_xsampa.mp3")
    print("  test_pipeline_3_plain.mp3 / test_pipeline_3_xsampa.mp3")
    print("  test_pipeline_4_plain.mp3 / test_pipeline_4_xsampa.mp3")
    print("\n📋 Next: Listen to pairs and compare quality")


if __name__ == '__main__':
    test_pipeline_to_azure()
