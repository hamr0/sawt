
from flask import Flask, render_template, request, jsonify, Response, make_response, send_file
import sys
import os
import json
import csv
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, Generator
sys.path.append('src')

from src.main import ArabicTTS
from src.integrations.espeak import ESpeakTTS
from src.integrations.polly import PollyTTS
from src.core.hierarchical_processor import HierarchicalProcessor

app = Flask(__name__)

# Initialize eSpeak TTS
espeak_tts = ESpeakTTS()

# Initialize Polly TTS (graceful degradation if AWS credentials not available)
polly_tts = None
try:
    polly_tts = PollyTTS()
except (ImportError, RuntimeError) as e:
    print(f"[INFO] Polly not available: {e}")

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


@app.route('/process_with_progress', methods=['POST'])
def process_with_progress():
    """
    Process Arabic text with real-time progress updates via Server-Sent Events (SSE).

    Expected JSON:
    {
        "text": "صباح الخير",
        "dialect": "EG",
        "expected_ipa": "sˁɑbɑːħ"  # Optional
    }

    Returns:
    Server-Sent Events stream with progress updates:
    - step: Current processing step (1-6)
    - step_name: Name of current step
    - rule: Current phonological rule (for step 3)
    - status: "pending", "processing", or "complete"
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        dialect = data.get('dialect', 'EG')
        expected_ipa = data.get('expected_ipa', None)

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        def generate_progress():
            """Generate SSE events with progress updates"""
            try:
                # Step 1: Diacritization (handled internally by ArabicTTS)
                yield _format_sse_event({
                    'step': 1,
                    'step_name': 'Diacritization',
                    'status': 'processing',
                    'message': 'Analyzing text and applying diacritization rules...'
                })

                # Step 2: Syllabification
                yield _format_sse_event({
                    'step': 2,
                    'step_name': 'Syllabification',
                    'status': 'processing',
                    'message': 'Segmenting words into syllables...'
                })

                # Step 3: Phonological Rules (with sub-steps)
                yield _format_sse_event({
                    'step': 3,
                    'step_name': 'Phonological Rules',
                    'status': 'processing',
                    'message': 'Applying phonological rules...'
                })

                # Step 3.1: Gemination
                yield _format_sse_event({
                    'step': 3,
                    'step_name': 'Phonological Rules',
                    'rule': 'Gemination',
                    'status': 'processing',
                    'message': 'Processing gemination (shadda)...'
                })

                # Step 3.2: Sun Letters
                yield _format_sse_event({
                    'step': 3,
                    'step_name': 'Phonological Rules',
                    'rule': 'Sun Letters',
                    'status': 'processing',
                    'message': 'Processing sun letter assimilation...'
                })

                # Step 3.3: Allophones
                yield _format_sse_event({
                    'step': 3,
                    'step_name': 'Phonological Rules',
                    'rule': 'Allophones',
                    'status': 'processing',
                    'message': 'Processing allophone variations...'
                })

                # Step 3.4: Emphatic
                yield _format_sse_event({
                    'step': 3,
                    'step_name': 'Phonological Rules',
                    'rule': 'Emphatic',
                    'status': 'processing',
                    'message': 'Processing emphatic spread...'
                })

                # Step 4: Context Rules (Position Detection)
                yield _format_sse_event({
                    'step': 4,
                    'step_name': 'Context Rules',
                    'status': 'processing',
                    'message': 'Analyzing positional context...'
                })

                # Step 5: IPA Generation
                yield _format_sse_event({
                    'step': 5,
                    'step_name': 'IPA Generation',
                    'status': 'processing',
                    'message': 'Generating IPA transcription...'
                })

                # Step 6: X-SAMPA Conversion
                yield _format_sse_event({
                    'step': 6,
                    'step_name': 'X-SAMPA Conversion',
                    'status': 'processing',
                    'message': 'Converting to X-SAMPA format...'
                })

                # Process the text using ArabicTTS
                tts = ArabicTTS(dialect)
                tts_result = tts.process_text(text)

                # Convert to hierarchical structure
                hierarchical_result = hierarchical_processor.process_result(
                    tts_result,
                    text,
                    applied_rules_mapping=None
                )

                # Add expected IPA comparison if provided
                if expected_ipa:
                    hierarchical_result['expected_ipa'] = expected_ipa
                    hierarchical_result = _compare_with_expected_ipa(
                        hierarchical_result,
                        expected_ipa
                    )

                # Mark all rules as complete
                yield _format_sse_event({
                    'step': 3,
                    'step_name': 'Phonological Rules',
                    'rule': 'Gemination',
                    'status': 'complete',
                    'message': 'Gemination processing complete'
                })

                yield _format_sse_event({
                    'step': 3,
                    'step_name': 'Phonological Rules',
                    'rule': 'Sun Letters',
                    'status': 'complete',
                    'message': 'Sun letter processing complete'
                })

                yield _format_sse_event({
                    'step': 3,
                    'step_name': 'Phonological Rules',
                    'rule': 'Allophones',
                    'status': 'complete',
                    'message': 'Allophone processing complete'
                })

                yield _format_sse_event({
                    'step': 3,
                    'step_name': 'Phonological Rules',
                    'rule': 'Emphatic',
                    'status': 'complete',
                    'message': 'Emphatic spread processing complete'
                })

                # Mark main steps as complete
                yield _format_sse_event({
                    'step': 1,
                    'step_name': 'Diacritization',
                    'status': 'complete',
                    'message': 'Diacritization complete'
                })

                yield _format_sse_event({
                    'step': 2,
                    'step_name': 'Syllabification',
                    'status': 'complete',
                    'message': 'Syllabification complete'
                })

                yield _format_sse_event({
                    'step': 3,
                    'step_name': 'Phonological Rules',
                    'status': 'complete',
                    'message': 'Phonological rules processing complete'
                })

                yield _format_sse_event({
                    'step': 4,
                    'step_name': 'Context Rules',
                    'status': 'complete',
                    'message': 'Context analysis complete'
                })

                yield _format_sse_event({
                    'step': 5,
                    'step_name': 'IPA Generation',
                    'status': 'complete',
                    'message': 'IPA generation complete'
                })

                yield _format_sse_event({
                    'step': 6,
                    'step_name': 'X-SAMPA Conversion',
                    'status': 'complete',
                    'message': 'X-SAMPA conversion complete'
                })

                # Send final result
                yield _format_sse_event({
                    'type': 'result',
                    'data': hierarchical_result
                })

            except Exception as e:
                import traceback
                traceback.print_exc()
                yield _format_sse_event({
                    'type': 'error',
                    'error': str(e)
                })

        return Response(
            generate_progress(),
            mimetype='text/event-stream'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _format_sse_event(event_data: Dict) -> str:
    """
    Format event data as Server-Sent Event.

    Args:
        event_data: Dictionary with event data

    Returns:
        Formatted SSE event string
    """
    event_json = json.dumps(event_data, ensure_ascii=False)
    return f'data: {event_json}\n\n'


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
    Generate audio from Arabic text using eSpeak or Polly

    Expected JSON:
    {
        "text": "السلام عليكم",
        "dialect": "EG",           # Optional, default: "MSA"
        "engine": "espeak",        # Optional, "espeak" or "polly", default: "espeak"
        "speed": 150,              # Optional, default: 150 (eSpeak only)
        "pitch": 50,               # Optional, default: 50 (eSpeak only)
        "use_ipa": false           # Optional, default: false (uses Arabic text directly)
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
        engine = data.get('engine', 'espeak').lower()
        speed = data.get('speed', 150)
        pitch = data.get('pitch', 50)
        use_ipa = data.get('use_ipa', False)

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        if engine not in ['espeak', 'polly']:
            return jsonify({'error': f'Invalid engine: {engine}. Must be "espeak" or "polly"'}), 400

        # Process text through ArabicTTS pipeline
        tts = ArabicTTS(dialect)
        result = tts.process_text(text)

        # Extract IPA from syllables
        ipa_parts = []
        xsampa_parts = []
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

                    # Also extract X-SAMPA
                    syl_xsampa = syllable.get('xsampa', '')
                    if syl_xsampa:
                        xsampa_parts.append(syl_xsampa)

        # Combine IPA and X-SAMPA parts
        full_ipa = ' '.join(ipa_parts) if ipa_parts else text
        full_xsampa = ' '.join(xsampa_parts) if xsampa_parts else ''

        if engine == 'espeak':
            # Generate eSpeak audio
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"output_{dialect}_{timestamp}.wav"
            output_path = str(AUDIO_DIR / filename)

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
                audio_url = f"/static/audio/{filename}"
                return jsonify({
                    'success': True,
                    'audio_url': audio_url,
                    'ipa': full_ipa,
                    'message': message,
                    'engine': 'eSpeak',
                    'processing_result': result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': message,
                    'engine': 'eSpeak'
                }), 500

        elif engine == 'polly':
            # Generate Polly audio
            if polly_tts is None:
                return jsonify({
                    'success': False,
                    'error': 'Polly is not available. AWS credentials not configured or boto3 not installed.',
                    'engine': 'Polly'
                }), 503

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"output_{dialect}_{timestamp}.mp3"
            output_path = str(AUDIO_DIR / filename)

            # Generate audio using Polly
            success, message = polly_tts.generate_audio(
                text=text,
                xsampa=full_xsampa,
                output_path=output_path,
                voice_id='Zeina' if dialect in ['MSA', 'EG'] else 'Zeina',
                engine='neural'
            )

            if success:
                audio_url = f"/static/audio/{filename}"
                return jsonify({
                    'success': True,
                    'audio_url': audio_url,
                    'ipa': full_ipa,
                    'message': message,
                    'engine': 'AWS Polly',
                    'processing_result': result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': message,
                    'engine': 'AWS Polly'
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
