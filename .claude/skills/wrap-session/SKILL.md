---
name: wrap-session
description: End-of-session sweep for the ERCOT pipeline. Reviews the whole conversation for corrections, decisions, out-of-scope ideas, finished work, and new concepts that weren't captured yet, proposes all the doc updates in one batch, applies the approved ones, and suggests a commit. Use when the user says "/wrap-session", "let's wrap up", "done for today", "end of session", "that's it for now", or is clearly stopping work.
---

# Wrap session

The other project-memory skills are meant to fire in the moment, but in-the-moment capture misses things, especially mid-flow. This sweep is the safety net: one pass over the session so nothing worth keeping is lost, presented as a single batch the user can approve in one go.

## Steps

1. **Scan the whole conversation** and collect candidates in five buckets. For each, check whether it was already captured this session (don't re-propose things already written).

   | Bucket | Look for | Skill whose format to follow |
   | --- | --- | --- |
   | Lessons | corrections, redirections, mistakes Claude noticed | `capture-lesson` |
   | Decisions | choices between real alternatives, hard-parts work | `record-decision` |
   | Parked ideas | "later", "eventually", things deferred for scope | `park-idea` |
   | Progress | tasks finished and verified, a week ready to close | `plan-and-progress` |
   | Concepts | stack concepts explained for the first time, gotchas | `learning-notes` |

2. **Read the relevant skill files** in `.claude/skills/<name>/SKILL.md` for any bucket that has candidates, so each item uses the right format and destination.

3. **Present one consolidated proposal**, grouped by bucket and numbered so the user can approve selectively. Lead with the synopsis; keep full text short or collapsible-by-default (show full text for CLAUDE.md and spec changes, since those steer every session):

   ```
   **Session wrap-up: proposed doc updates**

   Lessons
   1. CLAUDE.md › Data conventions: raw tables keep source column names
   Decisions
   2. docs/decisions/0002-rest-catalog-over-hive.md: new record
   Parked
   3. docs/backlog.md › Week 6: size Kafka retention to laptop downtime
   Progress
   4. docs/weeks/week-04.md: tick "Day-1 check"
   Concepts
   5. docs/learning/iceberg/rest-catalog.md: new note

   <full text for each>

   Apply all, some (e.g. "1, 3, 4"), or none?
   ```

   If a bucket is empty, leave it out. If everything is empty, say "Nothing new to capture" and skip to step 5.

4. **Apply the approved items** exactly as shown. If the user edits one, revise and confirm just that item.

5. **Suggest a commit.** Propose message(s) in the CLAUDE.md style (`docs: record decision on REST catalog`, `spark: batch load one day of hub prices`), separating code and docs commits if both changed. Don't commit without the user saying so. Never stage `.env`, data files, checkpoints, or MinIO volumes. If the directory isn't a git repo yet, mention it and offer to run `git init` — don't run it unprompted.

6. **Leave a one-line pointer for next time**, like "Next up: <next task from the week file>." This makes the next session start fast.
