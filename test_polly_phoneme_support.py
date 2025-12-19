#!/usr/bin/env python3
"""
CRITICAL TEST: Does AWS Polly actually support phoneme tags for Arabic?

This test will compare:
1. Plain Arabic text
2. Arabic with IPA phoneme tag
3. Arabic with X-SAMPA phoneme tag

If phoneme tags work: pronunciation should be different/controlled
If phoneme tags DON'T work: all three should sound identical
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.integrations.polly import PollyTTS
    import boto3
except Exception as e:
    print(f"Error importing: {e}")
    sys.exit(1)

def test_polly_phoneme_support():
    print("=" * 80)
    print("AWS POLLY PHONEME TAG SUPPORT TEST FOR ARABIC")
    print("=" * 80)

    # Initialize Polly
    try:
        polly_client = boto3.client('polly', region_name='us-east-1')
        print("✅ Polly client initialized\n")
    except Exception as e:
        print(f"❌ Cannot initialize Polly: {e}")
        return

    # Test word: صباح (morning)
    arabic_text = "صباح"

    # Test cases
    test_cases = [
        {
            "name": "Test 1: Plain Arabic (baseline)",
            "ssml": f"<speak>{arabic_text}</speak>",
            "filename": "test1_plain.mp3"
        },
        {
            "name": "Test 2: IPA phoneme tag",
            "ssml": f'<speak><phoneme alphabet="ipa" ph="sˤɑbɑːħ">{arabic_text}</phoneme></speak>',
            "filename": "test2_ipa.mp3"
        },
        {
            "name": "Test 3: X-SAMPA phoneme tag",
            "ssml": f'<speak><phoneme alphabet="x-sampa" ph="s_?Aba:X\\">{arabic_text}</phoneme></speak>',
            "filename": "test3_xsampa.mp3"
        },
        {
            "name": "Test 4: WRONG pronunciation (should sound different if tags work)",
            "ssml": f'<speak><phoneme alphabet="ipa" ph="bɑtˤɑtˤɑ">{arabic_text}</phoneme></speak>',
            "filename": "test4_wrong.mp3"
        }
    ]

    results = []

    for test in test_cases:
        print(f"\n{test['name']}")
        print(f"SSML: {test['ssml']}")

        try:
            response = polly_client.synthesize_speech(
                Text=test['ssml'],
                TextType='ssml',
                OutputFormat='mp3',
                VoiceId='Zeina',
                Engine='neural'
            )

            output_path = f"static/audio/{test['filename']}"
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())

            print(f"✅ Generated: {output_path}")
            results.append({
                "test": test['name'],
                "status": "success",
                "file": output_path
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
    print("1. Compare Test 1 (plain) vs Test 2 (IPA)")
    print("   → If IDENTICAL: Polly ignores IPA tags ❌")
    print("   → If DIFFERENT: Polly uses IPA tags ✅")
    print()
    print("2. Compare Test 1 (plain) vs Test 3 (X-SAMPA)")
    print("   → If IDENTICAL: Polly ignores X-SAMPA tags ❌")
    print("   → If DIFFERENT: Polly uses X-SAMPA tags ✅")
    print()
    print("3. Listen to Test 4 (wrong pronunciation)")
    print("   → Should sound like 'batata' (potato) if tags work")
    print("   → Should sound like 'sabah' if tags are ignored")
    print()
    print("=" * 80)
    print("CRITICAL DECISION POINT")
    print("=" * 80)
    print("If phoneme tags work:")
    print("  ✅ Your X-SAMPA pipeline is valuable for Polly")
    print("  ✅ You can control pronunciation with your rules")
    print("  ✅ All dialects possible via phonetic control")
    print()
    print("If phoneme tags DON'T work:")
    print("  ❌ Polly only uses plain Arabic text")
    print("  ❌ Your phonological processing is unused")
    print("  ❌ Need different TTS engine for phonetic control")

if __name__ == '__main__':
    test_polly_phoneme_support()
