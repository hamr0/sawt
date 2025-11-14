#!/usr/bin/env python3
"""
Generate a full chapter-length Polly audio sample (2-3 minutes)
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.integrations.polly import PollyTTS


def main():
    """Generate chapter-length audio sample"""
    
    print("=" * 80)
    print("Amazon Polly - Full Chapter Sample Generator (2-3 minutes)")
    print("=" * 80)
    print()
    
    # Initialize Polly
    try:
        polly = PollyTTS()
        print("✅ Amazon Polly initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Polly: {e}")
        return
    
    # Full chapter: A story about a journey (classic Arabic storytelling style)
    chapter_text = """
الفصل الأول: رحلة إلى المعرفة

في قرية صغيرة على ضفاف نهر النيل، عاش شاب يدعى حسن. كان حسن شغوفاً بالمعرفة منذ صغره.
كان يقضي معظم وقته في قراءة الكتب القديمة التي ورثها عن جده. جده كان عالماً مشهوراً في 
القرية، وترك مكتبة كبيرة مليئة بالكتب النادرة.

في أحد الأيام، وجد حسن خريطة قديمة مخبأة في أحد الكتب. كانت الخريطة تشير إلى مكان 
مكتبة قديمة في مدينة بغداد. يقال إن هذه المكتبة تحتوي على أندر الكتب في العالم العربي.
قرر حسن أن يبدأ رحلة طويلة للبحث عن هذه المكتبة.

استعد حسن للرحلة بعناية. جمع بعض الطعام والماء، وأخذ معه الخريطة وبعض الكتب المفضلة 
لديه. ودع والديه وأصدقاءه، ووعدهم بأن يعود بمعرفة جديدة تنفع القرية كلها.

بدأت الرحلة في الصباح الباكر. سار حسن عبر الحقول الخضراء والجبال الشاهقة. كان يتوقف 
في القرى الصغيرة على طول الطريق، يسأل الناس عن المكتبة القديمة. بعض الناس سمعوا عنها،
وبعضهم لم يسمع. لكن الجميع نصحوه بالاستمرار في بحثه.

بعد أسبوع من السفر، وصل حسن إلى مدينة كبيرة. كانت المدينة مليئة بالأسواق النابضة 
بالحياة والمساجد الجميلة. توجه إلى السوق القديم، حيث يقال إن العلماء والتجار يلتقون.
هناك، التقى برجل عجوز يبيع الكتب القديمة.

سأل حسن الرجل العجوز عن المكتبة. ابتسم الرجل وقال: "أنت محظوظ يا بني. أنا أعرف المكان.
لكن الوصول إليه ليس سهلاً. عليك أن تعبر الصحراء الكبرى، وهي رحلة محفوفة بالمخاطر."

لم يخف حسن. كان مصمماً على الوصول إلى المكتبة. أعطاه الرجل العجوز دليلاً موثوقاً يعرف 
الطريق عبر الصحراء. انضم حسن إلى قافلة من التجار كانوا يسافرون في نفس الاتجاه.

كانت الرحلة عبر الصحراء صعبة. الحر الشديد نهاراً والبرد القارس ليلاً. لكن حسن واصل 
السير، مدفوعاً بشغفه بالمعرفة. كان يقرأ من كتبه كل ليلة عند نار المخيم، ويشارك قصصاً 
مع رفاقه في القافلة.

بعد عشرة أيام في الصحراء، ظهرت أخيراً مدينة بغداد في الأفق. كانت أسوارها العالية 
وقبابها الذهبية تلمع تحت أشعة الشمس. شعر حسن بالإثارة والترقب.

دخل حسن المدينة وبدأ البحث عن المكتبة. سأل الناس في الأسواق والمساجد. أخيراً، أرشده 
عالم مسن إلى حي قديم في المدينة. هناك، وجد مبنى قديماً مهيباً، مزيناً بالنقوش العربية 
الجميلة. كان هذا هو بيت الحكمة، المكتبة الأسطورية التي كان يبحث عنها.

دخل حسن المكتبة بقلب يخفق من الفرح. كانت الرفوف ممتدة من الأرض إلى السقف، مليئة 
بآلاف الكتب والمخطوطات. كتب في الرياضيات والفلك والطب والفلسفة والشعر. كان كنزاً حقيقياً 
من المعرفة.

قضى حسن أسابيع في المكتبة، يقرأ ويتعلم. درس علوم الفلك على يد علماء المدينة، وتعلم 
الرياضيات المتقدمة، وقرأ أعمال الفلاسفة العظام. كل يوم كان يكتشف شيئاً جديداً يثير 
دهشته وإعجابه.

عندما حان وقت العودة، كان حسن قد تغير. لم يعد الشاب الفضولي الذي غادر قريته. أصبح 
عالماً واعداً، مليئاً بالمعرفة والحكمة. حمل معه نسخاً من بعض الكتب النادرة، هدية من 
علماء بغداد.

عاد حسن إلى قريته بعد رحلة طويلة. استقبله أهل القرية بفرح عظيم. أسس مدرسة صغيرة في 
القرية، حيث بدأ يعلم الأطفال ما تعلمه في رحلته. نشر المعرفة التي اكتسبها، وألهم جيلاً 
جديداً من طلاب العلم.

وهكذا، تحولت رحلة حسن إلى رمز للسعي وراء المعرفة. علمت القرية كلها أن العلم لا حدود 
له، وأن السفر في طلب العلم يستحق كل تعب ومشقة. وظلت قصة حسن تروى للأجيال، تلهم الشباب 
لمتابعة أحلامهم وعدم الخوف من المجهول.

النهاية
    """.strip()
    
    output_dir = 'demo_output/polly_test'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'full_chapter_sample.mp3')
    
    # Statistics
    words = len(chapter_text.split())
    chars = len(chapter_text)
    lines = len(chapter_text.split('\n'))
    
    print(f"\n{'='*80}")
    print("CHAPTER DETAILS")
    print(f"{'='*80}")
    print(f"Title: الفصل الأول: رحلة إلى المعرفة (Chapter 1: Journey to Knowledge)")
    print(f"Genre: Arabic storytelling / Adventure")
    print(f"Statistics:")
    print(f"  - Words: {words}")
    print(f"  - Characters: {chars}")
    print(f"  - Lines: {lines}")
    print(f"  - Estimated reading time: {words / 150:.1f} minutes (at 150 words/min)")
    print()
    
    print("Generating audio... (this may take 30-60 seconds)")
    print()
    
    # Generate audio
    success, message = polly.generate_audio(
        text=chapter_text,
        xsampa="",  # Use Polly's built-in pronunciation
        output_path=output_path,
        voice_id="Zeina",
        engine="standard"
    )
    
    if success:
        # Get file info
        size_bytes = os.path.getsize(output_path)
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        # Estimate duration (rough: 48 kbps bitrate)
        estimated_duration_sec = (size_bytes * 8) / 48000
        estimated_duration_min = estimated_duration_sec / 60
        
        # Cost calculation
        cost_per_million = 4  # Standard engine: $4 per 1M chars
        cost = (chars / 1_000_000) * cost_per_million
        
        print(f"{'='*80}")
        print("✅ SUCCESS - CHAPTER AUDIO GENERATED!")
        print(f"{'='*80}")
        print()
        print(f"📁 File Information:")
        print(f"   Location: {output_path}")
        print(f"   Size: {size_mb:.2f} MB ({size_kb:.1f} KB)")
        print()
        print(f"⏱️  Duration:")
        print(f"   Estimated: {estimated_duration_min:.1f} minutes ({estimated_duration_sec:.0f} seconds)")
        print()
        print(f"💰 Cost:")
        print(f"   Characters processed: {chars:,}")
        print(f"   Cost: ${cost:.6f}")
        print(f"   Still within free tier: YES ✅")
        print()
        print(f"{'='*80}")
        print("🎧 HOW TO LISTEN")
        print(f"{'='*80}")
        print()
        print(f"Method 1 - mpv (recommended):")
        print(f"  mpv {output_path}")
        print()
        print(f"Method 2 - VLC:")
        print(f"  vlc {output_path}")
        print()
        print(f"Method 3 - ffplay:")
        print(f"  ffplay {output_path}")
        print()
        print(f"{'='*80}")
        print("📋 EVALUATION CHECKLIST")
        print(f"{'='*80}")
        print()
        print("As you listen, evaluate:")
        print("  [ ] Naturalness - Does it sound like a human narrator?")
        print("  [ ] Pronunciation - Are all words pronounced correctly?")
        print("  [ ] Prosody - Natural pauses and intonation?")
        print("  [ ] Consistency - Quality maintained throughout?")
        print("  [ ] Engagement - Would you listen to a full audiobook?")
        print("  [ ] Fatigue - Does it get tiring to listen to?")
        print()
        print("Compare with eSpeak to see the quality difference!")
        print()
    else:
        print(f"❌ Failed: {message}")
    

if __name__ == '__main__':
    main()
