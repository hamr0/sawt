"""
Test script for Flask API audio generation endpoint
"""
import requests
import json

# Base URL (update if running on different host/port)
BASE_URL = "http://localhost:5000"

def test_generate_audio():
    """Test audio generation endpoint"""
    print("=" * 70)
    print("Testing Flask API: /generate_audio")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Basic Arabic text",
            "data": {
                "text": "السلام عليكم",
                "dialect": "EG",
                "use_ipa": False
            }
        },
        {
            "name": "Arabic text with IPA generation",
            "data": {
                "text": "صباح الخير",
                "dialect": "EG",
                "use_ipa": True
            }
        },
        {
            "name": "Simple word",
            "data": {
                "text": "شمس",
                "dialect": "MSA"
            }
        }
    ]
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print("-" * 70)
        print(f"Request: {json.dumps(test['data'], ensure_ascii=False, indent=2)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/generate_audio",
                json=test['data'],
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Success!")
                print(f"  Audio URL: {result.get('audio_url')}")
                print(f"  IPA: {result.get('ipa', 'N/A')[:100]}...")
                print(f"  Message: {result.get('message')}")
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"  {response.text}")
        
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection Error: Flask server not running?")
            print(f"  Start server with: python app.py")
            break
        except Exception as e:
            print(f"✗ Exception: {e}")


def test_parse_endpoint():
    """Test existing parse endpoint"""
    print("\n" + "=" * 70)
    print("Testing Flask API: /parse")
    print("=" * 70)
    
    data = {
        "text": "الشمس",
        "dialect": "EG"
    }
    
    print(f"\nRequest: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/parse",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success!")
            print(f"  Dialect: {result.get('dialect')}")
            print(f"  Words processed: {len(result.get('words', []))}")
        else:
            print(f"✗ Error: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection Error: Flask server not running?")
    except Exception as e:
        print(f"✗ Exception: {e}")


if __name__ == "__main__":
    print("\n" + "🚀 Flask API Test Suite")
    print("Make sure Flask server is running: python app.py\n")
    
    # Test endpoints
    test_parse_endpoint()
    test_generate_audio()
    
    print("\n" + "=" * 70)
    print("Test suite complete!")
    print("=" * 70)
