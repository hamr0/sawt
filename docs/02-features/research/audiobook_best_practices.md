# Audiobook Production Best Practices

Research compiled from professional narrators, ACX/Audible standards, Storytel/Kitab Sawti, and TTS-specific sources.

## 1. Pauses and Silence

### Industry Standard Durations

| Context | Duration |
|---------|----------|
| Voice switch (narrator ↔ dialogue) | 300-700ms |
| Dialogue exchanges (back-and-forth) | 200-500ms (VARY, avoid uniform) |
| Paragraph breaks within narration | 1000-1500ms |
| Section breaks (marked by *** or ---) | 2000-3500ms |
| Chapter breaks | 2500ms+ |
| Start of file (room tone) | 500ms |
| End of file | 3500ms |

**Critical insight:** Uniform pauses are the #1 way to sound robotic. Vary break durations between segments. "The same gaps between speeches becomes very dull."

### Sources
- [Standards for Silence - Narrators Roadmap](https://www.narratorsroadmap.com/standards-for-silence-in-the-book/)
- [Let's Talk About Secs - Ladbroke Audio](https://ladbrokeaudio.com/lets-talk-about-secs/)
- [The Art of Pausing - Audiobookfest](https://audiobookfest.com/the-art-of-pausing-how-silence-shapes-an-audiobook-experience/)

## 2. Two-Voice / Multi-Voice Production

- **Said tags stay with narrator voice.** "He said" / "she said" and all attribution text must be rendered by the narrator voice. Only actual quoted speech goes to the dialogue voice.
- Voice switching needs a brief pause so listeners register the change.
- Understated transitions are better than dramatic ones.
- Consistent assignment: same voice always does the same role.
- Voices should differ enough to tell apart, but not so much it feels like two different audiobooks spliced together.
- Same-gender pairings (M/M, F/F) produce smoother transitions than mixed-gender.
- Female narrator over male dialogue works better than the reverse.

### Sources
- [Duet vs Dual Narration - Indie Audiobook Productions](https://www.indieaudiobookproductions.co.uk/post/duet-vs-dual-narration-in-audiobooks)
- [Dual & Duet Narrations - ACX Blog](https://www.acx.com/mp/blog/it-takes-two-dual-and-duet-narrations-are-spicing-up-romance)

## 3. Dialogue vs Narration Tone

- Narrator voice: warm, steady, authoritative — the "home base" voice.
- Dialogue voice: slightly more energy, slight pitch difference, more intimacy (speaking directly to someone rather than reading aloud).
- No "spillover" — narrator reads attribution in narrator voice, never bleeding into character voice.
- Subtle modifications work better than extreme ones: pitch adjustments, speed variations, tone shifts.
- "Embrace imperfection" — some breath noise and natural variation is better than hyper-clean synthesis.

### Sources
- [Jay Myers: Tips for Audiobook Narration](https://www.jaymyersvoiceover.com/blog-ideas/5-more-tips-for-better-audiobook-narration)
- [Academy Voices: Audiobook Narration Tips](https://www.academyvoices.com/audiobook-narration-tips-and-tricks)

## 4. Arabic Audiobook Specifics

### Market
- Storytel acquired Kitab Sawti → 5,000+ Arabic titles, largest Arabic library globally.
- Market is young (started ~2017), still growing. Piracy prevalent.
- Kitab Sawti operates 100+ narrators across Egypt, Levant, Gulf.

### Dialect Matching (Industry Standard)
- **Egyptian narrators for Egyptian authors, even when text is in MSA.** Accent/dialect match to author's origin matters.
- Three regional voice families: Egypt, Levant (Syria/Lebanon), Gulf (Saudi).
- Cross-regional appeal exists: Saudi listeners enjoy Egyptian books by Egyptian speakers.
- Modern Egyptian fiction uses MSA narration + dialect dialogue — matches Sawt's two-voice model.

### Arabic TTS Challenges
- Arabic script omits diacritics → TTS must predict vowels from context.
- Azure improved diacritic prediction by 78% word-level error reduction.
- Proper noun pronunciation is the #1 Arabic TTS failure point.
- The root system makes pronunciation context-dependent.

### Sources
- [Storytel's Yasmina Jraissati - Publishing Perspectives](https://publishingperspectives.com/2022/06/storytels-yasmina-jraissati-on-audiobooks-in-the-arab-world/)
- [Azure AI Arabic Pronunciation - Microsoft](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-voices-in-arabic-improved-pronunciation/4360306)

## 5. Top TTS Complaints from Listeners

1. **Monotonous prosody** — same rhythm repeating = auditory fatigue (#1 complaint)
2. **Pronunciation errors on names** — same name said 3 different ways
3. **Wrong emotional tone** — cheerful reading tragedy
4. **Uniform pauses** — metronome effect
5. **Uncanny valley compounds over time** — test with 10+ min, not spot checks

### Sources
- [AI Audiobook Narration Quality - Lovely Audiobooks](https://lovelyaudiobooks.info/ai-audiobook-narration-quality/)
- [How to Make TTS Sound Less Robotic - ElevenLabs](https://elevenlabs.io/blog/how-to-make-text-to-speech-sound-less-robotic)

## 6. Voice-Genre Matching

- Fiction: expressiveness and warmth
- Non-fiction: single voice, clarity and authority
- Romance: slower, more intimate
- Thriller: faster, more tension
- Arabic fiction: dialect-matched to author's region
- Arabic educational/formal: MSA

## 7. Actionable for Sawt

1. **Pause variation** — vary break durations, avoid uniform gaps
2. **Said tags with narrator** — attribution text stays with narrator voice
3. **Dialect matching** — validated by Storytel/Kitab Sawti practice
4. **Proper noun dictionary** — future pipeline stage for character names
5. **Long-form testing** — listen to 10+ minutes, not spot checks
6. **Prosody variation** — future SSML `<prosody>` rate/pitch adjustments
