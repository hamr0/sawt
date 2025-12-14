
from flask import Flask, render_template, request, jsonify, Response, make_response, send_file
import sys
import os
import json
import csv
import io
from pathlib import Path
from datetime import datetime
from typing import Dict
sys.path.append('src')

from src.main import ArabicTTS
from src.integrations.espeak import ESpeakTTS
from src.core.hierarchical_processor import HierarchicalProcessor

app = Flask(__name__)

# Initialize eSpeak TTS
espeak_tts = ESpeakTTS()

# Initialize hierarchical processor
hierarchical_processor = HierarchicalProcessor()

# Ensure static/audio directory exists
AUDIO_DIR = Path(__file__).parent / "static" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/parse', methods=['POST'])
def parse_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        dialect = data.get('dialect', 'MSA')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Process the text using ArabicTTS
        tts = ArabicTTS(dialect)
        result = tts.process_text(text)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process', methods=['POST'])
def process_hierarchical():
    """
    Process Arabic text and return hierarchical data structure (WORD + CHAR levels).

    This endpoint returns data in the format required for the matrix display:
    - WORD-level rows: One row per word with full word analysis
    - CHAR-level rows: Multiple rows per word, one for each character with role detection

    Expected JSON:
    {
        "text": "صباح الخير",
        "dialect": "EG",          # Optional, default: "EG"
        "expected_ipa": "sˁɑbɑːħ"  # Optional, for comparison highlighting
    }

    Returns:
    {
        "original_text": "صباح الخير",
        "dialect": "EG",
        "words": [
            {
                "type": "WORD",
                "word": "صباح",
                "position": "-",
                "original": "صباح",
                "diacritized": "صَبَاح",
                "syllable_pattern": "CV.CV",
                "syllable_index": "-",
                "syllable_role": "-",
                "phonology_rules": ["emphatic_spread"],
                "ipa": "sˁɑbɑːħ",
                "xsampa": "s_?Aba:X\\",
                "characters": [
                    {
                        "type": "CHAR",
                        "word": "صباح",
                        "position": "1-initial",
                        "original": "ص",
                        "diacritized": "صَ",
                        "syllable_pattern": "-",
                        "syllable_index": "1",
                        "syllable_role": "onset",
                        "phonology_rules": ["emphatic_spread"],
                        "ipa": "sˁ",
                        "xsampa": "s_?"
                    },
                    ...
                ]
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        dialect = data.get('dialect', 'EG')
        expected_ipa = data.get('expected_ipa', None)

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Step 1: Process the text using standard ArabicTTS pipeline
        tts = ArabicTTS(dialect)
        tts_result = tts.process_text(text)

        # Step 2: Convert to hierarchical structure with character-level analysis
        hierarchical_result = hierarchical_processor.process_result(
            tts_result,
            text,
            applied_rules_mapping=None  # Can be enhanced later
        )

        # Step 3: Add expected IPA comparison if provided
        if expected_ipa:
            hierarchical_result['expected_ipa'] = expected_ipa
            # Mark which words/chars match expected IPA
            hierarchical_result = _compare_with_expected_ipa(
                hierarchical_result,
                expected_ipa
            )

        return jsonify(hierarchical_result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def _compare_with_expected_ipa(result: Dict, expected_ipa: str) -> Dict:
    """
    Add comparison results with expected IPA.

    Args:
        result: Hierarchical processing result
        expected_ipa: Expected IPA for comparison

    Returns:
        Result with added comparison data
    """
    # Extract actual IPA from first word
    actual_ipa = ""
    for word in result.get('words', []):
        if word.get('type') == 'WORD':
            actual_ipa = word.get('ipa', '')
            break

    # Add comparison flag
    result['ipa_matches_expected'] = actual_ipa == expected_ipa
    result['actual_ipa'] = actual_ipa

    return result

@app.route('/download/json', methods=['POST'])
def download_json():
    try:
        data = request.get_json()
        text = data.get('text', '')
        dialect = data.get('dialect', 'MSA')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Process the text using ArabicTTS
        tts = ArabicTTS(dialect)
        result = tts.process_text(text)
        
        # Create JSON response for download
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        
        response = make_response(json_str)
        response.headers['Content-Disposition'] = f'attachment; filename=arabic_tts_output_{dialect.lower()}.json'
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    """
    Generate audio from Arabic text
    
    Expected JSON:
    {
        "text": "السلام عليكم",
        "dialect": "EG",  # Optional, default: "MSA"
        "speed": 150,     # Optional, default: 150
        "pitch": 50,      # Optional, default: 50
        "use_ipa": true   # Optional, default: false (uses Arabic text directly)
    }
    
    Returns:
    {
        "success": true,
        "audio_url": "/static/audio/output_12345.wav",
        "ipa": "...",
        "message": "Audio generated successfully"
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        dialect = data.get('dialect', 'MSA')
        speed = data.get('speed', 150)
        pitch = data.get('pitch', 50)
        use_ipa = data.get('use_ipa', False)
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"output_{dialect}_{timestamp}.wav"
        output_path = str(AUDIO_DIR / filename)
        
        # Process text through ArabicTTS pipeline
        tts = ArabicTTS(dialect)
        result = tts.process_text(text)
        
        # Extract IPA from syllables
        ipa_parts = []
        for word in result.get('words', []):
            if word.get('type') == 'arabic_word':
                for syllable in word.get('syllables', []):
                    # Try to get IPA from different sources
                    # Priority: pharyngealized_ipa > generated_ipa > ipa
                    syl_ipa = (
                        syllable.get('pharyngealized_ipa') or 
                        syllable.get('generated_ipa') or 
                        syllable.get('ipa', '')
                    )
                    if syl_ipa:
                        ipa_parts.append(syl_ipa)
        
        # Combine IPA parts
        full_ipa = ' '.join(ipa_parts) if ipa_parts else text
        
        # Generate audio
        if use_ipa and ipa_parts:
            # Use IPA input
            success, message = espeak_tts.generate_audio(
                full_ipa,
                output_path,
                speed=speed,
                pitch=pitch
            )
        else:
            # Use Arabic text directly
            success, message = espeak_tts.generate_audio_from_text(
                text,
                output_path,
                speed=speed,
                pitch=pitch
            )
        
        if success:
            # Return relative URL for audio file
            audio_url = f"/static/audio/{filename}"
            return jsonify({
                'success': True,
                'audio_url': audio_url,
                'ipa': full_ipa,
                'message': message,
                'processing_result': result
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/download/audio/<filename>')
def download_audio(filename):
    """
    Download audio file
    
    Args:
        filename: Name of the audio file
    
    Returns:
        Audio file as attachment
    """
    try:
        file_path = AUDIO_DIR / filename
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/csv', methods=['POST'])
def download_matrix_csv():
    """
    Download hierarchical matrix data as CSV.

    Expected JSON:
    {
        "text": "صباح الخير",
        "dialect": "EG",
        "expected_ipa": "sˁɑbɑːħ"  # Optional
    }

    Returns:
    CSV file with columns:
    Type, Word, Position, Original, Diacritized, Syllable_Pattern, Syllable_Index,
    Syllable_Role, Phonology_Rules, IPA, X-SAMPA

    Filename format: tts_matrix_YYYYMMDD_HHMMSS.csv
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        dialect = data.get('dialect', 'EG')
        expected_ipa = data.get('expected_ipa', None)

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Step 1: Process the text using standard ArabicTTS pipeline
        tts = ArabicTTS(dialect)
        tts_result = tts.process_text(text)

        # Step 2: Convert to hierarchical structure with character-level analysis
        hierarchical_result = hierarchical_processor.process_result(
            tts_result,
            text,
            applied_rules_mapping=None
        )

        # Step 3: Generate CSV from hierarchical data
        csv_content = _generate_hierarchical_csv(hierarchical_result)

        # Step 4: Create response with proper headers
        # Add UTF-8 BOM for Excel compatibility
        response_content = '\ufeff' + csv_content

        response = make_response(response_content)

        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tts_matrix_{timestamp}.csv'

        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def _generate_hierarchical_csv(result: Dict) -> str:
    """
    Generate hierarchical CSV content from processing result.

    CSV format with 11 columns:
    Type, Word, Position, Original, Diacritized, Syllable_Pattern, Syllable_Index,
    Syllable_Role, Phonology_Rules, IPA, X-SAMPA

    Args:
        result: Hierarchical processing result from HierarchicalProcessor

    Returns:
        CSV content as string with proper escaping and UTF-8 support
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Write CSV headers
    headers = [
        'Type', 'Word', 'Position', 'Original', 'Diacritized',
        'Syllable_Pattern', 'Syllable_Index', 'Syllable_Role',
        'Phonology_Rules', 'IPA', 'X-SAMPA'
    ]
    writer.writerow(headers)

    # Extract and flatten rows from hierarchical data
    rows = _flatten_matrix_rows(result)

    # Write data rows with proper escaping
    for row in rows:
        phonology_rules = row.get('phonology_rules', [])
        if isinstance(phonology_rules, list):
            phonology_rules_str = ';'.join(phonology_rules) if phonology_rules else '-'
        else:
            phonology_rules_str = str(phonology_rules) if phonology_rules else '-'

        csv_row = [
            row.get('type', ''),
            row.get('word', ''),
            row.get('position', '-'),
            row.get('original', ''),
            row.get('diacritized', ''),
            row.get('syllable_pattern', '-'),
            row.get('syllable_index', '-'),
            row.get('syllable_role', '-'),
            phonology_rules_str,
            row.get('ipa', ''),
            row.get('xsampa', '')
        ]

        writer.writerow(csv_row)

    csv_content = output.getvalue()
    output.close()

    return csv_content


def _flatten_matrix_rows(result: Dict) -> list:
    """
    Flatten hierarchical data structure into rows for CSV export.

    Converts nested WORD/CHAR structure into flat list of rows,
    maintaining hierarchy through Word column for CHAR rows.

    Args:
        result: Hierarchical processing result

    Returns:
        List of row dictionaries ready for CSV serialization
    """
    rows = []

    if not result.get('words') or not isinstance(result['words'], list):
        return rows

    for word_obj in result['words']:
        # Add WORD-level row
        word_row = {
            'type': word_obj.get('type', 'WORD'),
            'word': word_obj.get('word', ''),
            'position': '-',
            'original': word_obj.get('original', ''),
            'diacritized': word_obj.get('diacritized', ''),
            'syllable_pattern': word_obj.get('syllable_pattern', '-'),
            'syllable_index': '-',
            'syllable_role': '-',
            'phonology_rules': word_obj.get('phonology_rules', []),
            'ipa': word_obj.get('ipa', ''),
            'xsampa': word_obj.get('xsampa', '')
        }
        rows.append(word_row)

        # Add CHAR-level rows (children of this word)
        if word_obj.get('characters') and isinstance(word_obj['characters'], list):
            for char_obj in word_obj['characters']:
                char_row = {
                    'type': char_obj.get('type', 'CHAR'),
                    'word': char_obj.get('word', word_obj.get('word', '')),
                    'position': char_obj.get('position', '-'),
                    'original': char_obj.get('original', ''),
                    'diacritized': char_obj.get('diacritized', ''),
                    'syllable_pattern': '-',
                    'syllable_index': char_obj.get('syllable_index', '-'),
                    'syllable_role': char_obj.get('syllable_role', '-'),
                    'phonology_rules': char_obj.get('phonology_rules', []),
                    'ipa': char_obj.get('ipa', ''),
                    'xsampa': char_obj.get('xsampa', '')
                }
                rows.append(char_row)

    return rows


@app.route('/download/dictionary/csv')
def download_dictionary_csv():
    try:
        # Load the master dictionary
        with open('data/dictionaries/masterTTS.json', 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = ['Word', 'IPA', 'Syllables', 'Pattern', 'Dialect', 'Stress_Pattern']
        writer.writerow(headers)
        
        # Write data rows
        for word, data in master_data.items():
            if isinstance(data, dict):
                ipa = data.get('ipa', '')
                syllables = data.get('syllables', [])
                pattern = data.get('pattern', '')
                dialect = data.get('dialect', '')
                stress_pattern = data.get('stress_pattern', '')
                
                # Convert syllables list to string if it's a list
                if isinstance(syllables, list):
                    syllables_str = ' | '.join(syllables)
                else:
                    syllables_str = str(syllables)
                
                writer.writerow([word, ipa, syllables_str, pattern, dialect, stress_pattern])
        
        # Create response
        csv_content = output.getvalue()
        output.close()
        
        response = make_response(csv_content)
        response.headers['Content-Disposition'] = 'attachment; filename=masterTTS_dictionary.csv'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
