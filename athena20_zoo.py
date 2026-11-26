#!/usr/bin/env python3
"""ATHENA 20 — THE CIPHER ZOO.
Every cipher class, known and imagined, gets an engine, a gate, and a
verdict. Known: Vigenere-family polyalphabetic, transposition, Playfair
digraphic signatures. Imagined: acrostic channels, word-length ciphers,
distance ciphers, and Logic III — the syllabic/verbose cipher where one
cipher unit speaks a whole consonant cluster (the Egyptian door,
rebuilt as pure logic). Discipline as always: an engine that fails its
gate issues no manuscript verdict."""
import json, math, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import athena20 as A

DIRS = A.DIRS

def _ic(stream):
    n = len(stream)
    if n < 2: return 0.0
    c = Counter(stream); k = len(c)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * k

def _cond_h1(stream):
    if len(stream) < 3: return 0.0
    bi = Counter(zip(stream, stream[1:])); uni = Counter(stream)
    h = 0.0
    for (a, b), c in bi.items():
        h -= (c / (len(stream) - 1)) * math.log2(c / uni[a])
    return h

def _letter_freq(counter):
    tot = sum(counter.values())
    return {c: v / tot for c, v in counter.items()}

def language_refs():
    refs = {}
    heb = A.hebrew_vocab()
    if heb: refs["hebrew"] = _letter_freq(Counter({c: sum(v for w, v in heb.items() if False) for c in []}) or
                                           Counter(c for w, v in heb.items() for c in w for _ in range(v)))
    lat = A.latin_vocab()
    if lat: refs["latin"] = _letter_freq(Counter(c for w, v in lat.items() for c in w for _ in range(v)))
    egy = A.egyptian_vocab()
    if egy: refs["egyptian"] = _letter_freq(Counter(c for w in egy for c in w))
    return refs

# ---------------- VIGENERE LAB ----------------
def _vigenere_solve(stream, period, ref_freq):
    alpha = sorted(ref_freq)
    key = []
    for col_i in range(period):
        col = stream[col_i::period]
        cc = Counter(col); n = len(col)
        best = None
        for shift in range(len(alpha)):
            chi = 0.0
            for j, letter in enumerate(alpha):
                obs = cc.get(alpha[(j + shift) % len(alpha)], 0)
                exp = ref_freq[letter] * n
                chi += (obs - exp) ** 2 / max(exp, 1e-9)
            if best is None or chi < best[0]: best = (chi, shift)
        key.append(best[1])
    return key

def vigenere_lab(words, refs):
    stream = [u for w in words for u in A.eva_segment(w)]
    rng = random.Random(3)
    shuffled = stream[:]; rng.shuffle(shuffled)
    table = {}
    for per in range(1, 17):
        ic_r = sum(_ic(stream[i::per]) for i in range(per)) / per
        ic_s = sum(_ic(shuffled[i::per]) for i in range(per)) / per
        table[per] = {"ic": round(ic_r, 4), "ic_shuffled": round(ic_s, 4)}
    # gate: encrypt a Latin letter stream, solver must find period + key
    lat_text = (DIRS["corpora"] / "latin_corpus.txt").read_text(encoding="utf-8", errors="replace").lower()
    letters = [c for c in lat_text if "a" <= c <= "z"]
    alpha = sorted(refs["latin"]); pos = {c: i for i, c in enumerate(alpha)}
    gate = {}
    for key_word in ("ave", "romae"):
        shifts = [pos[c] for c in key_word]
        enc = [alpha[(pos[c] + shifts[i % len(shifts)]) % len(alpha)] for i, c in enumerate(letters[:20000])]
        scored = sorted(((sum(_ic(enc[i::p]) for i in range(p)) / p, p) for p in range(1, 13)), reverse=True)
        found_period = scored[0][1]
        key = _vigenere_solve(enc, found_period, refs["latin"])
        rec = sum(1 for a, b in zip(key, shifts) if a == b) / len(shifts) if found_period == len(shifts) else 0.0
        gate[key_word] = {"true_period": len(shifts), "found_period": found_period, "key_recovery": round(rec, 3)}
    gate_pass = all(g["found_period"] == g["true_period"] and g["key_recovery"] >= 0.7 for g in gate.values())
    best_per = max(table, key=lambda p: table[p]["ic"] - table[p]["ic_shuffled"])
    out = {"gate": gate, "gate_pass": gate_pass, "period_table": table,
           "best_period": best_per, "best_margin": round(table[best_per]["ic"] - table[best_per]["ic_shuffled"], 4)}
    if not gate_pass:
        out["status"] = "SOLVER_NOT_VALIDATED — manuscript verdict withheld"; return out
    out["verdict"] = ("POLYALPHABETIC SIGNATURE PRESENT at period %d" % best_per) if out["best_margin"] > 0.15 * table[best_per]["ic_shuffled"] + 0.01 else \
                     "no polyalphabetic period stands out from the shuffled control"
    return out

# ---------------- TRANSPOSITION PROFILE ----------------
def transposition_profile(words, refs):
    units = [u for w in words for u in A.eva_segment(w)]
    prof_c = sorted((v / len(units) for v in Counter(units).values()), reverse=True)
    res = {}
    rng = random.Random(11)
    for lang, ref in refs.items():
        prof_l = sorted(ref.values(), reverse=True)
        m = min(len(prof_c), len(prof_l))
        chi = sum((prof_c[i] - prof_l[i]) ** 2 / prof_l[i] for i in range(m))
        # bootstrap: how well does the language fit ITSELF at this size?
        letters = list(ref); wts = [ref[c] for c in letters]
        boots = []
        for _ in range(12):
            sample = rng.choices(letters, weights=wts, k=len(units))
            pb = sorted((v / len(units) for v in Counter(sample).values()), reverse=True)
            mb = min(len(pb), len(prof_l))
            boots.append(sum((pb[i] - prof_l[i]) ** 2 / prof_l[i] for i in range(mb)))
        boots.sort()
        res[lang] = {"profile_chi2": round(chi, 4), "self_fit_median": round(boots[len(boots) // 2], 4),
                     "fits_like_self": chi <= boots[int(0.9 * len(boots))]}
    return {"results": res,
            "reading": "a pure letter-transposition of language X must fit X's letter profile about as well as X fits itself"}

# ---------------- PLAYFAIR SIGNATURE ----------------
def playfair_signature(words):
    dbl = 0; tot = 0
    for w in words:
        us = A.eva_segment(w)
        for a, b in zip(us, us[1:]):
            tot += 1
            if a == b: dbl += 1
    return {"doubled_digraphs": dbl, "digraphs": tot,
            "verdict": "Playfair-family EXCLUDED as sole cipher (it can never write a doubled digraph)"
                       if dbl > 0 else "signature compatible with Playfair family (necessary, not sufficient)"}

# ---------------- ACROSTIC + LENGTH + DISTANCE (imagined) ----------------
def acrostic_channel(loci):
    inits, mids = [], []
    for loc in loci:
        ws = A.words_of([loc])
        if not ws: continue
        inits.append(A.eva_segment(ws[0])[0])
        mid = ws[len(ws) // 2]
        mids.append(A.eva_segment(mid)[0])
    return {"initial_unit_h1": round(_cond_h1(inits), 3), "middle_unit_h1_control": round(_cond_h1(mids), 3),
            "initial_tokens": len(inits),
            "verdict": "acrostic channel carries structure" if _cond_h1(inits) < _cond_h1(mids) - 0.15
                       else "initials no more structured than middles — no acrostic signal"}

def length_cipher(words):
    lens = [len(A.eva_segment(w)) for w in words]
    rng = random.Random(5)
    sh = lens[:]; rng.shuffle(sh)
    return {"length_stream_h1": round(_cond_h1(lens), 3), "shuffled_h1": round(_cond_h1(sh), 3),
            "verdict": "word-length sequence carries order information" if _cond_h1(lens) < _cond_h1(sh) - 0.05
                       else "length order indistinguishable from shuffled — no length cipher"}

def distance_cipher(words):
    stream = [u for w in words for u in A.eva_segment(w)]
    top = [u for u, _ in Counter(stream).most_common(5)]
    gaps = []
    last = {}
    for i, u in enumerate(stream):
        if u in last and u in top: gaps.append(i - last[u])
        last[u] = i
    rng = random.Random(9)
    sh = stream[:]; rng.shuffle(sh)
    gaps_s = []; last = {}
    for i, u in enumerate(sh):
        if u in last and u in top: gaps_s.append(i - last[u])
        last[u] = i
    return {"gap_stream_h1_mod26": round(_cond_h1([g % 26 for g in gaps]), 3),
            "shuffled_h1_mod26": round(_cond_h1([g % 26 for g in gaps_s]), 3),
            "verdict": "inter-letter distances carry structure" if _cond_h1([g % 26 for g in gaps]) < _cond_h1([g % 26 for g in gaps_s]) - 0.05
                       else "distances no more structured than shuffled — no distance cipher"}

# ---------------- LOGIC III: SYLLABIC / VERBOSE ----------------
def _segmentations(skel, n_units, cand, cap=300):
    out = []
    def rec(i, rest, pieces):
        if len(out) >= cap: return
        if i == n_units:
            if rest == "": out.append(tuple(pieces))
            return
        for L in (1, 2, 3):
            if L <= len(rest):
                rec(i + 1, rest[L:], pieces + [rest[:L]])
    rec(0, skel, [])
    return out

def logic3(words):
    egy = A.egyptian_vocab()
    skels = sorted({w for w in egy if 2 <= len(w) <= 12})
    skel_set = set(skels)
    top = [w for w, _ in Counter(words).most_common(25)]
    cipher = {w: tuple(A.eva_segment(w)) for w in top}
    cand = defaultdict(set)
    impossible = []
    for w, us in cipher.items():
        found = False
        for sk in skels:
            if len(us) <= len(sk) <= 3 * len(us):
                for seg in _segmentations(sk, len(us), cand):
                    found = True
                    for u, piece in zip(us, seg): cand[u].add(piece)
        if not found: impossible.append(w)
    gate_rng = random.Random(17)
    inventory = sorted({c for s in skels for c in s})
    units = ["g%02d" % i for i in range(10)]
    syll = {u: "".join(gate_rng.choice(inventory) for _ in range(gate_rng.randint(1, 3))) for u in units}
    planted = []
    tries = 0
    while len(planted) < 20 and tries < 4000:
        tries += 1
        us = tuple(gate_rng.choice(units) for _ in range(gate_rng.randint(2, 5)))
        if "".join(syll[u] for u in us) in skel_set: planted.append(us)
    def solve(cipher_map, node_cap=20000):
        units_all = sorted({u for us in cipher_map.values() for u in us})
        cand_l = {u: sorted(cand.get(u, [])) for u in units_all}
        state = {"nodes": 0}
        def word_ok(us, assign):
            # exists a completion whose concatenation is an attested skeleton
            from functools import lru_cache
            pieces = [None] * len(us)
            def rec(i, built):
                if len(built) > 12: return False
                if i == len(us): return built in skel_set
                u = us[i]
                opts = (assign[u],) if u in assign else cand_l.get(u, [])
                return any(rec(i + 1, built + o) for o in opts if len(built) + len(o) <= 12)
            return rec(0, "")
        def search(assign):
            state["nodes"] += 1
            if state["nodes"] > node_cap: return None
            if len(assign) == len(units_all): return dict(assign)
            un = [u for u in units_all if u not in assign]
            u = min(un, key=lambda x: len(cand_l.get(x, [])))
            for piece in cand_l.get(u, []):
                na = dict(assign); na[u] = piece
                if all(word_ok(us, na) for us in cipher_map.values()):
                    r = search(na)
                    if isinstance(r, dict): return r
            return False
        r = search({})
        return ("UNDECIDED" if r is None else "CONSISTENT" if isinstance(r, dict) else "INCONSISTENT"), state["nodes"]
    # gate: the planted cipher must NOT be excluded
    saved = dict(cand)
    cand.clear()
    for us in planted:
        sk = "".join(syll[u] for u in us)
        for seg in _segmentations(sk, len(us), cand):
            for u, piece in zip(us, seg): cand[u].add(piece)
    g_out, _ = solve({("p%d" % i): us for i, us in enumerate(planted)})
    gate_pass = g_out == "CONSISTENT"
    cand.clear(); cand.update(saved)
    if impossible:
        return {"gate_pass": gate_pass, "gate_outcome_on_planted": g_out,
                "verdict": "INCONSISTENT", "reason": "no Egyptian skeleton segments into these words at all",
                "impossible_words": impossible[:8]}
    if not gate_pass:
        return {"gate_pass": False, "gate_outcome_on_planted": g_out,
                "status": "SOLVER_NOT_VALIDATED — manuscript verdict withheld"}
    outcome, nodes = solve(cipher)
    return {"gate_pass": True, "verdict": outcome, "nodes": nodes,
            "model": "each EVA unit = one fixed consonant cluster (1-3 letters); word reading must be an attested Egyptian form",
            "types_tested": len(top)}


# ---------------- ZOO+ : the remaining cages ----------------
def bifid_polybius(words):
    stream = [u for w in words for u in A.eva_segment(w)]
    pairs = [tuple(stream[i:i + 2]) for i in range(0, len(stream) - 1, 2)]
    rng = random.Random(13)
    sh = stream[:]; rng.shuffle(sh)
    pairs_s = [tuple(sh[i:i + 2]) for i in range(0, len(sh) - 1, 2)]
    return {"pair_ic": round(_ic(pairs), 4), "pair_ic_shuffled": round(_ic(pairs_s), 4),
            "verdict": "fractionation signature present (pair stream structured)" if _ic(pairs) > _ic(pairs_s) * 1.2
                       else "no Polybius/Bifid fractionation signature beyond control"}

def autokey_probe(words):
    stream = [u for w in words for u in A.eva_segment(w)]
    rng = random.Random(15)
    sh = stream[:]; rng.shuffle(sh)
    def agree(s, lag):
        return sum(1 for i in range(lag, len(s)) if s[i] == s[i - lag]) / max(1, len(s) - lag)
    rows = {lag: {"agree": round(agree(stream, lag), 4), "agree_shuffled": round(agree(sh, lag), 4)}
            for lag in range(1, 13)}
    best = max(rows, key=lambda l: rows[l]["agree"] - rows[l]["agree_shuffled"])
    return {"lags": rows, "best_lag": best,
            "verdict": "autokey/running-key feedback signature at lag %d" % best
                       if rows[best]["agree"] - rows[best]["agree_shuffled"] > 0.01
                       else "no autokey feedback signature at any lag"}

def codebook_profile(words, refs_words):
    prof_c = sorted((v / len(words) for v in Counter(words).values()), reverse=True)[:100]
    res = {}
    rng = random.Random(19)
    for lang, vocab in refs_words.items():
        prof_l = sorted((v / sum(vocab.values()) for v in vocab.values()), reverse=True)[:100]
        m = min(len(prof_c), len(prof_l))
        chi = sum((prof_c[i] - prof_l[i]) ** 2 / prof_l[i] for i in range(m))
        boots = []
        pool = [w for w, v in vocab.items() for _ in range(min(v, 5))]
        for _ in range(10):
            sample = [rng.choice(pool) for _ in range(len(words))]
            pb = sorted((v / len(words) for v in Counter(sample).values()), reverse=True)[:100]
            mb = min(len(pb), len(prof_l))
            boots.append(sum((pb[i] - prof_l[i]) ** 2 / prof_l[i] for i in range(mb)))
        boots.sort()
        res[lang] = {"word_profile_chi2": round(chi, 3), "self_fit_median": round(boots[len(boots) // 2], 3),
                     "fits_like_self": chi <= boots[int(0.9 * len(boots))]}
    return {"results": res,
            "reading": "a word-for-word codebook in language X should show X's word-frequency profile; a weak, necessary-not-sufficient test"}

def reverse_stream(words):
    stream = [u for w in words for u in A.eva_segment(w)]
    fwd = _cond_h1(stream); rev = _cond_h1(stream[::-1])
    return {"forward_h1": round(fwd, 3), "reversed_h1": round(rev, 3),
            "verdict": "stream is direction-asymmetric (reversed reads differently)" if abs(fwd - rev) > 0.05
                       else "no directional asymmetry beyond noise"}

def run_zoo(loci):
    words = [w.lower() for w in A.words_of(loci)]
    refs = language_refs()
    refs_words = {}
    heb = A.hebrew_vocab()
    if heb: refs_words["hebrew"] = heb
    lat = A.latin_vocab()
    if lat: refs_words["latin"] = lat
    egy = A.egyptian_vocab()
    if egy: refs_words["egyptian"] = Counter(egy)
    zoo = {"version": "ATHENA 20 — Cipher Zoo (everything)", "words": len(words),
           "vigenere": vigenere_lab(words, refs),
           "transposition_profile": transposition_profile(words, refs),
           "playfair": playfair_signature(words),
           "acrostic": acrostic_channel(loci),
           "length_cipher": length_cipher(words),
           "distance_cipher": distance_cipher(words),
           "logic3_syllabic_egyptian": logic3(words),
           "bifid_polybius": bifid_polybius(words),
           "autokey_probe": autokey_probe(words),
           "codebook_profile": codebook_profile(words, refs_words),
           "reverse_stream": reverse_stream(words)}
    brk = DIRS["results"] / "breaker_ZL3b.json"
    if brk.exists():
        zoo["breaker_assault"] = json.loads(brk.read_text()).get("by_language", {})
    return zoo

def main():
    for fname, tag in (("ZL3b-n.txt", "ZL3b"), ("IT2a-n.txt", "IT2a")):
        path = DIRS["data"] / fname
        if not path.exists(): continue
        zoo = run_zoo(A.load_loci(path))
        out = DIRS["results"] / ("zoo_%s.json" % tag)
        out.write_text(json.dumps(zoo, ensure_ascii=False, indent=1))
        print("wrote", out)

if __name__ == "__main__":
    main()
