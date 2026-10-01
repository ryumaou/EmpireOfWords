#!/usr/bin/env python3
"""
new_lc.py -- Python port of the supplied new-lc.pl.

This is the file-output variant of lc.pl. It uses the same two-character
conflux algorithm but writes generated words to an explicitly named file.

Original-style:
    python new_lc.py -25 language.txt chinese.txt

Modern:
    python new_lc.py 25 language.txt chinese.txt
"""
from __future__ import annotations
import argparse
import random
import re
import sys
from pathlib import Path

MIN_LENGTH = 3
MAX_LENGTH = 7


def read_source_text(path: Path) -> str:
    """Read modern UTF-8 or legacy Windows-1252 without inventing U+FFFD."""
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def configure_utf8_stdio() -> None:
    """Make Windows pipes deterministic and independent of the console code page."""
    for stream_name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")


def load_data(path: Path) -> list[str]:
    data = []
    for line in read_source_text(path).splitlines(keepends=True):
        line = re.sub(r"#.*", "", line)
        if not line:
            continue
        line = re.sub(r"^\s*", "", line)
        line = re.sub(r"\s*\n$", "", line)
        line = re.sub(r"\s+", " ", line, count=1)
        data.extend([" ", *list(line)])
    if len(data) < 2:
        raise ValueError("source data contains too little usable text")
    data.extend([" ", data[1]])
    return data


def build_tables(data):
    followers = {}
    start_pairs = []
    for i in range(len(data) - 2):
        first, second, third = data[i:i+3]
        pair = first + second
        followers[pair] = followers.get(pair, "") + third
        if first == " ":
            start_pairs.append(second + third)
    return followers, start_pairs


def new_word(seed, followers, rng, min_length):
    word = seed
    for _ in range(100000):
        pair = word[-2:]
        choices = followers.get(pair, "")
        if not choices:
            raise RuntimeError(f"no continuation found for pair {pair!r}")
        letter = rng.choice(choices)
        if word.endswith(" "):
            if len(word) > min_length:
                return word
            word = word[-1:] + letter
        else:
            word = word.lstrip(" ")
            word += letter
    raise RuntimeError("generation did not terminate")


def main(argv=None):
    configure_utf8_stdio()
    argv = list(sys.argv[1:] if argv is None else argv)

    # Old syntax: -25 output input
    if len(argv) == 3 and re.fullmatch(r"-\d+", argv[0]):
        number = int(argv[0][1:])
        output = Path(argv[1])
        source = Path(argv[2])
        seed = None
        min_length = MIN_LENGTH
        max_length = MAX_LENGTH
    else:
        p = argparse.ArgumentParser(description="File-output port of new-lc.pl")
        p.add_argument("number", type=int)
        p.add_argument("output", type=Path)
        p.add_argument("source", type=Path)
        p.add_argument("--seed", type=int)
        p.add_argument("--min-length", type=int, default=MIN_LENGTH)
        p.add_argument("--max-length", type=int, default=MAX_LENGTH)
        a = p.parse_args(argv)
        number, output, source = a.number, a.output, a.source
        seed, min_length, max_length = a.seed, a.min_length, a.max_length

    rng = random.Random(seed)
    try:
        data = load_data(source)
        followers, starts = build_tables(data)
        new = rng.choice(starts)
        with output.open("w", encoding="utf-8", newline="\n") as fh:
            for _ in range(number):
                new = new_word(new[-2:], followers, rng, min_length)
                fh.write(new[:max_length] + "\n")
    except (OSError, ValueError, RuntimeError, IndexError) as exc:
        print(f"{Path(sys.argv[0]).name}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
