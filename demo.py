#!/usr/bin/env python3
"""prereg-lab demo: the full lifecycle in a couple of seconds, in a throwaway temp dir.

Toy experiment: builtin sum() vs a manual loop over the same integers.
Walks the whole prereg-lab pipeline - question -> pilot -> registry ->
preregister (freeze) -> run -> analyze -> verdict lookup -> report - and then
shows the guards refusing to overwrite the freeze and the manifest.

Deterministic measurements (seed 1337). Timestamps are the only real-time part.
Leaves nothing on your disk: everything happens in a temp dir that is removed
at the end.

Usage: python demo.py
"""

import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True  # keep the "leaves nothing on your disk" promise literal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from prereg import sign_flip_p  # noqa: E402

PREREG = """\
# PREREGISTRATION - demo (builtin sum vs manual loop)

## 0. Hypotheses
H1: builtin sum() is >= 10% faster than a manual for-loop on the median
    full-pass time over identical integer lists.
H0: no difference.
H2: n/a (conditional experiments are out of scope for the demo).

## 1. Fixed conditions - NOT changed after start
- 200,000 integers per list, identical lists for both arms (seed 1337)
- 12 paired repeats, shuffled arm order within each pair
- 1 untimed warm-up pass; interpreter: the one running this demo
- pilot noise floor (Phase 2 calibration): {noise_floor} of median pass

## 4. Metrics
Primary: median full-pass time, relative reduction R = (loop - builtin)/loop.
Secondary: none.

## 5. Analysis plan
Exact two-sided sign-flip randomization test on paired differences, alpha 0.05.
Verdict rule: ADOPT builtin if R >= 0.10 AND p < 0.05; otherwise KEEP loop.
"""


def hr(title):
    print("\n" + "=" * 64 + f"\n {title}\n" + "=" * 64)


def run_cli(args):
    r = subprocess.run([sys.executable, os.path.join(HERE, "prereg.py")] + args,
                       capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def measure(arm, xs):
    t0 = time.perf_counter()
    if arm == "builtin":
        s = sum(xs)
    else:
        s = 0
        for x in xs:
            s += x
    return time.perf_counter() - t0, s


def main():
    rng = random.Random(1337)
    work = tempfile.mkdtemp(prefix="prereg-lab-demo-")
    try:
        hr("1. QUESTION - one sentence, metric named, cost estimated")
        print("Does builtin sum() beat a manual for-loop on median full-pass time over")
        print("identical integer lists? Metric: median pass seconds. Cost: ~24 runs, seconds.")

        hr("2. PILOT - calibration only: 'how do I run it', never 'does X work'")
        xs = [rng.randrange(0, 1000) for _ in range(200_000)]
        pilot = [measure("builtin", xs)[0] for _ in range(3)]
        med = sorted(pilot)[1]
        noise = (max(pilot) - min(pilot)) / med
        print(f"3 untimed calibration passes -> noise floor {noise:.1%} of median pass")
        print("(sets operational expectations; no hypothesis is tested here)")

        hr("3. REGISTRY - DECISIONS.md opened before anything else, rows at decision time")
        reg = os.path.join(work, "DECISIONS.md")
        for dec, ev in [("Demo design: builtin vs manual loop, paired repeats",
                         "same interpreter, same lists"),
                        ("Threshold 10%: below it, the switch is not worth a diff review",
                         "practical-significance argument, pre-data")]:
            _, out = run_cli(["decide", reg, dec, "--evidence", ev])
            print(out.splitlines()[0])

        hr("4. PREREGISTER - hypotheses, thresholds, analysis plan -> frozen + sha256")
        prereg_path = os.path.join(work, "PREREGISTRATION.md")
        with open(prereg_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(PREREG.format(noise_floor=f"{noise:.1%}"))
        print("written; nothing confirmatory has been measured yet")
        code, out = run_cli(["freeze", prereg_path, "--copy-to", os.path.join(work, "docs")])
        print(out)

        hr("5. RUN - 12 paired repeats, shuffled arm order, raw records only")
        reference = sum(xs)  # computed once, outside the timed window
        measure("builtin", xs)  # warm-up, untimed
        raw = []
        builtin_t, loop_t, sums_match = [], [], True
        for i in range(12):
            for arm in rng.sample(["builtin", "loop"], 2):
                dt, s = measure(arm, xs)
                raw.append({"pair": i, "arm": arm, "seconds": round(dt, 6), "sum": s})
                (builtin_t if arm == "builtin" else loop_t).append(dt)
                sums_match = sums_match and (s == reference)  # every pass, BOTH arms
        with open(os.path.join(work, "raw_runs.jsonl"), "w", encoding="utf-8") as f:
            for r in raw:
                f.write(json.dumps(r) + "\n")
        print("24 raw records -> raw_runs.jsonl (one record per run, not a summary)")
        print(f"correctness gate: builtin sum == loop sum == reference on every pass: {sums_match}")

        hr("6. ANALYZE - only the preregistered test, effect + p")
        diffs = [l - b for b, l in zip(builtin_t, loop_t)]
        p = sign_flip_p(diffs)[0]
        b_med = sorted(builtin_t)[6]
        l_med = sorted(loop_t)[6]
        rel = (l_med - b_med) / l_med
        print(f"median pass: builtin {b_med*1000:.2f} ms vs loop {l_med*1000:.2f} ms")
        print(f"relative reduction R = {rel:.1%}   (frozen threshold: >= 10%)")
        print(f"exact two-sided sign-flip p = {p:.6f}   (frozen alpha: 0.05)")

        hr("7. VERDICT - looked up from the frozen rule, not argued")
        verdict = "ADOPT builtin" if (rel >= 0.10 and p < 0.05) else "KEEP loop"
        print(f"rule: ADOPT builtin if R >= 0.10 AND p < 0.05, else KEEP loop")
        print(f"fired: {verdict}  (R = {rel:.1%}, p = {p:.6f})")

        hr("8. REPORT - manifest, deviations... and the guards refuse to rewrite history")
        code, out = run_cli(["manifest", work, "-o", os.path.join(work, "docs", "manifest.sha256")])
        print(out)
        print("Deviations: none found - demo, but the section would be here anyway.")

        code, out = run_cli(["freeze", prereg_path, "--copy-to", os.path.join(work, "docs")])
        print(f"re-freeze exit {code}:")
        print("  " + out.replace("\n", "\n  "))
        code, out = run_cli(["manifest", work, "-o", os.path.join(work, "docs", "manifest.sha256")])
        print(f"manifest overwrite exit {code}:")
        print("  " + out.replace("\n", "\n  "))
        print("\nImmutable by default. That is the whole point.")
    finally:
        shutil.rmtree(work, ignore_errors=True)
        print("\n(temp dir removed - your disk is clean)")
        print("Now imagine the agent doing this before every benchmark it runs for you.")


if __name__ == "__main__":
    main()
