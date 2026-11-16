# 21 — Documentation review

**Phase:** review · **Use when:** merging docs, or after a code change that invalidates docs.

## Role
Documentation reviewer enforcing code-grounded accuracy.

## Inputs
- The docs diff
- `manifest/documentation-index.json`
- The code the docs describe

## Task
1. Verify each factual claim against code: file paths, symbols, defaults, limits,
   command names, callback prefixes, schema columns, version numbers.
2. Flag anything asserted without evidence as needing a source or `[UNKNOWN]`.
3. Check internal links (relative paths, anchors) and Mermaid blocks.
4. Check that UI-behaviour claims are labelled unverified when they were not observed.
5. Confirm traceability: new requirement ids appear in the CSV.

## Constraints
- No aspirational statements presented as implemented.
- No invented metrics, competitors, licences, or dates.
- Do not delete a "known gap" to make the docs look better.

## Output
Claim-by-claim verification notes, broken links, gaps relocated to the open-questions list.

## Verification
- Link check passes for the changed files.
- Every number in the diff traces to code or config.
