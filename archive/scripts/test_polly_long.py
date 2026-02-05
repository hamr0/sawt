#!/usr/bin/env python3
"""
Generate a longer Polly audio sample for quality evaluation
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.integrations.polly import PollyTTS


def main():
    """Generate longer audio samples"""
    
    print("=" * 70)
    print("Amazon Polly - Long Audio Sample Generator")
    print("=" * 70)
    print()
    
    # Initialize Polly
    try:
        polly = PollyTTS()
        print("✅ Amazon Polly initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Polly: {e}")
        return
    
    # Test samples with increasing length
    samples = [
        {
            'name': 'short_paragraph',
            'title': 'Short Paragraph (2-3 sentences)',
            'text': '''
اللغة العربية هي لغة غنية وجميلة. يتحدث بها أكثر من أربعمائة مليون شخص حول العالم.
وهي واحدة من أقدم اللغات في التاريخ.
            '''.strip()
        },
        {
            'name': 'medium_story',
            'title': 'Medium Story (5-6 sentences)',
            'text': '''
في يوم من الأيام، كان هناك رجل عجوز يعيش في قرية صغيرة. كان يحب القراءة والكتابة كثيراً.
كل يوم، كان يذهب إلى المكتبة لقراءة الكتب القديمة. وجد كتاباً قديماً عن تاريخ البلاد.
قرأ الكتاب بعناية وتعلم الكثير من المعلومات الجديدة. شعر بالسعادة لأنه اكتشف شيئاً مهماً.
            '''.strip()
        },
        {
            'name': 'long_passage',
            'title': 'Long Passage (~10 sentences)',
            'text': '''
التعليم هو أساس تقدم الأمم وازدهارها. منذ القدم، اهتم العرب بالعلم والمعرفة وبناء المكتبات الكبيرة.
كانت بغداد في العصر العباسي مركزاً للعلم والثقافة. جاء العلماء من جميع أنحاء العالم للدراسة في جامعاتها.
ترجم العلماء العرب الكتب اليونانية والفارسية والهندية إلى اللغة العربية. أضافوا إليها اكتشافاتهم وابتكاراتهم الخاصة.
في مجالات الرياضيات والفلك والطب والفلسفة، قدم العلماء العرب إسهامات عظيمة. 
اخترعوا الصفر وطوروا علم الجبر واكتشفوا نجوماً جديدة. كما ألفوا كتباً طبية ظلت تدرس في أوروبا لقرون عديدة.
هذا التراث العلمي العظيم يجب أن نفخر به ونحافظ عليه. علينا أن نستمر في طريق العلم والمعرفة كما فعل أجدادنا.
            '''.strip()
        }
    ]
    
    output_dir = 'demo_output/polly_test'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nGenerating {len(samples)} audio samples...\n")
    
    for i, sample in enumerate(samples, 1):
        print(f"{'='*70}")
        print(f"Sample {i}/{len(samples)}: {sample['title']}")
        print(f"{'='*70}")
        
        text = sample['text']
        output_path = os.path.join(output_dir, f"long_sample_{sample['name']}.mp3")
        
        # Count words and characters
        words = len(text.split())
        chars = len(text)
        
        print(f"Text preview: {text[:100]}...")
        print(f"Statistics: {words} words, {chars} characters")
        print(f"\nGenerating audio...")
        
        # Generate audio
        success, message = polly.generate_audio(
            text=text,
            xsampa="",  # Use Polly's built-in pronunciation
            output_path=output_path,
            voice_id="Zeina",
            engine="standard"
        )
        
        if success:
            # Get file info
            size_bytes = os.path.getsize(output_path)
            size_kb = size_bytes / 1024
            
            # Estimate duration (rough: 48 kbps bitrate)
            estimated_duration = (size_bytes * 8) / 48000  # seconds
            
            print(f"✅ Success!")
            print(f"   File: {output_path}")
            print(f"   Size: {size_kb:.1f} KB")
            print(f"   Estimated duration: {estimated_duration:.1f} seconds")
            
            # Cost calculation
            cost_per_million = 4  # Standard engine: $4 per 1M chars
            cost = (chars / 1_000_000) * cost_per_million
            print(f"   Cost: ${cost:.6f}")
            print(f"\n🎵 Play with: mpv {output_path}")
        else:
            print(f"❌ Failed: {message}")
        
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nGenerated samples saved to: {output_dir}/")
    print("\nTo listen:")
    print(f"  cd {output_dir}")
    print(f"  mpv long_sample_short_paragraph.mp3")
    print(f"  mpv long_sample_medium_story.mp3")
    print(f"  mpv long_sample_long_passage.mp3")
    print()


if __name__ == '__main__':
    main()
