# Notes on building this

## Curating the word list

The encoder needs a map from digit-patterns (consonant strings, length 2 or more) to a small list of memorable words. Building that map turned out to be most of the project.

### Starting point

Google's `unigram_freq.csv` — about 330K unigrams from web corpus, ranked by frequency. The raw list is full of OCR junk (`gooook`, `oogko`), brand spam, obscure surnames, foreign words, web concatenations (`polarlake`), and clinical terms (`cysteinyl`). At a glance maybe 20% are real, recognisable English.

### Bucketing

First pass: split every word into a bucket by its full consonant pattern. So `lab` → bucket `18`, `museum` → bucket `353`, etc. Bucket sizes drop fast with length:

| pattern length | populated buckets | avg words/bucket |
|---:|---:|---:|
| 2  | 100    | 278 |
| 3  | 1,000  | 70  |
| 4  | 9,069  | 8.6 |
| 5  | 29,408 | 2.2 |
| 6  | 33,846 | 1.3 |

For length 2 every possible pattern (00–99) is populated; for length 3 same (all of 000–999). Higher lengths get patchy fast.

### Curation by parallel LLM agents

Manually reviewing 300K+ entries isn't tractable. But neither is a single heuristic — a good filter needs to recognise that "Massachusetts" is a fine mnemonic and "magentis" (a Kia model) is not. So: hand the buckets to LLM subagents in parallel, ~100 at a time, each with selection rules.

Rules: keep concrete, visualisable words and broadly-known proper nouns (`Libya`, `Tarzan`, `IMDB`). Reject obscure surnames, foreign-language words, OCR junk, niche acronyms, clinical jargon. Phrases are fine if they're vivid ("leg up", "lob a pencil").

- **Length 2 (100 buckets):** 20 agents × 5 buckets each. Each agent looked at the top 30 entries per bucket and returned the best 4–10. Result: 805 curated picks.
- **Length 3 (1,000 buckets):** 100 agents × 10 buckets. 5,817 picks. Fourteen buckets came back empty (e.g. `009`, `189`, `308` — combinations with no real English words). Hand-rescued these with abbreviations and phrases: `add up` for 009, `LBJ` for 189, `IMDB` for 308, `no soup` for 259, `pad up` for 909, `tied up` for 709.
- **Length 4 (9,069 buckets):** 100 agents × ~91 buckets. Hit the API rate limit ~60% of the way through, finished the rest in two follow-up batches. 14,782 picks. Most length-4 buckets have only 1–10 candidates, so the agent's job became "is this one real word?" rather than "top 10 of 30."
- **Length 5–6:** the long tail. Applied a frequency floor first (≥ 40K) to drop the OCR/junk noise that infests low-frequency entries — sampling showed that band is 100% garbage. After the floor, split each bucket: single-candidate patterns went to dedicated yes/no agents (one read + one write, very fast); multi-candidate patterns went to normal curate agents. ~50 agents per length. Resulted in 15K picks at L5 and 12K at L6.
- **Length 7+:** dropped entirely. Coverage of all possible N-digit numbers at L7 is 0.1% — these patterns essentially never match a random number, so they're dead storage. The chunking algorithm uses L2/L3 (both 100% covered) as a fallback for anything longer.

### Final shape

The shipped index is `assets/word_index.json` — 795 KB, 28,827 patterns, ~49,000 words. Each pattern maps to an ordered list of words, ranked by mnemonic quality (not by frequency — the agents chose ordering). The UI shows the top 5 per chunk.

Coverage by length, after all curation:

| length | covered patterns | % of all N-digit numbers |
|---:|---:|---:|
| 2 | 100 / 100 | 100% |
| 3 | 1,000 / 1,000 | 100% |
| 4 | 5,934 / 10,000 | 59.3% |
| 5 | 10,835 / 100,000 | 10.8% |
| 6 | 10,958 / 1M | 1.10% |

L2 and L3 being fully covered means the chunking algorithm can always find an encoding — longer chunks just shorten the result.

---

## On the name

I thought I'd invented this scheme. It turns out the basic idea — mapping digits to consonants and using the resulting words as memory hooks — has been around for nearly 400 years. The earliest published version is Stanislaus Mink von Wennsshein in 1648, refined by Aimé Paris in the early 1800s and named the **Major System** after Major Beniowski, a Polish émigré in 1840s England who wrote a popular book on it. Bruno Furst, Tony Buzan, and Harry Lorayne all popularised it in the 20th century.

So: independently rediscovered, with a 400-year track record of working. Reasonable consolation.

But the version I built isn't the standard one. The standard Major System is **phonetic** — digits map to sound families:

| Digit | Standard (sound) | Mine (shape) |
|---|---|---|
| 0 | /s/, /z/ | D, Q, X |
| 1 | /t/, /d/ | L, V |
| 2 | /n/ | N, Z |
| 3 | /m/ | M, W |
| 4 | /r/ | R, K |
| 5 | /l/ | S |
| 6 | /ʃ/, /tʃ/, /dʒ/ | C, F, G |
| 7 | /k/, /g/ | T |
| 8 | /f/, /v/ | B, H |
| 9 | /p/, /b/ | J, P |

The standard system was designed so the digit and its sound have a phonetic association (3 = m because cursive m has three humps, 4 = r because of "fou**r**," etc.). It's sound-based: silent letters don't count (silent k in *knight*), doubled consonants count once (*Mississippi* = M-S-S-P = 4 digits, not 7), H/W/Y are skipped as semi-vowels.

Mine is **shape-based**: each letter maps to the digit it resembles when rotated or written.

- 3 = M, W (M rotated 90° is a 3; W is M flipped — both have three peaks)
- 2 = N, Z (N on its side is 2; Z literally traces a 2)
- 8 = B, H (B has two stacked loops like 8; H is the two verticals of 8)
- 9 = P, J (P is 9 upright; J is 9 flipped)
- 5 = S (mirrored 5)
- 7 = T (a tilted 7)
- 0 = D, Q, X (closed/round shapes)
- 4 = R, K (vertical + branches like 4)
- 6 = C, F, G (curves with hooks; lowercase g = 6)
- 1 = L, V (single-stroke shapes)

## Why the shape-based version is more efficient

Two reasons it packs more digits per word than the standard:

**1. H and W carry digits.** In the standard system H, W, Y are silent / semi-vowels and never contribute to the encoding. In mine, H = 8 and W = 3 — both useful. So words like "wash" (W-S-H = 358), "what" (W-T = 37), "Hawaii" (H-W = 83), "BMW" (B-M-W = 833), "highway" (H-G-H-W = 8683) all encode digits that the standard system would either skip entirely or compress.

**2. Doubled letters count twice.** *Mississippi* in the standard system is M-S-S-P = 3559 (4 digits, because the double-s and double-p each count as one /s/ and one /p/ sound). In mine it's M-S-S-S-S-P-P = 3555599 (7 digits) — almost twice as much information from the same word.

Information-theoretically, each digit carries log₂(10) ≈ 3.32 bits. The standard system extracts roughly 65–70% of letters as digits (silent letters and H/W/Y are lost); mine extracts ~77% (only vowels + Y skipped) and doubles count. In typical English text that's about **30–40% more digits per word**, or equivalently, about a third fewer words needed to encode the same number.

For long numbers (phone numbers, dates, license plates, account numbers) that's the difference between a 3-word and a 4-word phrase to remember — and the shorter one wins basically every time, because the cognitive cost of mnemonic recall scales with the number of distinct elements, not the digit count.

## Trade-offs

The standard system has one genuine advantage: it's **spelling-invariant**. *Cell* and *sell* encode the same (05) because they sound the same; *night* and *knight* both encode 27. Mine treats those as different (`cell`=61, `sell`=51; `night`=287, `knight`=4287). So the standard system has tighter equivalence classes — fewer distinct "words" available per digit pattern, but each pattern's set is more semantically/sonically coherent.

Mine in exchange:
- Works directly on the written letters, no pronunciation rules needed
- Handles proper nouns, foreign loanwords, codes, and license plates without ambiguity
- No exceptions to memorise (no silent-letter rules, no soft-c-vs-hard-c, no double-consonant collapse)
- More bits per word, fewer words per number

The decision tree for a learner: if you think in sounds, the standard is more natural; if you think in letters (which most people who can read English do, more than they think they do), the shape-based version is significantly easier to internalise and use.

## What changes when encoding is cheap

"More efficient" above is about bits-per-word, not about being easier to memorise — those are separate axes. The more interesting framing is what happens to the *workflow* when encoding becomes free.

Pre-computer, finding a word for a digit string was hand-work. The realistic workflow was: memorise a fixed peg table of ~100 words (one per two-digit number — e.g. 31 = "mat", 41 = "rat", 59 = "lip", 26 = "nash") and compose any long number out of those. Pi to 8 digits — 31415926 — becomes four separate peg words: *mat-rat-lip-nash*. Four images, easy enough to picture, but disjointed: no narrative connecting them.

With cheap encoding, you don't need a peg table. You can search a curated set of 49K words and phrases for whatever segmentation produces the most natural result. Pi 31415926 becomes:

- **"malarial sponge"** — M-L-R-L (3141) + S-P-N-G (5926). Two words, weirdly evocative, sticks immediately.
- **"movie release panic"** — M-V (31) + R-L-S (415) + P-N-C (926). Three common words that form an actual mental scene.

You'd basically never get to "movie release panic" by hand. Finding it requires scanning candidate words at every digit boundary, holding several partial phrases in mind, and picking the combination that reads naturally. That's the kind of search humans are bad at and computers do trivially.

The asymmetry is the key insight: memorisation cost lives entirely in **decoding** — you still have to picture the word and read its consonants. That cost is the same in any of these schemes. Encoding cost — finding the right word in the first place — used to dominate, and that's gone. So the right kind of mnemonic system to design today isn't one that's easy to compose by hand; it's one that's easy to **decode**, regardless of how much compute went into encoding.

Two practical consequences:

- A larger curated vocabulary is now strictly better. Every additional real, visualisable word gives the encoder more flexibility to find a natural phrase. A 49K-word list is dramatically richer than the ~100-word peg table the old practitioners worked from.
- Letter-based mappings (like this one) are easier than sound-based ones, because the computer doesn't have to guess pronunciation. Spelling-invariance — the standard system's main advantage — only matters if you're hand-composing, and you're not.

Put differently: a peg-table system is optimised for a regime where you compose mentally and decode mentally. A computer-assisted system is optimised for a regime where you compose once with a search, and decode mentally forever after. The asymmetry favours throwing compute at the encoding side and letting the human side be as simple as possible.

It probably needs its own name to distinguish from the canonical phonetic version. "Shape Major" maybe. Or just claim it as a separate system entirely.
