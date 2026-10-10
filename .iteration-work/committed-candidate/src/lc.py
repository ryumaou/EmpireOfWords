#!/usr/bin/env python3
"""
lc.py -- Python port of Christopher Pound's lc.pl language confluxer.

Original algorithm preserved:
- Read a source-language word corpus.
- Strip # comments and normalize whitespace.
- Build a mapping from every two-character pair to all characters observed
  following that pair (duplicates retained as probability weights).
- Record pairs that occur at word starts.
- Generate each new word by walking the pair table.
- Seed the next generated word from the final pair of the previous result.
- Reject words that terminate before the configured minimum.
- Truncate printed words to the configured maximum.

Original Perl defaults:
    min_length = 3
    max_length = 7

Compatibility:
    python lc.py -50 datafile
    python lc.py -s datafile

Modern equivalents are also accepted:
    python lc.py 50 datafile
    python lc.py --stats datafile
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
    data: list[str] = []
    for line in read_source_text(path).splitlines(keepends=True):
        line = re.sub(r"#.*", "", line)
        if not line:
            continue
        line = re.sub(r"^\s*", "", line)
        line = re.sub(r"\s*\n$", "", line)
        # Perl's s/\s+/ / has no /g: replace only the first run.
        line = re.sub(r"\s+", " ", line, count=1)
        data.extend([" ", *list(line)])
    if len(data) < 2:
        raise ValueError("source data contains too little usable text")
    # Perl: push(@data, ' ', $data[1]);
    data.extend([" ", data[1]])
    return data


def build_tables(data: list[str]) -> tuple[dict[str, str], list[str]]:
    followers: dict[str, str] = {}
    start_pairs: list[str] = []
    # Equivalent to shifting the Perl @data array until only two chars remain.
    for i in range(len(data) - 2):
        first, second, third = data[i], data[i + 1], data[i + 2]
        pair = first + second
        followers[pair] = followers.get(pair, "") + third
        if first == " ":
            start_pairs.append(second + third)
    return followers, start_pairs


def new_word(seed: str, followers: dict[str, str], rng: random.Random,
             min_length: int = MIN_LENGTH) -> str:
    """Iterative equivalent of the original Perl recursive new_word()."""
    word = seed
    safety = 0
    while True:
        safety += 1
        if safety > 100000:
            raise RuntimeError("generation did not terminate; check source corpus")

        pair = word[-2:]
        choices = followers.get(pair, "")
        if not choices:
            # The Perl script assumes every reached pair exists. Give a useful
            # error rather than silently inventing behavior.
            raise RuntimeError(f"no continuation found for pair {pair!r}")
        letter = rng.choice(choices)

        if word.endswith(" "):
            if len(word) > min_length:
                return word
            word = word[-1:] + letter
        else:
            if word.startswith(" "):
                word = word[1:]
            word += letter


def generate(path: Path, number: int, rng: random.Random,
             min_length: int = MIN_LENGTH,
             max_length: int = MAX_LENGTH) -> list[str]:
    data = load_data(path)
    followers, start_pairs = build_tables(data)
    if not start_pairs:
        raise ValueError("no word-start pairs found in source data")

    new = rng.choice(start_pairs)
    result: list[str] = []
    for _ in range(number):
        new = new_word(new[-2:], followers, rng, min_length)
        result.append(new[:max_length])
    return result


def parse_cli(argv: list[str]) -> argparse.Namespace:
    # Preserve the old "-50 filename" and "-s filename" interface.
    if len(argv) == 2 and re.fullmatch(r"-\d+", argv[0]):
        return argparse.Namespace(
            source=Path(argv[1]), number=int(argv[0][1:]), stats=False,
            seed=None, min_length=MIN_LENGTH, max_length=MAX_LENGTH
        )
    if len(argv) == 2 and argv[0].startswith("-s"):
        return argparse.Namespace(
            source=Path(argv[1]), number=0, stats=True,
            seed=None, min_length=MIN_LENGTH, max_length=MAX_LENGTH
        )

    p = argparse.ArgumentParser(description="Christopher Pound lc.pl port")
    p.add_argument("number", nargs="?", type=int, default=250)
    p.add_argument("source", type=Path)
    p.add_argument("-s", "--stats", action="store_true")
    p.add_argument("--seed", type=int)
    p.add_argument("--min-length", type=int, default=MIN_LENGTH)
    p.add_argument("--max-length", type=int, default=MAX_LENGTH)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    args = parse_cli(list(sys.argv[1:] if argv is None else argv))
    rng = random.Random(args.seed)

    try:
        data = load_data(args.source)
        followers, start_pairs = build_tables(data)
    except (OSError, ValueError) as exc:
        print(f"{Path(sys.argv[0]).name}: {exc}", file=sys.stderr)
        return 1

    if args.stats:
        # Original Perl prints hash entries in hash order. Python dict insertion
        # order is used here because Perl hash order is implementation-specific.
        for pair, chars in followers.items():
            print(f"{pair}:{chars}")
        return 0

    try:
        new = rng.choice(start_pairs)
        for _ in range(args.number):
            new = new_word(new[-2:], followers, rng, args.min_length)
            print(new[:args.max_length])
    except (RuntimeError, IndexError) as exc:
        print(f"{Path(sys.argv[0]).name}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
