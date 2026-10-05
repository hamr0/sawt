# Email to Rasha — Voice Selection + Outreach

**Subject:** Sawt — need your ears + outreach help

---

Hey Rasha,

I'm at the point where the tech side is working and I need help with two things: **picking the right voices** and **outreach to publishers/platforms**. Let me catch you up on where things stand.

**What the pipeline does (the simple version):**

We take a digital book (EPUB or Word file) and run it through a series of steps:

1. **Extract the text** — pull clean text out of the book file
2. **Split into chapters** — detect where chapters start and end naturally
3. **Detect dialogue** — figure out which parts are narration and which parts are characters speaking
4. **Generate audio** — send the text to an AI voice service with two different voices: one for the narrator, one for dialogue

All the text processing (steps 1-3) is done and tested on 12 books. It works well — about 95% accuracy on telling narration from dialogue. The part I need help with now is step 4: choosing the right voices.

**Two voice providers to choose from:**

- **Google Chirp3-HD** — Good, consistent, natural. More even and steady, like a reliable narrator. 30 Arabic voices. ~$4/book.
- **ElevenLabs** — Best available quality, warmer, more expressive and human. 53 Arabic community voices (Egyptian, MSA, Levantine, Gulf, etc.). ~$12/book — 3x more expensive.

We might end up using one for some books and the other for others, or we might find that Google is good enough across the board.

**What I found so far from my initial listening:**

I did a first pass through about 40 voices across both providers. Here's what I noticed about what sounds good for audiobooks:

- **Warm and soft wins** — voices that sound like someone telling you a bedtime story, not reading the news or giving a speech
- **Egyptian + MSA accents** work best for our books — Levantine is OK too, but no Gulf
- **Female voices stood out more** — 7 out of my 10 favorites from ElevenLabs were female
- **Two distinct styles needed** — a more "formal/narrative" voice for the narrator parts, and a "soft/warm" voice for when characters are speaking. The contrast between the two is what makes it feel alive.

From ElevenLabs, my top pick so far is **Sara** (MSA, female) — soft, expressive, warm. For narrator I liked **Razan** (MSA, formal, academic tone). Together they give you a clear contrast: Razan narrates the scene, Sara brings the characters to life.

**Pairings I think could work (ElevenLabs):**

| Combo | Narrator | Dialogue | Why |
|-------|----------|----------|-----|
| F/F #1 | Razan (MSA, formal) | Sara (MSA, soft) | Formal narrator vs warm dialogue — my top pick |
| F/F #2 | Ghizlane (MSA, calm) | Alice (Egyptian, charming) | Steady narrative vs Egyptian warmth |
| F/F #3 | Mona (MSA, expressive) | Salma (Levantine, friendly) | Formal vs intimate |
| M/F | Hanafi (Egyptian) | Sara (MSA, soft) | Classic male narrator / female dialogue |

For Google, I haven't paired them yet — I liked 5 voices but they need more listening to figure out which pair well together.

**But I want your fresh ears on all of this.** I'll send you the samples and you tell me what you think — you might hear something completely different. The full voice catalog for both providers is below with all samples generated. I also attached a CSV (voice_selection_tables.csv) with a "Rasha Verdict" column for you to fill in.

**What I need from you:**

**1. Voice selection**

I'll send you all the audio samples (83 total). For each provider:
- Listen to everything
- Pick your 2-6 favorites
- Then we pair them and test on full chapters until we get winning combos

We need solid pairs for the first two books.

**2. Outreach**

I'm attaching a document (AUDIOBOOK_DISTRIBUTION.md) that has the full market picture — copyright status, platform policies, business paths, numbers. The short version: there's a massive gap (70,000 Arabic books/year vs 5,000 audiobooks total), we can produce at $4-12/book vs $1,000+ for human narration, and the best paths are partnering with Storytel MENA, Arabookverse, or publishers like Hindawi directly. The doc has the details on who to approach and why.

Let me know when you're ready for the voice samples!

---

## Google Chirp3-HD — 30 voices (all sampled)

All voices use one Arabic model (ar-XA). No accent/dialect distinction — Google uses the same pronunciation model, different speaker characteristics. Files in `google/` folder.

| # | File | Voice | Gender | Amr Verdict |
|---|------|-------|--------|------------|
| 1 | Chirp3-HD-Achernar.mp3 | Achernar | F | Liked |
| 2 | Chirp3-HD-Aoede.mp3 | Aoede | F | Not selected |
| 3 | Chirp3-HD-Autonoe.mp3 | Autonoe | F | New |
| 4 | Chirp3-HD-Callirrhoe.mp3 | Callirrhoe | F | New |
| 5 | Chirp3-HD-Despina.mp3 | Despina | F | New |
| 6 | Chirp3-HD-Erinome.mp3 | Erinome | F | New |
| 7 | Chirp3-HD-Gacrux.mp3 | Gacrux | F | New |
| 8 | Chirp3-HD-Kore.mp3 | Kore | F | Not selected |
| 9 | Chirp3-HD-Laomedeia.mp3 | Laomedeia | F | Liked |
| 10 | Chirp3-HD-Leda.mp3 | Leda | F | New |
| 11 | Chirp3-HD-Pulcherrima.mp3 | Pulcherrima | F | New |
| 12 | Chirp3-HD-Sulafat.mp3 | Sulafat | F | New |
| 13 | Chirp3-HD-Vindemiatrix.mp3 | Vindemiatrix | F | New |
| 14 | Chirp3-HD-Zephyr.mp3 | Zephyr | F | Not selected |
| 15 | Chirp3-HD-Achird.mp3 | Achird | M | Not selected |
| 16 | Chirp3-HD-Algenib.mp3 | Algenib | M | New |
| 17 | Chirp3-HD-Algieba.mp3 | Algieba | M | New |
| 18 | Chirp3-HD-Alnilam.mp3 | Alnilam | M | New |
| 19 | Chirp3-HD-Charon.mp3 | Charon | M | Not selected |
| 20 | Chirp3-HD-Enceladus.mp3 | Enceladus | M | New |
| 21 | Chirp3-HD-Fenrir.mp3 | Fenrir | M | Liked |
| 22 | Chirp3-HD-Iapetus.mp3 | Iapetus | M | New |
| 23 | Chirp3-HD-Orus.mp3 | Orus | M | New |
| 24 | Chirp3-HD-Puck.mp3 | Puck | M | Liked |
| 25 | Chirp3-HD-Rasalgethi.mp3 | Rasalgethi | M | New |
| 26 | Chirp3-HD-Sadachbia.mp3 | Sadachbia | M | Liked |
| 27 | Chirp3-HD-Sadaltager.mp3 | Sadaltager | M | New |
| 28 | Chirp3-HD-Schedar.mp3 | Schedar | M | New |
| 29 | Chirp3-HD-Umbriel.mp3 | Umbriel | M | New |
| 30 | Chirp3-HD-Zubenelgenubi.mp3 | Zubenelgenubi | M | New |

---

## ElevenLabs — 53 voices (all sampled)

Community-contributed Arabic voices. Each has a different accent, tone, and personality. Files in `elevenlabs/` folder, named `{Voice}_{Accent}_{Gender}.mp3`.

### Female voices (22)

| # | File | Voice | Accent | Use Case | Amr Verdict | Notes |
|---|------|-------|--------|----------|------------|-------|
| 1 | Sara_MSA_F.mp3 | Sara | MSA | Narrative | **Top pick** | Soft, expressive, warm |
| 2 | Alice_Egyptian_F.mp3 | Alice | Egyptian | Narrative | Liked | Smooth, charming — only Egyptian female |
| 3 | Razan_MSA_F.mp3 | Razan | MSA | Educational | Liked | Academic, formal — great narrator |
| 4 | Mona_MSA_F.mp3 | Mona | MSA | Narrative | Liked | Attractive, expressive, formal |
| 5 | Ghizlane_MSA_F.mp3 | Ghizlane | MSA | Narrative | Liked | Smooth, distinctive, calm |
| 6 | Salma_Levantine_F.mp3 | Salma | Levantine | Conversational | Liked | Friendly, clear — good for dialogue |
| 7 | Suhair_MSA_F.mp3 | Suhair | MSA | Conversational | Liked | Warm, honest, clear |
| 8 | Abrar_Sabbah_MSA_F.mp3 | Abrar Sabbah | MSA | Narrative | Not selected | |
| 9 | Asmaa_MSA_F.mp3 | Asmaa | MSA | Educational | Not selected | |
| 10 | Habibah_MSA_F.mp3 | Habibah | MSA | Educational | Not selected | |
| 11 | Hoda_Egyptian_F.mp3 | Hoda | Egyptian | Conversational | Not selected | |
| 12 | Sana_MSA_F.mp3 | Sana | MSA | Narrative | Not selected | |
| 13 | Ghaida_narrative_Syrian_F.mp3 | Ghaida (narrative) | Syrian | Narrative | New | Soft, warm — Stories of Syria |
| 14 | Ghaida_cheerful_Syrian_F.mp3 | Ghaida (cheerful) | Syrian | Conversational | New | Warm, friendly, melodious |
| 15 | Farah_Jordanian_F.mp3 | Farah | Jordanian | Advertisement | New | Premium — warm, clear, expressive |
| 16 | Sara_Jordanian_Jordanian_F.mp3 | Sara (Jordanian) | Jordanian | Social media | New | Kind, expressive, calm |
| 17 | Heba_Mansuri_Saudi_F.mp3 | Heba Mansuri | Saudi | Narrative | New | Calm, modulated narrator |
| 18 | Heba_Mansuri_care_Saudi_F.mp3 | Heba Mansuri (care) | Saudi | Conversational | New | Calm, trustworthy |
| 19 | Sakina_Arabic_F.mp3 | Sakina | Arabic | Narrative | New | Elegant, meditative — storytelling |
| 20 | Rima_M_Tunisian_F.mp3 | Rima M | Tunisian | Conversational | New | Soothing, calm, professional |
| 21 | Salma_bilingual_Arabic_F.mp3 | Salma (bilingual) | Arabic | Conversational | New | Arab woman 30s |
| 22 | Salma_mature_Arabic_F.mp3 | Salma (mature) | Arabic | Conversational | New | Young artist from Dubai |

### Male voices (31)

| # | File | Voice | Accent | Use Case | Amr Verdict | Notes |
|---|------|-------|--------|----------|------------|-------|
| 23 | Hanafi_Egyptian_M.mp3 | Hanafi | Egyptian | Educational | Liked | Good male narrator |
| 24 | Moncellence_Egyptian_M.mp3 | Moncellence | Egyptian | Narrative | Liked | Clear, masculine |
| 25 | Yahya_MSA_M.mp3 | Yahya | MSA | Narrative | Liked | Deep, warm, expressive |
| 26 | Abdullah_Egyptian_M.mp3 | Abdullah | Egyptian | Narrative | Not selected | |
| 27 | Adam_Egyptian_M.mp3 | Adam | Egyptian | Narrative | Not selected | |
| 28 | Amr_Egyptian_M.mp3 | Amr | Egyptian | Narrative | Not selected | |
| 29 | Anas_MSA_M.mp3 | Anas | MSA | Narrative | Not selected | |
| 30 | Ashraf_MSA_M.mp3 | Ashraf | MSA | Narrative | Not selected | |
| 31 | Cherif_Malli_MSA_M.mp3 | Cherif Malli | MSA | Narrative | Not selected | |
| 32 | Haytham_Egyptian_M.mp3 | Haytham | Egyptian | Narrative | Not selected | Too dramatic |
| 33 | Hijazi_MSA_M.mp3 | Hijazi | MSA | Narrative | Not selected | |
| 34 | Marco_Nady_Egyptian_M.mp3 | Marco Nady | Egyptian | Narrative | Not selected | |
| 35 | Meisam_MSA_M.mp3 | Meisam | MSA | Narrative | Not selected | |
| 36 | Mohamed_Ben_MSA_M.mp3 | Mohamed Ben | MSA | Narrative | Not selected | |
| 37 | Omars_MSA_M.mp3 | Omars | MSA | Narrative | Not selected | |
| 38 | Ramy_Ibrahim_Egyptian_M.mp3 | Ramy Ibrahim | Egyptian | Narrative | Not selected | |
| 39 | Ali_Saudi_Saudi_M.mp3 | Ali | Saudi | Narrative | New | Calm, resonant, steady |
| 40 | Jeddawi_Saudi_M.mp3 | Jeddawi | Saudi | Narrative | New | Deep, confident — from Jeddah |
| 41 | Ilyass_Algerian_M.mp3 | Ilyass | Algerian | Narrative | New | Pro audiobook — calm, elegant |
| 42 | Salim_Tunisian_M.mp3 | Salim | Tunisian | Narrative | New | Unique Tunisian — clarity + warmth |
| 43 | Ibrahim_Levantine_M.mp3 | Ibrahim | Levantine | Narrative | New | Quiet, flexible — storytelling |
| 44 | Odai_Palestinian_M.mp3 | Odai | Palestinian | Narrative | New | Arabic poetry reciter — expressive |
| 45 | Yousef_MSA_M.mp3 | Yousef | MSA | Educational | New | Calm, reassuring — storytelling |
| 46 | Hammam_Egyptian_M.mp3 | Hammam | Egyptian | Social media | New | Warm, calm, expressive Egyptian |
| 47 | Nasser_MSA_M.mp3 | Nasser | MSA | Educational | New | Refined, masculine |
| 48 | Mazen_Lawand_MSA_M.mp3 | Mazen Lawand | MSA | Advertisement | New | Warm, dynamic, confident |
| 49 | Ghawi_Gulf_M.mp3 | Ghawi | Gulf | Narrative | New | YouTube, audiobooks |
| 50 | Hadi_N_Levantine_M.mp3 | Hadi N | Levantine | Conversational | New | Calm, clear, professional |
| 51 | Fadi_Levantine_M.mp3 | Fadi | Levantine | Conversational | New | Natural Lebanese voice |
| 52 | Mr_FF_Syrian_M.mp3 | Mr. FF | Syrian | Conversational | New | Middle-aged conversational |
| 53 | Karim_MSA_M.mp3 | Karim | MSA | Conversational | New | Native Arabic MSA |

---

## Summary

| Provider | Voices with samples |
|----------|-------------------|
| Google Chirp3-HD | 30 |
| ElevenLabs | 53 |
| **Total** | **83** |
