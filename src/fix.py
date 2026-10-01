#!/usr/bin/env python3
"""
fix.py -- faithful Python port of Christopher Pound's fix.pl (Nov 1996).

The original:
- chooses one affix length randomly from 2..4 characters;
- derives approximately one affix for every ten input words;
- chooses a prefix source 1/3 of the time, suffix source 2/3;
- accepts only candidate affixes containing a/e/i/o/u/y;
- leaves roughly half the input words unchanged;
- attaches a random derived affix to the other half;
- removes one vowel at a vowel/vowel join;
- lowercases the base when prefixing, or the affix when suffixing.
"""
from __future__ import annotations
import argparse
import random
import sys
from pathlib import Path

VOWELS = set("aeiouy")


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


def main():
    configure_utf8_stdio()
    p = argparse.ArgumentParser(description="Python port of Christopher Pound's fix.pl")
    p.add_argument("files", nargs="*")
    p.add_argument("--seed", type=int, help="Python-only reproducibility option")
    args = p.parse_args()
    rng = random.Random(args.seed)

    basic = read_lines(args.files)
    if not basic:
        return 0

    howlong = rng.randrange(3) + 2
    words = basic[:]

    # Perl: int($#basic/10)+1 where $#basic == len(basic)-1
    lim = int((len(basic) - 1) / 10) + 1
    fixes = []

    # Perl can fail if the corpus cannot yield enough vowel-containing
    # fragments. Keep its selection logic but protect against infinite loops.
    attempts = 0
    max_attempts = max(10000, len(words) * 100)
    while len(fixes) < lim:
        attempts += 1
        if attempts > max_attempts or not words:
            raise RuntimeError("not enough usable source fragments to derive requested affixes")

        idx = rng.randrange(len(words))
        word = words.pop(idx)
        pre = (rng.randrange(3) + 1) == 3
        if pre:
            fix = word[:howlong]
        else:
            fix = word[max(0, len(word) - howlong):]

        if not any(ch in VOWELS for ch in fix):
            continue
        fixes.append((pre, fix))

    for w in basic:
        # Perl: if (int(rand(2))) { print unchanged; next; }
        if rng.randrange(2):
            print(w)
            continue

        pre, fix = rng.choice(fixes)
        vp = bool(fix) and fix[0] in VOWELS
        vs = bool(fix) and fix[-1] in VOWELS

        if pre:
            if w and w[0] in VOWELS and vs:
                w = w[1:]
            w = w.lower()
            print(fix + w)
        else:
            if w and w[-1] in VOWELS and vp:
                w = w[:-1]
            fix = fix.lower()
            print(w + fix)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"{Path(sys.argv[0]).name}: {exc}", file=sys.stderr)
        raise SystemExit(1)
