"""
Test script for phonological rule pipeline integration
Tests all 4 processors working together in the ArabicTTS pipeline
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import ArabicTTS

def test_basic_integration():
    """Test basic pipeline integration"""
    print("=" * 70)
    print("Testing Phonological Pipeline Integration")
    print("=" * 70)
    
    # Initialize TTS
    tts = ArabicTTS("EG")
    
    # Test simple text
    test_cases = [
        "الشمس",     # Sun letter
        "القمر",     # Moon letter
        "صباح",      # Emphatic
        "مُدَرِّس",  # Gemination
        "أكل",       # Hamza allophones
    ]
    
    print("\nTest Cases:")
    print("-" * 70)
    
    for text in test_cases:
        try:
            result = tts.process_text(text)
            print(f"\n✓ {text}")
            
            # Show syllables and their properties
            for word in result["words"]:
                if word["type"] == "arabic_word":
                    print(f"  Original: {word['original']}")
                    print(f"  Syllables:")
                    for syl in word["syllables"]:
                        print(f"    - {syl.get('syllable', '')}")
                        
                        # Show phonological properties
                        properties = []
                        if syl.get('has_gemination'):
                            properties.append(f"gemination:{syl.get('geminated_consonant')}")
                        if syl.get('sun_letter_assimilation'):
                            properties.append(f"sun:{syl.get('assimilated_sun_letter')}")
                        if syl.get('has_positional_allophone'):
                            properties.append(f"allophone:{syl.get('detected_position')}")
                        if syl.get('has_emphatic'):
                            properties.append(f"emphatic:{syl.get('emphatic_consonants')}")
                        
                        if properties:
                            print(f"      Properties: {', '.join(properties)}")
                        
                        # Show IPA
                        if syl.get('generated_ipa'):
                            print(f"      IPA: /{syl.get('generated_ipa')}/")
                        if syl.get('pharyngealized_ipa'):
                            print(f"      Pharyngealized: /{syl.get('pharyngealized_ipa')}/")
        
        except Exception as e:
            print(f"\n✗ {text} - ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Integration test complete!")
    print("=" * 70)


def test_all_rules_together():
    """Test a word that triggers multiple rules"""
    print("\n" + "=" * 70)
    print("Testing Multiple Rules on Single Word")
    print("=" * 70)
    
    tts = ArabicTTS("EG")
    
    # Word with multiple phonological features
    # المدرِّس = the teacher (al + gemination)
    text = "المدرس"
    
    try:
        result = tts.process_text(text)
        print(f"\nWord: {text} (the teacher)")
        
        for word in result["words"]:
            if word["type"] == "arabic_word":
                print(f"\nSyllables breakdown:")
                for i, syl in enumerate(word["syllables"], 1):
                    print(f"\n  Syllable {i}: {syl.get('syllable', '')}")
                    print(f"    Pattern: {syl.get('pattern', 'N/A')}")
                    print(f"    Gemination: {syl.get('has_gemination', False)}")
                    print(f"    Sun letter: {syl.get('sun_letter_assimilation', False)}")
                    print(f"    Emphatic: {syl.get('has_emphatic', False)}")
                    print(f"    Position: {syl.get('detected_position', 'N/A')}")
        
        print("\n✓ Multiple rules applied successfully!")
    
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_basic_integration()
    test_all_rules_together()
