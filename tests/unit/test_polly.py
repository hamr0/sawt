"""
Unit tests for Amazon Polly Integration
Tests PollyTTS wrapper class functionality with mocked boto3 calls
Target: 100% coverage of Polly integration workflow
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.integrations.polly import PollyTTS


class TestPollyInitialization:
    """Test PollyTTS initialization and error handling"""
    
    @patch('src.integrations.polly.boto3')
    def test_initialization_success(self, mock_boto3):
        """Test successful initialization with default region"""
        mock_client = Mock()
        mock_boto3.client.return_value = mock_client
        
        polly = PollyTTS()
        
        assert polly.region == 'us-east-1'
        assert polly.polly_client == mock_client
        mock_boto3.client.assert_called_once_with('polly', region_name='us-east-1')
    
    @patch('src.integrations.polly.boto3')
    def test_initialization_custom_region(self, mock_boto3):
        """Test initialization with custom region"""
        mock_client = Mock()
        mock_boto3.client.return_value = mock_client
        
        polly = PollyTTS(region='us-west-2')
        
        assert polly.region == 'us-west-2'
        mock_boto3.client.assert_called_once_with('polly', region_name='us-west-2')
    
    def test_initialization_boto3_not_installed(self):
        """Test error when boto3 is not installed"""
        with patch('src.integrations.polly.boto3', None):
            with pytest.raises(ImportError) as exc_info:
                PollyTTS()
            
            assert "boto3 is not installed" in str(exc_info.value)
            assert "pip install boto3" in str(exc_info.value)
    
    @patch('src.integrations.polly.boto3')
    def test_initialization_credentials_not_configured(self, mock_boto3):
        """Test error when AWS credentials are not configured"""
        mock_boto3.client.side_effect = Exception("Unable to locate credentials")
        
        with pytest.raises(RuntimeError) as exc_info:
            PollyTTS()
        
        assert "Failed to initialize Polly client" in str(exc_info.value)
        assert "configure AWS credentials" in str(exc_info.value)
        assert "AWS_SETUP_GUIDE.md" in str(exc_info.value)


class TestXSAMPAToSSML:
    """Test X-SAMPA to SSML conversion"""
    
    @patch('src.integrations.polly.boto3')
    def test_xsampa_to_ssml_basic(self, mock_boto3):
        """Test basic X-SAMPA to SSML conversion"""
        mock_boto3.client.return_value = Mock()
        polly = PollyTTS()
        
        result = polly.xsampa_to_ssml("saba:H", "صباح")
        
        assert result == '<speak><phoneme alphabet="x-sampa" ph="saba:H">صباح</phoneme></speak>'
    
    @patch('src.integrations.polly.boto3')
    def test_xsampa_to_ssml_complex(self, mock_boto3):
        """Test complex X-SAMPA with emphatic consonants"""
        mock_boto3.client.return_value = Mock()
        polly = PollyTTS()
        
        result = polly.xsampa_to_ssml("s_?Aba:X\\", "صَباح")
        
        assert '<speak>' in result
        assert 'alphabet="x-sampa"' in result
        assert 'ph="s_?Aba:X\\"' in result
        assert "صَباح" in result
        assert '</speak>' in result
    
    @patch('src.integrations.polly.boto3')
    def test_xsampa_to_ssml_empty_text(self, mock_boto3):
        """Test SSML conversion with empty text - should use plain text"""
        mock_boto3.client.return_value = Mock()
        polly = PollyTTS()
        
        # Empty X-SAMPA should return plain text SSML (no phoneme tag)
        result = polly.xsampa_to_ssml("", "")
        assert result == '<speak></speak>'
        
        # Empty X-SAMPA with text should return text without phoneme tag
        result = polly.xsampa_to_ssml("", "صباح")
        assert result == '<speak>صباح</speak>'


class TestGenerateAudio:
    """Test audio generation with Polly"""
    
    @patch('src.integrations.polly.boto3')
    def test_generate_audio_success(self, mock_boto3):
        """Test successful audio generation"""
        # Mock Polly client
        mock_client = Mock()
        mock_response = {
            'AudioStream': Mock(read=Mock(return_value=b'fake_audio_data'))
        }
        mock_client.synthesize_speech.return_value = mock_response
        mock_boto3.client.return_value = mock_client
        
        polly = PollyTTS()
        
        # Mock file writing
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            success, message = polly.generate_audio(
                text="صباح",
                xsampa="saba:H",
                output_path="test_output.mp3"
            )
        
        assert success is True
        assert "Audio generated successfully" in message
        assert "test_output.mp3" in message
        
        # Verify Polly API was called correctly
        mock_client.synthesize_speech.assert_called_once()
        call_args = mock_client.synthesize_speech.call_args[1]
        assert call_args['TextType'] == 'ssml'
        assert call_args['OutputFormat'] == 'mp3'
        assert call_args['VoiceId'] == 'Zeina'
        assert call_args['Engine'] == 'neural'
        assert '<phoneme alphabet="x-sampa"' in call_args['Text']
    
    @patch('src.integrations.polly.boto3')
    def test_generate_audio_with_hala_voice(self, mock_boto3):
        """Test audio generation with Hala voice (Gulf Arabic)"""
        mock_client = Mock()
        mock_response = {'AudioStream': Mock(read=Mock(return_value=b'fake_audio'))}
        mock_client.synthesize_speech.return_value = mock_response
        mock_boto3.client.return_value = mock_client
        
        polly = PollyTTS()
        
        with patch('builtins.open', create=True):
            success, message = polly.generate_audio(
                text="مرحبا",
                xsampa="marHaba",
                output_path="test.mp3",
                voice_id='Hala'
            )
        
        assert success is True
        call_args = mock_client.synthesize_speech.call_args[1]
        assert call_args['VoiceId'] == 'Hala'
    
    @patch('src.integrations.polly.boto3')
    def test_generate_audio_with_standard_engine(self, mock_boto3):
        """Test audio generation with standard engine"""
        mock_client = Mock()
        mock_response = {'AudioStream': Mock(read=Mock(return_value=b'fake_audio'))}
        mock_client.synthesize_speech.return_value = mock_response
        mock_boto3.client.return_value = mock_client
        
        polly = PollyTTS()
        
        with patch('builtins.open', create=True):
            success, message = polly.generate_audio(
                text="مرحبا",
                xsampa="marHaba",
                output_path="test.mp3",
                engine='standard'
            )
        
        assert success is True
        call_args = mock_client.synthesize_speech.call_args[1]
        assert call_args['Engine'] == 'standard'
    
    @patch('src.integrations.polly.boto3')
    def test_generate_audio_client_not_initialized(self, mock_boto3):
        """Test error when Polly client is not initialized"""
        mock_boto3.client.return_value = Mock()
        polly = PollyTTS()
        polly.polly_client = None
        
        success, message = polly.generate_audio(
            text="test",
            xsampa="test",
            output_path="test.mp3"
        )
        
        assert success is False
        assert "Polly client not initialized" in message


class TestErrorHandling:
    """Test comprehensive error handling scenarios"""
    
    @patch('src.integrations.polly.boto3')
    def test_error_no_credentials(self, mock_boto3):
        """Test error handling for missing credentials"""
        mock_client = Mock()
        mock_client.synthesize_speech.side_effect = Exception("NoCredentialsError: Unable to locate credentials")
        mock_boto3.client.return_value = mock_client
        
        polly = PollyTTS()
        success, message = polly.generate_audio("test", "test", "test.mp3")
        
        assert success is False
        assert "AWS credentials not configured" in message
        assert "AWS_SETUP_GUIDE.md" in message
    
    @patch('src.integrations.polly.boto3')
    def test_error_access_denied(self, mock_boto3):
        """Test error handling for insufficient IAM permissions"""
        mock_client = Mock()
        mock_client.synthesize_speech.side_effect = Exception("AccessDenied: User not authorized")
        mock_boto3.client.return_value = mock_client
        
        polly = PollyTTS()
        success, message = polly.generate_audio("test", "test", "test.mp3")
        
        assert success is False
        assert "IAM permissions insufficient" in message
        assert "polly:SynthesizeSpeech" in message
    
    @patch('src.integrations.polly.boto3')
    def test_error_rate_limit(self, mock_boto3):
        """Test error handling for API rate limiting"""
        mock_client = Mock()
        mock_client.synthesize_speech.side_effect = Exception("Throttling: Rate exceeded")
        mock_boto3.client.return_value = mock_client
        
        polly = PollyTTS()
        success, message = polly.generate_audio("test", "test", "test.mp3")
        
        assert success is False
        assert "API rate limit exceeded" in message
        assert "Wait and retry" in message
    
    @patch('src.integrations.polly.boto3')
    def test_error_network(self, mock_boto3):
        """Test error handling for network failures"""
        mock_client = Mock()
        mock_client.synthesize_speech.side_effect = Exception("NetworkingError: Connection timeout")
        mock_boto3.client.return_value = mock_client
        
        polly = PollyTTS()
        success, message = polly.generate_audio("test", "test", "test.mp3")
        
        assert success is False
        assert "Network error" in message
    
    @patch('src.integrations.polly.boto3')
    def test_error_generic(self, mock_boto3):
        """Test error handling for generic Polly errors"""
        mock_client = Mock()
        mock_client.synthesize_speech.side_effect = Exception("Unknown Polly error")
        mock_boto3.client.return_value = mock_client
        
        polly = PollyTTS()
        success, message = polly.generate_audio("test", "test", "test.mp3")
        
        assert success is False
        assert "Polly error" in message
        assert "Unknown Polly error" in message


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""
    
    @patch('src.integrations.polly.boto3')
    def test_full_workflow(self, mock_boto3):
        """Test complete workflow from initialization to audio generation"""
        # Setup mock
        mock_client = Mock()
        mock_response = {'AudioStream': Mock(read=Mock(return_value=b'mp3_data'))}
        mock_client.synthesize_speech.return_value = mock_response
        mock_boto3.client.return_value = mock_client
        
        # Initialize
        polly = PollyTTS(region='us-east-1')
        assert polly.region == 'us-east-1'
        
        # Convert X-SAMPA to SSML
        ssml = polly.xsampa_to_ssml("marHaba", "مرحبا")
        assert "x-sampa" in ssml
        assert "مرحبا" in ssml
        
        # Generate audio
        with patch('builtins.open', create=True):
            success, message = polly.generate_audio(
                text="مرحبا",
                xsampa="marHaba",
                output_path="greeting.mp3",
                voice_id='Zeina',
                engine='neural'
            )
        
        assert success is True
        assert "greeting.mp3" in message
    
    @patch('src.integrations.polly.boto3')
    def test_multiple_audio_generations(self, mock_boto3):
        """Test generating multiple audio files in sequence"""
        mock_client = Mock()
        mock_response = {'AudioStream': Mock(read=Mock(return_value=b'audio'))}
        mock_client.synthesize_speech.return_value = mock_response
        mock_boto3.client.return_value = mock_client
        
        polly = PollyTTS()
        
        test_cases = [
            ("صباح", "saba:H", "test1.mp3"),
            ("مساء", "masa:?", "test2.mp3"),
            ("السلام", "?assala:m", "test3.mp3"),
        ]
        
        with patch('builtins.open', create=True):
            for text, xsampa, output in test_cases:
                success, message = polly.generate_audio(text, xsampa, output)
                assert success is True
                assert output in message
        
        assert mock_client.synthesize_speech.call_count == 3


# Mark all tests for unit test category
pytestmark = pytest.mark.unit
