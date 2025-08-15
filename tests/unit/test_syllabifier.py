import pytest
from src.core.syllabifier import ArabicSyllabifier

@pytest.fixture
def msa_syllabifier():
    return ArabicSyllabifier("MSA")

def test_cv_syllable(msa_syllabifier):
    result = msa_syllabifier.segment("مَ")
    assert result == [['مَ']]
    assert msa_syllabifier.classify_pattern(result[0]) == "CV"

def test_cvcc_validation(msa_syllabifier):
    valid = msa_syllabifier.validate_cvcc(['ب', 'ر', 'ق'])
    assert valid is True