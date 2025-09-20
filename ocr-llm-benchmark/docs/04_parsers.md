# 04 — Parsers & Adapters

**Goal:** Add models quickly by subclassing `adapters/base.py`.

**Steps:**
- Copy `adapters/example_openai.py` or `adapters/example_ollama.py`.
- Implement: `name`, `supports_images`, `max_image_res`, `infer(doc_bytes, prompt, ...)`.
- Return: parsed JSON and raw text, plus timing + token stats.

**Where it can fail & fixes:**
- *Image input required but PDF given* → Use `tools/pdf_to_images.py` to rasterize first.
- *Large PDFs* → Downscale with controlled sampling; record input pixels used.
