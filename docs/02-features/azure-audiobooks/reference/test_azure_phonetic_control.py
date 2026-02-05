#!/usr/bin/env python3
"""
Azure Speech Service Phonetic Control Test

Main test orchestrator for evaluating Azure TTS with X-SAMPA vs plain text.
Runs 5 comprehensive tests and generates comparison reports.
"""
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main import ArabicTTS
from tools.azure_tts.azure_integration import AzureTTS


class AzureTestOrchestrator:
    """Orchestrates Azure TTS testing with X-SAMPA vs plain text comparison"""

    def __init__(self):
        """Initialize TTS engines"""
        print("Initializing TTS engines...")

        # Initialize Arabic TTS pipeline
        try:
            self.arabic_tts = ArabicTTS()
            print("✓ Arabic TTS pipeline initialized")
        except Exception as e:
            print(f"✗ Error initializing Arabic TTS: {e}")
            sys.exit(1)

        # Initialize Azure TTS
        try:
            self.azure_tts = AzureTTS()
            print("✓ Azure TTS initialized")
        except Exception as e:
            print(f"✗ Error initializing Azure TTS: {e}")
            print("  Make sure AZURE_SPEECH_KEY environment variable is set")
            sys.exit(1)

        # Test results storage
        self.results = []

        # Output directory
        self.output_dir = Path(__file__).parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)

    def process_text_to_xsampa(self, text: str, dialect: str = 'EG') -> Tuple[str, str]:
        """
        Process Arabic text through pipeline to get X-SAMPA

        Args:
            text: Arabic text
            dialect: Dialect code (EG, MSA, etc.)

        Returns:
            Tuple of (processed_text, xsampa)
        """
        try:
            # Process text through pipeline
            result = self.arabic_tts.synthesize(
                text,
                dialect=dialect,
                output_format='none'  # Don't generate audio yet
            )

            # Extract X-SAMPA
            if 'syllables' in result:
                xsampa_parts = []
                for syl in result['syllables']:
                    xsampa_parts.append(syl.get('xsampa', ''))
                xsampa = ''.join(xsampa_parts)
            else:
                xsampa = ''

            return text, xsampa

        except Exception as e:
            print(f"  Warning: Error processing text: {e}")
            return text, ''

    def test_sample1_phonological(self):
        """Test 1: Phonological Features Showcase"""
        print("\n" + "=" * 70)
        print("TEST 1: Phonological Features Showcase")
        print("=" * 70)

        sample_path = Path(__file__).parent / "samples" / "sample1_phonological.txt"
        if not sample_path.exists():
            print(f"✗ Sample file not found: {sample_path}")
            print("  Run generate_test_samples.py first")
            return

        # Read sample text
        with open(sample_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract Arabic sentences (skip comment lines)
        sentences = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('='):
                # Check if it's Arabic text
                if any('\u0600' <= c <= '\u06FF' for c in line):
                    sentences.append(line)

        # Combine into single text for processing
        full_text = ' '.join(sentences[:10])  # Use first 10 sentences for 5-min sample

        print(f"Processing {len(full_text)} characters...")

        # Process to get X-SAMPA
        processed_text, xsampa = self.process_text_to_xsampa(full_text, dialect='EG')

        # Generate audio: Plain text version
        print("\nGenerating Azure audio (plain text)...")
        output_plain = self.output_dir / "sample1_plain.mp3"
        success, msg = self.azure_tts.generate_audio(
            processed_text,
            '',
            str(output_plain),
            voice='ar-EG-ShakirNeural',
            use_phonetic=False
        )
        print(f"  {'✓' if success else '✗'} {msg}")

        # Generate audio: X-SAMPA version
        print("\nGenerating Azure audio (X-SAMPA)...")
        output_xsampa = self.output_dir / "sample1_xsampa.mp3"
        success, msg = self.azure_tts.generate_audio(
            processed_text,
            xsampa,
            str(output_xsampa),
            voice='ar-EG-ShakirNeural',
            use_phonetic=True
        )
        print(f"  {'✓' if success else '✗'} {msg}")

        # Store results
        self.results.append({
            'test': 'Sample 1: Phonological Features',
            'text_length': len(full_text),
            'xsampa_length': len(xsampa),
            'output_plain': str(output_plain),
            'output_xsampa': str(output_xsampa)
        })

    def test_sample2_rare_words(self):
        """Test 2: Rare and Ambiguous Words"""
        print("\n" + "=" * 70)
        print("TEST 2: Rare and Ambiguous Words")
        print("=" * 70)

        sample_path = Path(__file__).parent / "samples" / "sample2_rare_words.txt"
        if not sample_path.exists():
            print(f"✗ Sample file not found: {sample_path}")
            return

        # Read sample text
        with open(sample_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract Arabic sentences
        sentences = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('='):
                if any('\u0600' <= c <= '\u06FF' for c in line):
                    sentences.append(line)

        full_text = ' '.join(sentences[:15])

        print(f"Processing {len(full_text)} characters...")

        # Process to get X-SAMPA
        processed_text, xsampa = self.process_text_to_xsampa(full_text, dialect='EG')

        # Generate both versions
        output_plain = self.output_dir / "sample2_plain.mp3"
        print("\nGenerating plain text version...")
        self.azure_tts.generate_audio(processed_text, '', str(output_plain),
                                       voice='ar-EG-ShakirNeural', use_phonetic=False)

        output_xsampa = self.output_dir / "sample2_xsampa.mp3"
        print("Generating X-SAMPA version...")
        self.azure_tts.generate_audio(processed_text, xsampa, str(output_xsampa),
                                       voice='ar-EG-ShakirNeural', use_phonetic=True)

        self.results.append({
            'test': 'Sample 2: Rare Words',
            'text_length': len(full_text),
            'output_plain': str(output_plain),
            'output_xsampa': str(output_xsampa)
        })

    def test_sample3_multidialect(self):
        """Test 3: Multi-Dialect Consistency"""
        print("\n" + "=" * 70)
        print("TEST 3: Multi-Dialect Consistency")
        print("=" * 70)

        sample_path = Path(__file__).parent / "samples" / "sample3_multidialect.txt"
        if not sample_path.exists():
            print(f"✗ Sample file not found: {sample_path}")
            return

        # Read sample text
        with open(sample_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract sections for each dialect
        sections = content.split('## VERSION')

        voices = [
            ('ar-SA-ZariyahNeural', 'MSA', 'MSA'),
            ('ar-EG-ShakirNeural', 'EG', 'Egyptian'),
            ('ar-AE-FatimaNeural', 'EG', 'Gulf')  # Use EG processing, Gulf voice
        ]

        for i, (voice, dialect_code, dialect_name) in enumerate(voices, 1):
            print(f"\nDialect {i}: {dialect_name}")

            # Extract Arabic text for this section
            if i < len(sections):
                section = sections[i]
                sentences = []
                for line in section.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('='):
                        if any('\u0600' <= c <= '\u06FF' for c in line):
                            sentences.append(line)

                full_text = ' '.join(sentences[:5])

                # Process
                processed_text, xsampa = self.process_text_to_xsampa(full_text, dialect=dialect_code)

                # Generate both versions
                output_plain = self.output_dir / f"sample3_{dialect_name.lower()}_plain.mp3"
                output_xsampa = self.output_dir / f"sample3_{dialect_name.lower()}_xsampa.mp3"

                print(f"  Generating {dialect_name} plain text...")
                self.azure_tts.generate_audio(processed_text, '', str(output_plain),
                                               voice=voice, use_phonetic=False)

                print(f"  Generating {dialect_name} X-SAMPA...")
                self.azure_tts.generate_audio(processed_text, xsampa, str(output_xsampa),
                                               voice=voice, use_phonetic=True)

    def test_sample4_dialogue(self):
        """Test 4: Multi-Voice Character Dialogue"""
        print("\n" + "=" * 70)
        print("TEST 4: Multi-Voice Character Dialogue")
        print("=" * 70)

        sample_path = Path(__file__).parent / "samples" / "sample4_dialogue.txt"
        if not sample_path.exists():
            print(f"✗ Sample file not found: {sample_path}")
            return

        # Read dialogue
        with open(sample_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse dialogue
        dialogue_segments = []
        voice_map = {
            'NARRATOR': 'ar-EG-SalmaNeural',
            'AHMED': 'ar-EG-ShakirNeural',
            'FATIMA': 'ar-SA-HamedNeural'
        }

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('[') and ']' in line:
                # Parse [CHARACTER] text
                char_end = line.index(']')
                character = line[1:char_end]
                text = line[char_end + 1:].strip()

                if character in voice_map and any('\u0600' <= c <= '\u06FF' for c in text):
                    # Process text
                    processed_text, xsampa = self.process_text_to_xsampa(text, dialect='EG')

                    dialogue_segments.append({
                        'text': processed_text,
                        'xsampa': xsampa,
                        'voice': voice_map[character],
                        'character': character
                    })

        # Take first 15 segments for 5-minute sample
        dialogue_segments = dialogue_segments[:15]

        print(f"Processing {len(dialogue_segments)} dialogue segments...")

        # Generate plain text version (multi-voice)
        print("\nGenerating multi-voice audio (plain text)...")
        output_plain = self.output_dir / "sample4_dialogue_plain.mp3"
        plain_segments = [{'text': s['text'], 'voice': s['voice']} for s in dialogue_segments]
        self.azure_tts.generate_audio_with_voices(plain_segments, str(output_plain))

        # Generate X-SAMPA version (multi-voice)
        print("Generating multi-voice audio (X-SAMPA)...")
        output_xsampa = self.output_dir / "sample4_dialogue_xsampa.mp3"
        self.azure_tts.generate_audio_with_voices(dialogue_segments, str(output_xsampa))

        self.results.append({
            'test': 'Sample 4: Multi-Voice Dialogue',
            'segments': len(dialogue_segments),
            'output_plain': str(output_plain),
            'output_xsampa': str(output_xsampa)
        })

    def test_sample5_chapter(self):
        """Test 5: Long-Form Audiobook Chapter"""
        print("\n" + "=" * 70)
        print("TEST 5: Long-Form Audiobook Chapter")
        print("=" * 70)

        sample_path = Path(__file__).parent / "samples" / "sample5_chapter.txt"
        if not sample_path.exists():
            print(f"✗ Sample file not found: {sample_path}")
            return

        # Read chapter
        with open(sample_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract Arabic sentences
        sentences = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('='):
                if any('\u0600' <= c <= '\u06FF' for c in line):
                    sentences.append(line)

        # Use first portion for 5-minute sample
        full_text = ' '.join(sentences[:20])

        print(f"Processing chapter ({len(full_text)} characters)...")

        # Process
        processed_text, xsampa = self.process_text_to_xsampa(full_text, dialect='EG')

        # Generate both versions
        print("\nGenerating chapter audio (plain text)...")
        output_plain = self.output_dir / "sample5_chapter_plain.mp3"
        self.azure_tts.generate_audio(processed_text, '', str(output_plain),
                                       voice='ar-EG-ShakirNeural', use_phonetic=False)

        print("Generating chapter audio (X-SAMPA)...")
        output_xsampa = self.output_dir / "sample5_chapter_xsampa.mp3"
        self.azure_tts.generate_audio(processed_text, xsampa, str(output_xsampa),
                                       voice='ar-EG-ShakirNeural', use_phonetic=True)

        # Calculate cost estimate
        char_count = len(processed_text)
        cost_per_million = 16  # $16 per 1M characters
        cost_this_sample = (char_count / 1_000_000) * cost_per_million

        print(f"\n📊 Cost Analysis:")
        print(f"  Characters: {char_count:,}")
        print(f"  Cost this sample: ${cost_this_sample:.4f}")
        print(f"  Estimated cost per 100k-word audiobook: ${cost_this_sample * 20:.2f}")

        self.results.append({
            'test': 'Sample 5: Chapter',
            'text_length': len(full_text),
            'char_count': char_count,
            'cost': cost_this_sample,
            'output_plain': str(output_plain),
            'output_xsampa': str(output_xsampa)
        })

    def generate_report(self):
        """Generate summary report"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)

        for result in self.results:
            print(f"\n{result['test']}")
            print("-" * 70)
            for key, value in result.items():
                if key != 'test':
                    print(f"  {key}: {value}")

        # Create results directory and write report
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)

        report_path = results_dir / "test_run_summary.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("Azure TTS Phonetic Control Test - Summary Report\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for result in self.results:
                f.write(f"\n{result['test']}\n")
                f.write("-" * 70 + "\n")
                for key, value in result.items():
                    if key != 'test':
                        f.write(f"  {key}: {value}\n")

        print(f"\n✓ Report saved: {report_path}")

    def run_all_tests(self):
        """Run all 5 tests"""
        print("=" * 70)
        print("AZURE TTS PHONETIC CONTROL TEST SUITE")
        print("=" * 70)
        print()
        print("This will generate:")
        print("  - 10+ audio files (plain text + X-SAMPA versions)")
        print("  - Comparison of pronunciation accuracy")
        print("  - Cost analysis for audiobook production")
        print()
        input("Press Enter to continue...")
        print()

        # Run tests
        self.test_sample1_phonological()
        self.test_sample2_rare_words()
        self.test_sample3_multidialect()
        self.test_sample4_dialogue()
        self.test_sample5_chapter()

        # Generate report
        self.generate_report()

        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETE!")
        print("=" * 70)
        print(f"\nAudio files: {self.output_dir}")
        print(f"Results: {Path(__file__).parent / 'results'}")
        print("\nNext steps:")
        print("  1. Listen to all audio files")
        print("  2. Compare plain text vs X-SAMPA versions")
        print("  3. Rate quality using evaluation criteria")
        print("  4. Make decision on X-SAMPA value")


def main():
    """Main entry point"""
    orchestrator = AzureTestOrchestrator()
    orchestrator.run_all_tests()


if __name__ == "__main__":
    main()
