# 02 — Benchmark Runners

**Goal:** Orchestrate model calls with timers + retries to collect latency + token metrics.

**Command:**
```bash
python scripts/run_benchmark.py --models Dummy,OpenAI,Ollama --pdf-dir ./data/pdfs --out ./runs/2025-09-20
```

**Verification:**
- Inspect `run_config.json` and `results/*.jsonl`.
- Confirm each model produced JSON/table for each scenario.
- Ensure error budget & retries recorded.

**Where it can fail & fixes:**
- *API keys not set* → Check env vars in adapter docs.
- *HTTP 429 / rate limits* → Backoff + jitter in adapters.
- *Streaming parsing issues* → Fallback to non-stream mode for metrics sanity.
