# 06 — Reporting

**Goal:** Create consistent reports per run.

- `summarize_run.py` produces tables and small charts.
- Compare multiple runs to track regressions.

**Where it can fail & fixes:**
- *Missing files in a run* → Re-run only failed items using `--resume` flag.
