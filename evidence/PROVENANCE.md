# PROVENANCE

What a clone of this repository can verify on its own, and what is author-attested.
Written 2026-11-21 in response to an external review; hashes are of the shipped files.

## Repo-verifiable artifacts

| Artifact | Path | sha256 |
|----------|------|--------|
| Frozen eval protocol (frozen 2026-11-21 00:48 UTC, **before** every measurement) | [evidence/PREREGISTRATION-iter2_frozen.md](PREREGISTRATION-iter2_frozen.md) | `82dbb085e90cd65c773ca423f699e57b41e492e0f18dcaae711aaa02c3898d87` |
| Eval definitions + pre-committed assertions | [evals/evals.json](../evals/evals.json) | `2089dc5dad96b7fb29938d7e019a46e24f6c344a0f3c374ab5bf694a90c3e1f5` |
| Aggregated benchmark (10 runs, 3 test cases) | [evidence/benchmark.json](benchmark.json) | `ca67ebe8fccb60030fff0c5ecb36eb4a0a2e6a900250029cadbe413c2c2fb4c2` |
| v1 skill snapshot (pre-review state, for diffing what the review changed) | [evidence/skill-snapshot-v1/](skill-snapshot-v1/) | SKILL.md `f337161effdcf51763576df0fb1eafe89095b07e104bb0458c3e4ecefaabff4e` |
| Per-run grading records (10 runs, exact text/passed/evidence schema) | [evidence/grading/](grading/) | scanned: 0 local paths |

## Timeline (machine-local, UTC+5; UTC in parentheses)

- 2026-11-21 05:48:54 (00:48 UTC) — eval protocol frozen, sha256 above
- 2026-11-21 05:55:35 (00:55 UTC) — first measurement file written (eval-0, with_skill run)
- 2026-11-21 06:21:44 (01:21 UTC) — last measurement file written (eval-2, baseline run)
- freeze precedes every measurement mtime by at least 6 minutes; grading and aggregation
  follow (benchmark.json generated 01:33 UTC)

## Workspace → repo mapping (attested)

Original files live in the author's private workspace. Shipped copies:

- `workspace/skill-snapshot-v1/` → [evidence/skill-snapshot-v1/](skill-snapshot-v1/) (shipped)
- `workspace/iteration-2/*/*/run-*/grading.json` → [evidence/grading/](grading/) (shipped,
  renamed `eval-name-configuration-run-N.json`)
- run outputs / raw measurement files → **not shipped** (large; contain machine-specific
  paths); per-run pass rates, timing, and token counts are in
  [evidence/benchmark.json](benchmark.json), per-assertion verdicts in the grading files
- the repo copy of the frozen protocol carries a copy-time mtime; the attested original
  mtime is the timeline entry above — the sha256 is the identity that matters

## Errata (disclosed, not silently fixed — the skill's own change protocol)

- Frozen protocol §2 says "the eval prompts and assertions **above** are frozen": the
  assertions are not printed in that document; they live in `evals/evals.json` (sha256
  above). The frozen text is immutable, so this is disclosed here instead of edited.
- `benchmark.json` `runs_per_configuration` was `3` in an earlier revision, which was true
  only for eval-0; corrected to a per-eval map {eval-0: 3, eval-1: 1, eval-2: 1}.

## Known limits

- n = 3 per cell on the hands-on eval; one run per cell on the two advisory evals —
  directional evidence, declared exploratory in the frozen protocol.
- Runs executed on a single author machine (Windows, Python 3.11); graders were
  independent agent sessions, but the environment is not distributed.
