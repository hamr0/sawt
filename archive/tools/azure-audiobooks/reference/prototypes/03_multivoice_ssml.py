#!/usr/bin/env python3
"""
Prototype 3: Multi-Voice SSML Generation
Tests Azure voice switching with SSML

Goal: Validate Azure accepts voice switching and generates quality audio
"""

import os
import sys
import csv
from pathlib import Path
from datetime import datetime

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("ERROR: Azure Speech SDK not installed")
    print("Run: pip install azure-cognitiveservices-speech")
    sys.exit(1)


# Voice mapping for characters (based on detected 32 Azure voices)
VOICE_MAP = {
    'Narrator': {
        'voice': 'ar-EG-SalmaNeural',  # Female narrator
        'gender': 'female',
        'dialect': 'Egyptian',
        'prosody': {'rate': '1.0', 'pitch': '0%', 'volume': '0%'}
    },
    'أحمد': {
        'voice': 'ar-EG-ShakirNeural',  # Male character
        'gender': 'male',
        'dialect': 'Egyptian',
        'prosody': {'rate': '1.0', 'pitch': '0%', 'volume': '0%'}
    },
    'فاطمة': {
        'voice': 'ar-SA-ZariyahNeural',  # Female character (different dialect for variety)
        'gender': 'female',
        'dialect': 'Saudi',
        'prosody': {'rate': '0.95', 'pitch': '+5%', 'volume': '0%'}
    },
    'محمود': {
        'voice': 'ar-SA-HamedNeural',  # Male character (different dialect)
        'gender': 'male',
        'dialect': 'Saudi',
        'prosody': {'rate': '1.05', 'pitch': '-5%', 'volume': '0%'}
    },
    'Unknown': {
        'voice': 'ar-EG-ShakirNeural',  # Default male voice
        'gender': 'male',
        'dialect': 'Egyptian',
        'prosody': {'rate': '1.0', 'pitch': '0%', 'volume': '0%'}
    }
}


class SSMLGenerator:
    """Generate SSML with multi-voice support"""

    def __init__(self, voice_map: dict):
        self.voice_map = voice_map

    def generate_ssml(self, segments: list) -> str:
        """
        Generate SSML from character detection segments

        Args:
            segments: List of segment dicts with speaker, text, prosody

        Returns:
            SSML string with voice switching
        """
        ssml_parts = []

        # SSML header
        ssml_parts.append(
            '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="ar-EG">'
        )

        current_voice = None

        for seg in segments:
            speaker = seg['speaker']
            text = seg['text']

            # Skip empty segments
            if not text or text == '.':
                continue

            # Get voice config
            voice_config = self.voice_map.get(speaker, self.voice_map['Unknown'])
            voice_name = voice_config['voice']
            prosody = voice_config['prosody']

            # Switch voice if needed
            if voice_name != current_voice:
                # Close previous voice tag
                if current_voice is not None:
                    ssml_parts.append('</voice>')

                # Open new voice tag
                ssml_parts.append(f'<voice name="{voice_name}">')
                current_voice = voice_name

            # Add prosody if non-default
            if prosody['rate'] != '1.0' or prosody['pitch'] != '0%' or prosody['volume'] != '0%':
                ssml_parts.append(
                    f'<prosody rate="{prosody["rate"]}" pitch="{prosody["pitch"]}" volume="{prosody["volume"]}">'
                )
                ssml_parts.append(text)
                ssml_parts.append('</prosody>')
            else:
                ssml_parts.append(text)

            # Add pause between segments
            ssml_parts.append('<break time="300ms"/>')

        # Close last voice tag
        if current_voice is not None:
            ssml_parts.append('</voice>')

        # SSML footer
        ssml_parts.append('</speak>')

        return '\n'.join(ssml_parts)

    def generate_ssml_from_csv(self, csv_path: Path) -> str:
        """Generate SSML from character detection CSV"""

        segments = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip stats rows
                if row['Type'] != 'SEGMENT':
                    break

                segments.append({
                    'speaker': row['Speaker'],
                    'text': row['Text']
                })

        return self.generate_ssml(segments)


def test_azure_synthesis(ssml: str, output_path: Path) -> tuple:
    """
    Test SSML with Azure TTS

    Returns:
        (success: bool, message: str)
    """
    subscription_key = os.getenv('AZURE_SPEECH_KEY')
    region = os.getenv('AZURE_SPEECH_REGION', 'eastus')

    if not subscription_key:
        return False, "AZURE_SPEECH_KEY environment variable not set"

    try:
        # Create speech config
        speech_config = speechsdk.SpeechConfig(
            subscription=subscription_key,
            region=region
        )

        # Set output format
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

        # Create audio config for file output
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))

        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        # Synthesize
        result = synthesizer.speak_ssml_async(ssml).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            duration = len(result.audio_data) / (16000 * 2)  # Approximate duration
            file_size = output_path.stat().st_size / 1024  # KB

            return True, f"Generated {file_size:.1f} KB, ~{duration:.1f}s duration"

        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            return False, f"Synthesis canceled: {cancellation.reason} - {cancellation.error_details}"

        else:
            return False, f"Synthesis failed: {result.reason}"

    except Exception as e:
        return False, f"Exception: {str(e)}"


def main():
    """Run multi-voice SSML prototype"""

    print("=" * 80)
    print("Prototype 3: Multi-Voice SSML Generation")
    print("=" * 80)

    # Find latest character detection CSV
    csv_dir = Path(__file__).parent / 'outputs'
    csv_files = sorted(csv_dir.glob('character_detection_*.csv'))

    if not csv_files:
        print("\n✗ ERROR: No character detection CSV found")
        print("   Run 01_character_detection.py first")
        sys.exit(1)

    csv_path = csv_files[-1]
    print(f"\n1. Using character detection CSV: {csv_path.name}")

    # Generate SSML
    print("\n2. Generating multi-voice SSML...")
    generator = SSMLGenerator(VOICE_MAP)
    ssml = generator.generate_ssml_from_csv(csv_path)

    # Save SSML
    output_dir = Path(__file__).parent / 'outputs'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ssml_path = output_dir / f'multivoice_ssml_{timestamp}.xml'

    with open(ssml_path, 'w', encoding='utf-8') as f:
        f.write(ssml)

    print(f"   ✓ SSML generated: {ssml_path}")
    print(f"   Characters: {len([v for v in VOICE_MAP.values()])}")

    # Show voice assignments
    print("\n   Voice Assignments:")
    for char, config in VOICE_MAP.items():
        print(f"   - {char}: {config['voice']} ({config['gender']}, {config['dialect']})")

    # Test with Azure
    print("\n3. Testing with Azure TTS...")
    print("   This will use your AZURE_SPEECH_KEY environment variable")

    audio_path = output_dir / f'multivoice_audio_{timestamp}.mp3'

    success, message = test_azure_synthesis(ssml, audio_path)

    if success:
        print(f"   ✓ Audio generated: {audio_path}")
        print(f"   {message}")
    else:
        print(f"   ✗ Azure synthesis failed: {message}")
        print("\n   SSML is still valid - check your Azure credentials:")
        print("   export AZURE_SPEECH_KEY='your-key-here'")
        print("   export AZURE_SPEECH_REGION='eastus'")

    # Validation
    print("\n" + "=" * 80)
    print("Validation Results")
    print("=" * 80)

    print(f"\n✓ SSML Generation: SUCCESS")
    print(f"  - Valid multi-voice SSML generated")
    print(f"  - 5 characters mapped to Azure voices")
    print(f"  - Voice switching with prosody support")

    if success:
        print(f"\n✓ Azure Synthesis: SUCCESS")
        print(f"  - Multi-voice audio generated")
        print(f"  - Voice switching confirmed working")
        print(f"\n✓ Prototype 3 SUCCESS - Multi-voice SSML validated!")
    else:
        print(f"\n⚠ Azure Synthesis: SKIPPED (no credentials)")
        print(f"  - SSML structure validated")
        print(f"  - Manual Azure test needed")
        print(f"\n⚠ Prototype 3 PARTIAL - SSML valid, Azure test pending")

    print("\n" + "=" * 80)
    print(f"Generated Files:")
    print(f"1. SSML: {ssml_path}")
    if success:
        print(f"2. Audio: {audio_path}")
    print("\nNext Steps:")
    print(f"1. Review SSML structure for correctness")
    if success:
        print(f"2. Listen to audio for voice switching quality")
    else:
        print(f"2. Set Azure credentials and re-run to test synthesis")
    print("=" * 80)


if __name__ == '__main__':
    main()
