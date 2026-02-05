# Arabic TTS - Localhost Setup Guide

## Quick Start (TL;DR)

```bash
cd /home/hamr/PycharmProjects/ArabicTTS

# Install dependencies
pip3 install -r requirements.txt

# Run the web application
python3 app.py

# Open browser to: http://localhost:5000
```

---

## Prerequisites

### System Requirements
- **Operating System:** Linux (Ubuntu 20.04+ recommended), macOS, or Windows
- **Python:** 3.9 or higher (You have: Python 3.10.12 ✓)
- **RAM:** 512MB minimum (1GB+ recommended)
- **Disk Space:** ~100MB for code and dependencies

### Required Software

**Already Installed on Your System:**
- ✅ Python 3.10.12
- ✅ pip3 (Python package manager)
- ✅ Git 2.34.1

**Will Be Installed via pip:**
- Flask (web framework)
- NumPy (numerical operations)
- Pandas (data manipulation)
- PyYAML (configuration)
- python-Levenshtein (string matching)
- pytest (testing)
- tqdm (progress bars)

---

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd /home/hamr/PycharmProjects/ArabicTTS
```

### 2. (Optional) Create Virtual Environment

**Recommended** to isolate dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

**To deactivate later:**
```bash
deactivate
```

### 3. Install Python Dependencies

```bash
# Install all required packages
pip3 install -r requirements.txt

# Verify installation
pip3 list | grep -E "Flask|numpy|pandas|pytest"
```

**Expected output:**
```
Flask          3.x.x
numpy          1.x.x
pandas         2.x.x
pytest         8.x.x
...
```

### 4. Verify Project Structure

```bash
# Check critical files exist
ls -la app.py src/main.py data/dictionaries/masterTTS.json templates/index.html

# Should show all files exist
```

### 5. Run System Tests (Optional but Recommended)

```bash
# Run the test suite
python3 test_system.py

# Or run with pytest
python3 -m pytest tests/ -v
```

---

## Running the Application

### Method 1: Web Application (Recommended)

```bash
# Start the Flask web server
python3 app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

**Access the web interface:**
1. Open your browser
2. Navigate to: `http://localhost:5000`
3. You should see the "Arabic TTS Parser" interface

**Using the Web Interface:**
1. Enter Arabic text in the textarea
2. Select a dialect (MSA, EG, Gulf, Levantine, Maghreb)
3. Click "Parse Text" to process
4. View JSON output below
5. Click "Download JSON" to save results

### Method 2: Python API (Programmatic)

```bash
# Start Python interactive shell
python3
```

```python
# Import the TTS processor
from src.main import ArabicTTS

# Create processor instance for MSA
tts = ArabicTTS("MSA")

# Process some text
text = "الْحَمْدُ لِلّٰهِ"
result = tts.process_text(text)

# View results
import json
print(json.dumps(result, ensure_ascii=False, indent=2))

# Save to file
tts.to_json(result, "output.json")
print("Saved to output.json")
```

### Method 3: Command Line Script

```bash
# Using the batch processor
python3 scripts/process_text.py

# Or process a specific file
python3 -c "
from src.main import ArabicTTS
tts = ArabicTTS('EG')
result = tts.process_file('data/test_cases/eg_sample.txt')
tts.to_json(result, 'output_eg.json')
print('Processed Egyptian sample')
"
```

---

## Configuration

### Port Configuration

**Default:** Port 5000

**To change port:**

Edit `app.py` (line 110):
```python
# Change this line:
app.run(host='0.0.0.0', port=5000, debug=True)

# To (for example, port 8080):
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Debug Mode

**Production deployment:** Set `debug=False` in `app.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

### Host Configuration

**Current:** `0.0.0.0` (accessible from network)

**Localhost only:**
```python
app.run(host='127.0.0.1', port=5000, debug=True)
```

---

## Testing

### Run All Tests

```bash
# Run full test suite
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ -v --cov=src
```

### Run Specific Tests

```bash
# Unit tests only
python3 -m pytest tests/unit/ -v

# Integration tests only
python3 -m pytest tests/integration/ -v

# Specific test file
python3 -m pytest tests/unit/test_dialects.py -v
```

### Test with Sample Files

```bash
# Test MSA sample
python3 -c "
from src.main import ArabicTTS
tts = ArabicTTS('MSA')
result = tts.process_file('data/test_cases/msa_sample.txt')
print('MSA test passed:', result['dialect'] == 'MSA')
"

# Test Egyptian sample
python3 -c "
from src.main import ArabicTTS
tts = ArabicTTS('EG')
result = tts.process_file('data/test_cases/eg_sample.txt')
print('EG test passed:', result['dialect'] == 'EG')
"
```

---

## Troubleshooting

### Issue 1: `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
# Install dependencies
pip3 install -r requirements.txt

# If using virtual environment, make sure it's activated
source venv/bin/activate
pip3 install -r requirements.txt
```

### Issue 2: Port 5000 Already in Use

**Check what's using port 5000:**
```bash
lsof -i :5000
```

**Solution 1: Kill the process**
```bash
kill -9 <PID>
```

**Solution 2: Use different port**
```bash
# Edit app.py and change port to 8080 or any available port
```

### Issue 3: `FileNotFoundError: data/dictionaries/masterTTS.json`

**Solution:**
```bash
# Verify file exists
ls -la data/dictionaries/masterTTS.json

# If missing, check git status
git status

# Restore from git if needed
git checkout data/dictionaries/masterTTS.json
```

### Issue 4: Permission Denied

**Solution:**
```bash
# Make sure files are readable
chmod -R 755 /home/hamr/PycharmProjects/ArabicTTS

# For scripts
chmod +x scripts/*.py
```

### Issue 5: Import Errors

**Problem:** `ImportError: cannot import name 'ArabicTTS'`

**Solution:**
```bash
# Make sure you're in the project root
cd /home/hamr/PycharmProjects/ArabicTTS

# Try running with module syntax
python3 -m src.main

# Or add project root to PYTHONPATH
export PYTHONPATH="/home/hamr/PycharmProjects/ArabicTTS:$PYTHONPATH"
```

### Issue 6: Empty Results or Errors

**Check dictionary loading:**
```python
python3 -c "
import json
with open('data/dictionaries/masterTTS.json') as f:
    data = json.load(f)
    print('Dictionary loaded:', 'EG' in data)
    print('EG entries:', len(data['EG']))
"
```

**Expected:** Should show True and a number (e.g., 100+)

### Issue 7: Browser Can't Connect

**Check if app is running:**
```bash
# In another terminal
curl http://localhost:5000

# Should return HTML
```

**Check firewall:**
```bash
# Ubuntu
sudo ufw status
sudo ufw allow 5000/tcp

# Check if port is listening
netstat -tuln | grep 5000
```

---

## Usage Examples

### Example 1: Basic Text Processing

```python
from src.main import ArabicTTS

# Initialize for Egyptian dialect
tts = ArabicTTS("EG")

# Process simple text
text = "مرحبا"
result = tts.process_text(text)

# Print results
import json
print(json.dumps(result, ensure_ascii=False, indent=2))
```

### Example 2: Process Multiple Dialects

```python
from src.main import ArabicTTS

text = "السلام عليكم"

for dialect in ["MSA", "EG", "Gulf", "Levantine", "Maghreb"]:
    tts = ArabicTTS(dialect)
    result = tts.process_text(text)
    print(f"\n{dialect}:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

### Example 3: Batch Processing

```python
from src.main import ArabicTTS
import os

tts = ArabicTTS("MSA")

# Process multiple texts
texts = [
    "الحمد لله",
    "كيف حالك",
    "شكرا جزيلا"
]

for i, text in enumerate(texts):
    result = tts.process_text(text)
    tts.to_json(result, f"output_{i+1}.json")
    print(f"Processed: {text}")
```

### Example 4: Web API Usage (with curl)

```bash
# Start the app
python3 app.py &

# Parse text via API
curl -X POST http://localhost:5000/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "مرحبا", "dialect": "EG"}'

# Download as JSON file
curl -X POST http://localhost:5000/download/json \
  -H "Content-Type: application/json" \
  -d '{"text": "السلام عليكم", "dialect": "MSA"}' \
  -o output.json

# Download master dictionary as CSV
curl http://localhost:5000/download/dictionary/csv -o masterTTS.csv
```

---

## Development Workflow

### Making Changes

1. **Edit source files** in `src/` directory
2. **Restart Flask app** to see changes (or use debug mode auto-reload)
3. **Run tests** to verify changes
4. **Commit changes** to git

### Adding New Dialect

1. Create new file: `src/dialects/new_dialect.py`
2. Add phonetic data to `data/dictionaries/masterTTS.json`
3. Update `DIALECTS` dict in `src/main.py`
4. Add test case: `tests/unit/test_new_dialect.py`
5. Run tests: `pytest tests/unit/test_new_dialect.py`

### Debugging

**Enable Flask debug mode** (already enabled by default):
```python
app.run(debug=True)  # Auto-reloads on code changes
```

**Use debug utility:**
```python
from src.utils.debug import debug_print

debug_print(result)  # Pretty prints data structures
```

**Add logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Processing text: {text}")
```

---

## API Reference

### Python API

#### ArabicTTS Class

```python
from src.main import ArabicTTS

# Constructor
tts = ArabicTTS(dialect: str)
# dialect: "MSA", "EG", "Gulf", "Levantine", or "Maghreb"

# Methods
result = tts.process_text(text: str) -> Dict
result = tts.process_file(filename: str) -> Dict
tts.to_json(data: Dict, filename: str) -> None
```

#### ArabicSyllabifier Class

```python
from src.main import ArabicSyllabifier

syllabifier = ArabicSyllabifier(dialect: str)
syllables = syllabifier.segment_syllables(word: str) -> List[List[str]]
pattern = syllabifier.classify_pattern(syllable: List[str]) -> str
ipa_result = syllabifier.map_to_ipa(word: str) -> List[Dict]
```

### Web API

#### POST /parse
Process Arabic text and return JSON.

**Request:**
```json
{
  "text": "Arabic text here",
  "dialect": "MSA"
}
```

**Response:**
```json
{
  "dialect": "MSA",
  "words": [...]
}
```

#### POST /download/json
Download processed text as JSON file.

**Request:** Same as /parse

**Response:** File download

#### GET /download/dictionary/csv
Export master dictionary as CSV.

**Response:** CSV file download

---

## Performance Tips

### 1. Use Caching for Repeated Words

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_process(text, dialect):
    tts = ArabicTTS(dialect)
    return tts.process_text(text)
```

### 2. Batch Processing

Use `scripts/batch_processor.py` for large text files instead of processing line-by-line.

### 3. Production Deployment

**Use Gunicorn instead of Flask development server:**

```bash
pip3 install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**With systemd service:**
```ini
[Unit]
Description=Arabic TTS Service
After=network.target

[Service]
User=hamr
WorkingDirectory=/home/hamr/PycharmProjects/ArabicTTS
Environment="PATH=/home/hamr/PycharmProjects/ArabicTTS/venv/bin"
ExecStart=/home/hamr/PycharmProjects/ArabicTTS/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

---

## Security Considerations

### For Localhost Development
- Default settings are fine (debug=True, host=0.0.0.0)

### For Production Deployment
1. **Disable debug mode:** `debug=False`
2. **Use reverse proxy:** Nginx or Apache in front
3. **Add rate limiting:** Flask-Limiter
4. **Validate input:** Already done in app.py
5. **Use HTTPS:** Let's Encrypt certificate
6. **Set proper CORS:** Configure Flask-CORS if needed

---

## Next Steps

After setting up:

1. **Read** `PROJECT_DOCUMENTATION.md` for comprehensive understanding
2. **Try examples** in the web interface with different dialects
3. **Explore** the master dictionary: `data/dictionaries/masterTTS.json`
4. **Run tests** to understand expected behavior
5. **Check OneNote documentation** at `/home/hamr/PycharmProjects/OneNote/Arabic TTS/`

---

## Quick Reference Commands

```bash
# Start web app
python3 app.py

# Run tests
python3 -m pytest tests/ -v

# Process text from Python
python3 -c "from src.main import ArabicTTS; tts=ArabicTTS('MSA'); print(tts.process_text('مرحبا'))"

# Check if app is running
curl http://localhost:5000

# Install dependencies
pip3 install -r requirements.txt

# Create virtual environment
python3 -m venv venv && source venv/bin/activate

# View logs (if running in background)
tail -f nohup.out
```

---

## Support & Documentation

- **Project Documentation:** `PROJECT_DOCUMENTATION.md`
- **README:** `README.md`
- **OneNote Docs:** `/home/hamr/PycharmProjects/OneNote/Arabic TTS/`
- **Code Comments:** Inline documentation in `src/` files
- **Test Examples:** `tests/` directory

---

## Success Checklist

After setup, verify:
- [ ] Dependencies installed (`pip3 list | grep Flask`)
- [ ] Flask app starts (`python3 app.py`)
- [ ] Web interface loads (`http://localhost:5000`)
- [ ] Can process text in web UI
- [ ] Tests pass (`pytest tests/`)
- [ ] Can import in Python (`from src.main import ArabicTTS`)
- [ ] Sample files process correctly

---

**You're all set!** The Arabic TTS system is ready to run on your localhost. Start with the web interface at `http://localhost:5000` and explore the phonetic processing capabilities.
