#!/usr/bin/env python3
"""
prop.py -- faithful Python port of Christopher Pound's prop.pl (Oct 1995).

Turns lc output into two-part proper names.

Original behavior:
- count only a/e/i/o/u in each generated word (y is NOT a vowel here);
- fewer than 3 vowels -> short-name pool;
- 3 or more vowels -> long-name pool;
- truncate the larger pool to the size of the smaller;
- pop one item from each pool;
- uppercase the first character of each;
- randomly print "short long" or "long short".
"""
from __future__ import annotations
import argparse
import random
import sys
from pathlib import Path

VOWEL_CUTOFF = 3
VOWELS = set("aeiou")


def read_text_auto(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def configure_utf8_stdio() -> None:
    for stream_name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")


def read_lines(files):
    if not files:
        return [line.rstrip("\r\n") for line in sys.stdin]
    result = []
    for name in files:
        result.extend(line.rstrip("\r\n") for line in read_text_auto(Path(name)).splitlines(keepends=True))
    return result


def perl_ascii_capitalize_first(word: str) -> str:
    # Perl's tr/[a-z]/[A-Z]/ affects ASCII lowercase only.
    if word and "a" <= word[0] <= "z":
        return chr(ord(word[0]) - 32) + word[1:]
    return word


def main():
    configure_utf8_stdio()
    p = argparse.ArgumentParser(description="Python port of Christopher Pound's prop.pl")
    p.add_argument("files", nargs="*")
    p.add_argument("--seed", type=int, help="Python-only reproducibility option")
    p.add_argument("--vowel-cutoff", type=int, default=VOWEL_CUTOFF)
    args = p.parse_args()
    rng = random.Random(args.seed)

    short = []
    long = []
    for word in read_lines(args.files):
        v = sum(1 for c in word if c in VOWELS)
        if v < args.vowel_cutoff:
            short.append(word)
        else:
            long.append(word)

    # Perl sets $#short=$#long or vice versa. This retains the earliest
    # elements and discards excess elements from the END of the larger array.
    size = min(len(short), len(long))
    short = short[:size]
    long = long[:size]

    while short:
        a = perl_ascii_capitalize_first(short.pop())
        b = perl_ascii_capitalize_first(long.pop())
        if rng.randrange(2):
            print(f"{a} {b}")
        else:
            print(f"{b} {a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
