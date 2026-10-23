---
name: capture-lesson
description: Turn a user correction into a durable project rule or lesson. Use this whenever the user corrects Claude, rejects or redirects an approach, or says things like "no", "don't", "actually", "that's wrong", "I told you", "stop doing X", "we always do Y" — and also when Claude notices its own mistake. Decides whether the correction is a one-off or a generalizable rule, then proposes an update to CLAUDE.md, docs/lessons.md, or user memory. Use it even for small or mid-task corrections; those are the ones most often lost.
---

# Capture lesson

Corrections are the most valuable signal in this project: each one marks a place where Claude's default behavior didn't match what the user wanted or what the stack actually does. If a correction isn't written down, it gets repeated next session. The goal is to turn a specific incident into a general principle, put it where it will actually be read, and do it without derailing the current task.

## Steps

1. **Restate the correction in one line**, so the user can see it was understood ("You're saying raw tables shouldn't drop any source columns, even ones we don't use yet").

2. **Classify it.** Pick the one destination that fits best:

   | Kind | Example | Destination |
   | --- | --- | --- |
   | One-off, specific to this task | "Use the 2024-07-15 file, not the 14th" | Nothing. Say so in one line and move on. |
   | Project rule or convention | "Never put business logic in the Spark ingestion job" | `CLAUDE.md`, under the matching section (Scope rules, Working style, Data conventions, Git, Environment notes) |
   | Technical lesson about the stack | "Trino can't see the table because Spark wrote it to a different catalog" | `docs/lessons.md` |
   | Personal preference about how Claude works in any project | "Keep your summaries shorter" | User memory (the auto-memory directory), not the repo |

   The test for one-off vs. rule: would the same mistake plausibly happen again in a different task? If yes, it's a rule or lesson.

3. **Generalize.** Write the abstract principle, not the incident, and include a short *why*. A rule with a reason lets future-Claude handle cases the rule didn't anticipate.
   - Weak: "Don't rename `SettlementPointPrice` to `price` in raw_rt_prices."
   - Strong: "Raw tables keep source column names as-is. Renaming belongs in dbt staging models. Why: raw is the replayable record of what ERCOT sent; renames there make reprocessing and debugging harder."

4. **Check for duplicates and conflicts.** Read the target file first. If a rule already covers this, propose sharpening that rule rather than adding a near-copy. If the correction contradicts an existing rule, show both and propose which one wins — the user's latest correction usually does, but say so explicitly.

5. **Propose, then wait.** Never write before the user approves. Use this block:

   ```
   **Proposed doc update** (capture-lesson)
   - CLAUDE.md › Data conventions: add a rule that raw tables keep source column names
   <exact text to add, or a before/after for an amended rule>
   Apply this? (yes / edit / skip)
   ```

   On "edit", revise and show again. On "skip", drop it without argument.

6. **Return to the task.** One short proposal, then back to work. Don't turn a correction into a long discussion.

## `docs/lessons.md` format

Create the file the first time it's needed with a one-line intro ("Technical lessons learned building this pipeline, newest first."). Add entries at the top:

```markdown
## 2026-10-22 — Spark and Trino must share one catalog name
**Tags:** iceberg, trino, spark
**Lesson:** Spark and Trino see the same Iceberg tables only when both point at the same REST catalog URI and warehouse. A table written under a different catalog is invisible to the other engine, with no error — just "table not found".
**Why it matters:** This is the day-1 integration risk; silent mismatches waste hours.
**Triggered by:** Trino couldn't find `raw.rt_prices` after the first Spark write.
```

Lessons double as interview material, so write them so they'd make sense to someone who wasn't there.

## Edge cases

- **Several corrections at once:** handle them in one proposal block, one bullet each.
- **The user is frustrated:** acknowledge it briefly, fix the actual problem first, then propose the lesson.
- **A correction to the spec itself** (e.g. changing the plan): don't edit the spec quietly. Propose it as a spec change with the reason, and if it's an architectural choice, hand off to `record-decision`.
