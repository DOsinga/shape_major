# Major System mnemonic word curation — length 6 multi-candidate buckets

Curate length-6 word lists for a Major System mnemonic web app. Mapping (vowels ignored):

| Digit | Consonants |
|---|---|
| 0 | D, Q, X |
| 1 | L, V |
| 2 | N, Z |
| 3 | M, W |
| 4 | R, K |
| 5 | S |
| 6 | C, F, G |
| 7 | T |
| 8 | B, H |
| 9 | J, P |

## Task

The orchestrator gives you a chunk file like `/tmp/l6_curate/NNN.txt` containing ~170 six-digit pattern names, one per line.

For each pattern XXXXXX in your chunk file:

1. Read `/Users/douwe/Dropbox/Douwe/Proj/memory_app/prioritized/6/XXXXXX.txt`. Format: `word<TAB>frequency`. **The file already has 2+ candidates pre-filtered to freq ≥ 40K.**
2. Pick the **0–5 best** Major System mnemonic words from those candidates.
3. Write picks back to the same file in `word<TAB>frequency` format. Rank best-first by mnemonic quality. Capitalize proper nouns.
4. **If none qualify, write an empty file.** Don't pad with weak picks.

## Selection rules

**KEEP** (priority order):
1. **Visualizable / concrete** — real things, places, people, animals: `museum`, `Lincoln`, `Romeo`, `dolphin`, `Massachusetts`, `Cincinnati`. Short-sentence mnemonics also fine.
2. **Real English or broadly-known names** — common words, plus widely-recognized proper nouns.
3. **Unambiguous spelling**.

Well-known abbreviations are OK (`LBJ`, `IMDB`, `NATO`) if broadly recognized.

**REJECT**:
- Obscure acronyms/initialisms (`mscorlib`, `usbhid`)
- Foreign-language words a typical English speaker won't know
- OCR junk, made-up brands, web concatenations
- Niche pop-culture or surnames known only to one community
- Awkward clinical/anatomical terms
- Typos / misspellings

## Output rules

- 0–5 picks per bucket. Don't pad with weak picks.
- Preserve the original frequency from the source file.
- Use Read and Write tools. No commentary.
- Process **all** patterns listed in your chunk file. Do not stop early.
