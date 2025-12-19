#!/usr/bin/env python3
"""
Test Multi-Voice Audiobook Generation with Azure

Demonstrates automatic character voice assignment for audiobook production
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.azure_tts.azure_integration import AzureTTS
from tools.azure_tts.character_voice_assignment import CharacterVoiceAssigner, Gender


def test_multivoice_story():
    """Test multi-voice generation with character dialogue"""
    print("=" * 80)
    print("MULTI-VOICE AUDIOBOOK TEST")
    print("=" * 80)

    # Sample story with multiple characters
    story = """كان يا ما كان في قديم الزمان، في مدينة صغيرة، عاش رجل يدعى أحمد وزوجته فاطمة.

قال أحمد: يا فاطمة، أريد أن أذهب إلى السوق لشراء بعض الطعام.

قالت فاطمة: حسناً يا أحمد، لكن كن حذراً في الطريق.

ذهب أحمد إلى السوق ووجد صديقه القديم علي.

صرخ علي: أحمد! يا لها من مفاجأة! لم أرك منذ سنوات!

رد أحمد: علي! كم أنا سعيد برؤيتك! كيف حالك؟

همس علي: الحمد لله، الأمور جيدة. وأنت؟

قال أحمد: أنا بخير، الحمد لله.

عاد أحمد إلى البيت وحكى لفاطمة عن لقائه.

قالت فاطمة: ما شاء الله! يجب أن ندعو علي لزيارتنا قريباً.

وعاشوا في سعادة وهناء."""

    print("\n📖 STORY TEXT:")
    print(story)
    print("\n" + "=" * 80)

    # Initialize voice assigner
    print("\n🎭 ANALYZING STORY AND ASSIGNING VOICES...")
    assigner = CharacterVoiceAssigner(dialect='EG', narrator_gender=Gender.FEMALE)

    # Analyze and generate SSML
    segments, ssml = assigner.analyze_and_assign(story)

    # Print results
    print(f"\n📊 ANALYSIS RESULTS:")
    print(f"  Total segments: {len(segments)}")
    print(f"  Narration: {sum(1 for s in segments if s.segment_type == 'narration')}")
    print(f"  Dialogue: {sum(1 for s in segments if s.segment_type == 'dialogue')}")

    print(f"\n👥 DETECTED CHARACTERS:")
    summary = assigner.get_character_summary()
    for name, info in summary.items():
        print(f"  - {name}: {info['gender']} → {info['voice']} ({info['dialogue_count']} lines)")

    # Save SSML
    ssml_file = '/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/multivoice_story.ssml'
    with open(ssml_file, 'w', encoding='utf-8') as f:
        f.write(ssml)
    print(f"\n✅ SSML saved to: {ssml_file}")

    # Generate audio with Azure
    print("\n🎙️ GENERATING AUDIO WITH AZURE...")
    azure = AzureTTS()

    output_file = '/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/multivoice_story.mp3'
    success, msg = azure.generate_audio_from_ssml(ssml, output_file)

    if success:
        print(f"✅ {msg}")
        print(f"\n🎧 Listen to the multi-voice audiobook:")
        print(f"   {output_file}")
    else:
        print(f"❌ {msg}")

    print("\n" + "=" * 80)


def test_complex_dialogue():
    """Test with more complex dialogue patterns"""
    print("\n" + "=" * 80)
    print("COMPLEX DIALOGUE TEST")
    print("=" * 80)

    # More complex story with narrator descriptions
    story = """في يوم من الأيام، كانت هناك فتاة صغيرة اسمها ليلى تعيش في قرية جميلة.

صاحت ليلى بفرح: أمي! انظري إلى الطائر الجميل في الحديقة!

قالت الأم بحنان: نعم يا حبيبتي، إنه طائر رائع. لكن يجب أن نحترم الطيور ولا نزعجها.

فجأة ظهر أخوها الأكبر حسن وهو يحمل كتاباً.

قال حسن بحماس: ليلى! لقد وجدت كتاباً عن الطيور في المكتبة!

ردت ليلى بسعادة: رائع يا حسن! هل يمكنك أن تقرأ لي عنه؟

قال حسن: بالطبع! دعيني أريك الصور أولاً.

جلس الأطفال معاً وبدأوا يقرأون عن الطيور الجميلة."""

    print("\n📖 STORY TEXT:")
    print(story)

    # Analyze
    assigner = CharacterVoiceAssigner(dialect='EG', narrator_gender=Gender.FEMALE)
    segments, ssml = assigner.analyze_and_assign(story)

    # Print character info
    print(f"\n👥 DETECTED CHARACTERS:")
    summary = assigner.get_character_summary()
    for name, info in summary.items():
        print(f"  - {name}: {info['gender']} → {info['voice']}")

    # Save SSML
    ssml_file = '/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/complex_dialogue.ssml'
    with open(ssml_file, 'w', encoding='utf-8') as f:
        f.write(ssml)
    print(f"\n✅ SSML saved to: {ssml_file}")

    # Generate audio
    print("\n🎙️ GENERATING AUDIO WITH AZURE...")
    azure = AzureTTS()

    output_file = '/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/complex_dialogue.mp3'
    success, msg = azure.generate_audio_from_ssml(ssml, output_file)

    if success:
        print(f"✅ {msg}")
        print(f"\n🎧 Listen to: {output_file}")
    else:
        print(f"❌ {msg}")


def test_long_audiobook_chapter():
    """Test with longer audiobook chapter-style content"""
    print("\n" + "=" * 80)
    print("LONG AUDIOBOOK CHAPTER TEST")
    print("=" * 80)

    # Longer chapter with multiple scenes and characters
    chapter = """الفصل الأول: البداية

في صباح يوم جميل من أيام الربيع، استيقظ أحمد على صوت زقزقة العصافير. كان يشعر بالحماس لأن اليوم كان يوم مميز.

قال أحمد لنفسه: اليوم سأبدأ مشروعي الجديد!

نزل إلى المطبخ حيث وجد أمه فاطمة تحضر الفطور.

قالت فاطمة: صباح الخير يا أحمد! لقد استيقظت مبكراً اليوم.

رد أحمد: صباح النور يا أمي! أنا متحمس لبدء العمل على مشروعي.

ابتسمت فاطمة وقالت: هذا رائع يا بني! لكن لا تنسى أن تأكل فطورك أولاً.

بعد الفطور، خرج أحمد من المنزل وتوجه نحو المكتبة. في الطريق، قابل صديقه القديم علي.

صاح علي: أحمد! إلى أين أنت ذاهب في هذا الصباح الجميل؟

رد أحمد: مرحباً يا علي! أنا ذاهب إلى المكتبة للبحث عن معلومات لمشروعي.

قال علي: يا له من توقيت مثالي! أنا أيضاً ذاهب إلى هناك. هل تمانع إذا رافقتك؟

رد أحمد بسعادة: بالطبع! يسعدني ذلك.

مشى الصديقان معاً وهما يتحدثان عن أحلامهما وطموحاتهما. كان يوماً جميلاً، ولم يعلما أن مغامرة كبيرة تنتظرهما."""

    print(f"\n📖 CHAPTER ({len(chapter)} characters)")
    print(chapter[:200] + "...\n")

    # Analyze
    assigner = CharacterVoiceAssigner(dialect='EG', narrator_gender=Gender.FEMALE)
    segments, ssml = assigner.analyze_and_assign(chapter)

    # Print stats
    print(f"📊 CHAPTER STATISTICS:")
    print(f"  Total segments: {len(segments)}")
    print(f"  Characters detected: {len(assigner.characters)}")

    print(f"\n👥 CHARACTER VOICE ASSIGNMENTS:")
    summary = assigner.get_character_summary()
    for name, info in summary.items():
        print(f"  - {name}: {info['gender']} → {info['voice']} ({info['dialogue_count']} lines)")

    # Calculate approximate duration (rough estimate: 150 words/min in Arabic)
    word_count = len(chapter.split())
    estimated_duration = (word_count / 150) * 60  # seconds
    print(f"\n⏱️ ESTIMATED AUDIO DURATION: ~{estimated_duration:.1f} seconds ({word_count} words)")

    # Save SSML
    ssml_file = '/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/audiobook_chapter.ssml'
    with open(ssml_file, 'w', encoding='utf-8') as f:
        f.write(ssml)
    print(f"\n✅ SSML saved to: {ssml_file}")

    # Generate audio
    print("\n🎙️ GENERATING AUDIOBOOK CHAPTER WITH AZURE...")
    azure = AzureTTS()

    output_file = '/home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/audiobook_chapter.mp3'
    success, msg = azure.generate_audio_from_ssml(ssml, output_file)

    if success:
        print(f"✅ {msg}")
        print(f"\n🎧 Listen to the full chapter: {output_file}")
    else:
        print(f"❌ {msg}")


def main():
    """Run all multi-voice tests"""
    print("\n" + "=" * 80)
    print("AZURE MULTI-VOICE AUDIOBOOK SYSTEM")
    print("Automatic Character Voice Assignment")
    print("=" * 80)

    try:
        # Test 1: Simple story
        test_multivoice_story()

        # Test 2: Complex dialogue
        test_complex_dialogue()

        # Test 3: Long chapter
        test_long_audiobook_chapter()

        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETE")
        print("=" * 80)
        print("\n📁 Generated files in: /home/hamr/PycharmProjects/ArabicTTS/audio/azure_tests/")
        print("  - multivoice_story.mp3")
        print("  - complex_dialogue.mp3")
        print("  - audiobook_chapter.mp3")
        print("\n🎧 Listen to compare automatic voice assignment quality!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
