"""
Azure Speech Service Integration for Arabic TTS
Wrapper for Azure Cognitive Services Speech SDK with X-SAMPA phonetic input support
"""
import os
from pathlib import Path
from typing import Optional, Tuple, List, Dict

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    speechsdk = None


class AzureTTS:
    """
    Wrapper class for Azure Speech Service text-to-speech engine

    Supports X-SAMPA phonetic input for Arabic speech synthesis.
    Requires Azure Speech SDK and valid subscription credentials.
    """

    # Azure neural voices for Arabic dialects
    VOICES = {
        # Egyptian Arabic
        'ar-EG-SalmaNeural': {'language': 'ar-EG', 'gender': 'Female', 'dialect': 'Egyptian'},
        'ar-EG-ShakirNeural': {'language': 'ar-EG', 'gender': 'Male', 'dialect': 'Egyptian'},

        # Saudi/MSA
        'ar-SA-ZariyahNeural': {'language': 'ar-SA', 'gender': 'Female', 'dialect': 'MSA/Saudi'},
        'ar-SA-HamedNeural': {'language': 'ar-SA', 'gender': 'Male', 'dialect': 'MSA/Saudi'},

        # UAE/Gulf
        'ar-AE-FatimaNeural': {'language': 'ar-AE', 'gender': 'Female', 'dialect': 'Gulf'},
        'ar-AE-HamdanNeural': {'language': 'ar-AE', 'gender': 'Male', 'dialect': 'Gulf'},

        # Syria/Levantine
        'ar-SY-AmanyNeural': {'language': 'ar-SY', 'gender': 'Female', 'dialect': 'Levantine'},
        'ar-SY-LaithNeural': {'language': 'ar-SY', 'gender': 'Male', 'dialect': 'Levantine'},
    }

    def __init__(
        self,
        subscription_key: Optional[str] = None,
        region: str = 'eastus',
        verify_installation: bool = True
    ):
        """
        Initialize Azure TTS wrapper

        Args:
            subscription_key: Azure subscription key (or set AZURE_SPEECH_KEY env var)
            region: Azure region (default: 'eastus')
            verify_installation: Check if Azure SDK is installed

        Raises:
            ImportError: If Azure Speech SDK is not installed
            ValueError: If subscription key is not provided
        """
        if speechsdk is None:
            raise ImportError(
                "Azure Speech SDK is not installed. Please install it:\n"
                "pip install azure-cognitiveservices-speech"
            )

        # Get subscription key from parameter or environment
        self.subscription_key = subscription_key or os.getenv('AZURE_SPEECH_KEY')
        if not self.subscription_key:
            raise ValueError(
                "Azure subscription key not provided.\n"
                "Set AZURE_SPEECH_KEY environment variable or pass subscription_key parameter.\n"
                "Get your key from: https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices"
            )

        self.region = region

        # Create speech config
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription_key,
            region=self.region
        )

        # Set output format to MP3
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz128KBitRateMonoMp3
        )

    def xsampa_to_ssml(
        self,
        xsampa: str,
        text: str,
        voice: str = 'ar-EG-ShakirNeural',
        escape_xml: bool = True
    ) -> str:
        """
        Convert X-SAMPA phonetic string to Azure SSML format

        Args:
            xsampa: X-SAMPA phonetic transcription
            text: Original Arabic text (fallback)
            voice: Azure voice name
            escape_xml: Escape XML special characters in text

        Returns:
            SSML string with phoneme tag

        Example:
            >>> azure.xsampa_to_ssml("s_?Aba:X\\", "صباح", "ar-EG-ShakirNeural")
            '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
                    xml:lang="ar-EG">
              <voice name="ar-EG-ShakirNeural">
                <phoneme alphabet="x-sampa" ph="s_?Aba:X\\">صباح</phoneme>
              </voice>
            </speak>'
        """
        # Get language from voice
        language = self._get_language_from_voice(voice)

        # Escape XML special characters if needed
        if escape_xml:
            text = self._escape_xml(text)
            xsampa = self._escape_xml(xsampa)

        # Build SSML
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language}">
  <voice name="{voice}">
    <phoneme alphabet="x-sampa" ph="{xsampa}">{text}</phoneme>
  </voice>
</speak>'''

        return ssml

    def plain_text_to_ssml(
        self,
        text: str,
        voice: str = 'ar-EG-ShakirNeural',
        escape_xml: bool = True
    ) -> str:
        """
        Convert plain Arabic text to Azure SSML format (no phonetic control)

        Args:
            text: Arabic text
            voice: Azure voice name
            escape_xml: Escape XML special characters

        Returns:
            SSML string without phoneme tag
        """
        # Get language from voice
        language = self._get_language_from_voice(voice)

        # Escape XML special characters if needed
        if escape_xml:
            text = self._escape_xml(text)

        # Build SSML (no phoneme tag)
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language}">
  <voice name="{voice}">
    {text}
  </voice>
</speak>'''

        return ssml

    def generate_audio(
        self,
        text: str,
        xsampa: str,
        output_path: str,
        voice: str = 'ar-EG-ShakirNeural',
        use_phonetic: bool = True
    ) -> Tuple[bool, str]:
        """
        Generate audio using Azure Speech Service

        Args:
            text: Original Arabic text
            xsampa: X-SAMPA phonetic representation
            output_path: Path to save MP3 file
            voice: Azure voice name (default: ar-EG-ShakirNeural)
            use_phonetic: Use X-SAMPA phonetic control (default: True)

        Returns:
            Tuple of (success: bool, message: str)

        Example:
            >>> success, msg = azure.generate_audio("صباح", "s_?Aba:X\\", "output.mp3")
            >>> print(msg)
            'Audio generated successfully: output.mp3 (45123 bytes)'
        """
        try:
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate SSML
            if use_phonetic and xsampa:
                ssml = self.xsampa_to_ssml(xsampa, text, voice)
            else:
                ssml = self.plain_text_to_ssml(text, voice)

            # Configure audio output
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            # Synthesize speech
            result = synthesizer.speak_ssml_async(ssml).get()

            # Check result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                file_size = os.path.getsize(output_path)
                mode = "X-SAMPA" if (use_phonetic and xsampa) else "plain text"
                return True, f"Audio generated successfully: {output_path} ({file_size} bytes, {mode})"

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg = f"Azure TTS canceled: {cancellation.reason}"
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    error_msg += f" - {cancellation.error_details}"
                return False, error_msg

            else:
                return False, f"Azure TTS failed with reason: {result.reason}"

        except Exception as e:
            return False, f"Error generating audio: {str(e)}"

    def generate_audio_with_voices(
        self,
        segments: List[Dict[str, str]],
        output_path: str
    ) -> Tuple[bool, str]:
        """
        Generate audio with multiple voices (for dialogue/multi-character)

        Args:
            segments: List of segments with keys:
                - 'text': Arabic text
                - 'xsampa': X-SAMPA phonetic (optional)
                - 'voice': Azure voice name
            output_path: Path to save MP3 file

        Returns:
            Tuple of (success: bool, message: str)

        Example:
            >>> segments = [
            ...     {'text': 'قال الراوي', 'voice': 'ar-EG-SalmaNeural'},
            ...     {'text': 'مرحبا', 'voice': 'ar-EG-ShakirNeural'}
            ... ]
            >>> success, msg = azure.generate_audio_with_voices(segments, "dialogue.mp3")
        """
        try:
            # Build multi-voice SSML
            ssml_parts = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">']

            for segment in segments:
                text = segment['text']
                voice = segment['voice']
                xsampa = segment.get('xsampa', '')

                language = self._get_language_from_voice(voice)
                text_escaped = self._escape_xml(text)

                ssml_parts.append(f'  <voice name="{voice}">')

                if xsampa:
                    xsampa_escaped = self._escape_xml(xsampa)
                    ssml_parts.append(f'    <phoneme alphabet="x-sampa" ph="{xsampa_escaped}">{text_escaped}</phoneme>')
                else:
                    ssml_parts.append(f'    {text_escaped}')

                ssml_parts.append('  </voice>')

            ssml_parts.append('</speak>')
            ssml = '\n'.join(ssml_parts)

            # Configure audio output
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            # Synthesize speech
            result = synthesizer.speak_ssml_async(ssml).get()

            # Check result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                file_size = os.path.getsize(output_path)
                return True, f"Multi-voice audio generated: {output_path} ({file_size} bytes, {len(segments)} segments)"

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg = f"Azure TTS canceled: {cancellation.reason}"
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    error_msg += f" - {cancellation.error_details}"
                return False, error_msg

            else:
                return False, f"Azure TTS failed with reason: {result.reason}"

        except Exception as e:
            return False, f"Error generating multi-voice audio: {str(e)}"

    def generate_audio_from_ssml(
        self,
        ssml: str,
        output_path: str
    ) -> Tuple[bool, str]:
        """
        Generate audio from pre-built SSML

        Args:
            ssml: Complete SSML string with voice tags
            output_path: Path to save audio file

        Returns:
            Tuple of (success: bool, message: str)

        Example:
            >>> ssml = '''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">
            ...   <voice name="ar-EG-SalmaNeural">مرحبا</voice>
            ... </speak>'''
            >>> azure.generate_audio_from_ssml(ssml, "output.mp3")
        """
        try:
            # Configure audio output
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            # Synthesize speech
            result = synthesizer.speak_ssml_async(ssml).get()

            # Check result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                file_size = os.path.getsize(output_path)
                return True, f"Audio generated from SSML: {output_path} ({file_size} bytes)"

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg = f"Azure TTS canceled: {cancellation.reason}"
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    error_msg += f" - {cancellation.error_details}"
                return False, error_msg

            else:
                return False, f"Azure TTS failed with reason: {result.reason}"

        except Exception as e:
            return False, f"Error generating audio from SSML: {str(e)}"

    def _get_language_from_voice(self, voice: str) -> str:
        """Extract language code from voice name (e.g., 'ar-EG-ShakirNeural' → 'ar-EG')"""
        if voice in self.VOICES:
            return self.VOICES[voice]['language']
        # Fallback: extract first two parts
        parts = voice.split('-')
        if len(parts) >= 2:
            return f"{parts[0]}-{parts[1]}"
        return 'ar-EG'  # Default to Egyptian

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))

    def list_voices(self) -> Dict[str, Dict]:
        """Return dictionary of available Arabic voices"""
        return self.VOICES.copy()


if __name__ == "__main__":
    # Quick test
    print("Testing Azure Speech Service Integration")
    print("=" * 70)

    # Check if SDK is installed
    if speechsdk is None:
        print("✗ Azure Speech SDK not installed")
        print("  Install with: pip install azure-cognitiveservices-speech")
        exit(1)

    # Check for subscription key
    subscription_key = os.getenv('AZURE_SPEECH_KEY')
    if not subscription_key:
        print("✗ AZURE_SPEECH_KEY environment variable not set")
        print("  Set your key: export AZURE_SPEECH_KEY='your-key-here'")
        print("  Get key from: https://portal.azure.com")
        exit(1)

    # Initialize
    try:
        azure = AzureTTS()
        print("✓ Azure TTS initialized")
        print(f"  Region: {azure.region}")
        print(f"  Available voices: {len(azure.VOICES)}")
    except Exception as e:
        print(f"✗ Error: {e}")
        exit(1)

    # List voices
    print("\nAvailable Arabic Voices:")
    print("-" * 70)
    for voice_name, info in azure.VOICES.items():
        print(f"  {voice_name}")
        print(f"    Dialect: {info['dialect']}, Gender: {info['gender']}")

    # Test 1: Generate audio from plain Arabic text
    print("\nTest 1: Generate audio from plain Arabic text")
    print("-" * 70)
    text = "السلام عليكم"
    output = "/tmp/test_azure_plain.mp3"
    success, msg = azure.generate_audio(text, "", output, use_phonetic=False)
    print(f"  Text: {text}")
    print(f"  Output: {output}")
    print(f"  Result: {'✓' if success else '✗'} {msg}")

    # Test 2: Generate audio with X-SAMPA
    print("\nTest 2: Generate audio with X-SAMPA phonetic control")
    print("-" * 70)
    text = "صباح"
    xsampa = "s_?Aba:X\\"
    output = "/tmp/test_azure_xsampa.mp3"
    success, msg = azure.generate_audio(text, xsampa, output, use_phonetic=True)
    print(f"  Text: {text}")
    print(f"  X-SAMPA: {xsampa}")
    print(f"  Output: {output}")
    print(f"  Result: {'✓' if success else '✗'} {msg}")

    print("\n" + "=" * 70)
    print("Azure integration test complete!")
