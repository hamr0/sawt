#!/usr/bin/env python3
"""
Colon-Based Character Detection for Arabic Dialogue
Detects dialogue using : (colon) as the dialogue marker
"""

import re
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
from collections import Counter


class ColonBasedDetector:
    """Detect characters using colon-based dialogue patterns"""

    def __init__(self):
        # Known character names
        self.known_names = {
            'أدهم', 'إدريس', 'أميمة', 'جبلاوي', 'قدري', 'همام', 'هند',
            'جبل', 'رفاعة', 'قاسم', 'عرفة', 'الداية'
        }

        # Speaker verbs that come before names
        self.speaker_verbs = [
            'قال', 'قالت', 'رد', 'ردت', 'أجاب', 'أجابت',
            'تحدث', 'تحدثت', 'صاح', 'صاحت', 'نادى', 'نادت', 'نادته',
            'هتف', 'هتفت', 'سأل', 'سألت', 'تساءل', 'تساءلت',
            'ضحك', 'ضحكت', 'بكى', 'بكت', 'صرخ', 'صرخت',
            'همس', 'همست', 'غنى', 'غنت', 'يترنم', 'تترنم',
            'يقول', 'تقول', 'يرد', 'ترد', 'يصيح', 'تصيح',
            'ينادي', 'تنادي', 'يهتف', 'تهتف', 'يسأل', 'تسأل',
            'يتساءل', 'تتساءل'
        ]

    def extract_names_from_text(self, text: str) -> Set[str]:
        """
        Extract character names from lines with colons
        Strategy: Look at all words in "before colon" part and identify likely names
        """
        found_names = set()

        # Get all text before colons
        for line in text.split('\n'):
            if ':' in line:
                before_colon = line.split(':', 1)[0]
                # Split into words and add each word as potential name
                words = before_colon.split()
                for word in words:
                    # Clean up punctuation
                    word = word.strip('،,.؟!؛')
                    if len(word) > 2:  # Names are usually > 2 characters
                        found_names.add(word)

        # Add known names from outside (these might be in presentation forms from the text itself)
        # We'll extract them from the actual text, not from standard Arabic
        found_names.update(self.known_names)

        # Filter out obvious stop words and common words
        stop_words = {
            'هو', 'هي', 'ذلك', 'هذا', 'هذه', 'كان', 'كانت', 'كانوا',
            'وهو', 'وهي', 'ثم', 'من', 'إلى', 'في', 'على', 'عن',
            'الذي', 'التي', 'هذه', 'تلك', 'ما', 'لا', 'نعم',
            'قال', 'قالت', 'يقول', 'تقول', 'قائلة', 'بصوت',
            'وقال', 'فقال', 'فقالت', 'ردت', 'رد', 'أجاب', 'أجابت'
        }
        found_names = {name for name in found_names if name not in stop_words and len(name) > 1}

        return found_names

    def segment_text_by_colon(self, text: str) -> List[Dict]:
        """
        Segment text using colon as dialogue marker
        Pattern: [name/verb] + : + dialogue text
        """
        # Extract character names first
        character_names = self.extract_names_from_text(text)
        print(f"   Extracted {len(character_names)} character names")
        print(f"   Names: {', '.join(sorted(character_names))}")

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

                    # Try to find speaker in "before colon" part
                    speaker = self.find_speaker(before_colon, character_names)

                    if speaker != 'Unknown':
                        # Found attributed dialogue
                        segments.append({
                            'segment_id': segment_id,
                            'line_num': line_num,
                            'type': 'dialogue',
                            'text': after_colon,
                            'speaker': speaker,
                            'attribution': before_colon,
                            'detection_method': 'colon_pattern',
                            'confidence': 'high',
                            'status': 'success',
                            'needs_review': '-'
                        })
                        segment_id += 1
                        continue

            # No colon or no speaker found - treat as narrative
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

    def find_speaker(self, attribution_text: str, character_names: Set[str]) -> str:
        """
        Find speaker name in attribution text using simple string search
        This works even with Unicode presentation forms!

        Examples:
        - "قال أدهم" → أدهم (if أدهم in character_names)
        - "وصاحت أميمة بغضب" → أميمة (if أميمة in character_names)
        - "ثم قال" → Unknown (no name found)
        """
        # Simple approach: Check if any character name appears in attribution
        # This works regardless of Unicode presentation forms!
        for name in character_names:
            # Simple substring search - works with presentation forms
            if name in attribution_text:
                return name

        # No character name found - return Unknown
        return 'Unknown'

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
            'high_conf': high_conf,
            'medium_conf': medium_conf,
            'low_conf': low_conf,
            'flagged': flagged,
            'flagged_pct': round(flagged / total * 100, 1) if total > 0 else 0,
            'detection_methods': dict(detection_methods),
            'speakers': speakers
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
                f"Dialogue: {stats['dialogue_count']}",
                f"Narrative: {stats['narrative_count']}",
                f"Success: {stats['success']} ({stats['success_rate']}%)",
                f"Flagged: {stats['flagged']} ({stats['flagged_pct']}%)",
                '-', '-', '-', '-'
            ])

            speaker_stats = [f"Characters: {len(stats['speakers'])}"]
            for speaker, counts in sorted(stats['speakers'].items(), key=lambda x: x[1]['speeches'], reverse=True):
                if counts['speeches'] > 0:
                    speaker_stats.append(f"{speaker}: {counts['speeches']} speeches")
                else:
                    speaker_stats.append(f"{speaker}: {counts['segments']} segs")
            while len(speaker_stats) < 10:
                speaker_stats.append('-')
            writer.writerow(['Character Stats'] + speaker_stats[:9])

            method_stats = [f"{m}: {c}" for m, c in sorted(stats['detection_methods'].items(), key=lambda x: x[1], reverse=True)]
            while len(method_stats) < 10:
                method_stats.append('-')
            writer.writerow(['Detection Methods'] + method_stats[:9])


def main():
    """Test colon-based detection"""

    book_path = Path("/home/hamr/Documents/PycharmProjects/ArabicTTS/tools/azure_tts/awalad-7aretna.txt")

    print("=" * 80)
    print("Colon-Based Character Detection Test")
    print("=" * 80)
    print(f"\nBook: {book_path.name}")

    # Read text
    with open(book_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"Size: {len(text):,} characters, {len(text.split())} lines")

    # Detect
    print("\nRunning colon-based detection...")
    detector = ColonBasedDetector()
    segments = detector.segment_text_by_colon(text)
    print(f"✓ Detected {len(segments)} segments")

    # Stats
    stats = detector.calculate_stats(segments)

    print(f"\n{'=' * 80}")
    print("RESULTS")
    print(f"{'=' * 80}")
    print(f"\nTotal Segments: {stats['total']}")
    print(f"  Dialogue: {stats['dialogue_count']} ({round(stats['dialogue_count']/stats['total']*100, 1)}%)")
    print(f"  Narrative: {stats['narrative_count']} ({round(stats['narrative_count']/stats['total']*100, 1)}%)")

    print(f"\nDetected Characters: {len(stats['speakers'])}")
    for speaker, counts in sorted(stats['speakers'].items(), key=lambda x: x[1]['speeches'], reverse=True):
        if counts['speeches'] > 0:
            print(f"  {speaker}: {counts['speeches']} speeches ({counts['segments']} total segments)")
        else:
            print(f"  {speaker}: {counts['segments']} segments")

    print(f"\nDetection Methods:")
    for method, count in sorted(stats['detection_methods'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {method}: {count}")

    # Export
    output_dir = Path(__file__).parent / 'outputs'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'colon_detection_{timestamp}.csv'

    detector.export_to_csv(segments, output_path)
    print(f"\n✓ Saved to: {output_path}")


if __name__ == '__main__':
    main()
