# Learning Spanish — SI1M Family Challenge

A family learning system built around the 20-day "Spanish in 1 Month" (SI1M)
course from the Accelerated Spanish YouTube channel. Lessons use progressive
substitution: English sentences gradually absorb Spanish vocabulary,
becoming "Spanglish" and eventually nearly full Spanish.

## Structure

- **`docs/`** — static site served via GitHub Pages
  - `index.html` — per-user week dashboard (Mon–Fri lessons, Sat review, Sun quiz)
  - `lesson.html` — flashcard session player (two 10-card sessions per day)
  - `quiz.html` — end-of-week gate quiz; score 8/10 to unlock the next week
  - `data/days/` — flashcard content for days 2–20
  - `data/quizzes/` — the four weekly gate quizzes
  - Progress is stored per-user in the browser's localStorage; visitors are
    identified by a `?u=<code>` link parameter.
- **`scripts/send_weekly_sms.py`** — queues a weekly iMessage (Sunday 11pm,
  via a local `launchd` job) containing each person's personal site link.
  Recipient details live in a gitignored config file.
- **`flashcard-app/`** — earlier local-only flashcard web app (predecessor of
  the site; still works locally via `python3 server.py`).
- **`download_videos.py`** — downloads course videos into `LLMContext/`
  (gitignored) from the source spreadsheet.

## Course structure

| Week | Days | Theme |
|------|------|-------|
| 1 | 1–5 | Foundation |
| 2 | 6–10 | Mortar |
| 3 | 11–15 | Bricks |
| 4 | 16–20 | Decoration |

Each day has ~20 flashcards split into two 10-card sessions. Weekly quizzes
gate progression: pass to advance, fail and review until you pass.
