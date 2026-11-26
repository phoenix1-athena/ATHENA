# ATHENA — findings summary (verified results only, 2026-11-25)

All results below were produced on the full ZL3b-n transcription and,
where stated, replicated on the independent Takahashi IT2a-n witness.
Negative results are reported with the same prominence as positive ones.

## Deductive exclusions (constraint logic, not statistics)

- **Egyptian, Hebrew, and Latin are all INCONSISTENT as simple
  substitution** at EVA-unit level — proven twice, on the EVA alphabet
  and on an independently induced alphabet. Egyptian fails at pattern
  level (the doubled-unit patterns of qokeey/qokeedy/qokaiin have no
  skeleton in the 42,166-form lexicon at all); Hebrew fails at global
  level (every candidate key for qokaiin starves the doubled-glyph word
  family); Latin likewise.
- **All three are also INCONSISTENT under homophonic substitution**
  (Logic Core II, soundness-gated: planted cipher CONSISTENT, true key
  verified, corrupted instance INCONSISTENT). The substitution family is
  therefore excluded wholesale for these three languages.
- The Egyptian hypothesis had already failed statistically at full scale
  in an earlier edition (skeleton-test coverage 0.2655 token / 0.0365
  type, bigram log-likelihood −6.2237, not beating all random-remap
  controls — grade D by its own pre-registered rule).
- **Crib attack:** the 25 most-repeated label word-types are inconsistent
  with zodiac + month-name cribs in Latin, German, Italian, French, and
  Hebrew transliteration, under simple and homophonic substitution.

## The generator programme (what kind of process made this text?)

A battery of seven metrics (glyph entropy h0/h1, type-token ratio, hapax
share, word-trigram repetition, edit-distance-1 neighbour density,
word-length distribution) scores synthetic texts against the real book.
Six generator generations were built and measured on one code path:

- Machine/grammar/human-error copier models: distance 2.07 / 1.61 / 2.03.
  All fail the same way — they cluster repetition locally; the real
  text's repetition is spread out.
- **"The Table"** (global frequency-weighted pool + local copy/modify
  seasoning + recombination coinage): **0.604**, type-token ratio
  essentially exact.
- Current best, **v7** (Table + finite-stock phrases at low dose):
  **0.513**, against a pre-registered pass bar of 0.40 that remains
  unmet. The standing obstacle is the **hapax wall**: the real book coins
  far more one-off words than any contender (gap −0.19 vs limit 0.08).

## Residual atlas (where the book defies its best imitation)

Per-folio z-scores against generator windows: the hardest metric to fake
is edit-distance-1 neighbour density (mean z +4.39). The most
generator-defying folios are **f57v, f80r, f76r, f77r, f84r**. f76r was
independently flagged as the book's largest repetition "sink" (54.7%)
by an unrelated scan in an earlier edition.

## Structure that survives every control

- Word boundaries are real (within-word entropy 4.081 with spaces vs
  4.394 deleted, 4.103 arbitrary 5-chunks — a real but slim margin).
- Alphabet induction from raw characters recovers EVA's ch/sh/in/iin
  units unprompted, then goes beyond EVA (qo, aiin, dy, qok, edy).
- Adjacent doubled glyphs run at 0.54× chance overall — yet 92% of all
  doubling is the single unit **e** (4,504 of 4,883).
- The book falls into thirds with distinct statistics ("parties of
  three"); word-trigram repetition runs ~10× the shuffled control.
- Core statistics (h0, h1, TTR, trigram repetition) hold in BOTH
  transcription witnesses; top-10 word overlap 8/10. The anomalies are
  in the book, not in one transcriber.
- Labels behave like names, not prose: 46.8% of label word-types never
  appear in body text.
- Clean negatives: Fibonacci reading orders and word lengths, a 3-axis
  word lattice, GCD/arithmetic modules in the counts, binary byte-text
  encodings, lunar/tidal/celestial cycles, Vigenère periods.

## Solver proof battery (blind, known-answer)

10 of 14 tests passed at the registered bars. Substitution: 100%
plaintext recovery on Latin and English at 800 and 2,500 letters.
Vigenère: period found, 100% key recovery, both languages. Both logic
gates pass. Transposition initially failed (wrong permutation family);
the corrected solver was afterwards verified standalone at **100%
accuracy**. Homophonic stream-solving provably cannot identify the true
key from letter statistics alone (found key −3.9078 vs true key −3.8733
— a statistical tie); a word-aware homophonic solver that scores
decrypted words against the attested vocabulary has been built in
response and is under gate validation at time of release.

## A visual observation

Folio **f71r** (Aries) is built **1 – 5 – 10**: one animal at the centre,
five star-bearing figures in the inner ring, ten in the outer ring
(15 figures, counted and machine-verified 2026-11-25). Whether the
zodiac section's figure counts encode a calendar structure is an open
question the releaser flags for others.

## What ATHENA does not claim

No translation. No decipherment. No language identification. Every
positive-sounding historical hypothesis tested so far has been excluded
or graded D. What remains standing is a set of hard structural facts
about how the text behaves — and a generator that imitates it better
than any published baseline known to the releaser, without yet passing.
