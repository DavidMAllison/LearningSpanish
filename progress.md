# Spanish Learning Progress

## Current Status

- **Current System:** Family site + weekly iMessage (as of 2026-07-18)
- **Course:** Spanish in 1 Month Challenge
- **Last Updated:** 2026-07-18

## How it works now

- The course runs on the GitHub Pages site (`docs/`): https://davidmallison.github.io/LearningSpanish/
- Weekly structure: Mon-Fri lessons (2 x 10-card sessions/day), Saturday review,
  Sunday gate quiz (8/10 to unlock the next week). Fail = review and retake.
- Each family member has a personal `?u=` link; per-person progress lives in
  their own phone's browser localStorage.
- Every Sunday at 11:00pm a launchd job (`com.si1m.weekly-sms`) queues an
  iMessage per person via Keanu's outbox with their personal link.

## History

- 2026-07-18: Replaced the daily Gmail-draft cloud routine (now disabled) with
  the family site + weekly SMS. Old routine: claude.ai/code/routines.
- 2026-07-16: Restarted from Day 1 after a long gap; added 10-card
  micro-sessions to the local flashcard app (still usable via
  `flashcard-app/server.py`, superseded by the site).
- 2026-02-06: Originally stalled at Day 2.

## Notes

- Day folders (videos/PDFs) are local-only in `LLMContext/` (gitignored).
