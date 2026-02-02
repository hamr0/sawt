# Arabic TTS - Localhost Edition

**Status:** ✅ Ready to Run

This is the Arabic Text-to-Speech system, migrated from Replit to your local machine and fully configured for localhost development.

## What This Project Does

Converts Arabic text into IPA (International Phonetic Alphabet) phonetic representations with support for 5 major Arabic dialects. This provides the foundational text-processing layer needed for building complete Arabic TTS systems.

## Quick Start

```bash
cd /home/hamr/PycharmProjects/ArabicTTS
python3 app.py
```

Open browser: **http://localhost:5000**

## Documentation

📖 **Start Here:**
- **QUICK_START.md** - 3-minute getting started guide
- **PROJECT_DOCUMENTATION.md** - Complete technical overview (19KB)
- **LOCALHOST_SETUP_GUIDE.md** - Detailed setup & troubleshooting (14KB)

📂 **Also Available:**
- **OneNote Documentation:** `/home/hamr/PycharmProjects/OneNote/Arabic TTS/`
- **Original README:** `README.md`

## Key Features

- ✅ Multi-dialect support (MSA, Egyptian, Gulf, Levantine, Maghreb)
- ✅ Web interface with real-time processing
- ✅ Python API for programmatic access
- ✅ IPA/X-SAMPA phonetic output
- ✅ Syllable segmentation & pattern classification
- ✅ 19,581-line master phonetic dictionary
- ✅ JSON/CSV export functionality

## Setup Status

| Component | Status |
|-----------|--------|
| Dependencies | ✅ Installed |
| Imports | ✅ Verified |
| Processing | ✅ Tested |
| Flask App | ✅ Working |
| Port 5000 | ✅ Available |
| Documentation | ✅ Complete |

## Usage Examples

### Web Interface
1. Start: `python3 app.py`
2. Open: http://localhost:5000
3. Enter Arabic text
4. Select dialect
5. Click "Parse Text"

### Python API
```python
from src.main import ArabicTTS

tts = ArabicTTS("MSA")
result = tts.process_text("مرحبا")
print(result)
```

### Command Line
```bash
python3 -c "from src.main import ArabicTTS; tts=ArabicTTS('EG'); print(tts.process_text('السلام عليكم'))"
```

## Project Structure

```
ArabicTTS/
├── app.py                      # Flask web application
├── src/main.py                 # Core processor
├── data/dictionaries/          # Phonetic database (19K+ lines)
├── templates/index.html        # Web interface
├── tests/                      # Unit & integration tests
├── PROJECT_DOCUMENTATION.md    # Complete guide
├── LOCALHOST_SETUP_GUIDE.md    # Setup instructions
└── QUICK_START.md              # Quick reference
```

## Troubleshooting

**App won't start?**
```bash
./setup_localhost.sh
```

**Dependencies issue?**
```bash
pip3 install --user -r requirements.txt
```

**More help?**
Check `LOCALHOST_SETUP_GUIDE.md` (Troubleshooting section)

## Next Steps

1. ✅ **You are here** - System is ready!
2. 🚀 Start the app: `python3 app.py`
3. 📖 Read: `PROJECT_DOCUMENTATION.md`
4. 🧪 Test: `python3 -m pytest tests/ -v`
5. 🎯 Explore different dialects in the web interface

## Support

- **Comprehensive Documentation:** `PROJECT_DOCUMENTATION.md`
- **Setup Guide:** `LOCALHOST_SETUP_GUIDE.md`
- **Quick Reference:** `QUICK_START.md`
- **OneNote Docs:** `/home/hamr/PycharmProjects/OneNote/Arabic TTS/`

---

**Ready to go!** Start with: `python3 app.py`
