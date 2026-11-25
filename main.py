#!/usr/bin/env python3
"""Monday Morning Punchlines — entry program.

The joke lives in joke.txt next to this script. This program loads it,
checks it against the competition's gate (UTF-8 text, 1-200 characters,
not only whitespace, exactly one line), and writes it verbatim to
/output/entry.txt (or $MAKEFUN_OUTPUT_DIR/entry.txt when that is set).

Python 3 standard library only; no network, no arguments needed.
"""

import os
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "joke.txt"
MIN_LEN = 1
MAX_LEN = 200


def load_joke() -> str:
    """Read the joke, dropping a single trailing line ending if present."""
    text = SOURCE.read_text(encoding="utf-8")
    for ending in ("\r\n", "\n", "\r"):
        if text.endswith(ending):
            text = text[: -len(ending)]
            break
    return text


def problems(text: str) -> list[str]:
    """Every way the joke can fail the gate, as human-readable reasons."""
    found: list[str] = []
    if "\n" in text or "\r" in text:
        found.append("joke must be exactly one line")
    if not text.strip():
        found.append("joke must not be empty or only whitespace")
    if not MIN_LEN <= len(text) <= MAX_LEN:
        found.append(
            f"joke must be {MIN_LEN}-{MAX_LEN} characters, got {len(text)}"
        )
    return found


def main() -> int:
    text = load_joke()
    bad = problems(text)
    if bad:
        for reason in bad:
            print(f"error: {reason}", file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.txt"
    out_path.write_text(text, encoding="utf-8")
    print(f"wrote {len(text)} characters to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
