#!/usr/bin/env python3
"""
Azure X-SAMPA Simple Test - Find what phonemes Azure actually supports
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.azure_tts.azure_integration import AzureTTS


def test_simple_xsampa():
    print("=" * 80)
    print("AZURE X-SAMPA PHONEME COMPATIBILITY TEST")
    print("=" * 80)

    azure = AzureTTS()

    # Test progressively simpler X-SAMPA strings
    tests = [
        {
            "name": "Test 1: Very simple (basic consonants + vowels)",
            "text": "سلام",
            "xsampa": "salam"
        },
        {
            "name": "Test 2: With long vowels",
            "text": "سلام",
            "xsampa": "sala:m"
        },
        {
            "name": "Test 3: With pharyngeal (H for ħ)",
            "text": "صباح",
            "xsampa": "sabaH"
        },
        {
            "name": "Test 4: With glottal stop (? for ʔ)",
            "text": "أكل",
            "xsampa": "?akl"
        },
        {
            "name": "Test 5: With emphatic (no modifiers)",
            "text": "صباح",
            "xsampa": "sabah"  # Just use plain letters
        },
        {
            "name": "Test 6: Full phrase simple",
            "text": "صباح الخير",
            "xsampa": "sabah alxajr"
        }
    ]

    results = []
    for test in tests:
        print(f"\n{test['name']}")
        print(f"  Text: {test['text']}")
        print(f"  X-SAMPA: {test['xsampa']}")

        output = f"/tmp/test_simple_{len(results)+1}.mp3"
        success, msg = azure.generate_audio(
            test['text'],
            test['xsampa'],
            output,
            voice='ar-EG-ShakirNeural',
            use_phonetic=True
        )

        if success:
            print(f"  ✅ {msg}")
            results.append((test['name'], test['xsampa'], output, True))
        else:
            print(f"  ❌ {msg}")
            results.append((test['name'], test['xsampa'], output, False))

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    successful = [r for r in results if r[3]]
    failed = [r for r in results if not r[3]]

    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    for name, xsampa, path, _ in successful:
        print(f"  - {xsampa}")

    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(results)}")
        for name, xsampa, path, _ in failed:
            print(f"  - {xsampa}")

    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    if successful:
        print("Azure X-SAMPA works with simplified notation!")
        print("Next steps:")
        print("  1. Update X-SAMPA converter to use simpler notation")
        print("  2. Avoid underscore modifiers (_?)")
        print("  3. Use basic ASCII letters where possible")
        print("  4. Test with actual pipeline output")
    else:
        print("Azure X-SAMPA not working even with simple notation")
        print("May need to use plain text approach")


if __name__ == '__main__':
    test_simple_xsampa()
