# ATHENA — a Voynich manuscript research workbench

**Anonymous release, 2026-11-25. Authors: Phoenix 1, Chris Marlin, and James Carpenter.** Published under the name Phoenix 1; no affiliation.
The work is offered as-is for verification and reuse.

ATHENA is a dependency-free Python (stdlib-only) workbench for the
statistical, logical, and generative analysis of the Voynich manuscript
(Beinecke MS 408), built around one discipline:

> **No decipherment claim is made without a frozen key, a blind held-out
> prediction beating hoax/shuffled controls, replication on a second
> transcription witness, and an A–D evidence grade.**

Solvers must pass known-answer gates on planted ciphers before any
manuscript output is trusted; a solver that fails its gate has its
manuscript proposals withheld by design.

## What's in this package

- `athena20.py` — the main program: tabula-rasa core (alphabet induction,
  boundary trial, statistics battery), a deductive constraint-logic core
  (simple substitution), Logic Core II (homophonic substitution),
  a generator gauntlet, and a per-folio residual atlas.
- `athena20_zoo.py` — the cipher zoo: Vigenère lab, transposition profile,
  Playfair signature, acrostic, Bifid/Polybius pair-IC, autokey lag probe,
  codebook word-profile, reverse stream, and Logic III (syllabic/verbose
  substitution under deductive test).
- `athena20_breaker.py` — tetragram-LM annealing solvers (substitution,
  homophonic stream + word-aware, transposition) with known-answer gates.
- `athena20_proof.py` — the blind proof battery: real Latin/English/Hebrew
  texts encrypted under every claimed cipher class, attacked blind, scored
  against the known plaintexts.
- `athena20_assault.py` — the grand assault harness (every validated solver
  × every alphabet × every language, manuscript vs shuffled control).
- `data/` — both transcription witnesses: ZL3b-n (Zandbergen–Landini,
  IVTFF 2.0) and IT2a-n (Takahashi). SHA-256 verified against public
  mirrors.
- `corpora/` — Egyptian (Pyramid Texts CoNLL-U + 42,166-form MdC lexicon),
  Hebrew (Westminster Leningrad Codex, 55,643 consonantal types after
  nikud stripping), Latin (Caesar), Greek (Homer, Iliad — Perseus TEI, 111,898 words; added 2026-11-26), Italian (Dante, Divina Commedia: Inferno, 34,321 words; added 2026-11-26).
- `results/` — machine-readable result files for the runs summarised in
  `FINDINGS_SUMMARY.md`.

Run: `python3 athena20.py --self-test` then
`python3 athena20.py --input data/ZL3b-n.txt`

## Status — 2026-11-26

- **Greek and Italian join the panel.** The two corpora above close a gap noted in the original release; the deductive logic panel now tests five languages against the manuscript.
- **All-languages sweep (2026-11-26):** Greek and Italian faced the deductive panel on both witnesses — INCONSISTENT under simple and homophonic substitution, like Hebrew, Egyptian and Latin before them. The substitution family is now excluded for five languages.
- **ATHENA: Voynich Breaker** — a tap-only cipher game built from real Voynich word-types — was built on 2026-11-26; store releases in progress.
- **Phoenix 1, Inc.**, a Tennessee C-corporation, is being formed to carry the work.
- The ATHENA 20 master run (core + cipher zoo + breaker, both witnesses) is in progress; consolidated results will be posted here when verified.

## Licence

Code and findings: public domain (CC0) as far as the releaser can grant.
Underlying corpora and transcriptions belong to their respective projects
and are redistributed for research verification.
