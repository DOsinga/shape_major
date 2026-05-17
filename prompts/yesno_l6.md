# Major System yes/no filter — length 6 single-candidate buckets

Each line of the chunk file you're given is a triple: `<pattern>\t<word>\t<frequency>`. The word is the *only* candidate in its length-6 bucket. Your job is to decide for each one: is the word a usable Major System mnemonic?

## Mapping (for context — vowels ignored)

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

## Decision rules

**KEEP** if the word is:
- A real English word (`associative`, `outlining`, `printout`, `depositary`)
- A broadly-known proper noun (`Massachusetts`, `Mississippi`, `Washington`, `Tennessee`, `Cincinnati`)
- A well-known abbreviation/initialism (`USDA`, `LBJ`, `IMDB`-style — but at length 6, these are rare)

**DROP** if the word is:
- A web concatenation, brand name, or OCR junk (`polarlake`, `magentis`, `liteortica`, `greefing`, `beasriality`)
- A foreign-language word a typical English speaker won't know
- An obscure surname or place name (`mallett`, `guterson`, `huminiecki`, `bocholt`)
- A technical/clinical term most people won't recognize (`cysteinyl`, `diffusive`)
- A typo or misspelling (`neverthe`, `tomorow`)

## Task

The orchestrator gives you a chunk file path like `/tmp/l6_yesno/NNN.txt`. Each line is `<pattern>\t<word>\t<frequency>`.

1. Read your chunk file.
2. For each line, decide KEEP or DROP using the rules above.
3. Write the list of patterns to DROP (one 6-digit pattern per line, nothing else) to `/tmp/l6_drops/NNN.txt` — same `NNN` as your input chunk.

If the input is `/tmp/l6_yesno/007.txt`, output to `/tmp/l6_drops/007.txt`.

Don't list KEEPs. Don't add commentary. Just the DROP list, one pattern per line. If no patterns should be dropped, write an empty file.
