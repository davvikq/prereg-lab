# Prereg-Lab Case Studies

Four factual episodes from a preregistered local-LLM inference lab (experiments E01-E08 on
speculative decoding, pre-generation latency, and KV-cache behavior). Each shows one rule
of the skill doing real work. Read once before your first experiment; the point is not
these specific setups, it is how the same temptations recur in every domain.

## 1. The confound discovered mid-run (fix nothing, register everything)

The frozen decisions said all configurations run at 6 threads (set by a pilot). Weeks
before the verdict, while checking plan files, the agent found the run plan had
`draft_threads: 8` for three configurations - the plan was written before the pilot
decision and never updated. Three blocks were already measured at 8 threads.

The tempting move: quietly fix the plan for remaining blocks, or restart everything.
Either destroys comparability. What the discipline demanded:

- Registry entry with facts: which configurations, which blocks, when, why
- Blast-radius analysis: the confound biases only the draft-quant contrast (8 threads on a
  hybrid CPU slows draft generation specifically); the primary contrast and the
  target-quant contrasts were structurally unaffected - both sides at 6 threads
- Affected contrasts marked CONFOUNDED - descriptive only, excluded from verdict-deciding
- A separate follow-up experiment pre-planned to re-measure the affected contrasts cleanly

The lesson: a mid-run confound is not an emergency, it is a bookkeeping event. The
experiment survives it; a quiet patch does not survive an audit.

## 2. The session that died mid-experiment (survival by construction)

A long measurement run was launched as a child of the agent session. The session ended;
the run died with it, mid-block. No raw loss beyond the partial block - but the next run
was launched detached (its own process group), and resume was done by completeness:
inspect raw files, skip fully completed blocks, restart only the partial one, with block
order regenerated from the same seed so the resumed plan matched the original.

The lesson: assume your own session will die. Detached launch + raw-per-request files +
deterministic order turns a disaster into a restart. Resuming "fresh with improvements"
instead would have quietly mixed two protocols into one dataset.

## 3. The verdict that was not revised (even when its rationale broke)

An early experiment produced a frozen verdict: the mechanism under test failed, 0
successes under the strict criterion. Later diagnostics showed why - the criterion itself
was subtly wrong for the system under test (greedy decoding depended on KV history the
criterion assumed away), plus one implementation bug. The verdict still stood, exactly as
frozen, because verdicts are lookup results, not beliefs.

What happened instead: post-hoc diagnostics published separately, the failure decomposed
(criterion vs bug vs mechanism), and a NEW preregistration written for the follow-up with
a corrected criterion - which then ran and produced its own frozen verdict, later
replicated by a third preregistered experiment.

The lesson: when a verdict's rationale turns out wrong, you do not edit the verdict; you
disclose and run a new experiment. The chain of frozen verdicts is the lab's memory. A
revised verdict would have made the memory a narrative.

## 4. The honest downgrade (freeze after data exists = not preregistered)

One late experiment had a protocol and analysis code written before the first measurement,
but the formal freezing step (hashing, frozen copy) happened after some data existed. The
discipline demanded this be disclosed, not laundered: the report and registry state that
the result qualifies as "confirming by pre-written code", a weaker class of evidence than
preregistered - with the exact timeline given so any reader can judge.

The lesson: the difference between preregistered and prewritten-but-unfrozen is real, and
the only way to keep the strong label strong is to admit when it does not apply. A
methodology that never downgrades its own evidence is marketing, not science.
