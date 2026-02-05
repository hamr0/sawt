"""
Smoke test for mishkal (Arabic diacritization library)
Tests basic functionality to verify installation
"""
import pytest
from mishkal.tashkeel import TashkeelClass


class TestMishkalSmoke:
    """Smoke tests for mishkal library"""
    
    @pytest.fixture
    def tashkeel(self):
        """Create TashkeelClass instance"""
        return TashkeelClass()
    
    def test_mishkal_import(self):
        """Test that mishkal imports successfully"""
        from mishkal import tashkeel
        assert tashkeel is not None
    
    def test_tashkeel_basic_diacritization(self, tashkeel):
        """Test basic diacritization on simple text"""
        # Test sentence 1: "How are you?" (Egyptian Arabic)
        text1 = "ازيك"
        result1 = tashkeel.tashkeel(text1)
        
        # Verify output is not empty and contains diacritics
        assert result1 is not None
        assert len(result1) > 0
        assert result1 != text1  # Should have diacritics added
        
        print(f"Test 1 - Input: {text1}")
        print(f"Test 1 - Output: {result1}")
    
    def test_tashkeel_common_phrase(self, tashkeel):
        """Test diacritization on common Arabic phrase"""
        # Test sentence 2: "Praise be to God"
        text2 = "الحمد لله"
        result2 = tashkeel.tashkeel(text2)
        
        assert result2 is not None
        assert len(result2) >= len(text2)  # Diacritics add length
        
        print(f"Test 2 - Input: {text2}")
        print(f"Test 2 - Output: {result2}")
    
    def test_tashkeel_with_sun_letter(self, tashkeel):
        """Test diacritization with sun letter (الشمس)"""
        # Test sentence 3: "The sun" (contains sun letter ش)
        text3 = "الشمس"
        result3 = tashkeel.tashkeel(text3)
        
        assert result3 is not None
        assert len(result3) > 0
        
        print(f"Test 3 - Input: {text3}")
        print(f"Test 3 - Output: {result3}")
    
    def test_tashkeel_preserves_already_diacritized(self, tashkeel):
        """Test that already diacritized text is handled correctly"""
        # Text with some diacritics already present
        text4 = "مَدْرَسَة"  # school (already diacritized)
        result4 = tashkeel.tashkeel(text4)
        
        assert result4 is not None
        assert len(result4) > 0
        
        print(f"Test 4 - Input: {text4}")
        print(f"Test 4 - Output: {result4}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
