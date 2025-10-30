#!/usr/bin/env python3
"""
Manual audio quality testing script
Tests the complete TTS pipeline with various inputs
"""
import requests
import json
import os
import time
from pathlib import Path

BASE_URL = "http://localhost:5000"

def test_audio_generation():
    """Test audio generation with various inputs"""
    print("=" * 70)
    print("🎵 MANUAL AUDIO QUALITY TESTING")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Test 1: Simple Greeting (Egyptian)",
            "data": {
                "text": "السلام عليكم",
                "dialect": "EG",
                "use_ipa": False,
                "speed": 150,
                "pitch": 50
            }
        },
        {
            "name": "Test 2: Morning Greeting with IPA (Egyptian)",
            "data": {
                "text": "صباح الخير",
                "dialect": "EG",
                "use_ipa": True,
                "speed": 150,
                "pitch": 50
            }
        },
        {
            "name": "Test 3: Simple Word - Sun (MSA)",
            "data": {
                "text": "الشمس",
                "dialect": "MSA",
                "use_ipa": False
            }
        },
        {
            "name": "Test 4: Simple Word - Moon (MSA)",
            "data": {
                "text": "القمر",
                "dialect": "MSA",
                "use_ipa": False
            }
        },
        {
            "name": "Test 5: Emphatic Consonants (Egyptian)",
            "data": {
                "text": "صباح",
                "dialect": "EG",
                "use_ipa": True
            }
        },
        {
            "name": "Test 6: Complex Sentence (Egyptian)",
            "data": {
                "text": "أنا أحب اللغة العربية",
                "dialect": "EG",
                "use_ipa": False
            }
        },
        {
            "name": "Test 7: Fast Speech",
            "data": {
                "text": "مرحبا",
                "dialect": "EG",
                "speed": 200,
                "pitch": 50
            }
        },
        {
            "name": "Test 8: Slow Speech",
            "data": {
                "text": "مرحبا",
                "dialect": "EG",
                "speed": 100,
                "pitch": 50
            }
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"{test['name']}")
        print(f"{'='*70}")
        print(f"Request Data:")
        print(json.dumps(test['data'], ensure_ascii=False, indent=2))
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/generate_audio",
                json=test['data'],
                timeout=30
            )
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if audio file exists
                audio_url = result.get('audio_url', '')
                audio_path = Path(__file__).parent.parent / audio_url.lstrip('/')
                
                file_exists = audio_path.exists()
                file_size = audio_path.stat().st_size if file_exists else 0
                
                print(f"\n✅ SUCCESS")
                print(f"  Audio URL: {audio_url}")
                print(f"  File Path: {audio_path}")
                print(f"  File Exists: {'✓' if file_exists else '✗'}")
                print(f"  File Size: {file_size:,} bytes")
                print(f"  IPA: {result.get('ipa', 'N/A')[:80]}...")
                print(f"  Generation Time: {duration:.2f}s")
                print(f"  Message: {result.get('message')}")
                
                results.append({
                    'test': test['name'],
                    'success': True,
                    'file_size': file_size,
                    'duration': duration,
                    'audio_path': str(audio_path)
                })
                
                # Play audio command suggestion
                if file_exists:
                    print(f"\n  🔊 Play audio with:")
                    print(f"     aplay {audio_path}")
                    print(f"     or")
                    print(f"     ffplay -nodisp -autoexit {audio_path}")
                
            else:
                print(f"\n❌ ERROR: {response.status_code}")
                print(f"  Response: {response.text}")
                results.append({
                    'test': test['name'],
                    'success': False,
                    'error': response.text
                })
        
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Connection Error: Flask server not running?")
            print(f"  Start server with: python app.py")
            return
        except Exception as e:
            print(f"\n❌ Exception: {e}")
            results.append({
                'test': test['name'],
                'success': False,
                'error': str(e)
            })
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r.get('success'))
    total_count = len(results)
    
    print(f"\nSuccess Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    print("\nResults:")
    for r in results:
        status = "✅" if r.get('success') else "❌"
        print(f"  {status} {r['test']}")
        if r.get('success'):
            print(f"      Size: {r.get('file_size', 0):,} bytes, Time: {r.get('duration', 0):.2f}s")
    
    # Audio files location
    if success_count > 0:
        audio_dir = Path(__file__).parent.parent / "static" / "audio"
        print(f"\n📁 Audio files saved to: {audio_dir}")
        print(f"   Total files: {len(list(audio_dir.glob('*.wav')))} WAV files")


def test_server_health():
    """Check if Flask server is running"""
    print("\n🔍 Checking Flask server...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running")
            return True
        else:
            print(f"⚠️  Flask server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask server is not running")
        print("\nTo start the server:")
        print("  cd /home/hamr/Documents/PycharmProjects/ArabicTTS")
        print("  python3 app.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎵 Arabic TTS Manual Audio Testing")
    print("=" * 70)
    
    if test_server_health():
        print("\nStarting audio generation tests...\n")
        time.sleep(1)
        test_audio_generation()
    else:
        print("\n⚠️  Cannot run tests without Flask server")
    
    print("\n" + "=" * 70)
    print("Testing complete!")
    print("=" * 70)
