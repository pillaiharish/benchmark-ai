# 03 — Metrics (Beyond TPS)

We capture:
- **TTFT** (time to first token)
- **TPOT** (time per output token)
- **Token Generation Time** (first→last token)
- **Total Latency (E2EL)** = TTFT + Token Generation Time
- **P50 / P99** latencies
- **RPS / TPS**
- **Goodput** (% meeting SLA; timeouts excluded)
- **Throughput vs Latency** (batch size effects)
- **Token counts**: input/output tokens (as reported by the model or estimated)
- **Document geometry**: page size (A4 or not), width/height (points, mm)
- **Input pixels**: if model requires image rasterization; we log W×H pixels fed
- **Model-declared image limits**: max resolution, DPI notes if stated by provider

**Verification:**
- `runs/*/metrics_summary.json` contains P50/P90/P99 and SLA Goodput.

**Where it can fail & fixes:**
- *No token usage from provider* → Estimate via tokenizer libs; mark as estimated.
- *Stream tokenization ambiguity* → Use consistent tokenizer per model family.
