#!/usr/bin/env python3
"""
Generate Test Samples for Azure TTS Evaluation

Creates 5 test samples (~5 minutes each) from existing test data:
1. Phonological Features Showcase
2. Rare/Ambiguous Words
3. Multi-Dialect Consistency
4. Multi-Voice Character Dialogue
5. Long-Form Audiobook Chapter
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def load_test_dataset():
    """Load Egyptian Arabic test dataset"""
    dataset_path = project_root / "data" / "test_cases" / "egyptian_arabic_test_dataset.json"
    with open(dataset_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_master_tts():
    """Load masterTTS.json for rare words"""
    master_path = project_root / "data" / "dictionaries" / "masterTTS.json"
    with open(master_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_sample1_phonological():
    """
    Sample 1: Phonological Features Showcase
    Select sentences with gemination, sun letters, emphatic spread, allophones
    Target: ~5 minutes (~750-1000 words)
    """
    dataset = load_test_dataset()
    sentences = dataset['test_sentences']

    # Select sentences with key phonological features
    selected = []
    for s in sentences:
        features = s.get('phonological_features', [])
        # Look for gemination, sun letters, emphatic, pharyngeal
        if any(keyword in ' '.join(features).lower() for keyword in
               ['gemination', 'sun letter', 'emphatic', 'pharyngeal', 'assimilation']):
            selected.append(s)

    # Build sample content
    lines = []
    lines.append("# Sample 1: Phonological Features Showcase")
    lines.append("# Purpose: Test X-SAMPA vs plain text for complex phonological features")
    lines.append("# Expected duration: ~5 minutes")
    lines.append("")

    for s in selected:
        lines.append(f"## Sentence {s['id']}: {s['category']}")
        lines.append(s['arabic'])
        lines.append(f"# Transliteration: {s['transliteration']}")
        lines.append(f"# English: {s['english']}")
        lines.append(f"# Features: {', '.join(s['phonological_features'])}")
        lines.append("")

    # Repeat to reach ~5 minutes (each sentence ~10-15 seconds, need ~20-25 repetitions)
    # For now, repeat the collection 3 times
    content = '\n'.join(lines)
    final_content = [content] * 3

    output_path = Path(__file__).parent / "samples" / "sample1_phonological.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n\n=== REPETITION ===\n\n'.join(final_content))

    print(f"✓ Generated: {output_path}")
    print(f"  Sentences: {len(selected)} unique, repeated 3 times")


def generate_sample2_rare_words():
    """
    Sample 2: Rare/Ambiguous Words
    Select uncommon words from masterTTS.json
    Target: ~5 minutes
    """
    master = load_master_tts()

    # Select 30 rare/interesting words
    rare_words = []

    # Prioritize words with:
    # - Foreign loan words
    # - Multiple dialectal variations
    # - Uncommon phoneme combinations

    for word_data in master[:100]:  # Check first 100 entries
        word = word_data['word']
        # Skip very common words
        if word not in ['من', 'في', 'على', 'إلى', 'هذا', 'ذلك', 'أن', 'لا', 'نعم']:
            rare_words.append(word_data)
            if len(rare_words) >= 30:
                break

    # Build sample content
    lines = []
    lines.append("# Sample 2: Rare and Ambiguous Words")
    lines.append("# Purpose: Test if X-SAMPA helps with uncommon vocabulary")
    lines.append("# Expected duration: ~5 minutes")
    lines.append("")

    for i, word_data in enumerate(rare_words, 1):
        word = word_data['word']
        ipa_msa = word_data.get('ipa_msa', '')
        ipa_eg = word_data.get('ipa_eg', '')

        lines.append(f"## Word {i}")
        lines.append(word)
        if ipa_msa:
            lines.append(f"# IPA (MSA): /{ipa_msa}/")
        if ipa_eg:
            lines.append(f"# IPA (EG): /{ipa_eg}/")
        lines.append("")

    # Create sentences with these words (repeat each word in a sentence)
    lines.append("")
    lines.append("# === TEST SENTENCES ===")
    lines.append("")

    for word_data in rare_words:
        word = word_data['word']
        # Simple sentence pattern: "هذا كلمة X" (This is word X)
        lines.append(f"هذا كلمة {word} وهي مهمة")
        lines.append("")

    output_path = Path(__file__).parent / "samples" / "sample2_rare_words.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"✓ Generated: {output_path}")
    print(f"  Words: {len(rare_words)}")


def generate_sample3_multidialect():
    """
    Sample 3: Multi-Dialect Consistency
    Same passage in MSA, Egyptian, Gulf
    Target: ~5 minutes (3x same passage in different dialects)
    """
    # Use a common passage that exists across dialects
    dataset = load_test_dataset()

    # Select 5-7 sentences for the base passage
    base_sentences = dataset['test_sentences'][:7]

    lines = []
    lines.append("# Sample 3: Multi-Dialect Consistency Test")
    lines.append("# Purpose: Test dialect switching and consistency")
    lines.append("# Expected duration: ~5 minutes (same passage x 3 dialects)")
    lines.append("")

    # MSA version
    lines.append("## VERSION 1: Modern Standard Arabic (MSA)")
    lines.append("# Voice: ar-SA-ZariyahNeural")
    lines.append("")
    for s in base_sentences:
        lines.append(s['arabic'])
    lines.append("")

    # Egyptian version
    lines.append("## VERSION 2: Egyptian Arabic (EG)")
    lines.append("# Voice: ar-EG-ShakirNeural")
    lines.append("")
    for s in base_sentences:
        lines.append(s['arabic'])
    lines.append("")

    # Gulf version
    lines.append("## VERSION 3: Gulf Arabic (UAE)")
    lines.append("# Voice: ar-AE-FatimaNeural")
    lines.append("")
    for s in base_sentences:
        lines.append(s['arabic'])
    lines.append("")

    output_path = Path(__file__).parent / "samples" / "sample3_multidialect.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"✓ Generated: {output_path}")
    print(f"  Sentences per dialect: {len(base_sentences)}")


def generate_sample4_dialogue():
    """
    Sample 4: Multi-Voice Character Dialogue
    Dialogue between narrator, male character, female character
    Target: ~5 minutes
    """
    lines = []
    lines.append("# Sample 4: Multi-Voice Character Dialogue")
    lines.append("# Purpose: Test character differentiation via voice switching")
    lines.append("# Expected duration: ~5 minutes")
    lines.append("")
    lines.append("# Characters:")
    lines.append("# - NARRATOR: ar-EG-SalmaNeural (female)")
    lines.append("# - AHMED: ar-EG-ShakirNeural (male, Egyptian)")
    lines.append("# - FATIMA: ar-SA-HamedNeural (male voice for contrast, or use another)")
    lines.append("")

    # Simple dialogue story
    dialogue = [
        ("NARRATOR", "في يوم من الأيام، كان هناك رجل يدعى أحمد"),
        ("NARRATOR", "خرج أحمد من بيته في الصباح الباكر"),
        ("AHMED", "السلام عليكم، صباح الخير"),
        ("NARRATOR", "قال أحمد لجاره"),
        ("FATIMA", "وعليكم السلام، صباح النور يا أحمد"),
        ("NARRATOR", "ردت فاطمة بابتسامة"),
        ("AHMED", "كيف حالك اليوم؟"),
        ("FATIMA", "الحمد لله، أنا بخير"),
        ("NARRATOR", "واستمر الحديث بينهما"),
        ("AHMED", "هل تريدين الذهاب إلى السوق؟"),
        ("FATIMA", "نعم، أريد شراء بعض الخضروات"),
        ("NARRATOR", "ذهبا معاً إلى السوق"),
        ("AHMED", "الشمس ساطعة اليوم"),
        ("FATIMA", "نعم، إنه يوم جميل"),
        ("NARRATOR", "وصلا إلى السوق المزدحم"),
        ("AHMED", "ماذا تحتاجين من السوق؟"),
        ("FATIMA", "أحتاج طماطم وبصل وخيار"),
        ("NARRATOR", "بدأت فاطمة تختار الخضروات"),
        ("AHMED", "هذه الطماطم طازجة جداً"),
        ("FATIMA", "سأشتري كيلو من هذه"),
    ]

    # Repeat dialogue to reach ~5 minutes
    for _ in range(3):
        for character, text in dialogue:
            lines.append(f"[{character}] {text}")
        lines.append("")
        lines.append("=== SCENE REPEAT ===")
        lines.append("")

    output_path = Path(__file__).parent / "samples" / "sample4_dialogue.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"✓ Generated: {output_path}")
    print(f"  Dialogue lines: {len(dialogue)} x 3 repetitions")


def generate_sample5_chapter():
    """
    Sample 5: Long-Form Audiobook Chapter
    Realistic audiobook excerpt with mixed content
    Target: ~5 minutes
    """
    dataset = load_test_dataset()

    # Use all 25 sentences to build a coherent "chapter"
    sentences = dataset['test_sentences']

    lines = []
    lines.append("# Sample 5: Long-Form Audiobook Chapter")
    lines.append("# Purpose: Test real-world audiobook production scenario")
    lines.append("# Expected duration: ~5 minutes")
    lines.append("")
    lines.append("# === CHAPTER 1: صباح في القاهرة (A Morning in Cairo) ===")
    lines.append("")

    # Organize sentences into paragraphs
    paragraph_breaks = [0, 5, 10, 15, 20, 25]

    for i in range(len(paragraph_breaks) - 1):
        start = paragraph_breaks[i]
        end = paragraph_breaks[i + 1]

        lines.append(f"## Paragraph {i + 1}")
        for s in sentences[start:end]:
            lines.append(s['arabic'] + ". ")
        lines.append("")

    # Repeat to reach ~5 minutes
    content = '\n'.join(lines)
    final_content = [content] * 2

    output_path = Path(__file__).parent / "samples" / "sample5_chapter.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n\n=== CHAPTER CONTINUES ===\n\n'.join(final_content))

    print(f"✓ Generated: {output_path}")
    print(f"  Total sentences: {len(sentences)} x 2 repetitions")


def main():
    """Generate all 5 test samples"""
    print("=" * 70)
    print("Generating Azure TTS Test Samples")
    print("=" * 70)
    print()

    # Create samples directory
    samples_dir = Path(__file__).parent / "samples"
    samples_dir.mkdir(exist_ok=True)

    # Generate each sample
    print("Sample 1: Phonological Features Showcase")
    generate_sample1_phonological()
    print()

    print("Sample 2: Rare and Ambiguous Words")
    generate_sample2_rare_words()
    print()

    print("Sample 3: Multi-Dialect Consistency")
    generate_sample3_multidialect()
    print()

    print("Sample 4: Multi-Voice Character Dialogue")
    generate_sample4_dialogue()
    print()

    print("Sample 5: Long-Form Audiobook Chapter")
    generate_sample5_chapter()
    print()

    print("=" * 70)
    print("All test samples generated successfully!")
    print(f"Location: {samples_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
