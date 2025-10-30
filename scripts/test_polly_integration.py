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


class PollyIntegration:
    """
    Integration layer between your IPA engine and Amazon Polly
    """
    
    def __init__(self, use_polly=True):
        self.use_polly = use_polly
        
        if use_polly:
            try:
                import boto3
                self.polly = boto3.client('polly', region_name='us-east-1')
                print("✅ Amazon Polly client initialized")
            except ImportError:
                print("❌ boto3 not installed. Run: pip install boto3")
                self.use_polly = False
            except Exception as e:
                print(f"❌ Failed to initialize Polly: {e}")
                print("Make sure AWS credentials are configured: aws configure")
                self.use_polly = False
    
    def xsampa_to_ssml(self, xsampa, original_text):
        """
        Convert X-SAMPA to Polly SSML format
        
        Args:
            xsampa: X-SAMPA phonetic string (from your system)
            original_text: Original Arabic text
        
        Returns:
            SSML string ready for Polly
        """
        # Polly SSML with phoneme tag
        ssml = f'''<speak>
    <phoneme alphabet="x-sampa" ph="{xsampa}">{original_text}</phoneme>
</speak>'''
        return ssml
    
    def generate_audio_polly(self, ssml, output_path, voice_id='Zeina', engine='neural'):
        """
        Generate audio using Amazon Polly
        
        Args:
            ssml: SSML string with phoneme tags
            output_path: Where to save the MP3 file
            voice_id: Polly voice (Zeina=MSA female, Hala=Gulf female)
            engine: 'neural' (better quality) or 'standard'
        
        Returns:
            True if successful, False otherwise
        """
        if not self.use_polly:
            print("❌ Polly not available. Skipping audio generation.")
            return False
        
        try:
            # Call Polly API
            response = self.polly.synthesize_speech(
                Text=ssml,
                TextType='ssml',
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine=engine
            )
            
            # Save audio file
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            print(f"✅ Audio generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Polly generation failed: {e}")
            return False
    
    def test_sentence(self, text, dialect='MSA', output_dir='demo_output/polly_test'):
        """
        Complete pipeline test: Text → IPA → SSML → Polly → Audio
        
        Args:
            text: Arabic text to process
            dialect: Dialect code (MSA, EG, etc.)
            output_dir: Where to save outputs
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
        
        # Step 2: Convert to SSML
        print("\nStep 2: Converting to Polly SSML...")
        ssml = self.xsampa_to_ssml(xsampa, text)
        print(f"  SSML:\n{ssml}")
        
        # Save SSML for inspection
        ssml_path = os.path.join(output_dir, f"test_{dialect}.ssml")
        with open(ssml_path, 'w', encoding='utf-8') as f:
            f.write(ssml)
        print(f"  Saved: {ssml_path}")
        
        # Step 3: Generate audio with Polly
        print("\nStep 3: Generating audio with Amazon Polly...")
        audio_path = os.path.join(output_dir, f"test_{dialect}_polly.mp3")
        
        # Choose voice based on dialect
        voice_map = {
            'MSA': 'Zeina',  # Standard Arabic, female
            'EG': 'Zeina',   # No EG voice, use MSA (your phonetics will make it EG!)
            'Gulf': 'Hala',  # Gulf Arabic, female
        }
        voice_id = voice_map.get(dialect, 'Zeina')
        
        success = self.generate_audio_polly(ssml, audio_path, voice_id=voice_id)
        
        if success:
            # Get file size
            size_kb = os.path.getsize(audio_path) / 1024
            print(f"  Audio size: {size_kb:.1f} KB")
            print(f"\n🎵 Play the audio: {audio_path}")
        
        return {
            'text': text,
            'dialect': dialect,
            'ipa': result.get('ipa', ''),
            'xsampa': xsampa,
            'ssml_path': ssml_path,
            'audio_path': audio_path if success else None,
            'success': success
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
    
    # Initialize integration
    polly = PollyIntegration()
    
    # Test sentences (from your test dataset)
    test_cases = [
        {
            'text': 'صباح الخير',
            'dialect': 'MSA',
            'translation': 'Good morning'
        },
        {
            'text': 'السلام عليكم',
            'dialect': 'MSA',
            'translation': 'Peace be upon you'
        },
        {
            'text': 'الشمس',
            'dialect': 'MSA',
            'translation': 'The sun'
        },
        {
            'text': 'القمر',
            'dialect': 'MSA',
            'translation': 'The moon'
        },
        {
            'text': 'كتاب',
            'dialect': 'MSA',
            'translation': 'Book'
        }
    ]
    
    # Run tests
    results = []
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'#'*60}")
        print(f"Test Case {i}/{len(test_cases)}: {test['translation']}")
        print(f"{'#'*60}")
        
        result = polly.test_sentence(
            text=test['text'],
            dialect=test['dialect']
        )
        results.append(result)
    
    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    successful = sum(1 for r in results if r['success'])
    print(f"Tests run: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    
    if successful > 0:
        print(f"\n✅ Polly integration WORKS!")
        print(f"\nAudio files saved to: demo_output/polly_test/")
        print(f"\nNext steps:")
        print(f"1. Listen to the generated audio files")
        print(f"2. Compare with eSpeak output")
        print(f"3. Validate pronunciation accuracy")
        print(f"4. Estimate costs for audiobook production")
        
        # Cost estimate
        total_chars = sum(len(r['text']) for r in results)
        cost_per_million = 16  # Neural voice pricing
        estimated_cost = (total_chars / 1_000_000) * cost_per_million
        
        print(f"\n💰 Cost Analysis:")
        print(f"   Characters processed: {total_chars}")
        print(f"   Cost for this test: ${estimated_cost:.6f}")
        print(f"   ")
        print(f"   For a 100,000 word audiobook (~600,000 chars):")
        print(f"   Estimated cost: ${(600000/1000000)*cost_per_million:.2f}")
    else:
        print(f"\n⚠️  Polly integration needs setup")
        print(f"\nTo fix:")
        print(f"1. Install boto3: pip install boto3")
        print(f"2. Configure AWS: aws configure")
        print(f"3. Ensure Polly access in your AWS account")
    
    print(f"\n{'='*60}\n")


if __name__ == '__main__':
    main()
