---
name: prereg-lab
description: Use when an empirical claim will drive a decision - benchmarks, performance comparisons, "is X faster/better than Y", A/B tests, comparing models or configs, validating an optimization before adopting it - requires freezing hypotheses, conditions, metrics, and thresholds BEFORE the first measurement, never interpreting data before collection is complete, and looking up the verdict from frozen criteria. Use this even when the comparison seems quick, obvious, or "just a sanity check" - quick unfrozen comparisons are exactly where measurement self-deception lives.
---

# Prereg-Lab

You are good at measuring things, and that is the problem. When you build something and
then measure it, every incentive you have points toward confirming that it works: you pick
the threshold after seeing the data, you quietly fix a confound mid-run, you report the
best of three repeats. Each step is innocent. Together they produce conclusions that feel
solid and are not.

This skill applies clinical-trial discipline to engineering experiments: freeze what you
expect before you look, run the plan without touching it, look up the verdict instead of
arguing it. It was distilled from a real experiment lab (preregistered local-LLM inference
studies) where this discipline caught confounds, mid-run temptations, and post-hoc
rationalization before they became false conclusions.

## Overview

**Core principle:** An unpreregistered measurement is an anecdote, not evidence.

**Violating the letter of this process is violating the spirit of this process.**

## The Iron Law

```
NO INTERPRETATION OF MEASURED DATA UNTIL PREREGISTRATION IS FROZEN
AND DATA COLLECTION IS COMPLETE
```

If you have not frozen the preregistration, you cannot look at results. If collection is
incomplete, you cannot look at results.

The only exception is mechanical correctness: "did the process produce output", "is the raw
file growing", "are counters incrementing". You may verify the experiment RUNS. You may not
look at what it SAYS. "Just checking the means" is a violation, not an exception.

## When to Use

Use for ANY question whose answer will drive a decision:

- Performance comparisons ("is config A faster than B")
- Benchmark runs used to pick a model, quant, or build
- A/B tests of prompts, UI variants, or bot flows
- Validating an optimization before adopting it
- Reproducing a claimed result before relying on it

**Use this ESPECIALLY when:**
- The comparison seems obvious or the effect looks huge (big effects die to confounds too)
- You built the thing being measured (you are the interested party)
- Under time pressure (time pressure makes peeking tempting, and peeking poisons everything)
- The measurement is expensive, so re-running is painful (exactly when honesty matters most)

**Don't use - mark EXPLORATORY instead:**
- Smoke tests, debugging, profiling to find candidate causes
- Summarizing published benchmarks or docs

Write the word EXPLORATORY in the journal when you are exploring. Exploratory findings may
become preregistered hypotheses for a NEW experiment. They may never become conclusions.

## The Phases

Complete each phase before starting the next. Skipping a phase is not speed, it is waste
you discover later.

### Phase 1: The Question

Write one sentence: "Does X beat Y on metric M under conditions C?" If the sentence names
no metric and no conditions, it is not an experiment yet - it is a vibe. Estimate the cost
(number of runs x minutes per run) and reduce scope NOW if it exceeds budget. Scope cuts
after the freeze are protocol deviations.

### Phase 2: Preregistration

Write `PREREGISTRATION.md` BEFORE any measurement of the main matrix. The skeleton is in
`templates.md` in this directory. Contents, in order:

1. **Hypotheses.** H1 (primary, falsifiable, directional), H0, and H2 conditional on H1
   passing its threshold. A numeric threshold in advance - ">= 10% relative on the primary
   metric" - chosen by argument, not by anticipation of the result.
2. **Fixed objects table.** Role | Item | Why. Every model, version, build, and companion
   component gets a stated reason. The reason is what stops silent substitution later.
3. **Fixed conditions.** The literal list of things NOT changed after start: versions,
   threads, seeds, sizes, eval set, prompts. If it can drift, it goes on this list.
4. **Eval set.** Source, size, fingerprint (hash), and how you know it did not leak into
   anything the system was tuned on.
5. **Metrics.** The primary metric chosen by a principled argument written BEFORE data
   (example: "AR over AL, because AL includes a bonus token that is not the draft's
   merit"). Secondary metrics are reported but do not decide.
6. **Analysis plan.** The test, the alpha, the comparison family, the stopping rule, and
   the verdict rule that maps outcomes to verdicts. Read `statistics.md` in this
   directory when choosing the test.
7. **Change protocol.** Changes are allowed only as appended addenda marked "changed after
   start, reason". The original text is never edited.

**Freeze** the preregistration: `python prereg.py freeze PREREGISTRATION.md --copy-to docs/<exp>/`
writes a frozen copy and records sha256 of both files. Record the hashes in the registry.
From this moment the experiment is armed: the conditions in the frozen text now outrank
your judgment. That asymmetry is the whole point.

### Phase 3: Decisions Registry

Append-only `DECISIONS.md`, one row per decision, written immediately after the decision
and before the action:

| ID | Date | Decision | Evidence |
|----|------|----------|----------|

Rules: never rewrite history - a reversed decision gets status SUPERSEDED with a pointer to
its replacement. Every row cites a fact (a file, a counter, a command output), not a
feeling. A decision made on explicit user approval records the approval as the evidence.
The registry is what makes the experiment auditable by a stranger.

### Phase 4: Pilot

Run a small pilot to fix operational parameters: thread counts, batch sizes, timeouts, and
the **noise floor** (repeat spread of the primary metric on identical configs). The pilot
runs BEFORE the freeze, not after - thresholds informed by it are still preregistered,
because they are set before main-matrix data exists. Record the pilot in the registry.

### Phase 5: Run

- **Randomize by blocks, not per request.** The unit of randomization is
  (configuration x repeat). Shuffle block order with a recorded seed so thermal drift and
  background processes do not correlate with the factor; shuffle item order within blocks.
- **Raw files only.** Every request writes its own record (jsonl). Summaries without raws
  cannot be resumed, audited, or re-analyzed.
- **Journal every anomaly** with a timestamp: OOM, restart, background process, odd counter
  value. Anomalies are data, not noise.
- **Long runs must survive session death.** Launch detached from the agent session
  (PowerShell `Start-Process`, `nohup`). On restart, resume by completeness: read raw
  files, skip completed blocks, restart only the partial one. Deterministic block order
  (seed) makes the resumed plan identical to the original.
- **Aborting is allowed and is a registry entry** with facts: processes killed, files
  saved, what is preserved. Interpretation is still forbidden.

**Mid-run discoveries do not change conditions.** This rule feels wrong every time, which
is why it is a rule. If you discover a confound - say, a plan parameter diverges from the
frozen value - do NOT patch it mid-run. Measured blocks stay comparable only under the
conditions they were measured under. Instead: (a) registry entry with facts and blast
radius, (b) mark the affected contrasts CONFOUNDED - descriptive only, never verdict-
deciding, (c) plan a separate follow-up experiment that re-measures them cleanly. Only
contrasts whose fixed conditions held on both sides decide the primary hypothesis.

### Phase 6: Analysis

Run only the preregistered analysis. `statistics.md` in this directory contains the
toolkit: sign-flip randomization test, cluster bootstrap-t, Holm correction, sequential
stopping rules, with code.

- Report effect size AND confidence interval AND p for every preregistered contrast. A bare
  p-value is not a result.
- Secondary metrics are reported alongside even when the verdict uses only the primary.
- If the preregistered test gives p = 0.06 against a frozen 0.05 threshold, the verdict is
  what the frozen rule says. You do not switch tests. If you want to know why it missed,
  explore separately - labeled POST-HOC, in its own files, deciding nothing.

### Phase 7: Verdict

The verdict is looked up, not argued: map outcomes through the frozen verdict rule and
stop there. Verdicts are not revisited, ever. If later diagnostics show the verdict's
rationale was wrong, you disclose that separately and design a NEW preregistered
experiment - the old verdict stands as the record of what the frozen rule concluded. A
failed gate is a reported result, not a hidden embarrassment.

### Phase 8: Report

Write `REPORT-<exp>.md`: verdict up top, preregistered contrasts with effect/CI/p,
secondary metrics, post-hoc sections labeled POST-HOC, and a Deviations section -
mandatory even when empty, because "no deviations" is a claim that gets verified. Then
generate the artifact manifest: `python prereg.py manifest experiments/<exp>/ -o docs/<exp>/<exp>_artifacts_manifest.sha256`
and record the manifest's own sha256 in the registry.

## Red Flags - STOP

If you catch yourself thinking:

- "Just peek at the first blocks to see if it's working" (it is never "just")
- "The effect looks like ~12%, so let's set the threshold at 10%"
- "The best repeat is the real performance, the others had background noise"
- "I'll analyze as I go, the plan can follow the data"
- "Switching from sign-flip to t-test is a technicality, same p roughly"
- "It doesn't count, I only looked at tok/s, not acceptance"
- "The confound is minor, I'll just fix the config for the remaining blocks"
- "Verdict is close, let me re-look at the frozen rule for wiggle room"

ALL of these mean: STOP. Return to the Iron Law. The data you have already seen cannot be
unseen, which is exactly why the next step is registering what you saw as a deviation, not
proceeding as if you hadn't.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Peeking doesn't count" | Peeked data shapes every later decision. It counts most. |
| "Threshold after the pilot" | Pilot comes BEFORE the freeze, never after. |
| "I'm confident the effect is real" | Confidence is the thing being tested. |
| "Just this once, it's a tiny experiment" | Tiny experiments feed big decisions most often. |
| "Fixing the confound mid-run is more rigorous" | It destroys comparability of finished blocks. Register, mark, follow up. |
| "Different test, same conclusion anyway" | Then the preregistered test will show it too. |
| "Verdict rules are for grants, not code" | Your verdict is no more honest because the subject is code. |
| "Exploratory means I can decide from it" | Exploratory means nobody decides from it until it survives a new experiment. |
| "Re-running the aborted blocks fresh" | Fresh must mean under frozen conditions with resume-by-completeness, not cherry-picked restarts. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| 1. Question | One sentence: X vs Y on M under C, cost estimate | Metric and conditions named |
| 2. Preregister | Hypotheses, fixed objects/conditions, metrics, analysis plan; freeze + sha256 | Frozen copy exists, hashes in registry |
| 3. Registry | DECISIONS.md row per decision, evidence cited | Append-only, facts not feelings |
| 4. Pilot | Operational params + noise floor, set BEFORE freeze | Params preregistered |
| 5. Run | Block randomization, raws, journal, detached, confound protocol | Data complete, no mid-run changes |
| 6. Analyze | Preregistered test only, effect + CI + p | No test switching |
| 7. Verdict | Look up from frozen rule | Not revisited |
| 8. Report | Deviations section, POST-HOC labels, artifact manifest | Stranger can re-derive verdict from raws |

## Supporting Techniques

These are part of prereg-lab and live in this directory:

- **`templates.md`** - Skeletons: PREREGISTRATION.md, DECISIONS row, deviation addendum,
  REPORT, run metadata schema. Read at Phase 2.
- **`statistics.md`** - The analysis toolkit with code: sign-flip randomization test,
  cluster bootstrap-t, Holm, alpha spending. Read at Phase 6, and at Phase 2 when writing
  the analysis plan.
- **`case-studies.md`** - Four factual episodes where this discipline mattered: the
  confound discovered mid-run, the session that died mid-experiment, the verdict that was
  not revised even when its rationale turned out wrong, and the honest downgrading of a
  post-hoc freeze. Read once, before your first experiment, to understand why the rules
  exist.
- **`prereg.py`** - Deterministic helpers, stdlib only: `freeze` (sha256 + frozen copy),
  `manifest` (sha256 of all raw artifacts), `signtest` (Monte Carlo sign-flip p),
  `holm` (step-down adjusted p-values). Run instead of improvising equivalents, so every
  experiment hashes and tests the same way.
