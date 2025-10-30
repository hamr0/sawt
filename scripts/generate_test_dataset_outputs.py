#!/usr/bin/env python3
"""
Generate expected outputs for test dataset
Processes all test sentences and creates syllabification, IPA, and audio files
"""
import sys
import json
import os
from pathlib import Path
sys.path.insert(0, 'src')

from src.main import ArabicTTS
from src.integrations.espeak import ESpeakTTS


def load_test_dataset(filepath):
    """Load test dataset from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def process_sentence(tts, sentence_data):
    """Process a single sentence and generate expected outputs"""
    arabic_text = sentence_data['arabic']
    
    # Process through TTS pipeline
    result = tts.process_text(arabic_text)
    
    # Extract processed data
    processed_words = []
    for word in result.get('words', []):
        if word.get('type') == 'arabic_word':
            word_data = {
                'original': word['original'],
                'syllables': []
            }
            
            for syllable in word.get('syllables', []):
                syllable_data = {
                    'syllable': syllable.get('syllable', ''),
                    'pattern': syllable.get('pattern', ''),
                    'ipa': syllable.get('ipa', ''),
                    'generated_ipa': syllable.get('generated_ipa', ''),
                    'has_gemination': syllable.get('has_gemination', False),
                    'sun_letter_assimilation': syllable.get('sun_letter_assimilation', False),
                    'has_emphatic': syllable.get('has_emphatic', False)
                }
                
                # Add pharyngealized IPA if present
                if 'pharyngealized_ipa' in syllable:
                    syllable_data['pharyngealized_ipa'] = syllable['pharyngealized_ipa']
                
                word_data['syllables'].append(syllable_data)
            
            processed_words.append(word_data)
    
    return {
        'id': sentence_data['id'],
        'arabic': arabic_text,
        'transliteration': sentence_data['transliteration'],
        'english': sentence_data['english'],
        'category': sentence_data['category'],
        'processed_words': processed_words,
        'phonological_features': sentence_data['phonological_features']
    }


def generate_audio(espeak, sentence_data, output_dir):
    """Generate audio file for a sentence"""
    sentence_id = sentence_data['id']
    arabic_text = sentence_data['arabic']
    
    # Create output filename
    safe_transliteration = sentence_data['transliteration'].replace(' ', '_').replace('/', '_')
    audio_filename = f"sentence_{sentence_id:02d}_{safe_transliteration}.wav"
    audio_path = os.path.join(output_dir, audio_filename)
    
    # Generate audio from Arabic text
    success, msg = espeak.generate_audio_from_text(
        text=arabic_text,
        output_path=audio_path,
        speed=150,
        pitch=50,
        amplitude=100
    )
    
    if success:
        file_size = os.path.getsize(audio_path)
        return {
            'success': True,
            'filename': audio_filename,
            'path': audio_path,
            'size_bytes': file_size,
            'message': msg
        }
    else:
        return {
            'success': False,
            'filename': audio_filename,
            'error': msg
        }


def main():
    """Main processing function"""
    print("=" * 80)
    print("Egyptian Arabic Test Dataset - Expected Outputs Generator")
    print("=" * 80)
    print()
    
    # Paths
    project_root = Path(__file__).parent.parent
    dataset_path = project_root / "data" / "test_cases" / "egyptian_arabic_test_dataset.json"
    output_dir = project_root / "data" / "test_cases" / "reference_outputs"
    audio_dir = project_root / "data" / "test_cases" / "reference_audio"
    
    # Create output directories
    output_dir.mkdir(exist_ok=True)
    audio_dir.mkdir(exist_ok=True)
    
    # Load test dataset
    print(f"Loading test dataset from: {dataset_path}")
    dataset = load_test_dataset(dataset_path)
    print(f"✓ Loaded {len(dataset['test_sentences'])} test sentences")
    print()
    
    # Initialize TTS
    print("Initializing Egyptian Arabic TTS...")
    tts = ArabicTTS(dialect="EG")
    print("✓ TTS initialized")
    print()
    
    # Initialize eSpeak
    print("Initializing eSpeak NG...")
    try:
        espeak = ESpeakTTS()
        espeak_available = True
        print("✓ eSpeak NG initialized")
    except RuntimeError as e:
        espeak_available = False
        print(f"⚠ eSpeak NG not available: {e}")
        print("  Audio generation will be skipped")
    print()
    
    # Process all sentences
    print("Processing sentences...")
    print("-" * 80)
    
    expected_outputs = {
        'metadata': {
            'source_dataset': 'egyptian_arabic_test_dataset.json',
            'dialect': 'Egyptian Arabic (EG)',
            'total_sentences': len(dataset['test_sentences']),
            'generation_date': '2025-10-30',
            'tts_version': '1.0'
        },
        'sentences': [],
        'audio_files': []
    }
    
    for i, sentence_data in enumerate(dataset['test_sentences'], 1):
        sentence_id = sentence_data['id']
        arabic_text = sentence_data['arabic']
        
        print(f"[{i:2d}/{len(dataset['test_sentences'])}] Processing: {arabic_text}")
        
        # Generate expected TTS output
        processed = process_sentence(tts, sentence_data)
        expected_outputs['sentences'].append(processed)
        
        # Generate audio if eSpeak available
        if espeak_available:
            audio_result = generate_audio(espeak, sentence_data, audio_dir)
            expected_outputs['audio_files'].append({
                'sentence_id': sentence_id,
                'audio': audio_result
            })
            
            if audio_result['success']:
                size_kb = audio_result['size_bytes'] / 1024
                print(f"      ✓ Audio: {audio_result['filename']} ({size_kb:.1f} KB)")
            else:
                print(f"      ✗ Audio failed: {audio_result['error']}")
        
        print()
    
    print("-" * 80)
    print()
    
    # Save expected outputs
    output_file = output_dir / "expected_outputs.json"
    print(f"Saving expected outputs to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(expected_outputs, f, ensure_ascii=False, indent=2)
    
    output_size = os.path.getsize(output_file) / 1024
    print(f"✓ Expected outputs saved ({output_size:.1f} KB)")
    print()
    
    # Summary statistics
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total sentences processed: {len(expected_outputs['sentences'])}")
    
    if espeak_available:
        audio_success = sum(1 for a in expected_outputs['audio_files'] if a['audio']['success'])
        print(f"Audio files generated: {audio_success}/{len(expected_outputs['audio_files'])}")
        
        if audio_success > 0:
            total_audio_size = sum(
                a['audio']['size_bytes'] 
                for a in expected_outputs['audio_files'] 
                if a['audio']['success']
            )
            print(f"Total audio size: {total_audio_size / 1024:.1f} KB")
    
    print()
    print(f"Output directory: {output_dir}")
    if espeak_available:
        print(f"Audio directory: {audio_dir}")
    print()
    print("✓ Dataset generation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
