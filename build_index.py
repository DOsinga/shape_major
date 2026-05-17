"""Combine prioritized buckets into the single word_index.json the web app loads.

Reads `prioritized/<N>/<pattern>.txt` for each length 2..max_length, drops the
frequency column, and writes one JSON object mapping pattern -> [word, ...]
(ranked best-first by mnemonic quality, as the agents ordered them).
"""

import argparse
import glob
import json
import os


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prioritized', default='prioritized', help='Input prioritized/ dir')
    parser.add_argument('--out', default='static/word_index.json', help='Output JSON path')
    parser.add_argument('--max-length', type=int, default=6,
                        help='Drop patterns longer than this (default: 6 — L7+ has near-zero coverage)')
    args = parser.parse_args()

    index = {}
    per_length = {}

    for length_dir in sorted(glob.glob(os.path.join(args.prioritized, '*'))):
        try:
            n = int(os.path.basename(length_dir))
        except ValueError:
            continue
        if n > args.max_length:
            continue
        count = 0
        for fpath in sorted(glob.glob(os.path.join(length_dir, '*.txt'))):
            pattern = os.path.splitext(os.path.basename(fpath))[0]
            words = []
            for line in open(fpath):
                line = line.rstrip()
                if not line:
                    continue
                w = line.split('\t')[0]
                words.append(w)
            if words:
                index[pattern] = words
                count += len(words)
        per_length[n] = (sum(1 for k in index if len(k) == n), count)

    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))

    size = os.path.getsize(args.out)
    total = sum(len(v) for v in index.values())
    print(f'wrote {args.out} ({size/1024:.1f} KB)')
    print(f'  patterns: {len(index):,}')
    print(f'  words:    {total:,}')
    print()
    print(f"  {'len':>4} {'patterns':>10} {'words':>10}")
    for n, (pats, words) in sorted(per_length.items()):
        print(f'  {n:>4} {pats:>10,} {words:>10,}')


if __name__ == '__main__':
    main()
