"""
SSML generation from verified segments.

Single voice:  all segments → one voice tag
Two voice:     narrator/dialogue → two voice tags
Multi voice:   per-character → unique voice tags

Input:  output/{book}/segments/chapter_*.csv
Output: output/{book}/ssml/chapter_*.ssml
"""
