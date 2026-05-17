# Major System mnemonic word curation

Curate word lists for a Major System mnemonic web app. The Major System maps digits to consonants so any number can be encoded as a memorable word. Mapping (vowels ignored):

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

## Task per bucket

The orchestrator gives you a list of bucket patterns (e.g. `035`, `127`). For each pattern XXX:

1. Read `/Users/douwe/Dropbox/Douwe/Proj/memory_app/buckets/3/XXX.txt`. Format: `word<TAB>frequency`, sorted by frequency descending.
2. From the **top 30 lines** (or all lines if fewer), pick the **4–10 best** Major System mnemonic words.
3. Write picks to `/Users/douwe/Dropbox/Douwe/Proj/memory_app/prioritized/3/XXX.txt` in the same `word<TAB>frequency` format. Rank best-first by mnemonic quality (not frequency). Capitalize proper nouns (e.g. `Lincoln`, `Tarzan`, `Hawaii`).

## Selection rules

**KEEP** (priority order):
1. **Visualizable / concrete** — easy to picture as a thing, place, person, or animal. `lab` (chemistry lab), `aloha` (Hawaii), `Tarzan` (jungle scene). Short sentence mnemonics also work ("lob a pencil"), so don't be overly strict — but reject if the word evokes no clear image.
2. **Real English or broadly-known names** — common words, plus proper nouns recognized across generations: `Lincoln`, `Italy`, `Hawaii`, `Romeo`, `Tarzan`, `Saturn`.
3. **Unambiguous spelling** — the encoding's main consonants should be the obvious ones in the word.

**REJECT**:
- Acronyms / initialisms (`vba`, `lbo`, `cdc`, `atx`, `nih`, `tdd`)
- Foreign-language words a typical English speaker won't know (`liebe`, `tiava`, `nuevo`, `auch`)
- OCR junk, made-up brands, web concatenations (`gokgl`, `oogook`, `mscorlib`)
- Niche pop-culture names / surnames known to only one community or generation (`Aaliyah`, `Leahy`, `Loeb`, `Naboo`)
- Awkward clinical/anatomical terms

## Output rules

- 4–10 picks per bucket. Fewer is fine if the bucket is genuinely thin; **don't pad with weak picks**.
- Preserve the original frequency from the source file.
- Capitalize proper nouns even though they're lowercase in the source.
- Use Read and Write tools. No commentary or progress messages.
