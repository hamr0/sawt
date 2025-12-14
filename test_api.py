#!/usr/bin/env python3
"""
Test the /process endpoint API.
"""

import json
import requests
import sys
from threading import Thread
import time

def run_flask_app():
    """Run Flask app in background."""
    from app import app
    app.run(host='127.0.0.1', port=5001, debug=False)

def test_api():
    """Test the /process endpoint."""

    # Wait for Flask to start
    time.sleep(2)

    base_url = 'http://127.0.0.1:5001'

    # Test data
    test_data = {
        'text': 'صباح',
        'dialect': 'EG'
    }

    print(f"\nTesting /process endpoint with: {test_data['text']}")

    try:
        response = requests.post(f'{base_url}/process', json=test_data)

        if response.status_code == 200:
            result = response.json()
            print("\nResponse received successfully!")
            print(json.dumps(result, ensure_ascii=False, indent=2)[:1000] + "...")

            # Verify structure
            assert 'words' in result, "Missing 'words' key"
            assert len(result['words']) > 0, "No words in result"

            word = result['words'][0]
            assert word.get('type') == 'WORD', "First entry should be WORD type"
            assert 'characters' in word, "WORD should have 'characters'"

            chars = word['characters']
            for char in chars:
                assert char.get('type') == 'CHAR', f"Character should be CHAR type, got {char.get('type')}"
                assert 'syllable_role' in char, "Missing syllable_role"
                assert 'phonology_rules' in char, "Missing phonology_rules"

            print("\n✓ API test passed!")
        else:
            print(f"Error: Status code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Start Flask in background
    app_thread = Thread(target=run_flask_app, daemon=True)
    app_thread.start()

    # Test API
    test_api()
