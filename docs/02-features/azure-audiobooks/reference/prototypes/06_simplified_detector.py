#!/usr/bin/env python3
"""
Simplified Character Detection for Arabic Dialogue
Clean state-machine approach:
1. Em dash (–) → Narrator voice
2. No dash, no colon → Narrator narration (or dialogue continuation if in dialogue mode)
3. Has colon (:) → Extract narration, name, start dialogue collection
"""

import re
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
from collections import Counter


class SimplifiedDetector:
    """Simplified detector with clean state machine logic"""

    def __init__(self, character_names: Set[str] = None):
        """
        Initialize detector

        Args:
            character_names: Set of known character names (from Wikipedia, book reviews, etc.)
                            If None, will attempt to extract from text
        """
        self.character_names = character_names or set()

        # Stop words to filter out when extracting names
        self.stop_words = {
            # Pronouns
            'هو', 'هي', 'ذلك', 'هذا', 'هذه', 'وهو', 'وهي', 'فهو', 'فهي',
            'وﻫﻮ', 'وﻫﻲ', 'ﻓﻬﻮ', 'ﻓﻬﻲ', 'ﻫﻮ', 'ﻫﻲ',
            # Common words
            'ثم', 'من', 'إلى', 'في', 'على', 'عن', 'كان', 'كانت',
            'الذي', 'التي', 'ما', 'لا', 'نعم', 'إنه', 'إنها',
            # Adverbs/modifiers
            'بغضب', 'برقة', 'بحدة', 'بصوت', 'ﺑﻐﻀﺐ', 'ﺑﺤﺪة', 'ﺑﺼﻮت',
            'باسما', 'ضاحكا', 'عاليا', 'ﺑﺎﺳﻤًﺎ', 'ﺿﺎﺣﻜًﺎ', 'ﻋﺎﻟﻴًﺎ',
        }

        # Common speech verbs
        self.speech_verbs = {
            'قال', 'قالت', 'رد', 'ردت', 'صاح', 'صاحت', 'نادى', 'نادت',
            'ﻗﺎل', 'ﻗﺎﻟﺖ', 'ﻓﻘﺎل', 'ﻓﻘﺎﻟﺖ', 'وﻗﺎل', 'وﻗﺎﻟﺖ',
            'وﺻﺎﺣﺖ', 'ﻓﺼﺎح', 'وﺿﺤﻚ', 'ﻓﻀﺤﻚ', 'وﻧﺎدﺗﻪ',
        }

    def extract_name_from_attribution(self, attribution: str) -> Optional[str]:
        """
        Extract character name from attribution text

        Strategy:
        - Only match against provided character names
        - If no match, return None (will be marked as "Unknown")

        Note: Character names should be provided from external sources
        (Wikipedia, book reviews, etc.) rather than extracted heuristically

        Args:
            attribution: Text before colon (e.g., "وﻗﺎل أدﻫﻢ")

        Returns:
            Character name or None if not found
        """
        # Check known names only
        for name in self.character_names:
            if name in attribution:
                return name

        # No known name found - will be marked as "Unknown"
        return None

    def split_narration_and_attribution(self, before_colon: str) -> Tuple[str, str]:
        """
        Split text before colon into narration + attribution

        Example: "وﺿﺤﻚ ﺿﺤﻜﺔ ًﻛﺮﻳﻬﺔ وﻗﺎل أدﻫﻢ"
        Returns: ("وﺿﺤﻚ ﺿﺤﻜﺔ ًﻛﺮﻳﻬﺔ", "وﻗﺎل أدﻫﻢ")

        Strategy: Scan from right to left to find speech verb
        """
        words = before_colon.split()

        # Scan from end backwards to find speech verb
        for i in range(len(words) - 1, -1, -1):
            word = words[i].strip('،,.؛؟!')

            # Check if this is a speech verb
            if word in self.speech_verbs:
                # Split here
                narration = ' '.join(words[:i]) if i > 0 else ''
                attribution = ' '.join(words[i:])
                return narration.strip(), attribution.strip()

            # Check for prefixed verbs (وقال، فقالت)
            for prefix in ['و', 'ف', 'ب', 'ﻓ', 'و']:
                if word.startswith(prefix) and len(word) > 1:
                    stem = word[len(prefix):]
                    if stem in self.speech_verbs:
                        narration = ' '.join(words[:i]) if i > 0 else ''
                        attribution = ' '.join(words[i:])
                        return narration.strip(), attribution.strip()

        # No verb found - entire text is attribution
        return '', before_colon.strip()

    def segment_text(self, text: str) -> List[Dict]:
        """
        Segment text using simplified state machine

        State machine:
        - READING: Looking for next segment
        - IN_DIALOGUE: Collecting dialogue continuation lines

        Line types:
        1. Em dash → Narrator voice
        2. Contains : → Narration + Character dialogue start (enter IN_DIALOGUE)
        3. Plain → Narrator narration OR dialogue continuation (depends on state)
        """
        lines = text.strip().split('\n')
        segments = []
        segment_id = 1

        # State tracking
        in_dialogue = False
        current_dialogue = []
        current_speaker = None
        current_dialogue_start_line = None
        pending_narration = []  # Narration that appears between dialogues

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check for em dash (narrator voice)
            if line.startswith('–') or line.startswith('—'):
                # If we were in dialogue, close it first
                if in_dialogue and current_dialogue:
                    segments.append({
                        'segment_id': segment_id,
                        'line_num': current_dialogue_start_line,
                        'type': 'dialogue',
                        'text': ' '.join(current_dialogue),
                        'speaker': current_speaker or 'Unknown',
                        'attribution': '-',
                        'detection_method': 'colon_pattern',
                        'confidence': 'medium' if current_speaker else 'low',
                        'status': 'success',
                        'needs_review': '-' if current_speaker else 'no_name_found'
                    })
                    segment_id += 1
                    current_dialogue = []
                    in_dialogue = False

                # Flush any pending narration first
                if pending_narration:
                    segments.append({
                        'segment_id': segment_id,
                        'line_num': line_num,
                        'type': 'narrative',
                        'text': ' '.join(pending_narration),
                        'speaker': 'Narrator',
                        'attribution': '-',
                        'detection_method': 'default',
                        'confidence': 'high',
                        'status': 'success',
                        'needs_review': '-'
                    })
                    segment_id += 1
                    pending_narration = []

                # Create narrator voice segment (remove em dash)
                narrator_text = line[1:].strip()
                if narrator_text:
                    segments.append({
                        'segment_id': segment_id,
                        'line_num': line_num,
                        'type': 'narrative',
                        'text': narrator_text,
                        'speaker': 'Narrator',
                        'attribution': '-',
                        'detection_method': 'em_dash_narrator',
                        'confidence': 'high',
                        'status': 'success',
                        'needs_review': '-'
                    })
                    segment_id += 1
                continue

            # Check for colon (dialogue start)
            if ':' in line:
                # If we were in dialogue, close it first
                if in_dialogue and current_dialogue:
                    segments.append({
                        'segment_id': segment_id,
                        'line_num': current_dialogue_start_line,
                        'type': 'dialogue',
                        'text': ' '.join(current_dialogue),
                        'speaker': current_speaker or 'Unknown',
                        'attribution': '-',
                        'detection_method': 'colon_pattern',
                        'confidence': 'medium' if current_speaker else 'low',
                        'status': 'success',
                        'needs_review': '-' if current_speaker else 'no_name_found'
                    })
                    segment_id += 1
                    current_dialogue = []

                # Split by colon
                parts = line.split(':', 1)
                before_colon = parts[0].strip()
                after_colon = parts[1].strip() if len(parts) > 1 else ''

                # Combine pending narration with text before colon
                if pending_narration:
                    full_before_colon = ' '.join(pending_narration) + ' ' + before_colon
                    pending_narration = []
                else:
                    full_before_colon = before_colon

                # Split narration from attribution
                narration, attribution = self.split_narration_and_attribution(full_before_colon)

                # Create ONE narrator segment combining all pending + pre-dialogue narration
                if narration:
                    segments.append({
                        'segment_id': segment_id,
                        'line_num': line_num,
                        'type': 'narrative',
                        'text': narration,
                        'speaker': 'Narrator',
                        'attribution': '-',
                        'detection_method': 'default',
                        'confidence': 'high',
                        'status': 'success',
                        'needs_review': '-'
                    })
                    segment_id += 1

                # Extract speaker name from attribution
                # But also check the full narration for character names
                speaker = self.extract_name_from_attribution(attribution)
                if not speaker and narration:
                    # Try to find name in narration part too
                    speaker = self.extract_name_from_attribution(narration)

                # Create narrator segment for attribution (the "he said" part)
                # This was previously being discarded, causing 12.6% text loss
                if attribution:
                    segments.append({
                        'segment_id': segment_id,
                        'line_num': line_num,
                        'type': 'narrative',
                        'text': attribution,
                        'speaker': 'Narrator',
                        'attribution': '-',
                        'detection_method': 'dialogue_attribution',
                        'confidence': 'high',
                        'status': 'success',
                        'needs_review': '-'
                    })
                    segment_id += 1

                # Start dialogue collection
                current_speaker = speaker
                current_dialogue = [after_colon] if after_colon else []
                current_dialogue_start_line = line_num
                in_dialogue = True
                continue

            # Plain line (no dash, no colon)
            if in_dialogue:
                # Check if dialogue ends on this line (closing guillemet «)
                if '«' in line:
                    # Dialogue ends - split at closing guillemet
                    parts = line.split('«', 1)
                    dialogue_part = parts[0] + '«'  # Include closing guillemet
                    after_dialogue = parts[1].strip() if len(parts) > 1 else ''

                    # Add dialogue part
                    current_dialogue.append(dialogue_part)

                    # Close current dialogue
                    segments.append({
                        'segment_id': segment_id,
                        'line_num': current_dialogue_start_line,
                        'type': 'dialogue',
                        'text': ' '.join(current_dialogue),
                        'speaker': current_speaker or 'Unknown',
                        'attribution': '-',
                        'detection_method': 'colon_pattern',
                        'confidence': 'medium' if current_speaker else 'low',
                        'status': 'success',
                        'needs_review': '-' if current_speaker else 'no_name_found'
                    })
                    segment_id += 1
                    current_dialogue = []
                    in_dialogue = False

                    # Save text after dialogue as pending narration
                    if after_dialogue:
                        pending_narration.append(after_dialogue)
                else:
                    # Continuation of current dialogue
                    current_dialogue.append(line)
            else:
                # Not in dialogue - this is narration
                # Save as pending narration (might be pre-attribution for next colon)
                pending_narration.append(line)

        # Close any remaining dialogue
        if in_dialogue and current_dialogue:
            segments.append({
                'segment_id': segment_id,
                'line_num': current_dialogue_start_line,
                'type': 'dialogue',
                'text': ' '.join(current_dialogue),
                'speaker': current_speaker or 'Unknown',
                'attribution': '-',
                'detection_method': 'colon_pattern',
                'confidence': 'medium' if current_speaker else 'low',
                'status': 'success',
                'needs_review': '-' if current_speaker else 'no_name_found'
            })
            segment_id += 1

        # Flush any remaining pending narration
        if pending_narration:
            segments.append({
                'segment_id': segment_id,
                'line_num': len(lines),
                'type': 'narrative',
                'text': ' '.join(pending_narration),
                'speaker': 'Narrator',
                'attribution': '-',
                'detection_method': 'default',
                'confidence': 'high',
                'status': 'success',
                'needs_review': '-'
            })

        return segments

    def calculate_stats(self, segments: List[Dict]) -> Dict:
        """Calculate statistics"""
        total = len(segments)
        success = sum(1 for s in segments if s['status'] == 'success')

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
            'speakers': speakers
        }

    def export_to_csv(self, segments: List[Dict], output_path: Path):
        """Export to CSV with stats"""
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

            speaker_stats = [f"Characters: {len(stats['speakers'])}"]
            for speaker, counts in sorted(stats['speakers'].items(), key=lambda x: x[1]['speeches'], reverse=True):
                if counts['speeches'] > 0:
                    speaker_stats.append(f"{speaker}: {counts['speeches']} speeches")
            while len(speaker_stats) < 10:
                speaker_stats.append('-')
            writer.writerow(['Character Stats'] + speaker_stats[:9])


def main():
    """Test simplified detector"""

    book_path = Path("/home/hamr/Documents/PycharmProjects/ArabicTTS/tools/azure_tts/awalad-7aretna.txt")

    print("=" * 80)
    print("Simplified Character Detection Test")
    print("=" * 80)
    print(f"\nBook: {book_path.name}")

    # Read text
    with open(book_path, 'r', encoding='utf-8') as f:
        text = f.read()

    input_word_count = len(text.split())
    print(f"Size: {len(text):,} characters, {input_word_count} words")

    # Known character names (from Wikipedia/book reviews)
    # Children of Our Alley (أولاد حارتنا) main characters
    known_names = {
        # Standard Arabic forms
        'أدهم', 'إدريس', 'أميمة', 'جبلاوي', 'قدري', 'همام', 'هند',
        'جبل', 'رفاعة', 'قاسم', 'عرفة', 'الداية',
        'عباس', 'رضوان', 'جليل',
        # Presentation form variants (from actual text)
        'أدﻫﻢ', 'إدرﻳﺲ', 'أﻣﻴﻤﺔ', 'اﻟﺠﺒﻼوي', 'ﻗﺪري', 'ﻫﻤﺎم', 'ﻫﻨﺪ',
        'ﺟﺒﻞ', 'رﻓﺎﻋﺔ', 'ﻗﺎﺳﻢ', 'ﻋﺮﻓﺔ', 'اﻟﺪاﻳﺔ',
        'ﻋﺒﺎس', 'رﺿﻮان', 'ﺟﻠﻴﻞ'
    }

    print(f"\nKnown character names: {len(known_names)}")
    print(f"Names: {', '.join(sorted(known_names))}")

    # Detect
    print("\nRunning simplified detection...")
    detector = SimplifiedDetector(character_names=known_names)
    segments = detector.segment_text(text)
    print(f"✓ Detected {len(segments)} segments")

    # Stats
    stats = detector.calculate_stats(segments)

    print(f"\n{'=' * 80}")
    print("RESULTS")
    print(f"{'=' * 80}")
    print(f"\nTotal Segments: {stats['total']}")
    print(f"  Dialogue: {stats['dialogue_count']} ({stats['dialogue_pct']}%)")
    print(f"  Narrative: {stats['narrative_count']}")

    print(f"\nConfidence Distribution:")
    print(f"  High: {stats['high_conf']}")
    print(f"  Medium: {stats['medium_conf']}")
    print(f"  Low: {stats['low_conf']}")
    print(f"  Flagged for review: {stats['flagged']} ({stats['flagged_pct']}%)")

    print(f"\nDetected Characters: {len(stats['speakers'])}")
    for speaker, counts in sorted(stats['speakers'].items(), key=lambda x: x[1]['speeches'], reverse=True):
        if counts['speeches'] > 0:
            print(f"  {speaker}: {counts['speeches']} speeches")
        else:
            print(f"  {speaker}: {counts['segments']} segments (narrator)")

    # Export
    output_dir = Path(__file__).parent / 'outputs'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'simplified_detection_{timestamp}.csv'

    detector.export_to_csv(segments, output_path)
    print(f"\n✓ Saved to: {output_path}")

    # Validate word count
    output_word_count = sum(len(seg['text'].split()) for seg in segments)
    word_loss = input_word_count - output_word_count
    word_loss_pct = (word_loss / input_word_count * 100) if input_word_count > 0 else 0

    print(f"\n{'=' * 80}")
    print("WORD COUNT VALIDATION")
    print(f"{'=' * 80}")
    print(f"Input:  {input_word_count} words")
    print(f"Output: {output_word_count} words")
    print(f"Lost:   {word_loss} words ({word_loss_pct:.1f}%)")
    if word_loss > 0:
        print(f"⚠️  WARNING: Text is being lost during processing!")

    # Show first few segments for inspection
    print(f"\n{'=' * 80}")
    print("SAMPLE SEGMENTS (first 10)")
    print(f"{'=' * 80}")
    for seg in segments[:10]:
        print(f"\n[{seg['segment_id']}] Line {seg['line_num']} | {seg['type'].upper()} | Speaker: {seg['speaker']}")
        print(f"  Text: {seg['text'][:100]}{'...' if len(seg['text']) > 100 else ''}")
        print(f"  Method: {seg['detection_method']} | Confidence: {seg['confidence']}")


if __name__ == '__main__':
    main()
