"""
SSML generation from verified segments.

Single voice:  all segments → one voice tag
Two voice:     narrator/dialogue → two voice tags
Multi voice:   per-character → unique voice tags

Input:  output/{book}/03_segments/ssml/chapter_*.csv
Output: output/{book}/04_ssml/chapter_*.ssml
"""
