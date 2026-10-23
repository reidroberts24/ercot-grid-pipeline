---
name: learning-notes
description: Save interview-prep notes on data engineering concepts to docs/learning/. Use this whenever a Spark, Kafka, Iceberg, Trino, dbt, Airflow, SeaweedFS, or Superset concept comes up for the first time in this project (e.g. watermarks, hidden partitioning, MERGE INTO, snapshots, checkpoints, consumer offsets, incremental models, SCD snapshots), when the user asks "why does X work this way", "explain X", or "how does X work under the hood", or when we hit a gotcha in one of these tools that's worth remembering.
---

# Learning notes

The user is building this project to become fluent in the stack a big-tech data engineering team uses, and to defend it in interviews. Explanations in chat are gone after the session; a short note tied to how *this* project uses the concept is what they'll reread before an interview. Notes should be the kind of thing you'd want on one page the night before a system-design round.

## Steps

1. **Explain in chat first**, briefly: what the concept is and why it works that way (per CLAUDE.md's working style). The note is a durable copy, not a substitute for answering.

2. **Check for an existing note.** Look in `docs/learning/<tool>/`. If one covers the concept, propose an update (a new gotcha, a new usage, a sharper interview answer) rather than a new file.

3. **Propose, then wait.**

   ```
   **Proposed doc update** (learning-notes)
   - docs/learning/spark/watermarks.md: new note on event-time watermarks for late ERCOT intervals
   <full note text>
   Apply this? (yes / edit / skip)
   ```

4. **Don't over-collect.** One note per concept that matters in interviews or bit us in practice. Basic syntax ("how to select a column") doesn't need a note.

## Location and naming

`docs/learning/<tool>/<concept-slug>.md`, where `<tool>` is one of `spark`, `kafka`, `iceberg`, `trino`, `dbt`, `airflow`, or `general` (for cross-cutting topics like idempotency or exactly-once). Create folders as needed. If `docs/learning/README.md` exists, add a line to it; create it once there are three or more notes.

## Note template

Keep it under about 60 lines. Concrete beats comprehensive.

```markdown
# <Concept>

**Tool:** Spark Structured Streaming · **First used:** week 6, `spark/streaming/rt_prices.py`

## What it is
1–2 sentences.

## Why it works this way
The design reason — the problem it solves and the tradeoff it makes. This is the part interviewers probe.

## How this project uses it
Specific to ERCOT: which job, which table, which setting and why that value.

## Gotchas
Things that went wrong or surprised us, with the fix. Link to `docs/lessons.md` entries if relevant.

## Interview questions
- **Q:** <likely question>
  **A:** <2–3 sentence answer, grounded in this project>
- **Q:** ...

## Further reading
- <official doc link>
```

Only fill "How this project uses it" with things that are actually true in the repo; if the concept is being introduced before it's used, say "Planned for week N" instead of inventing details.
