
# Arabic Text-to-Speech (TTS) System

A comprehensive Arabic Text-to-Speech system that processes Arabic text and converts it to IPA (International Phonetic Alphabet) representation with dialect-specific phonological rules and syllabification.

## Features

- **Multi-Dialect Support**: MSA (Modern Standard Arabic), Egyptian, Gulf, Levantine, and Maghreb dialects
- **Syllabification**: Advanced Arabic syllable segmentation with pattern classification (CV, CVC, CVCC, CVV)
- **IPA Mapping**: Accurate phonetic transcription with dialect-specific variations
- **Web Interface**: User-friendly Flask web application for real-time text processing
- **Export Options**: Download results as JSON or CSV format
- **Character Analysis**: Detailed position and type analysis for Arabic characters

## Project Structure

```
arabic-tts/
├── data/                   # Data resources
│   ├── dictionaries/       # Phonetic dictionaries
│   │   └── masterTTS.json  # Main dialect dictionary
│   └── test_cases/         # Sample texts for testing
│       ├── msa_sample.txt
│       └── eg_sample.txt
│
├── src/                    # Source code
│   ├── core/               # Core processing modules
│   │   ├── syllabifier.py
│   │   ├── ipa_mapper.py
│   │   └── tts_processor.py
│   ├── dialects/           # Dialect-specific implementations
│   │   ├── msa.py
│   │   ├── egyptian.py
│   │   ├── gulf.py
│   │   ├── levantine.py
│   │   └── maghreb.py
│   ├── utils/              # Helper functions
│   └── main.py             # Main TTS processor
│
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
│
├── templates/              # Web interface templates
│   └── index.html
│
├── app.py                  # Flask web application
├── requirements.txt        # Python dependencies
└── test_system.py          # System test runner
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Web Interface

1. Start the web application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. Enter Arabic text, select a dialect, and click "Parse Text"

4. Download results in JSON or CSV format

### Command Line

```python
from src.main import ArabicTTS

# Initialize with desired dialect
tts = ArabicTTS("MSA")  # or "EG", "Gulf", "Levantine", "Maghreb"

# Process text
text = "الْحَمْدُ لِلّٰهِ"
result = tts.process_text(text)

# Save to JSON
tts.to_json(result, "output.json")
```

### Example Output

Input: `الْحَمْدُ لِلّٰهِ`

```json
{
  "dialect": "MSA",
  "words": [
    {
      "type": "arabic_word",
      "original": "الْحَمْدُ",
      "syllables": [
        {
          "syllable": "الْ",
          "pattern": "CV",
          "ipa": "al",
          "position": "initial"
        },
        {
          "syllable": "حَمْ",
          "pattern": "CVC",
          "ipa": "ħam",
          "position": "medial"
        },
        {
          "syllable": "دُ",
          "pattern": "CV",
          "ipa": "du",
          "position": "final"
        }
      ]
    }
  ]
}
```

## Supported Dialects

- **MSA (Modern Standard Arabic)**: Standard formal Arabic
- **Egyptian (EG)**: Egyptian Arabic dialect
- **Gulf**: Gulf Arabic varieties
- **Levantine**: Levantine Arabic (Syrian, Lebanese, Palestinian, Jordanian)
- **Maghreb**: North African Arabic (Moroccan, Tunisian, Algerian)

## Syllable Patterns

The system recognizes and classifies the following Arabic syllable patterns:

- **CV**: Consonant + Vowel (e.g., مَ, لِ)
- **CVC**: Consonant + Vowel + Consonant (e.g., كَتَ, بِنْ)
- **CVCC**: Consonant + Vowel + Consonant + Consonant (with constraints)
- **CVV**: Consonant + Long Vowel (e.g., كاْ, لِيْ)

## Features

### Text Processing Pipeline

1. **Tokenization**: Split text into words, punctuation, and special characters
2. **Character Analysis**: Classify characters by type and position
3. **Word Grouping**: Group consecutive Arabic characters into words
4. **Syllabification**: Segment words into syllables with pattern classification
5. **IPA Mapping**: Apply dialect-specific phonetic rules

### Web Interface Features

- Real-time text processing
- Dialect selection
- JSON output display
- Download options (JSON/CSV)
- Arabic text input with RTL support

## Testing

Run the test suite:

```bash
python test_system.py
```

Run specific tests:

```bash
python -m pytest tests/ -v
```

## API Endpoints

- `GET /`: Main web interface
- `POST /parse`: Process Arabic text and return JSON
- `POST /download/json`: Download processed text as JSON file
- `GET /download/dictionary/csv`: Download master dictionary as CSV

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## Requirements

- Python 3.9+
- Flask
- NumPy
- Pandas
- PyYAML
- python-Levenshtein
- pytest

## License

This project is open source. See LICENSE file for details.

## Deployment

This application is designed to run on Replit. The web app will be available at the provided Replit URL when deployed.

## Technical Details

### Character Support

- Arabic letters (U+0600 to U+06FF)
- Tashkeel (diacritical marks)
- Special characters and punctuation
- English letters and numbers (pass-through)

### Phonological Rules

- Gemination handling
- Sun letter assimilation
- Dialect-specific sound changes
- Position-dependent allophone selection

## Troubleshooting

1. **Import Errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
2. **Dictionary Missing**: Check that `data/dictionaries/masterTTS.json` exists
3. **Web App Not Starting**: Verify Flask is installed and port 5000 is available

For more technical details, see the inline documentation in the source code.
