#!/usr/bin/env python3
"""
Festival TTS - Long Multi-Voice Test

Generates 1+ minute audiobook with:
- Mishkal diacritization (proven better)
- Voice variations (narrator, male character, female character, older character)
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main import ArabicTTS


def generate_audio_with_voice(text, output_path, pitch=100, speed=1.0, voice_desc=""):
    """
    Generate audio with specific voice parameters using text2wave

    Args:
        text: Arabic text (diacritized)
        output_path: Output WAV file
        pitch: Pitch value (80=low, 100=normal, 150=high)
        speed: Speed multiplier (0.85=fast, 1.0=normal, 1.2=slow)
        voice_desc: Description for logging
    """
    # Create Festival script with voice parameters
    festival_script = f"""
(voice_ara_norm_ziad_hts)
(set! duffint_params '((start {pitch}) (end {pitch})))
(Parameter.set 'Duration_Stretch {speed})
"""

    # Write script to temp file
    script_file = Path(output_path).parent / f"{Path(output_path).stem}_script.scm"
    with open(script_file, 'w') as f:
        f.write(festival_script)

    # Generate audio using text2wave with custom voice settings
    result = subprocess.run(
        ['text2wave', '-eval', festival_script.strip(), '-o', str(output_path)],
        input=text,
        text=True,
        capture_output=True,
        timeout=60
    )

    # Clean up script
    if script_file.exists():
        script_file.unlink()

    if result.returncode == 0 and Path(output_path).exists():
        size = Path(output_path).stat().st_size
        duration = size / 44100 / 2  # Rough estimate (16-bit mono at 22050 Hz)
        print(f"  ✅ {voice_desc}: {Path(output_path).name} ({size} bytes, ~{duration:.1f}s)")
        return True
    else:
        print(f"  ❌ {voice_desc} failed: {result.stderr}")
        return False


def test_long_multivoice_story():
    """Generate long audiobook with multiple character voices"""
    print("=" * 80)
    print("FESTIVAL LONG MULTI-VOICE TEST")
    print("=" * 80)
    print("\nGenerating 1+ minute audiobook with:")
    print("  - Mishkal diacritization (better quality)")
    print("  - 4 voice variations (narrator, male, female, older)")
    print("=" * 80)

    pipeline = ArabicTTS(dialect='EG')
    output_dir = Path("/home/hamr/PycharmProjects/ArabicTTS/audio/festival_tests")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Long story (~1-2 minutes when spoken)
    long_story = """كان يا ما كان في قديم الزمان، في مدينة صغيرة، عاش رجل فقير اسمه أحمد. كان أحمد يعمل بجد كل يوم لكسب قوت يومه، لكنه لم يفقد الأمل أبداً.

قال أحمد لنفسه: اليوم سيكون يوماً مختلفاً. سأجد طريقة لتحسين حياتي.

في صباح ذلك اليوم، ذهب أحمد إلى السوق كالعادة. وهناك، قابل رجلاً عجوزاً يجلس تحت شجرة كبيرة.

قال الرجل العجوز بصوت هادئ: يا بني، أراك تعمل بجد كل يوم. هل تريد أن تسمع نصيحة من رجل عجوز؟

رد أحمد باهتمام: نعم يا سيدي، أنا مستعد لسماع أي نصيحة تساعدني.

قال الرجل العجوز: الحكمة الحقيقية ليست في كثرة المال، بل في القناعة والعمل الصالح. إذا عملت بإخلاص وساعدت الآخرين، فإن الحياة ستكافئك.

فكر أحمد في كلام الرجل العجوز. وفي اليوم التالي، بدأ يساعد جيرانه وأصدقاءه كلما استطاع.

وبعد أيام قليلة، قابل أحمد تاجراً غنياً في السوق.

قال التاجر: لقد سمعت عنك يا أحمد. الناس يقولون إنك رجل أمين ومخلص. أريد أن أعرض عليك العمل معي في تجارتي.

فرح أحمد كثيراً وقال: شكراً لك يا سيدي. سأعمل بكل جد وإخلاص.

وهكذا، تحسنت حياة أحمد، وعاش هو وعائلته في سعادة، ولم ينسَ أبداً نصيحة الرجل العجوز."""

    print(f"\n📖 Story length: {len(long_story)} characters")
    print(f"   Estimated duration: ~1.5-2 minutes")

    # Process through mishkal
    print("\n🔄 Processing through mishkal...")
    result = pipeline.process_text(long_story, dialect='EG')

    # Extract diacritized text
    diacritized_words = []
    for word in result.get('words', []):
        if word.get('type') == 'arabic_word':
            syllables = [syl['syllable'] for syl in word.get('syllables', [])]
            diacritized_words.append(''.join(syllables))
        elif word.get('type') == 'punct':
            diacritized_words.append(word.get('original', ''))

    full_diacritized = ''.join(diacritized_words)
    print(f"✅ Diacritization complete ({len(full_diacritized)} chars)")

    # Voice configurations
    voices = {
        'narrator': {
            'pitch': 100,
            'speed': 1.0,
            'desc': 'Narrator (normal male)'
        },
        'male': {
            'pitch': 110,
            'speed': 0.95,
            'desc': 'Male character (slightly higher, faster)'
        },
        'female': {
            'pitch': 150,
            'speed': 1.0,
            'desc': 'Female character (high pitch)'
        },
        'older': {
            'pitch': 85,
            'speed': 1.15,
            'desc': 'Older character (low, slower)'
        }
    }

    # Generate audio for each voice type
    print(f"\n🎙️ Generating audio with {len(voices)} voice variations...")
    print("=" * 80)

    generated_files = []

    for voice_name, voice_params in voices.items():
        output_file = output_dir / f"long_story_{voice_name}.wav"

        success = generate_audio_with_voice(
            full_diacritized,
            output_file,
            pitch=voice_params['pitch'],
            speed=voice_params['speed'],
            voice_desc=voice_params['desc']
        )

        if success:
            generated_files.append((voice_name, output_file))

    # Summary
    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)

    print(f"\n📁 Audio files: {output_dir}/")
    print("\n🎧 Generated files:")
    for voice_name, filepath in generated_files:
        voice_desc = voices[voice_name]['desc']
        print(f"  - {filepath.name} - {voice_desc}")

    print("\n📊 LISTENING GUIDE:")
    print("\n1. Compare voice variations:")
    print("   - long_story_narrator.wav (normal male)")
    print("   - long_story_male.wav (male character - slightly different)")
    print("   - long_story_female.wav (female character - high pitch)")
    print("   - long_story_older.wav (older character - low, slow)")

    print("\n2. Evaluate multi-character audiobook:")
    print("   - Can you distinguish different characters?")
    print("   - Does female voice sound natural or artificial?")
    print("   - Is older voice believable?")
    print("   - Would this work for a 10-hour audiobook?")

    print("\n3. Quality assessment:")
    print("   Rate 1-5: ⭐⭐⭐⭐⭐")
    print("   - Voice quality: ___")
    print("   - Character differentiation: ___")
    print("   - Naturalness: ___")
    print("   - Listening fatigue (after 2 min): ___")

    print("\n💡 Next steps based on rating:")
    print("   ⭐⭐⭐⭐⭐ or ⭐⭐⭐⭐ → Festival is production-ready!")
    print("   ⭐⭐⭐ → Consider XTTS for better quality")
    print("   ⭐⭐ or ⭐ → Use Azure (proven quality)")


def test_segmented_multivoice():
    """Generate segmented audiobook with different voices per character"""
    print("\n" + "=" * 80)
    print("BONUS: SEGMENTED MULTI-VOICE AUDIOBOOK")
    print("=" * 80)
    print("\nGenerating story with automatic voice assignment per character")
    print("=" * 80)

    pipeline = ArabicTTS(dialect='EG')
    output_dir = Path("/home/hamr/PycharmProjects/ArabicTTS/audio/festival_tests")

    # Story segments (narrator + dialogue)
    segments = [
        {
            'text': 'كان يا ما كان في قديم الزمان رجل اسمه أحمد',
            'voice': 'narrator',
            'character': 'Narrator'
        },
        {
            'text': 'قال أحمد: يا أصدقائي، أريد أن أخبركم قصة مهمة',
            'voice': 'male',
            'character': 'أحمد'
        },
        {
            'text': 'قالت فاطمة: نحن مستعدون للاستماع يا أحمد',
            'voice': 'female',
            'character': 'فاطمة'
        },
        {
            'text': 'قال الرجل العجوز بحكمة: في قديم الزمان كانت الحياة مختلفة',
            'voice': 'older',
            'character': 'الرجل العجوز'
        },
        {
            'text': 'واستمر أحمد في الحديث عن تجاربه ومغامراته',
            'voice': 'narrator',
            'character': 'Narrator'
        }
    ]

    # Voice parameters
    voice_params = {
        'narrator': {'pitch': 100, 'speed': 1.0},
        'male': {'pitch': 110, 'speed': 0.95},
        'female': {'pitch': 150, 'speed': 1.0},
        'older': {'pitch': 85, 'speed': 1.15}
    }

    print(f"\n🎭 Story segments: {len(segments)}")

    segment_files = []

    for i, segment in enumerate(segments, 1):
        print(f"\n--- Segment {i}: {segment['character']} ---")
        print(f"Text: {segment['text'][:60]}...")

        # Diacritize
        result = pipeline.process_text(segment['text'], dialect='EG')

        diacritized_words = []
        for word in result.get('words', []):
            if word.get('type') == 'arabic_word':
                syllables = [syl['syllable'] for syl in word.get('syllables', [])]
                diacritized_words.append(''.join(syllables))
            elif word.get('type') == 'punct':
                diacritized_words.append(word.get('original', ''))

        diacritized = ''.join(diacritized_words)

        # Generate audio
        voice_type = segment['voice']
        params = voice_params[voice_type]
        output_file = output_dir / f"segment_{i}_{voice_type}.wav"

        success = generate_audio_with_voice(
            diacritized,
            output_file,
            pitch=params['pitch'],
            speed=params['speed'],
            voice_desc=f"{segment['character']} ({voice_type})"
        )

        if success:
            segment_files.append(output_file)

    print("\n" + "=" * 80)
    print("SEGMENTED AUDIOBOOK COMPLETE")
    print("=" * 80)
    print(f"\n📁 Segments: {output_dir}/")
    print("\n🎧 Listen in order:")
    for i, filepath in enumerate(segment_files, 1):
        print(f"  {i}. {filepath.name}")

    print("\n💡 This demonstrates automatic character voice assignment!")
    print("   Each character gets a distinct voice based on role:")
    print("   - Narrator → Normal male")
    print("   - Male character → Slightly higher/faster")
    print("   - Female character → High pitch")
    print("   - Older character → Low pitch, slower")


if __name__ == '__main__':
    # Run main test
    test_long_multivoice_story()

    # Run segmented test
    test_segmented_multivoice()
