#!/usr/bin/env python3
"""Monday Morning Punchlines — entry program.

The joke lives in joke.txt next to this script. This program loads it,
checks it against the competition's gate (UTF-8 text, 1-200 characters,
not only whitespace, exactly one line), and writes it verbatim to
/output/entry.txt (or $MAKEFUN_OUTPUT_DIR/entry.txt when that is set).

The write is atomic — the joke goes to a temporary file in the same
directory first and is then moved into place — and the finished file is
read back and compared byte for byte with the joke, so a run can never
report success while leaving a partial or wrong entry.txt behind.

Python 3 standard library only; no network, no arguments needed.
"""

import os
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "joke.txt"
MIN_LEN = 1
MAX_LEN = 200


def load_joke() -> str:
    """Read the joke, dropping a single trailing line ending if present.

    Raises OSError when the file cannot be read and UnicodeDecodeError
    when it is not valid UTF-8; main() turns both into a one-line
    error message instead of a traceback.
    """
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


def write_entry(text: str, out_dir: Path) -> Path:
    """Write the joke to <out_dir>/entry.txt, atomically and verified.

    The bytes go to a temporary file in the same directory first, then
    os.replace() moves it into place, so an interrupted run can never
    leave a half-written entry.txt behind. The finished file is read
    back and compared byte for byte with the joke; a mismatch is an
    error, not a success message. Raises OSError on any failure.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.txt"
    if out_path.is_dir():
        raise IsADirectoryError(f"output path is a directory: {out_path}")
    data = text.encode("utf-8")
    fd, tmp_name = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, out_path)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise
    if out_path.read_bytes() != data:
        raise OSError(f"verification failed: {out_path} does not match the joke")
    return out_path


def main() -> int:
    try:
        text = load_joke()
    except FileNotFoundError:
        print(f"error: joke file not found: {SOURCE}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(f"error: joke file is not valid UTF-8: {SOURCE}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: cannot read joke file {SOURCE}: {exc}", file=sys.stderr)
        return 1
    bad = problems(text)
    if bad:
        for reason in bad:
            print(f"error: {reason}", file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        out_path = write_entry(text, out_dir)
    except OSError as exc:
        print(f"error: cannot write entry: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {len(text)} characters to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
