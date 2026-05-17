"""Partition a unigram frequency CSV into one bucket per consonant pattern.

Reads a CSV like Google's `unigram_freq.csv` (word,count) and writes one file
per distinct consonant pattern to `buckets/<N>/<pattern>.txt`, where N is the
number of mapped consonants. Each output file is `word<TAB>frequency`, sorted
by frequency descending.

The mapping is shape-based (M -> 3 because M rotated is a 3, S -> 5 because
S looks like a mirrored 5, etc.). See thoughts.md for the full story.
"""

import argparse
import csv
import os
from collections import defaultdict

LETTER_TO_DIGIT = {
    'B': 8, 'C': 6, 'D': 0, 'F': 6, 'G': 6, 'H': 8, 'J': 9, 'K': 4, 'L': 1,
    'M': 3, 'N': 2, 'P': 9, 'Q': 0, 'R': 4, 'S': 5, 'T': 7, 'V': 1, 'W': 3,
    'X': 0, 'Z': 2,
}


def consonant_pattern(word: str) -> str:
    return ''.join(
        str(LETTER_TO_DIGIT[c])
        for c in word.upper()
        if c in LETTER_TO_DIGIT
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_path', help='Unigram CSV (word,count). Header expected.')
    parser.add_argument('--out', default='buckets', help='Output directory (default: buckets)')
    parser.add_argument('--min-len', type=int, default=3, help='Min word length (default: 3)')
    parser.add_argument('--max-len', type=int, default=14, help='Max word length (default: 14)')
    parser.add_argument('--min-pattern', type=int, default=2, help='Min consonant count (default: 2)')
    args = parser.parse_args()

    by_pattern = defaultdict(list)

    with open(args.csv_path) as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for row in reader:
            if len(row) < 2:
                continue
            word, count = row[0], row[1]
            if len(word) < args.min_len or len(word) > args.max_len:
                continue
            if not any(v in word.lower() for v in 'aeiouy'):
                continue
            pattern = consonant_pattern(word)
            if len(pattern) < args.min_pattern:
                continue
            try:
                by_pattern[pattern].append((word, int(count)))
            except ValueError:
                continue

    # Write one file per pattern, sorted by frequency desc
    total = 0
    per_n = defaultdict(int)
    for pattern, items in by_pattern.items():
        items.sort(key=lambda x: -x[1])
        n = len(pattern)
        subdir = os.path.join(args.out, str(n))
        os.makedirs(subdir, exist_ok=True)
        with open(os.path.join(subdir, f'{pattern}.txt'), 'w') as out:
            for word, count in items:
                out.write(f'{word}\t{count}\n')
        total += len(items)
        per_n[n] += 1

    print(f'wrote {total:,} words across {len(by_pattern):,} patterns')
    print(f"{'len':>4} {'patterns':>10}")
    for n in sorted(per_n):
        print(f'{n:>4} {per_n[n]:>10,}')


if __name__ == '__main__':
    main()
