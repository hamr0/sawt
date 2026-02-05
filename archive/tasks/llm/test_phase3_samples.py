#!/usr/bin/env python3
"""Quick test of Phase 3 changes with sample words."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.main import ArabicTTS

# Test words that had UNKNOWN patterns before
test_words = ['للغاز', 'الطبيعي', 'البدري', 'تخفيض', 'محمد', 'نور']

print("=" * 70)
print("Phase 3: Testing Sample Words")
print("=" * 70)

tts = ArabicTTS('MSA')

unknown_count = 0
success_count = 0

for word in test_words:
    try:
        result = tts.process_text(word)
        syllables = result['words'][0]['syllables']

        has_unknown = False
        patterns = []
        for syl in syllables:
            pattern = syl['pattern']
            patterns.append(f"{syl['syllable']}({pattern})")
            if 'UNKNOWN' in pattern:
                has_unknown = True
                unknown_count += 1

        status = '✗' if has_unknown else '✓'
        patterns_str = ' + '.join(patterns)
        print(f"{status} {word:15} | {patterns_str}")

        if not has_unknown:
            success_count += 1

    except Exception as e:
        print(f"✗ {word:15} | ERROR: {str(e)[:50]}")

print("\n" + "=" * 70)
print(f"Results: {success_count}/{len(test_words)} success")
print(f"UNKNOWN patterns: {unknown_count}")

if unknown_count == 0:
    print("\n✅ Phase 3 implementation successful! No UNKNOWN patterns!")
else:
    print(f"\n⚠ Still have {unknown_count} UNKNOWN patterns")
