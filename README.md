# Major System

A shape-based mnemonic system for memorising numbers. Each digit maps to a set
of consonants chosen for visual similarity (3 = M because M rotated 90° is a
3, 8 = B because B has two stacked loops like 8, etc.). Type a number, get a
phrase; type a word, see what number it encodes.

This differs from the canonical phonetic Major System (~1648) — see
`thoughts.md` for the history, design rationale, and trade-offs.

## [Live demo](https://douwe.com/projects/major_system)

## Mapping

| Digit | Letters | Why |
|---|---|---|
| 0 | D, Q, X | closed/round shapes |
| 1 | L, V | single-stroke verticals |
| 2 | N, Z | N on its side ≈ 2; Z literally traces a 2 |
| 3 | M, W | both have 3 peaks; M rotated = 3 |
| 4 | R, K | vertical + branches like a 4 |
| 5 | S | S = mirrored 5 |
| 6 | C, F, G | curves with hooks; lowercase g = 6 |
| 7 | T | tilted 7 |
| 8 | B, H | B has two stacked loops like 8; H = the two verticals |
| 9 | J, P | P = 9 upright; J = 9 flipped |

Vowels and Y are skipped. Doubled consonants both count (`Mississippi` =
3555599, not 3559).

## Files

- `major_system.html` — the live page (input + JS that loads the index and
  searches for segmentations)
- `static/word_index.json` — 795 KB index: `{pattern: [word, word, ...]}` for
  28,827 patterns covering lengths 2–6
- `thoughts.md` — design notes / blog draft on the curation process and
  asymmetry of encode vs decode cost
- `build_buckets.py` — partition the raw n-gram CSV into one file per
  consonant pattern
- `prepare_curation.py` — apply a frequency floor and split patterns into
  chunks for parallel agent dispatch
- `apply_drops.py` — apply the drop lists produced by the yes/no agents
- `build_index.py` — combine the curated buckets into `word_index.json`
- `prompts/` — the agent curation prompts, one per length

## How to reproduce the index

Start with a unigram frequency CSV (`word,count`). The original used was
Google's 333k-word [unigram_freq.csv](https://www.kaggle.com/datasets/rtatman/english-word-frequency).

```bash
# 1. Bucket every word by its consonant pattern.
#    Writes buckets/<N>/<pattern>.txt for N in 2..14.
python build_buckets.py path/to/unigram_freq.csv

# 2. Length-by-length curation.
#    For length 2 and 3, the index is small enough that every populated bucket
#    deserves a full agent pass — no frequency floor.
python prepare_curation.py --length 2 --no-split
python prepare_curation.py --length 3 --no-split
# (run agents over chunks/2/curate/*.txt and chunks/3/curate/*.txt
#  using prompts/curate_l3.md — agents write back to prioritized/2/ and 3/)

# Length 4: same shape, but buckets are sparser. No floor needed.
python prepare_curation.py --length 4 --no-split --curate-per-chunk 91
# (run agents over chunks/4/curate/*.txt using prompts/curate_l4.md)

# Length 5 and 6: frequency floor + yes/no vs curate split. Most buckets at
# this length have a single candidate, so the yes/no agents (decide
# keep-or-drop in bulk) handle them fast.
python prepare_curation.py --length 5 --floor 40000
python prepare_curation.py --length 6 --floor 40000
# (run agents over chunks/5/yesno/*.txt and chunks/5/curate/*.txt — and same
#  for 6 — using prompts/yesno_l{5,6}.md and prompts/curate_l{5,6}.md.
#  yesno agents emit drops/<N>/<NNN>.txt; curate agents write directly to
#  prioritized/<N>/.)

# 3. Apply the yes/no drops for length 5 and 6.
python apply_drops.py --drops drops/5 --prioritized prioritized/5
python apply_drops.py --drops drops/6 --prioritized prioritized/6

# 4. Build the final index.
python build_index.py --out static/word_index.json
```

Length 7+ is intentionally dropped — coverage at L7 is 0.10% of all 7-digit
numbers, essentially never matches anything, and `build_index.py`'s
`--max-length 6` default reflects that.

## How the agent curation works

The curation can't be fully automated by a heuristic — a good filter needs to
recognise that "Massachusetts" is a fine mnemonic and "magentis" (a Kia
model) is not. So each chunk is handed to an LLM subagent with the rules from
the corresponding `prompts/*.md` file. The agents read bucket files, apply
the rules, and write the kept words back. Roughly 1–2 hours of compute time
(in parallel) to do the whole pipeline.

The split between `yesno` and `curate` styles matters for efficiency:

- **`yesno`** agents get a chunk of ~475 single-candidate buckets in one
  prompt. They scan the list and emit only the patterns to drop. One read +
  one write per agent regardless of chunk size — very fast.
- **`curate`** agents get ~170 multi-candidate buckets. They read each file,
  pick the best 0–5 candidates, and write the result back. More tool calls
  per agent, but produces ranked picks.

For lengths 2–4 every bucket has multiple candidates, so the yes/no style
doesn't apply — pass `--no-split` to `prepare_curation.py`.

## Coverage

| pattern length | covered patterns | % of all N-digit numbers |
|---:|---:|---:|
| 2 | 100 / 100 | 100% |
| 3 | 1,000 / 1,000 | 100% |
| 4 | 5,934 / 10,000 | 59.3% |
| 5 | 10,835 / 100,000 | 10.8% |
| 6 | 10,958 / 1,000,000 | 1.10% |

L2 and L3 being fully covered means the chunking algorithm can always find an
encoding — longer chunks just shorten the result.
