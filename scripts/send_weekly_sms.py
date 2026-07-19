#!/usr/bin/env python3
"""Queue the weekly SI1M Spanish iMessage for each family member.

Writes one JSON spool file per recipient into Keanu's outbox directory
(/Users/Shared/cooking-state/outbox/). Keanu's daemon picks each file up
within a few seconds and sends it via iMessage. This is Keanu's sanctioned
cross-project handoff pattern — no Keanu code is imported or modified.

Usage:
    python3 send_weekly_sms.py            # queue messages for all recipients
    python3 send_weekly_sms.py --dry-run  # print what would be queued
    python3 send_weekly_sms.py --only d   # queue only for the given user code

Config: sms_config.json (same directory, gitignored):
    {
      "site_url": "https://example.github.io/repo/",
      "outbox_dir": "/Users/Shared/cooking-state/outbox",
      "recipients": [{"handle": "+1...", "code": "d"}, ...]
    }
"""

import argparse
import json
import sys
import time
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "sms_config.json"

MESSAGE = "\U0001F1EA\U0001F1F8 Spanish week ahead! Your lessons for this week: {url}?u={code}"


def main():
    parser = argparse.ArgumentParser(description="Queue weekly SI1M iMessages via Keanu outbox")
    parser.add_argument("--dry-run", action="store_true", help="print messages without queuing")
    parser.add_argument("--only", metavar="CODE", help="only send to the recipient with this user code")
    args = parser.parse_args()

    if not CONFIG_PATH.exists():
        print(f"Error: config not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)

    config = json.loads(CONFIG_PATH.read_text())
    outbox = Path(config["outbox_dir"])
    site_url = config["site_url"].rstrip("/") + "/"

    recipients = config["recipients"]
    if args.only:
        recipients = [r for r in recipients if r["code"] == args.only]
        if not recipients:
            print(f"Error: no recipient with code '{args.only}'", file=sys.stderr)
            sys.exit(1)

    if not args.dry_run and not outbox.is_dir():
        print(f"Error: outbox directory not found: {outbox}", file=sys.stderr)
        sys.exit(1)

    for r in recipients:
        text = MESSAGE.format(url=site_url, code=r["code"])
        entry = {"handle": r["handle"], "text": text}
        if args.dry_run:
            print(f"[dry-run] {r['handle']}: {text}")
            continue
        # Create-exclusive unique filename so concurrent writers can't collide
        filename = f"si1m-weekly-{int(time.time() * 1000)}-{r['code']}.json"
        path = outbox / filename
        with open(path, "x") as f:
            json.dump(entry, f)
        print(f"queued {path.name} -> {r['handle']}")


if __name__ == "__main__":
    main()
