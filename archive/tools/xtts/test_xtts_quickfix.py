#!/usr/bin/env python3
"""
XTTS Quick Fix Test - Try to fix PyTorch 2.9 weights_only issue
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# QUICK FIX: Add safe globals before importing TTS
import torch
try:
    # Try the new PyTorch 2.6+ safe_globals approach
    # Need to add ALL XTTS classes that are serialized
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsAudioConfig

    # Add all known XTTS classes
    safe_classes = [XttsConfig, XttsAudioConfig]
    torch.serialization.add_safe_globals(safe_classes)
    print(f"✓ Added {len(safe_classes)} XTTS classes to safe globals")
except Exception as e:
    print(f"⚠ Could not add safe globals: {e}")
    print("  Trying alternative approach...")

# Now import TTS
from TTS.api import TTS
from src.main import ArabicTTS
import time

def test_xtts_arabic():
    """Test XTTS with Arabic text"""

    print("=" * 80)
    print("XTTS Arabic TTS Test (Quick Fix)")
    print("=" * 80)

    # Simple test sample
    test_text = 'صباح الخير يا أصدقائي'

    # Initialize pipeline
    print("\n1. Initializing Arabic TTS pipeline...")
    pipeline = ArabicTTS(dialect='EG')

    # Initialize XTTS
    print("\n2. Initializing XTTS...")
    os.environ['COQUI_TOS_AGREED'] = '1'

    try:
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        print(f"   Loading: {model_name}")

        tts = TTS(model_name, progress_bar=True, gpu=False)

        print(f"   ✓ Model loaded successfully!")
        print(f"   Languages: {tts.languages if hasattr(tts, 'languages') else 'Multiple including Arabic'}")

        # Quick test - plain text
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "quickfix_test.wav"

        print(f"\n3. Generating test audio...")
        print(f"   Text: {test_text}")

        start_time = time.time()
        tts.tts_to_file(
            text=test_text,
            language="ar",
            file_path=str(output_path)
        )
        elapsed = time.time() - start_time

        file_size = output_path.stat().st_size / 1024  # KB
        print(f"   ✓ Generated: {output_path}")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Size: {file_size:.1f} KB")

        print(f"\n{'=' * 80}")
        print("SUCCESS! XTTS is working!")
        print(f"{'=' * 80}")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        print(f"\n{'=' * 80}")
        print("FAILED - Need different fix approach")
        print(f"{'=' * 80}")
        return False


if __name__ == "__main__":
    success = test_xtts_arabic()
    sys.exit(0 if success else 1)
