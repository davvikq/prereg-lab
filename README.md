# prereg-lab

Clinical-trial discipline for AI-agent measurements — freeze the hypothesis before the data exists, and look the verdict up instead of arguing it.

An experiment protocol that doesn't beg the agent to be honest — it makes dishonesty procedurally awkward.

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg) ![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg) ![Evaluated](https://img.shields.io/badge/eval-preregistered-brightgreen)

## Why prereg-lab

When an AI agent measures its own work — "is config A faster than B?", "did the optimization help?", "adopt or not?" — it self-deceives in innocent, predictable ways:

- Picks the acceptance threshold **after** seeing the data ("looks like ~12%... let's require 10%")
- Reports the best of three repeats as "the" performance
- Quietly patches conditions mid-run when a confound appears
- Reruns the analysis with a different test when p = 0.06
- Argues with the result until the result agrees

Each step is innocent. Together they produce conclusions that feel solid and aren't. A benchmark without a preregistration is an anecdote wearing a lab coat.

prereg-lab is a [SKILL.md](SKILL.md) skill that applies clinical-trial discipline to engineering experiments: freeze what you expect before you look, run the plan without touching it, look up the verdict instead of arguing it. It was distilled from a real preregistered local-LLM inference lab, where the method repeatedly caught confounds and post-hoc rationalization before they became false conclusions.

## How it works

```
NO INTERPRETATION OF MEASURED DATA UNTIL PREREGISTRATION IS FROZEN
AND CONFIRMATORY DATA COLLECTION IS COMPLETE
```

Eight phases, each with a reason attached:

| Phase | What happens | Why it matters |
|-------|--------------|----------------|
| 1. Question | One sentence: X vs Y on metric M under conditions C | A question without a metric is a vibe |
| 2. Pilot | Operational params + noise floor — calibration only, "how do I run it", never "does X work" | The only pre-freeze measurements the Iron Law allows |
| 3. Registry | Append-only DECISIONS.md, one row per decision, written **at decision time** | `prereg.py decide` stamps a mechanical UTC timestamp — backfilled registries are narratives |
| 4. Preregister | Hypotheses, fixed conditions, numeric thresholds, analysis plan → frozen copy + sha256 | After the freeze, the text outranks your judgment |
| 5. Run | Block randomization, raw files only, anomaly journal, detached processes | Assumes your own session will die; resumes by completeness |
| 6. Analyze | Only the preregistered test; effect + CI + p | p = 0.06 against a frozen 0.05 → the verdict is what the rule says |
| 7. Verdict | Looked up from the frozen rule, never revisited | Wrong rationale? Disclose it, run a NEW experiment |
| 8. Report | Mandatory Deviations section, POST-HOC labels, artifact manifest | "No deviations" is a claim that gets verified |

For pure advisory questions (no measurements, no numbers used as evidence) the skill steps aside — the ceremony would be expensive theatre. For "should I adopt based on these numbers I already have?" it refuses to bless them and drafts a cheap follow-up instead.

## How prereg-lab compares

| | prereg-lab | "Be careful" prompting | Eyeball & rerun | Academic prereg skills (OSF/AsPredicted) |
|---|---|---|---|---|
| Freezes hypotheses + thresholds **before** first measurement | ✅ sha256-frozen copy | ❌ | ❌ | ✅ for human studies |
| Forbids interpreting partial data | ✅ Iron Law | ❌ | ❌ | ⚠️ process, not enforcement |
| Verdict looked up from frozen rule | ✅ | ❌ | ❌ | ⚠️ |
| Append-only decisions registry, mechanical timestamps | ✅ `prereg.py decide` | ❌ | ❌ | ❌ |
| Deterministic stats toolkit bundled | ✅ sign-flip, Holm, manifests | ❌ | ❌ | ❌ |
| Survives agent session death | ✅ detached runs, resume-by-completeness | ❌ | ❌ | ❌ |
| Honest-deviations section mandated | ✅ | ❌ | ❌ | ⚠️ |
| Target | **Your agent's own benchmarks** | — | — | Human-subject studies |

Not an OSF skill. It doesn't write preregistration documents for registries — it gates the measurements your agent was about to take five minutes from now.

## Quickstart

Tested with harnesses that read SKILL.md skills (Claude Code, Codex, Cursor, OpenCode). One clone, one install:

```bash
git clone --depth 1 https://github.com/davvikq/prereg-lab
python prereg-lab/prereg.py install    # stdlib only, Python 3.11+
```

`install` copies the skill into the standard agent skills locations it detects: the canonical shared `~/.agents/skills` (always), plus existing harness dirs — `~/.claude/skills`, OpenCode locations, project-local `.agents` / `.claude` / `.opencode` — and prints exactly where it landed. One skill folder, all your agents.

- Preview targets first: `--dry-run`
- Exotic harness location: `--dir /path/to/skills` (repeatable)
- Already installed a different version? Skipped, never silently replaced — `--update` to overwrite
- Verify: `python prereg-lab/prereg.py --help`

Then just ask the agent to measure something — "проверь, что новый конфиг быстрее", "run an A/B on these prompts", "did the optimization help?" — and watch it freeze a preregistration before the first measurement instead of vibing its way to a conclusion.

That's it.

## Preview

The full lifecycle in about a second — ending with the guards refusing to rewrite history:

![prereg-lab demo: preregister, freeze, decide, run, analyze, verdict lookup - and the guards refusing to overwrite](assets/demo.gif)

Prefer an interactive player? `assets/demo.cast` is a standard asciinema v2 recording of the same session.

## Example session

Real output of `python demo.py` — the whole lifecycle on a toy experiment (builtin `sum()` vs a manual loop), in about one second, in a throwaway temp dir (paths shortened; the registry table is abridged):

```
1. QUESTION - one sentence, metric named, cost estimated
   Does builtin sum() beat a manual for-loop on median full-pass time over
   identical integer lists? Metric: median pass seconds. Cost: ~24 runs, seconds.
   registry opened before the pilot:
   appended: | D-001 | 2026-11-22 12:55 UTC | Pilot plan: 3 calibration passes, builtin only; calibration only | ... |

2. PILOT - calibration only: 'how do I run it', never 'does X work'
   3 untimed calibration passes -> noise floor 10.3% of median pass
   (sets operational expectations; no hypothesis is tested here)
   appended: | D-002 | 2026-11-22 12:55 UTC | Pilot noise floor 10.3%; operational calibration only | ... |

3. REGISTRY - DECISIONS.md opened before the pilot; rows at decision time
   appended: | D-003 | 2026-11-22 12:55 UTC | Demo design: builtin vs manual loop, paired repeats | ... |
   appended: | D-004 | 2026-11-22 12:55 UTC | Threshold 10%: below it, the switch is not worth a diff review | ... |
   (the demo then prints the full append-only table)

4. PREREGISTER - hypotheses, thresholds, analysis plan -> frozen + sha256
   written; nothing confirmatory has been measured yet
   sha256:   adfa15e198077908...  (frozen copy: docs/PREREGISTRATION_frozen.md)

5. RUN - 12 paired repeats, shuffled arm order, raw records only
   24 raw records -> raw_runs.jsonl (one record per run, not a summary)
   correctness gate: builtin sum == loop sum == reference on every pass: True

6. ANALYZE - only the preregistered test, effect + p
   median pass: builtin 0.48 ms vs loop 3.50 ms
   relative reduction R = 86.3%   (frozen threshold: >= 10%)
   exact two-sided sign-flip p = 0.000488   (frozen alpha: 0.05)

7. VERDICT - looked up from the frozen rule, not argued
   rule: ADOPT builtin if R >= 0.10 AND p < 0.05, else KEEP loop
   fired: ADOPT builtin  (R = 86.3%, p = 0.000488)

8. REPORT - report, manifest, deviations... then the guards refuse to rewrite history
   report written -> REPORT-demo.md
   5 files -> .../docs/manifest.sha256
   manifest sha256: aa01cd6bbc077ef0...
   Deviations: none found - demo, but the section would be here anyway.
   re-freeze exit 1:
     freeze: .../PREREGISTRATION_frozen.md already exists. Do NOT overwrite -
     the change protocol is append-only addenda ('changed after start, reason').
   manifest overwrite exit 1:
     manifest: .../manifest.sha256 exists. Manifests are immutable -
     write a new one for the new state instead.

Immutable by default. That is the whole point.
```

Run it yourself — `python demo.py` — your disk stays clean. Timings, and therefore R and the prereg/manifest hashes, vary by machine; the verdict logic does not.

## What's inside

| File | Purpose |
|------|---------|
| `SKILL.md` | The skill: 8 phases, Iron Law, Red Flags, rationalization table |
| `templates.md` | Skeletons: preregistration, decisions registry, deviation addendum, report |
| `statistics.md` | The analysis toolkit with code: sign-flip randomization test, cluster bootstrap-t, Holm, stopping rules |
| `case-studies.md` | Four factual episodes where the discipline mattered — read once to learn why the rules exist |
| `prereg.py` | Deterministic helpers, stdlib only |
| `demo.py` | The lifecycle above in ~1 second, in a throwaway temp dir |
| `evals/evals.json` | 3 test cases with pre-committed assertions |
| `evidence/benchmark.json` | The evaluation described below, machine-readable |
| `evidence/PROVENANCE.md` | Hashes, timeline, and what is repo-verifiable vs author-attested |
| `evidence/grading/` | Per-run grading records for the 10 eval runs |

`prereg.py` commands:

| Command | Purpose |
|---------|---------|
| `freeze FILE --copy-to DIR` | sha256 + frozen copy; refuses to overwrite an existing freeze |
| `manifest DIR -o FILE` | sha256 manifest of artifacts; refuses to overwrite — manifests are immutable |
| `decide REGISTRY "..." --evidence "..."` | append-only registry row with a mechanical UTC timestamp |
| `signtest --diffs ...` | sign-flip randomization test (exact ≤ 17 diffs, Monte Carlo beyond) |
| `holm p1 p2 ...` | Holm step-down adjusted p-values for a preregistered family |
| `install` | copy the skill into detected agent skills locations; `--dir`, `--update`, `--dry-run` |

## The evidence

The skill was evaluated with a preregistered protocol — frozen before any run and shipped in-repo: [evidence/PREREGISTRATION-iter2_frozen.md](evidence/PREREGISTRATION-iter2_frozen.md) (sha256 82dbb085…). 10 agent runs across 3 test cases, with-skill vs baseline, graded by separate grader sessions against pre-committed assertions.

| Test case | with_skill | baseline | Paired diffs |
|-----------|-----------|----------|--------------|
| **Hands-on benchmark** (n=3) | **0.905** | 0.381 | +0.571, +0.571, +0.429 — all favor the skill |
| "Bless these two numbers" advisory | 1.00 | 1.00 | non-discriminating |
| Mid-run confound response | 1.00 | 0.80 | new no-peek assertion caught the baseline |

Two of the three with-skill hands-on runs missed the 10-minute wall-clock assertion (912.7s and 706.3s vs 700s) — every method assertion passed in all three. The measured runs themselves took seconds; the overhead is agent reasoning and artifact production, and it is included in the 0.905 above.

Full numbers: [evidence/benchmark.json](evidence/benchmark.json); per-run grading: [evidence/grading/](evidence/grading/); hashes and attested limits: [evidence/PROVENANCE.md](evidence/PROVENANCE.md). Honest caveats, in the skill's own spirit: n = 3 per cell on the hands-on eval (one run per cell on the two advisory evals), so the paired sign-flip test was declared exploratory in advance (minimum two-sided p = 0.25 at n = 3) — this is consistent directional evidence, not statistical confirmation. In all three baseline runs the same four assertions failed — no preregistration, no freeze before confirmatory data, no rule-derived verdict, no registry — and run 1 additionally failed effect+variance.

The moment that sold it: in one graded run, `str.find` beat regex by 26.7% — the preregistered "≥10%" threshold passed, but exact sign-flip gave **p = 0.0625 against a frozen 0.05**. The frozen rule fired *against* the intuition, and the agent complied: no test switching, no added repeats. Verdicts are looked up, not argued. That's the whole point.

Cost, honestly stated: with-skill runs use ~4.8× more tokens on hands-on benchmarks, and 2 of 3 exceeded the 10-minute wall-clock bound (the measurements themselves took seconds; the rest is reasoning and artifacts). For advisory questions it stays out of the way — and the trigger description tells it to.

## Data & Privacy

100% local. No telemetry, no network calls, no accounts. `prereg.py` hashes files and runs math — nothing leaves your machine.

## FAQ

**Is this just a prompt telling the agent to be careful?**
No. The discipline lives in process artifacts — frozen copies with hashes, append-only registries with mechanical timestamps, immutable manifests — and `prereg.py` refuses the operations that would quietly break them.

**Can the agent still cheat?**
Yes. The skill raises the cost of self-deception; it doesn't handcuff anyone. In one graded run the agent still appended a registry row late — which broke the manifest hash and got caught. That's the design working: violations leave fingerprints.

**Will it slow my agent down?**
On hands-on benchmarks, yes — roughly 5× tokens, and in our runs 2/3 exceeded a 10-minute wall-clock bound. The measurements themselves took seconds; the rest is reading the skill and producing artifacts. For advisory questions the trigger description keeps it out of the way, and a tiny bounded experiment earns a one-page preregistration — the discipline is the freeze order, not the page count.

**Does it work outside llama.cpp / ML benchmarks?**
It's domain-neutral: prompts, configs, build times, search quality, anything measurable. Case studies in the skill happen to come from LLM inference work.

**Can I use the statistics without the skill?**
Yes. `prereg.py` and `statistics.md` are standalone — the sign-flip test and Holm correction are the right default for small paired agent experiments regardless.

**What about false negatives — strict thresholds rejecting real effects?**
That's the cost of honesty, and the skill prices it explicitly: thresholds and stopping rules are chosen before the data exists, and a failed gate is a reported result, not a hidden embarrassment. Want a second look? Run a new preregistered experiment — never revise the verdict.

## Tests

The eval definitions and per-run grading are the test evidence. `evals/evals.json` holds 3 test cases with pre-committed assertions; the full pipeline (runs, grading, aggregation) follows the skill-creator loop, with grading artifacts kept in `evidence/grading/`. Smoke-check the toolkit:

```bash
python demo.py                                   # lifecycle + overwrite guards, ~1 s
python prereg.py signtest --diffs 1 2 3          # exact, p = 0.25
python prereg.py holm 0.003 0.014 0.052          # step-down adjusted
```

The freeze/manifest overwrite guards are exercised by `demo.py`.

## License

MIT — use it, fork it, ship it. © 2026 Davvik.
