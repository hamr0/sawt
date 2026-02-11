#!/usr/bin/env python3
"""
RTL-Aware Character Detection for Arabic Dialogue
Handles right-to-left text with colon-based dialogue detection
Extracts names directly from text in their original encoding
"""

import re
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
from collections import Counter


class RTLAwareDetector:
    """Detect characters using RTL-aware colon-based dialogue patterns"""

    def __init__(self):
        # Stop words and verb indicators (in presentation form - extracted from text)
        # These will be filtered out when looking for names
        self.stop_words_and_verbs = {
            # Pronouns (standard + presentation forms)
            'هو', 'هي', 'ذلك', 'هذا', 'هذه', 'وهو', 'وهي', 'فهو', 'فهي',
            'وﻫﻮ', 'وﻫﻲ', 'ﻓﻬﻮ', 'ﻓﻬﻲ', 'ﻫﻮ', 'ﻫﻲ',
            # Conjunctions/particles
            'ثم', 'من', 'إلى', 'في', 'على', 'عن', 'كان', 'كانت', 'كانوا',
            'الذي', 'التي', 'ما', 'لا', 'نعم', 'إنه', 'إنها',
            # Verb-like patterns (common endings)
            'قائلة', 'قائلا', 'هاتفة', 'هاتف', 'متكئة', 'جالسة',
            'ساخرا', 'ساخرة', 'يتثاءب', 'تتثاءب', 'يترنم', 'تترنم',
            'يبتسم', 'تبتسم', 'يتمطيتﻤﻄﻖ', 'يحمل لﻖ', 'ﻳﺘﺜﺎءب', 'ﻳﱰﻧﻢ', 'ﻳﺤﻤﻠﻖ', 'ﻳﺘﻤﻄﻖ',
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
            # Possessive nouns (not character names)
            'امرأته', 'زوجها', 'زوجته', 'الرجل', 'المرأة', 'الكوخ', 'البيت',
            'اﻣﺮأﺗﻪ', 'زوﺟﻬﺎ', 'اﻟﻜﻮخ', 'اﻟﺒﻴﺖ', 'اﻟﺮﺟﻞ', 'اﻟﺪاﻳﺔ', 'اﻟﺼﻮت', 'اﻟﻈﻼم',
            'ﺟﻠﺒﺎﺑﻪ', 'رأﺳﻬﺎ', 'ﻛﻮﺧﻪ', 'ﻣﻴﱠﺰﺗﻪ', 'ٍﻣﻜﺘﻮم', 'ﺻﻮت', 'اﻵﻓﺎق',
        }

        # Verb patterns to filter (words starting or ending with these are likely verbs)
        self.verb_endings = {
            'قال', 'قالت', 'رد', 'ردت', 'صاح', 'صاحت', 'نادى', 'نادت', 'نادته',
            'توسلت', 'عادت', 'عاد', 'دخل', 'رقد', 'سكت', 'صمت', 'ضحك', 'قهقه',
            'أشفق', 'نظر', 'راح', 'تساءل', 'جاءه', 'صكت', 'نف', 'تنول',
            # Presentation form versions
            'ﻓﻘﺎل', 'ﻓﻘﺎﻟﺖ', 'وﻗﺎل', 'وﻗﺎﻟﺖ', 'ﻗﺎل', 'ﻗﺎﻟﺖ',
            'ﻓﺼﺎح', 'وﺻﺎﺣﺖ', 'ﻓﻀﺤﻚ', 'وﺿﺤﻚ', 'ﻓﻘﻬﻘﻪ',
            'وﻧﺎدﺗﻪ', 'وﺗﻮﺳﻠﺖ', 'وﻋﺎد', 'وﻋﺎدت', 'ودﺧﻞ', 'ورﻗﺪ', 'وﺳﺎد',
            'ﻓﺴﻜﺖ', 'ﻓﺼﻤﺖ', 'ﻓﺄﺷﻔﻖ', 'ﻓﻨﻈﺮ', 'ﻓﺮاح', 'ﻓﺘﺴﺎءل', 'ﻓﺠﺎءه',
            'وﺻﻜﱠﺖ', 'ﻓﻨَﻔﱠ', 'وردد', 'ﺗﻨﺎول', 'ﺗﻮﱄ',
        }

        # Character names discovered from the text
        self.discovered_names = set()

    def extract_speaker_from_attribution(self, attribution: str) -> Tuple[str, str]:
        """
        Extract speaker name from attribution text using heuristic approach

        Strategy: Find the longest, most "name-like" word after filtering out
        stop words, verbs, and modifiers.

        Returns: (speaker_name, detection_method)
        """
        # Clean attribution
        attribution = attribution.strip()

        # Split into words
        words = attribution.split()
        if not words:
            return 'Unknown', 'empty_attribution'

        # Strategy 1: Check for discovered names (from previous dialogues)
        for name in self.discovered_names:
            if name in attribution:
                return name, 'discovered_name_match'

        # Strategy 2: Find longest word that's not a stop word or verb
        candidates = []
        for word in words:
            # Clean word of punctuation
            clean_word = word.strip('،,.؛؟!')

            # Skip if empty or too short
            if len(clean_word) <= 2:
                continue

            # Skip if in stop words/verbs list
            if clean_word in self.stop_words_and_verbs:
                continue

            # Skip if exact match to verb ending
            if clean_word in self.verb_endings:
                continue

            # Add as candidate with its length
            candidates.append((clean_word, len(clean_word)))

        # If we have candidates, pick the longest one
        if candidates:
            # Sort by length (descending)
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_name = candidates[0][0]

            # Add to discovered names
            self.discovered_names.add(best_name)

            return best_name, 'longest_word_heuristic'

        return 'Unknown', 'no_name_found'

    def segment_text_by_colon(self, text: str) -> List[Dict]:
        """
        Segment text using colon as dialogue marker with RTL-aware name extraction
        """
        segments = []
        segment_id = 1

        # Split into lines
        lines = text.strip().split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check if line contains colon (dialogue marker)
            if ':' in line:
                # Split by colon
                parts = line.split(':', 1)
                if len(parts) == 2:
                    before_colon = parts[0].strip()
                    after_colon = parts[1].strip()

                    # Extract speaker using RTL-aware methods
                    speaker, method = self.extract_speaker_from_attribution(before_colon)

                    # Determine confidence and status
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
                        'line_num': line_num,
                        'type': 'dialogue',
                        'text': after_colon,
                        'speaker': speaker,
                        'attribution': before_colon,
                        'detection_method': f'colon+{method}',
                        'confidence': confidence,
                        'status': status,
                        'needs_review': needs_review
                    })
                    segment_id += 1
                    continue

            # No colon - treat as narrative
            segments.append({
                'segment_id': segment_id,
                'line_num': line_num,
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
    """Test RTL-aware detection"""

    book_path = Path("/home/hamr/Documents/PycharmProjects/ArabicTTS/tools/azure_tts/awalad-7aretna.txt")

    print("=" * 80)
    print("RTL-Aware Character Detection Test")
    print("=" * 80)
    print(f"\nBook: {book_path.name}")

    # Read text
    with open(book_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"Size: {len(text):,} characters, {len(text.split())} words")

    # Detect
    print("\nRunning RTL-aware detection...")
    detector = RTLAwareDetector()
    segments = detector.segment_text_by_colon(text)
    print(f"✓ Detected {len(segments)} segments")
    print(f"✓ Discovered {len(detector.discovered_names)} character names")
    print(f"   Names: {', '.join(sorted(detector.discovered_names))}")

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
    for method, count in sorted(stats['detection_methods'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {method}: {count}")

    # Export
    output_dir = Path(__file__).parent / 'outputs'
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'rtl_aware_detection_{timestamp}.csv'

    detector.export_to_csv(segments, output_path)
    print(f"\n✓ Saved to: {output_path}")


if __name__ == '__main__':
    main()
