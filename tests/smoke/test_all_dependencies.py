"""
Comprehensive smoke tests for all project dependencies
Verifies that all critical components are installed and functional
"""
import pytest
import json
import subprocess
import os
from pathlib import Path


class TestAllDependencies:
    """Smoke tests for all project dependencies"""
    
    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        # Navigate up from tests/smoke/ to project root
        return Path(__file__).parent.parent.parent
    
    def test_mishkal_import(self):
        """Test that mishkal library imports successfully"""
        try:
            from mishkal import tashkeel
            assert tashkeel is not None
            print("✓ mishkal imported successfully")
        except ImportError as e:
            pytest.fail(f"mishkal import failed: {e}")
    
    def test_mishkal_basic_functionality(self):
        """Test mishkal basic diacritization"""
        from mishkal.tashkeel import TashkeelClass
        
        tashkeel = TashkeelClass()
        text = "السلام عليكم"
        result = tashkeel.tashkeel(text)
        
        assert result is not None
        assert len(result) > 0
        print(f"✓ mishkal diacritization works: {text} → {result}")
    
    def test_espeak_ng_installed(self):
        """Test that eSpeak NG is installed and accessible"""
        try:
            result = subprocess.run(
                ['espeak-ng', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0
            assert 'eSpeak NG' in result.stdout
            print(f"✓ eSpeak NG installed: {result.stdout.split()[0:3]}")
        except FileNotFoundError:
            pytest.fail("espeak-ng not found in PATH")
        except subprocess.TimeoutExpired:
            pytest.fail("espeak-ng command timed out")
    
    def test_espeak_ng_subprocess_call(self):
        """Test eSpeak NG subprocess call with basic synthesis"""
        output_file = '/tmp/smoke_test_espeak.wav'
        
        try:
            # Clean up any existing file
            if os.path.exists(output_file):
                os.remove(output_file)
            
            # Run eSpeak NG
            result = subprocess.run(
                ['espeak-ng', 'test', '-w', output_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0
            assert os.path.exists(output_file)
            assert os.path.getsize(output_file) > 0
            print(f"✓ eSpeak NG synthesis works: {os.path.getsize(output_file)} bytes")
            
            # Clean up
            os.remove(output_file)
            
        except subprocess.TimeoutExpired:
            pytest.fail("eSpeak NG synthesis timed out")
        except Exception as e:
            pytest.fail(f"eSpeak NG synthesis failed: {e}")
    
    def test_espeak_ng_arabic_voice(self):
        """Test eSpeak NG Arabic voice"""
        output_file = '/tmp/smoke_test_arabic.wav'
        
        try:
            # Clean up any existing file
            if os.path.exists(output_file):
                os.remove(output_file)
            
            # Run eSpeak NG with Arabic voice
            result = subprocess.run(
                ['espeak-ng', '-v', 'ar', 'مرحبا', '-w', output_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0
            assert os.path.exists(output_file)
            assert os.path.getsize(output_file) > 0
            print(f"✓ eSpeak NG Arabic voice works: {os.path.getsize(output_file)} bytes")
            
            # Clean up
            os.remove(output_file)
            
        except subprocess.TimeoutExpired:
            pytest.fail("eSpeak NG Arabic synthesis timed out")
        except Exception as e:
            pytest.fail(f"eSpeak NG Arabic synthesis failed: {e}")
    
    def test_espeak_ng_ipa_input(self):
        """Test eSpeak NG with IPA input (critical for pipeline)"""
        output_file = '/tmp/smoke_test_ipa.wav'
        
        try:
            # Clean up any existing file
            if os.path.exists(output_file):
                os.remove(output_file)
            
            # Run eSpeak NG with IPA input (X-SAMPA format)
            result = subprocess.run(
                ['espeak-ng', '-v', 'ar', '[[test]]', '-w', output_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0
            assert os.path.exists(output_file)
            assert os.path.getsize(output_file) > 0
            print(f"✓ eSpeak NG IPA input works: {os.path.getsize(output_file)} bytes")
            
            # Clean up
            os.remove(output_file)
            
        except subprocess.TimeoutExpired:
            pytest.fail("eSpeak NG IPA synthesis timed out")
        except Exception as e:
            pytest.fail(f"eSpeak NG IPA synthesis failed: {e}")
    
    def test_master_tts_json_exists(self, project_root):
        """Test that masterTTS.json exists and is readable"""
        master_tts_path = project_root / 'data' / 'dictionaries' / 'masterTTS.json'
        
        assert master_tts_path.exists(), f"masterTTS.json not found at {master_tts_path}"
        assert master_tts_path.is_file()
        print(f"✓ masterTTS.json exists: {master_tts_path}")
    
    def test_master_tts_json_loading(self, project_root):
        """Test loading masterTTS.json"""
        master_tts_path = project_root / 'data' / 'dictionaries' / 'masterTTS.json'
        
        try:
            with open(master_tts_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert isinstance(data, dict)
            assert len(data) > 0
            print(f"✓ masterTTS.json loaded: {len(data)} entries")
            
        except json.JSONDecodeError as e:
            pytest.fail(f"masterTTS.json is not valid JSON: {e}")
        except Exception as e:
            pytest.fail(f"Failed to load masterTTS.json: {e}")
    
    def test_master_tts_json_structure(self, project_root):
        """Test masterTTS.json has expected structure"""
        master_tts_path = project_root / 'data' / 'dictionaries' / 'masterTTS.json'
        
        with open(master_tts_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check for Egyptian Arabic dialect data
        eg_entries = [k for k in data.keys() if 'EG' in str(data.get(k, {}))]
        assert len(eg_entries) > 0, "No Egyptian Arabic (EG) entries found"
        print(f"✓ masterTTS.json has Egyptian Arabic entries: {len(eg_entries)}")
    
    def test_syllable_patterns_json_exists(self, project_root):
        """Test that syllable_patterns.json exists and is readable"""
        patterns_path = project_root / 'data' / 'dictionaries' / 'syllable_patterns.json'
        
        assert patterns_path.exists(), f"syllable_patterns.json not found at {patterns_path}"
        assert patterns_path.is_file()
        print(f"✓ syllable_patterns.json exists: {patterns_path}")
    
    def test_syllable_patterns_json_loading(self, project_root):
        """Test loading syllable_patterns.json"""
        patterns_path = project_root / 'data' / 'dictionaries' / 'syllable_patterns.json'
        
        try:
            with open(patterns_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert isinstance(data, dict)
            assert 'dialects' in data
            assert 'EG' in data['dialects']
            print(f"✓ syllable_patterns.json loaded successfully")
            
        except json.JSONDecodeError as e:
            pytest.fail(f"syllable_patterns.json is not valid JSON: {e}")
        except Exception as e:
            pytest.fail(f"Failed to load syllable_patterns.json: {e}")
    
    def test_syllable_patterns_structure(self, project_root):
        """Test syllable_patterns.json has expected patterns"""
        patterns_path = project_root / 'data' / 'dictionaries' / 'syllable_patterns.json'
        
        with open(patterns_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        eg_patterns = data['dialects']['EG']['patterns']
        expected_patterns = ['CV', 'CVC', 'CVV', 'CVCC', 'CVVC']
        
        for pattern in expected_patterns:
            assert pattern in eg_patterns, f"Pattern {pattern} not found"
        
        print(f"✓ syllable_patterns.json has all expected patterns: {expected_patterns}")
    
    def test_pytest_installed(self):
        """Test that pytest is installed"""
        import pytest as pt
        assert pt is not None
        print(f"✓ pytest installed: version {pt.__version__}")
    
    def test_pytest_cov_installed(self):
        """Test that pytest-cov is installed"""
        try:
            import pytest_cov
            assert pytest_cov is not None
            print(f"✓ pytest-cov installed")
        except ImportError:
            pytest.fail("pytest-cov not installed")
    
    def test_flask_installed(self):
        """Test that Flask is installed"""
        try:
            import flask
            assert flask is not None
            print(f"✓ Flask installed: version {flask.__version__}")
        except ImportError:
            pytest.fail("Flask not installed")
    
    def test_numpy_installed(self):
        """Test that NumPy is installed"""
        try:
            import numpy as np
            assert np is not None
            print(f"✓ NumPy installed: version {np.__version__}")
        except ImportError:
            pytest.fail("NumPy not installed")
    
    def test_pandas_installed(self):
        """Test that Pandas is installed"""
        try:
            import pandas as pd
            assert pd is not None
            print(f"✓ Pandas installed: version {pd.__version__}")
        except ImportError:
            pytest.fail("Pandas not installed")
    
    def test_all_critical_dependencies(self):
        """Summary test: verify all critical dependencies are available"""
        critical_deps = []
        
        # Test imports
        try:
            from mishkal import tashkeel
            critical_deps.append("mishkal")
        except ImportError:
            pass
        
        try:
            import flask
            critical_deps.append("flask")
        except ImportError:
            pass
        
        try:
            import pytest
            critical_deps.append("pytest")
        except ImportError:
            pass
        
        try:
            import numpy
            critical_deps.append("numpy")
        except ImportError:
            pass
        
        # Test espeak-ng
        try:
            result = subprocess.run(
                ['espeak-ng', '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                critical_deps.append("espeak-ng")
        except:
            pass
        
        expected_deps = ["mishkal", "flask", "pytest", "numpy", "espeak-ng"]
        missing_deps = set(expected_deps) - set(critical_deps)
        
        assert len(missing_deps) == 0, f"Missing critical dependencies: {missing_deps}"
        print(f"✓ All critical dependencies installed: {critical_deps}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
