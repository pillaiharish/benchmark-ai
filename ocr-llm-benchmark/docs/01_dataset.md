# 01 — Synthetic Dataset (PDF) Generator

**Goal:** Generate a stable set of PDFs covering table edge-cases.

## Scenarios
1) Centered table on the page
2) Full-width table (edge-to-edge on a single page)
3) Two tables, same column count, separated by a thin line
4) Two tables, first has fewer columns, second has more
5) Row merges/splits
6) Column merges/splits

**Command:**
```bash
python scripts/generate_pdfs.py --out ./data/pdfs
```

**Verification:**
- Check `data/pdfs/manifest.json` lists all files with deterministic hashes.
- Open PDFs and visually confirm layout.
- Run `python tools/inspect_pdf.py --file data/pdfs/SCENARIO.pdf` to log page size (A4 or not).

**Where it can fail & fixes:**
- *Missing fonts on some systems* → Use built-in Helvetica; avoid custom TTF unless embedded.
- *Merged cells clipping* → Ensure cell paddings and `span` math are correct; see code comments.
- *Vector PDF has no "DPI"* → DPI applies when rasterizing. We log page size in points/mm and the **input pixels** used by the VLM (see metrics spec).

