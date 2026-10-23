---
name: park-idea
description: Park an out-of-scope idea in docs/backlog.md so it isn't lost and doesn't derail the current week. Use this whenever the user or Claude suggests an improvement, feature, optimization, or new tool that belongs to a later week of the build plan, a stretch goal, or the spec's out-of-scope list — including "it would be cool to...", "we should eventually...", "what about adding Flink/ML/a front end/AWS", or any time the CLAUDE.md scope rule ("if a task would pull in work from a later week, say so and ask") applies. Also use it to review or prune the backlog.
---

# Park idea

This project has a history of stalling from scope creep. Good ideas are the main source of it, because they're tempting to act on immediately. Parking an idea is a way of saying yes to it later so that it's easy to say no to it now. The point is speed: capture it in a few lines, then get back to the current task.

## Steps

1. **Place it.** Read the spec's build plan (`docs/ercot-portfolio-project.md`) and the "Current phase" line in CLAUDE.md. Decide where the idea fits:
   - a specific later week (cite the checkbox it belongs with, if any);
   - a stretch goal (after week 8);
   - the out-of-scope list (ML or forecasting, custom web front end, cloud deployment, Terraform/Kubernetes) — this list is binding until the user lands a job;
   - unsorted, if it doesn't clearly fit anywhere.

   If it actually belongs to the *current* week, it isn't a parking case — say so and suggest adding it to this week's tasks instead (see `plan-and-progress`).

2. **Check for duplicates.** If the backlog already has it, propose adding the new angle to the existing entry instead.

3. **Propose, then wait.** Write nothing until approved:

   ```
   **Proposed doc update** (park-idea)
   - docs/backlog.md › Stretch: add "Rewrite the streaming job in Flink"
   <exact entry text>
   Apply this? (yes / edit / skip)
   ```

4. **Return to the task** in the same message. Don't elaborate on the idea's design; that's for when it's picked up.

## `docs/backlog.md` format

Create the file on first use with these sections, in this order:

```markdown
# Backlog

Ideas deferred from the active week. Pulled into a week's plan by `plan-and-progress`, which removes them from here.

## Later in the build plan

### Week 5
### Week 6
### Week 7
### Week 8

## Stretch (after week 8, pick one)

## Out of scope (binding until job landed)

## Unsorted
```

Entry format:

```markdown
- **Kafka topic retention sized to laptop downtime** — set retention to cover the longest expected gap so the stream can resume from offsets. *Why deferred:* Kafka isn't added until week 6. *Fits:* week 6, "Spark Structured Streaming job from Kafka". *Added:* 2026-10-22
```

Only keep headings for weeks still ahead; drop a week's heading once that week closes and its items have been pulled in or re-parked.

## Reviewing the backlog

When asked to review the backlog, or when a week is being planned, list the items targeting the upcoming week and flag any that now look unnecessary. Propose removals the same way as additions.
