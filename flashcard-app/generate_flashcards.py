#!/usr/bin/env python3
"""Generate Spanglish flashcards using the Anthropic Claude API.

Usage:
    python generate_flashcards.py --day 5      # Regenerate Day 5 only
    python generate_flashcards.py --all        # Regenerate all days (2-20)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
FLASHCARDS_DIR = DATA_DIR / "flashcards"
VOCABULARY_FILE = DATA_DIR / "vocabulary.json"
LLMCONTEXT_DIR = BASE_DIR.parent / "LLMContext"

# Quiz transcript PDF paths per day
QUIZ_TRANSCRIPTS = {
    2: "Day2/Day 2 Quiz Transcript.pdf",
    3: "Day3/Day 3 Quiz Transcript.pdf",
    4: "Day4/Day 4 Quiz Transcript.pdf",
    5: "Day5/Day 5 Quiz Transcript.pdf",
    6: "Day6/Day 6 Quiz Transcript.pdf",
    7: "Day7/Day 7 Quiz Transcript.pdf",
    8: "Day8/Day 8 Quiz Transcript.pdf",
    9: "Day9/Day 9 Quiz Transcript.pdf",
    10: "Day10/Day 10 Quiz Transcript.pdf",
    11: "Day11/Day 11 Quiz Transcript (1).pdf",
    12: "Day12/Day 12 Quiz Transcript (1).pdf",
    13: "Day13/Day 13 Quiz Transcript.pdf",
    14: "Day14/Day 14 Quiz Transcript (1).pdf",
    15: "Day15/Day 15 Quiz Transcript.pdf",
    16: "Day16/Day 16 Quiz Transcript.pdf",
    17: "Day17/Day 17 Quiz Transcript.pdf",
    18: "Day18/Day 18 Quiz Transcript.pdf",
    19: "Day19/Day 19 Quiz Transcript.pdf",
    20: "Day20/Day 20 Quiz Transcript.pdf",
}

ALL_DAYS = list(range(2, 21))  # Days 2-20


def load_vocabulary():
    """Load the vocabulary database from JSON."""
    with open(VOCABULARY_FILE) as f:
        return json.load(f)


def get_cumulative_vocab(vocabulary, day):
    """Get all vocabulary words available up to and including a given day."""
    cumulative = []
    for d in range(2, day + 1):
        day_key = str(d)
        if day_key in vocabulary:
            cumulative.extend(vocabulary[day_key])
    return cumulative


def get_new_vocab(vocabulary, day):
    """Get only the NEW vocabulary introduced on a specific day."""
    day_key = str(day)
    return vocabulary.get(day_key, [])


def format_vocab_list(vocab_entries):
    """Format vocabulary entries as a readable list."""
    lines = []
    for entry in vocab_entries:
        lines.append(f"- {entry['word']} ({entry['pos']}): {entry['meaning']}")
    return "\n".join(lines)


def read_quiz_pdf_base64(day):
    """Read a quiz transcript PDF and return its base64-encoded content."""
    import base64

    relative_path = QUIZ_TRANSCRIPTS.get(day)
    if not relative_path:
        return None
    full_path = LLMCONTEXT_DIR / relative_path
    if not full_path.exists():
        print(f"  Warning: Quiz transcript not found: {full_path}")
        return None
    with open(full_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def generate_flashcards_for_day(client, vocabulary, day):
    """Generate flashcards for a single day using the Claude API."""
    cumulative = get_cumulative_vocab(vocabulary, day)
    new_vocab = get_new_vocab(vocabulary, day)

    cumulative_text = format_vocab_list(cumulative)
    new_text = format_vocab_list(new_vocab) if new_vocab else "(No new words -- review day using all previous vocabulary)"

    # Determine which quiz transcript to use as a format example
    # Use the same day's transcript, or fall back to a nearby day
    example_day = day
    if day == 12:
        example_day = 11  # Day 12 is a review day
    quiz_pdf_b64 = read_quiz_pdf_base64(example_day)

    # Build the message content
    content = []

    # Include quiz transcript PDF if available
    if quiz_pdf_b64:
        content.append({
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": quiz_pdf_b64,
            },
        })

    prompt = f"""You are generating flashcards for Day {day} of a Spanish learning course called "Spanish in 1 Month" (SI1M).

The course uses a "progressive substitution" method: students start with English sentences and replace known Spanish words, creating Spanglish hybrid sentences. As they learn more Spanish words each day, the sentences become progressively more Spanish.

CUMULATIVE VOCABULARY (all Spanish words the student knows by Day {day}):
{cumulative_text}

NEW VOCABULARY FOR DAY {day}:
{new_text}

{"I have attached the Day " + str(example_day) + " quiz transcript PDF as a format reference. Study the pairs carefully -- each pair has an English sentence followed by the Spanglish answer where known Spanish words replace their English equivalents." if quiz_pdf_b64 else ""}

INSTRUCTIONS:
1. Generate exactly 20 flashcard pairs in the same style as the quiz transcript.
2. Each pair has:
   - An English sentence (natural, varied, conversational)
   - A Spanglish answer where ALL known Spanish vocabulary words are substituted in
3. Mark Spanish words in the answer with double asterisks for bold: **word**
4. Emphasize the NEW vocabulary for Day {day} -- make sure most sentences use at least one new word
5. Use a variety of sentence structures and topics (daily life, relationships, work, travel, etc.)
6. Keep sentences natural and conversational, not artificial or repetitive
7. For questions, use inverted punctuation: ¿...? and ¡...!
8. Make sure EVERY Spanish word the student knows is substituted -- never leave a word in English if its Spanish equivalent is in the vocabulary list
9. The English words that remain should be common English words NOT in the vocabulary list

Output ONLY valid JSON in this exact format (no markdown, no code fences):
{{"cards": [
  {{"english": "The English sentence.", "answer": "**The** Spanglish answer."}},
  ...
]}}"""

    content.append({"type": "text", "text": prompt})

    print(f"  Calling Claude API...")
    response = client.messages.create(
        model="claude-sonnet-4-5-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": content}],
    )

    # Extract the text response
    response_text = response.content[0].text.strip()

    # Try to parse JSON -- handle potential markdown fences
    if response_text.startswith("```"):
        # Strip markdown code fences
        lines = response_text.split("\n")
        # Remove first and last fence lines
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        response_text = "\n".join(lines)

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"  Error parsing API response as JSON: {e}")
        print(f"  Raw response:\n{response_text[:500]}")
        return None

    # Build the final flashcard file
    result = {
        "day": day,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cards": data["cards"],
    }

    return result


def save_flashcards(day, flashcard_data):
    """Save flashcard data to a JSON file."""
    FLASHCARDS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FLASHCARDS_DIR / f"day{day}.json"
    with open(output_path, "w") as f:
        json.dump(flashcard_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate SI1M Spanglish flashcards")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--day", type=int, help="Generate flashcards for a specific day (2-20)")
    group.add_argument("--all", action="store_true", help="Generate flashcards for all days")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is required.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    vocabulary = load_vocabulary()

    if args.all:
        days = ALL_DAYS
    else:
        if args.day < 2 or args.day > 20:
            print("Error: Day must be between 2 and 20.")
            sys.exit(1)
        days = [args.day]

    for day in days:
        print(f"Generating Day {day} flashcards...")
        result = generate_flashcards_for_day(client, vocabulary, day)
        if result:
            save_flashcards(day, result)
            print(f"  Generated {len(result['cards'])} cards.")
        else:
            print(f"  Failed to generate Day {day}.")

    print("Done!")


if __name__ == "__main__":
    main()
