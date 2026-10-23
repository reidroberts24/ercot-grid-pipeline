---
name: record-decision
description: Write a decision record in docs/decisions/ for a key architectural or technical choice in the ERCOT pipeline. Use this whenever we settle a choice between real alternatives (a tool, config, data layout, partition spec, idempotency or dedup strategy, streaming setting, dbt materialization, and so on), whenever work touches a row of the spec's "hard parts" table, or when the user says "let's go with", "why did we choose", "document this decision", "ADR", or "decision record". In this repo, use this skill instead of the generic /adr skill.
---

# Record decision

Decision records are the backbone of this project's interview story: the spec's "hard parts" table says each one should become a short decision record, and the week-8 README draws on them. A good record lets the user explain, months later and under interview pressure, what the problem was, what else was considered, and why this option won.

## When it's worth a record

Write one when there were genuinely competing options and the choice has consequences: anything in the hard-parts table (DST handling, idempotency, late data, compaction, partitioning, SCD, grain mismatch, data tests, recovery), choosing between tools or libraries, or a convention many files will follow. Skip it for trivially reversible implementation details — mention it in passing instead.

## Steps

1. **Draft from the conversation.** Most of the content is already in what was discussed. Ask only for pieces that are genuinely missing (usually: an option the user rejected without saying why). Don't run a long interview.

2. **Number it.** List `docs/decisions/` and take the next four-digit number. File name: `NNNN-short-kebab-slug.md`, e.g. `0003-merge-on-natural-key-for-dedup.md`.

3. **Superseding, not rewriting.** An accepted record is history. If a decision changes, write a new record, set the old one's status to `Superseded by NNNN`, and link both ways. The fact that the decision changed, and why, is itself a good interview story.

4. **Propose, then wait.** Show the full record and the index row; write nothing until approved:

   ```
   **Proposed doc update** (record-decision)
   - docs/decisions/0003-merge-on-natural-key-for-dedup.md: new record — dedup the cleaned layer with Iceberg MERGE on (settlement_point, interval_start_utc)
   - docs/decisions/README.md: add index row
   <full record text>
   Apply these? (yes / edit / skip)
   ```

5. **Link it.** If a related lesson or learning note exists, reference it under Related.

## Record template

```markdown
# NNNN. <Decision as a short statement>

- **Status:** Accepted   <!-- Proposed | Accepted | Superseded by NNNN -->
- **Date:** YYYY-MM-DD
- **Hard part:** <row from the spec's hard-parts table, or "none">

## Problem
What forced a choice, in 2–4 sentences. Include the constraint that made it non-obvious.

## Options considered
1. **<Option A>** — pros; cons.
2. **<Option B>** — pros; cons.
3. **<Option C>** — pros; cons.

## Decision
What we chose, concretely (table, config key, file).

## Why
The reasoning that tipped it. Name the tradeoff explicitly.

## Consequences
What this makes easier, what it makes harder, and what we'd revisit at 10x scale.

## How I'd explain it in an interview
3–4 sentences, first person, plain language. Problem → options → choice → tradeoff.

## Related
Files, other decisions, lessons, learning notes.
```

Keep the record to about one screen. The options and the "why" are the parts that matter most; don't pad the rest.

## Index: `docs/decisions/README.md`

Create it on first use:

```markdown
# Decision records

| # | Decision | Hard part | Status | Date |
| --- | --- | --- | --- | --- |
| [0001](0001-slug.md) | ... | ... | Accepted | YYYY-MM-DD |
```

Remove `docs/decisions/.gitkeep` once the first real record exists (include that in the proposal).
