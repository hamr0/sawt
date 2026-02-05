
#!/usr/bin/env python3
"""
Main test runner for the Arabic TTS system
"""

import sys
import os
sys.path.append('src')

from src.main import ArabicTTS

def test_basic_functionality():
    """Test basic TTS functionality"""
    print("Testing Arabic TTS System...")
    
    # Test with MSA dialect
    tts = ArabicTTS("MSA")
    
    # Test simple text
    test_text = "مرحبا بك"
    try:
        result = tts.process_text(test_text)
        print(f"✓ Successfully processed: {test_text}")
        print(f"  Output: {result}")
        return True
    except Exception as e:
        print(f"✗ Error processing text: {e}")
        return False

def test_file_processing():
    """Test file processing functionality"""
    try:
        tts = ArabicTTS("MSA")
        # Check if test file exists
        if os.path.exists("data/test_cases/msa_sample.txt"):
            result = tts.process_file("data/test_cases/msa_sample.txt")
            print("✓ File processing successful")
            return True
        else:
            print("⚠ Test file not found, skipping file test")
            return True
    except Exception as e:
        print(f"✗ File processing error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Arabic TTS System Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    if test_basic_functionality():
        tests_passed += 1
    
    if test_file_processing():
        tests_passed += 1
    
    print("=" * 50)
    print(f"Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
        sys.exit(1)
