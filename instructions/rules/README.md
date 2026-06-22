# Pipeline Workflow — Aturan Eksekusi

Workflow utama:

```
User Input
  → [1] Local LLM (Ollama) — enrich → klasifikasi intent/domain/complexity
  → [2] Check Rule — PLAN? BLOCK dan minta /workmode build. BUILD? Lanjut.
  → [3] Select Skill + Model — berdasarkan intent + complexity
  → [4] Execute — AI model eksekusi dengan aturan presisi
```

## File Index

| # | File | Isi |
|---|------|-----|
| 1 | `01-pipeline-flow.md` | Pipeline enrichment + klasifikasi |
| 2 | `02-mode-enforcement.md` | PLAN/BUILD enforcement — refusal pattern |
| 3 | `03-model-routing.md` | Model selection by complexity |
| 4 | `04-execution-rules.md` | Presisi input, YAGNI, langsung eksekusi |
| 5 | `05-logging.md` | Logging setiap stage |
