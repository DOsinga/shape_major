"""Apply yes/no agent drop lists to prioritized/.

The yes/no curation agents write a list of patterns to drop per chunk (one
6-digit-or-shorter pattern per line). This script reads all those drop files
and empties the corresponding prioritized/<N>/<pattern>.txt files.
"""

import argparse
import glob
import os


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--drops', required=True, help='Directory of drop files (e.g. drops/5)')
    parser.add_argument('--prioritized', required=True,
                        help='Prioritized dir to empty entries in (e.g. prioritized/5)')
    args = parser.parse_args()

    to_drop = set()
    for f in sorted(glob.glob(os.path.join(args.drops, '*.txt'))):
        for line in open(f):
            pat = line.strip()
            if pat:
                to_drop.add(pat)

    dropped = 0
    missing = 0
    for pat in to_drop:
        path = os.path.join(args.prioritized, f'{pat}.txt')
        if os.path.exists(path):
            open(path, 'w').close()
            dropped += 1
        else:
            missing += 1

    print(f'emptied {dropped:,} files ({missing:,} not found, '
          f'{len(to_drop):,} unique drops requested)')


if __name__ == '__main__':
    main()
