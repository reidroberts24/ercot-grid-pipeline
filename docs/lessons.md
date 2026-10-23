# Lessons

Technical lessons learned building this pipeline, newest first.

## 2026-10-22 — A settlement point name alone isn't a unique key
**Tags:** ercot, data-model, idempotency
**Lesson:** In NP6-905-CD, each load zone appears twice per interval: once as type `LZ` and once as `LZEW` (energy-weighted), with different prices. The natural key is (settlement point, settlement point type, delivery date, hour, interval), not settlement point plus time.
**Why it matters:** A week-5 `MERGE INTO` keyed only on point and time would quietly collapse two different prices into one.
**Triggered by:** Probing settlement point types while building the API client.
