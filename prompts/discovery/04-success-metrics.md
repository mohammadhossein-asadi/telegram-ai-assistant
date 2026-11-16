# 04 — Success metrics

**Phase:** discovery · **Use when:** defining how a feature or release will be judged.

## Role
Engineer who must be able to measure the outcome from existing data.

## Inputs
- `docs/product/product-dna.md` (M-01…M-06)
- `usage_logs` schema (`docs/database/data-dictionary.md`)
- `docs/devops/monitoring-logging.md`

## Task
1. For the change under discussion, define 1–3 metrics.
2. For each: definition, data source, query, target, and what a bad result implies.
3. Prefer metrics computable from `usage_logs` or `messages` without new instrumentation.
4. If a metric needs telemetry the project lacks, say so and mark it as a prerequisite.
5. State explicitly which metrics cannot be measured today.

## Constraints
- No invented baselines. Write "baseline: not measured" when true.
- Targets are proposals, labelled as such.
- Do not add analytics SDKs; the project has none and needs none for these metrics.

## Output
Metric table + SQL for each measurable metric + a "needs instrumentation" list.

## Verification
- Each SQL query runs against the schema in `artifacts/database/schema.sql`.
- No metric depends on a field that does not exist.
