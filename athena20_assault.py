#!/usr/bin/env python3
"""ATHENA 20 — THE GRAND ASSAULT.
Every solver x every alphabet x every language, against the real
manuscript and against its own shuffled shadow. The matrix is the
message: if any cell beats its control by a decisive margin, that
cell is a lead worth freezing a key over. If none does, the
substitution family has faced the full arsenal and the arsenal
itself files the negative."""
import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import athena20 as A
import athena20_breaker as B

def streams(words, merges):
    return {
        "eva_units": [u for w in words for u in A.eva_segment(w)],
        "raw_chars": [c for w in words for c in w],
        "induced": [s for w in words for s in A.apply_merges_word(w, merges)],
    }

def main():
    loci = A.load_loci(A.DIRS["data"] / "ZL3b-n.txt")
    words = [w.lower() for w in A.words_of(loci)]
    chars = A.char_stream(loci)
    merges = A.induce_alphabet(chars, max_merges=40)["merges"]
    sts = streams(words, merges)
    gates = B.gates()
    out = {"gates": gates, "cells": []}
    if not gates.get("all_pass"):
        out["status"] = "SOLVERS_NOT_VALIDATED — assault withheld"
        (A.DIRS["results"] / "grand_assault.json").write_text(json.dumps(out, indent=1))
        print("gates failed; assault withheld"); return
    eng_lm = None
    for alpha_name, stream in sts.items():
        ids = {s: i for i, s in enumerate(sorted(set(stream)))}
        cipher = [ids[s] for s in stream][:8000]
        rng = random.Random(8)
        shuf = cipher[:]; rng.shuffle(shuf)
        solvers = [("substitution", B.solve_substitution)]
        if alpha_name != "raw_chars": solvers.append(("homophonic", B.solve_homophonic))
        for lang in ("latin", "hebrew", "egyptian"):
            lm = B.get_lm(lang)
            for sname, solver in solvers:
                _, sc = solver(cipher, lm, iters=3000, restarts=2)
                _, sc_c = solver(shuf, lm, iters=3000, restarts=2)
                margin = round(sc - sc_c, 4)
                out["cells"].append({"alphabet": alpha_name, "solver": sname, "language": lang,
                                     "score": round(sc, 4), "control": round(sc_c, 4), "margin": margin,
                                     "lead": margin > 0.15})
                print(alpha_name, sname, lang, margin, flush=True)
    leads = [c for c in out["cells"] if c["lead"]]
    out["leads"] = leads
    out["verdict"] = ("LEAD CELLS: %d — freeze keys and run the claim protocol" % len(leads)) if leads else \
                      "no cell beats its shuffled control decisively: the substitution arsenal finds no purchase"
    p = A.DIRS["results"] / "grand_assault.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print("wrote", p)

if __name__ == "__main__":
    main()
