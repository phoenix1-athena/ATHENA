#!/usr/bin/env python3
"""ATHENA 20 — THE PROOF.
Superlatives are cheap. This battery is the bill: real texts, encrypted
under every cipher class the program claims, attacked blind by the
program's own solvers, scored against the known plaintexts. Pass bars
registered here, in advance, before a single run:
  simple substitution : >=75% letters at 2500, >=55% at 800
  homophonic          : >=60% at 2500
  Vigenere            : period found + >=70% of key at 4000
  columnar transp.    : >=60% at 3600
  logic engines       : planted CONSISTENT, corrupted INCONSISTENT
Whatever fails, prints as failed."""
import json, random, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import athena20 as A
import athena20_breaker as B
import athena20_zoo as Z

def english_letters():
    txt = ""
    for f in (Path(__file__).parent / "docs").glob("*.md") if (Path(__file__).parent / "docs").exists() else []:
        txt += f.read_text(encoding="utf-8", errors="replace")
    if len(txt) < 20000:  # fall back to the ATHENA 9/10 findings on file
        for base in ("ATHENA9", "ATHENA10"):
            d = Path(__file__).parent.parent / base / "docs"
            if d.exists():
                for f in d.glob("*.md"): txt += f.read_text(encoding="utf-8", errors="replace")
    return [c for c in txt.lower() if "a" <= c <= "z"]

def acc(dec, truth):
    return round(sum(1 for a, b in zip(dec, truth) if a == b) / max(1, len(truth)), 3)

def main():
    card = {"pass_bars": {"substitution_2500": 0.75, "substitution_800": 0.55,
                          "homophonic_2500": 0.60, "vigenere_key": 0.70, "transposition_3600": 0.60},
            "tests": []}
    rng = random.Random(101)
    # ---- substitution + homophonic, Latin and English ----
    streams = {}
    lat = B.corpus_letters("latin"); streams["latin"] = lat
    eng = english_letters()
    if len(eng) > 20000: streams["english"] = eng
    for lang, letters in streams.items():
        lm = B.LM(letters) if lang == "english" else B.get_lm(lang)
        idx = [lm.ai[c] for c in letters]
        for n, bar in ((800, 0.55), (2500, 0.75)):
            truth = idx[:n]
            perm = list(range(len(lm.alpha))); rng.shuffle(perm)
            cipher = [perm[i] for i in truth]
            key, _ = B.solve_substitution(cipher, lm, iters=4500, restarts=3)
            a = acc([key[s] for s in cipher], truth)
            card["tests"].append({"test": "substitution", "lang": lang, "n": n,
                                  "accuracy": a, "bar": bar, "pass": a >= bar})
            print("sub", lang, n, a, flush=True)
        n = 2500; truth = idx[:n]
        pool = list(range(70)); rng.shuffle(pool)
        enc = {}
        for li_ in range(len(lm.alpha)): enc[li_] = [pool.pop() for _ in range(rng.choice([2, 2, 3]))]
        hc = [rng.choice(enc[i]) for i in truth]
        hkey, _ = B.solve_homophonic(hc, lm, iters=120000, restarts=3)
        a = acc([hkey[s] for s in hc], truth)
        card["tests"].append({"test": "homophonic", "lang": lang, "n": n,
                              "accuracy": a, "bar": 0.60, "pass": a >= 0.60})
        print("homo", lang, n, a, flush=True)
        # ---- Vigenere ----
        refs = {"latin": {}, "english": {}}
        uni = Counter(letters); tot = sum(uni.values())
        ref = {c: v / tot for c, v in uni.items()}
        for kw in ("ave", "secretum"):
            shifts = [lm.ai[c] for c in kw if c in lm.ai]
            if len(shifts) != len(kw): continue
            stream = idx[:4000]
            enc_idx = [(v + shifts[i % len(shifts)]) % len(lm.alpha) for i, v in enumerate(stream)]
            enc_s = [lm.alpha[v] for v in enc_idx]  # zoo solver works on letter strings
            scored = sorted(((sum(Z._ic(enc_idx[i::p]) for i in range(p)) / p, p) for p in range(1, 13)), reverse=True)
            per = scored[0][1]
            key = Z._vigenere_solve(enc_s, per, ref) if per == len(shifts) else []
            rec = (sum(1 for a, b in zip(key, shifts) if a == b) / len(shifts)) if key else 0.0
            card["tests"].append({"test": "vigenere", "lang": lang, "key": kw, "found_period": per,
                                  "key_recovery": round(rec, 3), "bar": 0.70, "pass": per == len(shifts) and rec >= 0.70})
            print("vig", lang, kw, per, rec, flush=True)
        # ---- columnar transposition ----
        stream = idx[:3600]; k = 6; rows = len(stream) // k
        cols = [[stream[r_ * k + c] for r_ in range(rows)] for c in range(k)]
        order_true = [2, 0, 4, 1, 5, 3]
        tc = []
        for c in order_true: tc.extend(cols[c])
        res = B.solve_transposition(tc, lm, kmax=8)
        a = acc(res[3], stream) if res else 0.0
        card["tests"].append({"test": "transposition", "lang": lang, "n": 3600, "k": k,
                              "accuracy": a, "bar": 0.60, "pass": a >= 0.60})
        print("transp", lang, a, flush=True)
    # ---- logic engines ----
    g1 = A.logic_gate(); g2 = A.logic2_gate()
    card["tests"].append({"test": "logic_simple_gate", "pass": bool(g1.get("gate_pass")), "detail": g1})
    card["tests"].append({"test": "logic_homophonic_soundness_gate", "pass": bool(g2.get("gate_pass")), "detail": g2})
    card["passed"] = sum(1 for t in card["tests"] if t["pass"])
    card["total"] = len(card["tests"])
    out = A.DIRS["results"] / "PROOF.json"
    out.write_text(json.dumps(card, ensure_ascii=False, indent=1))
    print("wrote", out, "| passed", card["passed"], "of", card["total"], flush=True)

if __name__ == "__main__":
    main()
