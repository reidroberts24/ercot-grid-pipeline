---
name: sprint-plan
description: Gate before every new piece of implementation work in the ERCOT pipeline. Analyzes the current state of the repo and stack, checks it against the spec's goals for drift, and proposes a scoped plan for the next coding sprint, then waits for approval before any code is written. Use this whenever we're about to start a new task, step, or week — "let's start on X", "next step", "let's move on", "what's next", "ready for the next task", right after a task is marked done, or when Claude is about to begin building something new — even if the next task seems obvious.
---

# Sprint plan

Projects drift one reasonable step at a time: a "for now" shortcut that never gets paid back, a tool added because it was convenient, a polished component nothing downstream uses yet. Each step looks fine locally; the drift only shows when you compare the whole against the goal. This skill does that comparison at every task boundary, while it's still cheap to correct course, and turns the next task into a sprint plan the user approves before any code is written.

The goal it protects, from `docs/ercot-portfolio-project.md`: a pipeline that answers the spec's four questions on the agreed stack, built thin-slice first, and — just as important — a learning project that gives the user real, defensible depth in Kafka, Spark, Iceberg, Trino, and dbt.

## Step 1: Snapshot the current state

Gather facts, not impressions. Read or run:

- `CLAUDE.md` (Current phase, rules) and the spec's build plan checkboxes.
- `docs/weeks/week-NN.md` for the current week: which tasks are done, which is next.
- `git log --oneline` since the last sprint entry in the week file, and `git status` for uncommitted work.
- `docs/decisions/README.md`, `docs/backlog.md`, `docs/lessons.md` — skim for anything that bears on the next task.
- The repo tree (top two levels) to see what actually exists.
- `docker compose ps` if the next task touches the running stack.

Summarize in 3–6 bullets: what works end to end right now, what was built since the last sprint, anything uncommitted or half-done.

## Step 2: Drift check

Compare the current state and the proposed next task against the goal. For each check, mark ✅ on track, ⚠️ drifting (say how), or — not applicable:

| Check | Question to answer |
| --- | --- |
| Goal link | Which of the four questions, or which MVP piece, does this task move forward? If none, why are we doing it? |
| Thin slice | Does data already flow end to end in some crude form? If not, does this task help close the gap, or polish one stage further? |
| Phase scope | Is all of it in the current week's plan? Anything from a later week gets parked, not built. |
| Stack | Only tools in the spec's stack table (or approved in a decision record)? List any new libraries or services. |
| Conventions | UTC storage, raw close to source, idempotent loads, stated grain, extreme prices allowed — will this task respect each? |
| Shortcuts owed | Any "for now" choices (in decisions, the week file, or code comments) that are now due, or that this task makes harder to undo? |
| Spec vs. reality | Has anything built diverged from the spec without a decision record or spec update? |
| Learning value | Will the user understand what's built well enough to explain it in an interview? Which concepts does this sprint teach? |

Be honest rather than reassuring: one real ⚠️ is worth more than eight ✅. If something has drifted, propose the correction (park it, record a decision, update the spec, or pay back the shortcut now) as part of the plan.

## Step 3: Propose the sprint

Use this structure. Keep it to one screen; the steps are the part that matters.

```markdown
## Sprint: <task name from the week file>

**Why now:** one or two sentences — what it unblocks or which risk it retires.
**Serves:** <spec question(s) / MVP piece>

### Current state
- ...

### Drift check
| Check | Status | Note |
| --- | --- | --- |

### Scope
**In:** ...
**Out (parked or later):** ...

### Steps
1. <small, verifiable step> — *check:* <how we'll know it worked>
2. ...

**Files:** new/changed files.
**Done when:** the week file's criterion, made concrete.
**Concepts:** what the user will learn, and where a learning note is worth writing.
**Risks:** what could go wrong and the fallback.
**Records:** decision records, lessons, or benchmarks this sprint should produce.
**Questions for you:** only real decisions the user needs to make (or "none").
```

Order the steps so each one ends in something runnable and checked. Prefer the simplest version that works and name the tradeoff when choosing one approach over another.

## Step 4: Wait for approval

Write no code until the user approves the plan. On "edit", revise and show again. Once approved:

1. Propose adding a compact sprint entry under the task in the week file (date, scope in/out, any ⚠️ and how it was resolved), so the next drift check can see what was decided. Like every doc change, show it and wait for a yes.
2. Start on step 1 of the plan.

If the work reveals that the plan was wrong mid-sprint (a blocker, a tool that doesn't work, a scope surprise), stop and say so rather than silently changing course; a revised plan is cheap, quiet drift isn't.

## Relationship to other skills

- `plan-and-progress` owns the task list and checkboxes; this skill takes the next task from it and plans *how*. If there's no week file yet, run `plan-and-progress` first.
- Drift findings hand off to the owning skill: out-of-scope work → `park-idea`, an unrecorded choice → `record-decision`, a spec divergence → propose the spec edit.
