"""
eSpeak NG Integration for Arabic TTS
Wrapper for eSpeak NG text-to-speech engine with IPA input support
Includes IPA to X-SAMPA conversion for better eSpeak compatibility
"""
import subprocess
import os
from pathlib import Path
from typing import Optional, Tuple, Dict


class ESpeakTTS:
    """
    Wrapper class for eSpeak NG text-to-speech engine
    
    Supports IPA input for Arabic speech synthesis.
    eSpeak NG must be installed on the system.
    """
    
    def __init__(self, voice: str = "ar", verify_installation: bool = True):
        """
        Initialize eSpeak TTS wrapper
        
        Args:
            voice: eSpeak voice code (default: "ar" for Arabic)
            verify_installation: Check if eSpeak NG is installed
        
        Raises:
            RuntimeError: If eSpeak NG is not installed
        """
        self.voice = voice
        self.espeak_command = "espeak-ng"
        
        # IPA to X-SAMPA conversion map for Arabic phonemes
        self._build_ipa_to_xsampa_map()
        
        if verify_installation:
            if not self.is_espeak_installed():
                raise RuntimeError(
                    "eSpeak NG is not installed. Please install it:\n"
                    "Ubuntu/Debian: sudo apt install espeak-ng\n"
                    "MacOS: brew install espeak-ng\n"
                    "Windows: Download from https://github.com/espeak-ng/espeak-ng/releases"
                )
    
    def _build_ipa_to_xsampa_map(self):
        """Build IPA to X-SAMPA conversion mapping for Arabic phonemes"""
        self._ipa_xsampa_map: Dict[str, str] = {
            # Consonants
            'b': 'b',
            't': 't',
            'tˁ': 't_?',  # Emphatic t
            'd': 'd',
            'dˁ': 'd_?',  # Emphatic d
            'k': 'k',
            'q': 'q',
            'qˁ': 'q_?',  # Emphatic q
            'ʔ': '?',     # Glottal stop
            'f': 'f',
            'θ': 'T',     # th as in "think"
            'ð': 'D',     # th as in "this"
            'ðˁ': 'D_?',  # Emphatic dh
            's': 's',
            'sˁ': 's_?',  # Emphatic s
            'z': 'z',
            'ʃ': 'S',     # sh
            'ʒ': 'Z',     # zh
            'x': 'x',     # kh
            'ɣ': 'G',     # gh
            'ħ': 'X\\',   # voiceless pharyngeal
            'ʕ': '?\\',   # voiced pharyngeal
            'h': 'h',
            'm': 'm',
            'n': 'n',
            'l': 'l',
            'l~': 'l',    # Velarized l
            'r': 'r',
            'ɾ': '4',     # Flap r
            'w': 'w',
            'j': 'j',
            
            # Vowels
            'a': 'a',
            'ɑ': 'A',     # Back a (pharyngealized)
            'i': 'i',
            'ɪ': 'I',     # Lowered i (pharyngealized)
            'u': 'u',
            'ʊ': 'U',     # Lowered u (pharyngealized)
            
            # Long vowels
            'aː': 'a:',
            'ɑː': 'A:',
            'iː': 'i:',
            'ɪː': 'I:',
            'uː': 'u:',
            'ʊː': 'U:',
            
            # Diphthongs
            'aj': 'aj',
            'aw': 'aw',
            
            # Markers
            'ː': ':',     # Length marker
            'ˁ': '_?',    # Pharyngealization marker
        }
    
    def ipa_to_xsampa(self, ipa: str) -> str:
        """
        Convert IPA string to X-SAMPA notation
        
        Args:
            ipa: IPA transcription string
        
        Returns:
            X-SAMPA transcription string
        
        Example:
            >>> espeak.ipa_to_xsampa("sˁɑbɑːħ")
            's_?Aba:X\\'
        """
        xsampa = ipa
        
        # Sort by length (longest first) to match multi-character sequences first
        sorted_ipa = sorted(self._ipa_xsampa_map.items(), key=lambda x: len(x[0]), reverse=True)
        
        for ipa_char, xsampa_char in sorted_ipa:
            xsampa = xsampa.replace(ipa_char, xsampa_char)
        
        return xsampa
    
    def is_espeak_installed(self) -> bool:
        """
        Check if eSpeak NG is installed on the system
        
        Returns:
            True if installed, False otherwise
        """
        try:
            result = subprocess.run(
                [self.espeak_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def get_espeak_version(self) -> Optional[str]:
        """
        Get eSpeak NG version
        
        Returns:
            Version string or None if not installed
        """
        try:
            result = subprocess.run(
                [self.espeak_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse version from output
                # Example: "eSpeak NG text-to-speech: 1.50"
                lines = result.stdout.strip().split('\n')
                if lines:
                    return lines[0]
            return None
        except (subprocess.SubprocessError, FileNotFoundError):
            return None
    
    def generate_audio(
        self,
        ipa: str,
        output_path: str,
        speed: int = 150,
        pitch: int = 50,
        amplitude: int = 100
    ) -> Tuple[bool, str]:
        """
        Generate audio from IPA string using eSpeak NG
        
        Args:
            ipa: IPA transcription string
            output_path: Path to save WAV file
            speed: Speech speed (words per minute, default: 150)
            pitch: Pitch adjustment 0-99 (default: 50)
            amplitude: Volume 0-200 (default: 100)
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            success, msg = espeak.generate_audio("sˁɑbɑːħ", "output.wav")
        """
        try:
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Build eSpeak command
            # Format: espeak-ng -v ar "[[IPA]]" -w output.wav
            command = [
                self.espeak_command,
                "-v", self.voice,
                f"[[{ipa}]]",  # IPA input format for eSpeak
                "-w", output_path,
                "-s", str(speed),
                "-p", str(pitch),
                "-a", str(amplitude)
            ]
            
            # Execute eSpeak
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, f"eSpeak NG failed: {error_msg}"
            
            # Verify audio file was created
            if not os.path.exists(output_path):
                return False, f"Audio file was not created: {output_path}"
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                return False, f"Audio file is empty: {output_path}"
            
            return True, f"Audio generated successfully: {output_path} ({file_size} bytes)"
        
        except subprocess.TimeoutExpired:
            return False, "eSpeak NG timed out (30s)"
        
        except Exception as e:
            return False, f"Error generating audio: {str(e)}"
    
    def generate_audio_from_text(
        self,
        text: str,
        output_path: str,
        speed: int = 150,
        pitch: int = 50,
        amplitude: int = 100
    ) -> Tuple[bool, str]:
        """
        Generate audio directly from Arabic text (not IPA)
        
        Args:
            text: Arabic text
            output_path: Path to save WAV file
            speed: Speech speed (words per minute)
            pitch: Pitch adjustment 0-99
            amplitude: Volume 0-200
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Build eSpeak command (without IPA brackets)
            command = [
                self.espeak_command,
                "-v", self.voice,
                text,
                "-w", output_path,
                "-s", str(speed),
                "-p", str(pitch),
                "-a", str(amplitude)
            ]
            
            # Execute eSpeak
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, f"eSpeak NG failed: {error_msg}"
            
            # Verify audio file was created
            if not os.path.exists(output_path):
                return False, f"Audio file was not created: {output_path}"
            
            file_size = os.path.getsize(output_path)
            return True, f"Audio generated: {output_path} ({file_size} bytes)"
        
        except subprocess.TimeoutExpired:
            return False, "eSpeak NG timed out (30s)"
        
        except Exception as e:
            return False, f"Error generating audio: {str(e)}"


if __name__ == "__main__":
    # Quick test
    print("Testing eSpeak NG Integration")
    print("=" * 70)
    
    # Initialize
    try:
        espeak = ESpeakTTS()
        print(f"✓ eSpeak NG initialized")
        print(f"  Version: {espeak.get_espeak_version()}")
        print(f"  Voice: {espeak.voice}")
    except RuntimeError as e:
        print(f"✗ Error: {e}")
        exit(1)
    
    # Test 1: Generate audio from Arabic text
    print("\nTest 1: Generate audio from Arabic text")
    print("-" * 70)
    text = "السلام عليكم"
    output = "/tmp/test_arabic.wav"
    success, msg = espeak.generate_audio_from_text(text, output)
    print(f"  Text: {text}")
    print(f"  Output: {output}")
    print(f"  Result: {'✓' if success else '✗'} {msg}")
    
    # Test 2: IPA to X-SAMPA conversion
    print("\nTest 2: IPA to X-SAMPA conversion")
    print("-" * 70)
    test_ipa_strings = [
        ("sˁɑbɑːħ", "صباح - morning"),
        ("tˁɑʕɑːm", "طعام - food"),
        ("ʃams", "شمس - sun"),
        ("qamar", "قمر - moon"),
        ("ʔakl", "أكل - ate"),
    ]
    
    for ipa, description in test_ipa_strings:
        xsampa = espeak.ipa_to_xsampa(ipa)
        print(f"  {description}")
        print(f"    IPA:     /{ipa}/")
        print(f"    X-SAMPA: [{xsampa}]")
    
    # Test 3: Generate audio from IPA
    print("\nTest 3: Generate audio from IPA")
    print("-" * 70)
    ipa = "sɑlɑːm"
    output = "/tmp/test_ipa.wav"
    success, msg = espeak.generate_audio(ipa, output)
    print(f"  IPA: /{ipa}/")
    print(f"  Output: {output}")
    print(f"  Result: {'✓' if success else '✗'} {msg}")
    
    print("\n" + "=" * 70)
    print("eSpeak integration test complete!")
