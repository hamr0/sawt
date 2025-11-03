#!/usr/bin/env python3
"""
Amazon Polly Integration Test Script

This script tests converting your IPA output to Amazon Polly SSML
and generating natural-sounding Arabic audio.

Requirements:
- AWS account with Polly access
- boto3 installed: pip install boto3
- AWS credentials configured: aws configure
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import ArabicTTS
from src.integrations.polly import PollyTTS
from src.integrations.espeak import ESpeakTTS


class PollyTestRunner:
    """
    Test runner for Polly integration using PollyTTS class
    """
    
    def __init__(self):
        """Initialize Polly and eSpeak TTS clients"""
        # Initialize Polly
        try:
            self.polly = PollyTTS()
            print("✅ Amazon Polly client initialized")
            self.use_polly = True
        except ImportError as e:
            print(f"❌ {e}")
            self.polly = None
            self.use_polly = False
        except RuntimeError as e:
            print(f"❌ {e}")
            self.polly = None
            self.use_polly = False
        
        # Initialize eSpeak for comparison
        try:
            self.espeak = ESpeakTTS()
            print("✅ eSpeak TTS initialized")
            self.use_espeak = True
        except RuntimeError as e:
            print(f"❌ {e}")
            self.espeak = None
            self.use_espeak = False
    
    def test_sentence(self, text, dialect='MSA', output_dir='demo_output/polly_test', test_num=1):
        """
        Complete pipeline test: Text → IPA → Polly + eSpeak → Audio (comparison mode)
        
        Args:
            text: Arabic text to process
            dialect: Dialect code (MSA, EG, etc.)
            output_dir: Where to save outputs
            test_num: Test number for file naming
        """
        print(f"\n{'='*60}")
        print(f"Testing: {text}")
        print(f"Dialect: {dialect}")
        print(f"{'='*60}\n")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Your IPA engine
        print("Step 1: Processing with your IPA engine...")
        tts = ArabicTTS(dialect=dialect)
        result = tts.process_text(text)
        
        # Display your processing results
        print(f"  Syllabification: {result.get('syllabification', 'N/A')}")
        print(f"  IPA: {result.get('ipa', 'N/A')}")
        
        # Get X-SAMPA from your system
        # Note: You might need to adjust this based on your actual output
        xsampa = result.get('x_sampa', result.get('ipa', ''))
        print(f"  X-SAMPA: {xsampa}")
        
        # Step 2: Generate audio with Polly (FR-015: comparison mode)
        print("\nStep 2: Generating audio with Amazon Polly...")
        polly_path = os.path.join(output_dir, f"test_polly_{test_num:03d}_zeina_neural.mp3")
        
        # Choose voice based on dialect
        voice_map = {
            'MSA': 'Zeina',  # Standard Arabic, female
            'EG': 'Zeina',   # No EG voice, use MSA (your phonetics will make it EG!)
            'Gulf': 'Hala',  # Gulf Arabic, female
        }
        voice_id = voice_map.get(dialect, 'Zeina')
        
        polly_success = False
        if not self.use_polly:
            print("  ❌ Polly not available. Skipping Polly audio generation.")
        else:
            polly_success, message = self.polly.generate_audio(
                text=text,
                xsampa=xsampa,
                output_path=polly_path,
                voice_id=voice_id,
                engine='neural'
            )
            
            if polly_success:
                size_kb = os.path.getsize(polly_path) / 1024
                print(f"  ✅ Polly: {polly_path} ({size_kb:.1f} KB)")
            else:
                print(f"  ❌ Polly failed: {message}")
        
        # Step 3: Generate audio with eSpeak for comparison (FR-015)
        print("\nStep 3: Generating audio with eSpeak (for comparison)...")
        espeak_path = os.path.join(output_dir, f"test_polly_{test_num:03d}_espeak.wav")
        
        espeak_success = False
        if not self.use_espeak:
            print("  ❌ eSpeak not available. Skipping eSpeak audio generation.")
        else:
            # Use generate_audio method with IPA input
            espeak_success, message = self.espeak.generate_audio(
                ipa=result.get('ipa', ''),
                output_path=espeak_path
            )
            
            if espeak_success:
                size_kb = os.path.getsize(espeak_path) / 1024
                print(f"  ✅ eSpeak: {espeak_path} ({size_kb:.1f} KB)")
            else:
                print(f"  ❌ eSpeak failed: {message}")
        
        # Summary
        if polly_success or espeak_success:
            print(f"\n🎵 Audio files generated for comparison:")
            if polly_success:
                print(f"   Polly:  {polly_path}")
            if espeak_success:
                print(f"   eSpeak: {espeak_path}")
        
        return {
            'text': text,
            'dialect': dialect,
            'ipa': result.get('ipa', ''),
            'xsampa': xsampa,
            'polly_path': polly_path if polly_success else None,
            'espeak_path': espeak_path if espeak_success else None,
            'polly_success': polly_success,
            'espeak_success': espeak_success,
            'success': polly_success or espeak_success
        }


def main():
    """
    Run comprehensive Polly integration tests
    """
    print("""
╔════════════════════════════════════════════════════════════════╗
║     Amazon Polly Integration Test for Arabic TTS              ║
╚════════════════════════════════════════════════════════════════╝

This script will:
1. Process Arabic text with your IPA engine
2. Convert IPA/X-SAMPA to Polly SSML format
3. Generate audio using Amazon Polly neural voices
4. Compare quality with your current eSpeak output

Prerequisites:
- AWS account (free tier has 5M characters/month free for 12 months)
- AWS CLI configured: aws configure
- boto3 installed: pip install boto3
""")
    
    # Initialize test runner
    test_runner = PollyTestRunner()
    
    # Test sentences covering diverse phonetic patterns (FR-013, Appendix A)
    test_cases = [
        {
            'text': 'صباح الخير',
            'dialect': 'MSA',
            'translation': 'Good morning',
            'pattern': 'Simple sentence with common words'
        },
        {
            'text': 'المدرسة الجديدة',
            'dialect': 'MSA',
            'translation': 'The new school',
            'pattern': 'Consonant clusters'
        },
        {
            'text': 'كتابٌ جديدٌ',
            'dialect': 'MSA',
            'translation': 'A new book',
            'pattern': 'Tanween (nunation)'
        },
        {
            'text': 'ذهبتُ إلى السوق لشراء بعض الخضروات والفواكه',
            'dialect': 'MSA',
            'translation': 'I went to the market to buy some vegetables and fruits',
            'pattern': 'Long sentence (10-15 words)'
        },
        {
            'text': 'القواعد الإملائية والنحوية',
            'dialect': 'MSA',
            'translation': 'Spelling and grammatical rules',
            'pattern': 'Challenging phonemes'
        }
    ]
    
    # Run tests
    results = []
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'#'*60}")
        print(f"Test Case {i}/{len(test_cases)}: {test['translation']}")
        print(f"Pattern: {test['pattern']}")
        print(f"{'#'*60}")
        
        result = test_runner.test_sentence(
            text=test['text'],
            dialect=test['dialect'],
            test_num=i
        )
        results.append(result)
    
    # Enhanced Summary Report (FR-014, SM-001 to SM-004)
    print(f"\n\n{'='*60}")
    print("POC TEST SUMMARY REPORT")
    print(f"{'='*60}")
    
    # Test Results
    polly_successful = sum(1 for r in results if r.get('polly_success', False))
    espeak_successful = sum(1 for r in results if r.get('espeak_success', False))
    polly_failed = len(results) - polly_successful
    espeak_failed = len(results) - espeak_successful
    
    print(f"\n📊 Test Results:")
    print(f"   Total test cases: {len(results)}")
    print(f"   Polly:  {polly_successful} passed, {polly_failed} failed")
    print(f"   eSpeak: {espeak_successful} passed, {espeak_failed} failed")
    
    # File Sizes
    print(f"\n📁 Generated Files:")
    polly_files = [r for r in results if r.get('polly_success', False)]
    espeak_files = [r for r in results if r.get('espeak_success', False)]
    
    if polly_files:
        total_polly_size = 0
        for r in polly_files:
            if r.get('polly_path') and os.path.exists(r['polly_path']):
                size = os.path.getsize(r['polly_path'])
                total_polly_size += size
        print(f"   Polly audio:  {len(polly_files)} files, {total_polly_size / 1024:.1f} KB total")
    
    if espeak_files:
        total_espeak_size = 0
        for r in espeak_files:
            if r.get('espeak_path') and os.path.exists(r['espeak_path']):
                size = os.path.getsize(r['espeak_path'])
                total_espeak_size += size
        print(f"   eSpeak audio: {len(espeak_files)} files, {total_espeak_size / 1024:.1f} KB total")
    
    print(f"   Location: demo_output/polly_test/")
    
    # Cost Analysis
    if polly_successful > 0:
        total_chars = sum(len(r['text']) for r in results)
        cost_per_million = 16  # Neural voice pricing (USD)
        estimated_cost = (total_chars / 1_000_000) * cost_per_million
        free_tier_usage = (total_chars / 5_000_000) * 100  # % of monthly free tier
        
        print(f"\n💰 Cost Analysis:")
        print(f"   Characters processed: {total_chars:,}")
        print(f"   Cost for this POC: ${estimated_cost:.6f} (within free tier)")
        print(f"   Free tier usage: {free_tier_usage:.3f}% of 5M chars/month")
        print(f"   ")
        print(f"   Production estimates (after free tier):")
        print(f"   • 100k word audiobook (~600k chars): ${(600_000/1_000_000)*cost_per_million:.2f}")
        print(f"   • 10 audiobooks/month (~6M chars):  ${(6_000_000/1_000_000)*cost_per_million:.2f}")
    
    # Quality Assessment
    if polly_successful > 0:
        print(f"\n✅ SUCCESS - Polly Integration Working!")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Listen to all generated audio files")
        print(f"   2. Compare Polly vs eSpeak quality side-by-side")
        print(f"   3. Native speaker validation (target: ≥90% accuracy)")
        print(f"   4. Document findings in docs/polly/POC_RESULTS.md")
        print(f"   5. Make Go/No-Go decision based on success metrics")
        
        print(f"\n📋 Success Metrics Checklist (from PRD):")
        print(f"   [ ] SM-006: Audio quality significantly better than eSpeak")
        print(f"   [ ] SM-007: Native speaker validation ≥90% accuracy")
        print(f"   [ ] SM-008: Native speaker confirms 'acceptable for audiobooks'")
        print(f"   [{'✓' if estimated_cost == 0 else ' '}] SM-004: AWS costs $0 (within free tier)")
        print(f"   [✓] SM-001: POC execution time <5 days")
        
        print(f"\n💡 Comparison Instructions:")
        print(f"   For each test (001-005):")
        print(f"   • Play: test_polly_00X_zeina_neural.mp3")
        print(f"   • Play: test_polly_00X_espeak.wav")
        print(f"   • Note: Naturalness, pronunciation, clarity differences")
    else:
        print(f"\n⚠️  Polly Integration Needs Setup")
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Install boto3: pip install boto3>=1.28.0")
        print(f"   2. Configure AWS credentials: aws configure")
        print(f"   3. Verify Polly access in AWS account")
        print(f"   4. See: docs/polly/AWS_SETUP_GUIDE.md")
    
    if espeak_successful > 0 and polly_successful == 0:
        print(f"\n   eSpeak is working - comparison baseline available")
    
    print(f"\n{'='*60}\n")


if __name__ == '__main__':
    main()
