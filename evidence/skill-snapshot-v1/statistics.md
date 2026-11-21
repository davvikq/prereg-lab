# Prereg-Lab Statistics

The analysis toolkit. Read at Phase 2 (when writing the analysis plan) and Phase 6 (when
running it). Everything runs on a Python REPL with stdlib only; `prereg.py` in this
directory wraps the two workhorses (`signtest`, `holm`) so every experiment uses the same
implementation.

The common thread: agent-run experiments have small N, paired/blocked structure, and no
business being analyzed with Gaussian assumptions and no discipline. Randomization-based
inference makes no distributional assumptions - the only model is "the randomization you
actually did".

## Sign-flip randomization test (the default)

For paired or blocked designs: compute per-block differences `d_i = x_i - y_i` under the
sign convention fixed in the preregistration, then flip signs with all 2^n patterns (exact)
or Monte Carlo (large n). The randomization itself is the null: if the treatment did
nothing, signs are exchangeable.

```python
import random

def sign_flip_p(diffs, n_mc=99999, seed=1337):
    """Two-sided p for paired differences. Seed fixed in the preregistration."""
    obs = abs(sum(diffs))
    rng = random.Random(seed)
    ge = 0
    for _ in range(n_mc):
        s = sum(x * rng.choice((-1, 1)) for x in diffs)
        if abs(s) >= obs:
            ge += 1
    return (ge + 1) / (n_mc + 1)
```

- For n <= 17 enumerate all patterns exactly; otherwise Monte Carlo with the preregistered
  seed. Report the method and the seed.
- One-sided versions exist but require the direction to be stated in the preregistration.
  Choosing the side after seeing the data is the classic sin.

## Cluster bootstrap-t (for confidence intervals)

When requests are nested in blocks (sessions, configs, days), naive bootstrap over
requests underestimates variance. Bootstrap the BLOCKS:

```python
import random, statistics as st

def cluster_bootstrap_t(blocks, n_boot=9999, seed=1337):
    """blocks: list of per-block means. Returns (mean, ci_lo, ci_hi)."""
    rng = random.Random(seed)
    n = len(blocks)
    means = []
    for _ in range(n_boot):
        sample = [blocks[rng.randrange(n)] for _ in range(n)]
        means.append(st.mean(sample))
    means.sort()
    return (st.mean(blocks), means[int(0.025 * n_boot)], means[int(0.975 * n_boot)])
```

Report effect + CI + p for every preregistered contrast. The CI shows magnitude; the p
shows compatibility with the null; neither substitutes for the other.

## Holm step-down (for families of contrasts)

When the preregistration declares m contrasts in one family, control FWER:

`prereg.py holm 0.003 0.014 0.052` sorts p ascending, multiplies by (m - rank + 1),
propagates the running maximum, caps at 1. Use the adjusted values against the family
alpha. Declare the family and its size in the preregistration - adding comparisons after
seeing results inflates the family, which is the same sin as peeking.

## Sequential looks / early stopping

If the experiment may stop early, the stopping rule must be preregistered: fixed N, or a
spending function (e.g. O'Brien-Fleming gates G1, Gmax with boundary p-values computed
BEFORE the first look). Early stopping without preregistered gates re-inflates alpha the
same way as running the test many times; the frozen gates are what make "we stopped early
because it worked" honest. A post-hoc early stop means the result is reported as
suggestive, not confirmed - say so in the Deviations section.

## What "the verdict is looked up" means numerically

The preregistration contains an exact mapping, e.g.:

- H1 passes if relative drop on primary metric >= 10% with sign-flip p < 0.05
- H2 tested only if H1 passed
- Any gate failing -> the corresponding verdict, even if "everything else looked great"

If the result lands between two verdicts, the rule already assigned it one. Write that
one down. Ambiguity after the fact is resolved by the frozen text, not by debate.

## Metric choice: primary vs secondary

Pick ONE primary metric before data, by a principled argument written into the
preregistration (example: "AR over AL, because AL includes a bonus token that is not the
draft's merit"). Compute and report both. Decide by the primary. If the argument for the
choice was good, you will rarely be tempted to switch; if you are tempted, that temptation
is the signal that the secondary is telling a friendlier story and the primary is telling
the true one.
