#!/usr/bin/env python3
"""
Test Azure with MANUALLY VERIFIED X-SAMPA

Use known-correct X-SAMPA from Azure documentation to verify it actually works
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.azure_tts.azure_integration import AzureTTS


def test_manual_xsampa():
    print("=" * 80)
    print("MANUAL X-SAMPA TEST - KNOWN CORRECT PHONEMES")
    print("=" * 80)

    azure = AzureTTS()

    # Test cases with MANUALLY CRAFTED X-SAMPA
    # Using only phonemes we KNOW Azure supports
    tests = [
        {
            "name": "Test 1: Simple greeting (manual)",
            "text": "مرحبا",
            "xsampa": "marHaba",  # Simple: m-a-r-H-a-b-a
            "note": "Basic phonemes only"
        },
        {
            "name": "Test 2: With long vowels (manual)",
            "text": "سلام",
            "xsampa": "sala:m",  # s-a-l-a:-m
            "note": "Long vowel with colon"
        },
        {
            "name": "Test 3: Good morning (manual, simple)",
            "text": "صباح الخير",
            "xsampa": "sabaH alxajr",  # Simple: s-a-b-a-H SPACE a-l-x-a-j-r
            "note": "Two words with space"
        },
        {
            "name": "Test 4: Good morning (manual, with long vowels)",
            "text": "صباح الخير",
            "xsampa": "saba:H alxajr",  # s-a-b-a:-H SPACE a-l-x-a-j-r
            "note": "Long vowel in first word"
        },
        {
            "name": "Test 5: Good morning (manual, full phonetic)",
            "text": "صباح الخير",
            "xsampa": "saba:H al-xajr",  # With hyphen
            "note": "Hyphen between al-"
        },
    ]

    for i, test in enumerate(tests, 1):
        print(f"\n{test['name']}")
        print(f"  Text: {test['text']}")
        print(f"  X-SAMPA: {test['xsampa']}")
        print(f"  Note: {test['note']}")

        # Generate plain version
        output_plain = f"/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/manual_test_{i}_plain.mp3"
        success_plain, msg_plain = azure.generate_audio(
            test['text'], '', output_plain,
            voice='ar-EG-ShakirNeural',
            use_phonetic=False
        )
        print(f"  Plain: {'✅' if success_plain else '❌'} {msg_plain}")

        # Generate X-SAMPA version
        output_xsampa = f"/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/manual_test_{i}_xsampa.mp3"
        success_xsampa, msg_xsampa = azure.generate_audio(
            test['text'], test['xsampa'], output_xsampa,
            voice='ar-EG-ShakirNeural',
            use_phonetic=True
        )
        print(f"  X-SAMPA: {'✅' if success_xsampa else '❌'} {msg_xsampa}")

        if success_plain and success_xsampa:
            import os
            size_plain = os.path.getsize(output_plain)
            size_xsampa = os.path.getsize(output_xsampa)
            diff = ((size_plain - size_xsampa) / size_plain) * 100
            print(f"  Size: Plain={size_plain} bytes, X-SAMPA={size_xsampa} bytes, Diff={diff:.1f}%")

    print("\n" + "=" * 80)
    print("IMPORTANT: LISTEN TO THESE FILES")
    print("=" * 80)
    print("\nManually crafted X-SAMPA should produce CLEAR pronunciation.")
    print("If these are ALSO gibberish, then Azure doesn't support X-SAMPA for Arabic.")
    print("If these are CLEAR, then our pipeline X-SAMPA has issues.")
    print("\nFiles in: /home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/")
    print("  manual_test_1_plain.mp3 vs manual_test_1_xsampa.mp3")
    print("  manual_test_2_plain.mp3 vs manual_test_2_xsampa.mp3")
    print("  manual_test_3_plain.mp3 vs manual_test_3_xsampa.mp3")
    print("  manual_test_4_plain.mp3 vs manual_test_4_xsampa.mp3")
    print("  manual_test_5_plain.mp3 vs manual_test_5_xsampa.mp3")


if __name__ == '__main__':
    test_manual_xsampa()
