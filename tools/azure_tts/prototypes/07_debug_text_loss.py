#!/usr/bin/env python3
"""
Debug version of simplified detector with line-by-line tracking
to identify where the 12.6% text loss (341 words) is occurring
"""

import re
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
from collections import Counter


class DebugDetector:
    """Detector with full line-by-line debugging"""

    def __init__(self, character_names: Set[str] = None):
        self.character_names = character_names or set()

        # Stop words and speech verbs (same as simplified detector)
        self.stop_words = {
            'هو', 'هي', 'ذلك', 'هذا', 'هذه', 'وهو', 'وهي', 'فهو', 'فهي',
            'وﻫﻮ', 'وﻫﻲ', 'ﻓﻬﻮ', 'ﻓﻬﻲ', 'ﻫﻮ', 'ﻫﻲ',
            'ثم', 'من', 'إلى', 'في', 'على', 'عن', 'كان', 'كانت',
            'الذي', 'التي', 'ما', 'لا', 'نعم', 'إنه', 'إنها',
            'بغضب', 'برقة', 'بحدة', 'بصوت', 'ﺑﻐﻀﺐ', 'ﺑﺤﺪة', 'ﺑﺼﻮت',
            'باسما', 'ضاحكا', 'عاليا', 'ﺑﺎﺳﻤًﺎ', 'ﺿﺎﺣﻜًﺎ', 'ﻋﺎﻟﻴًﺎ',
        }

        self.speech_verbs = {
            'قال', 'قالت', 'رد', 'ردت', 'صاح', 'صاحت', 'نادى', 'نادت',
            'ﻗﺎل', 'ﻗﺎﻟﺖ', 'ﻓﻘﺎل', 'ﻓﻘﺎﻟﺖ', 'وﻗﺎل', 'وﻗﺎﻟﺖ',
            'وﺻﺎﺣﺖ', 'ﻓﺼﺎح', 'وﺿﺤﻚ', 'ﻓﻀﺤﻚ', 'وﻧﺎدﺗﻪ',
        }

        # Debug tracking
        self.line_tracking = []

    def extract_name_from_attribution(self, attribution: str) -> Optional[str]:
        """Extract character name from attribution text"""
        for name in self.character_names:
            if name in attribution:
                return name
        return None

    def split_narration_and_attribution(self, before_colon: str) -> Tuple[str, str]:
        """Split text before colon into narration + attribution"""
        words = before_colon.split()

        for i in range(len(words) - 1, -1, -1):
            word = words[i].strip('،,.؛؟!')

            if word in self.speech_verbs:
                narration = ' '.join(words[:i]) if i > 0 else ''
                attribution = ' '.join(words[i:])
                return narration.strip(), attribution.strip()

            for prefix in ['و', 'ف', 'ب', 'ﻓ', 'و']:
                if word.startswith(prefix) and len(word) > 1:
                    stem = word[len(prefix):]
                    if stem in self.speech_verbs:
                        narration = ' '.join(words[:i]) if i > 0 else ''
                        attribution = ' '.join(words[i:])
                        return narration.strip(), attribution.strip()

        return '', before_colon.strip()

    def segment_text(self, text: str) -> List[Dict]:
        """Segment text with full debugging"""
        lines = text.strip().split('\n')
        segments = []
        segment_id = 1

        # State tracking
        in_dialogue = False
        current_dialogue = []
        current_speaker = None
        current_dialogue_start_line = None
        pending_narration = []

        for line_num, line in enumerate(lines, 1):
            original_line = line  # Keep original for tracking
            line = line.strip()

            # Track this line
            line_info = {
                'line_num': line_num,
                'original_text': original_line,
                'word_count': len(line.split()),
                'disposition': 'UNPROCESSED',
                'target_segment': None,
                'action_taken': []
            }

            if not line:
                line_info['disposition'] = 'EMPTY_SKIPPED'
                self.line_tracking.append(line_info)
                continue

            # Check for em dash (narrator voice)
            if line.startswith('–') or line.startswith('—'):
                line_info['action_taken'].append('em_dash_detected')

                # If we were in dialogue, close it first
                if in_dialogue and current_dialogue:
                    line_info['action_taken'].append('closing_previous_dialogue')
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
                    line_info['action_taken'].append(f'flushing_pending_narration_{len(pending_narration)}_lines')
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
                    line_info['disposition'] = 'EM_DASH_NARRATOR'
                    line_info['target_segment'] = segment_id
                    line_info['action_taken'].append(f'created_narrator_segment_{segment_id}')
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
                else:
                    line_info['disposition'] = 'EM_DASH_EMPTY'
                    line_info['action_taken'].append('em_dash_but_no_text')

                self.line_tracking.append(line_info)
                continue

            # Check for colon (dialogue start)
            if ':' in line:
                line_info['action_taken'].append('colon_detected')

                # If we were in dialogue, close it first
                if in_dialogue and current_dialogue:
                    line_info['action_taken'].append('closing_previous_dialogue')
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

                line_info['action_taken'].append(f'split_at_colon_before={len(before_colon.split())}_after={len(after_colon.split())}')

                # Handle pending narration
                if pending_narration:
                    pending_word_count = sum(len(n.split()) for n in pending_narration)
                    line_info['action_taken'].append(f'pending_narration_{len(pending_narration)}_lines_{pending_word_count}_words')

                    if len(pending_narration) > 2 or pending_word_count > 200:
                        # Too much - flush most of it as narrator segment
                        narrator_text = ' '.join(pending_narration[:-1])
                        line_info['action_taken'].append(f'flushing_pending_as_segment_{segment_id}')
                        segments.append({
                            'segment_id': segment_id,
                            'line_num': line_num,
                            'type': 'narrative',
                            'text': narrator_text,
                            'speaker': 'Narrator',
                            'attribution': '-',
                            'detection_method': 'default',
                            'confidence': 'high',
                            'status': 'success',
                            'needs_review': '-'
                        })
                        segment_id += 1
                        full_before_colon = pending_narration[-1] + ' ' + before_colon
                        line_info['action_taken'].append('kept_last_pending_line_for_attribution')
                        pending_narration = []
                    else:
                        # Small amount - prepend to attribution
                        full_before_colon = ' '.join(pending_narration) + ' ' + before_colon
                        line_info['action_taken'].append('prepended_all_pending_to_attribution')
                        pending_narration = []
                else:
                    full_before_colon = before_colon

                # Split narration from attribution
                narration, attribution = self.split_narration_and_attribution(full_before_colon)
                line_info['action_taken'].append(f'split_narration_attribution_narration={len(narration.split())}_attribution={len(attribution.split())}')

                # Create narrator segment for narration (if exists)
                if narration:
                    line_info['action_taken'].append(f'created_pre_dialogue_narration_{segment_id}')
                    segments.append({
                        'segment_id': segment_id,
                        'line_num': line_num,
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

                # Extract speaker name
                speaker = self.extract_name_from_attribution(attribution)
                if not speaker and narration:
                    speaker = self.extract_name_from_attribution(narration)

                line_info['disposition'] = 'COLON_DIALOGUE_START'
                line_info['target_segment'] = segment_id
                line_info['action_taken'].append(f'starting_dialogue_speaker={speaker or "Unknown"}')

                # Start dialogue collection
                current_speaker = speaker
                current_dialogue = [after_colon] if after_colon else []
                current_dialogue_start_line = line_num
                in_dialogue = True

                self.line_tracking.append(line_info)
                continue

            # Plain line (no dash, no colon)
            if in_dialogue:
                # Check if dialogue ends on this line (closing guillemet «)
                if '«' in line:
                    line_info['action_taken'].append('closing_guillemet_detected')

                    # Dialogue ends - split at closing guillemet
                    parts = line.split('«', 1)
                    dialogue_part = parts[0] + '«'
                    after_dialogue = parts[1].strip() if len(parts) > 1 else ''

                    line_info['action_taken'].append(f'split_at_guillemet_dialogue={len(dialogue_part.split())}_after={len(after_dialogue.split())}')

                    # Add dialogue part
                    current_dialogue.append(dialogue_part)

                    # Close current dialogue
                    line_info['disposition'] = 'DIALOGUE_CONTINUATION_CLOSING'
                    line_info['target_segment'] = segment_id
                    line_info['action_taken'].append(f'closing_dialogue_segment_{segment_id}')

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
                        line_info['action_taken'].append('saved_after_dialogue_as_pending')
                else:
                    # Continuation of current dialogue
                    line_info['disposition'] = 'DIALOGUE_CONTINUATION'
                    line_info['target_segment'] = segment_id
                    line_info['action_taken'].append(f'added_to_dialogue_{segment_id}')
                    current_dialogue.append(line)
            else:
                # Not in dialogue - this is narration
                line_info['disposition'] = 'PENDING_NARRATION'
                line_info['action_taken'].append(f'added_to_pending_narration_buffer_{len(pending_narration)+1}')
                pending_narration.append(line)

            self.line_tracking.append(line_info)

        # Close any remaining dialogue
        if in_dialogue and current_dialogue:
            print(f"DEBUG: Closing remaining dialogue at end: {len(current_dialogue)} lines")
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
            print(f"DEBUG: Flushing remaining pending narration at end: {len(pending_narration)} lines")
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

    def export_debug_report(self, output_path: Path):
        """Export detailed line-by-line debug report"""
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Line_Num', 'Word_Count', 'Disposition', 'Target_Segment',
                'Actions', 'Original_Text'
            ])

            # Data rows
            for line_info in self.line_tracking:
                actions = ' | '.join(line_info['action_taken']) if line_info['action_taken'] else '-'
                writer.writerow([
                    line_info['line_num'],
                    line_info['word_count'],
                    line_info['disposition'],
                    line_info['target_segment'] or '-',
                    actions,
                    line_info['original_text'][:100] + ('...' if len(line_info['original_text']) > 100 else '')
                ])

        print(f"✓ Debug report saved to: {output_path}")


def main():
    """Run debug detector"""

    book_path = Path("/home/hamr/Documents/PycharmProjects/ArabicTTS/tools/azure_tts/awalad-7aretna.txt")

    print("=" * 80)
    print("DEBUG TEXT LOSS - Line-by-Line Tracking")
    print("=" * 80)
    print(f"\nBook: {book_path.name}")

    # Read text
    with open(book_path, 'r', encoding='utf-8') as f:
        text = f.read()

    input_word_count = len(text.split())
    input_lines = [line for line in text.strip().split('\n') if line.strip()]

    print(f"Size: {len(text):,} characters, {input_word_count} words, {len(input_lines)} non-empty lines")

    # Known character names
    known_names = {
        'أدهم', 'إدريس', 'أميمة', 'جبلاوي', 'قدري', 'همام', 'هند',
        'جبل', 'رفاعة', 'قاسم', 'عرفة', 'الداية',
        'عباس', 'رضوان', 'جليل',
        'أدﻫﻢ', 'إدرﻳﺲ', 'أﻣﻴﻤﺔ', 'اﻟﺠﺒﻼوي', 'ﻗﺪري', 'ﻫﻤﺎم', 'ﻫﻨﺪ',
        'ﺟﺒﻞ', 'رﻓﺎﻋﺔ', 'ﻗﺎﺳﻢ', 'ﻋﺮﻓﺔ', 'اﻟﺪاﻳﺔ',
        'ﻋﺒﺎس', 'رﺿﻮان', 'ﺟﻠﻴﻞ'
    }

    print(f"\nKnown character names: {len(known_names)}")

    # Detect with debugging
    print("\nRunning debug detection...")
    detector = DebugDetector(character_names=known_names)
    segments = detector.segment_text(text)
    print(f"✓ Detected {len(segments)} segments")

    # Calculate output word count
    output_word_count = sum(len(seg['text'].split()) for seg in segments)
    word_loss = input_word_count - output_word_count
    word_loss_pct = (word_loss / input_word_count * 100) if input_word_count > 0 else 0

    print(f"\n{'=' * 80}")
    print("WORD COUNT VALIDATION")
    print(f"{'=' * 80}")
    print(f"Input:  {input_word_count} words")
    print(f"Output: {output_word_count} words")
    print(f"Lost:   {word_loss} words ({word_loss_pct:.1f}%)")

    # Analyze line dispositions
    print(f"\n{'=' * 80}")
    print("LINE DISPOSITION ANALYSIS")
    print(f"{'=' * 80}")

    disposition_counts = Counter(line['disposition'] for line in detector.line_tracking)
    total_tracked_words = sum(line['word_count'] for line in detector.line_tracking)

    print(f"Total lines tracked: {len(detector.line_tracking)}")
    print(f"Total words in tracked lines: {total_tracked_words}")
    print(f"\nDisposition breakdown:")
    for disposition, count in sorted(disposition_counts.items(), key=lambda x: x[1], reverse=True):
        words_in_disposition = sum(line['word_count'] for line in detector.line_tracking if line['disposition'] == disposition)
        print(f"  {disposition:30s}: {count:3d} lines, {words_in_disposition:4d} words")

    # Find unprocessed lines
    unprocessed_lines = [line for line in detector.line_tracking if line['disposition'] == 'UNPROCESSED']
    if unprocessed_lines:
        print(f"\n⚠️  WARNING: {len(unprocessed_lines)} lines marked as UNPROCESSED!")
        print("First 5 unprocessed lines:")
        for line in unprocessed_lines[:5]:
            print(f"  Line {line['line_num']}: {line['original_text'][:80]}")

    # Export debug report
    output_dir = Path(__file__).parent / 'outputs'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    debug_report_path = output_dir / f'debug_line_tracking_{timestamp}.csv'

    detector.export_debug_report(debug_report_path)

    # Identify problematic lines (high word count but no clear disposition)
    print(f"\n{'=' * 80}")
    print("POTENTIAL PROBLEM LINES")
    print(f"{'=' * 80}")

    # Lines added to pending narration but never flushed?
    pending_lines = [line for line in detector.line_tracking if line['disposition'] == 'PENDING_NARRATION']
    if pending_lines:
        pending_words = sum(line['word_count'] for line in pending_lines)
        print(f"Lines in PENDING_NARRATION: {len(pending_lines)} lines, {pending_words} words")
        if pending_words > word_loss:
            print(f"⚠️  WARNING: More words in pending narration ({pending_words}) than total loss ({word_loss})!")
            print("This suggests pending narration is not being flushed properly")

    # Lines in dialogue continuation
    dialogue_cont = [line for line in detector.line_tracking if line['disposition'] == 'DIALOGUE_CONTINUATION']
    if dialogue_cont:
        dialogue_words = sum(line['word_count'] for line in dialogue_cont)
        print(f"\nLines in DIALOGUE_CONTINUATION: {len(dialogue_cont)} lines, {dialogue_words} words")


if __name__ == '__main__':
    main()
