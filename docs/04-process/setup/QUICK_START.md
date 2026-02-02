# Arabic TTS - Quick Start Guide

## ⚡ Instant Setup (3 Steps)

```bash
# 1. Navigate to project
cd /home/hamr/PycharmProjects/ArabicTTS

# 2. Run setup script
./setup_localhost.sh

# 3. Start the application
python3 app.py
```

**Open browser:** http://localhost:5000

---

## 🎯 What You Can Do

### Interactive TTS Demo Page (NEW!)
**URL:** http://localhost:5000/demo

A complete interactive demo showing the full TTS processing pipeline:

1. **Input Arabic text** - Type or upload .txt file
2. **Select dialect** - MSA, EG, Gulf, Levantine, Maghreb
3. **Process text** - Click "Process Text" button
4. **View pipeline stages:**
   - Stage 1: Diacritization (before/after)
   - Stage 2: Syllabification (syllable breakdown)
   - Stage 3: Phonological Processing (4 processors)
   - Stage 4: IPA Generation (phonetic transcription)
   - Stage 5: X-SAMPA Conversion (ASCII phonetics)
   - Stage 6: Audio Synthesis (playback + download)
5. **Listen to audio** - Inline HTML5 player
6. **Download outputs:**
   - JSON (complete pipeline data)
   - CSV (word comparison table)
   - WAV audio file

**Features:**
- Word-by-word comparison table (Original | Diacritized | X-SAMPA)
- Collapsible sections for each pipeline stage
- File upload support for batch processing
- Real-time audio generation and playback
- Comprehensive error handling

### Basic Web Interface
**URL:** http://localhost:5000

Simple interface for quick testing:
1. Enter Arabic text
2. Select dialect (MSA, EG, Gulf, Levantine, Maghreb)
3. Click "Parse Text"
4. View IPA phonetic output
5. Download as JSON

### Python API
```python
from src.main import ArabicTTS

# Initialize
tts = ArabicTTS("MSA")

# Process text
result = tts.process_text("مرحبا")

# View output
import json
print(json.dumps(result, ensure_ascii=False, indent=2))
```

### Command Line
```bash
# Quick test
python3 -c "from src.main import ArabicTTS; tts=ArabicTTS('EG'); print(tts.process_text('السلام عليكم'))"

# Process file
python3 -c "from src.main import ArabicTTS; tts=ArabicTTS('MSA'); tts.process_file('input.txt')"
```

---

## 📚 Documentation

- **PROJECT_DOCUMENTATION.md** - Complete system overview
- **LOCALHOST_SETUP_GUIDE.md** - Detailed setup instructions
- **README.md** - Original project documentation

---

## 🔧 Common Commands

```bash
# Start web app
python3 app.py

# Run tests
python3 -m pytest tests/ -v

# Check dependencies
pip3 list | grep -E "flask|numpy|pandas"

# Re-run setup
./setup_localhost.sh
```

---

## 🌍 Supported Dialects

- **MSA** - Modern Standard Arabic
- **EG** - Egyptian Arabic (most complete)
- **Gulf** - Gulf Arabic
- **Levantine** - Levantine Arabic
- **Maghreb** - Maghrebi Arabic

---

## ❓ Troubleshooting

**Port in use?**
```bash
# Check what's using port 5000
lsof -i :5000

# Or change port in app.py (line 110)
```

**Import errors?**
```bash
# Reinstall dependencies
pip3 install --user -r requirements.txt
```

**App won't start?**
```bash
# Run setup again
./setup_localhost.sh
```

---

## 📖 Example Usage

### Basic Processing
```python
from src.main import ArabicTTS

tts = ArabicTTS("EG")
result = tts.process_text("الحمد لله")
print(result["dialect"])  # Output: EG
```

### Multiple Dialects
```python
text = "مرحبا"
for dialect in ["MSA", "EG", "Gulf"]:
    tts = ArabicTTS(dialect)
    result = tts.process_text(text)
    print(f"{dialect}: {result}")
```

### Save to File
```python
tts = ArabicTTS("MSA")
result = tts.process_text("السلام عليكم")
tts.to_json(result, "output.json")
```

---

## 🎓 What This System Does

**Input:** Arabic text + Dialect selection
**Output:** IPA phonetic representation with:
- Syllable segmentation
- Pattern classification (CV, CVC, CVCC, CVV)
- Position-aware phonetics
- Dialect-specific sound variations

**Use Cases:**
- Building Arabic TTS systems
- Linguistic research
- Pronunciation tools
- Voice assistants
- Accessibility technology

---

## ✅ Success Checklist

After setup, verify:
- [ ] `./setup_localhost.sh` runs successfully
- [ ] `python3 app.py` starts the server
- [ ] http://localhost:5000 loads in browser
- [ ] Can process Arabic text in web UI
- [ ] Python imports work: `from src.main import ArabicTTS`

---

## 🚀 Next Steps

1. **Read the docs:** Open `PROJECT_DOCUMENTATION.md`
2. **Try different dialects:** Compare MSA vs EG pronunciation
3. **Explore the code:** Check out `src/main.py`
4. **Run tests:** `python3 -m pytest tests/ -v`
5. **Check OneNote:** `/home/hamr/PycharmProjects/OneNote/Arabic TTS/`

---

## 📍 File Locations

- **Project:** `/home/hamr/PycharmProjects/ArabicTTS/`
- **Documentation:** `/home/hamr/PycharmProjects/OneNote/Arabic TTS/`
- **Master Dictionary:** `data/dictionaries/masterTTS.json` (19,581 lines)
- **Web Template:** `templates/index.html`
- **Main Code:** `src/main.py`

---

**Ready to go! Start with:** `python3 app.py`
