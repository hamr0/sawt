"""
POC-3: Dialogue Detection

Chapter text → segments tagged as NARRATOR or DIALOGUE.
Phase A: Binary classification (two-voice) — the goal.
Phase B: Character attribution (multi-voice) — the beast, layered on top of Phase A.

Evolves from: archive/tools/azure_tts/prototypes/06_simplified_detector.py

Input:  output/{book}/chapters/chapter_*.txt
Output: output/{book}/segments/chapter_*.csv
"""
