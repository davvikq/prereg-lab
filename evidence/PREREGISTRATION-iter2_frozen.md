# PREREGISTRATION — iteration-2 eval

**Topic:** Does prereg-lab v2 (narrowed trigger description + `prereg.py decide` +
registry-discipline guidance) improve hands-on benchmark discipline over no-skill
baseline, without regressing on advisory scenarios?

**Date registered:** 2026-11-21, before any iteration-2 run.

## 0. Hypotheses

- **H1 (primary, directional):** On eval-0 (hands-on benchmark), mean assertion pass rate
  with_skill > without_skill across 3 runs per configuration.
- **H0:** No difference.
- **H2 (regression check, conditional on eval-0 design being sound):** On eval-1 and
  eval-2 (1 run per configuration each), with_skill pass rate >= without_skill pass rate
  (the refined scoping guidance does not hurt advisory behavior).

## 1. Fixed design

- Iteration-1 grading results and prompts are frozen; prompts are IDENTICAL to
  iteration-1 (only assertions changed, per grader eval-feedback).
- Baseline = without_skill in both iterations (consistent comparison).
- v1 skill snapshot preserved at `skill-snapshot-v1/` for provenance.
- Graders: batched per eval set, reading `agents/grader.md`, exact
  text/passed/evidence schema; timing sourced from run `timing.json` only.

## 2. Budget allocation (scoped BEFORE runs)

- eval-0: 3 runs x 2 configurations (the discriminating eval).
- eval-1, eval-2: 1 run x 2 configurations each (regression checks only).
- Rationale: eval-1/2 showed zero discrimination at iteration-1; 3x3 there would be
  pseudo-replication of budget. Total: 10 executor runs + 2 batch graders.

## 3. Metrics

Primary: mean assertion pass rate per configuration on eval-0.
Secondary: per-assertion pattern (which assertions differentiate), time, tokens.

## 4. Analysis plan

- Descriptive: mean +/- std of pass rates per configuration, eval-0.
- Paired sign-flip test on the 3 per-run differences: declared EXPLORATORY in advance -
  with n=3 the minimum two-sided p is 0.25, so no result can reach alpha=0.05. The
  comparison is directional evidence, not confirmation. A confirmatory claim would
  require >= 6 paired runs (min two-sided p = 0.03125).
- H2: descriptive comparison, single run per cell (weaker evidence, labeled as such).

## 5. Change protocol

Appended addenda only. The eval prompts and assertions above are frozen; assertion text
matches `evals/evals.json` v2 exactly.

## 6. Cost estimate

~10 executor runs (1.5-8 min each, concurrency 3), ~9M subagent tokens, 2 graders.
