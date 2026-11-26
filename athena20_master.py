#!/usr/bin/env python3
"""ATHENA 20 — THE MASTER RUN. One program, the whole arsenal:
core proofs (Logic I + II), the Gauntlet, the Residual Atlas, the
full Cipher Zoo on both witnesses, and the Breaker (gated solvers +
graded assault), closing with one consolidated verdict. This is the
'best codebreaker' configuration: every engine ATHENA 20 owns, run
end to end, filed as a single report."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import athena20 as A
import athena20_zoo as Z
import athena20_breaker as B

def main():
    zl = A.DIRS["data"] / "ZL3b-n.txt"
    it = A.DIRS["data"] / "IT2a-n.txt"
    master = {"program": "ATHENA 20.0 — The Best Program (master run)"}
    print("stage 1/4: core proofs + gauntlet + atlas", flush=True)
    master["core"] = A.build_report(zl)
    print("stage 2/4: cipher zoo, ZL witness", flush=True)
    master["zoo_zl"] = Z.run_zoo(A.load_loci(zl))
    if it.exists():
        print("stage 3/4: cipher zoo, Takahashi witness", flush=True)
        master["zoo_it"] = Z.run_zoo(A.load_loci(it))
    print("stage 4/4: breaker gates + assault", flush=True)
    master["breaker"] = B.assault()
    # consolidated verdict: the core verdict plus every zoo engine's line
    verdict = {"from_core": master["core"]["verdict"]}
    zoo_lines = {}
    for tag in ("zoo_zl", "zoo_it"):
        if tag in master:
            zoo_lines[tag] = {k: v.get("verdict") or v.get("status") or v.get("reading")
                              for k, v in master[tag].items() if isinstance(v, dict)}
    verdict["zoo_verdicts"] = zoo_lines
    bl = master["breaker"]
    verdict["breaker"] = ({"gates": bl.get("gates"), "status": bl.get("status"),
                           "by_language": bl.get("by_language")} if isinstance(bl, dict) else bl)
    master["consolidated_verdict"] = verdict
    out = A.DIRS["results"] / "ATHENA20_MASTER_ZL3b.json"
    out.write_text(json.dumps(master, ensure_ascii=False, indent=1))
    print("wrote", out, flush=True)

if __name__ == "__main__":
    main()
