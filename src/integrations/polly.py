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
            xsampa: X-SAMPA phonetic transcription (can be empty)
            text: Original Arabic text
        
        Returns:
            SSML string with phoneme tags for Polly (or plain text if X-SAMPA empty)
        
        Example:
            >>> polly.xsampa_to_ssml("saba:H", "صباح")
            '<speak><phoneme alphabet="x-sampa" ph="saba:H">صباح</phoneme></speak>'
            >>> polly.xsampa_to_ssml("", "صباح")
            '<speak>صباح</speak>'
        """
        # If X-SAMPA is empty, use plain text (Polly's built-in pronunciation)
        if not xsampa or xsampa.strip() == "":
            return f'<speak>{text}</speak>'
        # Otherwise use phoneme control
        return f'<speak><phoneme alphabet="x-sampa" ph="{xsampa}">{text}</phoneme></speak>'
    
    def generate_audio(
        self,
        text: str,
        xsampa: str,
        output_path: str,
        voice_id: str = 'Zeina',
        engine: str = 'neural'
    ) -> Tuple[bool, str]:
        """
        Generate audio using Amazon Polly
        
        Args:
            text: Original Arabic text
            xsampa: X-SAMPA phonetic representation
            output_path: Path to save MP3 file
            voice_id: Polly voice ('Zeina' for MSA, 'Hala' for Gulf)
            engine: 'neural' (better quality) or 'standard'
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> success, msg = polly.generate_audio("صباح", "saba:H", "output.mp3")
            >>> print(msg)
            'Audio generated successfully: output.mp3'
        """
        if not self.polly_client:
            return False, "Polly client not initialized"
        
        try:
            # Convert to SSML
            ssml = self.xsampa_to_ssml(xsampa, text)
            
            # Call Polly API
            response = self.polly_client.synthesize_speech(
                Text=ssml,
                TextType='ssml',
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine=engine
            )
            
            # Save audio file
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            return True, f"Audio generated successfully: {output_path}"
            
        except Exception as e:
            error_msg = str(e)
            if "NoCredentialsError" in error_msg or "credentials" in error_msg.lower():
                return False, "AWS credentials not configured. See docs/polly/AWS_SETUP_GUIDE.md"
            elif "AccessDenied" in error_msg:
                return False, "IAM permissions insufficient. Need polly:SynthesizeSpeech permission"
            elif "Throttling" in error_msg or "Rate" in error_msg:
                return False, "API rate limit exceeded. Wait and retry"
            elif "NetworkingError" in error_msg or "Connection" in error_msg:
                return False, f"Network error: {error_msg}"
            else:
                return False, f"Polly error: {error_msg}"
