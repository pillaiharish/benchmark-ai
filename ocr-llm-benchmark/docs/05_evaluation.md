# 05 — Evaluation & Scoring

**Goal:** Compare model outputs to ground-truth schemas.

**Metrics:**
- **Schema validity** (JSON matches schema; required keys present)
- **Cell-wise accuracy** (string match / fuzzy match)
- **Structure accuracy** (row/column counts, merges)
- **Robustness** (handles two tables, edge-to-edge, etc.)

**Where it can fail & fixes:**
- *Ambiguous headers* → Provide hints in prompt; multi-turn allowed for VLMs.
- *Merged cells* → Use `rowspan`/`colspan` fields in the target schema.
