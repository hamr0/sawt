#!/usr/bin/env python3
"""
Multi-line Aware Character Detection for Arabic Dialogue
Handles:
1. Multi-line dialogues (colon on first line, continuation on next lines)
2. Em dash dialogues (standalone character speeches marked with –)
3. Colon-based attribution extraction with RTL awareness
"""

import re
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
from collections import Counter


class MultilineAwareDetector:
    """Detect characters with proper multi-line dialogue handling"""

    def __init__(self):
        # Stop words and verb indicators (presentation form)
        self.stop_words_and_verbs = {
            # Pronouns (standard + presentation forms)
            'هو', 'هي', 'ذلك', 'هذا', 'هذه', 'وهو', 'وهي', 'فهو', 'فهي',
            'وﻫﻮ', 'وﻫﻲ', 'ﻓﻬﻮ', 'ﻓﻬﻲ', 'ﻫﻮ', 'ﻫﻲ',
            # Conjunctions/particles
            'ثم', 'من', 'إلى', 'في', 'على', 'عن', 'كان', 'كانت', 'كانوا',
            'الذي', 'التي', 'ما', 'لا', 'نعم', 'إنه', 'إنها',
            # Verb-like patterns
            'قائلة', 'قائلا', 'هاتفة', 'هاتف', 'متكئة', 'جالسة',
            'ساخرا', 'ساخرة', 'يتثاءب', 'تتثاءب', 'يترنم', 'تترنم',
            'يبتسم', 'تبتسم', 'ﻳﺘﺜﺎءب', 'ﻳﱰﻧﻢ', 'ﻳﺤﻤﻠﻖ', 'ﻳﺘﻤﻄﻖ',
            'يقول', 'تقول', 'يغني', 'تغني', 'يتساءل', 'ﻳﻘﻮل', 'ﻳﻐﻨﻲ', 'ﻳﺘﺴﺎءل', 'ﺗﻘﻮل',
            # Adverbs and manner descriptions
            'باسما', 'باسمة', 'عاليا', 'ضاحكا', 'ﺑﺎﺳﻤًﺎ', 'ﻋﺎﻟﻴًﺎ', 'ﺿﺎﺣﻜًﺎ', 'ﻣﻮﺟﻬًﺎ',
            'كريهة', 'ًﻛﺮﻳﻬﺔ', 'متقلص', 'ٍﻣﺘﻘﻠﺺ', 'محشوة', 'ٍﻣﺤﺸﻮة',
            'هامس', 'ٍﻫﺎﻣﺲ', 'بدرجة', 'ﺑﺪرﺟﺔ', 'صوبها', 'ﺻﻮﺑﻬﺎ',
            'المائلة', 'املﺎﺋﻠﺔ', 'المعالم', 'املﻌﺎﻟﻢ', 'الصدى', 'اﻟﺼﺪى', 'الآخر', 'اﻵﺧﺮ',
            'ضحكة', 'ﺿﺤﻜﺔ', 'الكبير', 'الكبري', 'اﻟﻜﺒري', 'حيث', 'ﺣﻴﺚ',
            'أعلى', 'ٍأﻋﲆ', 'بصوت', 'ﺑﺼﻮت', 'بصعوبة', 'ﺑﺼﻌﻮﺑﺔ', 'بوجه', 'ﺑﻮﺟﻪ',
            'هدوء', 'ﻫﺪوء', 'باب', 'ﺑﺎب', 'فانتحى', 'ﻓﺎﻧﺘﺤﻰ',
            # Verbs in presentation form
            'لتتنفس', 'ﻟﺘﺘﻨﻔﺲ', 'فتبعته', 'ﻓﺘﺒﻌﺘﻪ', 'فتبعه', 'ﻓﺘﺒﻌﻪ', 'فرجع', 'ﻓﺮﺟﻊ',
            # Modifiers
            'بصوت', 'بغضب', 'برقة', 'بحدة', 'بقلق', 'ﺑﻐﻀﺐ', 'ﺑﺤﺪة', 'ﺑﺮﻗﱠﺔ',
            # Possessive nouns
            'امرأته', 'زوجها', 'زوجته', 'الرجل', 'المرأة', 'الكوخ', 'البيت',
            'اﻣﺮأﺗﻪ', 'زوﺟﻬﺎ', 'اﻟﻜﻮخ', 'اﻟﺒﻴﺖ', 'اﻟﺮﺟﻞ', 'اﻟﺪاﻳﺔ', 'اﻟﺼﻮت', 'اﻟﻈﻼم',
            'ﺟﻠﺒﺎﺑﻪ', 'رأﺳﻬﺎ', 'ﻛﻮﺧﻪ', 'ﻣﻴﱠﺰﺗﻪ', 'ٍﻣﻜﺘﻮم', 'ﺻﻮت', 'اﻵﻓﺎق',
        }

        # Verb patterns to filter (standard + presentation forms)
        self.verb_endings = {
            # Standard Arabic forms
            'قال', 'قالت', 'رد', 'ردت', 'صاح', 'صاحت', 'نادى', 'نادت', 'نادته',
            'توسلت', 'عادت', 'عاد', 'دخل', 'رقد', 'سكت', 'صمت', 'ضحك', 'قهقه',
            'أشفق', 'نظر', 'راح', 'تساءل', 'جاءه', 'صكت', 'نف', 'تناول',
            'هتف', 'جلس', 'نهض', 'تجشأ', 'تنهد',
            # Presentation form versions (with prefixes)
            'ﻓﻘﺎل', 'ﻓﻘﺎﻟﺖ', 'وﻗﺎل', 'وﻗﺎﻟﺖ', 'ﻗﺎل', 'ﻗﺎﻟﺖ',
            'ﻓﺼﺎح', 'وﺻﺎﺣﺖ', 'ﻓﻀﺤﻚ', 'وﺿﺤﻚ', 'ﻓﻘﻬﻘﻪ',
            'وﻧﺎدﺗﻪ', 'وﺗﻮﺳﻠﺖ', 'وﻋﺎد', 'وﻋﺎدت', 'ودﺧﻞ', 'ورﻗﺪ', 'وﺳﺎد',
            'ﻓﺴﻜﺖ', 'ﻓﺼﻤﺖ', 'ﻓﺄﺷﻔﻖ', 'ﻓﻨﻈﺮ', 'ﻓﺮاح', 'ﻓﺘﺴﺎءل', 'ﻓﺠﺎءه',
            'وﺻﻜﱠﺖ', 'ﻓﻨَﻔﱠ', 'وردد', 'ﺗﻨﺎول', 'ﺗﻮﱄ',
            'وﻫﺘﻒ', 'ﻓﺠﻠﺲ', 'ﺛﻢ', 'ﻓﺘﻨﻬﺪ',
        }

        # Character names discovered from text
        self.discovered_names = set()

        # Last speaker for em dash dialogues
        self.last_speaker = None

    def split_narration_and_attribution(self, before_colon: str) -> Tuple[str, str]:
        """
        Split "before colon" text into narration + attribution

        Example: "وﺿﺤﻚ ﺿﺤﻜﺔ ًﻛﺮﻳﻬﺔ وﻗﺎل"
        Returns: ("وﺿﺤﻚ ﺿﺤﻜﺔ ًﻛﺮﻳﻬﺔ", "وﻗﺎل")
        """
        # Look for speaker verb patterns (قال، صاحت، etc.)
        # These typically appear at the END of the before-colon text
        words = before_colon.split()

        # Scan from right to left (end to beginning) to find attribution verb
        for i in range(len(words) - 1, -1, -1):
            word = words[i].strip('،,.؛؟!')

            # Check if this word is a verb or starts with و/ف + verb
            if word in self.verb_endings:
                # Found verb! Split here
                narration = ' '.join(words[:i]) if i > 0 else ''
                attribution = ' '.join(words[i:])
                return narration.strip(), attribution.strip()

            # Check for prefixed verbs (وقال، فقالت, etc.)
            for prefix in ['و', 'ف', 'ب']:
                if word.startswith(prefix) and len(word) > len(prefix):
                    stem = word[len(prefix):]
                    if stem in self.verb_endings or any(stem.startswith(v) for v in ['قال', 'صاح', 'ناد', 'رد']):
                        # Found prefixed verb! Split here
                        narration = ' '.join(words[:i]) if i > 0 else ''
                        attribution = ' '.join(words[i:])
                        return narration.strip(), attribution.strip()

        # No verb found - entire text is attribution
        return '', before_colon.strip()

    def extract_speaker_from_attribution(self, attribution: str) -> Tuple[str, str]:
        """Extract speaker name using heuristic filtering"""
        attribution = attribution.strip()
        words = attribution.split()
        if not words:
            return 'Unknown', 'empty_attribution'

        # Check for discovered names first
        for name in self.discovered_names:
            if name in attribution:
                return name, 'discovered_name_match'

        # Find longest word not in stop lists
        candidates = []
        for word in words:
            clean_word = word.strip('،,.؛؟!')
            if len(clean_word) <= 2:
                continue
            if clean_word in self.stop_words_and_verbs:
                continue
            if clean_word in self.verb_endings:
                continue
            candidates.append((clean_word, len(clean_word)))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_name = candidates[0][0]
            self.discovered_names.add(best_name)
            return best_name, 'longest_word_heuristic'

        return 'Unknown', 'no_name_found'

    def segment_text_multiline(self, text: str) -> List[Dict]:
        """
        Segment text with multi-line dialogue support

        Patterns:
        1. [narration + attribution]: [dialogue line 1]
           [dialogue line 2 - continuation]
           [dialogue line 3 - continuation]
        2. – [character dialogue] (em dash = direct character speech)
        3. [narration without colon or em dash] = narrator narration
        """
        segments = []
        segment_id = 1

        lines = text.strip().split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Pattern 1: Colon-based dialogue (may span multiple lines)
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    before_colon = parts[0].strip()
                    after_colon = parts[1].strip()

                    # Split narration from attribution
                    narration, attribution = self.split_narration_and_attribution(before_colon)

                    # Create narrator segment for narration part (if exists)
                    if narration:
                        segments.append({
                            'segment_id': segment_id,
                            'line_num': i + 1,
                            'type': 'narrative',
                            'text': narration,
                            'speaker': 'Narrator',
                            'attribution': '-',
                            'detection_method': 'pre_dialogue_narration',
                            'confidence': 'high',
                            'status': 'success',
                            'needs_review': '-'
                        })
                        segment_id += 1

                    # Extract speaker from attribution
                    speaker, method = self.extract_speaker_from_attribution(attribution)
                    self.last_speaker = speaker

                    # Collect full dialogue (this line + continuation lines)
                    dialogue_lines = [after_colon]
                    j = i + 1

                    # Continue reading lines until we hit another dialogue marker or blank line
                    while j < len(lines):
                        next_line = lines[j].strip()

                        # Stop if blank line
                        if not next_line:
                            break

                        # Stop if next line has colon (new dialogue)
                        if ':' in next_line:
                            break

                        # Stop if next line starts with em dash (new dialogue)
                        if next_line.startswith('–') or next_line.startswith('—'):
                            break

                        # Otherwise, this is a continuation line
                        dialogue_lines.append(next_line)
                        j += 1

                    # Combine all dialogue lines
                    full_dialogue = ' '.join(dialogue_lines)

                    # Determine confidence
                    if speaker == 'Unknown':
                        confidence = 'low'
                        status = 'warning'
                        needs_review = 'Confirm_Speaker'
                    elif 'verb_pattern' in method or 'pattern_' in method:
                        confidence = 'high'
                        status = 'success'
                        needs_review = '-'
                    else:
                        confidence = 'medium'
                        status = 'success'
                        needs_review = '-'

                    segments.append({
                        'segment_id': segment_id,
                        'line_num': f"{i+1}-{j}",
                        'type': 'dialogue',
                        'text': full_dialogue,
                        'speaker': speaker,
                        'attribution': attribution,
                        'detection_method': f'colon_multiline+{method}',
                        'confidence': confidence,
                        'status': status,
                        'needs_review': needs_review
                    })
                    segment_id += 1

                    # Skip processed continuation lines
                    i = j
                    continue

            # Pattern 2: Em dash dialogue (character speech)
            elif line.startswith('–') or line.startswith('—'):
                # Remove em dash and get dialogue text
                dialogue_text = line[1:].strip()

                # Speaker is the last speaker we saw (from previous colon line)
                speaker = self.last_speaker if self.last_speaker else 'Unknown'

                segments.append({
                    'segment_id': segment_id,
                    'line_num': i + 1,
                    'type': 'dialogue',
                    'text': dialogue_text,
                    'speaker': speaker,
                    'attribution': 'em_dash',
                    'detection_method': 'em_dash_continuation',
                    'confidence': 'medium' if speaker != 'Unknown' else 'low',
                    'status': 'success' if speaker != 'Unknown' else 'warning',
                    'needs_review': '-' if speaker != 'Unknown' else 'Confirm_Speaker'
                })
                segment_id += 1
                i += 1
                continue

            # Pattern 3: Narrative (no colon, no em dash)
            else:
                segments.append({
                    'segment_id': segment_id,
                    'line_num': i + 1,
                    'type': 'narrative',
                    'text': line,
                    'speaker': 'Narrator',
                    'attribution': '-',
                    'detection_method': 'default',
                    'confidence': 'high',
                    'status': 'success',
                    'needs_review': '-'
                })
                segment_id += 1
                i += 1
                continue

        return segments

    def calculate_stats(self, segments: List[Dict]) -> Dict:
        """Calculate statistics"""
        total = len(segments)
        success = sum(1 for s in segments if s['status'] == 'success')
        warning = sum(1 for s in segments if s['status'] == 'warning')
        error = sum(1 for s in segments if s['status'] == 'error')

        dialogue_count = sum(1 for s in segments if s['type'] == 'dialogue')
        narrative_count = sum(1 for s in segments if s['type'] == 'narrative')

        high_conf = sum(1 for s in segments if s['confidence'] == 'high')
        medium_conf = sum(1 for s in segments if s['confidence'] == 'medium')
        low_conf = sum(1 for s in segments if s['confidence'] == 'low')

        flagged = sum(1 for s in segments if s['needs_review'] != '-')

        detection_methods = Counter(s['detection_method'] for s in segments)

        speakers = {}
        for seg in segments:
            speaker = seg['speaker']
            if speaker not in speakers:
                speakers[speaker] = {'segments': 0, 'speeches': 0}
            speakers[speaker]['segments'] += 1
            if seg['type'] == 'dialogue':
                speakers[speaker]['speeches'] += 1

        return {
            'total': total,
            'success': success,
            'warning': warning,
            'error': error,
            'success_rate': round(success / total * 100, 1) if total > 0 else 0,
            'dialogue_count': dialogue_count,
            'narrative_count': narrative_count,
            'dialogue_pct': round(dialogue_count / total * 100, 1) if total > 0 else 0,
            'high_conf': high_conf,
            'medium_conf': medium_conf,
            'low_conf': low_conf,
            'flagged': flagged,
            'flagged_pct': round(flagged / total * 100, 1) if total > 0 else 0,
            'detection_methods': dict(detection_methods),
            'speakers': speakers,
            'unique_speakers': len([s for s in speakers if speakers[s]['speeches'] > 0])
        }

    def export_to_csv(self, segments: List[Dict], output_path: Path):
        """Export to CSV"""
        stats = self.calculate_stats(segments)

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Type', 'Segment_ID', 'Line_Num', 'Text', 'Speaker',
                'Attribution', 'Detection_Method', 'Confidence',
                'Status', 'Needs_Review'
            ])

            # Data rows
            for seg in segments:
                writer.writerow([
                    'SEGMENT', seg['segment_id'], seg['line_num'], seg['text'],
                    seg['speaker'], seg.get('attribution', '-'),
                    seg['detection_method'], seg['confidence'],
                    seg['status'], seg['needs_review']
                ])

            # Stats rows
            writer.writerow([
                'Processing Stats',
                f"Total: {stats['total']}",
                f"Dialogue: {stats['dialogue_count']} ({stats['dialogue_pct']}%)",
                f"Narrative: {stats['narrative_count']}",
                f"Success: {stats['success']} ({stats['success_rate']}%)",
                f"Flagged: {stats['flagged']} ({stats['flagged_pct']}%)",
                '-', '-', '-', '-'
            ])

            speaker_stats = [f"Characters: {stats['unique_speakers']}"]
            for speaker, counts in sorted(stats['speakers'].items(), key=lambda x: x[1]['speeches'], reverse=True):
                if counts['speeches'] > 0:
                    speaker_stats.append(f"{speaker}: {counts['speeches']} speeches")
            while len(speaker_stats) < 10:
                speaker_stats.append('-')
            writer.writerow(['Character Stats'] + speaker_stats[:9])

            method_stats = [f"{m}: {c}" for m, c in sorted(stats['detection_methods'].items(), key=lambda x: x[1], reverse=True)]
            while len(method_stats) < 10:
                method_stats.append('-')
            writer.writerow(['Detection Methods'] + method_stats[:9])


def main():
    """Test multi-line aware detection"""

    book_path = Path("/home/hamr/Documents/PycharmProjects/ArabicTTS/tools/azure_tts/awalad-7aretna.txt")

    print("=" * 80)
    print("Multi-line Aware Character Detection Test")
    print("=" * 80)
    print(f"\nBook: {book_path.name}")

    # Read text
    with open(book_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"Size: {len(text):,} characters")

    # Detect
    print("\nRunning multi-line aware detection...")
    detector = MultilineAwareDetector()
    segments = detector.segment_text_multiline(text)
    print(f"✓ Detected {len(segments)} segments")
    print(f"✓ Discovered {len(detector.discovered_names)} character names")
    print(f"   Names: {', '.join(sorted(detector.discovered_names)[:10])}")

    # Stats
    stats = detector.calculate_stats(segments)

    print(f"\n{'=' * 80}")
    print("RESULTS")
    print(f"{'=' * 80}")
    print(f"\nTotal Segments: {stats['total']}")
    print(f"  Dialogue: {stats['dialogue_count']} ({stats['dialogue_pct']}%)")
    print(f"  Narrative: {stats['narrative_count']}")

    print(f"\nDetected Characters: {stats['unique_speakers']}")
    for speaker, counts in sorted(stats['speakers'].items(), key=lambda x: x[1]['speeches'], reverse=True):
        if counts['speeches'] > 0:
            print(f"  {speaker}: {counts['speeches']} speeches")

    print(f"\nConfidence:")
    print(f"  High: {stats['high_conf']}")
    print(f"  Medium: {stats['medium_conf']}")
    print(f"  Low: {stats['low_conf']} (flagged: {stats['flagged']})")

    print(f"\nDetection Methods:")
    for method, count in sorted(stats['detection_methods'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {method}: {count}")

    # Export
    output_dir = Path(__file__).parent / 'outputs'
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'multiline_aware_detection_{timestamp}.csv'

    detector.export_to_csv(segments, output_path)
    print(f"\n✓ Saved to: {output_path}")


if __name__ == '__main__':
    main()
