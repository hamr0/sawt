#!/usr/bin/env python3
"""
Longer text comparison - Plain vs Manual X-SAMPA
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.azure_tts.azure_integration import AzureTTS


def test_longer():
    print("=" * 80)
    print("LONGER TEXT COMPARISON TEST")
    print("=" * 80)

    azure = AzureTTS()

    # Longer passage (3-4 sentences)
    long_text = """
كان يا ما كان في قديم الزمان رجل فقير يعيش في قرية صغيرة.
كان يعمل بجد كل يوم لكسب قوت يومه.
في صباح أحد الأيام خرج إلى السوق للبحث عن عمل جديد.
"""

    # Manual X-SAMPA for this text (simplified, phonetically reasonable)
    # Not perfect, but using only phonemes we know work
    long_xsampa = """
ka:n ja: ma: ka:n fi: qadi:m azza:man ra:Zul faqi:r ja:i:S fi: qarjatin SaGi:ra.
ka:n ja:mal biZiddin kulla jawm likasbi qu:ti jawmihi.
fi: saba:H aHadi alajja:m xaraZ ila: assu:q lilbaHT Qan Qamalin Zadi:d.
"""

    print(f"\nText ({len(long_text)} characters):")
    print(long_text)
    print(f"\nManual X-SAMPA:")
    print(long_xsampa)

    # Test 1: Plain text
    print("\n" + "=" * 80)
    print("Test 1: Plain Text (baseline)")
    print("=" * 80)

    output_plain = "/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/longer_plain.mp3"
    success, msg = azure.generate_audio(
        long_text.strip(), '', output_plain,
        voice='ar-EG-ShakirNeural',
        use_phonetic=False
    )
    print(f"{'✅' if success else '❌'} {msg}")

    # Test 2: Manual X-SAMPA
    print("\n" + "=" * 80)
    print("Test 2: Manual X-SAMPA (carefully crafted)")
    print("=" * 80)

    output_xsampa = "/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/longer_xsampa_manual.mp3"
    success, msg = azure.generate_audio(
        long_text.strip(), long_xsampa.strip(), output_xsampa,
        voice='ar-EG-ShakirNeural',
        use_phonetic=True
    )
    print(f"{'✅' if success else '❌'} {msg}")

    # Test 3: Pipeline X-SAMPA (problematic?)
    print("\n" + "=" * 80)
    print("Test 3: Pipeline X-SAMPA (from automatic conversion)")
    print("=" * 80)

    from src.main import ArabicTTS as PipelineTTS
    from src.core.azure_xsampa_converter import ipa_to_azure_xsampa

    pipeline = PipelineTTS(dialect='EG')
    result = pipeline.process_text(long_text.strip(), dialect='EG')

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
            ipa_parts.append(' ')  # Preserve word boundaries

    full_ipa = ''.join(ipa_parts)
    pipeline_xsampa = ipa_to_azure_xsampa(full_ipa)

    print(f"Pipeline IPA (first 100 chars): {full_ipa[:100]}...")
    print(f"Pipeline X-SAMPA (first 100 chars): {pipeline_xsampa[:100]}...")

    output_pipeline = "/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/longer_xsampa_pipeline.mp3"
    success, msg = azure.generate_audio(
        long_text.strip(), pipeline_xsampa, output_pipeline,
        voice='ar-EG-ShakirNeural',
        use_phonetic=True
    )
    print(f"{'✅' if success else '❌'} {msg}")

    # Summary
    print("\n" + "=" * 80)
    print("FILES GENERATED - PLEASE LISTEN")
    print("=" * 80)
    print("\n1. longer_plain.mp3 - Baseline (should be clear)")
    print("2. longer_xsampa_manual.mp3 - Manual X-SAMPA (carefully crafted)")
    print("3. longer_xsampa_pipeline.mp3 - Pipeline X-SAMPA (automatic)")
    print("\nCritical question:")
    print("  - If #2 (manual) is CLEAR → Pipeline conversion has issues")
    print("  - If #2 (manual) is GIBBERISH → Azure doesn't support X-SAMPA for Arabic")
    print("\nLocation: /home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/")


if __name__ == '__main__':
    test_longer()
