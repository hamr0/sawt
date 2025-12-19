#!/usr/bin/env python3
"""
Enhanced Character Detection with Name Extraction
Two-pass approach:
1. Extract character names from the entire text
2. Use names to identify speakers in dialogue
"""

import re
import csv
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set
from collections import Counter


class NameAwareDetector:
    """Detect characters using extracted names from text"""

    def __init__(self):
        # Known character names from Children of Gebelawi
        self.known_names = {
            'أدهم', 'إدريس', 'أميمة', 'جبلاوي', 'قدري', 'همام', 'هند',
            'جبل', 'رفاعة', 'قاسم', 'عرفة'
        }

        # Quotation patterns
        self.quote_patterns = [
            {'name': 'guillemet', 'pattern': r'«([^»]+)»', 'open': '«', 'close': '»'},
            {'name': 'guillemet_reversed', 'pattern': r'»([^«]+)«', 'open': '»', 'close': '«'},
            {'name': 'double', 'pattern': r'"([^"]+)"', 'open': '"', 'close': '"'},
            {'name': 'single', 'pattern': r"'([^']+)'", 'open': "'", 'close': "'"},
            {'name': 'em_dash', 'pattern': r'—\s*([^—]+?)(?=—|$)', 'open': '—', 'close': '—'}
        ]

        # Expanded speaker attribution patterns
        self.speaker_verbs = [
            'قال', 'قالت', 'رد', 'ردت', 'أجاب', 'أجابت',
            'تحدث', 'تحدثت', 'صاح', 'صاحت', 'نادى', 'نادت',
            'هتف', 'هتفت', 'سأل', 'سألت', 'تساءل', 'تساءلت',
            'ضحك', 'ضحكت', 'بكى', 'بكت', 'صرخ', 'صرخت',
            'همس', 'همست', 'غنى', 'غنت', 'يترنم', 'تترنم',
            'يقول', 'تقول', 'يرد', 'ترد', 'يصيح', 'تصيح',
            'ينادي', 'تنادي', 'يهتف', 'تهتف', 'يسأل', 'تسأل'
        ]

        # Special patterns for "voice of X" and similar
        self.special_patterns = [
            r'صوت\s+(\w+)',  # صوت أميمة = voice of Amima
            r'(\w+)\s+يترنم',  # X يترنم = X is singing
            r'(\w+)\s+يغني',  # X يغني = X is singing
        ]

    @staticmethod
    def normalize_arabic_text(text: str) -> str:
        """Normalize Arabic Presentation Forms to standard letters"""
        # Use NFD then NFC to normalize combining marks
        text = unicodedata.normalize('NFD', text)
        text = unicodedata.normalize('NFC', text)
        return text

    def extract_character_names(self, text: str) -> Set[str]:
        """
        Extract potential character names from text

        Strategy:
        1. Look for proper nouns (capitalized Arabic words)
        2. Find names in attribution patterns (قال X, ردت Y)
        3. Find names in special patterns (صوت X)
        4. Combine with known character names
        """
        extracted_names = set()

        # Extract from speaker attribution patterns
        for verb in self.speaker_verbs:
            # Pattern: verb + name (e.g., "قال أحمد")
            pattern = f'{verb}\\s+(\\w+)'
            matches = re.findall(pattern, text)
            extracted_names.update(matches)

        # Extract from special patterns
        for pattern in self.special_patterns:
            matches = re.findall(pattern, text)
            extracted_names.update(matches)

        # Add known names
        extracted_names.update(self.known_names)

        # Filter out common words (pronouns, articles, etc.)
        stop_words = {'هو', 'هي', 'ذلك', 'هذا', 'هذه', 'كان', 'كانت', 'إلى', 'من', 'في',
                      'وهو', 'وهي', 'الذي', 'التي', 'امرأته', 'رجل'}
        extracted_names = {name for name in extracted_names if name not in stop_words}

        return extracted_names

    def find_speaker_in_context(self, context_before: str, context_after: str,
                                character_names: Set[str]) -> Tuple[str, str, str]:
        """
        Find speaker name in surrounding context

        Returns:
            (speaker_name, detection_method, confidence)
        """
        # Try special patterns first (صوت X, X يترنم)
        for pattern in self.special_patterns:
            match = re.search(pattern, context_before)
            if match:
                potential_speaker = match.group(1)
                if potential_speaker in character_names:
                    return potential_speaker, f'special_pattern_before', 'high'

        # Try attribution patterns with known verbs
        for verb in self.speaker_verbs:
            # Pattern: verb + name (before quote)
            pattern_before = f'{verb}\\s+(\\w+).*$'
            match = re.search(pattern_before, context_before)
            if match:
                potential_speaker = match.group(1)
                if potential_speaker in character_names:
                    return potential_speaker, f'attr_{verb}_before', 'high'

            # Pattern: name + verb (after quote)
            pattern_after = f'^.*?(\\w+)\\s+{verb}'
            match = re.search(pattern_after, context_after)
            if match:
                potential_speaker = match.group(1)
                if potential_speaker in character_names:
                    return potential_speaker, f'attr_{verb}_after', 'high'

        # Fallback: Look for any character name in context
        for name in character_names:
            if name in context_before[-100:]:  # Check last 100 chars before
                return name, 'name_in_context_before', 'medium'
            if name in context_after[:100]:  # Check first 100 chars after
                return name, 'name_in_context_after', 'medium'

        return 'Unknown', 'no_attribution', 'low'

    def segment_text(self, text: str) -> List[Dict]:
        """
        Segment text with name-aware character detection
        """
        # Normalize Arabic text (handles presentation forms)
        text = self.normalize_arabic_text(text)
        print(f"   Text normalized ({len(text)} characters)")

        # First pass: Extract all character names
        character_names = self.extract_character_names(text)
        print(f"   Extracted character names: {', '.join(sorted(character_names))}")

        segments = []
        segment_id = 1

        # Split by paragraphs
        paragraphs = [p.strip() for p in text.strip().split('\n') if p.strip()]

        for para in paragraphs:
            pos = 0
            last_end = 0

            # Find all quotes
            quote_matches = []
            for quote_type in self.quote_patterns:
                for match in re.finditer(quote_type['pattern'], para):
                    quote_matches.append({
                        'start': match.start(),
                        'end': match.end(),
                        'text': match.group(1),
                        'full_match': match.group(0),
                        'type': quote_type['name'],
                        'pattern': quote_type['open'] + ' ' + quote_type['close']
                    })

            # Sort by position
            quote_matches.sort(key=lambda x: x['start'])

            # Process quotes and narrative
            for quote in quote_matches:
                # Narrative before quote
                if quote['start'] > last_end:
                    narrative_text = para[last_end:quote['start']].strip()
                    if narrative_text:
                        segments.append({
                            'segment_id': segment_id,
                            'type': 'narrative',
                            'text': narrative_text,
                            'speaker': 'Narrator',
                            'detection_method': 'default',
                            'confidence': 'high',
                            'quote_pattern': '-',
                            'status': 'success',
                            'needs_review': '-'
                        })
                        segment_id += 1

                # Quoted dialogue with name-aware detection
                context_before = para[max(0, quote['start']-150):quote['start']]
                context_after = para[quote['end']:min(len(para), quote['end']+150)]

                speaker, method, conf = self.find_speaker_in_context(
                    context_before, context_after, character_names
                )

                # Determine status
                if conf == 'low':
                    status = 'warning'
                    needs_review = 'Confirm_Speaker'
                else:
                    status = 'success'
                    needs_review = '-'

                segments.append({
                    'segment_id': segment_id,
                    'type': 'dialogue',
                    'text': quote['text'],
                    'speaker': speaker,
                    'detection_method': f"quote_{quote['type']}+{method}",
                    'confidence': conf,
                    'quote_pattern': quote['pattern'],
                    'status': status,
                    'needs_review': needs_review
                })
                segment_id += 1
                last_end = quote['end']

            # Remaining narrative
            if last_end < len(para):
                narrative_text = para[last_end:].strip()
                if narrative_text:
                    segments.append({
                        'segment_id': segment_id,
                        'type': 'narrative',
                        'text': narrative_text,
                        'speaker': 'Narrator',
                        'detection_method': 'default',
                        'confidence': 'high',
                        'quote_pattern': '-',
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

        high_conf = sum(1 for s in segments if s['confidence'] == 'high')
        medium_conf = sum(1 for s in segments if s['confidence'] == 'medium')
        low_conf = sum(1 for s in segments if s['confidence'] == 'low')

        flagged = sum(1 for s in segments if s['needs_review'] != '-')

        detection_methods = Counter(s['detection_method'] for s in segments)
        review_flags = Counter(s['needs_review'] for s in segments if s['needs_review'] != '-')

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
            'high_conf': high_conf,
            'medium_conf': medium_conf,
            'low_conf': low_conf,
            'flagged': flagged,
            'flagged_pct': round(flagged / total * 100, 1) if total > 0 else 0,
            'detection_methods': dict(detection_methods),
            'speakers': speakers,
            'review_flags': dict(review_flags)
        }

    def export_to_csv(self, segments: List[Dict], output_path: Path):
        """Export to CSV with stats rows"""
        stats = self.calculate_stats(segments)

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Type', 'Segment_ID', 'Chapter', 'Text', 'Speaker',
                'Detection_Method', 'Confidence', 'Quote_Pattern',
                'Speech_Count', 'Prosody_Rate', 'Prosody_Pitch',
                'Prosody_Volume', 'Status', 'Needs_Review'
            ])

            # Data rows
            for seg in segments:
                writer.writerow([
                    'SEGMENT', seg['segment_id'], 1, seg['text'], seg['speaker'],
                    seg['detection_method'], seg['confidence'], seg['quote_pattern'],
                    '-', '1.0', '0%', '0%', seg['status'], seg['needs_review']
                ])

            # Stats rows
            writer.writerow([
                'Processing Stats',
                f"Total Segments: {stats['total']}",
                f"Success: {stats['success']}",
                f"Warning: {stats['warning']}",
                f"Error: {stats['error']}",
                f"Success Rate: {stats['success_rate']}%",
                f"Flagged for Review: {stats['flagged']} ({stats['flagged_pct']}%)",
                '-', '-', '-', '-', '-', '-'
            ])

            speaker_stats = [f"Detected Characters: {len(stats['speakers'])}"]
            for speaker, counts in sorted(stats['speakers'].items(), key=lambda x: x[1]['segments'], reverse=True):
                if counts['speeches'] > 0:
                    speaker_stats.append(f"{speaker}: {counts['segments']} segs ({counts['speeches']} speeches)")
                else:
                    speaker_stats.append(f"{speaker}: {counts['segments']} segs")
            while len(speaker_stats) < 14:
                speaker_stats.append('-')
            writer.writerow(['Character Stats'] + speaker_stats[:13])

            method_stats = [f"{method}: {count}" for method, count in
                           sorted(stats['detection_methods'].items(), key=lambda x: x[1], reverse=True)]
            while len(method_stats) < 13:
                method_stats.append('-')
            writer.writerow(['Detection Methods'] + method_stats[:13])

            conf_stats = [
                f"High: {stats['high_conf']} ({round(stats['high_conf']/stats['total']*100, 1)}%)",
                f"Medium: {stats['medium_conf']} ({round(stats['medium_conf']/stats['total']*100, 1)}%)",
                f"Low: {stats['low_conf']} ({round(stats['low_conf']/stats['total']*100, 1)}%)"
            ]
            while len(conf_stats) < 13:
                conf_stats.append('-')
            writer.writerow(['Confidence Breakdown'] + conf_stats)

            if stats['review_flags']:
                flag_stats = [f"{flag}: {count}" for flag, count in sorted(stats['review_flags'].items())]
                while len(flag_stats) < 13:
                    flag_stats.append('-')
                writer.writerow(['Review Flags'] + flag_stats)


def main():
    """Test name-aware detection on real book"""

    book_path = Path("/home/hamr/Documents/PycharmProjects/ArabicTTS/tools/azure_tts/awalad-7aretna.txt")

    print("=" * 80)
    print("Name-Aware Character Detection Test")
    print("=" * 80)
    print(f"\nBook: {book_path.name}")

    # Read text
    with open(book_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"Size: {len(text):,} characters")

    # Detect with name awareness
    print("\nRunning name-aware detection...")
    detector = NameAwareDetector()
    segments = detector.segment_text(text)
    print(f"✓ Detected {len(segments)} segments")

    # Stats
    stats = detector.calculate_stats(segments)

    print(f"\n{'=' * 80}")
    print("RESULTS")
    print(f"{'=' * 80}")
    print(f"\nTotal Segments: {stats['total']}")
    print(f"Success: {stats['success']} ({stats['success_rate']}%)")
    print(f"Flagged: {stats['flagged']} ({stats['flagged_pct']}%)")

    print(f"\nDetected Characters: {len(stats['speakers'])}")
    for speaker, counts in sorted(stats['speakers'].items(), key=lambda x: x[1]['speeches'], reverse=True):
        if counts['speeches'] > 0:
            print(f"  {speaker}: {counts['speeches']} speeches, {counts['segments']} total segments")
        else:
            print(f"  {speaker}: {counts['segments']} segments")

    # Export
    output_dir = Path(__file__).parent / 'outputs'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'name_aware_detection_{timestamp}.csv'

    detector.export_to_csv(segments, output_path)
    print(f"\n✓ Saved to: {output_path}")


if __name__ == '__main__':
    main()
