#!/usr/bin/env python3
"""
Prototype 1: Character Detection Algorithm
Tests quotation parsing and speaker attribution detection

Goal: Validate >80% high confidence, <20% flagged for review
"""

import re
import csv
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


# Test sample with various quotation patterns
TEST_SAMPLE = """
كان يوما جميلا في القاهرة. المدينة مليئة بالحياة والحركة.

قال أحمد: «مرحبا يا فاطمة، كيف حالك اليوم؟»

ردت فاطمة بابتسامة: "أنا بخير والحمد لله. كيف كانت رحلتك إلى الإسكندرية؟"

«كانت رائعة جدا» أجاب أحمد. «زرت المكتبة القديمة والمتاحف».

قال محمود وهو يقترب منهما: 'سمعت أنكما تتحدثان عن الإسكندرية'.

"نعم، أحمد عاد للتو من هناك" قالت فاطمة.

تحدث أحمد عن المدينة بحماس، وقال: «يجب أن تزوروها جميعا في الصيف».

— هذا صحيح تماما، قال محمود، — المدينة جميلة في ذلك الوقت.

وهكذا استمرت المحادثة بينهم لساعات طويلة.
"""


class CharacterDetector:
    """Detect characters and their dialogue from Arabic text"""

    def __init__(self):
        # Quotation patterns (in priority order)
        self.quote_patterns = [
            {
                'name': 'guillemet',
                'pattern': r'«([^»]+)»',
                'open': '«',
                'close': '»',
                'confidence': 'high'
            },
            {
                'name': 'guillemet_reversed',
                'pattern': r'»([^«]+)«',
                'open': '»',
                'close': '«',
                'confidence': 'high'
            },
            {
                'name': 'double',
                'pattern': r'"([^"]+)"',
                'open': '"',
                'close': '"',
                'confidence': 'high'
            },
            {
                'name': 'single',
                'pattern': r"'([^']+)'",
                'open': "'",
                'close': "'",
                'confidence': 'medium'  # Less common, may be narrative
            },
            {
                'name': 'em_dash',
                'pattern': r'—\s*([^—]+?)(?=—|$)',
                'open': '—',
                'close': '—',
                'confidence': 'medium'
            }
        ]

        # Speaker attribution patterns
        self.speaker_patterns = [
            r'قال\s+(\w+)',      # قال أحمد
            r'قالت\s+(\w+)',     # قالت فاطمة
            r'رد\s+(\w+)',       # رد محمود
            r'ردت\s+(\w+)',      # ردت فاطمة
            r'أجاب\s+(\w+)',     # أجاب أحمد
            r'أجابت\s+(\w+)',    # أجابت فاطمة
            r'تحدث\s+(\w+)',     # تحدث محمود
            r'تحدثت\s+(\w+)',    # تحدثت فاطمة
        ]

    def detect_speaker(self, text: str, segment_before: str = '', segment_after: str = '') -> Tuple[str, str, str]:
        """
        Detect speaker from attribution patterns

        Returns:
            (speaker_name, detection_method, confidence)
        """
        # Check before segment (e.g., "قال أحمد: «...")
        for pattern in self.speaker_patterns:
            match = re.search(pattern, segment_before)
            if match:
                return match.group(1), 'speaker_attr_before', 'high'

        # Check after segment (e.g., "«...» قال أحمد")
        for pattern in self.speaker_patterns:
            match = re.search(pattern, segment_after)
            if match:
                return match.group(1), 'speaker_attr_after', 'high'

        return 'Unknown', 'no_attribution', 'low'

    def segment_text(self, text: str) -> List[Dict]:
        """
        Segment text into narrative and dialogue segments

        Returns:
            List of segments with metadata
        """
        segments = []
        segment_id = 1

        # Split by sentences/paragraphs
        paragraphs = [p.strip() for p in text.strip().split('\n') if p.strip()]

        for para in paragraphs:
            # Track position in paragraph
            pos = 0
            last_end = 0

            # Find all quotes in this paragraph
            quote_matches = []
            for quote_type in self.quote_patterns:
                for match in re.finditer(quote_type['pattern'], para):
                    quote_matches.append({
                        'start': match.start(),
                        'end': match.end(),
                        'text': match.group(1),
                        'full_match': match.group(0),
                        'type': quote_type['name'],
                        'pattern': quote_type['open'] + ' ' + quote_type['close'],
                        'confidence': quote_type['confidence']
                    })

            # Sort by position
            quote_matches.sort(key=lambda x: x['start'])

            # Process quotes and narrative segments
            for quote in quote_matches:
                # Narrative before quote
                if quote['start'] > last_end:
                    narrative_text = para[last_end:quote['start']].strip()
                    if narrative_text:
                        # Check for speaker attribution in narrative
                        speaker, method, conf = self.detect_speaker(
                            narrative_text,
                            segment_before=narrative_text,
                            segment_after=''
                        )

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

                # Quoted dialogue
                segment_before = para[max(0, quote['start']-100):quote['start']]
                segment_after = para[quote['end']:min(len(para), quote['end']+100)]

                speaker, attr_method, attr_conf = self.detect_speaker(
                    quote['text'],
                    segment_before,
                    segment_after
                )

                # Determine final confidence
                if attr_conf == 'high' and quote['confidence'] == 'high':
                    final_confidence = 'high'
                    status = 'success'
                    needs_review = '-'
                elif attr_conf == 'low':
                    final_confidence = 'medium'
                    status = 'warning'
                    needs_review = 'Confirm_Speaker'
                else:
                    final_confidence = 'medium'
                    status = 'success'
                    needs_review = '-'

                # Build detection method
                if attr_method != 'no_attribution':
                    detection_method = f"quote_{quote['type']}+{attr_method}"
                else:
                    detection_method = f"quote_{quote['type']}"

                segments.append({
                    'segment_id': segment_id,
                    'type': 'dialogue',
                    'text': quote['text'],
                    'speaker': speaker,
                    'detection_method': detection_method,
                    'confidence': final_confidence,
                    'quote_pattern': quote['pattern'],
                    'status': status,
                    'needs_review': needs_review
                })
                segment_id += 1

                last_end = quote['end']

            # Remaining narrative after last quote
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
        """Calculate statistics for segments"""
        total = len(segments)

        # Count by status
        success = sum(1 for s in segments if s['status'] == 'success')
        warning = sum(1 for s in segments if s['status'] == 'warning')
        error = sum(1 for s in segments if s['status'] == 'error')

        # Count by confidence
        high_conf = sum(1 for s in segments if s['confidence'] == 'high')
        medium_conf = sum(1 for s in segments if s['confidence'] == 'medium')
        low_conf = sum(1 for s in segments if s['confidence'] == 'low')

        # Count flagged for review
        flagged = sum(1 for s in segments if s['needs_review'] != '-')

        # Count by detection method
        detection_methods = {}
        for seg in segments:
            method = seg['detection_method']
            detection_methods[method] = detection_methods.get(method, 0) + 1

        # Count speakers and their speeches
        speakers = {}
        for seg in segments:
            speaker = seg['speaker']
            if speaker not in speakers:
                speakers[speaker] = {'segments': 0, 'speeches': 0}
            speakers[speaker]['segments'] += 1
            if seg['type'] == 'dialogue':
                speakers[speaker]['speeches'] += 1

        # Count review flags
        review_flags = {}
        for seg in segments:
            if seg['needs_review'] != '-':
                flag = seg['needs_review']
                review_flags[flag] = review_flags.get(flag, 0) + 1

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
            'detection_methods': detection_methods,
            'speakers': speakers,
            'review_flags': review_flags
        }

    def export_to_csv(self, segments: List[Dict], output_path: Path):
        """Export segments and stats to CSV matching learned pattern"""

        stats = self.calculate_stats(segments)

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            # Header row
            writer.writerow([
                'Type', 'Segment_ID', 'Chapter', 'Text', 'Speaker',
                'Detection_Method', 'Confidence', 'Quote_Pattern',
                'Speech_Count', 'Prosody_Rate', 'Prosody_Pitch',
                'Prosody_Volume', 'Status', 'Needs_Review'
            ])

            # Data rows
            for seg in segments:
                writer.writerow([
                    'SEGMENT',
                    seg['segment_id'],
                    1,  # Chapter (hardcoded for prototype)
                    seg['text'],
                    seg['speaker'],
                    seg['detection_method'],
                    seg['confidence'],
                    seg['quote_pattern'],
                    '-',  # Speech count (calculated later)
                    '1.0',  # Default prosody
                    '0%',
                    '0%',
                    seg['status'],
                    seg['needs_review']
                ])

            # Processing Stats row
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

            # Character Stats row
            speaker_stats = [
                f"Detected Characters: {len(stats['speakers'])}"
            ]
            for speaker, counts in sorted(stats['speakers'].items()):
                if counts['speeches'] > 0:
                    speaker_stats.append(
                        f"{speaker}: {counts['segments']} segs ({counts['speeches']} speeches)"
                    )
                else:
                    speaker_stats.append(
                        f"{speaker}: {counts['segments']} segs"
                    )

            # Pad to 14 columns
            while len(speaker_stats) < 14:
                speaker_stats.append('-')

            writer.writerow(['Character Stats'] + speaker_stats[:13])

            # Detection Methods row
            method_stats = [f"{method}: {count}" for method, count in sorted(stats['detection_methods'].items())]
            while len(method_stats) < 13:
                method_stats.append('-')
            writer.writerow(['Detection Methods'] + method_stats)

            # Confidence Breakdown row
            writer.writerow([
                'Confidence Breakdown',
                f"High: {stats['high_conf']} ({round(stats['high_conf']/stats['total']*100, 1)}%)",
                f"Medium: {stats['medium_conf']} ({round(stats['medium_conf']/stats['total']*100, 1)}%)",
                f"Low: {stats['low_conf']} ({round(stats['low_conf']/stats['total']*100, 1)}%)",
                '-', '-', '-', '-', '-', '-', '-', '-', '-'
            ])

            # Review Flags row
            flag_stats = [f"{flag}: {count}" for flag, count in sorted(stats['review_flags'].items())]
            while len(flag_stats) < 13:
                flag_stats.append('-')
            writer.writerow(['Review Flags'] + flag_stats)

            # Notes row
            writer.writerow([
                'Notes',
                'Detection Method Codes:',
                'quote_guillemet=« »',
                'quote_double=" "',
                "quote_single=' '",
                'quote_em_dash=— —',
                'speaker_attr_before=قال patterns before',
                'speaker_attr_after=قال patterns after',
                'default=No quotes',
                '-', '-', '-', '-'
            ])


def main():
    """Run character detection prototype"""

    print("=" * 80)
    print("Prototype 1: Character Detection Algorithm")
    print("=" * 80)

    # Initialize detector
    detector = CharacterDetector()

    # Run detection
    print("\n1. Segmenting test sample text...")
    segments = detector.segment_text(TEST_SAMPLE)
    print(f"   ✓ Detected {len(segments)} segments")

    # Calculate stats
    print("\n2. Calculating statistics...")
    stats = detector.calculate_stats(segments)

    print(f"   Total Segments: {stats['total']}")
    print(f"   Success: {stats['success']} ({stats['success_rate']}%)")
    print(f"   Warning: {stats['warning']}")
    print(f"   Error: {stats['error']}")
    print(f"   Flagged for Review: {stats['flagged']} ({stats['flagged_pct']}%)")

    print(f"\n   Confidence Breakdown:")
    print(f"   - High: {stats['high_conf']} ({round(stats['high_conf']/stats['total']*100, 1)}%)")
    print(f"   - Medium: {stats['medium_conf']} ({round(stats['medium_conf']/stats['total']*100, 1)}%)")
    print(f"   - Low: {stats['low_conf']} ({round(stats['low_conf']/stats['total']*100, 1)}%)")

    print(f"\n   Detected Characters: {len(stats['speakers'])}")
    for speaker, counts in sorted(stats['speakers'].items()):
        if counts['speeches'] > 0:
            print(f"   - {speaker}: {counts['segments']} segments ({counts['speeches']} speeches)")
        else:
            print(f"   - {speaker}: {counts['segments']} segments")

    print(f"\n   Detection Methods:")
    for method, count in sorted(stats['detection_methods'].items()):
        print(f"   - {method}: {count}")

    # Export to CSV
    output_dir = Path(__file__).parent / 'outputs'
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'character_detection_{timestamp}.csv'

    print(f"\n3. Exporting to CSV...")
    detector.export_to_csv(segments, output_path)
    print(f"   ✓ Saved to: {output_path}")

    # Validation
    print("\n" + "=" * 80)
    print("Validation Results")
    print("=" * 80)

    high_conf_pct = round(stats['high_conf'] / stats['total'] * 100, 1)
    flagged_pct = stats['flagged_pct']

    print(f"\nTarget: >80% high confidence")
    print(f"Actual: {high_conf_pct}%")
    print(f"Status: {'✓ PASS' if high_conf_pct >= 80 else '✗ FAIL'}")

    print(f"\nTarget: <20% flagged for review")
    print(f"Actual: {flagged_pct}%")
    print(f"Status: {'✓ PASS' if flagged_pct < 20 else '✗ FAIL'}")

    if high_conf_pct >= 80 and flagged_pct < 20:
        print("\n✓ Prototype 1 SUCCESS - Algorithm meets targets!")
    else:
        print("\n⚠ Prototype 1 PARTIAL - Algorithm needs tuning")

    print("\n" + "=" * 80)
    print(f"Next Steps:")
    print(f"1. Review CSV: {output_path}")
    print(f"2. Check flagged segments for accuracy")
    print(f"3. Tune detection patterns if needed")
    print("=" * 80)


if __name__ == '__main__':
    main()
