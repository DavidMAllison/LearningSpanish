#!/usr/bin/env python3
"""Local HTTP server for the SI1M Flashcard app.

Serves the web UI, flashcard JSON data, and provides a regeneration API.

Usage:
    ANTHROPIC_API_KEY=sk-... python server.py
    # Opens on http://localhost:8000
"""

import json
import mimetypes
import os
import sys
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).parent


class FlashcardHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves static files and the regeneration API."""

    def __init__(self, *args, **kwargs):
        # Serve files from the flashcard-app directory
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        # Serve index.html for the root path
        if self.path == "/" or self.path == "":
            self.path = "/static/index.html"
        elif self.path.startswith("/content/"):
            self.serve_content_file()
            return
        super().do_GET()

    def serve_content_file(self):
        """Serve files from the LLMContext directory under /content/."""
        # Decode URL-encoded path (handles spaces in filenames)
        rel_path = urllib.parse.unquote(self.path[len("/content/"):])

        # Resolve against LLMContext directory with path traversal protection
        content_dir = (BASE_DIR / ".." / "LLMContext").resolve()
        file_path = (content_dir / rel_path).resolve()

        if not str(file_path).startswith(str(content_dir)):
            self.send_error(403, "Forbidden")
            return

        if not file_path.is_file():
            self.send_error(404, "File not found")
            return

        # Determine content type
        content_type, _ = mimetypes.guess_type(str(file_path))
        if content_type is None:
            content_type = "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            # Inline display for PDFs, download for others
            disposition = "inline" if content_type == "application/pdf" else "attachment"
            self.send_header("Content-Disposition", f'{disposition}; filename="{file_path.name}"')
            self.end_headers()
            self.wfile.write(data)
        except OSError:
            self.send_error(500, "Error reading file")

    def do_POST(self):
        if self.path == "/api/regenerate":
            self.handle_regenerate()
        elif self.path == "/api/validate":
            self.handle_validate()
        else:
            self.send_error(404, "Not found")

    def handle_regenerate(self):
        # Check for API key
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            self.send_json_error(500, "ANTHROPIC_API_KEY environment variable not set")
            return

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json_error(400, "Invalid JSON")
            return

        day_value = data.get("day")
        if day_value is None:
            self.send_json_error(400, "Missing 'day' field")
            return

        # Import generation logic
        sys.path.insert(0, str(BASE_DIR))
        import anthropic

        from generate_flashcards import (
            ALL_DAYS,
            generate_flashcards_for_day,
            load_vocabulary,
            save_flashcards,
        )

        client = anthropic.Anthropic(api_key=api_key)
        vocabulary = load_vocabulary()

        if day_value == "all":
            days = ALL_DAYS
        else:
            try:
                day_num = int(day_value)
            except (ValueError, TypeError):
                self.send_json_error(400, "Invalid day value")
                return
            if day_num < 2 or day_num > 20:
                self.send_json_error(400, "Day must be between 2 and 20")
                return
            days = [day_num]

        results = {}
        for d in days:
            print(f"Generating Day {d} flashcards...")
            result = generate_flashcards_for_day(client, vocabulary, d)
            if result:
                save_flashcards(d, result)
                results[d] = len(result["cards"])
                print(f"  Generated {len(result['cards'])} cards.")
            else:
                results[d] = 0
                print(f"  Failed to generate Day {d}.")

        self.send_json_response(200, {"status": "ok", "generated": results})

    def handle_validate(self):
        # Check for API key
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            self.send_json_error(500, "ANTHROPIC_API_KEY environment variable not set")
            return

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json_error(400, "Invalid JSON")
            return

        sentences = data.get("sentences")
        day = data.get("day")

        if not sentences or not isinstance(sentences, list):
            self.send_json_error(400, "Missing or invalid 'sentences' field (must be array)")
            return

        if day is None:
            self.send_json_error(400, "Missing 'day' field")
            return

        try:
            day_num = int(day)
        except (ValueError, TypeError):
            self.send_json_error(400, "Invalid day value")
            return

        if day_num < 2 or day_num > 20:
            self.send_json_error(400, "Day must be between 2 and 20")
            return

        # Import validation logic
        sys.path.insert(0, str(BASE_DIR))
        from validate_sentences import validate_sentences

        print(f"Validating {len(sentences)} sentence(s) for Day {day_num}...")
        results = validate_sentences(api_key, sentences, day_num)
        print(f"  Validation complete.")

        self.send_json_response(200, {"status": "ok", "results": results})

    def send_json_response(self, code, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json_error(self, code, message):
        self.send_json_response(code, {"error": message})

    def log_message(self, format, *args):
        # Cleaner logging
        print(f"[server] {args[0]}")


def main():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("localhost", port), FlashcardHandler)
    print(f"SI1M Flashcard server running at http://localhost:{port}")
    print("Press Ctrl+C to stop.")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\nWarning: ANTHROPIC_API_KEY not set. Regeneration will not work.")
        print("Set it with: export ANTHROPIC_API_KEY=sk-...")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
