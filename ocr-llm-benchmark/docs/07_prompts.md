# 07 — Prompts & Schemas

**Extraction Prompt (generic):**
```
You are an expert table extractor. Given a page, extract every table into JSON.
For each table: rows -> list[list[str]], header_indices, merges: list[{row, col, rowspan, colspan}].
Return strict JSON only:
{
  "tables": [
    {
      "rows": [["H1","H2"],["A","B"]],
      "header_indices": [0],
      "merges": [{"row":0,"col":0,"rowspan":1,"colspan":1}]
    }
  ]
}
```
**Table (Markdown) Prompt (alternative):**
```
Return tables in GitHub-flavored Markdown. One table per block. No explanation text.
```

**Where it can fail & fixes:**
- *Model returns prose around JSON* → Add "Return ONLY JSON". Use regex to extract JSON.
- *Incorrect merges* → Ask model to first list detected spans, then render tables.
