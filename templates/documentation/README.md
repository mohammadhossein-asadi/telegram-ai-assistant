# Documentation templates

| File | Use for |
| --- | --- |
| `document-template.md` | Any engineering doc: design, guide, reference, runbook |
| `../adr/ADR-template.md` | Architecture decisions |

## Conventions used across this repository

| Convention | Rule |
| --- | --- |
| File names | `kebab-case.md`, one topic per file |
| Heading levels | one `#`, sections `##`, no skipped levels |
| Diagrams | Mermaid in `artifacts/diagrams/*.mmd`, embedded or linked |
| Code references | backticked paths, e.g. `src/services/chat/engine.py` |
| Requirements | `FR-*`, `US-*`, `BR-*`, `NFR-*` ids from `docs/product/` |
| Unknowns | `[UNKNOWN — USER INPUT REQUIRED]` — never a guess |
| Verification | every doc that asserts behaviour says how to check it |
| Status | current behaviour vs proposed change must be distinguishable |

## Writing checklist

- [ ] Claims trace to code, config, artifact or a cited source
- [ ] Internal links resolve (relative paths, valid anchors)
- [ ] Mermaid blocks are syntactically valid
- [ ] Known gaps are stated, not hidden
- [ ] No secrets, tokens, or user data
- [ ] Added to `manifest/documentation-index.json`
