#!/usr/bin/env python3
"""
Multi-Engine TTS Comparison

Compare Azure vs Polly vs eSpeak on the same content.
Generates side-by-side audio files for blind testing.
"""
import sys
import random
from pathlib import Path
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main import ArabicTTS
from tools.azure_tts.azure_integration import AzureTTS

# Check if Polly is available
try:
    from src.integrations.polly import PollyTTS
    POLLY_AVAILABLE = True
except Exception:
    POLLY_AVAILABLE = False

# Check if eSpeak is available
try:
    from src.integrations.espeak import ESpeakTTS
    ESPEAK_AVAILABLE = True
except Exception:
    ESPEAK_AVAILABLE = False


class EngineComparator:
    """Compare multiple TTS engines on the same content"""

    def __init__(self):
        """Initialize all available TTS engines"""
        print("Initializing TTS engines...")

        # Initialize Arabic TTS pipeline (required for all engines)
        self.arabic_tts = ArabicTTS()
        print("✓ Arabic TTS pipeline initialized")

        # Initialize engines
        self.engines = {}

        # Azure
        try:
            self.engines['azure'] = AzureTTS()
            print("✓ Azure TTS initialized")
        except Exception as e:
            print(f"✗ Azure TTS not available: {e}")

        # Polly
        if POLLY_AVAILABLE:
            try:
                self.engines['polly'] = PollyTTS()
                print("✓ AWS Polly initialized")
            except Exception as e:
                print(f"✗ AWS Polly not available: {e}")
        else:
            print("⚠ AWS Polly not installed")

        # eSpeak
        if ESPEAK_AVAILABLE:
            try:
                self.engines['espeak'] = ESpeakTTS()
                print("✓ eSpeak NG initialized")
            except Exception as e:
                print(f"✗ eSpeak NG not available: {e}")
        else:
            print("⚠ eSpeak NG not installed")

        if not self.engines:
            print("✗ No TTS engines available!")
            sys.exit(1)

        # Output directory
        self.output_dir = Path(__file__).parent / "outputs" / "comparison"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_text(self, text: str, dialect: str = 'EG') -> Tuple[str, str, str]:
        """
        Process text through pipeline

        Returns:
            Tuple of (processed_text, xsampa, ipa)
        """
        result = self.arabic_tts.synthesize(
            text,
            dialect=dialect,
            output_format='none'
        )

        # Extract phonetic representations
        xsampa_parts = []
        ipa_parts = []
        for syl in result.get('syllables', []):
            xsampa_parts.append(syl.get('xsampa', ''))
            ipa_parts.append(syl.get('ipa', ''))

        xsampa = ''.join(xsampa_parts)
        ipa = ''.join(ipa_parts)

        return text, xsampa, ipa

    def compare_simple_phrase(self, text: str, test_name: str):
        """
        Compare engines on a simple phrase

        Args:
            text: Arabic text
            test_name: Name for output files
        """
        print(f"\n{'=' * 70}")
        print(f"Comparing engines: {test_name}")
        print(f"{'=' * 70}")
        print(f"Text: {text}")

        # Process text
        processed_text, xsampa, ipa = self.process_text(text)
        print(f"X-SAMPA: {xsampa}")
        print(f"IPA: /{ipa}/")

        results = []

        # Azure (plain text)
        if 'azure' in self.engines:
            print("\n[Azure - Plain Text]")
            output = self.output_dir / f"{test_name}_azure_plain.mp3"
            success, msg = self.engines['azure'].generate_audio(
                processed_text, '', str(output),
                voice='ar-EG-ShakirNeural', use_phonetic=False
            )
            print(f"  {'✓' if success else '✗'} {msg}")
            if success:
                results.append(('azure_plain', str(output)))

        # Azure (X-SAMPA)
        if 'azure' in self.engines:
            print("\n[Azure - X-SAMPA]")
            output = self.output_dir / f"{test_name}_azure_xsampa.mp3"
            success, msg = self.engines['azure'].generate_audio(
                processed_text, xsampa, str(output),
                voice='ar-EG-ShakirNeural', use_phonetic=True
            )
            print(f"  {'✓' if success else '✗'} {msg}")
            if success:
                results.append(('azure_xsampa', str(output)))

        # Polly (plain text only - X-SAMPA not supported for Arabic)
        if 'polly' in self.engines:
            print("\n[AWS Polly - Plain Text]")
            output = self.output_dir / f"{test_name}_polly_plain.mp3"
            success, msg = self.engines['polly'].generate_audio(
                processed_text, xsampa, str(output),
                voice_id='Zeina', engine='neural'
            )
            print(f"  {'✓' if success else '✗'} {msg}")
            if success:
                results.append(('polly_plain', str(output)))

        # eSpeak (IPA)
        if 'espeak' in self.engines:
            print("\n[eSpeak NG - IPA]")
            output = self.output_dir / f"{test_name}_espeak_ipa.wav"
            success, msg = self.engines['espeak'].generate_audio(
                ipa, str(output)
            )
            print(f"  {'✓' if success else '✗'} {msg}")
            if success:
                results.append(('espeak_ipa', str(output)))

        return results

    def generate_blind_test(self, results: List[Tuple[str, str]], test_name: str):
        """
        Generate randomized playlist for blind testing

        Args:
            results: List of (engine_name, file_path) tuples
            test_name: Name for the test
        """
        # Randomize order
        randomized = results.copy()
        random.shuffle(randomized)

        # Create blind test manifest
        manifest_path = self.output_dir / f"{test_name}_blind_test.txt"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(f"Blind Test: {test_name}\n")
            f.write("=" * 70 + "\n\n")
            f.write("Listen to each sample and rate:\n")
            f.write("  1. Voice Quality (1-5): Naturalness, prosody, emotion\n")
            f.write("  2. Pronunciation (1-5): Accuracy, clarity\n")
            f.write("  3. Overall (1-5): Would you listen to a full audiobook?\n\n")

            for i, (engine, path) in enumerate(randomized, 1):
                f.write(f"Sample {i}: {Path(path).name}\n")
                f.write(f"  Voice Quality: ___/5\n")
                f.write(f"  Pronunciation: ___/5\n")
                f.write(f"  Overall:       ___/5\n")
                f.write(f"  Notes: _________________________________\n\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("ANSWER KEY (don't look until after rating!):\n")
            f.write("=" * 70 + "\n\n")

            for i, (engine, path) in enumerate(randomized, 1):
                f.write(f"Sample {i}: {engine}\n")

        print(f"\n✓ Blind test manifest: {manifest_path}")

    def run_comparison_suite(self):
        """Run standard comparison tests"""
        print("=" * 70)
        print("MULTI-ENGINE TTS COMPARISON")
        print("=" * 70)
        print()
        print(f"Available engines: {', '.join(self.engines.keys())}")
        print()

        # Test 1: Simple greeting
        results1 = self.compare_simple_phrase(
            "السلام عليكم ورحمة الله وبركاته",
            "test1_greeting"
        )
        self.generate_blind_test(results1, "test1_greeting")

        # Test 2: Phonologically complex
        results2 = self.compare_simple_phrase(
            "صباح الخير، الشمس ساطعة اليوم",
            "test2_complex"
        )
        self.generate_blind_test(results2, "test2_complex")

        # Test 3: Rare words
        results3 = self.compare_simple_phrase(
            "المكتبة الوطنية تحتوي على مخطوطات تاريخية",
            "test3_rare_words"
        )
        self.generate_blind_test(results3, "test3_rare_words")

        print("\n" + "=" * 70)
        print("COMPARISON COMPLETE")
        print("=" * 70)
        print(f"\nOutput directory: {self.output_dir}")
        print("\nNext steps:")
        print("  1. Use blind test manifests to rate samples")
        print("  2. Compare scores across engines")
        print("  3. Determine which engine/mode is best")

    def quick_test(self, text: str):
        """Quick test of all engines on given text"""
        print(f"\nQuick test: {text}")
        self.compare_simple_phrase(text, "quick_test")


def main():
    """Main entry point"""
    comparator = EngineComparator()

    if len(sys.argv) > 1:
        # Quick test mode with custom text
        text = ' '.join(sys.argv[1:])
        comparator.quick_test(text)
    else:
        # Full comparison suite
        comparator.run_comparison_suite()


if __name__ == "__main__":
    main()
