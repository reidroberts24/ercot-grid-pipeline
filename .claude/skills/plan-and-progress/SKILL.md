---
name: plan-and-progress
description: Plan and track the ERCOT pipeline's weekly build. Use this to break the current week of the spec's build plan into concrete tasks, to decide what to work on next, to mark tasks and spec checkboxes done when work finishes, and to close out a week and move to the next (retro, carry-overs, updating the "Current phase" line in CLAUDE.md). Trigger on "what's next", "what should I work on", "plan this week", "we finished X", "mark that done", "where are we", "let's move to week N", or whenever a piece of planned work has just been completed and verified.
---

# Plan and progress

The spec's build plan is deliberately coarse: three to five checkboxes per week. This skill turns those into session-sized tasks, keeps a visible record of progress, and enforces the project's main discipline — thin slice first, and only the current week's work.

Sources of truth:
- `docs/ercot-portfolio-project.md` — the build plan checkboxes.
- `CLAUDE.md` — the "Current phase" line.
- `docs/weeks/week-NN.md` — the task breakdown for each week (created by this skill).
- `docs/backlog.md` — deferred ideas, some targeted at specific weeks.
- `docs/lessons.md` — lessons that may affect how a task should be done.

Pick the mode from the request.

## Mode: plan the week

1. Read the current week's checkboxes, any backlog items under that week, and lessons relevant to it.
2. Break each checkbox into tasks of roughly one working session. For each task, give:
   - a clear **done when** criterion that can be checked (a query returns rows, a test passes, a restart produces no duplicates);
   - the **concept it teaches** (e.g. "Iceberg REST catalog", "Spark DataFrame writes"), since the project exists to build depth in the stack.
3. Order tasks so data flows end to end as early as possible. A crude version of every stage beats a polished first stage.
4. Flag anything that would pull in later-week work and offer to park it instead.
5. Propose the week file (format below), and wait for approval before writing.

## Mode: update progress

When work finishes *and has been verified* (ran it, saw the output), propose ticking the task in the week file. When all tasks under a spec checkbox are done, also propose ticking the spec checkbox. Don't tick things on the strength of "it should work".

## Mode: what's next

Read the week file and recommend one next task, with one or two sentences on why it's next (usually: it unblocks the end-to-end path, or it retires the biggest risk). If there's no week file yet, offer to plan the week first. Once the user wants to start it, hand off to `sprint-plan` before writing any code.

## Mode: close the week

1. Check every spec checkbox for the week. For anything unfinished, ask: carry it into next week, or park it?
2. Propose a short retro at the bottom of the week file: what went well, what was hard, what to change. Keep it to a few bullets each — it feeds the week-8 write-up.
3. Propose updating the CLAUDE.md "Current phase" line to the next week (use the spec's week title).
4. Offer to plan the new week.

**Week 8 is different:** it's write-up, then stop. When closing week 7, remind the user of that, and don't plan stretch-goal work until the README is done.

## Week file format: `docs/weeks/week-NN.md`

```markdown
# Week 4: the thin slice

**Goal:** one day of hub and load-zone prices flowing from the API to a dbt model queried in Trino.

## Spec item: Bring up the core stack...

- [ ] **Compose file with SeaweedFS, REST catalog, Spark, Trino** — *done when:* all four containers healthy. *Teaches:* how the Iceberg REST catalog decouples engines from storage.
- [ ] **Day-1 check: write an Iceberg table from Spark, read it from Trino** — *done when:* `SELECT count(*)` in Trino matches the Spark write. *Teaches:* catalog and S3 configuration shared across engines.

## Spec item: Pull one day of prices...

- [ ] ...

## Retro
<!-- filled in at week close -->
```

## Proposing changes

Every write goes through a proposal first:

```
**Proposed doc update** (plan-and-progress)
- docs/weeks/week-04.md: tick "Day-1 check" (verified: Trino count = 96 rows)
- docs/ercot-portfolio-project.md: tick week 4 item 1 (all tasks done)
<exact diffs>
Apply these? (yes / edit / skip)
```

Show the actual diff for spec and CLAUDE.md edits, since those files steer every session.
