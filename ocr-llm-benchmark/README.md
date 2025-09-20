# OCR & LLM/VLM Parsing Benchmark

A reproducible benchmark to compare SLMs/LLMs/VLMs on *document parsing* tasks (especially tables).
You can add a newly released model and re-run the same suite to compare outputs, latency, and quality.

## Key Ideas
- **Deterministic synthetic PDFs**: We generate the same set of PDFs on every run for apples-to-apples comparisons.
- **Adapters**: Each model is a small Python class implementing a common interface (`adapters/base.py`), so you can plug models in quickly.
- **Metrics beyond TPS**: We log TTFT, TPOT, P50/P99, Goodput, throughput vs latency trade-offs, token usage, page geometry (A4 or not), and effective input pixels.
- **Ground-truth schemas**: We store expected table structures to evaluate JSON/table outputs.

## Quickstart
```bash
# 1) Create myenv
python3 -m venv myenv && source myenv/bin/activate
pip install -r requirements.txt

# 2) Generate synthetic PDFs (deterministic)
python scripts/generate_pdfs.py --out ./data/pdfs

# 3) Run a smoke benchmark with the Dummy adapter
python scripts/run_benchmark.py --models Dummy --pdf-dir ./data/pdfs --out ./runs/latest

# 4) View a run summary
python scripts/summarize_run.py --run ./runs/latest
```

## Repo Layout
- `docs/` — task breakdown, metrics, known failure modes and fixes
- `scripts/` — PDF generation, runners, summarizers
- `adapters/` — plug-in interfaces for models (LLM/VLM/SLM) + examples
- `data/` — generated PDFs and ground-truth
- `runs/` — per-run metrics and outputs
- `prompts/` — extraction prompts and JSON schema
- `tools/` — helper utilities

See `docs/01_dataset.md` to start.
