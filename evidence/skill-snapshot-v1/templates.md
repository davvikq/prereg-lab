# Prereg-Lab Templates

Use these skeletons as-is. Fill every field; delete nothing - an empty section states
"considered, nothing to declare", which is different from it being absent.

## PREREGISTRATION.md

```markdown
# PREREGISTRATION

**Topic:** <one sentence: does X beat Y on metric M under conditions C>
**Date registered:** <BEFORE first measurement of the main matrix>
**Status:** frozen before the main matrix. Changes are allowed only as appended
addenda marked "changed after start, reason" - the original text is never edited.
sha256: <from prereg.py freeze> (frozen copy: docs/<exp>/PREREG_<exp>_frozen.md)

## 0. What exactly is tested

<2-4 sentences of mechanism: WHY you expect the effect. Hypotheses without a
mechanism cannot be defended when the result is ambiguous.>

### H1 (primary)
<directional, falsifiable, with numeric threshold>

### H0
<null>

### H2 (tested only if H1 passes its threshold)
<conditional claim>

## 1. Fixed objects

| Role | Item | Why |
|------|------|-----|
| <target/model/config> | <exact version/build> | <the reason, not "obvious"> |

## 2. Fixed conditions - NOT changed after start

- <version, threads, seeds, temperature, sizes, eval set, prompts, n_predict...>
- <if it can drift, it goes on this list>

## 3. Eval set

Source: <where from>. Size: <N>. Fingerprint: <sha256>.
Leakage: <how you know this did not tune anything that measured it>.

## 4. Metrics

Primary: <metric> - chosen because <principled argument written BEFORE data>.
Secondary: <list, descriptive only, computed and reported alongside>.

## 5. Analysis plan

Test: <sign-flip randomization / cluster bootstrap-t>. Alpha: <0.05 unless argued>.
Family: <which contrasts, how many, Holm m=<k>>. Stopping: <fixed N / OBF gates>.
Verdict rule: <outcome -> verdict mapping, exact>.

## 6. Change protocol

Appended addenda only, each "changed after start <date>, reason: <...>".

## 10. Cost estimate

<blocks x repeats x minutes; disk; what gets computed where>
```

## DECISIONS row

```markdown
| D-<NNN> | <date time> | <decision> | <fact: file, counter, command output - or explicit user approval> |
```

Reversal format - the original row stays untouched:

```markdown
| D-<NNN> | <date> | SUPERSEDED by D-<MMM>: <what changed> | <fact> |
```

## Deviation addendum (appended to frozen preregistration)

```markdown
---
**Changed after start <date>, reason:** <what and why>.
Blast radius: <which contrasts/blocks are affected, how>.
Original text above is unchanged.
```

## REPORT-<exp>.md

```markdown
# REPORT - <exp>

## 1. Verdict
<one line, looked up from the frozen rule, with the deciding numbers>

## 2. Preregistered contrasts
| Contrast | Effect | CI | p | Verdict-relevant |
|----------|--------|----|----|------------------|

## 3. Secondary metrics
<descriptive, reported alongside>

## 4. Post-hoc (labeled POST-HOC; decides nothing)
<separate subsections and files for each post-hoc probe>

## 10. Deviations
<mandatory even when empty: "none found - checked against <list>">

## 11. Artifacts
<paths to raw files; manifest path; manifest sha256>
```

## Run metadata: block_meta.jsonl

One JSON line per (configuration x repeat) block, written by the runner, read first on
any resume:

```json
{"block_id": 7, "config": "target_q4_draft_q8", "repeat": 2,
 "seed": 1337, "started_at": "...", "finished_at": "...",
 "n_records": 96, "anomalies": ["background process detected 22:14"]}
```

Resume rule: read this file, skip blocks with `finished_at` set and `n_records` equal to
the preregistered per-block count, restart only partial blocks - under the same frozen
conditions, never "fresh and improved".
