# Major System mnemonic word curation — length 4

Curate length-4 word lists for a Major System mnemonic web app. Mapping (vowels ignored):

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

The orchestrator gives you a chunk file like `/tmp/l4_chunks/NNN.txt` containing ~90 four-digit pattern names, one per line.

For each pattern XXXX in your chunk file:

1. Read `/Users/douwe/Dropbox/Douwe/Proj/memory_app/buckets/4/XXXX.txt`. Format: `word<TAB>frequency`, sorted by frequency descending. **Note:** most length-4 buckets are small (1–10 words). A few have up to ~50.
2. From **all** lines (or top 30 if there are more), pick **0–5 best** Major System mnemonic words.
3. Write picks to `/Users/douwe/Dropbox/Douwe/Proj/memory_app/prioritized/4/XXXX.txt` in `word<TAB>frequency` format. Rank best-first by mnemonic quality. Capitalize proper nouns.
4. **If no candidates qualify, write an empty file.** Don't pad with weak picks.

## Selection rules

**KEEP** (priority order):
1. **Visualizable / concrete** — real things, places, people, animals: `museum`, `Lincoln`, `Romeo`, `Tarzan`, `Hawaii`, `dolphin`. Short-sentence mnemonics also fine ("lob a pencil", "leg up").
2. **Real English or broadly-known names** — common words, plus widely-recognized proper nouns.
3. **Unambiguous spelling**.

Well-known abbreviations are OK (`LBJ`, `IMDB`, `TBD`, `NATO`, `IKEA`, `NASA`) if they're broadly recognized.

**REJECT**:
- Obscure acronyms/initialisms (`mscorlib`, `usbhid`, `vmware-tools`)
- Foreign-language words a typical English speaker won't know
- OCR junk, made-up brands, web concatenations
- Niche pop-culture / surnames known only to one community
- Awkward clinical/anatomical terms

## Output rules

- 0–5 picks per bucket. Length-4 buckets are often tiny; if nothing meets the bar, write an empty file.
- Preserve the original frequency from the source file.
- Use Read and Write tools. No commentary or progress messages.
- Process **all** patterns listed in your chunk file. Do not stop early.
