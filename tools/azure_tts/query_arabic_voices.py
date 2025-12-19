#!/usr/bin/env python3
"""
Query Azure Speech Service for Arabic Voice Capabilities
Tests what styles each Arabic voice actually supports
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("ERROR: Azure Speech SDK not installed")
    print("Run: pip install azure-cognitiveservices-speech")
    sys.exit(1)

import json
from datetime import datetime


def query_arabic_voices():
    """Query Azure for all Arabic voices and their capabilities"""

    print("=" * 80)
    print("Azure Arabic Voice Capabilities Query")
    print("=" * 80)

    # Check for Azure credentials
    subscription_key = os.getenv('AZURE_SPEECH_KEY')
    region = os.getenv('AZURE_SPEECH_REGION', 'eastus')

    if not subscription_key:
        print("\nERROR: AZURE_SPEECH_KEY environment variable not set")
        print("\nSet it with:")
        print("  export AZURE_SPEECH_KEY='your-key-here'")
        print("  export AZURE_SPEECH_REGION='eastus'  # optional")
        sys.exit(1)

    print(f"\nConnecting to Azure Speech Service...")
    print(f"Region: {region}")

    try:
        # Create speech config
        speech_config = speechsdk.SpeechConfig(
            subscription=subscription_key,
            region=region
        )

        # Create synthesizer to query voices
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        # Get voice list
        print("\nQuerying available voices...")
        result = synthesizer.get_voices_async().get()

        if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
            print(f"✓ Retrieved {len(result.voices)} total voices")

            # Filter Arabic voices
            arabic_voices = [v for v in result.voices if v.locale.startswith('ar-')]
            print(f"✓ Found {len(arabic_voices)} Arabic voices")

            # Build detailed voice information
            voice_data = {
                "query_timestamp": datetime.now().isoformat(),
                "azure_region": region,
                "total_voices_available": len(result.voices),
                "arabic_voices_count": len(arabic_voices),
                "dialects": {}
            }

            # Organize by dialect
            for voice in arabic_voices:
                locale = voice.locale  # e.g., ar-EG, ar-SA

                if locale not in voice_data["dialects"]:
                    voice_data["dialects"][locale] = {
                        "locale": locale,  # e.g., ar-EG
                        "voices": []
                    }

                # Extract voice capabilities (only use attributes that exist)
                voice_info = {
                    "short_name": voice.short_name,  # e.g., ar-EG-ShakirNeural
                    "local_name": getattr(voice, 'local_name', voice.short_name),  # Arabic name
                    "gender": voice.gender.name.lower() if hasattr(voice.gender, 'name') else str(voice.gender).lower(),
                    "voice_type": voice.voice_type.name if hasattr(voice.voice_type, 'name') else str(voice.voice_type),
                    "style_list": list(voice.style_list) if hasattr(voice, 'style_list') and voice.style_list else [],
                    "role_play_list": list(voice.role_play_list) if hasattr(voice, 'role_play_list') and voice.role_play_list else []
                }

                voice_data["dialects"][locale]["voices"].append(voice_info)

            # Print summary
            print("\n" + "=" * 80)
            print("ARABIC VOICE SUMMARY")
            print("=" * 80)

            for locale, data in sorted(voice_data["dialects"].items()):
                print(f"\n{locale}")
                print("-" * 40)

                for voice in data["voices"]:
                    print(f"  • {voice['short_name']}")
                    print(f"    Gender: {voice['gender']}")
                    print(f"    Type: {voice['voice_type']}")

                    if voice['style_list']:
                        print(f"    Styles: {', '.join(voice['style_list'])}")
                    else:
                        print(f"    Styles: None (style tags not supported)")

                    if voice['role_play_list']:
                        print(f"    Roles: {', '.join(voice['role_play_list'])}")

            # Save to JSON
            output_file = Path(__file__).parent / "arabic_voices_capabilities.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(voice_data, f, indent=2, ensure_ascii=False)

            print("\n" + "=" * 80)
            print(f"✓ Full data saved to: {output_file}")
            print("=" * 80)

            # Key findings summary
            print("\n📊 KEY FINDINGS:")

            styles_supported = sum(1 for locale_data in voice_data["dialects"].values()
                                 for voice in locale_data["voices"]
                                 if voice['style_list'])

            print(f"  • Voices with style support: {styles_supported}/{len(arabic_voices)}")

            all_styles = set()
            for locale_data in voice_data["dialects"].values():
                for voice in locale_data["voices"]:
                    all_styles.update(voice['style_list'])

            if all_styles:
                print(f"  • Available styles: {', '.join(sorted(all_styles))}")
            else:
                print(f"  ⚠ NO ARABIC VOICES SUPPORT STYLES")
                print(f"    Style tags are likely English/Chinese only")

            return voice_data

        else:
            print(f"✗ Error: {result.error_details}")
            return None

    except Exception as e:
        print(f"\n✗ Error querying Azure: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = query_arabic_voices()

    if result:
        print("\n✓ Query complete!")
    else:
        print("\n✗ Query failed")
        sys.exit(1)
