
from flask import Flask, render_template, request, jsonify
import sys
import os
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
