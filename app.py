
from flask import Flask, render_template, request, jsonify, Response, make_response
import sys
import os
import json
import csv
import io
sys.path.append('src')

from src.main import ArabicTTS

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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
