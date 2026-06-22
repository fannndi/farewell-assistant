# Pipeline Flow — Enrich → Route → Execute

## 1. Input
User mengirim teks. Jika < 3 kata, skip enrichment.

## 2. Local LLM Enrichment (Ollama)
Panggil Ollama untuk klasifikasi JSON:
```json
{"intent": "build|fix|review|deploy|research|docs",
 "domain": "web|mobile|infra|data|general",
 "complexity": "low|medium|high|critical",
 "confidence": 0.0-1.0}
```
Skip jika mode=eco atau input < 3 kata. Fallback ke pattern-matching (quick classify).

## 3. Check Rule
Cocokkan intent vs work mode (PLAN/BUILD). Jika PLAN → blok build/fix/deploy.

## 4. Skill Chain
Pilih skill chain berdasarkan `intent` + `domain`. Contoh: `build_web` → 8 steps.

## 5. Model Route
Pilih combo model berdasarkan complexity.

## 6. Execute
Jalankan dengan precision rules (lihat `04-execution-rules.md`).
