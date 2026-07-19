#!/usr/bin/env python3
"""Validate Spanglish sentences using the Anthropic Claude API.

This module validates that a user's Spanglish sentence correctly substitutes
all known Spanish vocabulary words for a given day.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
VOCABULARY_FILE = DATA_DIR / "vocabulary.json"


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


def format_vocab_for_prompt(vocab_entries):
    """Format vocabulary entries for the validation prompt."""
    lines = []
    for entry in vocab_entries:
        lines.append(f"- {entry['word']} ({entry['pos']}): {entry['meaning']}")
    return "\n".join(lines)


def validate_sentences(api_key, sentences, day):
    """Validate Spanglish sentences using Claude.

    Args:
        api_key: Anthropic API key
        sentences: List of sentence strings to validate
        day: The day number (2-20) determining available vocabulary

    Returns:
        List of result dicts with: is_correct, feedback, corrected
    """
    import anthropic

    vocabulary = load_vocabulary()
    cumulative = get_cumulative_vocab(vocabulary, day)
    vocab_text = format_vocab_for_prompt(cumulative)

    client = anthropic.Anthropic(api_key=api_key)

    results = []
    for sentence in sentences:
        result = validate_single_sentence(client, sentence, day, vocab_text)
        results.append(result)

    return results


def validate_single_sentence(client, sentence, day, vocab_text):
    """Validate a single Spanglish sentence."""
    prompt = f"""You are validating a Spanglish sentence for Day {day} of a Spanish learning course.

The course uses "progressive substitution": students start with English sentences and replace known Spanish words, creating Spanglish hybrid sentences.

VOCABULARY AVAILABLE BY DAY {day}:
{vocab_text}

STUDENT'S SENTENCE:
"{sentence}"

TASK:
Check if the student has correctly substituted ALL Spanish words they should know by Day {day}.

Rules:
1. Every English word that has a Spanish equivalent in the vocabulary list MUST be replaced with its Spanish form
2. Spanish words should be in the correct form (articles must agree: el/la/los/las, pronouns in correct position, etc.)
3. Words NOT in the vocabulary list should remain in English
4. Word order follows Spanish conventions for pronouns (before the verb)

Respond with ONLY valid JSON (no markdown, no code fences):
{{
  "is_correct": true or false,
  "feedback": "Brief explanation of what was correct or what needs to be fixed",
  "corrected": "The corrected Spanglish sentence if is_correct is false, or the same sentence if correct"
}}"""

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = response.content[0].text.strip()

    # Handle potential markdown fences
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        response_text = "\n".join(lines)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {
            "is_correct": False,
            "feedback": "Error parsing validation response. Please try again.",
            "corrected": sentence,
        }
