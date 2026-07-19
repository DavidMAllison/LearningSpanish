# Learning Spanish - SI1M Challenge

## Project Overview

A 20-day Spanish language challenge ("Spanish in 1 Month") that teaches ~40% of the most commonly used Spanish words. Content is sourced from the Accelerated Spanish YouTube channel.

## Content Structure

All course materials live in `LLMContext/` with a folder per day (`Day1` through `Day20`).

- **Each day folder** contains lesson videos (`.mp4`) and optionally quiz PDFs
  - Videos are for the student to watch; not needed for homework generation/grading
  - Quiz transcript PDFs and vocabulary lists are the key reference materials
- **Every 5th day** (Day 5, 10, 15, 20) marks the end of a week and may include:
  - A weekly vocabulary list (PDF)
  - Memory palace images (PDF)
  - An additional quiz/quiz transcript (PDF)

### Weekly Themes

- **Week 1 (Days 1-5) "Foundation"**: Core grammar foundations, prepositions, articles, pronouns
- **Week 2 (Days 6-10) "Mortar"**: Ser, estar, past tense, subjunctives
- **Week 3 (Days 11-15) "Bricks"**: Possessives, verb phrases, gerunds, reflexive pronouns, ir/future
- **Week 4 (Days 16-20) "Decoration"**: Demonstratives, nouns, adverbs, polite phrases, greetings

## Homework Format

Each day has a homework assignment of ~15-20 sentences. The format is **progressive substitution** (Spanglish-to-Spanish):

1. An English sentence is provided
2. The student rewrites it, replacing all known Spanish words into the sentence (creating a "Spanglish" hybrid sentence)
3. Each day introduces new vocabulary, so sentences contain progressively more Spanish and less English
4. By the end of the course, sentences should be nearly complete Spanish

**Progression by week:**
- **Week 1**: Basic substitutions -- prepositions (de, a, en, con, por, para), connectors (que, y), demonstratives (eso), articles (el, la, los, las, un, una), pronouns (me, te, lo, la, las), negation (no), compounds (por qué, por eso, para que)
- **Week 2**: Adds ser/estar conjugations across tenses (present, imperfect, subjunctive) -- es, era, eras, son, eran, sea, seas, sean, está, estaba, estaban, esté, estés, estén, estemos, aquí, usted
- **Week 3**: Adds possessives, more verbs (ir, haber, hacer), gerunds, indirect object pronouns, reflexive pronouns
- **Week 4**: Adds demonstratives (esto/esta/estos/estas), nouns, adverbs, greetings, polite phrases

**Example (Day 5 level):**
- English: "The man from Ecuador says that he knows her."
- Answer: "**El** man **de** Ecuador says **que** he **la** knows."

## Source Spreadsheet

Original video links spreadsheet: `~/Downloads/Video Links - SI1M Challenge Updated.xlsx`

## Utility Scripts

- `download_videos.py` - Downloads YouTube videos from the spreadsheet into day folders using `/tmp/yt-dlp`
