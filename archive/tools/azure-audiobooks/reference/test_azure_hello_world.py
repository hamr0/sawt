#!/usr/bin/env python3
"""
Azure X-SAMPA Hello World Test

CRITICAL TEST: Does Azure Speech Service actually support X-SAMPA phoneme tags for Arabic?

This test will compare:
1. Plain Arabic text
2. Arabic with X-SAMPA phoneme tag

If phoneme tags work: pronunciation should be controllable via X-SAMPA
If phoneme tags DON'T work: both should sound identical (like Polly issue)
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.azure_tts.azure_integration import AzureTTS
except Exception as e:
    print(f"Error importing: {e}")
    sys.exit(1)


def test_azure_xsampa_support():
    print("=" * 80)
    print("AZURE SPEECH SERVICE X-SAMPA SUPPORT TEST FOR ARABIC")
    print("=" * 80)

    # Initialize Azure
    try:
        azure = AzureTTS()
        print("✅ Azure TTS initialized\n")
    except Exception as e:
        print(f"❌ Cannot initialize Azure TTS: {e}")
        print("\nTroubleshooting:")
        print("  1. Set AZURE_SPEECH_KEY environment variable:")
        print("     export AZURE_SPEECH_KEY='your-key-here'")
        print("  2. Install Azure Speech SDK:")
        print("     pip install azure-cognitiveservices-speech")
        print("  3. Get your key from: https://portal.azure.com")
        return

    # Test word: صباح (morning)
    arabic_text = "صباح الخير"

    # Test cases
    test_cases = [
        {
            "name": "Test 1: Plain Arabic (baseline)",
            "text": arabic_text,
            "xsampa": "",
            "use_phonetic": False,
            "filename": "/tmp/test_azure_plain.mp3"
        },
        {
            "name": "Test 2: X-SAMPA phoneme tag",
            "text": arabic_text,
            "xsampa": "s_?Aba:X\\AlXajr",  # صباح الخير in X-SAMPA
            "use_phonetic": True,
            "filename": "/tmp/test_azure_xsampa.mp3"
        },
        {
            "name": "Test 3: WRONG pronunciation (should sound different if tags work)",
            "text": arabic_text,
            "xsampa": "bAtAtA",  # "batata" (potato) - completely wrong
            "use_phonetic": True,
            "filename": "/tmp/test_azure_wrong.mp3"
        }
    ]

    results = []

    for test in test_cases:
        print(f"\n{test['name']}")
        print(f"Text: {test['text']}")
        if test['xsampa']:
            print(f"X-SAMPA: {test['xsampa']}")

        try:
            success, msg = azure.generate_audio(
                test['text'],
                test['xsampa'],
                test['filename'],
                voice='ar-EG-ShakirNeural',
                use_phonetic=test['use_phonetic']
            )

            if success:
                print(f"✅ {msg}")
                results.append({
                    "test": test['name'],
                    "status": "success",
                    "file": test['filename']
                })
            else:
                print(f"❌ {msg}")
                results.append({
                    "test": test['name'],
                    "status": "error",
                    "error": msg
                })

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error: {error_msg}")
            results.append({
                "test": test['name'],
                "status": "error",
                "error": error_msg
            })

    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS INSTRUCTIONS")
    print("=" * 80)
    print("\nListen to the generated files:")
    for r in results:
        if r['status'] == 'success':
            print(f"  - {r['file']}")

    print("\n📋 WHAT TO LISTEN FOR:")
    print("-" * 80)
    print("1. Compare Test 1 (plain) vs Test 2 (X-SAMPA)")
    print("   → If IDENTICAL: Azure ignores X-SAMPA tags ❌")
    print("   → If DIFFERENT: Azure uses X-SAMPA tags ✅")
    print()
    print("2. Listen to Test 3 (wrong pronunciation)")
    print("   → Should sound like 'batata' (potato) if X-SAMPA works")
    print("   → Should sound like 'sabah al-khayr' if X-SAMPA is ignored")
    print()
    print("=" * 80)
    print("CRITICAL DECISION POINT")
    print("=" * 80)
    print("If X-SAMPA phoneme tags work:")
    print("  ✅ Your phonological processing pipeline is valuable")
    print("  ✅ You can control pronunciation with your rules")
    print("  ✅ All dialects possible via phonetic control")
    print()
    print("If X-SAMPA phoneme tags DON'T work:")
    print("  ❌ Azure only uses plain Arabic text (like Polly)")
    print("  ❌ Your phonological processing may be over-engineering")
    print("  ❌ Need to reconsider TTS strategy")
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Listen to the 3 test files above")
    print("2. Determine if Test 1 and Test 2 sound different")
    print("3. If they sound the same:")
    print("   → Azure doesn't support X-SAMPA for Arabic")
    print("   → Consider using plain text approach")
    print("   → Simplify pipeline or find alternative TTS")
    print()
    print("4. If they sound different:")
    print("   → Proceed with full test suite:")
    print("   → python3 tools/azure_tts/test_azure_phonetic_control.py")
    print()


if __name__ == '__main__':
    test_azure_xsampa_support()
