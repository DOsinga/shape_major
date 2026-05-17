"""Prepare buckets for parallel agent curation.

Two outputs:
1. `prioritized/<N>/<pattern>.txt` — copy of each bucket file with a frequency
   floor applied. This is the starting state agents operate on for length 4+.
2. `chunks/<N>/<style>/<NNN>.txt` — chunk files of pattern names (or for
   "yesno" style, lines of `pattern<TAB>word<TAB>freq`). Each chunk gets one
   agent.

For lengths 5+ we split into "yesno" (single-candidate buckets — agent just
decides keep/drop) and "curate" (2+ candidates — agent picks top-N). For
lengths 2-4 every bucket goes to the curate batch.
"""

import argparse
import glob
import math
import os


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--buckets', default='buckets', help='Input buckets/ dir')
    parser.add_argument('--prioritized', default='prioritized', help='Output prioritized/ dir')
    parser.add_argument('--chunks', default='chunks', help='Output chunks/ dir')
    parser.add_argument('--length', type=int, required=True, help='Pattern length to process')
    parser.add_argument('--floor', type=int, default=0, help='Frequency floor (drop entries below)')
    parser.add_argument('--yesno-per-chunk', type=int, default=475,
                        help='Single-candidate patterns per yes/no chunk (default: 475)')
    parser.add_argument('--curate-per-chunk', type=int, default=170,
                        help='Multi-candidate patterns per curate chunk (default: 170)')
    parser.add_argument('--no-split', action='store_true',
                        help='Always use curate chunks (no yes/no split). Use for length 2-4.')
    args = parser.parse_args()

    n = args.length
    in_dir = os.path.join(args.buckets, str(n))
    out_dir = os.path.join(args.prioritized, str(n))
    os.makedirs(out_dir, exist_ok=True)

    single = []  # (pattern, word, freq)
    multi = []   # pattern (with 2+ survivors)

    for src in sorted(glob.glob(os.path.join(in_dir, '*.txt'))):
        pattern = os.path.splitext(os.path.basename(src))[0]
        survivors = []
        for line in open(src):
            line = line.rstrip()
            if not line:
                continue
            word, freq = line.split('\t')
            if int(freq) >= args.floor:
                survivors.append((word, int(freq)))
        survivors.sort(key=lambda x: -x[1])

        # Write filtered file to prioritized
        with open(os.path.join(out_dir, f'{pattern}.txt'), 'w') as out:
            for word, freq in survivors:
                out.write(f'{word}\t{freq}\n')

        if len(survivors) == 1:
            single.append((pattern, survivors[0][0], survivors[0][1]))
        elif len(survivors) >= 2:
            multi.append(pattern)

    # Chunks
    chunk_root = os.path.join(args.chunks, str(n))

    if args.no_split or not single:
        # All goes to curate. Combine single and multi.
        all_patterns = sorted([p for p, _, _ in single] + multi)
        if all_patterns:
            num = math.ceil(len(all_patterns) / args.curate_per_chunk)
            curate_dir = os.path.join(chunk_root, 'curate')
            os.makedirs(curate_dir, exist_ok=True)
            for i in range(num):
                with open(os.path.join(curate_dir, f'{i:03d}.txt'), 'w') as out:
                    for p in all_patterns[i::num]:
                        out.write(p + '\n')
            print(f'length {n}: {len(all_patterns)} patterns -> {num} curate chunks')
    else:
        # Yes/no for singles, curate for multi
        if single:
            num = math.ceil(len(single) / args.yesno_per_chunk)
            yesno_dir = os.path.join(chunk_root, 'yesno')
            os.makedirs(yesno_dir, exist_ok=True)
            for i in range(num):
                with open(os.path.join(yesno_dir, f'{i:03d}.txt'), 'w') as out:
                    for p, w, f in single[i::num]:
                        out.write(f'{p}\t{w}\t{f}\n')
            print(f'length {n}: {len(single)} single-candidate patterns -> {num} yesno chunks')

        if multi:
            num = math.ceil(len(multi) / args.curate_per_chunk)
            curate_dir = os.path.join(chunk_root, 'curate')
            os.makedirs(curate_dir, exist_ok=True)
            for i in range(num):
                with open(os.path.join(curate_dir, f'{i:03d}.txt'), 'w') as out:
                    for p in multi[i::num]:
                        out.write(p + '\n')
            print(f'length {n}: {len(multi)} multi-candidate patterns -> {num} curate chunks')


if __name__ == '__main__':
    main()
