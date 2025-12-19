"""
Amazon Polly Integration for Arabic TTS
Wrapper for Amazon Polly neural TTS with X-SAMPA phonetic input support
"""
from typing import Tuple

try:
    import boto3
except ImportError:
    boto3 = None


class PollyTTS:
    """
    Wrapper class for Amazon Polly text-to-speech engine
    
    Supports X-SAMPA phonetic input for Arabic speech synthesis.
    Requires boto3 and AWS credentials configured.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """
        Initialize Polly TTS wrapper
        
        Args:
            region: AWS region (default: 'us-east-1')
        
        Raises:
            ImportError: If boto3 is not installed
            RuntimeError: If AWS credentials are not configured
        """
        self.region = region
        self.polly_client = None
        
        if boto3 is None:
            raise ImportError(
                "boto3 is not installed. Please install it:\n"
                "pip install boto3>=1.28.0"
            )
        
        try:
            self.polly_client = boto3.client('polly', region_name=region)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Polly client: {e}\n"
                "Please configure AWS credentials:\n"
                "1. Set environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)\n"
                "2. Or run: aws configure\n"
                "3. See docs/polly/AWS_SETUP_GUIDE.md for detailed instructions"
            )
    
    def xsampa_to_ssml(self, xsampa: str, text: str) -> str:
        """
        Convert X-SAMPA phonetic string to Polly SSML format

        Args:
            xsampa: X-SAMPA phonetic transcription (IGNORED for Arabic - see note)
            text: Original Arabic text

        Returns:
            SSML string with plain text only (phoneme tags not supported for Arabic)

        Note:
            AWS Polly does NOT support X-SAMPA (or any phoneme alphabet) for Arabic voices.
            X-SAMPA is only supported for 22 languages (English, French, German, etc.).
            For Arabic (arb), Polly uses its built-in MSA pronunciation only.

            Supported languages for X-SAMPA: cy-GB, da-DK, de-DE, en-AU, en-GB, en-GB-WLS,
            en-IN, en-US, fr-BE, fr-CA, fr-FR, is-IS, it-IT, nb-NO, nl-BE, nl-NL, pl-PL,
            pt-BR, pt-PT, ro-RO, sv-SE, tr-TR

        Example:
            >>> polly.xsampa_to_ssml("saba:H", "صباح")
            '<speak>صباح</speak>'  # X-SAMPA ignored, plain text used
        """
        # ALWAYS use plain text for Arabic (phoneme tags not supported)
        return f'<speak>{text}</speak>'
    
    def generate_audio(
        self,
        text: str,
        xsampa: str,
        output_path: str,
        voice_id: str = 'Zeina',
        engine: str = 'neural'
    ) -> Tuple[bool, str]:
        """
        Generate audio using Amazon Polly with automatic fallback

        Args:
            text: Original Arabic text
            xsampa: X-SAMPA phonetic representation
            output_path: Path to save MP3 file
            voice_id: Polly voice ('Zeina' for MSA, 'Hala' for Gulf)
            engine: 'neural' (better quality) or 'standard'

        Returns:
            Tuple of (success: bool, message: str)

        Notes:
            - If neural engine fails (voice doesn't support it), automatically
              retries with standard engine
            - Some Polly voices only support standard engine

        Example:
            >>> success, msg = polly.generate_audio("صباح", "saba:H", "output.mp3")
            >>> print(msg)
            'Audio generated successfully: output.mp3 (standard engine)'
        """
        if not self.polly_client:
            return False, "Polly client not initialized"

        # Convert to SSML
        ssml = self.xsampa_to_ssml(xsampa, text)

        # Try with requested engine first
        engines_to_try = [engine]

        # If neural was requested but fails, fallback to standard
        if engine == 'neural':
            engines_to_try.append('standard')

        last_error = None

        for current_engine in engines_to_try:
            try:
                # Call Polly API
                response = self.polly_client.synthesize_speech(
                    Text=ssml,
                    TextType='ssml',
                    OutputFormat='mp3',
                    VoiceId=voice_id,
                    Engine=current_engine
                )

                # Save audio file
                with open(output_path, 'wb') as f:
                    f.write(response['AudioStream'].read())

                engine_note = f" ({current_engine} engine)"
                return True, f"Audio generated successfully: {output_path}{engine_note}"

            except Exception as e:
                error_msg = str(e)
                last_error = error_msg

                # If this is a neural engine compatibility issue, try standard
                if current_engine == 'neural' and 'does not support the selected engine' in error_msg:
                    continue  # Try next engine

                # Otherwise, handle the error
                if "NoCredentialsError" in error_msg or "credentials" in error_msg.lower():
                    return False, "AWS credentials not configured. See docs/polly/AWS_SETUP_GUIDE.md"
                elif "AccessDenied" in error_msg:
                    return False, "IAM permissions insufficient. Need polly:SynthesizeSpeech permission"
                elif "Throttling" in error_msg or "Rate" in error_msg:
                    return False, "API rate limit exceeded. Wait and retry"
                elif "NetworkingError" in error_msg or "Connection" in error_msg:
                    return False, f"Network error: {error_msg}"
                elif "does not support" in error_msg:
                    # Voice doesn't support this engine, continue to next
                    continue
                else:
                    return False, f"Polly error: {error_msg}"

        # All engines failed
        if last_error:
            return False, f"Polly error: {last_error}"
        else:
            return False, "Polly audio generation failed with unknown error"
